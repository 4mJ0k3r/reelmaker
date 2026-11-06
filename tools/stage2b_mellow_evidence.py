"""Sample the Stage 2B actor and compare the same scene, framing and route on CPU Cairo."""

import argparse
import json
import platform
from dataclasses import asdict, replace
from pathlib import Path

from stage2a_character_evidence import FRAMES, SIZE, benchmark, cairo_image, sheet

from reelforge.blocking.sampling import _yellow_mellow_drawer, segment_at
from reelforge.characters.yellow_mellow_v2 import Stage, YellowMellowV2
from reelforge.characters.yellow_mellow_v2.artwork import character_commands
from reelforge.characters.yellow_mellow_v2.character import PRIMARY_CACHE
from reelforge.characters.yellow_mellow_v2.expressions import expression
from reelforge.characters.yellow_mellow_v2.investigation import FACES
from reelforge.characters.yellow_mellow_v2.quality import analyse
from reelforge.characters.yellow_mellow_v2.rig import evaluate
from reelforge.direction.sampling import camera_at, direction_frame
from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
from reelforge.rendering.diagnostic import color
from reelforge.storyboards.compiler import compile_storyboard
from reelforge.visual_library.composition.mellow_approach import mellow_storyboard

BEATS = ((58, "Notice"), (67, "Investigate"), (78, "Surprise"), (89, "Recover"))
SECTIONS = (
    (0, 39, "walk"),
    (40, 53, "brake"),
    (54, 62, "notice"),
    (63, 68, "investigate"),
    (69, 78, "surprise"),
    (79, 89, "recover"),
)


def frame_crop(plan, frame, renderer, offsets):
    p = plan.blocking
    x = segment_at(p, frame / 30).position(frame / 30)
    transform = camera_at(plan, frame).transform(1)
    origin = int(2 * (transform.tx + transform.sx * x))
    floor = int(2 * (transform.ty + transform.sy * p.y))
    left, top, right, bottom = offsets
    return cairo_image(renderer, direction_frame(plan, frame)).crop(
        (origin + left, floor + top, origin + right, floor + bottom)
    )


def motion_metrics(plan):
    drawer = _yellow_mellow_drawer(plan)
    performance = drawer._perf
    metrics = analyse(performance, sections=SECTIONS)
    metrics["units"] = "canonical V2 rig units; proof world scale = 0.4266667 logical px/unit"
    samples = [drawer.sample(frame) for frame in range(90)]
    secondary = [asdict(cf.state.secondary) for cf in samples]
    route_start = plan.segments[0].x0
    route = [segment_at(plan, frame / 30).position(frame / 30) for frame in range(90)]
    scale = plan.scale * drawer.draw_scale
    contacts = []
    planted_steps = []
    for frame, cf in enumerate(samples):
        state = cf.state
        # Resolve the displayed planted pivot using the real drawer origin and actor placement.
        contacts.append(
            [
                route[frame]
                + plan.scale * drawer.local_origin(cf)
                + scale * state.world(state.legs[side].ankle)[0]
                - scale * state.pose.pelvis_x
                for side in ("near", "far")
            ]
        )
        if frame:
            for index, side in enumerate(("near", "far")):
                before, after = samples[frame - 1].state.pose.foot(side), state.pose.foot(side)
                if before.lift == after.lift == before.pitch == after.pitch == 0:
                    planted_steps.append(abs(contacts[frame][index] - contacts[frame - 1][index]))
    return {
        **metrics,
        "root_world_travel": route[-1] - route_start,
        "max_flat_step_in_rendered_world": max(planted_steps),
        "boundary_position_and_speed": [
            [
                abs(a.position(b.start / 30) - b.position(b.start / 30)),
                abs(a.velocity(b.start / 30) - b.velocity(b.start / 30)),
            ]
            for a, b in zip(plan.segments[:-1], plan.segments[1:], strict=True)
        ],
        "secondary_abs_max": {k: max(abs(row[k]) for row in secondary) for k in secondary[0]},
        "face_at_beats": {
            str(frame): asdict(samples[frame].face) for frame in (54, 61, 68, 73, 85, 89)
        },
        "blink_nonzero_frames": [cf.frame for cf in samples if cf.blink > 0],
        "cache_after_sampling": len(performance._cache),
        "cache_capacity": PRIMARY_CACHE,
    }


