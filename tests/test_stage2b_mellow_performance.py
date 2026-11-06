"""Yellow Mellow's Stage 2B opt-in uses the registered actor and native motion."""

import json
import math

import pytest
from jsonschema import Draft202012Validator

from reelforge.blocking.contract import compile_blocking
from reelforge.blocking.sampling import _yellow_mellow_drawer, commands, inspect_frame
from reelforge.blocking.schema import blocking_schema
from reelforge.characters.registry import YELLOW_MELLOW_ID, character_info
from reelforge.characters.yellow_mellow_v2 import YellowMellowV2
from reelforge.characters.yellow_mellow_v2.character import PRIMARY_CACHE
from reelforge.characters.yellow_mellow_v2.investigation import NAME
from reelforge.characters.yellow_mellow_v2.quality import (
    PENETRATION_TOLERANCE,
    SLIDE_TOLERANCE,
    analyse,
)
from reelforge.characters.yellow_mellow_v2.transitions import pose_vector
from reelforge.core.errors import InputError
from reelforge.direction.sampling import direction_frame
from reelforge.scenes.assets import asset_by_id, cost
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.storyboards.schema import storyboard_schema
from reelforge.visual_library.composition.mellow_approach import mellow_storyboard
from reelforge.visual_library.composition.rowan_approach import rowan_storyboard


@pytest.mark.parametrize("world", ("farm", "cold_ridge"))
@pytest.mark.parametrize("view", ("establishing", "medium"))
def test_registered_performance_runs_in_both_kits(world, view):
    data = mellow_storyboard(world, view)
    Draft202012Validator(storyboard_schema()).validate(data)
    storyboard = compile_storyboard(data)
    plan = storyboard.direction.blocking
    base = json.loads(storyboard.direction_json)["base"]
    Draft202012Validator(blocking_schema()).validate(base)
    assert base["performance"]["name"] == NAME
    assert plan.character == YELLOW_MELLOW_ID and plan.mellow_investigation
    assert plan.performance_reaction is None
    nodes = {n.id: n for n in plan.compiled.hierarchy}
    assert nodes["rowan"].depth == nodes["ground"].depth
    assert nodes["rowan"].world.scale == 0.64
    assert "rowan_contact" not in nodes
    first = direction_frame(storyboard.direction, 78)
    assert first != direction_frame(storyboard.direction, 77)
    assert first == direction_frame(storyboard.direction, 78)


def test_acting_and_rendered_contacts():
    proof = compile_storyboard(mellow_storyboard("cold_ridge")).direction.blocking
    old = compile_storyboard(mellow_storyboard("cold_ridge", legacy=True)).direction.blocking
    drawer, old_drawer = _yellow_mellow_drawer(proof), _yellow_mellow_drawer(old)
    refined = analyse(drawer._perf)["summary"]
    legacy = analyse(old_drawer._perf)["summary"]
    assert refined["max_planted_contact_slide_units"] <= SLIDE_TOLERANCE
    assert refined["max_ground_penetration_units"] <= PENETRATION_TOLERANCE
    assert refined["max_leg_reach_error_units"] == 0
    assert not refined["clamped_channel_frames"] and not refined["knee_flip_events"]
    assert refined["max_joint_step_units"] < legacy["max_joint_step_units"]
    assert len(drawer._perf._cache) <= PRIMARY_CACHE
    assert inspect_frame(proof, 89)["position"][0] - inspect_frame(proof, 0)["position"][0] > 50
    assert drawer.sample(57).state.pose.look_x > 0.7
    assert drawer.sample(57).state.pose.head_yaw < drawer.sample(63).state.pose.head_yaw
    assert drawer.sample(68).face.mouth_curve < drawer.sample(63).face.mouth_curve
    assert drawer.sample(73).face.mouth_open > 0.7
    assert drawer.sample(89).face.mouth_open == 0
    assert [f for f in range(90) if drawer.sample(f).blink > 0] == list(range(82, 87))
    assert pose_vector(drawer.sample(87).state.pose) == pytest.approx(
        pose_vector(drawer.sample(89).state.pose), abs=1e-12
    )
    prev = None
    asset = asset_by_id(YELLOW_MELLOW_ID)
    for f in range(90):
        current = drawer.sample(f)
        x, paths = commands(proof, f / 30)
        assert x == commands(old, f / 30)[0]
        assert all(
            n <= bound
            for n, bound in zip(cost(paths), (asset.max_paths, asset.max_ops), strict=True)
        )
        state = current.state
        rendered = {}
        for side in ("near", "far"):
            foot = state.pose.foot(side)
            if foot.lift == foot.pitch == 0:
                local = drawer.local_origin(current) + state.legs[side].ankle[0] * drawer.draw_scale
                rendered[side] = x + proof.scale * local
                if prev and side in prev:
                    assert math.isclose(rendered[side], prev[side], rel_tol=0, abs_tol=1e-7)
        prev = rendered


@pytest.mark.parametrize(
    "performance",
    [
        {"name": "notice_and_react", "reaction": "surprised"},
        {"name": NAME, "reaction": "frightened"},
        {"name": NAME, "reaction": float("nan")},
        {"name": NAME, "reaction": "surprised", "joints": []},
    ],
)
def test_rejects_wrong_vocabulary_and_untrusted_fields(performance):
    doc = mellow_storyboard("farm")
    doc["rowan"]["performance"] = performance
    with pytest.raises(InputError):
        compile_storyboard(doc)


def test_rowan_cannot_select_mellow_performance():
    doc = rowan_storyboard("farm")
    doc["rowan"]["performance"] = {"name": NAME, "reaction": "surprised"}
    with pytest.raises(InputError, match="registered for this character"):
        compile_storyboard(doc)


def test_rejects_invalid_blocking_timing_and_expression():
    doc = compile_storyboard(mellow_storyboard("farm"))
    base = json.loads(doc.direction_json)["base"]
    base["segments"][-1]["expression"] = "frightened"
    with pytest.raises(InputError, match="accepted expression"):
        compile_blocking(base)
    base["segments"][-1]["expression"] = "surprised"
    base["segments"][-1]["start_frame"] = 57
    base["segments"][-2]["end_frame"] = 57
    with pytest.raises(InputError, match="45..54"):
        compile_blocking(base)


def test_mirror_route_and_legacy_action_registry():
    doc = compile_storyboard(mellow_storyboard("cold_ridge"))
    base = json.loads(doc.direction_json)["base"]
    base["start"] = {"position": [250, 480], "facing": "left"}
    for segment in base["segments"]:
        segment["facing"] = "left"
        segment["destination"][0] = 360 - segment["destination"][0]
    plan = compile_blocking(base)
    drawer = _yellow_mellow_drawer(plan)
    assert drawer.sample(78).state.sign == -1
    assert drawer.sample(78).state.pose.look_x > 0
    assert inspect_frame(plan, 89)["position"][0] < 200
    assert character_info(YELLOW_MELLOW_ID).scene_actions == YellowMellowV2.actions()
    assert NAME not in YellowMellowV2.actions()
