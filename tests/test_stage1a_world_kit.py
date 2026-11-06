from dataclasses import replace

import pytest

from reelforge.catalog.inventory import inventory
from reelforge.core.errors import InputError
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.visual_library.composition.farm import ROWAN, farm_scene
from reelforge.visual_library.nature.farm_ground import SUPPORT

COMPONENTS = {
    "cinematic_dusk_sky_01",
    "cinematic_dusk_hills_01",
    "cinematic_farm_track_01",
    "cinematic_farm_tree_01",
    "cinematic_dusk_contact_01",
}


@pytest.mark.parametrize("asset_id", sorted(COMPONENTS))
def test_registered_recipes_are_deterministic_bounded_and_discoverable(asset_id):
    asset = asset_by_id(asset_id)
    entry = next(item for item in inventory()["components"] if item["id"] == asset_id)
    assert entry["registration"] == ["scene"]
    assert entry["variants"] == list(asset.variants)
    assert entry["planner_exposure"] == "unavailable"
    assert entry["production_status"] == "candidate"
    assert entry["quality_review"] == "not_assessed"
    for warmth, atmosphere in ((0, 0), (1, 1)):
        shapes = []
        for variant in asset.variants:
            commands = recipe(asset, variant, warmth, atmosphere, 0, 0, None)
            assert commands == recipe(asset, variant, warmth, atmosphere, 1, 3, None)
            paths, operations = cost(commands)
            assert 0 < paths <= asset.max_paths and 0 < operations <= asset.max_ops
            shapes.append(tuple(command.path for command in commands))
        assert len(set(shapes)) == len(shapes)


@pytest.mark.parametrize("view", ["establishing", "medium"])
def test_farm_views_use_existing_support_and_resolve(view):
    compiled = compile_scene(farm_scene(view))
    legacy = compile_scene(farm_scene(view, legacy=True))
    assert scene_frame(compiled, 36) == scene_frame(compiled, 36)
    assert scene_frame(compiled, 36) != scene_frame(legacy, 36)
    nodes = {node.id: node for node in compiled.scene.nodes}
    actor = nodes["rowan"]
    assert (actor.transform.x, actor.transform.y) == ROWAN
    assert nodes["rowan_contact"].transform.point(0, 0) == ROWAN
    assert actor.ground_id == "ground"
    ground = asset_by_id(nodes[actor.ground_id].asset_id)
    assert ground.anchor == (0, 0)
    assert ground.support_envelope == SUPPORT
    for key in ("orchard_tree", "roadside_tree", "foreground_tree"):
        assert asset_by_id(nodes[key].asset_id).anchor == (0, 0)


@pytest.mark.parametrize(
    ("needle", "replacement", "message"),
    [
        ('"leaning"', '"untrusted_variant"', "Trusted variants"),
        ('"scale": 0.81', '"scale": 2.1', "finite number"),
        ('"warmth": 0.8', '"warmth": -0.1', "finite number"),
    ],
)
def test_invalid_scene_parameters_are_rejected(needle, replacement, message, monkeypatch):
    import json

    from reelforge.scenes.contract import validate_scene
    from reelforge.visual_library.composition import farm

    def corrupt(data):
        serialized = json.dumps(data)
        assert needle in serialized
        return validate_scene(json.loads(serialized.replace(needle, replacement, 1)))

    monkeypatch.setattr(farm, "validate_scene", corrupt)
    with pytest.raises(InputError, match=message):
        farm_scene()


def test_actor_cannot_leave_new_support_envelope():
    scene = farm_scene()
    nodes = tuple(
        replace(node, transform=replace(node.transform, y=410)) if node.id == "rowan" else node
        for node in scene.nodes
    )
    with pytest.raises(InputError, match="outside the ground"):
        compile_scene(replace(scene, nodes=nodes))
