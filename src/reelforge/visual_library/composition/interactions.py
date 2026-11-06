"""Finite choreography presets composed over the existing scene evaluator."""

from dataclasses import dataclass, replace

from reelforge.characters import living, presets, rowan
from reelforge.characters.contact import FootPlacement, ease, plant_feet
from reelforge.characters.rig import Pose, Rigid
from reelforge.scenes.assets import asset_by_id, cost
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import CharacterFrame, compile_scene, evaluate_layers
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.living_assets import cart
from reelforge.visual_library.composition.living_worlds import node, world_manifest


@dataclass(frozen=True)
class Interaction:
    actors: tuple[str, ...]
    prop: str
    variants: tuple[str, ...]
    frames: int
    kit: str
    mood: str


INTERACTIONS = {
    "pickup_carry_place": Interaction(("scout_01", "mechanic_01"), "parcel_01",
                                      ("wrapped", "utility"), 180, "village_lane", "evening"),
    "sit_stand": Interaction(("rowan_01", "scout_01", "mechanic_01"), "bench_01",
                             ("timber", "painted", "weathered"), 150, "village_lane", "daylight"),
    "push_cart": Interaction(("mechanic_01", "scout_01"), "handcart_01",
                             ("empty", "loaded"), 150, "woodland_creek", "windy"),
}


@dataclass(frozen=True)
class InteractionPlan:
    identity: str
    actor: str
    variant: str
    scene: object


@dataclass(frozen=True)
class Sample:
    pose: Pose
    prop: tuple[float, float]
    contact: bool
    expression: str
    travel: float = 0


def compile_interaction(data):
    fields = {"schema_version", "interaction", "actor", "prop", "variant"}
    if not isinstance(data, dict) or set(data) != fields or data["schema_version"] != "interaction-0.1":
        raise ValueError("Supply exactly the interaction-0.1 request fields")
    if any(not isinstance(data[field], str) for field in fields):
        raise ValueError("Interaction fields must be strings")
    identity, actor, variant = (data[k] for k in ("interaction", "actor", "variant"))
    spec = INTERACTIONS.get(identity)
    if spec is None or actor not in spec.actors or data["prop"] != spec.prop or variant not in spec.variants:
        raise ValueError("Unsupported registered interaction/actor/prop pairing")
    scene = world_manifest(spec.kit, spec.mood, actor=actor, frames=spec.frames)
    scene["title"] = identity.replace("_", " ").title()
    actor_node = next(n for n in scene["nodes"] if n["id"] == "actor")
    actor_node["transform"]["x"] = 126 if identity == "sit_stand" else 115
    actor_node["transform"]["y"] = 587
    scale = actor_node["transform"]["scale"]
    if identity == "sit_stand":
        scene["nodes"] = [n for n in scene["nodes"] if n["id"] != "shop_bench"]
    scene["nodes"].append(node("interaction_prop", "midground", 8 if identity == "sit_stand" else 10,
                               spec.prop, variant, actor_node["transform"]["x"],
                               actor_node["transform"]["y"], scale * (2 if actor == "rowan_01" else 1)))
    compiled = compile_scene(validate_scene(scene))
    return InteractionPlan(identity, actor, variant, compiled)


def ramp(t, start, end):
    return ease((t - start) / (end - start))


def sit_sample(actor, t):
    seated = ramp(t, .55, 1.55) * (1 - ramp(t, 3.2, 4.35))
    if actor == "rowan_01":
        standing = presets.sample_pose(presets.CharacterPreset(), 0., travel=False)
        angles = dict(standing.angles)
        angles["torso"] = .20 * seated
        pose = Pose(Rigid(standing.root.x - 7 * seated,
                          standing.root.y * (1 - seated) - 40 * seated), tuple(angles.items()))
        pose = plant_feet(pose, (FootPlacement(9), FootPlacement(-9)), presets.SKELETON)
        expression = "focused" if seated < .98 else "calm"
    else:
        profile = living.PROFILES[actor]
        crouch = (profile.upper + profile.lower - 25) * seated
        pose = living.sample_pose(actor, "idle", 0, crouch=crouch)
        expression = "neutral" if seated < .98 else "happy"
    return Sample(pose, (-5, 0), seated >= 1, expression)


