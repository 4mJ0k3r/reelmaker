"""Structural contract for the cinematic project editor."""

from reelforge.characters.living import ACTIONS, EXPRESSIONS, PROFILES
from reelforge.characters.living_transitions import TRANSITIONS
from reelforge.episodes.schema import episode_schema
from reelforge.geometry.schema import array, obj
from reelforge.productions.contract import FRAMES_PER_SEGMENT, MAX_SEGMENTS
from reelforge.scenes.assets import asset_by_id
from reelforge.visual_library.composition.interactions import INTERACTIONS
from reelforge.visual_library.composition.living_worlds import WORLD_KITS
from reelforge.visual_library.living_assets import EFFECTS

VERSION = "cinematic-project-0.1"
EFFECT_IDS = (*EFFECTS, "ground_mist_01")
SIGNAL = "streetlamp_01"
DRESSING = {
    "delivered_parcel": ("village_lane", "parcel_01", "wrapped", 159, 587, 0.78),
    "parked_cart": ("woodland_creek", "handcart_01", "loaded", 213, 587, 0.78),
}
CAMERAS = (
    "establishing",
    "medium",
    "close_up",
    "interaction_detail",
    "object_reveal",
    "reaction",
    "follow",
    "atmospheric_close",
)
CAPTION_STYLES = ("subtitle", "chapter", "lower_third")
CAPTION_LINE = r"[A-Za-z0-9 .,!?':&()\-]{1,32}"
TITLE = r"^[A-Za-z0-9][A-Za-z0-9 .,!?':&()\-]{0,119}$"
ID = {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,47}$"}
MAX_FRAMES = FRAMES_PER_SEGMENT * MAX_SEGMENTS


def choice(values):
    return {"enum": list(values)}


def integer(lo, hi):
    return {"type": "integer", "minimum": lo, "maximum": hi}


def project_schema():
    span = {
        "start": integer(0, MAX_FRAMES - 1),
        "end": integer(1, MAX_FRAMES),
    }
    beat = obj(
        {
            "id": ID,
            **span,
            "actor": choice((*PROFILES, "rowan_01")),
            "world": choice(WORLD_KITS),
            "mood": choice(sorted({m for moods in WORLD_KITS.values() for m in moods})),
            "action": choice((*ACTIONS, *TRANSITIONS, *INTERACTIONS)),
            "expression": choice(EXPRESSIONS),
            "stage_x": integer(36, 276),
            "variant": choice(sorted({v for spec in INTERACTIONS.values() for v in spec.variants})),
            "effect": obj(
                {
                    "id": choice(EFFECT_IDS),
                    "variant": choice(
                        sorted({v for i in EFFECT_IDS for v in asset_by_id(i).variants})
                    ),
                }
            ),
            "signal": choice(("unlit", "lit")),
            "dressing": choice(DRESSING),
        },
        ("expression", "stage_x", "variant", "effect", "signal", "dressing"),
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:reelforge:{VERSION}",
        **obj(
            {
                "schema_version": {"const": VERSION},
                "title": {"type": "string", "pattern": TITLE, "maxLength": 120},
                "beats": array(beat, 1, MAX_SEGMENTS),
                "shots": array(obj({"id": ID, "camera": choice(CAMERAS)}), 1, MAX_SEGMENTS),
                "captions": array(
                    obj(
                        {
                            **span,
                            "style": choice(CAPTION_STYLES),
                            "lines": array(
                                {"type": "string", "pattern": f"^{CAPTION_LINE}$", "maxLength": 32},
                                1,
                                2,
                            ),
                        }
                    ),
                    0,
                    24,
                ),
                "audio": episode_schema()["properties"]["audio"],
            }
        ),
    }
