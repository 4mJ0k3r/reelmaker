"""Reproduce matched Cairo framing, cut reviews and Stage 2C resource measurements."""

import argparse
import json
import math
import platform
import time
from pathlib import Path

from stage1c_cold_stills import monitored_result
from stage2a_character_evidence import SIZE, cairo_image, sheet

from reelforge.direction.contract import compile_direction
from reelforge.direction.sampling import (
    actor_override,
    bounds,
    camera_at,
    direction_frame,
    inspect_frame,
    instance_commands,
    intersection,
    shot_at,
)
from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
from reelforge.rendering.diagnostic import color
from reelforge.resources.deployment import cpu_snapshot
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.assets import cost
from reelforge.scenes.graph import evaluate_layers
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.visual_library.composition.character_staging import (
    WORLDS,
    cinematic_character_staging,
)
from reelforge.visual_library.composition.mellow_approach import mellow_storyboard
from reelforge.visual_library.composition.rowan_approach import rowan_storyboard

CASES = (
    ("yellow-ridge", "yellow_mellow_v2", "cold_ridge", mellow_storyboard),
    ("rowan-farm", "rowan_01", "farm", rowan_storyboard),
    ("yellow-farm", "yellow_mellow_v2", "farm", mellow_storyboard),
    ("rowan-ridge", "rowan_01", "cold_ridge", rowan_storyboard),
)
BEATS = ((12, "Context"), (50, "Attention"), (76, "Reaction"), (89, "Settle"))
SAMPLES = (0, 12, 21, 22, 33, 50, 56, 57, 65, 72, 76, 83, 89)


def metrics(plan, frame, prop):
    info = inspect_frame(plan, frame)
    shot = shot_at(plan, frame)
    actor = info["actor_bounds_logical"]
    obj = bounds(instance_commands(plan, prop, frame))
    x0, y0, x1, y1 = actor
    margin = shot.margin
    visible_height = min(640, y1) - max(0, y0)
    safe = (margin, margin, 360 - margin, 640 - margin)
    return {
        "frame": frame,
        "source_frame": info["source_frame"],
        "actor_world": info["actor_world"],
        "actor_bbox_pixels": [v * 2 for v in actor],
        "actor_width_px": (x1 - x0) * 2,
        "projected_actor_height_px": (y1 - y0) * 2,
        "visible_actor_height_px": visible_height * 2,
        "visible_frame_height_percent": visible_height / 640 * 100,
        "actor_safe_margin_full": all(
            (x0 >= margin, y0 >= margin, x1 <= 360 - margin, y1 <= 640 - margin)
        ),
        "actor_safe_margin_for_declared_framing": (
            x0 >= margin
            and x1 <= 360 - margin
            and margin <= y0 <= 640 - margin
            and (shot.framing != "full" or y1 <= 640 - margin)
        ),
        "actual_feet_crop": y1 > 640,
        "safe_margin_px": margin * 2,
        "object_id": prop,
        "object_bbox_pixels": [v * 2 for v in obj],
        "object_safe_visible_fraction": intersection(obj, safe)
        / ((obj[2] - obj[0]) * (obj[3] - obj[1])),
        "foreground_overlap_upper": info["foreground_bbox_overlap_upper"],
        "tracking_error_logical": info["tracking_error_logical"],
        "camera": info["camera"],
        "target_kind": shot.target.kind,
        "target_node": shot.target.node_id,
        "track": shot.track,
        "framing": shot.framing,
        "shot": shot.id,
    }


def cut_metrics(plan):
    cuts = []
    for shot in plan.shots[1:]:
        old = camera_at(plan, shot.start - 1)
        new = camera_at(plan, shot.start)
        before, after = (inspect_frame(plan, f) for f in (shot.start - 1, shot.start))
        cuts.append(
            {
                "frames": [shot.start - 1, shot.start],
                "continuity": shot.continuity,
                "scale_ratio": new.zoom / old.zoom,
                "pan_logical": math.hypot(new.x - old.x, new.y - old.y),
                "actor_world_displacement": math.dist(before["actor_world"], after["actor_world"]),
            }
        )
    return cuts


