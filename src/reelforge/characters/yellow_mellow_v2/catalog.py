"""Trusted V2 character metadata and ground-origin drawing adapter.

Yellow Mellow V2 can be selected by validated blocking and storyboard timelines.
The standalone command adapter also exposes the native action vocabulary.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from reelforge.rendering.model import DrawPath, RenderError, finite

from .character import ActionRequest, Stage, YellowMellowV2
from .expressions import EXPRESSIONS
from .motions import LOCOMOTION_ACTIONS, PRESETS
from .rig import STANDING_HEIGHT


@dataclass(frozen=True)
class CatalogEntry:
    character_id: str
    display_name: str
    standing_height_units: float
    actions: tuple[str, ...]
    expressions: tuple[str, ...]
    episode_integrated: bool
    notes: str


CATALOG: dict[str, CatalogEntry] = {
    "yellow_mellow_v2": CatalogEntry(
        "yellow_mellow_v2",
        "Yellow Mellow",
        STANDING_HEIGHT,
        tuple(sorted(PRESETS)) + LOCOMOTION_ACTIONS,
        tuple(sorted(EXPRESSIONS)),
        True,
        "Executable in blocking-0.2 and storyboard-0.1 with the registered V2 drawer.",
    )
}


def scale_for_height(logical_height: float) -> float:
    """Character scale that makes the standing figure ``logical_height`` units tall."""
    finite(logical_height)
    if not 20 <= logical_height <= 1200:
        raise RenderError("logical height must be 20..1200")
    return logical_height / STANDING_HEIGHT


def command_source(
    character_id: str,
    requests: list[ActionRequest],
    *,
    scale: float = 1.0,
    seed: str = "yellow_mellow_v2",
) -> tuple[int, Callable[[int], tuple[DrawPath, ...]]]:
    """Return (frame count, frame -> commands) placed with the ground origin at (0, 0).

    Root travel is kept in world space (like Rowan's ``preset_commands``); a compositor or
    camera owns final framing.
    """
    if character_id not in CATALOG:
        raise RenderError(f"Unknown character {character_id!r}; catalog has {sorted(CATALOG)}")
    perf = YellowMellowV2(seed=seed).animate(requests)
    stage = Stage(x=0.0, ground_y=0.0, scale=scale)

    def commands(frame: int) -> tuple[DrawPath, ...]:
        return perf.draw(frame, stage)

    return perf.frames, commands
