"""Stage 3A.1 signal timing, admission, and performance compatibility."""

from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from reelforge.blocking.sampling import inspect_frame as inspect_actor
from reelforge.contracts.project import project_digest
from reelforge.core.errors import InputError
from reelforge.direction.sampling import actor_override, camera_at, inspect_frame, shot_at
from reelforge.episodes.contract import compile_episode, frame_origin
from reelforge.episodes.schema import episode_schema
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.visual_library.composition.cinematic_story import cinematic_story


@pytest.fixture(scope="module")
def original():
    return cinematic_story()


@pytest.fixture(scope="module")
def refined():
    return cinematic_story("the_other_light_refined")


@pytest.fixture(scope="module")
def plans(original, refined):
    return compile_episode(original), compile_episode(refined)


def _commands(asset, variant, frame):
    return recipe(asset, variant, 0.18, 0.51, 0.05, frame / 30, None)


def test_original_manifest_is_identical(original):
    assert project_digest(original) == (
        "8d276d403f48f9768a19bca2f902e7a26afaf4984933d906ff76a50bad4b0cbd"
    )


def test_refined_manifest_is_admitted_and_reproducible(refined, plans):
    Draft202012Validator(episode_schema()).validate(refined)
    assert cinematic_story("the_other_light_refined") == refined
    _, plan = plans
    assert plan.frames == 270 and plan.audio is None
    assert [(s.id, local) for s, local in (frame_origin(plan, f) for f in (0, 90, 180, 269))] == [
        ("beacon", 0), ("approach", 0), ("ridge", 0), ("ridge", 89),
    ]


def test_opening_actor_matches_approach_handoff(plans):
    _, plan = plans
    opening, approach, _ = (s.direction for s in plan.segments)
    assert opening.actor_id == approach.actor_id
    for frame in (0, 27, 28, 89):
        assert inspect_frame(opening, frame)["actor_bounds_logical"]
    assert inspect_frame(opening, 89)["actor_world"] == inspect_frame(approach, 0)["actor_world"]
    assert camera_at(opening, 89) == camera_at(approach, 0)
    node = next(n for n in opening.compiled.scene.nodes if n.id == opening.actor_id)
    assert node.character.direction == approach.blocking.start_facing
    assert node.ground_id == approach.blocking.support_id


def test_all_middle_actor_samples_and_camera_are_identical(plans):
    before, after = (p.segments[1].direction for p in plans)
    assert before.blocking.mellow_investigation and after.blocking.mellow_investigation
    for frame in range(90):
        # Includes local rig drawing commands and native moving contact shadows.
        assert actor_override(before, frame) == actor_override(after, frame)
        assert inspect_actor(before.blocking, frame) == inspect_actor(after.blocking, frame)
        assert camera_at(before, frame) == camera_at(after, frame)
    assert shot_at(after, 50).id == "attention"
    assert shot_at(after, 57).id == "reaction"


def test_beacon_surge_is_one_bounded_change():
    asset = asset_by_id("beacon_01")
    assert asset.variants == ("buried", "active", "local_signal", "ridge_surge")
    for frame in range(90):
        base = _commands(asset, "local_signal", frame)
        surge = _commands(asset, "ridge_surge", frame)
        assert surge[:len(base)] == base
        assert len(surge) == len(base) + (3 if 44 <= frame <= 56 else 0)
        assert surge == _commands(asset, "ridge_surge", frame)
        if 44 <= frame <= 56:
            assert 0 < surge[-1].fill.a <= 1
    assert _commands(asset, "ridge_surge", 50)[-1].fill.a == 1


def test_delayed_light_has_one_rise_and_holds():
    asset = asset_by_id("answer_light_01")
    assert asset.variants == ("default", "ridge_reveal")
    assert _commands(asset, "default", 0)
    for frame in range(24):
        assert not _commands(asset, "ridge_reveal", frame)
    samples = [_commands(asset, "ridge_reveal", f) for f in range(24, 90)]
    alphas = [sample[-1].fill.a for sample in samples]
    assert 0 < alphas[0] < alphas[14] == alphas[-1] == 1
    assert alphas == sorted(alphas)
    assert samples[-1] == _commands(asset, "ridge_reveal", 55)
    for f, sample in enumerate(samples, 24):
        assert sample == _commands(asset, "ridge_reveal", f)
        paths, operations = cost(sample)
        assert paths <= asset.max_paths and operations <= asset.max_ops


def test_unknown_event_variant_rejected(refined):
    invalid = deepcopy(refined)
    nodes = invalid["segments"][2]["direction"]["base"]["nodes"]
    next(n for n in nodes if n["id"] == "distant_light")["variant"] = "arbitrary_event"
    with pytest.raises(InputError, match="variant"):
        compile_episode(invalid)
