"""Continuous, deterministic transition clips with explicit planted-foot targets."""

import math
from dataclasses import dataclass

from reelforge.characters import living
from reelforge.characters.contact import ease
from reelforge.characters.rig import Pose, Rigid, two_bone


TRANSITIONS = ("idle_to_walk", "walk_to_stop", "idle_to_notice", "notice_to_react", "react_to_idle")
FRAMES = 90


@dataclass(frozen=True)
class TransitionSample:
    pose: Pose
    feet: tuple[tuple[float, float], ...]
    planted: tuple[bool, bool]


def mix(a, b, weight):
    return a + (b - a) * weight


def replant(identity, root, angles, feet):
    profile = living.PROFILES[identity]
    y = root.y
    limit = profile.upper + profile.lower - .25
    for sign, (x, ankle_y) in zip((-1, 1), feet, strict=True):
        dx = x - root.x - sign * 5
        y = max(y, ankle_y - math.sqrt(limit * limit - dx * dx))
    for side, sign, (x, ankle_y) in zip(("far", "near"), (-1, 1), feet, strict=True):
        hip, knee = two_bone(x-root.x-sign*5, ankle_y-y, profile.upper, profile.lower)
        angles.update({f"{side}_hip": hip, f"{side}_knee": knee, f"{side}_foot": -hip-knee})
    return Pose(Rigid(root.x, y), tuple(sorted(angles.items())))


def starting_foot(t, side):
    # Far foot steps first at .4s. Each foot alternates every .6s.
    first = 1.0 if side == "near" else .4
    initial = 10 if side == "near" else -10
    if t <= first:
        return (initial, -5), True
    elapsed = t - first
    cycle = math.floor(elapsed / 1.2)
    phase = (elapsed - cycle * 1.2) / .6
    previous = initial if cycle == 0 else initial + 42 + (cycle-1)*44
    if phase >= 1:
        return (initial + 42 + cycle*44, -5), True
    destination = initial + 42 + cycle*44
    return (mix(previous, destination, ease(phase)), -5-8*math.sin(math.pi*phase)**2), False


def sample_transition(identity, transition, frame):
    if identity not in living.PROFILES or transition not in TRANSITIONS:
        raise ValueError("Choose a registered living actor and transition")
    if type(frame) is not int or not 0 <= frame < FRAMES:
        raise ValueError("Transition frame must be an integer within 0..89")
    t = frame / 30
    if transition == "idle_to_walk":
        weight = ease((t-.2)/.8)
        idle = living.sample_pose(identity, "idle", t)
        walking = living.sample_pose(identity, "walk", max(0,t-.4))
        angles = {key: mix(value, dict(walking.angles)[key], weight) for key,value in idle.angles}
        elapsed = max(0,t-.4)
        x = 30 * elapsed * ease(elapsed/.6)
        root = Rigid(x, mix(idle.root.y, walking.root.y, weight))
        targets = [starting_foot(t, side) for side in ("far", "near")]
        feet, planted = tuple(v[0] for v in targets), tuple(v[1] for v in targets)
    elif transition == "walk_to_stop":
        duration = 2 * (1.5/1.13 - .4)
        u = max(0,min(1,(t-.4)/duration))
        clock = t if t <= .4 else .4 + duration * (u-u**3+.5*u**4)
        walking = living.sample_pose(identity, "walk", clock)
        idle = living.sample_pose(identity, "idle", t)
        weight = ease(u)
        angles = {key: mix(value, dict(idle.angles)[key], weight) for key,value in walking.angles}
        root = Rigid(walking.root.x, mix(walking.root.y, idle.root.y, weight))
        joints = living.RIGS[identity].evaluate(walking)
        feet = tuple((joints[f"{side}_foot"].x,joints[f"{side}_foot"].y) for side in ("far","near"))
        planted = tuple(abs(y+5)<1e-8 for _,y in feet)
    else:
        source, destination, offset = {
            "idle_to_notice": ("idle","notice",0),
            "notice_to_react": ("notice","react",.55),
            "react_to_idle": ("react","idle",.4),
        }[transition]
        before = living.sample_pose(identity, source, t+offset)
        after = living.sample_pose(identity, destination, max(0,t-.35))
        weight = ease((t-.35)/.8)
        angles = {key: mix(value, dict(after.angles)[key], weight) for key,value in before.angles}
        root = Rigid(0,mix(before.root.y,after.root.y,weight))
        feet, planted = ((-10,-5),(10,-5)), (True,True)
    pose = replant(identity, root, angles, feet)
    return TransitionSample(pose, feet, planted)
