"""Shared owned transaction, original visual backends and one global narration mux."""
import hashlib
import os
import time
from dataclasses import asdict, dataclass
from contextlib import contextmanager
from pathlib import Path
from threading import Event
from types import SimpleNamespace

from reelforge.audio.registry import AudioRegistry, digest
from reelforge.audio.processing import mix_pcm, verify_audio, bitstream_hash
from reelforge.contracts.project import load_project, project_digest
from reelforge.core.errors import OperationError
from reelforge.core.transaction import OwnedDirectory
from reelforge.cinematic_projects.operator import output_destination
from reelforge.cinematic_projects.narration import check_narration_storage, mux_narration
from reelforge.cinematic_projects.storyboard import write_storyboard, black_frames
from reelforge.cinematic_projects.workflow import _write_json
from reelforge.productions.workflow import render_production, _full_decode_hashes, _verify_pts
from reelforge.resources.monitor import JobMonitor, preflight_memory
from reelforge.resources.deployment import memory_observability
from reelforge.reels.workflow import stream_check, cancelled_check
from reelforge.reels.contract import cue_schedule
from reelforge.media.verify import faststart_boxes
from .contract import compile_request


@contextmanager
def owned(parent, prefix):
    owner = OwnedDirectory(parent, prefix)
    try:
        yield owner
    finally:
        owner.cleanup()


def resolve_audio(plan, registry, private=None, cancelled=None, native=True):
    if plan.audio is None:
        return ()
    tracks = AudioRegistry(registry).resolve(plan.audio, plan.frames, validate_media=native,
                     validation_root=private, cancelled=cancelled, narration_full_tail=True)
    if tuple(cue_schedule(tracks)) != plan.audio_cues:
        raise OperationError('AUDIO_CHANGED', 'Audio identity or schedule changed after planning')
    return tracks


def private_destination(plan, output, registry):
    destination = output_destination(output)
    checkout = Path(__file__).resolve().parents[3]
    if (checkout / 'AGENTS.md').is_file():
        if destination.is_relative_to(checkout):
            raise OperationError('UNIFIED_PRIVATE_PATH', 'Keep production outputs outside the engine checkout')
        if plan.audio is not None and Path(registry).resolve().is_relative_to(checkout):
            raise OperationError('UNIFIED_PRIVATE_PATH', 'Keep production narration registry outside the engine checkout')
    return destination


def preflight(plan, output, registry, cancelled=None):
    destination = private_destination(plan, output, registry)
    preflight_memory()
    check_narration_storage(destination.parent, plan.frames)
    with JobMonitor(workspace=destination.parent, cancelled=cancelled) as monitor:
        with owned(destination.parent, '.reelforge-unified-probe-') as owner:
            resolve_audio(plan, registry, owner.path, cancelled)
    _resource_gate(monitor)
    return {'ready': True, 'advisory': True, 'plan_sha256': plan.timeline['plan_sha256']}


@dataclass
class Slice:
    episode: object
    start: int
    captions: tuple

    @property
    def title(self):
        return self.episode.title

    @property
    def frames(self):
        return self.episode.frames

    @property
    def silent(self):
        return True

    @property
    def audio(self):
        return None


def render_director_chunk(plan, output, *, registry_root, cancelled):
    from reelforge.cinematic_projects.captions import caption_paths
    from reelforge.episodes.contract import frame_origin
    from reelforge.episodes.workflow import encode_episode_frames
    from reelforge.direction.sampling import direction_frame
    from reelforge.reels.workflow import render_av
    overlays = [(cue, caption_paths(cue)) for cue in plan.captions]

    def render_silent(visual, target, *, encoder_staging, cancelled):
        def sample(local):
            segment, frame = frame_origin(visual.episode, local)
            global_frame = visual.start + local
            overlay = next((paths for cue, paths in overlays if cue.start <= global_frame < cue.end), ())
            return direction_frame(segment.direction, frame) + overlay
        return encode_episode_frames(visual.frames, sample, target, encoder_staging=encoder_staging, cancelled=cancelled)

    return render_av(plan, output, frames=plan.frames, visual_plan=plan,
                     render_silent=render_silent, registry_root=registry_root, cancelled=cancelled,
                     contract_version='reel-production-0.1-director-visual', silent=True)


