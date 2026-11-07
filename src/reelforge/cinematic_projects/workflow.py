"""Adapt the bounded cinematic plan to the existing episode AV renderer."""

import hashlib
import json
import os
import resource
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event

from reelforge.audio.registry import digest
from reelforge.contracts.project import load_project, project_digest
from reelforge.core.errors import OperationError
from reelforge.core.transaction import OwnedDirectory
from reelforge.episodes.workflow import encode_episode_frames
from reelforge.media.verify import faststart_boxes
from reelforge.productions.contract import Production, ProductionChunk
from reelforge.productions.workflow import _full_decode_hashes, render_production
from reelforge.reels.workflow import cancelled_check, render_av, stream_check, temporary_size
from reelforge.resources.deployment import check_workspace, memory_observability
from reelforge.resources.monitor import JobMonitor, preflight_memory

from .captions import caption_paths
from .contract import CHUNK_SHOTS, SHOT_FRAMES, Project, load_cinematic_project
from .sampling import visual_frame
from .schema import VERSION
from .storyboard import black_frames, write_storyboard


@dataclass(frozen=True)
class EpisodeSlice:
    project: Project
    start: int
    frames: int

    @property
    def title(self):
        return self.project.title

    @property
    def silent(self):
        return self.project.silent

    @property
    def audio(self):
        return self.project.audio


def frame_sampler(project):
    overlays = [(cue, caption_paths(cue)) for cue in project.captions]

    def sample(frame):
        caption = next((paths for cue, paths in overlays if cue.start <= frame < cue.end), ())
        return visual_frame(project, frame) + caption

    return sample


def render_episode_slice(
    plan: EpisodeSlice, output: Path, *, registry_root: Path, cancelled: Event
):
    def render_silent(visual, target, *, encoder_staging, cancelled):
        sample = frame_sampler(visual.project)
        result = encode_episode_frames(
            visual.frames,
            lambda frame: sample(visual.start + frame),
            target,
            encoder_staging=encoder_staging,
            cancelled=cancelled,
        )
        result["global_start_frame"] = visual.start
        result["encoding"] = "Global acting and caption clocks; explicit camera cuts"
        return result

    return render_av(
        plan,
        output,
        frames=plan.frames,
        visual_plan=plan,
        render_silent=render_silent,
        registry_root=registry_root,
        cancelled=cancelled,
        contract_version=VERSION,
        silent=plan.silent,
    )


