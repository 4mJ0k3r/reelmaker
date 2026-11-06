"""Structural schemas for bounded episodes; nested semantic admission is mandatory."""

from reelforge.direction.schema import direction_schema
from reelforge.geometry.schema import array, obj
from reelforge.reels.schema import reel_schema


def episode_schema():
    reel = reel_schema()
    audio = reel["properties"]["audio"]
    audio["properties"]["narration"]["anyOf"][1]["properties"]["start_frame"]["maximum"] = 899
    audio["properties"]["cues"]["items"]["properties"]["start_frame"]["maximum"] = 899
    identity = {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,47}$"}
    storyboard = obj({"id": identity, "storyboard": reel["properties"]["storyboard"]})
    registered_world = {
        "properties": {"schema_version": {"enum": ["scene-0.1", "environment-0.1"]}},
        "required": ["schema_version"],
    }
    blocking_world = {
        "properties": {
            "schema_version": {"enum": ["blocking-0.1", "blocking-0.2"]},
            "base": registered_world,
        },
        "required": ["schema_version", "base"],
    }
    directed = direction_schema()
    directed["properties"]["base"]["allOf"] = [{"oneOf": [registered_world, blocking_world]}]
    direction = obj({"id": identity, "direction": directed})
    registered_storyboard = {
        "properties": {"storyboard": {"properties": {"world": registered_world}}}
    }
    return {
        "$schema": reel["$schema"],
        "$id": "urn:reelforge:episode-0.3",
        "$defs": reel["$defs"],
        **obj(
            {
                "schema_version": {"enum": ["episode-0.1", "episode-0.2", "episode-0.3"]},
                "title": {"type": "string", "minLength": 1, "maxLength": 120, "pattern": r"\S"},
                "segments": array({"oneOf": [storyboard, direction]}, 1, 10),
                "audio": {"anyOf": [audio, {"type": "null"}]},
            }
        ),
        "allOf": [
            {
                "if": {"properties": {"schema_version": {"enum": ["episode-0.1", "episode-0.2"]}}},
                "then": {"properties": {"segments": {"items": {"required": ["storyboard"]}}}},
            },
            {
                "if": {"properties": {"schema_version": {"const": "episode-0.3"}}},
                "then": {"properties": {"segments": {"items": registered_storyboard}}},
            },
            {
                "if": {"properties": {"schema_version": {"const": "episode-0.1"}}},
                "then": {"properties": {"audio": {"type": "object"}}},
            },
        ],
    }
