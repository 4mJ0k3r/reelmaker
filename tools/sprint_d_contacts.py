"""Measure adjacent grounded-ankle movement in registered actor and interaction clips."""

import argparse
import json
from dataclasses import replace
from math import dist

from reelforge.characters import living, living_transitions
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS,
    compile_interaction,
    sample_interaction,
)


def measure(poses, actor, scale):
    joints = [living.RIGS[actor].evaluate(pose) for pose in poses]
    drift = []
    for previous, current in zip(joints, joints[1:]):
        for side in ("far", "near"):
            a, b = (frame[f"{side}_foot"] for frame in (previous, current))
            if abs(a.y + 5) < 1e-7 and abs(b.y + 5) < 1e-7:
                drift.append(abs(b.x - a.x) * scale)
    return {"grounded_pairs": len(drift), "max_adjacent_drift": max(drift, default=0)}


def evaluate(refined):
    result = {}
    params = {"refined": True} if refined else {}
    for actor in living.PROFILES:
        clips = {}
        for action in ("walk", "run", "react"):
            poses = [living.sample_pose(actor, action, f / 30, **params) for f in range(90)]
            clips[action] = measure(poses, actor, .78)
        for transition in living_transitions.TRANSITIONS:
            poses = [living_transitions.sample_transition(actor, transition, f, **params).pose
                     for f in range(90)]
            clips[transition] = measure(poses, actor, .78)
        for identity, offset in (("pickup_carry_place", (0, -16)), ("push_cart", (-51, -41))):
            spec = INTERACTIONS[identity]
            plan = compile_interaction({"schema_version": "interaction-0.1", "actor": actor,
                                        "interaction": identity, "prop": spec.prop,
                                        "variant": spec.variants[0]})
            if refined:
                plan = replace(plan, refined=True)
            samples = [sample_interaction(plan, f) for f in range(spec.frames)]
            errors = []
            for sample in samples:
                if sample.contact:
                    hand = living.RIGS[actor].evaluate(sample.pose)["near_hand"]
                    target = tuple(x + y for x, y in zip(sample.prop, offset, strict=True))
                    errors.append(.78 * dist((hand.x, hand.y), target))
            clips[identity] = {**measure([s.pose for s in samples], actor, .78),
                               "max_hand_socket_error": max(errors)}
        result[actor] = clips
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refined", action="store_true")
    print(json.dumps(evaluate(parser.parse_args().refined), indent=2))
