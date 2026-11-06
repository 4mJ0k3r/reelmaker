"""One trusted, self-contained editorial recipe over registered Cold Ridge assets."""

from copy import deepcopy

from reelforge.characters.registry import YELLOW_MELLOW_ID
from reelforge.episodes.contract import compile_episode

from .character_staging import _shot, cinematic_character_staging


def _insert(title, world, shot):
    return dict(schema_version="direction-0.1", title=title, base=world, shots=[shot])


def cinematic_story(story="the_other_light"):
    """Return an admitted original or refined Yellow Mellow / Cold Ridge episode."""
    if story not in ("the_other_light", "the_other_light_refined"):
        raise ValueError("Select the_other_light or the_other_light_refined")
    approach = cinematic_character_staging(YELLOW_MELLOW_ID, "cold_ridge")
    blocking = approach["base"]
    opening = deepcopy(blocking["base"])
    # Object inserts keep the traveler out of frame. The camera never shows a new pose.
    opening["nodes"] = [node for node in opening["nodes"] if node["id"] != blocking["actor_id"]]
    ending = deepcopy(opening)
    ending["nodes"].append(
        dict(
            id="distant_light",
            kind="asset",
            parent="massif",
            order=1,
            visible=True,
            asset_id="answer_light_01",
            variant="default",
            transform=dict(x=285, y=303, scale=1.15, rotation_degrees=0),
        )
    )
    beacon = _insert(
        "A light in the pass",
        opening,
        _shot(
            "beacon_insert",
            0,
            90,
            "close_up",
            {"kind": "node", "id": "beacon"},
            [2.55, 3.65],
            (164, 472),
            offset_y=-26,
            framing="offscreen",
        ),
    )
    ridge = _insert(
        "The other light",
        ending,
        _shot(
            "ridge_reveal",
            0,
            90,
            "object_reveal",
            {"kind": "node", "id": "distant_light"},
            [1.56, 1.7],
            (218, 265),
            framing="offscreen",
        ),
    )
    episode = dict(
        schema_version="episode-0.3",
        title="The Other Light",
        segments=[
            dict(id="beacon", direction=beacon),
            dict(id="approach", direction=approach),
            dict(id="ridge", direction=ridge),
        ],
        audio=None,
    )
    if story == "the_other_light_refined":
        _refine(episode, blocking["base"])
    compile_episode(episode)
    return episode


def _refine(episode, approach_world):
    opening, approach, ending = (s["direction"] for s in episode["segments"])
    # Same fixed actor node and ground as the first instant of the approved walk.
    opening["base"] = deepcopy(approach_world)
    beacon_target = {"kind": "node", "id": "beacon"}
    opening["shots"] = [
        _shot(
            "traveler_and_beacon", 0, 28, "object_reveal", beacon_target, [1.62, 1.56], (267, 507)
        ),
        _shot(
            "ridge_geography", 28, 90, "establishing", beacon_target, [1.14, 1.08], (247, 484)
        ),
    ]
    beacon = next(n for n in approach["base"]["base"]["nodes"] if n["id"] == "beacon")
    beacon["variant"] = "ridge_surge"
    light = next(n for n in ending["base"]["nodes"] if n["id"] == "distant_light")
    light["variant"] = "ridge_reveal"
    ending["shots"][0].update(zoom=[1.48, 1.62], screen=[207, 262], hold_out_frames=30)
