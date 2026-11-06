"""The same Yellow Mellow approach at the farm door or Cold Ridge beacon."""

from reelforge.characters.registry import YELLOW_MELLOW_ID
from reelforge.characters.yellow_mellow_v2.investigation import NAME, REACTION

from .rowan_approach import rowan_storyboard


def mellow_storyboard(world, view="establishing", *, legacy=False):
    """Use the established camera and staging, with the V2 standing-height convention."""
    data = rowan_storyboard(world, view, legacy=True)
    data["title"] = "Yellow Mellow investigates a signal"
    actor = data["rowan"]
    actor["character"] = YELLOW_MELLOW_ID
    if not legacy:
        actor["performance"] = {"name": NAME, "reaction": REACTION}
    node = next(n for n in data["world"]["nodes"] if n["id"] == actor["actor_id"])
    node["asset_id"] = YELLOW_MELLOW_ID
    node["transform"]["scale"] = 0.64
    node["character"] = dict(character=YELLOW_MELLOW_ID, action="idle", expression="neutral")
    start_x = actor["start"]["position"][0]
    walk, brake, acting = data["beats"]
    walk.update(
        frames=40,
        action=dict(kind="walk_to", expression="neutral", end_x=start_x + 40.5, end_speed=44),
    )
    brake.update(
        frames=14,
        action=dict(kind="stop_at", expression="curious", end_x=start_x + 40.5 + 44 * 14 / 60),
    )
    acting.update(frames=36, action=dict(kind="react", expression="surprised"))
    return data
