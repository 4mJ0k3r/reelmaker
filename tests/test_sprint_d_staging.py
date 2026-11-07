"""Contract coverage for additive bounded two-actor performances."""

import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import state_at, visual_frame
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples/sprint-d/unexpected_meeting.json"
REGISTRY = ROOT / "assets/audio"


def test_pair_uses_independent_clocks_and_preserves_positions_at_cut():
    project = compile_project(json.loads(REQUEST.read_text()), REGISTRY)
    before, after = (state_at(project, frame) for frame in (89, 90))
    assert before["shot"] != after["shot"]
    assert before["root_world"] == after["root_world"]
    assert before["partner"]["root_world"] == after["partner"]["root_world"]
    assert before["partner"]["expression"] == "neutral"
    assert after["partner"]["expression"] == "surprised"
    assert after["authored_frame"] == 89
    assert after["partner"]["authored_frame"] == 0
    assert after["partner"]["facing"] == "left"
    assert state_at(project, 180)["partner"]["facing"] == "right"
    assert after["actor"] != after["partner"]["actor"]
    assert all(y == pytest.approx(577.1) for _, y in after["partner"]["feet_world"].values())
    sample = visual_frame(project, 273)
    assert visual_frame(project, 8) != sample
    assert visual_frame(project, 273) == sample


@pytest.mark.parametrize("field,value", [
    ("actor", "scout_01"), ("stage_x", 81), ("action", "push_cart"),
    ("stage_x", 170.0), ("delay_frames", 7.0),
])
def test_rejects_untrusted_or_overlapping_pairs(field, value):
    data = json.loads(REQUEST.read_text())
    data["beats"][0]["partner"][field] = value
    with pytest.raises(InputError):
        compile_project(data, REGISTRY)


def test_legacy_contract_rejects_extended_beats():
    data = json.loads(REQUEST.read_text())
    data["schema_version"] = "cinematic-project-0.1"
    with pytest.raises(InputError):
        compile_project(data, REGISTRY)
