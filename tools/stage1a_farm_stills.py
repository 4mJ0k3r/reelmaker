"""Generate farm reference stills and a bounded render-cost sample. No video."""

import argparse
import json
import platform
import time
from pathlib import Path

from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
from reelforge.rendering.diagnostic import color
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.assets import asset_by_id, cost, recipe
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.farm import GROUND, HORIZON, farm_scene

FRAMES = (0, 8, 16, 24, 32, 36, 44, 52, 60, 68, 76, 89)
SIZE = (720, 1280)


def art(asset, variant, x, y, scale=1):
    placement = Placement(x, y, scale)
    commands = recipe(asset_by_id(asset), variant, 0.8, 0.52, 0, 0, None)
    return tuple(placement.command(command) for command in commands)


def sample(output):
    renderer = CairoRenderer()
    with (
        JobMonitor(workspace=output.parent.resolve()) as monitor,
        renderer.surface(*SIZE) as surface,
    ):
        output.mkdir(exist_ok=False)

        def draw(commands):
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Still sampling cancelled: {monitor.limit_reason}")
            renderer.draw(surface, commands, background=color("565d58"), logical_size=(360, 640))

        scene = compile_scene(farm_scene())
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        maximum = (0, 0)
        for frame in FRAMES:
            commands = scene_frame(scene, frame)
            draw(commands)
            maximum = tuple(map(max, zip(maximum, cost(commands), strict=True)))
        cpu_seconds = time.process_time() - cpu_start
        wall_seconds = time.perf_counter() - wall_start
        monitor.sample()
        render_peak = monitor.tree_peak

        commands = scene_frame(scene, 36)
        draw(commands)
        original = surface.pixel_sha256()
        draw(scene_frame(scene, 36))
        if original != surface.pixel_sha256():
            raise RuntimeError("Integrated frame changed on identical re-evaluation")
        surface.write_png(output / "farm-establishing.png")

        for name, view, legacy, frame in (
            ("farm-before", "establishing", True, 36),
            ("farm-medium", "medium", False, 36),
            ("stability-first", "medium", False, 0),
            ("stability-last", "medium", False, 89),
        ):
            draw(scene_frame(compile_scene(farm_scene(view, legacy=legacy)), frame))
            surface.write_png(output / f"{name}.png")

        sky = art("cinematic_dusk_sky_01", "default", 0, 0)
        draw(sky + art("cinematic_dusk_hills_01", "rolling", *HORIZON))
        surface.write_png(output / "sky-hills.png")
        draw(art("cinematic_farm_track_01", "default", *GROUND))
        surface.write_png(output / "ground-path.png")
        draw(
            art("cinematic_dusk_contact_01", "trunk", 88, 483, 1.12)
            + art("cinematic_dusk_contact_01", "trunk", 236, 483, 1.12)
            + art("cinematic_farm_tree_01", "broad", 88, 483, 1.12)
            + art("cinematic_farm_tree_01", "leaning", 236, 483, 1.12)
        )
        surface.write_png(output / "tree-silhouettes.png")
    if monitor.cancelled.is_set():
        raise RuntimeError(f"Still sampling cancelled: {monitor.limit_reason}")
    return {
        "python": platform.python_version(),
        "renderer": backend_versions(),
        "resolution": SIZE,
        "frame_indices": FRAMES,
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "frame_36_pixel_sha256": original,
        "max_sampled_paths_and_ops": maximum,
        "allowed_paths_and_ops": (scene.path_allowance, scene.operation_allowance),
        "sample_tree_peak_rss_bytes": render_peak,
        "monitor": monitor.report(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New evidence directory under existing outputs")
    args = parser.parse_args()
    print(json.dumps(sample(args.output), indent=2))
