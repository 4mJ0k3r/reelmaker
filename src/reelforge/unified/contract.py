"""Native-free, bounded production admission and deterministic timestamp mapping."""
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from reelforge.contracts.project import project_digest
from reelforge.core.errors import InputError, Issue
from reelforge.audio.registry import AudioRegistry
from reelforge.stories.audio_contract import AudioPlan, Cue
from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.captions import fits_mobile_width
from reelforge.cinematic_projects.schema import CAPTION_LINE

VERSION = 'reel-production-0.1'
BACKENDS = ('director-v3', 'cinematic-project-0.2')
ID = {'type': 'string', 'pattern': '^[a-z][a-z0-9_]{0,47}$'}
TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 800}
TIME = {'type': 'string', 'pattern': r'^(0|[1-9][0-9]{0,2})(\.[0-9]{1,9})?$', 'maxLength': 13}
HASH = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
PRESETS = ('establish', 'reaction', 'investigate', 'threat', 'travel', 'travel_run', 'resolve')
STYLES = ('standard', 'route', 'weather', 'decision', 'settle', 'relief_close', 'run_wide', 'run_tight', 'run_exit', 'parcel_reveal')
MOODS = ('calm', 'tense', 'storm', 'determined', 'hopeful', 'warm')


def obj(properties, optional=()):
    return {'type': 'object', 'properties': properties, 'required': [k for k in properties if k not in optional], 'additionalProperties': False}


def array(item, maximum=40, minimum=0):
    return {'type': 'array', 'items': item, 'minItems': minimum, 'maxItems': maximum}


def schema():
    shot = obj({'preset': {'enum': PRESETS}, 'style': {'enum': STYLES},
                'variant': {'type': 'integer', 'minimum': 0, 'maximum': 39}, 'weather': {'type': 'boolean'}})
    event = obj({'id': ID, 'start': TIME, 'end': TIME, 'label': TEXT,
                 'world': {'enum': ('orchard', 'frost_peak')}, 'mood': {'enum': MOODS},
                 'shots': array(shot, 20, 1), 'required_assets': array(ID, 16), 'forbidden_assets': array(ID, 16)},
                 ('world', 'mood', 'shots'))
    narration = obj({'asset_id': ID, 'sha256': HASH, 'start': TIME,
                     'trim_start': TIME, 'trim_end': {'anyOf': [TIME, {'type': 'null'}]},
                     'gain': {'type': 'number', 'minimum': .05, 'maximum': .8},
                     'provenance': {'enum': ('user_finished_recording', 'synthetic_timing_fixture')}})
    subtitle = obj({'id': ID, 'start': TIME, 'end': TIME, 'language': {'enum': ('en',)},
                    'style': {'enum': ('subtitle', 'chapter', 'lower_third')},
                    'lines': array({'type': 'string', 'pattern': '^' + CAPTION_LINE + '$', 'maxLength': 32}, 2, 1)})
    return obj({'schema_version': {'const': VERSION}, 'id': ID,
                'title': {'type': 'string', 'pattern': r'^[A-Za-z0-9][A-Za-z0-9 .,!?\x27:&()\-]{0,119}$'},
                'backend': {'enum': BACKENDS}, 'script': obj({'text': {'type': 'string', 'maxLength': 16000}, 'sha256': HASH}),
                'duration_seconds': {'type': 'integer', 'minimum': 6, 'maximum': 60, 'multipleOf': 3},
                'tail_policy': {'enum': ('exact', 'pad_silence')}, 'allow_trim': {'type': 'boolean'},
                'narration': {'anyOf': [{'type': 'null'}, narration]}, 'events': array(event, 20, 1),
                'subtitles': array(subtitle, 24), 'cinematic': {'type': ['object', 'null']}})


def fail(path, message, code='UNIFIED_CONTRACT'):
    raise InputError(Issue(code, path, message))


