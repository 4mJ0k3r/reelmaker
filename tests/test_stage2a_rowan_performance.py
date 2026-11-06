"""Native-free validation of opt-in acting, motion and storyboard integration."""

import json

import pytest
from jsonschema import Draft202012Validator
from test_snowy_mountain import _snowy_storyboard

from reelforge.blocking.contract import compile_blocking
from reelforge.blocking.sampling import blocking_frame, commands, inspect_frame, sample
from reelforge.blocking.schema import blocking_schema
from reelforge.characters.presets import (
    ACTIONS,
    EXPRESSIONS,
    SKELETON,
    CharacterPreset,
    sample_pose,
)
from reelforge.characters.registry import character_info
from reelforge.characters.rowan import draw_character
from reelforge.characters.rowan_performance import NAME, face_cue
from reelforge.core.errors import InputError
from reelforge.direction.sampling import direction_frame
from reelforge.scenes.assets import asset_by_id, cost
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.storyboards.schema import storyboard_schema
from reelforge.visual_library.composition.cold_ridge import cold_ridge_manifest
from reelforge.visual_library.composition.rowan_approach import rowan_approach, rowan_storyboard


@pytest.mark.parametrize("world", ["farm", "cold_ridge"])
@pytest.mark.parametrize("view", ["establishing", "medium"])
def test_storyboard_integrates_same_performance(world, view):
    doc = rowan_storyboard(world, view)
    Draft202012Validator(storyboard_schema()).validate(doc)
    sb = compile_storyboard(doc)
    plan = sb.direction.blocking
    assert json.loads(sb.direction_json)["base"]["performance"]["name"] == NAME
    assert plan.performance_reaction == "surprised"
    nodes = {n.id: n for n in plan.compiled.hierarchy}
    assert nodes["rowan"].depth == nodes["ground"].depth
    assert nodes["rowan"].world.scale == pytest.approx(0.72)
    assert all(n.id != "rowan_contact" for n in plan.compiled.hierarchy)
    assert direction_frame(sb.direction, 76) == direction_frame(sb.direction, 76)
    assert direction_frame(sb.direction, 76) != direction_frame(sb.direction, 75)


@pytest.mark.parametrize("reaction", ["surprised", "frightened"])
def test_route_gaze_and_planted_feet(reaction):
    manifest = rowan_approach("farm", reaction=reaction)
    Draft202012Validator(blocking_schema()).validate(manifest)
    plan = compile_blocking(manifest)
    legacy = compile_blocking(rowan_approach("farm", legacy=True, reaction=reaction))
    asset = asset_by_id("rowan_01")
    for frame in range(90):
        old, new = inspect_frame(legacy, frame), inspect_frame(plan, frame)
        assert new["position"] == old["position"]
        assert new["velocity"] == old["velocity"]
        assert new["screen_origin"] == old["screen_origin"]
        assert all(c["error"] is None or c["error"] <= 1e-7 for c in new["contacts"])
        assert -1 <= new["secondary"]["gaze"] <= 1
        assert 0 <= new["performance"]["amount"] <= 1
        assert 0 <= new["performance"]["closure"] <= 1
        paths, ops = cost(commands(plan, frame / 30)[1])
        assert paths <= asset.max_paths and ops <= asset.max_ops
    assert (
        inspect_frame(plan, 44)["secondary"]["gaze"]
        > inspect_frame(legacy, 44)["secondary"]["gaze"]
    )
    assert inspect_frame(plan, 59)["performance"]["target"] == "concerned"
    assert inspect_frame(plan, 76)["performance"]["target"] == reaction
    assert inspect_frame(plan, 82)["performance"]["closure"] == 1
    assert inspect_frame(plan, 89)["performance"]["amount"] == 1
    assert inspect_frame(plan, 89)["performance"]["closure"] == 0
    for frame in (40, 43, 47, 59, 65, 66, 68, 70, 76, 77, 84, 85):
        left, right = (sample(plan, frame / 30 + dt)[2] for dt in (-1e-6, 1e-6))
        assert abs(left.root.x - right.root.x) <= 0.005
        assert abs(left.root.y - right.root.y) <= 0.005
        assert (
            max(abs(a[1] - b[1]) for a, b in zip(left.angles, right.angles, strict=True)) <= 0.001
        )
    assert blocking_frame(plan, 76) == blocking_frame(plan, 76)


def test_left_facing_uses_the_same_beat():
    data = rowan_approach("cold_ridge")
    data["base"] = cold_ridge_manifest(layout="saddle")
    data["start"] = {"position": [250, 480], "facing": "left"}
    for segment in data["segments"]:
        segment["facing"] = "left"
        segment["destination"][0] = 360 - segment["destination"][0]
    plan = compile_blocking(data)
    assert inspect_frame(plan, 76)["facing"] == "left"
    assert inspect_frame(plan, 76)["secondary"]["gaze"] == pytest.approx(0.92)
    assert inspect_frame(plan, 76)["position"][0] > 146  # Beacon lies in the facing direction.


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("performance", {"name": "arbitrary", "reaction": "surprised"}),
        ("performance", {"name": NAME, "reaction": ["surprised"]}),
        ("performance", {"name": NAME, "reaction": "frightened", "joints": []}),
        ("schema_version", "blocking-0.1"),
        ("character", "yellow_mellow_v2"),
    ],
)
def test_rejects_unsupported_selectors(field, value):
    manifest = rowan_approach("farm")
    manifest[field] = value
    with pytest.raises(InputError, match="performance|Select|Supply"):
        compile_blocking(manifest)


def test_rejects_performance_on_short_final_hold():
    from reelforge.visual_library.composition.farm_motion import farm_walk

    data = farm_walk()
    data["schema_version"] = "blocking-0.2"
    data["performance"] = {"name": NAME, "reaction": "surprised"}
    with pytest.raises(InputError, match="final idle"):
        compile_blocking(data)


def test_legacy_character_identity_and_vocabulary():
    rowan = character_info("rowan_01")
    assert rowan.scene_actions == ACTIONS
    assert rowan.expressions == EXPRESSIONS
    assert len(SKELETON.joints) == 17
    for action in ACTIONS:
        pose = sample_pose(CharacterPreset(action=action), 0.5)
        assert all(draw_character(pose, expression=expression) for expression in EXPRESSIONS)
    assert face_cue(70, 47, 59, "surprised").target != face_cue(70, 47, 59, "frightened").target
    sb = compile_storyboard(_snowy_storyboard())
    assert sb.direction.blocking.character == "yellow_mellow_v2"
    assert sb.direction.blocking.performance_reaction is None
    original = direction_frame(sb.direction, 46)
    assert original == direction_frame(sb.direction, 46)
    assert original != direction_frame(sb.direction, 47)
