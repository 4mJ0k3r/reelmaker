"""Check the motion envelopes and deterministic semantic coverage."""

import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import acting_at, camera_for

ROOT = Path(__file__).resolve().parents[1]


def _project(name):
    path = ROOT / f"examples/sprint-d/{name}.json"
    return json.loads(path.read_text())


def test_auto_coverage_schedules_the_cue_and_shared_closing():
    data = _project("unexpected_meeting")
    for shot in data["shots"]:
        shot.pop("focus", None)
        shot["camera"] = "auto"
    project = compile_project(data, ROOT / "assets/audio")
    assert [(shot.camera, shot.focus) for shot in project.shots] == [
        ("establishing", "actor"), ("reaction", "partner"),
        ("object_reveal", "actor"), ("two_shot", "actor"),
    ]


@pytest.mark.parametrize("name", ["outpost_camera", "ravine_camera"])
def test_camera_moves_without_an_internal_jump(name):
    project = compile_project(_project(name), ROOT / "assets/audio")
    for shot in project.shots:
        views = [camera_for(shot, acting_at(shot.beat, frame - shot.beat.start), frame)
                 for frame in range(shot.start, shot.end)]
        assert views[0] != views[-1]
        for a, b in zip(views, views[1:]):
            assert abs(a.x - b.x) < 4
            assert abs(a.y - b.y) < 3
            assert abs(a.zoom - b.zoom) < .05


def test_actor_cue_must_land_on_an_editorial_cut():
    from reelforge.core.errors import InputError

    data = _project("unexpected_meeting")
    data["beats"][0]["cue_frame"] = 181
    with pytest.raises(InputError, match="editorial cut"):
        compile_project(data, ROOT / "assets/audio")
