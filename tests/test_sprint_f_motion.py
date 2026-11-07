"""Opt-in staged clips preserve old root travel, contacts and camera clocks."""

import json
from pathlib import Path

import pytest

from reelforge.characters import living, living_transitions
from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import acting_at, camera_for, state_at, visual_frame
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets/audio"


@pytest.mark.parametrize("identity", ["scout_01", "mechanic_01"])
def test_new_stop_changes_weight_without_moving_contacts(identity):
    rig = living.RIGS[identity]
    for frame in range(90):
        old = living_transitions.sample_transition(identity, "walk_to_stop", frame, refined=True)
        new = living_transitions.sample_settled_stop(identity, frame)
        assert new.pose.root.x == old.pose.root.x
        assert new.feet == old.feet and new.planted == old.planted
        feet = rig.evaluate(new.pose)
        for i, side in enumerate(("far", "near")):
            assert (feet[f"{side}_foot"].x, feet[f"{side}_foot"].y) == pytest.approx(new.feet[i], abs=1e-8)
        if frame in (0, 58, 86, 89):
            assert new == old
        if frame == 68:
            assert new.pose.root.y > old.pose.root.y + 2


def project(name, style=None):
    data = json.loads((ROOT / "examples/sprint-f" / f"motion_{name}.json").read_text())
    data["audio"] = None
    if style:
        data["beats"][1]["cue_style"] = style
    return compile_project(data, REGISTRY)


def test_staggered_reaction_and_camera_across_cut():
    before, after = project("before"), project("after")
    for n in (0, 61, 89, 90, 152, 174, 175, 179, 180, 182, 197, 220, 280, 359):
        old_shot, local = before.at(n)
        new_shot, _ = after.at(n)
        def camera(shot):
            beat = shot.beat
            return camera_for(shot, acting_at(beat, local), n, partner=acting_at(beat, local, partner=True))
        assert camera(old_shot) == camera(new_shot)
        state = state_at(after, n)
        if n >= 90:
            reference = state_at(after, 90)
            for actor, rest in ((state, reference), (state["partner"], reference["partner"])):
                assert actor["root_world"][0] == rest["root_world"][0]
                for foot in actor["feet_world"]:
                    assert actor["feet_world"][foot] == pytest.approx(rest["feet_world"][foot], abs=1e-8)
    assert state_at(after, 179)["beat_frame"] + 1 == state_at(after, 180)["beat_frame"]
    lead_first = state_at(after, 185)
    assert lead_first["expression"] == "surprised" and lead_first["partner"]["expression"] == "concerned"
    assert state_at(after, 201)["partner"]["expression"] == "surprised"
    assert state_at(after, 240)["partner"]["expression"] == "happy"
    assert visual_frame(before, 156) != visual_frame(after, 156)
    assert visual_frame(before, 192) != visual_frame(after, 192)
    first = visual_frame(after, 197)
    visual_frame(after, 128)
    assert first == visual_frame(after, 197) == visual_frame(project("after"), 197)


def test_alert_variant_and_legacy_scope():
    assert state_at(project("after", "alert_settle"), 185)["expression"] == "frightened"
    data = json.loads((ROOT / "examples/sprint-f/motion_after.json").read_text())
    data["audio"] = None
    data["schema_version"] = "cinematic-project-0.1"
    with pytest.raises(InputError):
        compile_project(data, REGISTRY)


def test_recognition_adds_a_staggered_gesture_without_moving_feet_or_camera():
    before, after = project("after"), project("after", "relief_recognize")
    for frame in range(90, 360):
        old_shot, local = before.at(frame)
        new_shot, _ = after.at(frame)
        old = [acting_at(old_shot.beat, local, partner=partner) for partner in (False, True)]
        new = [acting_at(new_shot.beat, local, partner=partner) for partner in (False, True)]
        assert camera_for(old_shot, old[0], frame, partner=old[1]) == camera_for(
            new_shot, new[0], frame, partner=new[1]
        )
        for earlier, current, identity, peak in zip(
            old, new, ("scout_01", "mechanic_01"), (195, 211)
        ):
            assert current.pose.root == earlier.pose.root
            rig = living.RIGS[identity]
            a, b = rig.evaluate(earlier.pose), rig.evaluate(current.pose)
            for foot in ("near_foot", "far_foot"):
                assert (a[foot].x, a[foot].y) == pytest.approx((b[foot].x, b[foot].y), abs=1e-8)
            if frame == peak:
                assert b["near_hand"].y < a["near_hand"].y - 5
                assert b["near_hand"].x > a["near_hand"].x + 10
            if frame < peak - 12 or frame >= peak + 33:
                assert earlier == current
