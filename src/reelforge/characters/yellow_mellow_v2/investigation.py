"""A planted investigation staged with Yellow Mellow's existing clips and face rig."""

from dataclasses import replace

from .character import Entry, Performance
from .expressions import adjust, blend_faces, expression
from .motions import (
    ClipStart,
    KeyedClip,
    LocomotionClip,
    LocoSegment,
    arms,
    head_tilt,
    look,
    upright,
)
from .rig import ArmPose, smoothstep

NAME = "investigate_and_react"
REACTION = "surprised"

FACES = {
    "neutral": expression("neutral"),
    "curious": adjust(
        expression("curious"),
        brow_asym=0.6,
        upper_lid=0.20,
        mouth_open=-0.17,
        mouth_curve=0.4,
        mouth_width=0.23,
    ),
    "concerned": adjust(
        expression("concerned"),
        brow_tilt=0.12,
        upper_lid=0.27,
        mouth_curve=-0.17,
    ),
    "surprised": adjust(
        expression("surprised"),
        eye_scale=-0.05,
        brow_asym=0.48,
        brow_raise=-0.35,
        mouth_width=0.09,
    ),
    "settled": adjust(
        expression("neutral"),
        brow_asym=0.68,
        upper_lid=0.14,
        mouth_curve=0.29,
    ),
}


class RouteWalk(LocomotionClip):
    """Use the accepted world route as the input to the native V2 stride and anchors."""

    def __init__(self, start, route, world_scale):
        self.route = route
        self.world_scale = world_scale
        self.origin = route[0].x0
        super().__init__(
            start,
            [LocoSegment(s.mode, s.end - s.start) for s in route],
            route[0].facing,
        )

    def _segment(self, frame):
        return next((s for s in self.route if frame < s.end), self.route[-1])

    def displacement(self, frame):
        return (self._segment(frame).position(frame / 30) - self.origin) / self.world_scale

    def _build_profile(self):
        brake, end = self.route[-1].start, self.duration
        # The parent uses these endpoints to place its final stance-phase correction.
        self.keys = [
            (0.0, 0.0, 0.0),
            (brake, self._speed(brake)[0], 0.0),
            (end, 0.0, 0.0),
            (end, 0.0, 0.0),
        ]

    def _speed(self, frame):
        speed = abs(self._segment(frame).velocity(frame / 30)) / (30 * self.world_scale)
        return speed, 0.0

    def _initial_phase(self):
        return 0.67

    def _cycle_duty(self, foot, cycle):
        # The route starts accelerating immediately. Seed the opening stance at a walk duty
        # so the initially planted far foot can release before its first swing becomes cramped.
        if cycle - self._offset(foot) <= self.phi0:
            return 0.70, 0.0
        return super()._cycle_duty(foot, cycle)

    def _integrate(self):
        super()._integrate()
        self.tr.d = [abs(self.displacement(t)) for t in self.tr.t]

    def pose(self, t):
        # Walking has a neutral eyeline. The focused eye shift belongs to the notice.
        return replace(super().pose(t), look_x=0.0)


def _acting(start, duration, direction):
    base = upright(start.pose)
    eyes = replace(start.pose, look_x=0.77, look_y=0.14)
    turned = look(start, 16, direction=direction, amount=0.54).end_pose()
    tilt = head_tilt(start, 15, angle=0.19).end_pose()
    notice = replace(
        base,
        look_x=eyes.look_x,
        look_y=eyes.look_y,
        head_yaw=turned.head_yaw,
        head=tilt.head,
        neck=tilt.neck,
        chest=0.035,
    )
    investigate = arms(
        replace(
            notice,
            spine=0.095,
            chest=0.07,
            pelvis_height=base.pelvis_height - 2.0,
            pelvis_x=base.pelvis_x + 1.35 * base.sign,
        ),
        near=ArmPose(-0.60, -0.82, -0.05, "relaxed"),
        far=ArmPose(0.15, -0.20, 0.04, "relaxed"),
    )
    recoil = replace(
        investigate,
        spine=-0.12,
        chest=-0.06,
        neck=-0.07,
        head=-0.12,
        pelvis_x=base.pelvis_x - 1.5 * base.sign,
        pelvis_height=base.pelvis_height - 2.6,
        look_y=-0.1,
    )
    guarded = arms(
        recoil,
        near=ArmPose(-0.78, -1.2, -0.15, "relaxed"),
        far=ArmPose(0.67, 0.34, 0.1, "relaxed"),
    )
    held = arms(
        replace(base, spine=0.025, neck=0.028, head=0.075, head_yaw=0.14, look_x=0.57, look_y=0.05),
        near=ArmPose(-0.14, -0.19, 0.02, "relaxed"),
    )
    return KeyedClip(
        start,
        duration,
        [
            (3, eyes),
            (9, notice),
            (15, investigate),
            (18, replace(investigate, head=-0.095, neck=-0.03, look_y=-0.1)),
            (22, recoil),
            (25, guarded),
            (30, held),
            (duration, held),
        ],
        face_fn=_face,
        blink_frames=(27,),
    )


def _face(t, base):
    current = base
    for frame, duration, target in (
        (0, 7, "curious"),
        (9, 5, "concerned"),
        (15, 4, "surprised"),
        (24, 7, "settled"),
    ):
        if t >= frame:
            current = blend_faces(current, FACES[target], smoothstep((t - frame) / duration))
    return current


def build_investigation(character, route, world_scale):
    neutral = FACES["neutral"]
    walk = RouteWalk(ClipStart(character.start_pose, neutral), route[:-1], world_scale)
    duration = route[-1].end - route[-1].start
    acting = _acting(ClipStart(walk.end_pose(), neutral), duration, route[-1].facing)
    entries = [
        Entry(0, 0, walk, neutral, ((0, neutral),), "locomotion"),
        Entry(walk.duration, 1, acting, neutral, ((0, neutral),), NAME),
    ]
    return Performance(
        entries, route[-1].end, character.seed, natural_blinks=False
    ), walk.displacement
