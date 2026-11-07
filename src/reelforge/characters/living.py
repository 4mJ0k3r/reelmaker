"""Two original scene actors using the existing rigid hierarchy and planar IK."""

import math
from dataclasses import dataclass

from reelforge.characters.contact import ease
from reelforge.characters.rig import Joint, Pose, Rigid, Skeleton, two_bone
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.architecture.buildings import box, plane
from reelforge.visual_library.world_assets import oval, stroke


ACTIONS = ("idle", "walk", "run", "notice", "react")
EXPRESSIONS = ("neutral", "happy", "concerned", "surprised", "frightened", "determined")


@dataclass(frozen=True)
class Profile:
    name: str
    shoulder: int
    torso: int
    head: int
    upper: int
    lower: int
    sleeve: int
    forearm: int
    skin: str
    coat: str
    trim: str
    pants: str

    @property
    def height(self):
        return self.upper + self.lower + self.torso + 2 * self.head + 8


PROFILES = {
    "scout_01": Profile("Mira Scout", 12, 31, 13, 25, 27, 16, 15,
                        "bc805a", "527d72", "d69d52", "344a4a"),
    "mechanic_01": Profile("Bram Mechanic", 19, 35, 15, 23, 25, 18, 16,
                           "c58a6e", "a77c54", "7a98a3", "414958"),
}


def skeleton(profile):
    joints = [Joint("hips", None), Joint("torso", "hips"),
              Joint("head", "torso", (4, -profile.torso))]
    for side, sign in (("far", -1), ("near", 1)):
        joints.extend((
            Joint(f"{side}_hip", "hips", (sign * 5, 0)),
            Joint(f"{side}_knee", f"{side}_hip", (0, profile.upper)),
            Joint(f"{side}_foot", f"{side}_knee", (0, profile.lower)),
            Joint(f"{side}_shoulder", "torso", (sign * profile.shoulder / 2, -profile.torso + 7)),
            Joint(f"{side}_elbow", f"{side}_shoulder", (0, profile.sleeve)),
            Joint(f"{side}_hand", f"{side}_elbow", (0, profile.forearm)),
        ))
    return Skeleton(tuple(joints))


RIGS = {identity: skeleton(profile) for identity, profile in PROFILES.items()}


def step_target(phase, stride, lift, offset):
    """Planted first half of a cycle; interpolate to the next footprint in swing."""
    shifted = phase + offset
    cycle = math.floor(shifted)
    u = shifted - cycle
    swing = max(0, 2 * u - 1)
    return ((cycle + ease(swing) - offset + .25) * stride,
            -5 - lift * math.sin(math.pi * swing) ** 2)


def sample_pose(identity, action, seconds, *, crouch=0., hand=None, gait_weight=1., refined=False):
    profile = PROFILES[identity]
    if action not in ACTIONS or not math.isfinite(seconds) or not 0 <= seconds <= 12:
        raise ValueError("Select a registered action and time within twelve seconds")
    walking = action in ("walk", "run")
    fast = action == "run"
    cycle = seconds * (1.95 if fast else 1.13) if walking else 0.
    stride = (40 if fast else 22) * (1.08 if identity == "scout_01" else .94)
    lean = .22 if fast else .09 if walking else .015 * math.sin(seconds * 4)
    agile = identity == "scout_01"
    notice_duration = (1.28 if agile else 1.62) if refined else 1.4
    reaction_duration = (1.20 if agile else 1.55) if refined else 1.15
    notice = math.sin(math.pi * ease(min(seconds / notice_duration, 1))) if action == "notice" else 0
    react = math.sin(math.pi * ease(min(seconds / reaction_duration, 1))) if action == "react" else 0
    lean *= gait_weight if walking else 1
    lean += .13 * notice - (.25 if identity == "scout_01" else .17) * react
    # Keep the registered route and cadence for contact choreography. Free acting
    # separates Scout's quicker recovery from Bram's heavier upper-body settling.
    if refined and not (walking and (crouch or gait_weight != 1 or hand)):
        anticipation = math.sin(math.pi * ease(seconds / .34)) if seconds < .34 else 0
        lean += (.045 if agile else .075) * math.sin(2 * math.pi * cycle)
        lean -= (.055 if agile else .085) * anticipation * (action in ("notice", "react"))
    x = cycle * stride if walking else 0
    y = -(profile.upper + profile.lower + 2.5) + crouch
    if walking:
        y += (3 if fast else 2) * math.sin(2 * math.pi * cycle) ** 2
    else:
        y += .55 * (1 + math.sin(seconds * 4))
    angles = {"torso": lean, "head": .18 * notice - .16 * react - lean * .4}
    legs = []
    for side, sign, offset in (("far", -1, .5), ("near", 1, 0)):
        foot = step_target(cycle, stride, 16 if fast else 8, offset) if walking else (sign * 10, -5)
        if walking:
            foot_x = foot[0] if refined else x + sign * 10 + gait_weight * (foot[0] - x - sign * 10)
            foot = (foot_x, -5 + gait_weight * (foot[1] + 5))
        hip = x + sign * 5
        dx = foot[0] - hip
        legs.append((side, dx, foot[1]))
        limit = profile.upper + profile.lower - .25
        y = max(y, foot[1] - math.sqrt(limit ** 2 - dx ** 2))
        angles[f"{side}_shoulder"] = sign * (.76 if fast else .48) * math.sin(2 * math.pi * cycle) * gait_weight - .8 * react
        angles[f"{side}_elbow"] = -.23 - .63 * react - (.52 if fast else .08)
        if refined and not (crouch or hand or gait_weight != 1):
            weight = 1.13 if identity == "scout_01" else .81
            angles[f"{side}_shoulder"] = weight * angles[f"{side}_shoulder"] + .16 * notice * sign
            angles[f"{side}_elbow"] -= .12 * notice * (sign == 1)
    for side, dx, ankle_y in legs:
        a, b = two_bone(dx, ankle_y - y, profile.upper, profile.lower)
        angles.update({f"{side}_hip": a, f"{side}_knee": b, f"{side}_foot": -a-b})
    if hand is not None:
        base = RIGS[identity].evaluate(Pose(Rigid(x, y), tuple(angles.items())))
        shoulder = base["near_shoulder"]
        dx, dy = hand[0] - shoulder.x, hand[1] - shoulder.y
        distance = math.hypot(dx, dy)
        limit = profile.sleeve + profile.forearm - .15
        if distance > limit:
            dx, dy = dx * limit / distance, dy * limit / distance
        a, b = two_bone(dx, dy, profile.sleeve, profile.forearm)
        offset = math.atan2(profile.forearm * math.sin(b), profile.sleeve + profile.forearm * math.cos(b))
        angles["near_shoulder"], angles["near_elbow"] = a - lean + 2 * offset, -b
    return Pose(Rigid(x, y), tuple(angles.items()))


