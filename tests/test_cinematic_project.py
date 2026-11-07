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
    ("mood", "windy", "/beats/0/mood"),
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


@pytest.mark.parametrize(("action", "actor", "world", "mood", "variant"), [
    ("pickup_carry_place", "scout_01", "village_lane", "evening", "wrapped"),
    ("push_cart", "mechanic_01", "woodland_creek", "windy", "loaded"),
])
def test_interaction_state_spans_independent_camera_shots(
    request_data, action, actor, world, mood, variant
):
    from math import dist

    from reelforge.cinematic_projects.sampling import state_at, visual_frame

    request_data["beats"][0].update(action=action, actor=actor, world=world, mood=mood,
                                    variant=variant)
    plan = compile_project(request_data, REGISTRY)
    before, after = state_at(plan, 89), state_at(plan, 90)
    assert before["shot"] != after["shot"]
    assert (before["authored_frame"], after["authored_frame"]) == (89, 90)
    assert before["contact"] and after["contact"]
    assert max(before["hand_socket_error"], after["hand_socket_error"]) < 1e-7
    assert dist(before["root_world"], after["root_world"]) < 3
    assert dist(before["prop_world"], after["prop_world"]) < 3
    first = visual_frame(plan, 90)
    assert visual_frame(plan, 89) != first
    assert visual_frame(plan, 90) == first
    assert state_at(plan, 90) == after


def test_caption_outlines_render_as_filled_mobile_geometry():
    pytest.importorskip("cairo")
    from reelforge.cinematic_projects.captions import caption_paths
    from reelforge.cinematic_projects.contract import Caption
    from reelforge.rendering.backends.cairo import CairoRenderer
    from reelforge.rendering.diagnostic import color

    paths = caption_paths(Caption(0, 30, "subtitle", ("Text must be visible.",)))
    assert len(paths) == 3 and len(paths[-1].path) > 30
    renderer = CairoRenderer()
    with renderer.surface(360, 640) as target:
        renderer.draw(target, paths, background=color("000000"), logical_size=(360, 640))
        ink = sum(target.pixel_rgba8_premultiplied(x, y)[0] > 160
                  for x in range(35, 302) for y in range(495, 521))
        assert ink > 200


def test_registered_audio_plans_role_and_frame_aligned_trim(request_data):
    request_data["audio"] = dict(sample_rate=48000, channels=2, codec="aac", bitrate=128000,
                                narration=None, cues=[dict(asset_id="diag_suspense",
                                start_frame=83, trim_start_frame=2, trim_end_frame=15, gain=.5)])
    project = compile_project(request_data, REGISTRY)
    cue, = project.audio_cues
    assert cue["start_sample"] == 83 * 1600
    assert cue["effective_samples"] == 13 * 1600
    assert [shot["audio_indices"] for shot in project.timeline()["shots"]] == [[0], [0]]
    request_data["audio"]["cues"][0]["asset_id"] = "diag_opening"
    with pytest.raises(InputError, match="expected registered role sfx"):
        compile_project(request_data, REGISTRY)
