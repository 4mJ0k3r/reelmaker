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
from reelforge.visual_library.composition.living_worlds import MOODS, WORLD_KITS, node, world_manifest

from .captions import fits_mobile_width
from .schema import (
    CAMERAS,
    CAPTION_LINE,
    CAPTION_STYLES,
    DRESSING,
    EFFECT_IDS,
    ID,
    INTENTS,
    MAX_FRAMES,
    MOTIONS,
    SIGNAL,
    STAGED_VERSION,
    TITLE,
    VERSION,
    project_schema,
)
from .staging import PACING, Performer, pose_at


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
    refined: bool = False
    facing: str = "right"
    delay: int = 0
    partner: Performer | None = None
    cue_frame: int | None = None
    grade: str | None = None
    pacing: str | None = None


@dataclass(frozen=True)
class Shot:
    id: str
    start: int
    end: int
    camera: str
    beat: Beat
    focus: str = "actor"
    motion: str = "hold"
    intent: str | None = None
    hold: bool = False


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
    def version(self):
        return self.request["schema_version"]

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
                    **({"direction": {"intent": shot.intent,
                                      "reason": INTENT_REASONS[shot.intent],
                                      "intentional_hold": shot.hold}}
                       if shot.intent else {}),
                    **({"focus": shot.focus, "motion": shot.motion}
                       if self.version == STAGED_VERSION else {}),
                    "beat": beat.id,
                    **({"pacing": beat.pacing,
                        "timing": {"lead": asdict(Performer(beat.actor, beat.action,
                            beat.expression, beat.facing, beat.delay, beat.pacing)),
                            "partner": asdict(beat.partner) if beat.partner else None}}
                       if beat.pacing or (beat.partner and beat.partner.pacing) else {}),
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
            "contract": self.version,
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
    version = data.get("schema_version") if isinstance(data, dict) else None
    if version not in (VERSION, STAGED_VERSION):
        fail("/schema_version", f"Use {VERSION} or {STAGED_VERSION}")
    for error in Draft202012Validator(project_schema(version)).iter_errors(data):
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


def _performer(raw, inherited_pacing=None):
    return Performer(raw["actor"], raw["action"], raw.get("expression", "neutral"),
                     raw.get("facing", "right"), raw.get("delay_frames", 0),
                     raw.get("pacing", inherited_pacing))


def _swept_bounds(performer, anchor, length, path, cue):
    if type(performer.delay) is not int or performer.delay >= length:
        fail(path + "/delay_frames", "Use an integer delay inside this beat")
    if performer.delay + PACING.get(performer.pacing, (0, 1, 1))[0] >= length:
        fail(path + "/pacing", "Pacing anticipation and delay must leave an active frame")
    first = anchor["x"]
    pose, _ = pose_at(performer, length - 1, refined=True)
    signed = 1 if performer.facing == "right" else -1
    last = first + signed * anchor["scale"] * pose.root.x
    if cue is not None and signed < 0 and abs(first - last) > 1e-8:
        fail(path + "/facing", "A moving actor facing left cannot pivot at a cue")
    low, high = min(first, last), max(first, last)
    if low < 32 or high > 320:
        fail(path + "/stage_x", "Actor travel must remain inside the supported staging lane")
    return low, high


