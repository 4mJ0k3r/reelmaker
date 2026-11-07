"""Random-access acting and composition on separate clocks."""

from dataclasses import dataclass, replace
from math import dist

from reelforge.characters import living, living_transitions, presets
from reelforge.characters.contact import ease
from reelforge.characters.rig import Pose
from reelforge.environments.scene import Camera
from reelforge.scenes.graph import CharacterFrame, evaluate_layers
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.frontier_art import actor_light
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS,
    Sample,
    interaction_frame,
    sample_interaction,
)

from .staging import Performer, face_left, performer_clock, pose_at


@dataclass(frozen=True)
class Acting:
    anchor: Placement
    pose: Pose
    expression: str
    interaction: Sample | None
    local_frame: int
    facing: str = "right"

    def point(self, x, y):
        return self.anchor.point(-x if self.facing == "left" else x, y)


def named_node(beat, name):
    return next(n for n in beat.scene.hierarchy if n.id == name)


def acting_at(beat, local, *, partner=False):
    anchor = named_node(beat, "partner" if partner else "actor").world
    if beat.refined and not beat.interaction:
        performer = beat.partner if partner else Performer(
            beat.actor, beat.action, beat.expression, beat.facing, beat.delay, beat.pacing
        )
        pose, clock = pose_at(performer, local, refined=True)
        facing = "right" if beat.cue_frame is not None and local >= beat.cue_frame else performer.facing
        _, active = performer_clock(performer, local)
        expression = performer.expression if active else "neutral"
        if performer.action == "react" and clock >= (36 if performer.actor == "scout_01" else 47):
            expression = "concerned" if expression in ("surprised", "frightened") else expression
        if beat.cue_frame is not None and local >= beat.cue_frame:
            cue_clock, cue_active = performer_clock(replace(performer, delay=0), local - beat.cue_frame)
            if performer.action in ("idle", "notice", "react"):
                pose = living.sample_pose(performer.actor, "notice",
                                          cue_clock / 30, refined=True) if cue_active else pose
            expression = ("determined" if cue_clock >= 15 else "surprised") if cue_active else expression
        return Acting(anchor, pose, expression, None, clock, facing)
    if beat.interaction:
        authored_frame = min(local, INTERACTIONS[beat.action].frames - 1)
        state = sample_interaction(beat.interaction, authored_frame)
        return Acting(anchor, state.pose, state.expression, state, authored_frame)
    if beat.action in living_transitions.TRANSITIONS:
        pose = living_transitions.sample_transition(beat.actor, beat.action, local).pose
    else:
        pose = living.sample_pose(beat.actor, beat.action, local / 30)
    return Acting(anchor, pose, beat.expression, None, local)


def state_at(project, frame):
    shot, local = project.at(frame)
    beat = shot.beat
    state = acting_at(beat, local)
    rig = presets.SKELETON if beat.actor == "rowan_01" else living.RIGS[beat.actor]
    joints = rig.evaluate(state.pose)
    point = state.point
    result = {
        "frame": frame,
        "shot": shot.id,
        "beat": beat.id,
        "actor": beat.actor,
        "authored_frame": state.local_frame,
        "beat_frame": local,
        "root_world": point(state.pose.root.x, state.pose.root.y),
        "feet_world": {k: point(joints[k].x, joints[k].y) for k in joints if k.endswith("_foot")},
        "active_captions": [i for i, c in enumerate(project.captions) if c.start <= frame < c.end],
        "active_audio_cues": [
            i
            for i, c in enumerate(project.audio_cues)
            if c["start_sample"] <= frame * 1600 < c["end_sample"]
        ],
    }
    if beat.refined:
        result["facing"] = state.facing
        result["expression"] = state.expression
        if beat.partner:
            other = acting_at(beat, local, partner=True)
            other_joints = living.RIGS[beat.partner.actor].evaluate(other.pose)
            result["partner"] = {
                "actor": beat.partner.actor, "facing": other.facing, "expression": other.expression,
                "authored_frame": other.local_frame,
                "root_world": other.point(other.pose.root.x, other.pose.root.y),
                "feet_world": {k: other.point(v.x, v.y) for k, v in other_joints.items()
                               if k.endswith("_foot")},
            }
    if state.interaction:
        prop = state.interaction.prop
        result.update(prop_world=point(*prop), contact=state.interaction.contact)
        socket = {"pickup_carry_place": (0, -16), "push_cart": (-51, -41)}.get(beat.action)
        if socket and state.interaction.contact:
            hand = point(joints["near_hand"].x, joints["near_hand"].y)
            target = point(prop[0] + socket[0], prop[1] + socket[1])
            result.update(
                hand_world=hand, socket_world=target, hand_socket_error=dist(hand, target)
            )
    return result


