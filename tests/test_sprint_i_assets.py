"""Opt-in asset direction, compatible appearance and native pixel evidence."""

import hashlib
import json

import pytest

from reelforge.characters.yellow_mellow_v2.artwork import (
    Placement,
    character_commands,
    torso_commands,
)
from reelforge.characters.yellow_mellow_v2.expressions import expression
from reelforge.characters.yellow_mellow_v2.rig import evaluate, standing_pose
from reelforge.mvp.director import inspect_directed_manifest
from reelforge.mvp.dressing import accessible_assets
from reelforge.mvp.planner import PlanError, build_production_manifest, plan_story, plan_summary
from reelforge.productions.contract import compile_production
from reelforge.scenes.assets import asset_by_id

ORCHARD = "Yellow Mellow finds an unusual object in an orchard. No beacon or lamp."
RIDGE = ("A blizzard begins on a snowy ridge. Yellow Mellow runs to escape. "
         "Later he reaches an orchard. No beacon or parcel.")


def direct(prompt, duration):
    plan = plan_story(prompt, duration, strategy="director-v3")
    manifest = build_production_manifest(plan)
    return plan, manifest, inspect_directed_manifest(plan, manifest)


def nodes(manifest):
    return [node for segment in manifest["segments"] for node in segment["storyboard"]["world"]["nodes"]]


def test_registered_dressing_and_deterministic_orchard_discovery():
    plan, manifest, staged = direct(ORCHARD, 15)
    other, again, _ = direct(ORCHARD, 15)
    assert plan_summary(plan) == plan_summary(other) and manifest == again
    assert {event["purpose"] for event in plan.events} >= {"orientation", "discovery", "resolution"}
    assert [shot["camera"] for shot in staged["shots"]].count("object_reveal") == 1
    assert not staged["beacon_visible"]
    assert {n.get("asset_id") for n in nodes(manifest)} & accessible_assets() == {
        "cinematic_dusk_sky_01", "shrub_cluster_01", "parcel_01",
    }
    assert all(asset_by_id(asset_id) for asset_id in accessible_assets())


def test_ridge_route_uses_environment_dressing_without_adding_focal_objects():
    plan, manifest, staged = direct(RIDGE, 60)
    assert staged["environment_transition_frames"] == [1080]
    assert staged["running_actions"]
    assert all(row["environment"] == "frost_peak" and row["frame"] < 1080
               for row in staged["running_actions"])
    used = {n.get("asset_id") for n in nodes(manifest)}
    assert used & accessible_assets() == accessible_assets() - {"parcel_01"}
    assert not used & {"beacon_01", "answer_light_01"}
    assert {n["variant"] for n in nodes(manifest) if n["kind"] == "character"} == {"reference_slim"}
    assert compile_production(manifest).frames == 1800


def test_context_and_negation_gate_dressing():
    _, manifest, _ = direct("Yellow Mellow walks in an orchard. No unusual object or shrubs.", 15)
    assert not {n.get("asset_id") for n in nodes(manifest)} & {"parcel_01", "shrub_cluster_01"}
    with pytest.raises(PlanError, match="Requested and forbidden: parcel"):
        direct("Yellow Mellow finds a parcel in the orchard. No objects.", 15)
    with pytest.raises(PlanError, match="only in the orchard"):
        direct("Yellow Mellow finds an unusual object on a snowy ridge.", 15)


def test_h_strategy_plan_and_manifest_digests_unchanged():
    plan = plan_story(
        "Yellow Mellow faces a blizzard on a snowy ridge. He runs to an orchard. No beacon.",
        15, strategy="director-v2",
    )
    digest = lambda data: hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    assert digest(plan_summary(plan)) == "cd2ccef3e5d9001f68b503cd0e0123bd32b27ab5865bf97022964df34d844bba"
    assert digest(build_production_manifest(plan)) == "0f692518bab16f03cc6721c00ad7480368b50d9f79a863d6daec9c37057afad4"


def test_reference_art_tapers_waist_without_changing_rig_or_hat():
    state = evaluate(standing_pose())
    before, after = torso_commands(state), torso_commands(state, slim=True)
    assert before[0].path[0].points[0] * 0.88 == pytest.approx(after[0].path[0].points[0], abs=0.01)
    assert before[0].path[0].points[1] == after[0].path[0].points[1]
    place = Placement(0, 0, 1, 1)
    face = expression("surprised")
    old, new = (character_commands(state, face, place, appearance=variant)
                for variant in ("default", "reference_slim"))
    assert old[-12:] == new[-12:]  # Same knit hat and pom-pom geometry and palette.


def test_native_audit_confirms_parcel_pixels_and_does_not_count_hidden_nodes():
    pytest.importorskip("cairo")
    from reelforge.mvp.asset_audit import audit_assets

    _, manifest, _ = direct(ORCHARD, 15)
    for node in nodes(manifest):
        if node.get("asset_id") == "shrub_cluster_01":
            node["visible"] = False
    production = compile_production(manifest)
    report = audit_assets(production)
    assert production.frames == 450
    assert {"parcel_01", "yellow_mellow_v2", "cinematic_dusk_sky_01"} <= set(
        report["pixel_confirmed_asset_ids"]
    )
    assert "shrub_cluster_01" in report["referenced_asset_ids"]
    assert "shrub_cluster_01" not in report["active_asset_ids"]
    focus = next(asset for shot in report["shots"] for asset in shot["assets"]
                 if asset["registered_asset_id"] == "parcel_01")
    assert focus["active_frames"] == 90 and focus["sample_frames_with_contribution"]
