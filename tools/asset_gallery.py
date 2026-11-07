"""Build an offline visual catalog and render registered evidence sequentially."""

import argparse
import json
import platform
import re
import shutil
import tempfile
import time
from pathlib import Path

from reelforge.catalog.inventory import ROOT, inventory
from reelforge.cinematic_projects.contract import capabilities, load_cinematic_project
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.architecture.buildings import BUILDINGS
from reelforge.visual_library.composition.building_showcase import building_showcase

from reelforge.visual_library.world_assets import WORLD_ASSETS
from reelforge.visual_library.living_assets import EFFECTS, PROPS
from reelforge.characters.living import PROFILES
from reelforge.characters.living_transitions import TRANSITIONS
from reelforge.visual_library.composition.interactions import INTERACTIONS
from reelforge.visual_library.composition.living_worlds import MOODS, WORLD_KITS

TEMPLATE = Path(__file__).with_name("asset_gallery.html")
SIZE = (720, 1280)
MOBILE = (360, 640)
FRAMES = (0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 89)
KEY = re.compile(r"[a-z][a-z0-9_.-]*\Z")


def cinematic_examples():
    directories = (ROOT / "examples/cinematic-projects", ROOT / "examples/sprint-d")
    registry = ROOT / "assets/audio"
    # Diagnostic audio examples carry an explicit fixture-setup link in the operator guide.
    projects = []
    for path in sorted(p for directory in directories for p in directory.glob("*.json")):
        source = json.loads(path.read_text(encoding="utf-8"))
        if source["audio"] is None:
            project = load_cinematic_project(path, registry)
            title, frames = project.title, project.frames
        else:
            title, frames = source["title"], len(source["shots"]) * 90
        projects.append({
            "title": title, "seconds": frames / 30, "diagnostic_audio": source["audio"] is not None,
            "request": "../../" + path.relative_to(ROOT).as_posix(),
        })
    discovery = capabilities(registry)
    return {"guide": "../CINEMATIC_PROJECTS.md", "examples": projects,
            "cameras": discovery["cameras"], "contract": discovery["contract"]}


def metadata(previews=None):
    """Read the authoritative inventory. This step has no native dependency."""
    previews = previews or {}
    entries = []
    for entry in inventory()["components"]:
        evidence = previews.get(entry["id"], {})
        details = entry["details"]
        entries.append({
            **{field: entry[field] for field in (
                "id", "name", "family", "type", "restrictions", "dependencies",
                "registration", "planner_exposure", "quality_review", "production_status",
            )},
            "description": details.get("description") or next(iter(entry["restrictions"]), entry["name"]),
            "variants": [
                {
                    "id": variant,
                    "description": details.get("variant_descriptions", {}).get(variant, ""),
                    "preview": evidence.get("variants", {}).get(variant),
                }
                for variant in entry["variants"]
            ],
            "evidence": evidence.get("context", []),
            "preview_status": (
                "rendered" if evidence.get("variants") else
                "context_only" if evidence.get("context") else "unavailable"
            ),
        })
    evidence = ROOT / "docs/visual-evidence/sprint-b"
    def world_paths(kit, mood):
        folder = "sprint-d" if kit in MOODS else "sprint-b"
        paths = [f"visual-evidence/{folder}/{kit}-{mood}-{width}.png" for width in (720, 360)]
        return ["../" + path for path in paths if (ROOT / "docs" / path).is_file()]
    def motion_path(key):
        folder = "sprint-d" if key in MOODS else "sprint-b"
        return f"visual-evidence/{folder}/motion/{key}.webp"

    return {"components": entries, "cinematic_projects": cinematic_examples(), "living_worlds": {
        "motion": {
            key: "../" + motion_path(key)
            for key in (*PROFILES, *WORLD_KITS, *INTERACTIONS)
            if (ROOT / "docs" / motion_path(key)).is_file()
        },
        "world_previews": {
            f"{kit}-{mood}": world_paths(kit, mood)
            for kit, moods in WORLD_KITS.items() for mood in moods
        },
        "transitions": {
            actor: {
                key: f"../visual-evidence/sprint-b1/motion/{actor}-{key}.webp"
                for key in TRANSITIONS
                if (ROOT / f"docs/visual-evidence/sprint-b1/motion/{actor}-{key}.webp").is_file()
            }
            for actor in PROFILES
        },
        "worlds": WORLD_KITS,
        "interactions": {identity: vars(spec) for identity, spec in INTERACTIONS.items()},
    }}