def _compile_beat(raw, path, *, staged=False):
    start, end = raw["start"], raw["end"]
    if type(start) is not int or type(end) is not int:
        fail(path, "Use integer frame indices")
    length = end - start
    max_shots = 4 if staged else 2
    if start % SHOT_FRAMES or length not in range(SHOT_FRAMES, (max_shots + 1) * SHOT_FRAMES, SHOT_FRAMES):
        fail(path, f"Use one to {max_shots} consecutive 90-frame shots per beat")
    action, actor, world, mood = (raw[k] for k in ("action", "actor", "world", "mood"))
    if mood not in WORLD_KITS[world]:
        fail(path + "/mood", f"Choose {', '.join(WORLD_KITS[world])} for {world}")
    expression = raw.get("expression", "neutral")
    spec = INTERACTIONS.get(action)
    partner = _performer(raw["partner"], raw.get("pacing")) if "partner" in raw else None
    cue = raw.get("cue_frame")
    lead = _performer(raw)
    if cue is not None and (type(cue) is not int or cue >= length or cue % SHOT_FRAMES
                            or raw.get("signal") != "lit" or not partner):
        fail(path + "/cue_frame", "Use an editorial cut within a paired beat with a lit signal")
    if spec:
        if "pacing" in raw:
            fail(path + "/pacing", "Registered interactions keep their fixed contact clock")
        if actor not in spec.actors:
            fail(path + "/actor", f"Choose {', '.join(spec.actors)} for {action}")
        if (world, mood) != (spec.kit, spec.mood):
            fail(path + "/world", f"{action} requires {spec.kit}/{spec.mood}")
        if raw.get("variant") not in spec.variants:
            fail(path + "/variant", f"{spec.prop} requires one of {', '.join(spec.variants)}")
        if length != 180 or {"expression", "stage_x", "facing", "delay_frames", "partner"} & raw.keys():
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
        if not staged and action in living_transitions.TRANSITIONS and length != living_transitions.FRAMES:
            fail(path + "/end", "A registered transition occupies exactly 90 frames")
        data = world_manifest(world, mood, actor=actor, frames=min(length, 180))
        actor_node = next(n for n in data["nodes"] if n["id"] == "actor")
        if "stage_x" in raw:
            if type(raw["stage_x"]) is not int:
                fail(path + "/stage_x", "Use an integer stage position")
            actor_node["transform"]["x"] = raw["stage_x"]
        anchor = actor_node["transform"]
        if staged:
            bounds = _swept_bounds(lead, anchor, length, path, cue)
            if partner:
                if actor == partner.actor:
                    fail(path + "/partner/actor", "Choose a different registered actor")
                other = raw["partner"]
                if type(other["stage_x"]) is not int:
                    fail(path + "/partner/stage_x", "Use an integer stage position")
                info = {"character": partner.actor, "action": "idle", "expression": partner.expression}
                extra = node("partner", "midground", 11, partner.actor, "default",
                             other["stage_x"], anchor["y"], anchor["scale"], kind="character",
                             ground_id="ground", character=info)
                second = _swept_bounds(partner, extra["transform"], length, path + "/partner", cue)
                gap = max(second[0] - bounds[1], bounds[0] - second[1])
                if gap < 42:
                    fail(path + "/partner/stage_x", "Keep the two swept lanes at least 42 units apart")
                data["nodes"].append(extra)
            final_pose = None
        elif action in ("walk", "run"):
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
    interaction = InteractionPlan(action, actor, raw["variant"], scene, staged) if spec else None
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
        staged, lead.facing, lead.delay, partner, cue,
        mood if world in MOODS else None,
        raw.get("pacing"),
    )


INTENT_REASONS = {
    "establish": "Orient the viewer in the selected registered world",
    "approach": "Follow the moving focal performer toward the next beat",
    "observe": "Show attention with alternating medium and close coverage",
    "react": "Read the focal performer's emotional response",
    "reveal": "Expose the registered practical light or story prop",
    "interact": "Frame the registered hand-to-prop action",
    "pursue": "Track the admitted locomotion without changing its clock",
    "wait": "Hold suspense with alternating environmental and performer coverage",
    "depart": "Follow the admitted departure motion",
    "resolve": "Close with shared coverage when a second actor is present",
    "cliffhanger": "End on a story object or an unresolved performer reaction",
}


def _coverage(beat, start, total, previous, *, intent=None, focus=None, hold=False):
    """Resolve requested automatic coverage from the beats, cues and existing shots."""
    if intent:
        subject = focus or ("partner" if beat.partner and previous
                            and previous.focus == "actor" and intent == "react" else "actor")
        if hold and previous and previous.beat is beat:
            return previous.camera, previous.focus
        if intent == "establish":
            if previous and previous.beat is beat and previous.camera == "establishing":
                return ("two_shot" if beat.partner else "medium"), subject
            return "establishing", subject
        if intent in ("approach", "pursue", "depart"):
            return "follow", subject
        if intent == "interact":
            return "interaction_detail", subject
        if intent == "reveal":
            return "object_reveal", subject
        if intent == "resolve":
            return ("two_shot" if beat.partner else "atmospheric_close"), subject
        if intent == "cliffhanger":
            return ("object_reveal" if beat.signal or beat.dressing or beat.interaction
                    else "reaction"), subject
        if intent == "react":
            if previous and previous.camera == "reaction" and previous.focus == subject:
                return "medium", subject
            return "reaction", subject
        if intent == "wait":
            return ("medium" if previous and previous.camera == "atmospheric_close"
                    else "atmospheric_close"), subject
        return ("close_up" if previous and previous.camera == "medium" else "medium"), subject
    if not previous:
        return "establishing", "actor"
    if beat.cue_frame is not None and start <= beat.start + beat.cue_frame < start + SHOT_FRAMES:
        return "object_reveal", "actor"
    if start + SHOT_FRAMES == total:
        return ("two_shot" if beat.partner else "atmospheric_close"), "actor"
    if beat is not previous.beat:
        ground = next(n.asset_id for n in beat.scene.scene.nodes if n.id == "ground")
        previous_ground = next(
            n.asset_id for n in previous.beat.scene.scene.nodes if n.id == "ground"
        )
        if ground != previous_ground:
            return "establishing", "actor"
    if beat.partner:
        return "reaction", "partner" if previous.focus == "actor" else "actor"
    if beat.interaction:
        return "interaction_detail", "actor"
    if beat.action in ("walk", "run", "idle_to_walk", "walk_to_stop"):
        return "follow", "actor"
    if beat.action in ("notice", "react", "notice_to_react"):
        return "reaction", "actor"
    return ("medium" if previous.camera != "medium" else "establishing"), "actor"


