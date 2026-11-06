"""Three admitted camera shots over an existing character performance."""

import json

from reelforge.characters.registry import ROWAN_ID, YELLOW_MELLOW_ID
from reelforge.direction.contract import compile_direction
from reelforge.storyboards.compiler import compile_storyboard

from .mellow_approach import mellow_storyboard
from .rowan_approach import rowan_storyboard

WORLDS = {"farm": ("barn", (263, 415)), "cold_ridge": ("beacon", (247, 484))}
_BUILDERS = {ROWAN_ID: rowan_storyboard, YELLOW_MELLOW_ID: mellow_storyboard}


def _shot(
    name, start, end, behavior, target, zoom, screen, *, track=False, offset_y=0, framing="full"
):
    return dict(
        id=name,
        start_frame=start,
        end_frame=end,
        behavior=behavior,
        target=target,
        track=track,
        look_ahead_seconds=0,
        zoom=zoom,
        offset_start=[0, offset_y],
        offset_end=[0, offset_y],
        screen=list(screen),
        hold_in_frames=0,
        hold_out_frames=0,
        framing=framing,
        safe_margin=8,
        foreground="clear",
        continuity="intentional_reframe" if start else "matched",
    )


def cinematic_character_staging(character, world):
    """Build and admit a direction-0.1 manifest for either trusted performance and World Kit."""
    if not isinstance(character, str) or character not in _BUILDERS:
        raise ValueError("Select rowan_01 or yellow_mellow_v2")
    if not isinstance(world, str) or world not in WORLDS:
        raise ValueError("Select farm or cold_ridge")

    original = compile_storyboard(_BUILDERS[character](world, "medium"))
    base = json.loads(original.direction_json)["base"]
    actor = {"kind": "actor", "id": base["actor_id"]}
    target_id, context_screen = WORLDS[world]
    settle = base["segments"][-1]["start_frame"]
    # The V2 episode sprite is much shorter than Rowan's in these approved assemblies.
    # Use distinct, measured framing and cut shortly before each rig's facial change.
    if character == YELLOW_MELLOW_ID:
        medium, close = 1.70, (3.05, 4.00)
        reaction_frame, floor, reaction_x = settle + 3, 643, 151
    else:
        medium, close = 1.55, (2.60, 2.78)
        reaction_frame, floor, reaction_x = settle + 3, 651, 136
    context_end = 22
    close_offset = -18
    close_screen = (reaction_x, floor + close[0] * close_offset)
    direction = dict(
        schema_version="direction-0.1",
        title=base["title"],
        base=base,
        shots=[
            _shot(
                "context",
                0,
                context_end,
                "establishing",
                {"kind": "node", "id": target_id},
                [1.08, 1.08],
                context_screen,
            ),
            _shot(
                "attention",
                context_end,
                reaction_frame,
                "follow",
                actor,
                [medium, medium],
                (129, 526),
                track=True,
            ),
            _shot(
                "reaction",
                reaction_frame,
                90,
                "close_up",
                actor,
                list(close),
                close_screen,
                track=True,
                offset_y=close_offset,
                framing="feet_crop",
            ),
        ],
    )
    compile_direction(direction)
    return direction
