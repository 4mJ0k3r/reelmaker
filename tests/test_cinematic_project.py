import copy
import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project, load_cinematic_project
from reelforge.contracts.project import project_digest
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/cinematic-projects"
REGISTRY = ROOT / "assets/audio"


@pytest.fixture
def request_data():
    return json.loads((EXAMPLES / "pickup_proof.json").read_text())


def test_plan_is_canonical_and_reacts_to_edit(request_data):
    first = compile_project(request_data, REGISTRY).timeline()
    reordered = dict(reversed(list(request_data.items())))
    assert compile_project(reordered, REGISTRY).timeline() == first
    first_digest = first.pop("plan_sha256")
    assert first_digest == project_digest(first)
    request_data["beats"][0]["actor"] = "mechanic_01"
    assert compile_project(request_data, REGISTRY).timeline()["plan_sha256"] != first_digest
    assert first["shots"][1]["acting_frame_at_start"] == 90
    assert first["shots"][1]["continuity"] == "continuous_beat"


@pytest.mark.parametrize(("field", "value", "path"), [
    ("mood", "windy", "/beats/0/world"),
    ("actor", "rowan_01", "/beats/0/actor"),
    ("variant", "loaded", "/beats/0/variant"),
    ("start", 90, "/beats/0"),
    ("end", 180.0, "/beats/0"),
    ("stage_x", 120, "/beats/0"),
    ("effect", {"id": "rain_field_01", "variant": "autumn"}, "/beats/0/effect/variant"),
    ("action", "../../run.py", "/beats/0/action"),
])
def test_rejects_incompatible_or_unsafe_beat(request_data, field, value, path):
    request_data["beats"][0][field] = value
    with pytest.raises(InputError) as caught:
        compile_project(request_data, REGISTRY)
    assert caught.value.issue.path == path


@pytest.mark.parametrize("invalid", [
    '{"x":0,"x":1}', '{"x":NaN}', '{"x":1e900}', '[' * 33 + ']' * 33,
    ' ' * 1_048_577,
])
def test_load_uses_strict_bounded_parser(tmp_path, invalid):
    file = tmp_path / "invalid.json"
    file.write_text(invalid)
    with pytest.raises(InputError):
        load_cinematic_project(file, REGISTRY)


@pytest.mark.parametrize("lines", [["  "], ["गाना"], ["Bad\n"], ["<script>"]])
def test_rejects_unsupported_caption_text(request_data, lines):
    request_data["captions"] = [{"start": 1, "end": 2, "style": "subtitle", "lines": lines}]
    with pytest.raises(InputError):
        compile_project(request_data, REGISTRY)


def test_rejects_caption_overlap(request_data):
    cue = {"start": 30, "end": 92, "style": "subtitle", "lines": ["Across the cut."]}
    request_data["captions"] = [cue, {**copy.deepcopy(cue), "start": 90, "end": 120}]
    with pytest.raises(InputError, match="non-overlapping"):
        compile_project(request_data, REGISTRY)


def test_captions_are_planned_on_both_sides_of_cut(request_data):
    request_data["captions"] = [
        {"start": 89, "end": 91, "style": "subtitle", "lines": ["Across the cut."]}
    ]
    assert [s["caption_indices"] for s in compile_project(request_data, REGISTRY).timeline()[
        "shots"]] == [[0], [0]]
