"""Finite actor staging helpers for cinematic-project-0.2."""

from dataclasses import dataclass, replace

from reelforge.characters import living, living_transitions
from reelforge.characters.contact import ease
from reelforge.characters.rig import Rigid

# anticipation frames, then rational clip speed. No camera or wall clock enters this map.
CUE_STYLES = ("alert", "relief")
PACING = {"measured": (12, 1, 1), "tense": (24, 3, 2), "urgent": (0, 2, 1)}


def performer_clock(performer, local):
    anticipation, numerator, denominator = PACING.get(performer.pacing, (0, 1, 1))
    elapsed = local - performer.delay - anticipation
    # Living clips admit at most twelve seconds; faster styles hold that endpoint.
    return min(360, max(0, elapsed) * numerator // denominator), elapsed >= 0


@dataclass(frozen=True)
class Performer:
    actor: str
    action: str
    expression: str
    facing: str
    delay: int
    pacing: str | None = None


def pose_at(performer, local, *, refined):
    frame, active = performer_clock(performer, local)
    action = performer.action if active else "idle"
    if action in living_transitions.TRANSITIONS:
        frame = min(frame, living_transitions.FRAMES - 1)
        return living_transitions.sample_transition(
            performer.actor, action, frame, refined=refined
        ).pose, frame
    return living.sample_pose(performer.actor, action, frame / 30, refined=refined), frame


def grounded_signal_response(performer, pose, since_cue, style):
    """Layer one stationary response over idle while keeping both feet planted."""
    anticipation, _, _ = PACING.get(performer.pacing, (0, 1, 1))
    elapsed = since_cue - performer.delay - anticipation
    if elapsed <= 0:
        return pose, performer.expression

    action = "react" if style == "alert" else "notice"
    weight = ease(elapsed / 8) * (1 - ease((elapsed - 34) / 18))
    if weight:
        response = living.sample_pose(performer.actor, action, min(elapsed, 48) / 30, refined=True)
        angles = dict(pose.angles)
        for joint, angle in response.angles:
            angles[joint] = living_transitions.mix(angles[joint], angle, weight)
        root = Rigid(pose.root.x, living_transitions.mix(pose.root.y, response.root.y, weight))
        pose = living_transitions.replant(performer.actor, root, angles, ((-10, -5), (10, -5)))

    expression = performer.expression
    if style == "relief" and elapsed >= 14:
        expression = "happy"
    elif 4 <= elapsed < 30:
        expression = "frightened" if style == "alert" else "surprised"
    return pose, expression


def face_left(commands):
    """Reflect each trusted actor path, preserving local gradients and clips."""
    return tuple(replace(command, transform=replace(
        command.transform, tx=-command.transform.tx, rotation=-command.transform.rotation,
        sx=-command.transform.sx,
    )) for command in commands)
