"""Native-free episode admission and inspection over independent visual segments."""

from dataclasses import dataclass
from pathlib import Path

from reelforge.audio.registry import AudioRegistry
from reelforge.contracts.project import load_project
from reelforge.core.errors import InputError, Issue
from reelforge.direction.contract import Direction, compile_direction
from reelforge.direction.sampling import inspect_frame as inspect_direction_frame
from reelforge.reels.contract import cue_schedule, metadata_plan
from reelforge.scenes.contract import identifier
from reelforge.stories.audio_contract import AudioPlan, audio_from_data
from reelforge.storyboards.compiler import (
    Storyboard,
    bounded_copy,
    compile_storyboard,
    inspect_beats,
    inspect_frame,
)


@dataclass(frozen=True)
class Segment:
    id: str
    storyboard: Storyboard

    @property
    def direction(self) -> Direction:
        return self.storyboard.direction


@dataclass(frozen=True)
class DirectionSegment:
    id: str
    direction: Direction


@dataclass(frozen=True)
class Episode:
    title: str
    segments: tuple[Segment | DirectionSegment, ...]
    audio: AudioPlan | None
    schema_version: str = "episode-0.2"

    @property
    def frames(self) -> int:
        return len(self.segments) * 90

    @property
    def silent(self) -> bool:
        return self.audio is None

    @property
    def report_contract(self) -> str:
        if self.schema_version == "episode-0.3":
            return self.schema_version
        # Preserve historical report labels, which distinguished silent from audio episodes.
        return "episode-0.2" if self.silent else "episode-0.1"


def fail(path, message):
    raise InputError(Issue("EPISODE_INVALID", path, message))


def require_registered_world(world, path):
    if not isinstance(world, dict) or world.get("schema_version") not in (
        "scene-0.1",
        "environment-0.1",
    ):
        fail(
            path, "Embed a registered scene or procedural environment; custom geometry is excluded"
        )


def compile_episode(data: object) -> Episode:
    d = bounded_copy(data)
    if not isinstance(d, dict) or set(d) != {"schema_version", "title", "segments", "audio"}:
        fail("", "Use exactly schema_version, title, segments, audio")
    if d["schema_version"] not in ("episode-0.1", "episode-0.2", "episode-0.3"):
        fail("/schema_version", "Use episode-0.1, episode-0.2 or episode-0.3")
    version = d["schema_version"]
    if not isinstance(d["title"], str) or not d["title"].strip() or len(d["title"]) > 120:
        fail("/title", "Use nonblank text <=120 characters")
    if not isinstance(d["segments"], list) or not 1 <= len(d["segments"]) <= 10:
        fail("/segments", "Use 1..10 ordered 90-frame segments")
    segments = []
    seen = set()
    for i, item in enumerate(d["segments"]):
        path = f"/segments/{i}"
        keys = set(item) if isinstance(item, dict) else set()
        if keys == {"id", "storyboard"}:
            source, compiler, segment_type = "storyboard", compile_storyboard, Segment
        elif version == "episode-0.3" and keys == {"id", "direction"}:
            source, compiler, segment_type = "direction", compile_direction, DirectionSegment
        elif version == "episode-0.3":
            fail(path, "Use id and exactly one complete storyboard or direction document")
        else:
            fail(path, "Use exactly id and storyboard; embed the complete accepted document")
        identifier(item["id"], path + "/id")
        if item["id"] in seen:
            fail(path + "/id", "Segment IDs must be unique")
        seen.add(item["id"])
        if version == "episode-0.3" and isinstance(item[source], dict):
            document = item[source]
            if source == "storyboard":
                require_registered_world(document.get("world"), path + "/storyboard/world")
            else:
                base = document.get("base")
                base_path = path + "/direction/base"
                if isinstance(base, dict) and base.get("schema_version") in (
                    "blocking-0.1",
                    "blocking-0.2",
                ):
                    require_registered_world(base.get("base"), base_path + "/base")
                else:
                    require_registered_world(base, base_path)
        try:
            segment = segment_type(item["id"], compiler(item[source]))
        except InputError as error:
            raise InputError(
                Issue(error.issue.code, f"{path}/{source}{error.issue.path}", error.issue.message)
            ) from error
        segments.append(segment)
    audio = audio_from_data(d["audio"], 90 * len(segments))
    if audio is None and version == "episode-0.1":
        fail("/audio", "Choose at least one registered narration or SFX track")
    return Episode(d["title"], tuple(segments), audio, version)


def load_episode(path: Path) -> Episode:
    return compile_episode(load_project(path))


def frame_origin(plan: Episode, frame: int) -> tuple[Segment | DirectionSegment, int]:
    if type(frame) is not int or not 0 <= frame < plan.frames:
        fail("/frame", f"Use integer frame 0..{plan.frames - 1}")
    index, local = divmod(frame, 90)
    return plan.segments[index], local


def inspect_segment(segment: Segment | DirectionSegment) -> dict:
    if isinstance(segment, Segment):
        return {"storyboard": inspect_beats(segment.storyboard)}
    return {
        "direction": {
            "contract": "direction-0.1",
            "title": segment.direction.title,
            "frames": 90,
            "fps": 30,
            "shots": [
                {
                    "id": shot.id,
                    "start": shot.start,
                    "end": shot.end,
                    "behavior": shot.behavior,
                    "target_kind": shot.target.kind,
                    "target_id": shot.target.node_id,
                }
                for shot in segment.direction.shots
            ],
        }
    }


def inspect_episode(plan: Episode, registry: AudioRegistry, frame: int | None = None) -> dict:
    cues = [] if plan.silent else cue_schedule(metadata_plan(plan, registry, plan.frames))
    result = {
        "contract": plan.report_contract,
        "title": plan.title,
        "frames": plan.frames,
        "fps": 30,
        "seconds": plan.frames / 30,
        "output": [720, 1280],
        "silent": plan.silent,
        "audio_streams": 0 if plan.silent else 1,
        "effective_samples_per_channel": 0 if plan.silent else plan.frames * 1600,
        "registry_validation": "not-applicable" if plan.silent else "metadata-only",
        "media_bytes_validated": False,
        "audio_cues": cues,
        "editorial_cuts": [i * 90 for i in range(1, len(plan.segments))],
        "acting_continuity_across_segments": False,
        "segments": [
            {
                "id": s.id,
                "start_frame": i * 90,
                "end_frame": (i + 1) * 90,
                **inspect_segment(s),
            }
            for i, s in enumerate(plan.segments)
        ],
    }
    if frame is not None:
        segment, local = frame_origin(plan, frame)
        result.update(
            global_frame=frame,
            global_sample=frame * 1600,
            segment_id=segment.id,
            local_frame=local,
            visual=(
                inspect_frame(segment.storyboard, local)
                if isinstance(segment, Segment)
                else inspect_direction_frame(segment.direction, local)
            ),
            active_cues=[c for c in cues if c["start_sample"] <= frame * 1600 < c["end_sample"]],
        )
    return result