def compile_project(data, registry_root: Path):
    _structure(data)
    staged = data["schema_version"] == STAGED_VERSION
    total = len(data["shots"]) * SHOT_FRAMES
    beats = []
    end = 0
    for i, raw in enumerate(data["beats"]):
        path = f"/beats/{i}"
        if raw["start"] != end or raw["end"] > total:
            fail(path, "Beats must cover the shot grid in order without gaps or overlaps")
        beat = _compile_beat(raw, path, staged=staged)
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
        focus = raw.get("focus", "actor")
        intent = raw.get("intent")
        hold = raw.get("hold", False)
        if (intent or "hold" in raw) and camera != "auto":
            fail(f"/shots/{i}/intent", "Use intent/hold only with camera auto")
        if "hold" in raw and not intent:
            fail(f"/shots/{i}/hold", "Select a registered intent before requesting a hold")
        if intent in ("approach", "pursue", "depart"):
            action = beat.partner.action if focus == "partner" and beat.partner else beat.action
            if action not in ("walk", "run", "idle_to_walk", "walk_to_stop"):
                fail(f"/shots/{i}/intent", "Movement intent requires walk/run or a locomotion transition")
        if intent == "interact" and (not beat.interaction or focus == "partner"):
            fail(f"/shots/{i}/intent", "interact requires a registered lead interaction")
        if hold and (not shots or shots[-1].beat is not beat or shots[-1].intent != intent):
            fail(f"/shots/{i}/hold", "Hold only the same intention in this continuous beat")
        if camera == "auto":
            if "focus" in raw and not intent:
                fail(f"/shots/{i}/focus", "Automatic coverage selects its own focus")
            camera, focus = _coverage(beat, start, total, shots[-1] if shots else None,
                                      intent=intent, focus=raw.get("focus"), hold=hold)
        if camera == "interaction_detail" and not beat.interaction:
            fail(f"/shots/{i}/camera", "interaction_detail requires a compatible interaction")
        if camera == "object_reveal" and not (beat.signal or beat.interaction or beat.dressing):
            fail(
                f"/shots/{i}/camera",
                "object_reveal requires a signal, dressed prop or interaction prop",
            )
        if (focus == "partner" or camera == "two_shot") and not beat.partner:
            fail(f"/shots/{i}", "This shot requires two actors in its beat")
        motion = raw.get("motion", "track" if intent in ("approach", "pursue", "depart") else "hold")
        shots.append(Shot(raw["id"], start, start + SHOT_FRAMES, camera, beat, focus, motion, intent, hold))
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
    from .operator import operator_metadata

    return {
        "operator": operator_metadata(),
        "contract": VERSION,
        "shot_frames": SHOT_FRAMES,
        "max_frames": MAX_FRAMES,
        "max_audio_frames": CHUNK_SHOTS * SHOT_FRAMES,
        "worlds": WORLD_KITS,
        "contract_versions": [VERSION, STAGED_VERSION],
        "staged_cameras": [*CAMERAS, "two_shot", "auto"],
        "camera_motions": MOTIONS,
        "shot_intents": INTENTS,
        "pacing_styles": {name: {"anticipation_frames": values[0],
                                 "clip_speed": [values[1], values[2]]}
                          for name, values in PACING.items()},
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
