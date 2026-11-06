"""A fixed second story over the existing Rowan and Dusk Farm direction."""

from copy import deepcopy

from reelforge.characters.registry import ROWAN_ID
from reelforge.episodes.contract import compile_episode

from .character_staging import _shot, cinematic_character_staging


def cinematic_farm_story(story="the_empty_doorway"):
    """Return the admitted silent 270-frame Empty Doorway episode."""
    if story != "the_empty_doorway":
        raise ValueError("Select the_empty_doorway")
    approach = cinematic_character_staging(ROWAN_ID, "farm")
    blocking = approach["base"]
    world = deepcopy(blocking["base"])
    actor = next(n for n in world["nodes"] if n["id"] == blocking["actor_id"])
    actor["character"].update(action="idle", expression="calm")
    barn = {"kind": "node", "id": "barn"}
    context, follow, reaction = approach["shots"]
    arrival = {
        **deepcopy(context),
        "id": "arrival",
        "end_frame": 90,
        "zoom": [0.96, context["zoom"][0]],
    }
    follow["end_frame"] = 31
    insert = _shot(
        "doorway_movement",
        31,
        reaction["start_frame"],
        "close_up",
        barn,
        [2.42, 2.42],
        (155, 446),
        offset_y=-28,
        framing="offscreen",
    )
    approach["shots"].insert(2, insert)
    next(n for n in blocking["base"]["nodes"] if n["id"] == "barn")["variant"] = (
        "doorway_shadow"
    )
    empty_world = deepcopy(world)
    empty_world["nodes"] = [n for n in empty_world["nodes"] if n["id"] != actor["id"]]
    empty = {
        **deepcopy(insert),
        "id": "empty_doorway",
        "start_frame": 0,
        "end_frame": 90,
        "zoom": [2.42, 2.60],
        "hold_in_frames": 12,
        "hold_out_frames": 20,
        "continuity": "matched",
    }

    episode = dict(
        schema_version="episode-0.3",
        title="The Empty Doorway",
        segments=[
            dict(
                id="arrival",
                direction=dict(
                    schema_version="direction-0.1", title="Arrival", base=world, shots=[arrival]
                ),
            ),
            dict(id="movement", direction=approach),
            dict(
                id="empty_doorway",
                direction=dict(
                    schema_version="direction-0.1",
                    title="Empty doorway",
                    base=empty_world,
                    shots=[empty],
                ),
            ),
        ],
        audio=None,
    )
    compile_episode(episode)
    return episode
