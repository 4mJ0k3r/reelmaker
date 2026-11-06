"""Stage 3A admission, editorial mapping and exact staging parity."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from reelforge.audio.registry import AudioRegistry
from reelforge.core.errors import InputError
from reelforge.direction.contract import compile_direction
from reelforge.direction.sampling import actor_override, direction_frame
from reelforge.episodes.contract import compile_episode, frame_origin, inspect_episode, load_episode
from reelforge.episodes.schema import episode_schema
from reelforge.productions.schema import production_schema
from reelforge.visual_library.composition.character_staging import cinematic_character_staging
from reelforge.visual_library.composition.cinematic_story import cinematic_story

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def document():
    return cinematic_story()


@pytest.fixture(scope="module")
def plan(document):
    return compile_episode(document)


@pytest.fixture(scope="module")
def legacy():
    return json.loads((ROOT / "examples/episodes/relay_to_shelter.json").read_text())


@pytest.fixture(scope="module")
def validator():
    schema = episode_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_recipe_is_fixed_and_reproducible(document, validator, tmp_path):
    with pytest.raises(ValueError, match="the_other_light"):
        cinematic_story("unknown")
    with pytest.raises(TypeError):
        cinematic_story(world="farm")
    assert cinematic_story("the_other_light") == document
    validator.validate(document)
    path = tmp_path / "episode.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert load_episode(path).frames == 270
    assert document["audio"] is None
    assert [s["id"] for s in document["segments"]] == ["beacon", "approach", "ridge"]


def test_legacy_and_mixed_episode_sources(document, legacy, validator):
    assert legacy["schema_version"] == "episode-0.1"
    validator.validate(legacy)
    legacy_plan = compile_episode(legacy)
    assert not legacy_plan.silent
    assert inspect_episode(legacy_plan, AudioRegistry(ROOT / "assets/audio"))["audio_cues"]
    silent = {**legacy, "schema_version": "episode-0.2", "audio": None}
    validator.validate(silent)
    assert compile_episode(silent).silent
    registered = next(
        s
        for s in legacy["segments"]
        if s["storyboard"]["world"]["schema_version"] == "environment-0.1"
    )
    mixed = {**document, "segments": [registered, document["segments"][1]]}
    validator.validate(mixed)
    plan = compile_episode(mixed)
    result = inspect_episode(plan, AudioRegistry(ROOT / "assets/audio"), frame=90)
    assert "storyboard" in result["segments"][0]
    assert "direction" in result["segments"][1]
    assert result["contract"] == "episode-0.3"
    assert (result["segment_id"], result["local_frame"], result["visual"]["shot"]) == (
        "approach",
        0,
        "context",
    )


@pytest.mark.parametrize("version", ["episode-0.1", "episode-0.2"])
def test_old_versions_reject_direction(document, validator, version):
    invalid = {**document, "schema_version": version}
    assert not validator.is_valid(invalid)
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == "/segments/0"


@pytest.mark.parametrize(
    ("keys", "path"),
    [
        (("storyboard",), "/segments/1"),
        (("path",), "/segments/1"),
        (("direction", "source"), "/segments/1"),
    ],
)
def test_reject_extra_or_untrusted_segment_fields(document, validator, keys, path):
    invalid = deepcopy(document)
    item = invalid["segments"][1]
    for key in keys:
        item[key] = "https://example.invalid/scene.json"
    assert not validator.is_valid(invalid)
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == path


def test_nested_direction_errors_and_geometry_rejection(document, validator):
    invalid = deepcopy(document)
    invalid["segments"][1]["direction"]["shots"][1]["target"]["id"] = "absent"
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == "/segments/1/direction/shots/1/target/id"

    invalid = deepcopy(document)
    invalid["segments"][1]["direction"]["base"]["base"] = {
        "schema_version": "composition-0.1",
        "geometry": {"commands": []},
    }
    assert not validator.is_valid(invalid)
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == "/segments/1/direction/base/base"


def test_segment_bounds_and_unique_ids(document, validator):
    invalid = {**document, "segments": [document["segments"][0]] * 11}
    assert not validator.is_valid(invalid)
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == "/segments"
    invalid["segments"] = invalid["segments"][:2]
    with pytest.raises(InputError) as error:
        compile_episode(invalid)
    assert error.value.issue.path == "/segments/1/id"


def test_mapping_and_registered_scene_continuity(plan):
    source = [
        (segment.id, local)
        for segment, local in (frame_origin(plan, f) for f in range(plan.frames))
    ]
    assert source == [(name, i) for name in ("beacon", "approach", "ridge") for i in range(90)]
    assert inspect_episode(plan, AudioRegistry(ROOT / "assets/audio"))["editorial_cuts"] == [
        90,
        180,
    ]
    for frame in (-1, 270):
        with pytest.raises(InputError):
            frame_origin(plan, frame)
    opening, approach, ending = (s.direction for s in plan.segments)

    def node(direction, name):
        return next(n for n in direction.compiled.hierarchy if n.id == name)

    for name in ("beacon", "ground", "near_peaks", "pine_right"):
        a, b, c = (node(d, name) for d in (opening, approach, ending))
        assert a == b == c
    assert opening.actor_id is ending.actor_id is None
    assert {n.id: n.asset_id for n in approach.compiled.scene.nodes}[approach.actor_id] == (
        "yellow_mellow_v2"
    )
    assert {n.id: n.asset_id for n in ending.compiled.scene.nodes}["distant_light"] == (
        "answer_light_01"
    )
    assert "distant_light" not in opening.compiled.painter_ids


def test_exact_stage2c_performance_projection_and_contacts(document, plan):
    staged = cinematic_character_staging("yellow_mellow_v2", "cold_ridge")
    assert document["segments"][1]["direction"] == staged
    actual = plan.segments[1].direction
    expected = compile_direction(staged)
    assert [(s.id, s.start, s.target.node_id) for s in actual.shots] == [
        ("context", 0, "beacon"),
        ("attention", 22, "rowan"),
        ("reaction", 57, "rowan"),
    ]
    for frame in range(90):
        assert actor_override(actual, frame) == actor_override(expected, frame)
        assert direction_frame(actual, frame) == direction_frame(expected, frame)


def test_native_directed_episode_transaction(document, tmp_path):
    import shutil

    from reelforge.core.errors import OperationError
    from reelforge.episodes.workflow import render_episode

    pytest.importorskip("cairo")
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        pytest.skip("FFmpeg and ffprobe are needed for the native transaction test")
    if Path("/tmp") in tmp_path.resolve().parents:
        pytest.skip("Use --basetemp outside /tmp for the native workspace preflight")
    plan = compile_episode({**document, "segments": document["segments"][:1]})
    output = tmp_path / "episode"
    report = render_episode(plan, output, registry_root=ROOT / "assets/audio")
    assert report["success"] and report["published"] and report["transaction_clean"]
    assert report["media_verified"] and report["streams"]["exact_video_pts"]
    assert report["streams"]["audio_streams"] == 0
    assert report["verification"]["decoded_frames"] == 90
    assert report["whole_job_memory"]["limit_reason"] is None
    clip = output / "reel.mp4"
    before = clip.stat()
    with pytest.raises(OperationError) as error:
        render_episode(plan, output, registry_root=ROOT / "assets/audio")
    assert error.value.code == "OUTPUT_EXISTS"
    assert clip.stat().st_ino == before.st_ino
    assert clip.stat().st_mtime_ns == before.st_mtime_ns
    assert {p.name for p in output.iterdir()} == {"reel.mp4", "report.json"}
    assert not Path(report["transaction_path"]).exists()


def test_production_schema_keeps_its_storyboard_shape(document, legacy):
    schema = production_schema()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    production = {**legacy, "schema_version": "production-0.1", "audio": None}
    validator.validate(production)
    invalid = {**production, "segments": document["segments"]}
    assert not validator.is_valid(invalid)
