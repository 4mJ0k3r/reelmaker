"""Strict native-free admission. Shot clocks never drive acting."""

import re
from bisect import bisect_right
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

from reelforge.audio.registry import AudioRegistry
from reelforge.characters import living, living_transitions
from reelforge.contracts.project import _pointer, load_project, project_digest
from reelforge.core.errors import InputError, Issue
from reelforge.productions.contract import FRAMES_PER_SEGMENT as SHOT_FRAMES
from reelforge.productions.contract import MAX_SEGMENTS_PER_CHUNK as CHUNK_SHOTS
from reelforge.reels.contract import cue_schedule, metadata_plan
from reelforge.scenes.assets import asset_by_id
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import CompiledScene, compile_scene
from reelforge.stories.audio_contract import AudioPlan, audio_from_data
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS,
    InteractionPlan,
    interaction_manifest,
)
from reelforge.visual_library.composition.living_worlds import WORLD_KITS, node, world_manifest

from .captions import fits_mobile_width
from .schema import (
    CAMERAS,
    CAPTION_LINE,
    CAPTION_STYLES,
    DRESSING,
    EFFECT_IDS,
    ID,
    MAX_FRAMES,
    SIGNAL,
    TITLE,
    VERSION,
    project_schema,
)


def fail(path, message):
    raise InputError(Issue("CINEMATIC_PROJECT", path, message))


@dataclass(frozen=True)
class Beat:
    id: str
    start: int
    end: int
    actor: str
    action: str
    expression: str
    scene: CompiledScene
    interaction: InteractionPlan | None
    signal: str | None
    dressing: str | None


@dataclass(frozen=True)
class Shot:
    id: str
    start: int
    end: int
    camera: str
    beat: Beat