def benchmark(renderer, plan, workspace):
    times = {"camera_seconds": 0.0, "geometry_seconds": 0.0, "raster_seconds": 0.0}
    hashes = {}
    maximum = (0, 0)
    with JobMonitor(workspace=workspace.resolve()) as monitor, renderer.surface(*SIZE) as surface:
        start = time.perf_counter()
        for frame in SAMPLES:
            t0 = time.perf_counter()
            camera = camera_at(plan, frame)
            t1 = time.perf_counter()
            layers = evaluate_layers(
                plan.compiled,
                frame,
                camera_override=camera,
                character_override=actor_override(plan, frame),
            )
            commands = tuple(command for layer in layers for command in layer.commands)
            t2 = time.perf_counter()
            renderer.draw(surface, commands, background=color("25394b"), logical_size=(360, 640))
            t3 = time.perf_counter()
            times["camera_seconds"] += t1 - t0
            times["geometry_seconds"] += t2 - t1
            times["raster_seconds"] += t3 - t2
            maximum = tuple(max(a, b) for a, b in zip(maximum, cost(commands), strict=True))
            hashes[str(frame)] = surface.pixel_sha256()
        wall = time.perf_counter() - start
        renderer.draw(
            surface, direction_frame(plan, 76), background=color("25394b"), logical_size=(360, 640)
        )
        assert surface.pixel_sha256() == hashes["76"]
    return {
        **times,
        "wall_seconds": wall,
        "paths_operations": maximum,
        "scene_allowance": (plan.compiled.path_allowance, plan.compiled.operation_allowance),
        "hashes": hashes,
        "host": cpu_snapshot(monitor.initial),
        **monitored_result(monitor),
    }


def build(output):
    output.mkdir()
    renderer = CairoRenderer()
    rows = {}
    combination = []
    hero_cuts = []
    grounding = []
    for i, (name, actor, world, builder) in enumerate(CASES):
        base = compile_storyboard(builder(world, "medium")).direction
        plan = compile_direction(cinematic_character_staging(actor, world))
        prop = WORLDS[world][0]
        selected = [metrics(plan, f, prop) for f, _ in BEATS]
        baseline = [metrics(base, f, prop) for f, _ in BEATS]
        rows[name] = {
            "baseline": baseline,
            "staged": selected,
            "cuts": cut_metrics(plan),
            "actor_frame_parity": all(
                actor_override(base, f) == actor_override(plan, f) for f in range(90)
            ),
        }
        panels = [(label, cairo_image(renderer, direction_frame(plan, f))) for f, label in BEATS]
        combination.extend((f"{name} / {label}", img) for label, img in panels)
        if i >= 2:
            continue
        sheet(output / f"{name}-progression.jpg", panels, 4, (180, 320))
        after = panels[2][1]
        after.save(output / f"{name}-reaction.jpg", quality=91, optimize=True)
        before = cairo_image(renderer, direction_frame(base, 76))
        sheet(
            output / f"{name}-comparison.jpg",
            [("Approved / 76", before), ("Stage 2C / 76", after)],
            2,
            (360, 640),
        )
        for shot in plan.shots[1:]:
            for f in (shot.start - 1, shot.start):
                hero_cuts.append(
                    (
                        f"{name} / {shot_at(plan, f).id} {f}",
                        cairo_image(renderer, direction_frame(plan, f)),
                    )
                )
        for f in (50, plan.shots[2].start - 1):
            still = cairo_image(renderer, direction_frame(plan, f))
            box = metrics(plan, f, prop)["actor_bbox_pixels"]
            cx = (box[0] + box[2]) / 2
            y = box[3]
            grounding.append(
                (
                    f"{name} / {f}",
                    still.crop(tuple(round(v) for v in (cx - 112, y - 170, cx + 112, y + 28))),
                )
            )
        if i == 0:
            wide = compile_storyboard(builder(world, "establishing")).direction
            rows[name]["original_wide"] = [metrics(wide, f, prop) for f, _ in BEATS]
            result = {
                "python": platform.python_version(),
                "renderer": backend_versions(),
                "resolution": SIZE,
                "frames": SAMPLES,
                "original_wide": benchmark(renderer, wide, output),
                "approved_clip_medium": benchmark(renderer, base, output),
                "staged": benchmark(renderer, plan, output),
            }
            (output / "performance.json").write_text(json.dumps(result, indent=2) + "\n")
    sheet(output / "four-combinations.jpg", combination, 4, (140, 249))
    sheet(output / "camera-cuts.jpg", hero_cuts, 4, (180, 320))
    sheet(output / "grounding.jpg", grounding, 4, (175, 155))
    (output / "framing.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