def write_metadata(output, previews=None):
    payload = json.dumps(metadata(previews), ensure_ascii=False, indent=2) + "\n"
    (output / "assets.json").write_text(payload, encoding="utf-8")
    # The HTML parser recognizes a script end tag even in JSON string literals.
    embedded = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = TEMPLATE.read_text(encoding="utf-8").replace("<!-- ASSET_DATA -->", embedded)
    (output / "index.html").write_text(html, encoding="utf-8")


def artwork(asset, variant, placement):
    commands = recipe(asset_by_id(asset), variant, 0.8, 0.52, 0, 0, None)
    return tuple(placement.command(command) for command in commands)


def historical_evidence(directory):
    """Reuse attributed catalog stills, including shared context and variant sheets."""
    previews = {}
    evidence_root = (ROOT / "docs/visual-evidence").resolve()
    for entry in inventory()["components"]:
        context, seen = [], set()
        for key, label in (
            ("preview_evidence", "Catalog reference (may show other components)"),
            ("integration_evidence", "Historical scene context"),
        ):
            for relative in entry["details"].get(key, ()):
                source = (ROOT / relative).resolve()
                if not source.is_relative_to(evidence_root) or source.suffix not in {".png", ".jpg"}:
                    raise ValueError(f"Unsupported catalog evidence path: {relative}")
                if source in seen or not source.is_file():
                    continue
                seen.add(source)
                target = Path("history", source.relative_to(evidence_root))
                destination = directory / target
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copyfile(source, destination)
                context.append({"path": (Path("previews") / target).as_posix(), "label": label})
        if context:
            previews[entry["id"]] = {"context": context}
    return previews