def frame(value):
    """Decimal text -> nearest integer 30fps frame; exact ties round upward."""
    return int((Decimal(value) * 30).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def stamp(value):
    f = frame(value)
    return {'supplied_seconds': value, 'frame': f,
            'error_seconds': str(Decimal(f) / 30 - Decimal(value))}


@dataclass
class Plan:
    request: dict
    frames: int
    visual: object
    manifest: dict
    captions: tuple
    audio: object
    audio_cues: tuple
    timeline: dict


def compile_request(data, registry_root: Path):
    import hashlib
    for err in Draft202012Validator(schema()).iter_errors(data):
        fail('/' + '/'.join(map(str, err.absolute_path)), err.message[:280])
    d = deepcopy(data)
    if hashlib.sha256(d['script']['text'].encode()).hexdigest() != d['script']['sha256']:
        fail('/script/sha256', 'Script text does not match expected SHA-256')
    frames = d['duration_seconds'] * 30
    spans, seen, cursor, quantization = [], set(), 0, []
    for i, e in enumerate(d['events']):
        path = f'/events/{i}'
        if e['id'] in seen:
            fail(path + '/id', 'Duplicate event ID')
        seen.add(e['id'])
        start, end = frame(e['start']), frame(e['end'])
        quantization.extend((stamp(e['start']), stamp(e['end'])))
        if start != cursor or not start < end <= frames:
            fail(path, 'Ordered half-open events must cover the film without gaps or overlaps')
        if start % 90 or end % 90:
            suggestion = {'start_frame': (start + 45) // 90 * 90, 'end_frame': (end + 45) // 90 * 90}
            fail(path, f'Review required: event edges {start}/{end} conflict with 90-frame grid; suggested {suggestion}; errors {suggestion["start_frame"]-start}/{suggestion["end_frame"]-end} frames. No mapping was applied.', 'TIMING_CONFLICT')
        if set(e['required_assets']) & set(e['forbidden_assets']):
            fail(path, 'An asset is both required and forbidden')
        spans.append((start, end))
        cursor = end
    if cursor != frames:
        fail('/events', 'Events must cover the declared film duration')
    from reelforge.cinematic_projects.contract import Caption
    captions, cursor, ids = [], 0, set()
    for i, c in enumerate(d['subtitles']):
        start, end = frame(c['start']), frame(c['end'])
        quantization.extend((stamp(c['start']), stamp(c['end'])))
        if c['id'] in ids or not cursor <= start < end <= frames:
            fail(f'/subtitles/{i}', 'Use unique IDs and sorted non-overlapping spans inside film')
        if any(not line.strip() or not fits_mobile_width(c['style'], line) for line in c['lines']):
            fail(f'/subtitles/{i}', 'Caption is blank or too wide for mobile safe area')
        ids.add(c['id'])
        captions.append(Caption(start, end, c['style'], tuple(c['lines'])))
        cursor = end
    audio, cues = None, ()
    narration = d['narration']
    if narration is not None:
        quantization.extend(stamp(narration[k]) for k in ('start','trim_start') )
        if narration['trim_end'] is not None:
            quantization.append(stamp(narration['trim_end']))
        reg = AudioRegistry(registry_root)
        asset = reg.assets.get(narration['asset_id'])
        if asset is None or asset.sha256 != narration['sha256'] or asset.role != 'narration':
            fail('/narration', 'Missing narration or expected identity/role mismatch')
        if not d['allow_trim'] and (frame(narration['trim_start']) != 0 or narration['trim_end'] is not None):
            fail('/narration', 'Explicit trim requires allow_trim: true')
        cue = Cue(asset.id, frame(narration['start']), frame(narration['trim_start']),
                  None if narration['trim_end'] is None else frame(narration['trim_end']), narration['gain'])
        if not 0 <= cue.start_frame < frames:
            fail('/narration/start', 'Offset must lie inside film')
        audio = AudioPlan(48000, 2, 'aac', 128000, cue, ())
        # New route retains full source tail even on short productions. Native-free metadata only.
        resolved = reg.resolve(audio, frames, validate_media=False, narration_full_tail=True)
        from reelforge.reels.contract import cue_schedule
        cues = tuple(cue_schedule(resolved))
        track, = resolved
        tail = frames * 1600 - cue.start_frame * 1600 - track.output_samples
        if d['tail_policy'] == 'exact' and tail != 0:
            fail('/tail_policy', f'Exact requires zero trailing padding; actual {tail} samples')
    if d['backend'] == 'director-v3':
        if d['cinematic'] is not None:
            fail('/cinematic', 'Mixed visual backends are unsupported')
        from .director import compile_events
        visual, manifest, coverage, warnings = compile_events(d, spans)
    else:
        if d['cinematic'] is None or d['cinematic'].get('schema_version') != 'cinematic-project-0.2':
            fail('/cinematic', 'Provide a bounded cinematic-project-0.2 document')
        manifest = deepcopy(d['cinematic'])
        if manifest.get('audio') is not None or manifest.get('captions'):
            fail('/cinematic', 'Author narration/captions at the unified level only')
        if any(set(e) & {'world', 'mood', 'shots'} for e in d['events']):
            fail('/events', 'Cinematic event labels map existing beats without Director recipes')
        manifest['captions'] = [dict(start=c.start, end=c.end, style=c.style, lines=list(c.lines)) for c in captions]
        visual = compile_project(manifest, registry_root)
        if visual.frames != frames or [(b.id, b.start, b.end) for b in {s.beat.id:s.beat for s in visual.shots}.values()] != [(e['id'], *span) for e, span in zip(d['events'], spans)]:
            fail('/events', 'Cinematic event IDs and spans must match the backend beats')
        coverage, warnings = [], ['Cinematic acting continues within beats; new beats are authored blocking cuts']
        for e, (start, end) in zip(d['events'], spans):
            beat = next(s.beat for s in visual.shots if s.beat.id == e['id'])
            visible = {n.id for n in beat.scene.hierarchy if n.visible}
            active = {n.asset_id for n in beat.scene.scene.nodes if n.id in visible and n.asset_id}
            _assets(e, active)
            coverage.append({'id': e['id'], 'start_frame': start, 'end_frame': end, 'assets': sorted(active), 'actor': beat.actor, 'action': beat.action})
    body = {'contract': VERSION, 'request_sha256': project_digest(d), 'frames': frames, 'fps': 30,
            'backend': d['backend'], 'backend_manifest': manifest, 'events': coverage,
            'captions': [dict(start=c.start, end=c.end, style=c.style, lines=list(c.lines)) for c in captions],
            'audio_cues': list(cues), 'timestamp_conversion': quantization,
            'max_quantization_error_seconds': str(max((abs(Decimal(q['error_seconds'])) for q in quantization), default=Decimal(0))),
            'warnings': warnings, 'audio_provenance': narration['provenance'] if narration else 'silent'}
    return Plan(d, frames, visual, manifest, tuple(captions), audio, cues, {**body, 'plan_sha256': project_digest(body)})


def _assets(event, active):
    from reelforge.scenes.assets import asset_by_id
    for identity in event['required_assets'] + event['forbidden_assets']:
        try:
            asset_by_id(identity)
        except (KeyError, ValueError, InputError):
            fail('/events/' + event['id'], f'Unknown registered asset {identity}')
    if missing := set(event['required_assets']) - active:
        fail('/events/' + event['id'], f'Required assets not staged: {sorted(missing)}')
    if present := set(event['forbidden_assets']) & active:
        fail('/events/' + event['id'], f'Forbidden assets staged: {sorted(present)}')
