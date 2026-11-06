"""Proof that the opt-in edit uses the existing camera and leaves performance intact."""

import math
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from reelforge.blocking.sampling import inspect_frame as inspect_motion
from reelforge.core.errors import InputError
from reelforge.direction.contract import MAX_SCALE_CUT_RATIO, compile_direction
from reelforge.direction.sampling import actor_override, direction_frame, inspect_frame, shot_at
from reelforge.direction.schema import direction_schema
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.visual_library.composition.character_staging import cinematic_character_staging
from reelforge.visual_library.composition.mellow_approach import mellow_storyboard
from reelforge.visual_library.composition.rowan_approach import rowan_storyboard

CASES = [
    ("rowan_01", "farm", rowan_storyboard),
    ("rowan_01", "cold_ridge", rowan_storyboard),
    ("yellow_mellow_v2", "farm", mellow_storyboard),
    ("yellow_mellow_v2", "cold_ridge", mellow_storyboard),
]


@pytest.fixture(scope="module", params=CASES)
def shot_pair(request):
    character, world, builder = request.param
    doc = cinematic_character_staging(character, world)
    return (
        world,
        doc,
        compile_direction(doc),
        compile_storyboard(builder(world, "medium")).direction,
    )


def test_three_valid_shots_at_intended_scales(shot_pair):
    world, doc, staged, baseline = shot_pair
    Draft202012Validator(direction_schema()).validate(doc)
    context, attention, reaction = staged.shots
    assert [s.behavior for s in staged.shots] == ["establishing", "follow", "close_up"]
    assert (context.framing, attention.framing, reaction.framing) == ("full", "full", "feet_crop")
    assert context.target.node_id == ("barn" if world == "farm" else "beacon")
    assert attention.track and reaction.track
    assert attention.target.node_id == reaction.target.node_id == staged.actor_id
    assert (
        math.dist(
            inspect_frame(staged, 24)["target_world"], inspect_frame(staged, 45)["target_world"]
        )
        > 10
    )
    assert [shot_at(staged, i).id for i in (0, 40, 89)] == ["context", "attention", "reaction"]
    assert [i for i in range(90) if inspect_frame(staged, i)["cut"]] == [
        attention.start,
        reaction.start,
    ]
    for cut in (attention.start, reaction.start):
        before, after = (inspect_frame(staged, f) for f in (cut - 1, cut))
        assert after["source_frame"] == before["source_frame"] + 1
        assert after["camera"]["zoom"] / before["camera"]["zoom"] <= MAX_SCALE_CUT_RATIO
        assert after["tracking_error_logical"] <= 1e-7
    close = inspect_frame(staged, 76)["actor_bounds_logical"]
    old = inspect_frame(baseline, 76)["actor_bounds_logical"]
    assert close[3] > 640
    assert close[3] - close[1] >= 1.5 * (old[3] - old[1])
    for frame in (12, 50, 76, 89):
        assert inspect_frame(staged, frame)["foreground_bbox_overlap_upper"] <= 0.15
        assert direction_frame(staged, frame) == direction_frame(staged, frame)
        assert direction_frame(staged, frame) != direction_frame(baseline, frame)


def test_camera_only_preserves_actor_route_and_shadows(shot_pair):
    _, _, staged, baseline = shot_pair
    new, old = staged.blocking, baseline.blocking
    assert new.segments == old.segments
    assert new.support == old.support and new.scale == old.scale
    assert new.performance_reaction == old.performance_reaction
    assert new.mellow_investigation == old.mellow_investigation
    assert staged.compiled.hierarchy == baseline.compiled.hierarchy
    assert staged.compiled.painter_ids == baseline.compiled.painter_ids
    hierarchy = {node.id: node for node in staged.compiled.hierarchy}
    assert hierarchy[new.actor_id].depth == hierarchy[new.support_id].depth
    for frame in range(90):
        assert actor_override(staged, frame) == actor_override(baseline, frame)
    for f in (0, 39, 53, 62, 76, 89):
        assert inspect_motion(new, f) == inspect_motion(old, f)


def test_direction_rejects_invalid_zoom_and_false_full_framing():
    doc = cinematic_character_staging("yellow_mellow_v2", "cold_ridge")
    invalid = deepcopy(doc)
    invalid["shots"][2]["zoom"] = [4, 4]
    with pytest.raises(InputError, match="scale ratio"):
        compile_direction(invalid)
    invalid = deepcopy(doc)
    invalid["shots"][2]["framing"] = "full"
    with pytest.raises(InputError, match="crops the figure"):
        compile_direction(invalid)


@pytest.mark.parametrize(
    ("character", "world"),
    [
        ("unknown", "farm"),
        ("yellow_mellow_v2", "unknown"),
        ([], "farm"),
    ],
)
def test_builder_rejects_unknown_choices(character, world):
    with pytest.raises(ValueError, match="Select"):
        cinematic_character_staging(character, world)
