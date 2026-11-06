"""Generate Cairo review sheets and a matched farm benchmark (Pillow for sheet assembly)."""

import argparse
import json
import math
import platform
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from phase9c_snowy_storyboard import shot1
from PIL import Image, ImageDraw
from stage1c_cold_stills import monitored_result

from reelforge.blocking.sampling import inspect_frame, sample
from reelforge.characters.presets import SKELETON, CharacterPreset, sample_pose
from reelforge.characters.rowan import draw_character
from reelforge.characters.rowan_performance import FaceCue, face_cue
from reelforge.characters.secondary import SecondaryMotion, preset_secondary
from reelforge.direction.sampling import direction_frame
from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
from reelforge.rendering.diagnostic import color
from reelforge.resources.deployment import cpu_snapshot
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.assets import cost
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.visual_library.composition.rowan_approach import rowan_storyboard

SIZE = (720, 1280)
FRAMES = (3, 20, 34, 46, 47, 58, 59, 64, 65, 70, 76, 83, 89)


def cairo_image(renderer, commands, backdrop="ddd6c6"):
    with TemporaryDirectory(dir="outputs") as staging, renderer.surface(*SIZE) as surface:
        renderer.draw(surface, commands, background=color(backdrop), logical_size=(360, 640))
        png = Path(staging) / "still.png"
        surface.write_png(png)
        with Image.open(png) as image:
            return image.convert("RGB")


