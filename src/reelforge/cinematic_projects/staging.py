"""Finite actor staging helpers for cinematic-project-0.2."""

from dataclasses import dataclass, replace

from reelforge.characters import living, living_transitions
from reelforge.characters.contact import ease
from reelforge.characters.rig import Rigid

# anticipation frames, then rational clip speed. No camera or wall clock enters this map.
CUE_STYLES = ("alert", "relief", "alert_settle", "relief_settle", "relief_recognize")
STAGED_TRANSITIONS = (*living_transitions.TRANSITIONS, "walk_to_settle")
LOCOMOTION = ("walk", "run", "idle_to_walk", "walk_to_stop", "walk_to_settle")
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
    if action == "walk_to_settle":
        frame = min(frame, living_transitions.FRAMES - 1)
        return living_transitions.sample_settled_stop(performer.actor, frame).pose, frame
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
    recognize = style == "relief_recognize"
    polished = recognize or style.endswith("_settle")
    alert = style.startswith("alert")
    if elapsed <= 0:
        if polished:
            listen = ease((since_cue + 43) / 18) * (1 - ease((since_cue + 16) / 16))
            if listen:
                pose = _planted_upper_body(performer.actor, pose, listen, 0)
        return pose, performer.expression

    action = "react" if alert else "notice"
    weight = ease(elapsed / 8) * (1 - ease((elapsed - 34) / 18))
    if weight:
        response = living.sample_pose(performer.actor, action, min(elapsed, 48) / 30, refined=True)
        angles = dict(pose.angles)
        for joint, angle in response.angles:
            angles[joint] = living_transitions.mix(angles[joint], angle, weight)
        root = Rigid(pose.root.x, living_transitions.mix(pose.root.y, response.root.y, weight))
        pose = living_transitions.replant(performer.actor, root, angles, ((-10, -5), (10, -5)))

    if polished:
        recoil = ease(elapsed / 9) * (1 - ease((elapsed - 17) / 23))
        if recoil:
            pose = _planted_upper_body(performer.actor, pose, 0, recoil)
    if recognize:
        reach = ease((elapsed - 5) / 12) * (1 - ease((elapsed - 28) / 21))
        if reach:
            angles = dict(pose.angles)
            # Mira lifts her hand toward the signal. Bram answers with a
            # smaller arm lift and a forward change of weight.
            mira = performer.actor == "scout_01"
            angles["near_shoulder"] -= (.52 if mira else .28) * reach
            angles["near_elbow"] -= (.92 if mira else .58) * reach
            angles["head"] -= (.16 if mira else .10) * reach
            angles["torso"] += (.04 if mira else .17) * reach
            pose = living_transitions.replant(
                performer.actor, pose.root, angles, ((-10, -5), (10, -5))
            )
    expression = performer.expression
    if not alert and elapsed >= 14:
        expression = "happy"
    elif 4 <= elapsed < 30:
        expression = "frightened" if alert else "surprised"
    return pose, expression


def _planted_upper_body(identity, pose, listen, recoil):
    angles = dict(pose.angles)
    # Mira's response is brisk. Bram's smaller turn favours the shoulder.
    torso = .16 if identity == "scout_01" else .10
    shoulder = .14 if identity == "scout_01" else .23
    angles["torso"] += .08 * listen - torso * recoil
    angles["head"] += .15 * listen - .11 * recoil
    angles["near_shoulder"] -= shoulder * recoil
    angles["far_shoulder"] += .08 * recoil
    root = Rigid(pose.root.x, pose.root.y + 2.8 * recoil)
    return living_transitions.replant(identity, root, angles, ((-10, -5), (10, -5)))


def face_left(commands):
    """Reflect each trusted actor path, preserving local gradients and clips."""
    return tuple(replace(command, transform=replace(
        command.transform, tx=-command.transform.tx, rotation=-command.transform.rotation,
        sx=-command.transform.sx,
    )) for command in commands)