def manipulation_sample(plan, t):
    actor = plan.actor
    if plan.identity == "pickup_carry_place":
        pickup, lift, lower, release = (ramp(t, *span) for span in
                                        ((.4,1.25),(1.25,2.25),(3.75,4.75),(4.75,5.6)))
        crouch = 32 * (pickup * (1-lift) + lower * (1-release))
        travel_time = 1.45 * ramp(t, 2.25, 3.75)
        gait = ramp(t,2.25,2.55) * (1-ramp(t,3.45,3.75))
        pose = living.sample_pose(actor, "walk", travel_time, crouch=crouch, gait_weight=gait)
        hand_x = pose.root.x + 18
        hand_y = -16 - 38 * lift * (1-lower)
        grasp = pickup * (1-release)
        prop_x = (hand_x if t >= 1.25 else 18)
        prop_y = hand_y + 16 if 1.25 <= t <= 4.75 else 0
        expression = "concerned" if t < 4.75 else "determined"
        contact = 1.25 <= t <= 4.75
    else:
        grasp = ramp(t,.35,1.15) * (1-ramp(t,3.85,4.65))
        travel_time = 2.15 * ramp(t, 1.15, 3.85)
        gait = ramp(t,1.15,1.45) * (1-ramp(t,3.55,3.85))
        crouch = 4 * grasp
        pose = living.sample_pose(actor, "walk", travel_time, crouch=crouch, gait_weight=gait)
        hand_x, hand_y = pose.root.x + 24, -41
        prop_x, prop_y = hand_x + 51, 0
        expression = "determined" if grasp > .5 else "neutral"
        contact = 1.15 <= t <= 3.85
    hand = living.RIGS[actor].evaluate(pose)["near_hand"]
    target = (hand.x + (hand_x - hand.x) * grasp, hand.y + (hand_y - hand.y) * grasp)
    if grasp > 0:
        pose = living.sample_pose(actor, "walk", travel_time, crouch=crouch, hand=target, gait_weight=gait)
    return Sample(pose, (prop_x, prop_y), contact, expression, pose.root.x)


def sample_interaction(plan, frame):
    if type(frame) is not int or not 0 <= frame < plan.scene.scene.frames:
        raise ValueError("Frame outside the admitted interaction duration")
    t = frame / 30
    return sit_sample(plan.actor, t) if plan.identity == "sit_stand" else manipulation_sample(plan, t)


def interaction_layers(plan, frame, *, camera_override=None):
    sample = sample_interaction(plan, frame)
    actor, prop = (next(n for n in plan.scene.hierarchy if n.id == key)
                   for key in ("actor", "interaction_prop"))
    if plan.actor == "rowan_01":
        actor_commands = rowan.contact_shadows(sample.pose, position=(0,0), scale=1) + rowan.draw_character(
            sample.pose, position=(0,0), expression=sample.expression)
    else:
        actor_commands = living.draw_pose(plan.actor, sample.pose, sample.expression)
    prop_x, prop_y = actor.world.point(*sample.prop)
    prop_world = Placement(prop_x, prop_y, prop.world.scale)
    hierarchy = tuple(replace(n, world=prop_world) if n.id == prop.id else n for n in plan.scene.hierarchy)
    compiled = replace(plan.scene, hierarchy=hierarchy)
    layers = evaluate_layers(compiled, frame, character_override=CharacterFrame(
        actor.id, actor.world, actor_commands), camera_override=camera_override)
    if plan.identity != "push_cart":
        return layers

    # Replace the last prop commands in its own layer with the same trusted
    # cart recipe at the wheel angle implied by the traveled distance.
    from reelforge.scenes.graph import camera_at

    camera = camera_override or camera_at(compiled, frame)
    projection = camera.transform(prop.depth)
    world = Placement(projection.tx, projection.ty, projection.sx).compose(prop_world)
    rotated = tuple(world.command(c) for c in cart(plan.variant, sample.travel / 9))
    asset = asset_by_id("handcart_01")
    paths, operations = cost(rotated)
    if paths > asset.max_paths or operations > asset.max_ops:
        raise ValueError("Cart override exceeds its registered geometry envelope")
    return tuple(replace(layer, commands=layer.commands[:-paths]+rotated)
                 if layer.id == prop.layer else layer for layer in layers)


def interaction_frame(plan, frame, *, camera_override=None):
    return tuple(c for layer in interaction_layers(plan, frame, camera_override=camera_override)
                 for c in layer.commands)
