"""The opt-in signal beat preserves staging and keeps the shot grid."""
import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import acting_at, state_at, visual_frame
from reelforge.cinematic_projects.staging import Performer, pose_at
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets/audio"
ORIGINAL = ROOT / "examples/sprint-d8-d9/the_last_transmission.json"


def request(style="alert", signal="unlit"):
    data = json.loads(ORIGINAL.read_text())
    beat = data["beats"][2]
    beat.update(cue_frame=71, cue_style=style, signal=signal, pacing="urgent", delay_frames=2)
    beat["partner"].update(delay_frames=14, facing="left")
    return data


@pytest.mark.parametrize(("style", "signal", "early", "settled"), [
    ("alert", "unlit", "frightened", "concerned"),
    ("relief", "lit", "surprised", "happy"),
])
def test_signal_edges_and_grounded_asymmetric_response(style, signal, early, settled):
    data = request(style, signal)
    project = compile_project(data, REGISTRY)
    assert project.timeline() == compile_project(data, REGISTRY).timeline()
    cue = 341
    before = state_at(project, cue - 1)
    at = state_at(project, cue)
    assert before["signal"] != at["signal"] == signal
    assert visual_frame(project, cue - 1) != visual_frame(project, cue)
    assert state_at(project, cue + 8)["expression"] == early
    assert state_at(project, cue + 8)["partner"]["expression"] == "concerned"
    assert state_at(project, cue + 20)["partner"]["expression"] == early
    assert state_at(project, cue + 60)["expression"] == settled

    beat = project.at(cue)[0].beat
    lead = Performer(beat.actor, "idle", beat.expression, beat.facing, beat.delay, beat.pacing)
    assert acting_at(beat, 71).pose == pose_at(lead, 71, refined=True)[0]
    assert acting_at(beat, 135).pose == pose_at(lead, 135, refined=True)[0]
    assert acting_at(beat, 88).pose != pose_at(lead, 88, refined=True)[0]
    for frame in range(cue - 1, cue + 61):
        state = state_at(project, frame)
        for subject, reference in ((state, before), (state["partner"], before["partner"])):
            assert subject["root_world"][0] == reference["root_world"][0]
            assert subject["facing"] == reference["facing"]
            for foot, point in reference["feet_world"].items():
                assert subject["feet_world"][foot] == pytest.approx(point, abs=1e-8)
    assert state_at(project, 359)["beat_frame"] + 1 == state_at(project, 360)["beat_frame"]
    sample = visual_frame(project, 360)
    visual_frame(project, 343)
    assert visual_frame(project, 360) == sample


@pytest.mark.parametrize(("change", "error"), [
    ({"cue_frame": 175}, "Leave time"),
    ({"cue_frame": 71.5}, "integer"),
    ({"action": "walk"}, "stationary idle"),
    ({"cue_style": "relief"}, "lamp to turn on"),
    ({"cue_style": "arbitrary"}, "is not one of"),
])
def test_opt_in_signal_contract_is_bounded(change, error):
    data = request()
    data["beats"][2].update(change)
    with pytest.raises(InputError, match=error):
        compile_project(data, REGISTRY)


def test_legacy_cue_rule_and_plan_are_preserved():
    data = json.loads(ORIGINAL.read_text())
    beat = data["beats"][2]
    project = compile_project(data, REGISTRY)
    assert all("signal_cue" not in shot for shot in project.timeline()["shots"])
    beat["cue_frame"] = 71
    with pytest.raises(InputError, match="editorial cut"):
        compile_project(data, REGISTRY)
