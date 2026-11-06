"""A1 registration, geometry, scene admission and offline gallery evidence."""

import hashlib
import json
import math
import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

from reelforge.catalog.inventory import ROOT, inventory
from reelforge.core.errors import InputError
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.architecture.buildings import BUILDINGS
from reelforge.visual_library.composition.building_showcase import building_showcase

from tools import asset_gallery

GALLERY = ROOT / "docs/asset-gallery"
from reelforge.visual_library.world_assets import WORLD_ASSETS

from reelforge.characters.living import PROFILES
from reelforge.visual_library.living_assets import EFFECTS, PROPS

ADDITIONS = WORLD_ASSETS | PROFILES | PROPS | EFFECTS

BASELINE_CATALOG = "df3c9ab5a6e4ee50c54a0f03c8d897512ef49623a67649fbb9ae82bf7288e6a7"
VARIANTS = {
    "house_01": ("daylight", "dusk", "weathered"),
    "shop_01": ("open", "closed", "weathered"),
}


@pytest.mark.parametrize("identity,variants", VARIANTS.items())
def test_building_recipes(identity, variants):
    asset = asset_by_id(identity)
    assert asset.kind == "asset"
    assert asset.variants == variants
    assert asset.anchor == (0, 0)
    assert asset.upright
    left, top, right, bottom = BUILDINGS[identity].bounds
    assert BUILDINGS[identity].doorway[1] == 0

    distinct = set()
    for variant in variants:
        commands = recipe(asset, variant, 0.8, 0.52, 0.2, 0, None)
        assert commands == recipe(asset, variant, 0.8, 0.52, 0.2, 2.9, None)
        distinct.add(commands)
        paths, ops = cost(commands)
        assert paths <= asset.max_paths
        assert ops <= asset.max_ops
        ground_contact = False
        for command in commands:
            for path in (command.path, command.clip or ()):
                for op in path:
                    coords = op.points
                    assert all(math.isfinite(value) for value in coords), op.kind
                    for x, y in zip(coords[::2], coords[1::2], strict=True):
                        assert left <= x <= right and top <= y <= bottom
                        ground_contact |= y == 0
        assert ground_contact
    assert len(distinct) == len(variants)

    with pytest.raises(ValueError, match="Unknown .* variant"):
        recipe(asset, "unknown", 0, 0, 0, 0, None)


@pytest.mark.parametrize("identity,variants", VARIANTS.items())
def test_validated_scene_placement(identity, variants):
    for variant in variants:
        manifest = building_showcase(identity, variant)
        compiled = compile_scene(validate_scene(manifest))
        placed = next(n for n in compiled.hierarchy if n.id == "building")
        assert placed.world == Placement(220, 473, 0.96)
        assert placed.world.point(0, 0) == (220, 473)
        assert placed.world.point(0, -10) == pytest.approx((220, 463.4))
        assert compiled.painter_ids.index("ground") < compiled.painter_ids.index("building")
        assert compiled.painter_ids.index("building") < compiled.painter_ids.index("rowan")
        assert scene_frame(compiled, 36) == scene_frame(compiled, 36)

    example = ROOT / "examples/asset-a1" / f"{identity}.scene.json"
    assert json.loads(example.read_text()) == building_showcase(identity, BUILDINGS[identity].farm_variant)
    manifest = building_showcase(identity, "missing")
    with pytest.raises(InputError, match="variant"):
        validate_scene(manifest)
    manifest = building_showcase(identity, variants[0])
    node = next(n for n in manifest["nodes"] if n["id"] == "building")
    node["transform"]["rotation_degrees"] = 15
    with pytest.raises(InputError, match="zero composed rotation"):
        compile_scene(validate_scene(manifest))


def test_historical_catalog_entries_preserved_with_barn_evidence_link():
    previous = [e for e in inventory()["components"] if e["id"] not in BUILDINGS and e["id"] not in ADDITIONS]
    assert len(previous) == 48
    barn = next(e for e in previous if e["id"] == "barn_01")
    assert barn["details"].pop("integration_evidence") == [
        "docs/visual-evidence/stage0c/rowan-barn.jpg"
    ]
    digest = hashlib.sha256(json.dumps(previous, sort_keys=True).encode()).hexdigest()
    assert digest == BASELINE_CATALOG


def embedded_data(html):
    content = re.search(r'<script type="application/json" id="asset-data">(.*?)</script>', html, re.S)
    return json.loads(content.group(1))


