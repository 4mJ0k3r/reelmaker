"""Chronological prompt direction and opt-in compatibility regressions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from reelforge.mvp.director import inspect_directed_manifest
from reelforge.mvp.planner import PlanError, build_production_manifest, plan_story, plan_summary
from reelforge.productions.contract import compile_production

ACCEPTANCE = (
    "Yellow Mellow is lost on a snowy mountain ridge. A blizzard begins. He runs downhill to "
    "escape. Later he reaches a warm orchard and slows down. He recognizes safety, relaxes and "
    "feels relieved. No emergency beacon should appear."
)


def direct(prompt, seconds=15):
    plan = plan_story(prompt, seconds, strategy="director-v2")
    manifest = build_production_manifest(plan)
    return plan, manifest, inspect_directed_manifest(plan, manifest)


@pytest.mark.parametrize("suffix", [
    "No emergency beacon should appear.",
    "Do not add a beacon.",
    "Without any emergency signal.",
    "The beacon must not be visible.",
    "No beacon or transmitter.",
    "The ridge should not contain a beacon.",
])
def test_beacon_negation_removes_nodes(suffix):
    plan, _, result = direct(f"Yellow Mellow hikes along the snowy ridge. {suffix}")
    assert plan.constraints["forbidden"] == ["beacon"]
    assert result["beacon_visible"] is False


@pytest.mark.parametrize(("prompt", "reason"), [
    ("On a snowy ridge he finds a beacon. No beacon.", "Requested and forbidden: beacon"),
    ("On a snowy ridge he runs. Do not run.", "Requested and forbidden: run"),
    ("On a snowy ridge he runs. Later a storm begins.", "storm before the escape"),
    ("On a snowy ridge he reaches safety. Then he runs.", "precede reaching safety"),
    ("On a snowy ridge he runs. Later he finds a beacon.", "investigation must precede"),
    ("On a snowy ridge a storm begins. He reaches an orchard. Then runs.", "before arrival"),
    ("On a snowy ridge he finds a beacon. No storm.", "includes storm weather"),
    ("On a snowy ridge he reaches an orchard. A blizzard begins.", "only supported"),
    ("Start in a mountain. Go to an orchard. Return to the mountain.", "one location transition"),
    ("An orchard with a narration.", "silent"),
    ("Mountain without walking.", "Cannot guarantee exclusion"),
])
def test_reject_conflicts_and_unadmitted_orders(prompt, reason):
    with pytest.raises(PlanError, match=reason):
        direct(prompt)


def test_acceptance_uses_actual_mountain_run_and_weather_before_arrival():
    plan, manifest, staging = direct(ACCEPTANCE, 60)
    compiled = compile_production(manifest)
    assert compiled.frames == 1800 and len(compiled.segments) == 20
    assert [event["purpose"] for event in plan.events] == [
        "orientation", "danger", "escape", "arrival", "resolution"
    ]
    assert [event["start_frame"] for event in plan.events] == [0, 360, 720, 1080, 1440]
    assert staging["environment_transition_frames"] == [1080]
    assert all(720 <= r["frame"] < 1080 for r in staging["running_actions"])
    assert {r["environment"] for r in staging["running_actions"]} == {"frost_peak"}
    assert staging["longest_consecutive_reaction_run"] <= 2
    assert not staging["beacon_visible"] and not staging["violations"]
    assert all(s["storm_foreground"] for s in staging["shots"][4:12])
    assert not any(s["storm_foreground"] for s in staging["shots"][:4] + staging["shots"][12:])
    assert staging["shots"][-1]["expressions"][-1] == "happy"
    assert {s["camera"] for s in staging["shots"][8:12]} == {"follow", "establishing"}
    assert len({tuple(s["zoom"]) for s in staging["shots"][8:12]}) == 4
    again, manifest_again, staging_again = direct(ACCEPTANCE, 60)
    assert (plan_summary(again), manifest_again, staging_again) == (
        plan_summary(plan), manifest, staging
    )


@pytest.mark.parametrize(("prompt", "locations", "run"), [
    ("In an orchard Yellow Mellow runs through the grove. No beacon.", ["orchard"], "orchard"),
    ("In the orchard he walks to the ridge. No storm or beacon.", ["orchard", "frost_peak"], None),
    ("He runs from the blizzard on the mountain, then reaches the orchard.", ["frost_peak", "orchard"], "frost_peak"),
    ("On a mountain he walks to safety. Never run.", ["frost_peak"], None),
    ("He investigates an emergency beacon on the mountain.", ["frost_peak"], None),
])
def test_unrelated_short_prompts_compile(prompt, locations, run):
    plan, manifest, staging = direct(prompt)
    assert compile_production(manifest).frames == 450
    assert plan.environments == locations
    assert {r["environment"] for r in staging["running_actions"]} == ({run} if run else set())
    assert staging["beacon_visible"] == ("investigates" in prompt)


def test_single_location_long_plan_preserves_length():
    plan, _, _ = direct("Yellow Mellow walks through the orchard and feels relieved.", 60)
    assert len(plan.beats) == 20
    assert plan.events[-1]["end_frame_exclusive"] == 1800


def test_legacy_plan_and_manifest_digests_match_approved_baseline():
    def digest(data):
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    evidence = Path(__file__).parent / "fixtures" / "sprint_h_legacy_digests.json"
    for sample in json.loads(evidence.read_text()):
        plan = plan_story(sample["prompt"], sample["duration"])
        assert digest(plan_summary(plan)) == sample["plan_sha256"]
        assert digest(build_production_manifest(plan)) == sample["manifest_sha256"]


def test_local_incidents_follow_mention_order():
    plan = plan_story(
        "On a mountain a blizzard begins. Later he finds a beacon. Then he runs.",
        60,
        strategy="director-v2",
    )
    assert [event["purpose"] for event in plan.events] == [
        "orientation", "danger", "beacon", "escape", "resolution"
    ]