def build(output):
    output.mkdir()
    renderer = CairoRenderer()
    plans = {}
    for world in ("farm", "cold_ridge"):
        for view in ("establishing", "medium"):
            plan = compile_storyboard(mellow_storyboard(world, view)).direction
            plans[world, view] = plan
            still = cairo_image(renderer, direction_frame(plan, 78))
            still.save(output / f"{world.replace('_', '-')}-{view}.jpg", quality=91, optimize=True)
    farm = plans["farm", "medium"]
    ridge = plans["cold_ridge", "medium"]
    legacy = compile_storyboard(mellow_storyboard("cold_ridge", "medium", legacy=True)).direction

    for refined in (False, True):
        stage = Stage(180, 505, 2.05)
        state = evaluate(YellowMellowV2(facing=0.92).start_pose)
        panels = []
        for label in FACES:
            face = (
                FACES[label] if refined else expression("neutral" if label == "settled" else label)
            )
            commands = character_commands(state, face, draw_placement(stage, 1))
            still = cairo_image(renderer, commands).crop((225, 405, 520, 740))
            panels.append((label, still))
        sheet(
            output / ("faces-after.jpg" if refined else "faces-before.jpg"), panels, 5, (157, 178)
        )

    sheet(
        output / "acting.jpg",
        [
            (f"{prefix} / {label}", frame_crop(plan, frame, renderer, (-112, -243, 128, 27)))
            for prefix, plan in (("Legacy", legacy), ("Refined", ridge))
            for frame, label in BEATS
        ],
        4,
        (182, 205),
    )
    sheet(
        output / "mobile.jpg",
        [
            (f"{name} / {label}", cairo_image(renderer, direction_frame(plan, frame)))
            for name, plan in (("Farm", farm), ("Ridge", ridge))
            for frame, label in BEATS[1:]
        ],
        3,
        (360, 640),
    )
    sheet(
        output / "continuity.jpg",
        [
            (str(frame), frame_crop(ridge, frame, renderer, (-112, -239, 128, 27)))
            for frame in (17, 18, 19, 39, 40, 41, 53, 54, 55, 69, 70, 71, 84, 85, 86)
        ],
        3,
        (138, 153),
    )
    sheet(
        output / "contacts.jpg",
        [
            (f"Frame {frame}", frame_crop(ridge, frame, renderer, (-56, -80, 63, 32)))
            for frame in (47, 48, 49, 52, 53, 54, 88, 89)
        ],
        4,
        (140, 132),
    )
    drawer = _yellow_mellow_drawer(ridge.blocking)
    stage = Stage(180, 520, 1.75)
    panels = []
    for frame, label in BEATS:
        current = drawer.sample(frame)
        geometry = character_commands(current.state, current.face, draw_placement(stage, 1))
        ink = color("29374b")
        solid = tuple(
            replace(
                c,
                fill=ink if c.fill else None,
                stroke=replace(c.stroke, paint=ink) if c.stroke else None,
            )
            for c in geometry
        )
        panels.append((label, cairo_image(renderer, solid).crop((170, 487, 579, 1070))))
    sheet(output / "silhouette.jpg", panels, 4, (176, 252))

    result = dict(
        python=platform.python_version(),
        renderer=backend_versions(),
        resolution=SIZE,
        frames=FRAMES,
        legacy=benchmark(renderer, legacy, output),
        refined=benchmark(renderer, ridge, output),
        motion={
            name: motion_metrics(plan.blocking)
            for name, plan in (
                ("legacy_ridge", legacy),
                ("refined_ridge", ridge),
                ("refined_farm", farm),
            )
        },
    )
    (output / "measurements.json").write_text(json.dumps(result, indent=2) + "\n")


def draw_placement(stage, sign):
    from reelforge.characters.yellow_mellow_v2.artwork import Placement

    return Placement(stage.x, stage.ground_y, stage.scale, sign)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