def draw_pose(identity, pose, expression):
    if expression not in EXPRESSIONS:
        raise ValueError("Unknown living actor expression")
    p = PROFILES[identity]
    scout = identity == "scout_01"
    joints = RIGS[identity].evaluate(pose)
    commands = [oval("22312b", pose.root.x + 3, 0, 19, 3, .28)]

    def part(joint, *paths):
        transform = joints[joint]
        placement = Placement(transform.x, transform.y, 1, transform.angle)
        commands.extend(placement.command(path) for path in paths)

    def arm(side, far=False):
        part(f"{side}_shoulder", box(-4, -3, 8, p.sleeve + 5, "394e50" if far else p.coat))
        part(f"{side}_elbow", box(-3.5, -3, 7, p.forearm + 3, p.coat))
        part(f"{side}_hand", oval(p.skin if scout else "53505a", 0, 0, 4.2, 5))

    arm("far", True)
    for side, tint in (("far", "353f46"), ("near", p.pants)):
        part(f"{side}_hip", box(-5, -2, 10, p.upper + 5, tint))
        part(f"{side}_knee", box(-4.5, -2, 9, p.lower + 4, tint))
        part(f"{side}_foot", plane("343439", (-6,-4), (5,-4), (11,1), (11,5), (-7,5)),
             box(-7, 3, 18, 2, "8c6e56"))
    w, h = p.shoulder, p.torso
    if scout:
        part("torso", oval("665047", -13, -h * .52, 9, 14),
             stroke("a78060", 2, (-19,-h*.6),(-15,-h*.25)))
    part("torso", plane(p.coat, (-w,-h+6), (-w+5,-h), (w-5,-h),
                        (w,-h+7), (w-3,1), (-w+3,1)),
         plane("3f5660" if scout else "80624d", (1,-h),(w-4,-h),(w,-h+7),(w-3,1),(5,1)),
         stroke(p.trim, 2, (-w+4,-h+8),(2,-h+4),(w-2,-h+9)))
    if scout:
        part("torso", stroke("dbaf6d", 3, (-8,-h+5),(8,-5)),
             box(3,-13,8,7,"ab784c"))
    else:
        part("torso", box(-11,-24,22,17,"637d88"), box(-9,-23,18,3,"a0b7b2"),
             box(-15,-7,29,4,"594743"), box(7,-10,6,9,"a8a7a2"))
    r = p.head
    part("head", oval("40393c", 0,-r,r+3,r+2),
         oval(p.skin, 3,-r+1,r-2,r-2), oval("e1ac7d",6,-r-2,r-5,r-6,.55))
    if scout:
        part("head", plane("50675d",(-r-3,-r),(-r-5,-2*r+1),(-5,-2*r-5),
                           (9,-2*r-2),(r+2,-2*r+5),(2,-2*r+4),(-7,-r+5)),
             plane("edb15d",(-8,-2),(5,1),(14,5),(1,9),(-11,4)))
    else:
        part("head", box(-r,-2*r+2,2*r,7,"78878a"),
             plane("a8aaa2",(-r,-2*r+2),(-r+6,-2*r-4),(r-3,-2*r-4),(r,-2*r+3)),
             box(-3,-2*r+7,r+9,4,"4a5d65"),
             oval("624b46", 6,-6,8,3))
    wide = expression in ("surprised", "frightened")
    eye_y = -r + 1
    for x in (3, 10):
        part("head", oval("f4dcc2", x,eye_y,3 if wide else 2.7,3.5 if wide else 1.9),
             oval("332c31", x+1,eye_y,1.2,1.8 if wide else 1.2))
        tilt = {"determined": 2, "concerned": -2, "frightened": -3}.get(expression, 0)
        part("head", stroke("4a3839", 1.3,(x-2,eye_y-4-tilt),(x+2,eye_y-4)))
    if wide:
        part("head", oval("603e3c",8,-5,3.2 if expression == "frightened" else 2.6,2.8))
    else:
        smile = 2 if expression == "happy" else -1.5 if expression == "concerned" else 0
        part("head", stroke("603e3c",1.2,(5,-5),(8,-5+smile),(11,-5)))
    arm("near")
    return tuple(commands)


def draw_actor(identity, action, expression, seconds):
    return draw_pose(identity, sample_pose(identity, action, seconds), expression)
