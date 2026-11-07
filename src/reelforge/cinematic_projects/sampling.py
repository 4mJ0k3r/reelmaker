"""Random-access acting and composition on separate clocks."""

from dataclasses import dataclass
from math import dist

from reelforge.characters import living, living_transitions, presets
from reelforge.characters.rig import Pose
from reelforge.environments.scene import Camera
from reelforge.scenes.graph import CharacterFrame, evaluate_layers
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS,
    Sample,
    interaction_frame,
    sample_interaction,
)


@dataclass(frozen=True)
class Acting:
    anchor: Placement
    pose: Pose
    expression: str
    interaction: Sample | None
    local_frame: int


def named_node(beat, name):
    return next(n for n in beat.scene.hierarchy if n.id == name)


def acting_at(beat, local):
    anchor = named_node(beat, "actor").world
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
    point = state.anchor.point
    result = {
        "frame": frame, "shot": shot.id, "beat": beat.id, "actor": beat.actor,
        "authored_frame": state.local_frame, "beat_frame": local,
        "root_world": point(state.pose.root.x, state.pose.root.y),
        "feet_world": {k: point(joints[k].x, joints[k].y) for k in joints
                       if k.endswith("_foot")},
        "active_captions": [i for i, c in enumerate(project.captions) if c.start <= frame < c.end],
        "active_audio_cues": [i for i, c in enumerate(project.audio_cues)
                              if c["start_sample"] <= frame * 1600 < c["end_sample"]],
    }
    if state.interaction:
        prop = state.interaction.prop
        result.update(prop_world=point(*prop), contact=state.interaction.contact)
        socket = {"pickup_carry_place": (0, -16), "push_cart": (-51, -41)}.get(beat.action)
        if socket and state.interaction.contact:
            hand = point(joints["near_hand"].x, joints["near_hand"].y)
            target = point(prop[0] + socket[0], prop[1] + socket[1])
            result.update(hand_world=hand, socket_world=target, hand_socket_error=dist(hand, target))
    return result


def camera_for(shot, state, frame):
    """All subjects and target positions are sampled before applying depth projection."""
    beat = shot.beat
    profile = living.PROFILES.get(beat.actor)
    height = state.anchor.scale * (profile.height if profile else 158)
    x, _ = state.anchor.point(state.pose.root.x, state.pose.root.y)
    floor = state.anchor.y
    prop_x = (state.anchor.point(*state.interaction.prop)[0] if state.interaction else x)
    progress = (frame - shot.start) / (shot.end - shot.start - 1)
    name = shot.camera
    if name == "establishing":
        return Camera(-4 + 8 * progress, 0, 1.015)
    if name == "atmospheric_close":
        return Camera(5 - 10 * progress, 0, 1.035)
    if name == "object_reveal":
        if beat.signal:
            lamp = named_node(beat, "streetlamp").world
            return _aim(lamp.x, lamp.y - 92 * lamp.scale, 2.30, 180, 330)
        return _aim(prop_x, floor - 24, 2.38, 206, 405)
    if name == "interaction_detail":
        zoom = 1.95 if beat.action == "push_cart" else 2.35
        return _aim((x + prop_x) / 2, floor - height * .50, zoom, 177, 377)
    if name == "close_up":
        return _aim(x, floor - height * .83, 3.0, 156, 320)
    if name == "reaction":
        return _aim(x, floor - height * .74, 2.70, 145, 325)
    if name == "follow":
        return _aim(x + min(25, max(0, prop_x - x)), floor - height * .50, 1.62, 157, 388)
    return _aim((x + prop_x) / 2, floor - height * .50, 1.78, 164, 398)


def _aim(x, y, zoom, screen_x, screen_y):
    return Camera(180 + zoom * (x - 180) - screen_x, 400 + zoom * (y - 400) - screen_y, zoom)


def visual_frame(project, frame):
    shot, local = project.at(frame)
    beat = shot.beat
    state = acting_at(beat, local)
    camera = camera_for(shot, state, frame)
    if beat.interaction:
        return interaction_frame(beat.interaction, state.local_frame, camera_override=camera,
                                 atmosphere_frame=frame)
    actor = CharacterFrame("actor", state.anchor, living.draw_pose(
        beat.actor, state.pose, state.expression
    ))
    return tuple(command for layer in evaluate_layers(
        beat.scene, local, character_override=actor, camera_override=camera,
        atmosphere_frame=frame,
    ) for command in layer.commands)
