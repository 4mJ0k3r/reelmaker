"""Explicit trusted builders and editorial options. Requests cannot supply code."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from reelforge.visual_library.composition.cinematic_story import cinematic_story
from reelforge.visual_library.composition.farm_story import cinematic_farm_story

EPISODE_CONTRACT = "episode-0.3"
FRAMES = 270
FPS = 30
OUTPUT = (720, 1280)


@dataclass(frozen=True)
class Edit:
    id: str
    description: str
    builder: Callable[[], dict]


@dataclass(frozen=True)
class Template:
    id: str
    title: str
    description: str
    genre: str
    character: str
    world: str
    events: tuple[tuple[str, str], ...]
    edits: tuple[Edit, ...]
    default_variant: str = "approved"

    def discovery(self) -> dict:
        return {
            "template_id": self.id,
            "title": self.title,
            "description": self.description,
            "genre": self.genre,
            "character": self.character,
            "world": self.world,
            "events": [
                {"asset_id": asset, "variant": variant} for asset, variant in self.events
            ],
            "variants": [{"id": e.id, "description": e.description} for e in self.edits],
            "default_variant": self.default_variant,
            "duration_frames": FRAMES,
            "seconds": FRAMES / FPS,
            "fps": FPS,
            "output": list(OUTPUT),
            "codec": "h264",
            "pixel_format": "yuv420p",
            "episode_contract": EPISODE_CONTRACT,
            "audio": "silent",
            "status": "candidate",
            "production_ready": False,
            "limitations": [
                "Fixed character, world, event timing and duration",
                "Registered editorial options only",
            ],
        }


def _ridge_watch() -> dict:
    document = cinematic_story("the_other_light_refined")
    opening, _, ending = document["segments"]
    shots = opening["direction"]["shots"]
    # Replace the two-shot introduction with one matched wide camera move.
    shots[:] = [{**shots[1], "id": "ridge_watch", "start_frame": 0,
                 "zoom": [0.94, 1.08], "continuity": "matched"}]
    ending["direction"]["shots"][0].update(
        zoom=[1.30, 1.54], screen=[223, 237], hold_out_frames=17
    )
    return document


def _threshold_hold() -> dict:
    document = cinematic_farm_story()
    # Start on the incident's camera, then close in on the unoccupied threshold.
    document["segments"][-1]["direction"]["shots"][0].update(
        zoom=[2.42, 3.12], offset_end=[-17, -33], hold_in_frames=0, hold_out_frames=25
    )
    return document


TEMPLATES = (
    Template(
        "other_light", "The Other Light",
        "A traveler investigates a beacon and sees a second light across the ridge.",
        "mountain mystery", "yellow_mellow_v2", "cold_ridge",
        (("beacon_01", "ridge_surge"), ("answer_light_01", "ridge_reveal")),
        (
            Edit("approved", "Original refined edit.",
                 partial(cinematic_story, "the_other_light_refined")),
            Edit("ridge_watch", "One wide introduction and a wider two-light reveal.", _ridge_watch),
        ),
    ),
    Template(
        "empty_doorway", "The Empty Doorway",
        "Rowan sees a shadow cross a barn entrance. When he looks again, it is empty.",
        "rural suspense", "rowan_01", "farm",
        (("barn_01", "doorway_shadow"),),
        (
            Edit("approved", "Original farm edit.", cinematic_farm_story),
            Edit("threshold_hold", "Earlier, tighter push into the empty doorway.", _threshold_hold),
        ),
    ),
)