def sheet(path, panels, columns, size):
    width, height = size
    label_height = 22
    rows = math.ceil(len(panels) / columns)
    canvas = Image.new("RGB", (width * columns, rows * (height + label_height)), "#232d3d")
    draw = ImageDraw.Draw(canvas)
    for i, (label, still) in enumerate(panels):
        x, y = (i % columns) * width, (i // columns) * (height + label_height)
        canvas.paste(still.resize(size, Image.Resampling.LANCZOS), (x, y + label_height))
        draw.text((x + 5, y + 5), label, fill="white")
    canvas.save(path, quality=87, optimize=True)


def benchmark(renderer, direction, output):
    geometry = raster = 0.0
    hashes = {}
    maxima = (0, 0)
    with JobMonitor(workspace=output.resolve()) as monitor, renderer.surface(*SIZE) as surface:
        started = time.perf_counter()
        for frame in FRAMES:
            t0 = time.perf_counter()
            commands = direction_frame(direction, frame)
            t1 = time.perf_counter()
            renderer.draw(surface, commands, background=color("25394b"), logical_size=(360, 640))
            t2 = time.perf_counter()
            geometry += t1 - t0
            raster += t2 - t1
            maxima = tuple(max(a, b) for a, b in zip(maxima, cost(commands), strict=True))
            hashes[str(frame)] = surface.pixel_sha256()
        total = time.perf_counter() - started
        renderer.draw(
            surface,
            direction_frame(direction, 76),
            background=color("25394b"),
            logical_size=(360, 640),
        )
        assert surface.pixel_sha256() == hashes["76"]
    return dict(
        geometry_seconds=geometry,
        raster_seconds=raster,
        wall_seconds=total,
        hashes=hashes,
        paths_and_operations=maxima,
        scene_allowance=(direction.compiled.path_allowance, direction.compiled.operation_allowance),
        fps=30,
        host=cpu_snapshot(monitor.initial),
        **monitored_result(monitor),
    )


def motion_metrics(plan):
    samples = [inspect_frame(plan, frame) for frame in range(90)]
    slides = []
    for a, b in zip(samples[:-1], samples[1:], strict=True):
        for first, second in zip(a["contacts"], b["contacts"], strict=True):
            if (
                first["state"] == second["state"] == "flat"
                and first["cycle_start"] == second["cycle_start"]
            ):
                slides.append(math.dist(first["world"], second["world"]))
    boundaries = []
    for left, right in zip(plan.segments[:-1], plan.segments[1:], strict=True):
        t = right.start / 30
        boundaries.append(
            [
                abs(left.position(t) - right.position(t)),
                abs(left.velocity(t) - right.velocity(t)),
            ]
        )
    max_arm_step = 0.0
    for a, b in zip(samples[:-1], samples[1:], strict=True):
        first, second = dict(a["pose"]["angles"]), dict(b["pose"]["angles"])
        max_arm_step = max(max_arm_step, abs(second["near_forearm"] - first["near_forearm"]))
    limb_errors = []
    for frame in range(90):
        _, _, pose, _, _, _, _, _ = sample(plan, frame / 30)
        joints = SKELETON.evaluate(pose)
        for side in ("near", "far"):
            for parent, child, length in (("thigh", "shin", 42), ("shin", "foot", 45)):
                a, b = joints[f"{side}_{parent}"], joints[f"{side}_{child}"]
                limb_errors.append(abs(math.dist((a.x, a.y), (b.x, b.y)) - length))
    return dict(
        planted_contact_world=max(c["error"] or 0 for a in samples for c in a["contacts"]),
        flat_foot_slide_world=max(slides),
        limb_length_error=max(limb_errors),
        route_boundary_position_and_velocity=boundaries,
        near_forearm_max_radians_per_frame=max_arm_step,
        secondary_abs_max={
            key: max(abs(a["secondary"][key]) for a in samples) for key in samples[0]["secondary"]
        },
    )


def run(output):
    output.mkdir()
    renderer = CairoRenderer()
    proofs = {}
    for world in ("farm", "cold_ridge"):
        for view in ("establishing", "medium"):
            direction = compile_storyboard(rowan_storyboard(world, view)).direction
            proofs[world, view] = direction
            still = cairo_image(renderer, direction_frame(direction, 76))
            still.save(output / f"{world}-{view}.jpg", quality=91, optimize=True)
    farm = proofs["farm", "medium"]
    cold = proofs["cold_ridge", "medium"]
    baseline = compile_storyboard(rowan_storyboard("farm", "medium", legacy=True)).direction
    fear = compile_storyboard(
        rowan_storyboard("cold_ridge", "medium", reaction="frightened")
    ).direction
    sheet(
        output / "mobile.jpg",
        [
            (f"{label} / {beat}", cairo_image(renderer, direction_frame(plan, frame)))
            for label, plan in (("Farm", farm), ("Ridge", cold))
            for frame, beat in ((34, "looking"), (62, "concern"), (76, "startled"))
        ],
        3,
        (360, 640),
    )
    for legacy in (True, False):
        panels = []
        for expression in ("calm", "concerned", "surprised", "frightened"):
            pose = sample_pose(CharacterPreset(action="idle"), 0.4, travel=False)
            cue = None if legacy else FaceCue(expression, expression, 1, 0)
            commands = draw_character(
                pose,
                position=(158, 600),
                scale=2.35,
                expression=expression,
                secondary=SecondaryMotion(gaze=0 if expression == "calm" else 0.92),
                face_cue=cue,
            )
            panels.append((expression, cairo_image(renderer, commands).crop((154, 0, 582, 550))))
        sheet(output / ("faces-before.jpg" if legacy else "faces-after.jpg"), panels, 4, (240, 313))

    panels = []
    for action, expression, frame, time_seconds in (
        ("look_around", "concerned", 62, 0.65),
        ("react", "surprised", 76, 0.35),
    ):
        preset = CharacterPreset(action=action, expression=expression)
        original = draw_character(
            sample_pose(preset, time_seconds, travel=False),
            position=(180, 543),
            scale=1.8,
            expression=expression,
            secondary=preset_secondary(preset, time_seconds),
        )
        plan = farm.blocking
        _, _, pose, _, secondary, _, _, _ = sample(plan, frame / 30)
        updated = draw_character(
            pose,
            position=(180, 543),
            scale=1.8,
            secondary=secondary,
            face_cue=face_cue(frame, 47, 59, "surprised"),
        )
        panels.extend(
            (label, cairo_image(renderer, paths).crop((175, 210, 590, 1110)))
            for label, paths in ((f"Original {action}", original), (f"Refined {action}", updated))
        )
    sheet(output / "acting.jpg", panels, 4, (196, 425))

    panels = []
    for frame, label in ((34, "Looking"), (62, "Concern"), (76, "Surprise"), (89, "Held")):
        _, _, pose, _, secondary, _, _, _ = sample(farm.blocking, frame / 30)
        commands = draw_character(pose, position=(170, 543), scale=1.8, secondary=secondary)
        silhouette = tuple(
            replace(c, fill=color("29374b"), stroke=None) for c in commands if c.fill
        )
        panels.append((label, cairo_image(renderer, silhouette).crop((151, 158, 584, 1118))))
    sheet(output / "silhouette.jpg", panels, 4, (172, 387))

    for plan, name in ((farm, "farm-continuity"), (cold, "ridge-continuity")):
        panels = []
        for frame in (5, 6, 7, 29, 30, 31, 46, 47, 48, 58, 59, 60, 65, 66, 67, 87, 88, 89):
            origin = inspect_frame(plan.blocking, frame)["position"][0]
            zoom = plan.shots[0].zoom[0]
            camera_x = 180 - plan.shots[0].screen[0]
            x = int((180 + (origin - 180) * zoom - camera_x) * 2)
            bottom = 1160 if plan is farm else 1044
            still = cairo_image(renderer, direction_frame(plan, frame))
            panels.append((str(frame), still.crop((x - 134, bottom - 450, x + 134, bottom))))
        sheet(output / f"{name}.jpg", panels, 6, (134, 225))

    contact_frames = (57, 58, 59, 60)
    overlap_frames = (70, 73, 76, 79)
    panels = [
        (
            f"Plant / {frame}",
            cairo_image(renderer, direction_frame(farm, frame)).crop((215, 980, 377, 1150)),
        )
        for frame in contact_frames
    ]
    panels.extend(
        (
            f"Overlap / {frame}",
            cairo_image(renderer, direction_frame(farm, frame)).crop((164, 615, 412, 875)),
        )
        for frame in overlap_frames
    )
    sheet(output / "contact-and-overlap.jpg", panels, 4, (155, 163))

    yellow = compile_storyboard(shot1()).direction
    sheet(
        output / "compatibility.jpg",
        [
            ("Cold Ridge / fear", cairo_image(renderer, direction_frame(fear, 76))),
            ("Yellow Mellow V2 / legacy", cairo_image(renderer, direction_frame(yellow, 46))),
        ],
        2,
        (360, 640),
    )
    results = dict(
        python=platform.python_version(),
        renderer=backend_versions(),
        resolution=SIZE,
        frames=FRAMES,
        legacy=benchmark(renderer, baseline, output),
        refined=benchmark(renderer, farm, output),
        motion={
            world: motion_metrics(plan.blocking)
            for world, plan in (("farm", farm), ("cold_ridge", cold), ("cold_frightened", fear))
        },
    )
    (output / "measurements.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    run(parser.parse_args().output)
