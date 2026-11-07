"""Pure story-0.2 audio syntax. Files and decoders are validated by the trusted registry."""

import re
from dataclasses import dataclass

from reelforge.core.errors import InputError, Issue
from reelforge.rendering.model import finite

SAMPLE_RATE, SAMPLES_PER_FRAME = 48000, 1600


def reject(path: str, message: str) -> None:
    raise InputError(Issue("STORY_AUDIO", path, message))


def exact(data, keys: set[str], path: str) -> None:
    if not isinstance(data, dict) or set(data) != keys:
        reject(path, "Expected exactly: " + ", ".join(sorted(keys)))


@dataclass(frozen=True)
class Cue:
    asset_id: str
    start_frame: int
    trim_start_frame: int
    trim_end_frame: int | None
    gain: float


@dataclass(frozen=True)
class AudioPlan:
    sample_rate: int
    channels: int
    codec: str
    bitrate: int
    narration: Cue | None
    cues: tuple[Cue, ...]

    @property
    def tracks(self) -> tuple[Cue, ...]:
        return ((self.narration,) if self.narration else ()) + self.cues


def cue_from_data(data, frames: int, path: str, *, long_narration=False) -> Cue:
    if long_narration and isinstance(data, dict) and "start_frame" not in data:
        data = {**data, "start_frame": 0}
    trim_limit = 1800 if long_narration else 900
    exact(data, {"asset_id", "start_frame", "trim_start_frame", "trim_end_frame", "gain"}, path)
    if not isinstance(data["asset_id"], str) or not re.fullmatch(
        r"[a-z][a-z0-9_]{0,47}", data["asset_id"]
    ):
        reject(
            path + "/asset_id", "Select a registered snake_case ID; paths and URLs are forbidden"
        )
    for key, low, high in (("start_frame", 0, frames - 1), ("trim_start_frame", 0, trim_limit - 1)):
        value = data[key]
        if type(value) is not int or not low <= value <= high:
            reject(path + "/" + key, f"Use an integer frame in [{low}, {high}]")
    end = data["trim_end_frame"]
    if end is not None and (type(end) is not int or not data["trim_start_frame"] < end <= trim_limit):
        reject(
            path + "/trim_end_frame", "Use null for asset end, or an integer after trim_start_frame"
        )
    try:
        finite(data["gain"])
    except ValueError:
        reject(path + "/gain", "Gain must be a finite number in [0.05, 0.8]")
    if not 0.05 <= data["gain"] <= 0.8:
        reject(path + "/gain", "Use linear gain in [0.05, 0.8]")
    return Cue(**data)


def audio_from_data(data, frames: int, *, long_narration=False) -> AudioPlan | None:
    if data is None:
        return None
    exact(data, {"sample_rate", "channels", "codec", "bitrate", "narration", "cues"}, "/audio")
    for key, expected in (("sample_rate", 48000), ("channels", 2), ("bitrate", 128000)):
        if type(data[key]) is not int or data[key] != expected:
            reject("/audio/" + key, f"Use integer {expected}")
    if data["codec"] != "aac":
        reject("/audio/codec", "Use aac")
    if not isinstance(data["cues"], list) or len(data["cues"]) > 4:
        reject("/audio/cues", "Use at most four sound-effect cues")
    narration = (
        cue_from_data(data["narration"], frames, "/audio/narration", long_narration=long_narration)
        if data["narration"] is not None
        else None
    )
    cues = tuple(cue_from_data(c, frames, f"/audio/cues/{i}") for i, c in enumerate(data["cues"]))
    if narration is None and not cues:
        reject(
            "/audio",
            "Audio-enabled stories require a narration or cue; use audio: null for silence",
        )
    return AudioPlan(48000, 2, "aac", 128000, narration, cues)
