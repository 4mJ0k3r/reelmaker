"""Contract, reproducibility, native-free CLI, and camera-only parity."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from reelforge.contracts.project import MAX_INPUT_BYTES, project_digest
from reelforge.core.errors import InputError
from reelforge.direction.sampling import actor_override, camera_at
from reelforge.episodes.contract import compile_episode
from reelforge.episodes.schema import episode_schema
from reelforge.story_templates import contract, registry
from reelforge.visual_library.composition.cinematic_story import cinematic_story
from tools.story_templates import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/story_templates"
FILES = sorted(EXAMPLES.glob("*.json"))


@pytest.fixture(scope="module")
def generated():
    return {
        path.stem: (template, edit, *contract.build(template, edit))
        for path in FILES
        for template, edit in [contract.load_request(path)]
    }


def test_discovery_registry_matches_all_compiled_examples(generated):
    assert len(generated) == 4
    assert len({t.id for t in registry.TEMPLATES}) == len(registry.TEMPLATES)
    schema = contract.request_schema()
    Draft202012Validator.check_schema(schema)
    for path in FILES:
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
        template, edit, document, plan = generated[path.stem]
        Draft202012Validator(episode_schema()).validate(document)
        assert compile_episode(document) == plan
        report = contract.inspect(template, edit, document, plan)
        assert report["episode_contract"] == plan.schema_version == "episode-0.3"
        assert report["duration_frames"] == plan.frames == 270
        assert report["episode_cut_frames"] == [90, 180]
        assert report["renderable"] and not report["native_preflight_run"]
        assert plan.silent and report["audio"] == "silent"
        assert report["output"] == [720, 1280]
        assert {e.id for e in template.edits} == {v["id"] for v in report["variants"]}
        assert template.default_variant in {e.id for e in template.edits}
        assert {(e["asset_id"], e["variant"]) for e in report["events"]} == set(template.events)


def test_original_and_approved_manifest_digests(generated):
    assert project_digest(cinematic_story("the_other_light")) == (
        "8d276d403f48f9768a19bca2f902e7a26afaf4984933d906ff76a50bad4b0cbd"
    )
    assert project_digest(generated["other_light_approved"][2]) == (
        "7e2d4ff954eac140589d4a182459a2e3550afffe8e70284e08e131faea504f1d"
    )
    assert project_digest(generated["empty_doorway_approved"][2]) == (
        "d3f67b2b8512c3d61390c427e26bebae18654580445e7554fc34e2fd8533687c"
    )


@pytest.mark.parametrize("alternate", ["other_light_ridge_watch", "empty_doorway_threshold_hold"])
def test_alternate_changes_only_admitted_cameras(generated, alternate):
    template, _, new, alternative = generated[alternate]
    _, _, old, approved = generated[f"{template.id}_approved"]
    assert new != old
    assert [s["id"] for s in new["segments"]] == [s["id"] for s in old["segments"]]
    for a, b in zip(new["segments"], old["segments"], strict=True):
        assert a["direction"]["base"] == b["direction"]["base"]
    assert new["segments"][1] == old["segments"][1]
    for frame in range(90):
        before = approved.segments[1].direction
        after = alternative.segments[1].direction
        assert actor_override(before, frame) == actor_override(after, frame)
    z0 = camera_at(approved.segments[-1].direction, 89).zoom
    z1 = camera_at(alternative.segments[-1].direction, 89).zoom
    assert abs(z1 - z0) >= 0.07


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("schema_version", "future", "REQUEST_VERSION"),
        ("template_id", "not_registered", "TEMPLATE_UNKNOWN"),
        ("variant", "threshold_hold", "TEMPLATE_VARIANT"),
        ("character", "rowan_01", "TEMPLATE_INCOMPATIBLE"),
        ("character", "unknown", "TEMPLATE_INCOMPATIBLE"),
        ("world", "farm", "TEMPLATE_INCOMPATIBLE"),
        ("world", "https://example.com", "TEMPLATE_INCOMPATIBLE"),
        ("variant", [], "REQUEST_TYPE"),
        ("code", "import os", "REQUEST_FIELD"),
        ("asset/path", "/tmp/untrusted", "REQUEST_FIELD"),
    ],
)
def test_schema_and_semantic_rejections(field, value, code):
    request = json.loads((EXAMPLES / "other_light_approved.json").read_text())
    request[field] = value
    assert not Draft202012Validator(contract.request_schema()).is_valid(request)
    with pytest.raises(InputError) as error:
        contract.resolve(request)
    assert error.value.issue.code == code
    assert error.value.issue.path == "/" + field.replace("/", "~1")


def test_required_fields_and_non_object():
    request = json.loads((EXAMPLES / "other_light_approved.json").read_text())
    for field in contract.FIELDS:
        incomplete = {k: v for k, v in request.items() if k != field}
        assert not Draft202012Validator(contract.request_schema()).is_valid(incomplete)
        with pytest.raises(InputError) as error:
            contract.resolve(incomplete)
        assert error.value.issue.as_dict()["path"] == f"/{field}"
    with pytest.raises(InputError, match="JSON object"):
        contract.resolve([])


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b'{"variant":0,"variant":1}', "JSON_DUPLICATE_KEY"),
        (b"[" * 33 + b"]" * 33, "JSON_INVALID"),
        (b" " * (MAX_INPUT_BYTES + 1), "INPUT_TOO_LARGE"),
        (b'{"variant":NaN}', "JSON_NONFINITE"),
        (b'{"variant":1e999}', "JSON_NONFINITE"),
        (b"{", "JSON_INVALID"),
        (b"\xff", "JSON_INVALID"),
    ],
)
def test_bounded_loader(raw, code, tmp_path):
    request = tmp_path / "input.json"
    request.write_bytes(raw)
    with pytest.raises(InputError) as error:
        contract.load_request(request)
    assert error.value.issue.code == code


def test_cli_native_free_and_atomic_generation(tmp_path, capsys, monkeypatch):
    monkeypatch.setitem(sys.modules, "cairo", None)

    def forbidden(*args, **kwargs):
        raise AssertionError("Template discovery or generation started a process")

    monkeypatch.setattr("subprocess.Popen", forbidden)
    example = str(EXAMPLES / "empty_doorway_threshold_hold.json")
    for command in (["list"], ["schema"], ["validate", example], ["inspect", example]):
        assert main(command) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)
    first, second = tmp_path / "one.json", tmp_path / "two.json"
    for destination in (first, second):
        assert main(["generate", example, "--output", str(destination)]) == 0
        assert json.loads(capsys.readouterr().out)["renderable"]
    assert first.read_bytes() == second.read_bytes()
    assert main(["generate", example, "--output", str(first)]) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "OUTPUT_EXISTS"
    assert first.read_bytes() == second.read_bytes()

    def no_link(*args):
        raise OSError("simulated publication failure")

    monkeypatch.setattr("tools.story_templates.os.link", no_link)
    failed = tmp_path / "failed.json"
    assert main(["generate", example, "--output", str(failed)]) == 1
    assert not failed.exists()
    assert set(tmp_path.iterdir()) == {first, second}


def test_extension_is_source_owned(generated, monkeypatch):
    template, edit, document, _ = generated["empty_doorway_approved"]
    new_edit = replace(edit, builder=lambda: document)
    demo = replace(template, id="test_only", edits=(new_edit,))
    monkeypatch.setattr(registry, "TEMPLATES", (*registry.TEMPLATES, demo))
    request = json.loads((EXAMPLES / "empty_doorway_approved.json").read_text())
    request["template_id"] = "test_only"
    Draft202012Validator(contract.request_schema()).validate(request)
    resolved = contract.resolve(request)
    assert resolved == (demo, new_edit)
    assert contract.build(*resolved)[0] == document
