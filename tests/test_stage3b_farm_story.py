"""Compatibility and timing checks for the second fixed cinematic story."""

import hashlib
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from reelforge.blocking.sampling import inspect_frame as inspect_actor
from reelforge.contracts.project import project_digest
from reelforge.core.errors import InputError
from reelforge.direction.contract import compile_direction
from reelforge.direction.sampling import actor_override, camera_at, inspect_frame, shot_at
from reelforge.episodes.contract import compile_episode, frame_origin
from reelforge.episodes.schema import episode_schema
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.visual_library.composition.character_staging import cinematic_character_staging
from reelforge.visual_library.composition.cinematic_story import cinematic_story
from reelforge.visual_library.composition.farm_story import cinematic_farm_story


@pytest.fixture(scope="module")
def manifest():
    return cinematic_farm_story()


@pytest.fixture(scope="module")
def plan(manifest):
    return compile_episode(manifest)


def test_admitted_standalone_recipe(manifest, plan):
    with pytest.raises(ValueError, match="the_empty_doorway"):
        cinematic_farm_story("untrusted_story")
    assert manifest == cinematic_farm_story("the_empty_doorway")
    assert manifest["schema_version"] == "episode-0.3"
    Draft202012Validator(episode_schema()).validate(manifest)
    assert plan.frames == 270 and plan.audio is None
    assert [(s.id, f) for s, f in (frame_origin(plan, n) for n in (0, 89, 90, 179, 180, 269))] == [
        ("arrival", 0),
        ("arrival", 89),
        ("movement", 0),
        ("movement", 89),
        ("empty_doorway", 0),
        ("empty_doorway", 89),
    ]


def test_rowan_and_farm_parity(plan):
    before = compile_direction(cinematic_character_staging("rowan_01", "farm"))
    after = plan.segments[1].direction
    assert after.blocking.character == before.blocking.character == "rowan_01"
    assert after.blocking.performance_reaction == before.blocking.performance_reaction == "surprised"
    for frame in range(90):
        assert actor_override(before, frame) == actor_override(after, frame)
        assert inspect_actor(before.blocking, frame) == inspect_actor(after.blocking, frame)
        if not 31 <= frame < 62:
            assert camera_at(before, frame) == camera_at(after, frame)


def test_cuts_and_geography(plan):
    arrival, approach, ending = (s.direction for s in plan.segments)
    assert camera_at(arrival, 89) == camera_at(approach, 0)
    assert inspect_frame(arrival, 89)["actor_world"] == inspect_frame(approach, 0)["actor_world"]
    assert camera_at(approach, 45) == camera_at(ending, 0)
    assert [shot_at(approach, f).id for f in (0, 22, 31, 62)] == [
        "context", "attention", "doorway_movement", "reaction",
    ]
    barns = [
        next(n for n in d.compiled.scene.nodes if n.id == "barn")
        for d in (arrival, approach, ending)
    ]
    assert all(n.asset_id == "barn_01" and n.transform == barns[0].transform for n in barns)
    assert [n.variant for n in barns] == ["dusk_graded", "doorway_shadow", "dusk_graded"]
    assert ending.actor_id is None
    for frame in range(31, 62):
        state = inspect_frame(approach, frame)
        assert state["shot"] == "doorway_movement" and state["node_bounds_logical"]
        assert state["actor_bounds_logical"][2] <= 0


def _barn(variant, frame):
    return recipe(asset_by_id("barn_01"), variant, 0.8, 0.52, 0.2, frame / 30, None)


@pytest.mark.parametrize(
    ("variant", "expected"),
    [
        ("default", "a53d0625d60cf6a477d2ac25382c5aacf38be7cac349f9a5198f0b0abd25e63d"),
        ("dusk_graded", "22ffdae51f0e71195e26c438452f457deec1f86d314db0d748473410b9095130"),
    ],
)
def test_historical_barn_command_hashes(variant, expected):
    for f in (0, 44, 89):
        assert hashlib.sha256(repr(_barn(variant, f)).encode()).hexdigest() == expected


def test_shadow_timing_direction_clip_and_budget():
    asset = asset_by_id("barn_01")
    assert asset.variants == ("default", "dusk_graded", "doorway_shadow")
    base = _barn("dusk_graded", 0)
    x_positions = []
    for f in range(90):
        commands = _barn("doorway_shadow", f)
        assert commands == _barn("doorway_shadow", f)
        assert commands[:len(base)] == base
        assert len(commands) == len(base) + (1 if 35 <= f <= 55 else 0)
        paths, ops = cost(commands)
        assert paths <= asset.max_paths and ops <= asset.max_ops
        if 35 <= f <= 55:
            shadow = commands[-1]
            assert shadow.clip is not None
            assert shadow.clip[0].points == (-42, -79)
            x_positions.append(shadow.path[0].points[0])
    assert x_positions == sorted(set(x_positions), reverse=True)


def test_unregistered_event_rejected(manifest):
    bad = deepcopy(manifest)
    nodes = bad["segments"][1]["direction"]["base"]["base"]["nodes"]
    next(n for n in nodes if n["id"] == "barn")["variant"] = "untrusted_effect"
    with pytest.raises(InputError, match="variant"):
        compile_episode(bad)


@pytest.mark.parametrize(
    ("story", "digest"),
    [
        ("the_other_light", "8d276d403f48f9768a19bca2f902e7a26afaf4984933d906ff76a50bad4b0cbd"),
        (
            "the_other_light_refined",
            "7e2d4ff954eac140589d4a182459a2e3550afffe8e70284e08e131faea504f1d",
        ),
    ],
)
def test_first_film_manifests_unchanged(story, digest):
    assert project_digest(cinematic_story(story)) == digest