@dataclass(frozen=True)
class Caption:
    start: int
    end: int
    style: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Project:
    title: str
    shots: tuple[Shot, ...]
    captions: tuple[Caption, ...]
    audio: AudioPlan | None
    audio_cues: tuple[dict, ...]
    request: dict

    @property
    def frames(self):
        return len(self.shots) * SHOT_FRAMES

    @property
    def silent(self):
        return self.audio is None

    def at(self, frame):
        if type(frame) is not int or not 0 <= frame < self.frames:
            fail("/frame", f"Use an integer frame in [0, {self.frames - 1}]")
        shot = self.shots[frame // SHOT_FRAMES]
        return shot, frame - shot.beat.start

    def timeline(self):
        rows = []
        for shot in self.shots:
            beat = shot.beat
            rows.append(
                {
                    "id": shot.id,
                    "start": shot.start,
                    "end": shot.end,
                    "camera": shot.camera,
                    "beat": beat.id,
                    "acting_frame_at_start": shot.start - beat.start,
                    "continuity": (
                        "continuous_beat" if shot.start > beat.start else "authored_blocking"
                    ),
                    "render": "interaction_frame" if beat.interaction else "evaluate_layers",
                    "caption_indices": [
                        i
                        for i, c in enumerate(self.captions)
                        if c.start < shot.end and c.end > shot.start
                    ],
                    "audio_indices": [
                        i
                        for i, c in enumerate(self.audio_cues)
                        if c["start_sample"] < shot.end * 1600
                        and c["end_sample"] > shot.start * 1600
                    ],
                }
            )
        body = {
            "contract": VERSION,
            "title": self.title,
            "frames": self.frames,
            "fps": 30,
            "output": [720, 1280],
            "request": self.request,
            "shots": rows,
            "audio_cues": self.audio_cues,
            "captions": [asdict(c) for c in self.captions],
            "editorial_cuts": [s.start for s in self.shots[1:]],
            "route": "episode_av"
            if self.frames <= SHOT_FRAMES * CHUNK_SHOTS
            else "production-0.1-chunk-assembly",
            "chunk_boundaries": list(
                range(SHOT_FRAMES * CHUNK_SHOTS, self.frames, SHOT_FRAMES * CHUNK_SHOTS)
            ),
        }
        return {**body, "plan_sha256": project_digest(body)}


def _structure(data):
    for error in Draft202012Validator(project_schema()).iter_errors(data):
        fail(_pointer(error.absolute_path), error.message[:280])
    if not re.fullmatch(TITLE.removeprefix("^").removesuffix("$"), data["title"]):
        fail("/title", "Use a single line of supported printable characters")
    for group in ("beats", "shots"):
        seen = set()
        for i, item in enumerate(data[group]):
            if not re.fullmatch(ID["pattern"], item["id"]) or item["id"] in seen:
                fail(f"/{group}/{i}/id", "Use a unique registered-format ID")
            seen.add(item["id"])


def _decorate(scene, raw, path):
    effect = raw.get("effect")
    if effect:
        effect_id = effect["id"]
        if effect["variant"] not in asset_by_id(effect_id).variants:
            fail(path + "/effect/variant", f"Choose {', '.join(asset_by_id(effect_id).variants)}")
        scene["nodes"] = [n for n in scene["nodes"] if n.get("asset_id") != effect_id]
        x, y, scale = {
            "ground_mist_01": (158, 611, 1.5),
            "smoke_wisp_01": (254, 447, 0.9),
        }.get(effect_id, (0, 0, 1))
        scene["nodes"].append(
            node("project_effect", "foreground", 6, effect_id, effect["variant"], x, y, scale)
        )
    if "signal" in raw:
        lamp = next((n for n in scene["nodes"] if n["id"] == "streetlamp"), None)
        if lamp is None:
            lamp = node("streetlamp", "midground", 7, SIGNAL, raw["signal"], 230, 548, 0.86)
            scene["nodes"].append(lamp)
        lamp["variant"] = raw["signal"]
    if "dressing" in raw:
        world, identity, variant, x, y, scale = DRESSING[raw["dressing"]]
        if raw["world"] != world or raw["action"] in INTERACTIONS:
            fail(path + "/dressing", f"Use only in {world}, outside active interactions")
        scene["nodes"].append(node("dressed_prop", "midground", 10, identity, variant, x, y, scale))


def _compile_beat(raw, path):
    start, end = raw["start"], raw["end"]
    if type(start) is not int or type(end) is not int:
        fail(path, "Use integer frame indices")
    length = end - start
    if start % SHOT_FRAMES or length not in (SHOT_FRAMES, 2 * SHOT_FRAMES):
        fail(path, "Use one or two consecutive 90-frame shots per beat")
    action, actor, world, mood = (raw[k] for k in ("action", "actor", "world", "mood"))
    if mood not in WORLD_KITS[world]:
        fail(path + "/mood", f"Choose {', '.join(WORLD_KITS[world])} for {world}")
    expression = raw.get("expression", "neutral")
    spec = INTERACTIONS.get(action)
    if spec:
        if actor not in spec.actors:
            fail(path + "/actor", f"Choose {', '.join(spec.actors)} for {action}")
        if (world, mood) != (spec.kit, spec.mood):
            fail(path + "/world", f"{action} requires {spec.kit}/{spec.mood}")
        if raw.get("variant") not in spec.variants:
            fail(path + "/variant", f"{spec.prop} requires one of {', '.join(spec.variants)}")
        if length < spec.frames or {"expression", "stage_x"} & raw.keys():
            fail(path, "Reserve 180 frames and use the interaction's fixed staging and acting")
        data = interaction_manifest(
            {
                "schema_version": "interaction-0.1",
                "interaction": action,
                "actor": actor,
                "prop": spec.prop,
                "variant": raw["variant"],
            }
        )
    else:
        if "variant" in raw:
            fail(path + "/variant", "Prop variants belong to a registered interaction")
        if actor not in living.PROFILES:
            fail(path + "/actor", "Rowan is supported only for sit_stand")
        if action in living_transitions.TRANSITIONS and length != living_transitions.FRAMES:
            fail(path + "/end", "A registered transition occupies exactly 90 frames")
        data = world_manifest(world, mood, actor=actor, frames=length)
        actor_node = next(n for n in data["nodes"] if n["id"] == "actor")
        if "stage_x" in raw:
            if type(raw["stage_x"]) is not int:
                fail(path + "/stage_x", "Use an integer stage position")
            actor_node["transform"]["x"] = raw["stage_x"]
        anchor = actor_node["transform"]
        if action in ("walk", "run"):
            final_pose = living.sample_pose(actor, action, (length - 1) / 30)
        elif action in living_transitions.TRANSITIONS:
            final_pose = living_transitions.sample_transition(actor, action, length - 1).pose
        else:
            final_pose = None
        if final_pose and anchor["x"] + anchor["scale"] * final_pose.root.x > 312:
            fail(path + "/stage_x", "Choose an earlier stage position or a shorter/slower action")
    _decorate(data, raw, path)
    try:
        scene = compile_scene(validate_scene(data))
    except InputError as error:
        fail(path, f"Scene admission rejected {error.issue.path}: {error}")
    interaction = InteractionPlan(action, actor, raw["variant"], scene) if spec else None
    return Beat(
        raw["id"],
        start,
        end,
        actor,
        action,
        expression,
        scene,
        interaction,
        raw.get("signal"),
        raw.get("dressing"),
    )


def compile_project(data, registry_root: Path):
    _structure(data)
    total = len(data["shots"]) * SHOT_FRAMES
    beats = []
    end = 0
    for i, raw in enumerate(data["beats"]):
        path = f"/beats/{i}"
        if raw["start"] != end or raw["end"] > total:
            fail(path, "Beats must cover the shot grid in order without gaps or overlaps")
        beat = _compile_beat(raw, path)
        beats.append(beat)
        end = beat.end
    if end != total:
        fail("/beats", f"Beats must cover all {total} frames")
    boundaries = [b.end for b in beats]
    shots = []
    for i, raw in enumerate(data["shots"]):
        start = i * SHOT_FRAMES
        beat = beats[bisect_right(boundaries, start)]
        camera = raw["camera"]
        if camera == "interaction_detail" and not beat.interaction:
            fail(f"/shots/{i}/camera", "interaction_detail requires a compatible interaction")
        if camera == "object_reveal" and not (beat.signal or beat.interaction or beat.dressing):
            fail(
                f"/shots/{i}/camera",
                "object_reveal requires a signal, dressed prop or interaction prop",
            )
        shots.append(Shot(raw["id"], start, start + SHOT_FRAMES, camera, beat))
    captions = []
    end = 0
    for i, raw in enumerate(data["captions"]):
        start = raw["start"]
        if (
            type(start) is not int
            or type(raw["end"]) is not int
            or not end <= start < raw["end"] <= total
        ):
            fail(f"/captions/{i}", "Use sorted, non-overlapping integer spans within the project")
        if any(not line.strip() or not re.fullmatch(CAPTION_LINE, line) for line in raw["lines"]):
            fail(f"/captions/{i}/lines", "Use nonblank supported ASCII text")
        if any(not fits_mobile_width(raw["style"], line) for line in raw["lines"]):
            fail(f"/captions/{i}/lines", "Split wide text into shorter mobile-safe lines")
        captions.append(Caption(start, raw["end"], raw["style"], tuple(raw["lines"])))
        end = raw["end"]
    if data["audio"] is not None and len(shots) > CHUNK_SHOTS:
        fail("/audio", "Audio is admitted only for 3–30-second projects")
    audio = audio_from_data(data["audio"], total)
    draft = Project(data["title"], tuple(shots), tuple(captions), audio, (), deepcopy(data))
    cues = (
        ()
        if audio is None
        else tuple(cue_schedule(metadata_plan(draft, AudioRegistry(registry_root), total)))
    )
    return Project(draft.title, draft.shots, draft.captions, audio, cues, draft.request)


def load_cinematic_project(path, registry_root):
    return compile_project(load_project(path), registry_root)


def capabilities(registry_root):
    return {
        "contract": VERSION,
        "shot_frames": SHOT_FRAMES,
        "max_frames": MAX_FRAMES,
        "max_audio_frames": CHUNK_SHOTS * SHOT_FRAMES,
        "worlds": WORLD_KITS,
        "actors": {
            **{
                i: {
                    "name": p.name,
                    "actions": living.ACTIONS,
                    "expressions": living.EXPRESSIONS,
                    "transitions": living_transitions.TRANSITIONS,
                }
                for i, p in living.PROFILES.items()
            },
            "rowan_01": {"name": "Rowan Vale", "interactions_only": True},
        },
        "interactions": {k: asdict(v) for k, v in INTERACTIONS.items()},
        "effects": {i: asset_by_id(i).variants for i in EFFECT_IDS},
        "cameras": CAMERAS,
        "caption_styles": CAPTION_STYLES,
        "signal": {SIGNAL: ["unlit", "lit"]},
        "dressing": {
            k: {"world": v[0], "prop": v[1], "variant": v[2]} for k, v in DRESSING.items()
        },
        "audio": {i: a.role for i, a in AudioRegistry(registry_root).assets.items()},
        "limits": [
            "No request-selected paths, code, custom geometry or generated audio",
            "Acting is continuous within a beat; the next beat is authored blocking",
            "Only silent projects can exceed ten shots",
        ],
    }