def _visual(plan, output, registry, cancelled):
    if plan.request['backend'] == 'cinematic-project-0.2':
        from reelforge.cinematic_projects.workflow import render_project
        return render_project(plan.visual, output, registry_root=registry, cancelled=cancelled)
    from reelforge.productions.contract import Production, ProductionChunk
    chunks = tuple(ProductionChunk(c.index,c.start_frame,Slice(c.episode,c.start_frame,plan.captions)) for c in plan.visual.chunks)
    production = Production(plan.visual.title,plan.visual.segments,chunks)
    return render_production(production,output,registry_root=registry,cancelled=cancelled,episode_renderer=render_director_chunk)


def _resource_gate(monitor):
    if not monitor.oom_telemetry_continuous or memory_observability(monitor.initial, monitor.final)['oom_events_changed']:
        raise OperationError('UNIFIED_RESOURCE','Missing OOM telemetry or changed OOM events; publication refused')


def render(plan, output, registry, cancelled=None):
    cancelled = cancelled if cancelled is not None else Event()
    started = time.perf_counter()
    # Re-admit mutable caller data rather than trusting a stale in-memory object.
    fresh = compile_request(plan.request, registry)
    if fresh.timeline != plan.timeline:
        raise OperationError('UNIFIED_CHANGED', 'Plan changed since compilation')
    plan = fresh
    output = private_destination(plan, output, registry)
    preflight_memory()
    check_narration_storage(output.parent,plan.frames)
    owner = OwnedDirectory(output.parent,'.reelforge-unified-')
    work = None
    committed = False
    preserved = False
    try:
        stage = owner.path
        with JobMonitor(workspace=stage,cancelled=cancelled) as monitor:
            work = OwnedDirectory(output.parent,'.reelforge-unified-work-')
            private = work.path / 'audio'
            private.mkdir()
            tracks = resolve_audio(plan,registry,private,cancelled)
            engine = _visual(plan,stage/'engine',registry,cancelled)
            if not engine.get('success'):
                if engine.get('cleanup_error'):
                    raise OperationError('UNIFIED_OWNERSHIP',f'Child ownership uncertain; preserve {stage} and {work.path}')
                raise OperationError('UNIFIED_ENGINE',str(engine.get('error') or engine))
            cancelled_check(cancelled)
            silent = stage/'engine/reel.mp4'
            video = stage/'reel.mp4'
            audio_proof = None
            if tracks:
                track, = tracks
                snapshot = private/track.asset.id/'input.wav'
                audio_proof = mux_narration(track,snapshot,plan.frames,silent,video,private,cancelled)
            else:
                os.link(silent,video)
            shots = [SimpleNamespace(id=f'shot_{i+1:02d}',start=i*90,end=(i+1)*90) for i in range(plan.frames//90)]
            storyboard = write_storyboard(SimpleNamespace(shots=shots),video,stage,cancelled)
            assets = None
            if plan.request['backend']=='director-v3':
                from reelforge.mvp.asset_audit import audit_assets
                cancelled_check(cancelled)
                assets = audit_assets(plan.visual)
                _write_json(stage/'asset_audit.json',assets)
            _write_json(stage/'request.json',plan.request)
            _write_json(stage/'plan.json',plan.timeline)
            inventory = {'script_sha256':plan.request['script']['sha256'],
                         'narration':None if not tracks else asdict(tracks[0].asset),
                         'provenance':plan.timeline['audio_provenance'], 'raw_source_copied':False}
            if inventory['narration']:
                inventory['narration'].pop('file')
            _write_json(stage/'private_inventory.json',inventory)
            report = {'success':True,'contract':plan.request['schema_version'],
                      'request_sha256':project_digest(plan.request),'plan_sha256':plan.timeline['plan_sha256'],
                      'video_sha256':digest(video),'silent_video_sha256':digest(silent),
                      'audio_verification':audio_proof,'storyboard':storyboard,
                      'audio_provenance':plan.timeline['audio_provenance'],
                      'wall_seconds':time.perf_counter()-started,
                      'real_voice_acceptance':'pending' if plan.timeline['audio_provenance']!='user_finished_recording' else 'requires human review'}
            _write_json(stage/'report.json',report)
            verification = verify(stage,registry,cancelled=cancelled)
            _write_json(stage/'verification.json',verification)
            work.cleanup();work=None
        _resource_gate(monitor)
        report.update(memory=monitor.report(),wall_seconds=time.perf_counter()-started)
        # Only replace own staged report before atomically publishing the directory.
        (stage/'report.json').unlink()
        _write_json(stage/'report.json',report)
        cancelled_check(cancelled)
        owner.publish_as(output)
        committed=True
        return report
    except OperationError as error:
        # A nested renderer may retain work *inside* our stage. Never recursively
        # remove that stage when a descendant's ownership is uncertain.
        uncertain = error.code in {
            'CINEMATIC_OWNERSHIP', 'UNIFIED_OWNERSHIP', 'WORKSPACE_IDENTITY',
            'TRANSACTION_IDENTITY', 'TRANSACTION_PRESERVED', 'TRANSACTION_CONTENT',
            'TRANSACTION_CLEANUP', 'ENCODER_OWNERSHIP', 'ENCODER_CLEANUP',
        }
        if uncertain:
            owner.preserve()
            if work is not None:
                work.preserve()
            preserved = True
        raise
    finally:
        if not preserved:
            try:
                if work is not None:work.cleanup()
            finally:
                if not committed:owner.cleanup()


def verify(directory, registry, cancelled=None):
    directory = Path(directory)
    if any(p.is_symlink() for p in (directory,*directory.parents)) or any(p.is_symlink() for p in directory.rglob('*')):
        raise OperationError('UNIFIED_INTEGRITY','Symlink package paths are forbidden')
    cancelled = cancelled if cancelled is not None else Event()
    plan = compile_request(load_project(directory/'request.json'),registry)
    recorded = load_project(directory/'plan.json')
    report = load_project(directory/'report.json')
    video,silent=directory/'reel.mp4',directory/'engine/reel.mp4'
    if recorded != plan.timeline or report.get('success') is not True or report.get('plan_sha256')!=plan.timeline['plan_sha256'] or report.get('request_sha256')!=project_digest(plan.request) or report.get('video_sha256')!=digest(video) or report.get('silent_video_sha256')!=digest(silent):
        raise OperationError('UNIFIED_INTEGRITY','Package request, plan or media identity changed')
    with JobMonitor(workspace=directory.parent,cancelled=cancelled) as monitor:
        streams=stream_check(video,cancelled,plan.frames,silent=plan.audio is None)
        hashes=_full_decode_hashes(video,plan.frames,cancelled)
        original=_full_decode_hashes(silent,plan.frames,cancelled)
        if len(hashes)!=plan.frames or hashes!=original or bitstream_hash(video,cancelled=cancelled)!=bitstream_hash(silent,cancelled=cancelled):
            raise OperationError('UNIFIED_INTEGRITY','Final video differs from verified silent source')
        # Re-establish chunk assembly identity, not just file/report hashes.
        if plan.request['backend']=='director-v3':
            chunk_hashes=[]
            for c in plan.visual.chunks:
                chunk_hashes.extend(_full_decode_hashes(directory/'engine/chunks'/f'chunk_{c.index:02d}'/'reel.mp4',c.frames,cancelled))
            if chunk_hashes!=hashes:
                raise OperationError('UNIFIED_ASSEMBLY','Chunk sequence differs from final video')
        else:
            from reelforge.cinematic_projects.workflow import verify_project
            verify_project(directory/'engine',registry_root=registry,cancelled=cancelled)
        audio_proof=None
        if plan.audio:
            with owned(directory.parent,'.reelforge-unified-verify-') as work:
                track,=resolve_audio(plan,registry,work.path,cancelled)
                snapshot=work.path/track.asset.id/'input.wav'
                reference,decoded=work.path/'reference.f32',work.path/'decoded.f32'
                mix_pcm((track,),plan.frames,{track.asset.id:snapshot},reference,cancelled=cancelled)
                audio_proof=verify_audio(silent,video,reference,decoded,(track,),plan.frames,cancelled=cancelled)
                if digest(snapshot)!=track.asset.sha256:
                    raise OperationError('AUDIO_CHANGED','Narration changed during independent verification')
        pts=_verify_pts(video,plan.frames,cancelled)
        boxes=faststart_boxes(video)
        black=black_frames(video,cancelled)
    _resource_gate(monitor)
    return {'verified':True,'frames':len(hashes),'streams':streams,'pts':pts,'mp4_boxes':boxes,
            'black_frames':black,'decoded_sequence_sha256':hashlib.sha256(''.join(hashes).encode()).hexdigest(),
            'video_bitstream_unchanged':True,'audio_verification':audio_proof,'memory':monitor.report()}
