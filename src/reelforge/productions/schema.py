"""Advisory production-0.1 schema; semantic validation lives in the compiler as elsewhere."""

from reelforge.geometry.schema import array, obj
from reelforge.reels.schema import reel_schema


def production_schema() -> dict:
    reel = reel_schema()
    storyboard = reel["properties"]["storyboard"]
    return {
        "$schema": reel["$schema"],
        "$id": "urn:reelforge:production-0.1",
        "$defs": reel["$defs"],
        **obj(
            {
                "schema_version": {"const": "production-0.1"},
                "title": {"type": "string", "minLength": 1, "maxLength": 120},
                "segments": array(
                    obj(
                        {
                            "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,47}$"},
                            "storyboard": storyboard,
                        }
                    ),
                    2,
                    20,
                ),
                "audio": {"type": "null"},
            }
        ),
    }
