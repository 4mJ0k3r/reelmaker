"""Benchmark editorial clocks and explicit shared lamp coverage."""

import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import acting_at, camera_for, named_node, state_at
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "examples/sprint-f3-f4/the_light_in_the_empty_town_cinematic_refined.json"


def request():
    data = json.loads(PROJECT.read_text())
    data["audio"] = None
    return data


def test_benchmark_boundaries_and_lamp_clock():
    data = request()
    project = compile_project(data, ROOT / "assets/audio")
    assert project.frames == 1800
    assert [s.start for s in project.shots] == list(range(0, 1800, 90))
    assert len(project.captions) == 18
    assert project.captions[15].lines == ("A lamp came on.",)
    off, on = (state_at(project, frame) for frame in (1529, 1530))
    assert (off["signal"], on["signal"]) == ("unlit", "lit")
    assert (off["active_captions"], on["active_captions"]) == ([14], [15])
    assert on["beat_frame"] == off["beat_frame"] + 1 == 90
    assert state_at(project, 1544)["expression"] == "surprised"
    assert state_at(project, 1544)["partner"]["expression"] == "concerned"
    assert state_at(project, 1563)["partner"]["expression"] == "surprised"

    cameras = []
    for frame in (1529, 1530):
        shot, local = project.at(frame)
        beat = shot.beat
        mira, bram = acting_at(beat, local), acting_at(beat, local, partner=True)
        camera = camera_for(shot, mira, frame, partner=bram)
        cameras.append(camera)
        lamp = named_node(beat, "streetlamp")
        actors = (named_node(beat, "actor"), named_node(beat, "partner"))
        for subject in (*actors, lamp):
            transform = camera.transform(subject.depth)
            x = transform.tx + subject.world.x * transform.sx
            assert 44 <= x <= 316
    assert cameras[0] == cameras[1]


def test_signal_two_shot_rejects_unrelated_beat():
    data = request()
    data["shots"][0]["camera"] = "signal_two_shot"
    with pytest.raises(InputError, match="requires a grounded signal cue"):
        compile_project(data, ROOT / "assets/audio")
