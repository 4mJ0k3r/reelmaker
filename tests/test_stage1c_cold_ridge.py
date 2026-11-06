from copy import deepcopy

import pytest

from reelforge.blocking.contract import compile_blocking
from reelforge.blocking.sampling import blocking_frame, inspect_frame
from reelforge.catalog.inventory import inventory
from reelforge.core.errors import InputError
from reelforge.environments import snowy
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.visual_library.composition.cold_ridge import (
    cold_ridge_manifest,
    cold_ridge_scene,
    cold_ridge_walk,
)

NEW_VARIANTS = (
    ("frost_peaks_01", "cinematic_far"),
    ("frost_peaks_01", "cinematic_massif"),
    ("frost_ridge_01", "sculpted"),
    ("pine_snow_01", "pinnacle"),
    ("pine_snow_01", "windshear"),
    ("beacon_01", "local_signal"),
    ("frost_foreground_01", "ridge_wind"),
)


@pytest.mark.parametrize(("asset_id", "variant"), NEW_VARIANTS)
def test_opt_in_registry_and_deterministic_budget(asset_id, variant):
    asset = asset_by_id(asset_id)
    entry = next(item for item in inventory()["components"] if item["id"] == asset_id)
    assert variant in entry["variants"]
    assert entry["production_status"] == "candidate"
    assert entry["quality_review"] == "not_assessed"
    for amount in (0.0, 1.0):
        args = (asset, variant, amount, amount, amount, 89 / 30, None)
        commands = recipe(*args)
        assert commands == recipe(*args)
        paths, ops = cost(commands)
        assert 0 < paths <= asset.max_paths
        assert 0 < ops <= asset.max_ops


@pytest.mark.parametrize("view", ["establishing", "medium"])
@pytest.mark.parametrize("layout", ["pass", "saddle"])
@pytest.mark.parametrize("weather", ["clear", "storm"])
def test_cold_views_resolve_with_support(view, layout, weather):
    compiled = compile_scene(cold_ridge_scene(view, layout=layout, weather=weather))
    nodes = {node.id: node for node in compiled.scene.nodes}
    resolved = {node.id: node for node in compiled.hierarchy}
    assert nodes["rowan"].ground_id == "ground"
    assert nodes["beacon"].variant == "local_signal"
    assert resolved["rowan"].depth == resolved["ground"].depth == resolved["beacon"].depth == 1
    assert resolved["far_peaks"].depth < resolved["near_peaks"].depth < resolved["ground"].depth
    assert resolved["outcrop"].world.point(0, 0) == resolved["rock_contact"].world.point(0, 0)
    assert "wind" in nodes if weather == "storm" else "wind" not in nodes
    assert scene_frame(compiled, 36) == scene_frame(compiled, 36)


def test_staging_and_variant_changes_are_explicit():
    first = cold_ridge_manifest()
    other = cold_ridge_manifest(layout="saddle")
    for node_id in ("rowan", "beacon", "pine_left", "pine_right", "outcrop"):
        a = next(node for node in first["nodes"] if node["id"] == node_id)
        b = next(node for node in other["nodes"] if node["id"] == node_id)
        assert a["transform"] != b["transform"]
    invalid = deepcopy(first)
    next(node for node in invalid["nodes"] if node["id"] == "ground")["variant"] = "slope"
    with pytest.raises(InputError, match="Trusted variants"):
        validate_scene(invalid)
    with pytest.raises(ValueError):
        cold_ridge_scene(weather="unknown")


def test_level_walk_retains_frost_corridor_and_contacts():
    plan = compile_blocking(cold_ridge_walk())
    assert plan.corridor == (30, 440, 330, 560)
    assert plan.support == (-70, 380, 430, 690)
    assert inspect_frame(plan, 89)["position"] == [166.2, 480]
    assert (
        max(
            contact["error"]
            for frame in range(90)
            for contact in inspect_frame(plan, frame)["contacts"]
            if contact["error"] is not None
        )
        < 1e-7
    )
    assert not any(node.id == "rowan_contact" for node in plan.compiled.scene.nodes)
    assert blocking_frame(plan, 35) != blocking_frame(plan, 36)


def test_legacy_beacon_and_planner_stay_on_original_variants():
    active = asset_by_id("beacon_01")
    assert recipe(active, "active", 0.18, 0.51, 0.85, 1.2, None) == snowy.beacon(
        "active", 0.18, 1.2
    )
    assert len(recipe(active, "local_signal", 0.18, 0.51, 0.85, 1.2, None)) < len(
        snowy.beacon("active", 0.18, 1.2)
    )
    from reelforge.mvp.storylib import ENVIRONMENTS, SHOT_PRESETS, build_shot

    opt_ins = set(NEW_VARIANTS)
    for preset in SHOT_PRESETS:
        shot = build_shot(preset, "frost_peak", title="Test", description="Test", mood="storm")
        assert all(
            (node.get("asset_id"), node.get("variant")) not in opt_ins
            for node in shot["world"]["nodes"]
        )
    assert set(ENVIRONMENTS) == {"orchard", "frost_peak"}