def render_evidence(directory):
    from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
    from reelforge.rendering.diagnostic import color
    from reelforge.resources.monitor import JobMonitor

    transparent = color("000000", 0)
    farm_fill = color("565d58")
    renderer = CairoRenderer()
    previews = historical_evidence(directory)
    measurements = {}
    with JobMonitor(workspace=directory) as monitor:
        def draw(surface, commands, logical_size, background):
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Preview cancelled: {monitor.limit_reason}")
            renderer.draw(surface, commands, logical_size=logical_size, background=background)

        def still(name, commands, size=SIZE, logical_size=MOBILE, background=transparent):
            with renderer.surface(*size) as surface:
                start = time.perf_counter()
                cpu = time.process_time()
                draw(surface, commands, logical_size, background)
                timing = {
                    "draw_ms": 1000 * (time.perf_counter() - start),
                    "cpu_ms": 1000 * (time.process_time() - cpu),
                }
                monitor.sample()
                surface.write_png(directory / name)
                timing["pixel_sha256"] = surface.pixel_sha256()
            return f"previews/{name}", timing

        for identity, item in (WORLD_ASSETS | PROPS | EFFECTS).items():
            left, top, right, bottom = item.bounds
            scale = min(1.65, 300 / (right - left), 270 / (bottom - top))
            placement = Placement(180 - scale * (left + right) / 2,
                                  320 - scale * (top + bottom) / 2, scale)
            variants, results = {}, {}
            for variant in item.variants:
                if identity in EFFECTS:
                    asset = asset_by_id(identity)
                    commands = recipe(asset, variant, .7, .4, 0, .7, None)
                    if identity == "smoke_wisp_01":
                        commands = tuple(Placement(175, 465, 2).command(c) for c in commands)
                    variants[variant], timing = still(f"{identity}-{variant}.png", commands,
                                                      background=color("33414d"))
                else:
                    commands = artwork(identity, variant, placement)
                    variants[variant], timing = still(f"{identity}-{variant}.png", commands)
                paths, operations = cost(commands)
                results[variant] = {**timing, "paths": paths, "operations": operations}
            previews[identity] = {"variants": variants}
            measurements[identity] = {"standalone": results}

        for identity, building in BUILDINGS.items():
            asset = asset_by_id(identity)
            if not KEY.fullmatch(identity) or any(not KEY.fullmatch(v) for v in asset.variants):
                raise ValueError("Invalid preview file identifier")
            variants, results, sheet = {}, {}, []
            left, top, right, bottom = building.bounds
            center = (left + right) / 2
            center_y = (top + bottom) / 2
            for index, variant in enumerate(asset.variants):
                commands = artwork(identity, variant, Placement(
                    180 - 1.45 * center, 320 - 1.45 * center_y, 1.45,
                ))
                variants[variant], timing = still(f"{identity}-{variant}.png", commands)
                paths, ops = cost(commands)
                results[variant] = {**timing, "paths": paths, "operations": ops}
                sheet.extend(artwork(identity, variant, Placement(
                    120 + 240 * index - center, 103 - center_y,
                )))
            sheet_size = (240 * len(variants), 206)
            contact_sheet, _ = still(f"{identity}-variants.png", tuple(sheet),
                                     sheet_size, sheet_size, color("d8d4c7"))

            scene = compile_scene(validate_scene(building_showcase(identity, building.farm_variant)))
            with renderer.surface(*SIZE) as surface:
                start, cpu = time.perf_counter(), time.process_time()
                path_counts, op_counts = [], []
                for frame in FRAMES:
                    commands = scene_frame(scene, frame)
                    paths, ops = cost(commands)
                    path_counts.append(paths)
                    op_counts.append(ops)
                    draw(surface, commands, MOBILE, farm_fill)
                integrated = {
                    "sample_frames": list(FRAMES),
                    "wall_ms_per_frame": 1000 * (time.perf_counter() - start) / len(FRAMES),
                    "cpu_ms_per_frame": 1000 * (time.process_time() - cpu) / len(FRAMES),
                    "paths": max(path_counts), "operations": max(op_counts),
                    "path_allowance": scene.path_allowance,
                    "operation_allowance": scene.operation_allowance,
                }
                monitor.sample()
            commands = scene_frame(scene, 36)
            full, full_timing = still(f"{identity}-farm.png", commands, background=farm_fill)
            mobile, mobile_timing = still(
                f"{identity}-farm-mobile.png", commands, MOBILE, background=farm_fill,
            )
            measurements[identity] = {
                "standalone": results, "integrated": integrated,
                "integrated_sha256": full_timing["pixel_sha256"],
                "mobile_sha256": mobile_timing["pixel_sha256"],
                "tree_peak_so_far_bytes": monitor.tree_peak,
            }
            previews[identity] = {
                "variants": variants,
                "context": [
                    {"path": contact_sheet, "label": "Variant sheet in selector order"},
                    {"path": full, "label": f"Dusk Farm · {building.farm_variant} · 720 × 1280"},
                    {"path": mobile, "label": f"Dusk Farm · {building.farm_variant} · 360 × 640"},
                ],
            }
    if monitor.cancelled.is_set():
        raise RuntimeError(f"Preview cancelled: {monitor.limit_reason}")
    report = monitor.report()
    return previews, {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "renderer": backend_versions(),
        "measurements": measurements,
        "monitor": {key: report[key] for key in (
            "memory_policy", "observed_memory_sources", "oom_telemetry_continuous",
            "estimated_simultaneous_tree_peak_rss_bytes", "sampling_interval_seconds",
            "samples", "job_budget_bytes", "reserve_bytes", "limit_reason",
            "minimum_effective_available_bytes", "wall_seconds",
        )},
    }


def build(output, *, metadata_only=False):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Keep staging outside the browsable gallery and on the same filesystem
    # so publishing the preview directory can use a rename.
    scratch = Path(tempfile.gettempdir())
    if scratch.stat().st_dev != output.stat().st_dev:
        scratch = output.parent
    with tempfile.TemporaryDirectory(prefix=".gallery-", dir=scratch) as temporary:
        stage = Path(temporary)
        if metadata_only:
            write_metadata(stage)
            metrics = None
        else:
            (stage / "previews").mkdir()
            previews, metrics = render_evidence(stage / "previews")
            write_metadata(stage, previews)
            current = output / "previews"
            if current.exists():
                current.rename(stage / "previous-previews")
            (stage / "previews").rename(current)
        for name in ("assets.json", "index.html"):
            (stage / name).replace(output / name)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build",))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/asset-gallery")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--metrics", type=Path, help="Optional JSON measurement output")
    args = parser.parse_args()
    if args.metadata_only and args.metrics:
        parser.error("--metrics requires rendering")
    metrics = build(args.output_dir, metadata_only=args.metadata_only)
    if args.metrics:
        args.metrics.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
