import json
import math
from pathlib import Path

import pytest

from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.contract import load_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.visual_library.world_assets import WORLD_ASSETS, draw_world_asset

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("identity", WORLD_ASSETS)
def test_registered_world_artwork(identity):
    definition = WORLD_ASSETS[identity]
    asset = asset_by_id(identity)
    assert asset.variants == definition.variants
    assert asset.support_envelope is None
    assert asset.upright == definition.upright
    with pytest.raises(ValueError):
        draw_world_asset(identity, "unknown")
    assert asset.anchor == (0, 0)
    left, top, right, bottom = definition.bounds
    variants = []
    for variant in asset.variants:
        commands = recipe(asset, variant, .8, .5, 0, 0, None)
        assert commands == recipe(asset, variant, .8, .5, 0, 2, None)
        assert all(0 < actual <= limit for actual, limit in zip(cost(commands), definition.budget))
        for command in commands:
            for operation in command.path:
                assert all(math.isfinite(coordinate) for coordinate in operation.points)
                for x, y in zip(operation.points[::2], operation.points[1::2], strict=True):
                    assert left <= x <= right and top <= y <= bottom
        variants.append(commands)
    assert len(set(variants)) == len(variants)


@pytest.mark.parametrize("name", ["village-roadside", "woodland-crossing"])
def test_showcase_random_access(name):
    scene = compile_scene(load_scene(ROOT / f"examples/asset-sprint/{name}.scene.json"))
    first = scene_frame(scene, 0)
    middle = scene_frame(scene, 45)
    assert scene_frame(scene, 89) != first
    assert scene_frame(scene, 0) == first
    assert scene_frame(scene, 45) == middle


def test_gallery_world_preview_coverage():
    gallery = ROOT / "docs/asset-gallery"
    entries = {entry["id"]: entry for entry in json.loads((gallery / "assets.json").read_text())["components"]}
    for identity, definition in WORLD_ASSETS.items():
        entry = entries[identity]
        assert entry["family"] == definition.family
        assert [item["id"] for item in entry["variants"]] == list(definition.variants)
        assert all((gallery / item["preview"]).is_file() for item in entry["variants"])
