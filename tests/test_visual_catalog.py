"""Catalog coverage and validation without native rendering."""

import json
import sys
from copy import deepcopy

import pytest
from jsonschema.exceptions import ValidationError

from reelforge.catalog.__main__ import generate, main, read_json, validate
from reelforge.catalog.inventory import ROOT, inventory
from reelforge.characters.registry import character_ids
from reelforge.procedural.contract import FAMILIES
from reelforge.scenes.assets import ASSETS


@pytest.fixture
def catalog():
    return inventory()


@pytest.fixture
def schema():
    return read_json(ROOT / "catalog" / "schema.json")


def test_registration_coverage_and_variants(catalog, schema):
    validate(catalog, schema, inventory())
    entries = {entry["id"]: entry for entry in catalog["components"]}
    assert {key for key, entry in entries.items() if "scene" in entry["registration"]} == {
        asset.id for asset in ASSETS
    }
    assert {key for key, entry in entries.items() if entry["type"] == "character"} == set(
        character_ids()
    )
    for asset in ASSETS:
        assert entries[asset.id]["variants"] == list(asset.variants)
    for family in FAMILIES:
        assert entries[family]["type"] == "procedural"
        assert entries[family]["registration"] == []
        assert entries[family]["planner_exposure"] == "unavailable"
    assert entries["barn_01"]["planner_exposure"] == "unavailable"
    assert entries["beacon_01"]["planner_exposure"] == "preset_only"
    assert entries["orchard"]["planner_exposure"] == "selectable"


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        ("id", "other_id", ValueError, "IDs disagree"),
        ("id", "Invalid!", ValidationError, "does not match"),
        ("production_status", "production_ready", ValidationError, None),
        ("registration", [], ValidationError, None),
        ("sources", ["src/reelforge/absent.py:example"], ValueError, "Missing implementation"),
        ("sources", ["src/reelforge/scenes/assets.py:bogus"], ValueError, "Metadata disagrees"),
        ("variants", ["invented"], ValueError, "Metadata disagrees"),
    ],
)
def test_rejects_inconsistent_metadata(catalog, schema, field, value, error, message):
    changed = deepcopy(catalog)
    changed["components"][0][field] = value
    with pytest.raises(error, match=message):
        validate(changed, schema, catalog)


def test_rejects_duplicate_or_missing_ids(catalog, schema):
    changed = deepcopy(catalog)
    changed["components"].append(changed["components"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        validate(changed, schema, catalog)
    del changed["components"][-2:]
    with pytest.raises(ValueError, match="IDs disagree"):
        validate(changed, schema, catalog)


def test_deterministic_generation_and_stale_check(catalog, tmp_path):
    generate(catalog, tmp_path, check=False)
    originals = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    generate(inventory(), tmp_path, check=False)
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == originals
    generate(catalog, tmp_path, check=True)
    (tmp_path / "components.md").write_text("stale", encoding="utf-8")
    with pytest.raises(ValueError, match="Stale catalog output: components.md"):
        generate(catalog, tmp_path, check=True)


def test_cli_discovery_without_native_renderer(capsys, monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("Catalog discovery started an external process")

    monkeypatch.setitem(sys.modules, "cairo", None)
    monkeypatch.setattr("subprocess.Popen", forbidden)
    assert main(["list", "--family", "architecture"]) == 0
    rows = [line.split("\t") for line in capsys.readouterr().out.splitlines()]
    assert rows and all(row[2] == "architecture" for row in rows)
    assert "barn_01" in {row[0] for row in rows}
    assert main(["show", "barn_01"]) == 0
    assert json.loads(capsys.readouterr().out)["variants"] == ["default"]
    with pytest.raises(SystemExit, match="2"):
        main(["show", "missing"])
    assert "Unknown component ID" in capsys.readouterr().err
    assert main(["validate"]) == 0
    assert main(["generate", "--check"]) == 0
