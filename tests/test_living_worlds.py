from math import hypot

import jsonschema
import pytest

from reelforge.characters import living
from reelforge.characters.registry import blocking_character_ids, character_ids
from reelforge.scenes.assets import asset_by_id, recipe
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.schema import scene_schema
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS, compile_interaction, interaction_frame, sample_interaction,
)
from reelforge.visual_library.composition.living_worlds import WORLD_KITS, world_manifest
from reelforge.visual_library.living_assets import EFFECTS

ACTORS = tuple(living.PROFILES)
PAIRINGS = [(key, actor, variant) for key, spec in INTERACTIONS.items()
            for actor in spec.actors for variant in spec.variants]


@pytest.mark.parametrize("actor", ACTORS)
def test_character_contract_and_pose(actor):
    assert actor in character_ids()
    assert actor not in blocking_character_ids()
    for action in living.ACTIONS:
        manifest = world_manifest("village_lane", "evening", actor=actor, action=action, frames=45)
        jsonschema.validate(manifest, scene_schema())
        scene = compile_scene(validate_scene(manifest))
        first = scene_frame(scene, 0)
        assert scene_frame(scene, 36) != first
        assert scene_frame(scene, 0) == first
        for frame in range(45):
            pose = living.sample_pose(actor, action, frame / 30)
            joints = living.RIGS[actor].evaluate(pose)
            assert all(joints[f"{side}_foot"].y <= -5 + 1e-9 for side in ("near", "far"))
    assert len({living.draw_actor(actor, "idle", expression, 0)
                for expression in living.EXPRESSIONS}) == len(living.EXPRESSIONS)


@pytest.mark.parametrize("actor", ACTORS)
@pytest.mark.parametrize("action,speed,stride", [("walk", 1.13, 22), ("run", 1.95, 40)])
def test_planted_foot_stays_world_fixed(actor, action, speed, stride):
    samples = [living.RIGS[actor].evaluate(living.sample_pose(actor, action, phase / speed))
               for phase in (0, .1, .2, .3, .4, .49)]
    assert all(abs(pose["near_foot"].x - samples[0]["near_foot"].x) < 1e-9 for pose in samples)
    assert all(abs(pose["near_foot"].y + 5) < 1e-9 for pose in samples)
    assert samples[-1]["hips"].x > samples[0]["hips"].x


@pytest.mark.parametrize("key,actor,variant", PAIRINGS)
def test_interaction_contact_and_random_access(key, actor, variant):
    spec = INTERACTIONS[key]
    plan = compile_interaction(dict(schema_version="interaction-0.1", interaction=key,
                                    actor=actor, prop=spec.prop, variant=variant))
    first = interaction_frame(plan, 0)
    assert interaction_frame(plan, spec.frames // 2) != first
    assert interaction_frame(plan, 0) == first
    samples = [sample_interaction(plan, frame) for frame in range(spec.frames)]
    assert any(sample.contact for sample in samples)
    assert not samples[0].contact and not samples[-1].contact
    assert samples[-1].prop[1] == 0
    for old, new in zip(samples, samples[1:]):
        assert hypot(old.prop[0]-new.prop[0], old.prop[1]-new.prop[1]) < 6
        assert hypot(old.pose.root.x-new.pose.root.x, old.pose.root.y-new.pose.root.y) < 6
    if key == "sit_stand":
        ratio = 2 if actor == "rowan_01" else 1
        assert all(abs(sample.pose.root.y + ratio * 19) < 3
                   for sample in samples if sample.contact)
        assert samples[0].pose == samples[-1].pose
    else:
        dx, dy = (0, -16) if key == "pickup_carry_place" else (-51, -41)
        for sample in samples:
            if sample.contact:
                hand = living.RIGS[actor].evaluate(sample.pose)["near_hand"]
                assert hypot(hand.x-sample.prop[0]-dx, hand.y-sample.prop[1]-dy) < 1e-8
        assert samples[-5].prop == samples[-1].prop


@pytest.mark.parametrize("field,value", [
    ("prop", "bench_01"), ("actor", "rowan_01"), ("variant", "unknown"),
    ("schema_version", 1), ("script", "anything"),
])
def test_invalid_interaction(field, value):
    data = dict(schema_version="interaction-0.1", interaction="pickup_carry_place",
                actor="scout_01", prop="parcel_01", variant="wrapped")
    data[field] = value
    with pytest.raises(ValueError):
        compile_interaction(data)


@pytest.mark.parametrize("identity", EFFECTS)
def test_effect_changes_and_is_bounded(identity):
    asset = asset_by_id(identity)
    for variant in asset.variants:
        first = recipe(asset, variant, .8, .4, 0, 0, None)
        assert recipe(asset, variant, .8, .4, 0, .5, None) != first
        assert recipe(asset, variant, .8, .4, 0, 0, None) == first


@pytest.mark.parametrize("kit,mood", [(kit, mood) for kit,moods in WORLD_KITS.items() for mood in moods])
def test_world_contract(kit, mood):
    manifest = world_manifest(kit, mood, actor="scout_01")
    scene = compile_scene(validate_scene(manifest))
    assert scene_frame(scene, 45) != scene_frame(scene, 0)
    with pytest.raises(ValueError):
        world_manifest(kit, "other")


def test_animated_gallery_references():
    import json
    from pathlib import Path

    gallery = Path(__file__).resolve().parents[1] / "docs/asset-gallery"
    data = json.loads((gallery / "assets.json").read_text())["living_worlds"]
    assert set(data["motion"]) == set(ACTORS) | set(WORLD_KITS) | set(INTERACTIONS)
    for paths in data["world_previews"].values():
        assert len(paths) == 2
        assert all((gallery / path).is_file() for path in paths)
    for path in data["motion"].values():
        assert (gallery / path).read_bytes()[8:12] == b"WEBP"


def test_film_existing_output_is_preserved(tmp_path):
    from tools.living_worlds import render_sequence

    existing = tmp_path / "film.mp4"
    existing.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        render_sequence([], tmp_path)
    assert existing.read_bytes() == b"existing"
