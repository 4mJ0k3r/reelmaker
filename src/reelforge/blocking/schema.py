"""Structural blocking schema. Continuous motion/support admission remains mandatory."""

from reelforge.characters.presets import EXPRESSIONS
from reelforge.characters.registry import ROWAN_ID, YELLOW_MELLOW_ID, character_info
from reelforge.characters.rowan_performance import performance_schema as rowan_performance_schema
from reelforge.characters.yellow_mellow_v2.investigation import NAME as MELLOW_NAME
from reelforge.characters.yellow_mellow_v2.investigation import REACTION as MELLOW_REACTION
from reelforge.geometry.schema import array, composition_schema, number, obj
from reelforge.procedural.schema import environment_schema
from reelforge.scenes.schema import scene_schema


def is_yellow_mellow():
    return {
        "required": ["character"],
        "properties": {"character": {"const": YELLOW_MELLOW_ID}},
    }


def actor_performance_schema():
    """Character-scoped selector rules shared by blocking and storyboard."""
    return {
        "if": is_yellow_mellow(),
        "then": {
            "properties": {
                "performance": obj(
                    {
                        "name": {"const": MELLOW_NAME},
                        "reaction": {"const": MELLOW_REACTION},
                    }
                )
            }
        },
        "else": {"properties": {"performance": rowan_performance_schema()}},
    }


def blocking_schema():
    identity = {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,47}$"}
    point = array(number(0, 640), 2, 2)
    facing = {"enum": ["left", "right"]}
    composition = composition_schema()

    # Its geometry refs are rooted in this embedding, not external files or resources.
    def rewrite(value):
        if isinstance(value, dict):
            return {
                k: (
                    "#/$defs/composition/$defs/geometry/$defs/shape"
                    if k == "$ref" and v == "#/$defs/geometry/$defs/shape"
                    else "#/$defs/composition/$defs/geometry"
                    if k == "$ref" and v == "#/$defs/geometry"
                    else rewrite(v)
                )
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [rewrite(v) for v in value]
        return value

    composition = rewrite(composition)
    composition.pop("$id", None)
    yellow_expressions = character_info(YELLOW_MELLOW_ID).expressions
    return {
        "allOf": [
            {
                "if": {"properties": {"schema_version": {"const": "blocking-0.1"}}},
                "then": {
                    "not": {"anyOf": [{"required": ["performance"]}, {"required": ["character"]}]}
                },
            },
            actor_performance_schema(),
            {
                "if": is_yellow_mellow(),
                "then": {
                    "properties": {
                        "segments": {
                            "items": {
                                "properties": {"expression": {"enum": list(yellow_expressions)}}
                            }
                        }
                    }
                },
                "else": {
                    "properties": {
                        "segments": {
                            "items": {"properties": {"expression": {"enum": list(EXPRESSIONS)}}}
                        }
                    }
                },
            },
        ],
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:reelforge:blocking-0.1",
        "$defs": {"composition": composition},
        **obj(
            {
                "schema_version": {"enum": ["blocking-0.1", "blocking-0.2"]},
                "character": {"enum": [ROWAN_ID, YELLOW_MELLOW_ID]},
                "performance": {"type": "object"},
                "title": {"type": "string", "minLength": 1, "maxLength": 120},
                "base": {
                    "oneOf": [scene_schema(), environment_schema(), {"$ref": "#/$defs/composition"}]
                },
                "actor_id": identity,
                "support_id": identity,
                "corridor": {"const": "level_field"},
                "start": obj({"position": point, "facing": facing}),
                "camera": {"enum": ["base", "locked", "exit_right"]},
                "segments": array(
                    obj(
                        {
                            "id": identity,
                            "start_frame": {"type": "integer", "minimum": 0, "maximum": 90},
                            "end_frame": {"type": "integer", "minimum": 0, "maximum": 90},
                            "mode": {"enum": ["idle", "walk", "run", "stop", "turn"]},
                            "destination": point,
                            "end_speed": number(0, 90),
                            "facing": facing,
                            "acting": {
                                "enum": ["idle", "look_around", "react", "activate", "none"]
                            },
                            "expression": {"type": "string"},
                        }
                    ),
                    1,
                    12,
                ),
            },
            optional=("character", "performance"),
        ),
    }
