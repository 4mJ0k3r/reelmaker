"""Finite actor staging helpers for cinematic-project-0.2."""

from dataclasses import dataclass, replace

from reelforge.characters import living, living_transitions


@dataclass(frozen=True)
class Performer:
    actor: str
    action: str
    expression: str
    facing: str
    delay: int


def pose_at(performer, local, *, refined):
    frame = max(0, local - performer.delay)
    action = performer.action if local >= performer.delay else "idle"
    if action in living_transitions.TRANSITIONS:
        frame = min(frame, living_transitions.FRAMES - 1)
        return living_transitions.sample_transition(
            performer.actor, action, frame, refined=refined
        ).pose, frame
    return living.sample_pose(performer.actor, action, frame / 30, refined=refined), frame


def face_left(commands):
    """Reflect each trusted actor path, preserving local gradients and clips."""
    return tuple(replace(command, transform=replace(
        command.transform, tx=-command.transform.tx, rotation=-command.transform.rotation,
        sx=-command.transform.sx,
    )) for command in commands)