def _write_json(path, content):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(content, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def _engine(project, stage, registry_root, cancellation):
    if len(project.shots) <= CHUNK_SHOTS:
        return render_episode_slice(
            EpisodeSlice(project, 0, project.frames),
            stage / "engine",
            registry_root=registry_root,
            cancelled=cancellation,
        )
    chunks = []
    for i, start in enumerate(range(0, project.frames, CHUNK_SHOTS * SHOT_FRAMES)):
        length = min(project.frames - start, CHUNK_SHOTS * SHOT_FRAMES)
        chunks.append(ProductionChunk(i, start, EpisodeSlice(project, start, length)))
    production = Production(project.title, project.shots, tuple(chunks))
    return render_production(
        production,
        stage / "engine",
        registry_root=registry_root,
        cancelled=cancellation,
        episode_renderer=render_episode_slice,
    )


def _collect_engine(source, stage, engine):
    """Link only the delivered evidence. The native staging tree is never published."""
    paths = [Path("report.json"), Path("reel.mp4")]
    for chunk in engine.get("chunk_reports", ()):
        root = Path("chunks") / f"chunk_{chunk['index']:02d}"
        paths.extend((root / "report.json", root / "reel.mp4"))
    for relative in paths:
        origin, target = source / relative, stage / relative
        if origin.is_symlink() or not origin.is_file():
            raise OperationError("CINEMATIC_PACKAGE", f"Missing verified engine file {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(origin, target, follow_symlinks=False)


def render_project(project, output, *, registry_root, cancelled=None):
    """Publish only a complete verified directory. An occupied target is never replaced."""
    started = time.perf_counter()
    own = time.process_time()
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    cancellation = cancelled if cancelled is not None else Event()
    output = output.parent.resolve() / output.name
    if os.path.lexists(output):
        raise OperationError("OUTPUT_EXISTS", "Choose a new output directory")
    cancelled_check(cancellation)
    preflight_memory()
    check_workspace(output.parent)
    owner = OwnedDirectory(output.parent, ".reelforge-cinematic-")
    committed = False
    work = None
    try:
        stage = owner.path
        plan = project.timeline()
        with JobMonitor(workspace=stage, cancelled=cancellation) as monitor:
            work = OwnedDirectory(output.parent, ".reelforge-cinematic-work-")
            engine = _engine(project, work.path, registry_root, cancellation)
            if not engine["success"]:
                detail = (
                    engine.get("error")
                    or engine.get("resource_error")
                    or engine.get("cleanup_error")
                )
                raise OperationError("CINEMATIC_ENGINE", f"Verified media unavailable: {detail}")
            _collect_engine(work.path / "engine", stage / "engine", engine)
            work.cleanup()
            work = None
            video = stage / "reel.mp4"
            os.link(stage / "engine/reel.mp4", video)
            streams = engine.get("streams")
            if streams is None:
                streams = stream_check(video, cancellation, project.frames, silent=True)
            black = black_frames(video, cancellation)
            storyboard = write_storyboard(project, video, stage, cancellation)
            _write_json(stage / "project.json", project.request)
            _write_json(stage / "timeline.json", plan)
            package_size = temporary_size(stage)
            video_hash = digest(video)
        if (
            not monitor.oom_telemetry_continuous
            or memory_observability(monitor.initial, monitor.final)["oom_events_changed"]
        ):
            raise OperationError("CINEMATIC_RESOURCE", "OOM telemetry refused publication")
        cancelled_check(cancellation)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        report = {
            "contract": VERSION,
            "success": True,
            "media_verified": True,
            "plan_sha256": plan["plan_sha256"],
            "video_sha256": video_hash,
            "frames": project.frames,
            "streams": streams,
            "black_frame_check": black,
            "storyboard": storyboard,
            "verification": engine["verification"],
            "assembly_frame_hash_match": engine.get("assembly_frame_hash_match"),
            "audio_verification": engine.get("audio_verification"),
            "wall_seconds": time.perf_counter() - started,
            "cpu_seconds": {
                "parent": time.process_time() - own,
                "children_user": after.ru_utime - children.ru_utime,
                "children_system": after.ru_stime - children.ru_stime,
            },
            "memory": monitor.report(),
            "stage_logical_bytes": package_size,
            "engine_report": "engine/report.json",
        }
        _write_json(stage / "report.json", report)
        cancelled_check(cancellation)
        owner.publish_as(output)
        committed = True
        return report
    finally:
        try:
            if work is not None:
                work.cleanup()
        finally:
            if not committed:
                owner.cleanup()


def verify_project(directory, *, registry_root, cancelled=None):
    """Recompile the snapshot and independently decode the delivered MP4."""
    project = load_cinematic_project(directory / "project.json", registry_root)
    timeline = project.timeline()
    if project_digest(load_project(directory / "timeline.json")) != project_digest(timeline):
        raise OperationError("CINEMATIC_INTEGRITY", "Timeline differs from compiled request")
    report = load_project(directory / "report.json")
    video = directory / "reel.mp4"
    if (
        not isinstance(report, dict)
        or report.get("success") is not True
        or report.get("plan_sha256") != timeline["plan_sha256"]
        or report.get("video_sha256") != digest(video)
    ):
        raise OperationError("CINEMATIC_INTEGRITY", "Plan or MP4 identity differs from report")
    cancellation = cancelled if cancelled is not None else Event()
    cancelled_check(cancellation)
    with JobMonitor(workspace=directory, cancelled=cancellation) as monitor:
        streams = stream_check(video, cancellation, project.frames, silent=project.silent)
        hashes = _full_decode_hashes(video, project.frames, cancellation)
        if len(hashes) != project.frames:
            raise OperationError("CINEMATIC_DECODE", "Decoded frame count differs")
        sequence = hashlib.sha256("".join(hashes).encode()).hexdigest()
        recorded = report.get("verification", {})
        if not isinstance(recorded, dict) or not (
            hashes == recorded.get("decoded_rgb_sha256")
            or sequence == recorded.get("decoded_sequence_sha256")
        ):
            raise OperationError("CINEMATIC_INTEGRITY", "Decoded video differs from recorded media")
        assembly_matches = None
        if len(project.shots) > CHUNK_SHOTS:
            chunk_limit = CHUNK_SHOTS * SHOT_FRAMES
            chunk_hashes = []
            for index, start in enumerate(range(0, project.frames, chunk_limit)):
                chunk = directory / "engine" / "chunks" / f"chunk_{index:02d}" / "reel.mp4"
                count = min(chunk_limit, project.frames - start)
                chunk_hashes.extend(_full_decode_hashes(chunk, count, cancellation))
            if chunk_hashes != hashes:
                raise OperationError("CINEMATIC_ASSEMBLY", "Decoded chunk sequence differs")
            assembly_matches = True
        faststart_boxes(video)
        black = black_frames(video, cancellation)
    if (
        not monitor.oom_telemetry_continuous
        or memory_observability(monitor.initial, monitor.final)["oom_events_changed"]
    ):
        raise OperationError("CINEMATIC_RESOURCE", "OOM telemetry refused verification")
    cancelled_check(cancellation)
    return {
        "verified": True,
        "frames": len(hashes),
        "streams": streams,
        "decoded_sequence_sha256": sequence,
        "assembly_frame_hash_match": assembly_matches,
        "black_frame_check": black,
        "plan_sha256": timeline["plan_sha256"],
        "video_sha256": digest(video),
    }
