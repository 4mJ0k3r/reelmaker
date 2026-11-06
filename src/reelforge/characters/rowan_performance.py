"""One authored Rowan acting beat layered over a fixed-facing, planted approach."""

from dataclasses import dataclass, replace

from .contact import ease, plant_feet
from .presets import SKELETON
from .rig import Pose, Rigid
from .secondary import settling_response

NAME = "notice_and_react"
REACTIONS = ("surprised", "frightened")


def performance_schema():
    return {
        "type": "object",
        "properties": {"name": {"const": NAME}, "reaction": {"enum": list(REACTIONS)}},
        "required": ["name", "reaction"],
        "additionalProperties": False,
    }


@dataclass(frozen=True)
class FaceCue:
    source: str
    target: str
    amount: float
    closure: float


def _ramp(frame, start, duration):
    return ease((frame - start) / duration)


def face_cue(frame, brake, hold, reaction):
    """Blend the same facial contours through each beat, with one settle blink."""
    flash = hold + 6
    if frame < flash:
        source, target, amount = "calm", "concerned", _ramp(frame, brake - 2, hold - brake + 5)
    elif frame < hold + 18:
        source, target, amount = "concerned", reaction, _ramp(frame, flash, 5)
    else:
        source, target, amount = reaction, "concerned", _ramp(frame, hold + 18, 7)
    # Blink once after the surprise peak. Onset and reopening are both eased.
    closure = _ramp(frame, hold + 21, 2) * (1 - _ramp(frame, hold + 23, 3))
    return FaceCue(source, target, amount, closure)


def apply_performance(pose, feet, distance, secondary, frame, brake, hold, reaction):
    """Change only Rowan's local balance and acting, then reuse the planted leg solve."""
    attention = _ramp(frame, brake - 7, 7)
    if not attention:
        return pose, secondary
    head = _ramp(frame, brake - 4, 9)
    concern = _ramp(frame, brake + 1, hold - brake + 6)
    release = _ramp(frame, hold + 18, 7)
    lean_back = _ramp(frame, hold + 9, 8) * (1 - 0.82 * release)
    head_recoil = _ramp(frame, hold + 7, 7) * (1 - 0.9 * release)
    guard = _ramp(frame, hold + 11, 7) * (1 - 0.83 * release)
    fear = 1.15 if reaction == "frightened" else 1
    angles = dict(pose.angles)
    angles["head"] += 0.17 * head - 0.11 * head_recoil
    angles["neck"] += 0.055 * head
    angles["torso"] += 0.095 * concern - 0.24 * lean_back * fear
    angles["scarf"] -= 0.19 * _ramp(frame, hold + 12, 6) * (1 - release)
    angles["near_arm"] += -0.13 * concern - 0.28 * guard * fear
    angles["near_forearm"] += -0.30 * concern - 1.03 * guard * fear
    angles["near_hand"] += 0.26 * guard
    angles["far_arm"] += 0.19 * lean_back
    angles["far_forearm"] -= 0.66 * guard * fear
    shifted = Pose(
        Rigid(
            pose.root.x + distance + 1.25 * concern - 4.1 * lean_back * fear,
            pose.root.y + 0.65 * concern + 3.1 * lean_back,
        ),
        tuple(angles.items()),
    )
    solved = plant_feet(shifted, feet, SKELETON)
    overlap = settling_response(max(0, (frame - hold - 8) / 30)) * (1 - release)
    return replace(solved, root=Rigid(solved.root.x - distance, solved.root.y)), replace(
        secondary,
        gaze=secondary.gaze * (1 - attention) + 0.92 * attention,
        hat_angle=secondary.hat_angle - 0.045 * overlap,
        hat_y=secondary.hat_y - 0.65 * overlap,
        bag_angle=secondary.bag_angle + 0.12 * overlap,
        bag_y=secondary.bag_y + 0.92 * overlap,
        strap_sag=secondary.strap_sag + 1.5 * overlap,
    )