def test_gallery_matches_inventory_and_local_evidence():
    page = (GALLERY / "index.html").read_text()
    data = json.loads((GALLERY / "assets.json").read_text())
    assert data == embedded_data(page)
    catalog = inventory()["components"]
    entries = data["components"]
    assert [e["id"] for e in entries] == [e["id"] for e in catalog]
    assert len({e["id"] for e in entries}) == len(entries) == 50 + len(ADDITIONS)
    references = set()
    for entry, registered in zip(entries, catalog, strict=True):
        assert entry["name"] == registered["name"]
        assert entry["family"] == registered["family"]
        assert entry["quality_review"] == registered["quality_review"]
        assert [v["id"] for v in entry["variants"]] == registered["variants"]
        paths = [v["preview"] for v in entry["variants"] if v["preview"]]
        context = [item["path"] for item in entry["evidence"]]
        assert entry["preview_status"] == (
            "rendered" if paths else "context_only" if context else "unavailable"
        )
        for value in paths + context:
            path = Path(value)
            assert path.parts[0] == "previews" and ".." not in path.parts
            assert (GALLERY / path).is_file()
            references.add(path)
        if entry["id"] in BUILDINGS:
            assert len(paths) == 3 and len(context) == 3
    assert references == {p.relative_to(GALLERY) for p in (GALLERY / "previews").rglob("*") if p.is_file()}
    assert "Preview unavailable" in page
    assert "entry.id.includes(query) || entry.name.toLowerCase().includes(query)" in page
    assert "fetch(" not in page and "https://" not in page


def test_metadata_only_is_native_free_and_escapes_html(tmp_path, monkeypatch):
    catalog = inventory()
    dangerous = "</script><script>alert(1)</script>"
    catalog["components"][0]["name"] = dangerous
    monkeypatch.setitem(sys.modules, "cairo", None)
    monkeypatch.setattr(asset_gallery, "inventory", lambda: catalog)
    assert asset_gallery.build(tmp_path, metadata_only=True) is None
    html = (tmp_path / "index.html").read_text()
    data = embedded_data(html)
    assert data["components"][0]["name"] == dangerous
    assert all(e["preview_status"] == "unavailable" for e in data["components"])
    assert dangerous not in html and "innerHTML" not in html
    parser = HTMLParser()
    parser.feed(html)
    assert not (tmp_path / "previews").exists()


def png_size(path):
    with path.open("rb") as stream:
        header = stream.read(24)
    assert header.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR")
    return struct.unpack(">II", header[16:])


def test_preview_formats_and_dimensions():
    for identity, variants in VARIANTS.items():
        previews = GALLERY / "previews"
        for variant in variants:
            assert png_size(previews / f"{identity}-{variant}.png") == (720, 1280)
        assert png_size(previews / f"{identity}-farm.png") == (720, 1280)
        assert png_size(previews / f"{identity}-farm-mobile.png") == (360, 640)
        assert png_size(previews / f"{identity}-variants.png") == (720, 206)
    for photo in (GALLERY / "previews/history").rglob("*.jpg"):
        assert photo.read_bytes().startswith(b"\xff\xd8\xff")


def test_native_rebuild_is_deterministic_and_removes_stale_previews(tmp_path):
    pytest.importorskip("cairo")

    def files(root):
        return {
            p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()
        }

    first = asset_gallery.build(tmp_path)
    original = files(tmp_path)
    (tmp_path / "previews/stale.png").write_bytes(b"stale")
    second = asset_gallery.build(tmp_path)
    assert files(tmp_path) == original
    for identity, data in first["measurements"].items():
        repeated = second["measurements"][identity]
        if identity not in BUILDINGS:
            assert repeated["standalone"].keys() == data["standalone"].keys()
            assert all(repeated["standalone"][v]["pixel_sha256"] == item["pixel_sha256"]
                       for v, item in data["standalone"].items())
            continue
        assert repeated["integrated_sha256"] == data["integrated_sha256"]
        assert repeated["mobile_sha256"] == data["mobile_sha256"]
        assert {v["pixel_sha256"] for v in repeated["standalone"].values()} == {
            v["pixel_sha256"] for v in data["standalone"].values()
        }
    # Committed metadata is platform-independent. Cairo rasterization can vary across versions.
    for name in ("index.html", "assets.json"):
        assert (tmp_path / name).read_bytes() == (GALLERY / name).read_bytes()