def _base_camera(shot, state, frame, *, partner=None):
    """All subjects and target positions are sampled before applying depth projection."""
    beat = shot.beat
    if shot.camera == "two_shot":
        a, b = (person.point(person.pose.root.x, person.pose.root.y)[0]
                for person in (state, partner))
        zoom = min(1.8, 255 / (abs(b - a) + 56))
        return _aim((a + b) / 2, state.anchor.y - 50, zoom, 180, 380)
    actor_id = beat.actor
    if shot.focus == "partner":
        state, actor_id = partner, beat.partner.actor
    profile = living.PROFILES.get(actor_id)
    height = state.anchor.scale * (profile.height if profile else 158)
    x, _ = state.point(state.pose.root.x, state.pose.root.y)
    floor = state.anchor.y
    prop_x = state.anchor.point(*state.interaction.prop)[0] if state.interaction else x
    progress = (frame - shot.start) / (shot.end - shot.start - 1)
    name = shot.camera
    if name == "establishing":
        return Camera(0 if beat.refined else -4 + 8 * progress, 0, 1.015)
    if name == "atmospheric_close":
        return Camera(0 if beat.refined else 5 - 10 * progress, 0, 1.035)
    if name == "object_reveal":
        if beat.signal:
            lamp = named_node(beat, "streetlamp").world
            return _aim(lamp.x, lamp.y - 110 * lamp.scale, 2.30, 180, 330)
        if beat.dressing:
            prop = named_node(beat, "dressed_prop").world
            return _aim(prop.x, prop.y - 24, 2.38, 202, 387)
        return _aim(prop_x, floor - 24, 2.38, 206, 387)
    if name == "interaction_detail":
        zoom = 1.95 if beat.action == "push_cart" else 2.35
        return _aim((x + prop_x) / 2, floor - height * 0.50, zoom, 177, 345)
    if name == "close_up":
        return _aim(x, floor - height * 0.83, 3.0, 204 if state.facing == "left" else 156, 320)
    if name == "reaction":
        return _aim(x, floor - height * 0.74, 2.70, 203 if state.facing == "left" else 145, 325)
    if name == "follow":
        return _aim(x + min(25, max(0, prop_x - x)), floor - height * 0.50, 1.62, 157, 388)
    return _aim((x + prop_x) / 2, floor - height * 0.50, 1.78, 164, 398)


def camera_for(shot, state, frame, *, partner=None):
    camera = _base_camera(shot, state, frame, partner=partner)
    if not shot.beat.refined:
        return camera
    u = ease((frame - shot.start) / (shot.end - shot.start - 1))
    motion = shot.motion
    travel, scale = {
        "hold": (0, 1), "pan": (30 * (u - .5), 1),
        "track": (-12 * (u - .5), 1),
        "push_in": (0, 1 + .11 * u),
        "pullback": (0, 1.10 - .10 * u),
        "reframe": (18 * (u - .5), 1 + .035 * u),
    }[motion]
    x, y = camera.x * scale + travel, camera.y * scale
    zoom = min(3.3, camera.zoom * scale)
    if shot.camera in ("two_shot", "medium", "follow", "interaction_detail"):
        subjects = (state, partner) if shot.camera == "two_shot" else (
            partner if shot.focus == "partner" else state,
        )
        centers = [person.point(person.pose.root.x, person.pose.root.y)[0] for person in subjects]
        if shot.camera == "interaction_detail":
            centers.append(state.point(*state.interaction.prop)[0])
        # Clamp animated framing against subject margins in the depth-1 staging plane.
        left, right = 180 + zoom * (min(centers) - 180), 180 + zoom * (max(centers) - 180)
        lower, upper = right - 322, left - 38
        x = min(max(x, lower), upper) if lower <= upper else (lower + upper) / 2
    return Camera(x, y, zoom)


def _aim(x, y, zoom, screen_x, screen_y):
    return Camera(180 + zoom * (x - 180) - screen_x, 400 + zoom * (y - 400) - screen_y, zoom)


def visual_frame(project, frame):
    shot, local = project.at(frame)
    beat = shot.beat
    state = acting_at(beat, local)
    partner = acting_at(beat, local, partner=True) if beat.partner else None
    camera = camera_for(shot, state, frame, partner=partner)
    if beat.interaction:
        return interaction_frame(
            beat.interaction, state.local_frame, camera_override=camera, atmosphere_frame=frame
        )
    def character(node, identity, acting):
        commands = living.draw_pose(identity, acting.pose, acting.expression)
        if beat.grade:
            commands = actor_light(commands, beat.grade)
        if acting.facing == "left":
            commands = face_left(commands)
        return CharacterFrame(node, acting.anchor, commands)

    actors = (character("actor", beat.actor, state),)
    if partner:
        actors += (character("partner", beat.partner.actor, partner),)
    scene = beat.scene
    if beat.cue_frame is not None and local < beat.cue_frame:
        nodes = tuple(replace(n, variant="unlit") if n.id == "streetlamp" else n
                      for n in scene.scene.nodes)
        scene = replace(scene, scene=replace(scene.scene, nodes=nodes))
    return tuple(
        command
        for layer in evaluate_layers(
            scene,
            min(local, scene.scene.frames - 1),
            character_override=actors,
            camera_override=camera,
            atmosphere_frame=frame,
        )
        for command in layer.commands
    )
