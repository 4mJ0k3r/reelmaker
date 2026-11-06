"""Render bounded Cold Ridge stills and measure the CPU-only paths."""

import argparse
import json
import platform
import time
from pathlib import Path

from reelforge.blocking.contract import compile_blocking
from reelforge.blocking.sampling import blocking_frame, inspect_frame
from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
from reelforge.rendering.diagnostic import color
from reelforge.resources.deployment import cpu_snapshot, memory_observability
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.cold_ridge import cold_ridge_scene, cold_ridge_walk

SIZE = (720, 1280)
FRAMES = (0, 12, 24, 36, 48, 60, 72, 89)


def art(asset_id, variant, x, y, scale=1):
    placement = Placement(x, y, scale)
    return tuple(
        placement.command(command)
        for command in recipe(asset_by_id(asset_id), variant, 0.18, 0.51, 0.05, 1.2, None)
    )


def monitored_result(monitor):
    observed = memory_observability(monitor.initial, monitor.final)
    if (
        monitor.cancelled.is_set()
        or not monitor.oom_telemetry_continuous
        or observed["oom_events_changed"]
    ):
        raise RuntimeError(f"Cold Ridge monitor did not pass: {monitor.limit_reason or observed}")
    return {
        "peak_tree_rss_bytes": monitor.tree_peak,
        "cancelled": False,
        "memory_policy": monitor.memory_policy,
        "oom_event_delta": observed["oom_event_delta"],
    }


def benchmark(output, **options):
    renderer = CairoRenderer()
    compiled = compile_scene(cold_ridge_scene(**options))
    hashes = {}
    peak_paths = peak_ops = 0
    with JobMonitor(workspace=output.resolve()) as monitor, renderer.surface(*SIZE) as surface:
        start, cpu = time.perf_counter(), time.process_time()
        for frame in FRAMES:
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Benchmark cancelled: {monitor.limit_reason}")
            commands = scene_frame(compiled, frame)
            paths, ops = cost(commands)
            peak_paths, peak_ops = max(paths, peak_paths), max(ops, peak_ops)
            renderer.draw(surface, commands, background=color("25394b"), logical_size=(360, 640))
            hashes[str(frame)] = surface.pixel_sha256()
        wall, cpu = time.perf_counter() - start, time.process_time() - cpu
        renderer.draw(
            surface,
            scene_frame(compiled, 36),
            background=color("25394b"),
            logical_size=(360, 640),
        )
        if surface.pixel_sha256() != hashes["36"]:
            raise RuntimeError("Frame 36 changed on repeat rasterization")
    return {
        "options": options,
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "wall_ms_per_frame": wall * 1000 / len(FRAMES),
        "hashes": hashes,
        "sample_paths_and_ops": [peak_paths, peak_ops],
        "scene_allowance": [compiled.path_allowance, compiled.operation_allowance],
        **monitored_result(monitor),
    }


def sample(output):
    output.mkdir(exist_ok=False)
    # Medium legacy storm is the highest command count of the matched proof variants.
    results = [
        benchmark(output, **options)
        for options in (
            {},
            {"view": "medium", "weather": "storm"},
            {"view": "medium", "weather": "storm", "legacy": True},
        )
    ]
    renderer = CairoRenderer()
    with JobMonitor(workspace=output.resolve()) as monitor, renderer.surface(*SIZE) as surface:

        def still(name, commands):
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Still sampling cancelled: {monitor.limit_reason}")
            renderer.draw(surface, commands, background=color("25394b"), logical_size=(360, 640))
            surface.write_png(output / f"{name}.png")

        for name, options in (
            ("cold-establishing", {}),
            ("cold-before", {"legacy": True}),
            ("cold-medium", {"view": "medium"}),
            ("cold-saddle", {"layout": "saddle"}),
            ("cold-storm", {"weather": "storm"}),
        ):
            still(name, scene_frame(compile_scene(cold_ridge_scene(**options)), 36))

        sky = art("frost_sky_01", "default", 0, 0)
        for name, far, near in (
            ("mountains-before", "far", "mid"),
            ("mountains", "cinematic_far", "cinematic_massif"),
        ):
            still(
                name,
                sky + art("frost_peaks_01", far, 180, 292) + art("frost_peaks_01", near, 180, 300),
            )

        for name, tall, low in (
            ("conifers-before", "tall", "short"),
            ("conifers", "pinnacle", "windshear"),
        ):
            still(
                name,
                art("frost_ridge_01", "sculpted", 180, 513)
                + art("pine_snow_01", tall, 87, 522, 1.18)
                + art("pine_snow_01", low, 244, 522, 1.18),
            )
        still(
            "terrain-rock",
            sky
            + art("frost_ridge_01", "sculpted", 180, 357)
            + art("cinematic_dusk_contact_01", "prop", 205, 436, 1.05)
            + art("frost_rocks_01", "cliff", 205, 436, 0.72),
        )
        walk = compile_blocking(cold_ridge_walk())
        for frame in (35, 36, 37, 51, 72):
            still(f"walk-{frame:02}", blocking_frame(walk, frame))
    contacts = [
        contact["error"]
        for frame in range(90)
        for contact in inspect_frame(walk, frame)["contacts"]
        if contact["error"] is not None
    ]
    return {
        "python": platform.python_version(),
        "renderer": backend_versions(),
        "host": cpu_snapshot(monitor.initial),
        "resolution": SIZE,
        "frames": FRAMES,
        "benchmarks": results,
        "still_monitor": monitored_result(monitor),
        "walk_max_contact_error": max(contacts),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Fresh directory under outputs")
    print(json.dumps(sample(parser.parse_args().output), indent=2))
