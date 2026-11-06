"""Generate and render trusted Sprint B world, actor, interaction and film presets."""

import argparse
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from reelforge.characters.living import ACTIONS, EXPRESSIONS, PROFILES
from reelforge.core.errors import InputError, OperationError
from reelforge.environments.scene import Camera
from reelforge.media.verify import verify_video
from reelforge.productions.workflow import _concat_copy, _verify_pts
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS, compile_interaction, interaction_frame, sample_interaction,
)
from reelforge.visual_library.composition.living_worlds import WORLD_KITS, node, world_manifest

from tools.scene import render_scene


FILMS = {
    "the_forgotten_parcel": ("pickup_carry_place", "scout_01", "wrapped"),
    "the_creek_crossing": ("push_cart", "mechanic_01", "loaded"),
}


def interaction_request(identity, actor, variant):
    return {"schema_version": "interaction-0.1", "interaction": identity,
            "actor": actor, "prop": INTERACTIONS[identity].prop, "variant": variant}


def actor_shot(identity, action, expression, frames=45):
    data = world_manifest("village_lane", "evening", actor=identity, action=action,
                          expression=expression, frames=frames)
    scene = compile_scene(validate_scene(data))

    def frame(plan, index):
        from reelforge.scenes.graph import evaluate_layers
        camera = Camera(-38 if action not in ("walk", "run") else -9, 88, 1.47)
        return tuple(c for layer in evaluate_layers(plan, index, camera_override=camera)
                     for c in layer.commands)

    return scene, frame


def film_shots(identity):
    key, actor, variant = FILMS[identity]
    plan = compile_interaction(interaction_request(key, actor, variant))
    spec = INTERACTIONS[key]
    bookend = (270 - spec.frames) // 2
    shots = []
    for ending in (False, True):
        mood = ("rainy_night" if key == "pickup_carry_place" else "misty") if ending else spec.mood
        scene = world_manifest(spec.kit, mood, actor=actor, action="react" if ending else "notice",
                               expression="surprised" if ending else "concerned", frames=bookend)
        actor_node = next(n for n in scene["nodes"] if n["id"] == "actor")
        anchor = next(n.world for n in plan.scene.hierarchy if n.id == "actor")
        sample = sample_interaction(plan, spec.frames - 1 if ending else 0)
        actor_node["transform"].update(x=anchor.x + anchor.scale*sample.travel, y=anchor.y)
        scene["nodes"].append(node("story_prop","midground",10,spec.prop,variant,
                                   *anchor.point(*sample.prop),anchor.scale))
        if ending and key == "push_cart":
            scene["nodes"].append(node("creek_wisp","midground",7,"smoke_wisp_01","rising",198,533,.9))
        scene["camera"] = "approach" if ending else "gentle_drift"
        shots.append((compile_scene(validate_scene(scene)), None))

    def close_shot(_scene, frame):
        u = frame / (spec.frames - 1)
        return interaction_frame(plan, frame, camera_override=Camera(-26+45*u, 129, 1.55))

    return [shots[0], (plan.scene, close_shot), shots[1]]


def read_request(path):
    with path.open("rb") as source:
        encoded = source.read(4097)
    if len(encoded) > 4096:
        raise ValueError("Preset request exceeds 4096 bytes")
    return json.loads(encoded)


def render_sequence(shots, output):
    """Reuse the scene renderer per shot, then the production stream-copy join."""
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    reports = []
    final = output / "film.mp4"
    # Keep multi-shot intermediates out of the review output. A same-device
    # staging path permits a final rename after full decode verification.
    scratch_root = Path("/var/tmp")
    if not scratch_root.is_dir() or scratch_root.stat().st_dev != output.stat().st_dev:
        scratch_root = output.parent
    with TemporaryDirectory(prefix=".reelforge-shots-", dir=scratch_root) as temporary:
        scratch = Path(temporary)
        paths = []
        for index, (scene, evaluator) in enumerate(shots):
            shot = scratch / f"shot_{index}"
            report = render_scene(scene, shot, frame_evaluator=evaluator)
            reports.append(report)
            paths.append(shot / "scene.mp4")
        frames = sum(r["frames"] for r in reports)
        with JobMonitor(workspace=scratch) as monitor:
            joined = scratch / "film.mp4"
            _concat_copy(paths, joined, monitor.cancelled)
            verification = verify_video(joined, width=720, height=1280, frames=frames,
                                        cancelled=monitor.cancelled)
            timestamps = _verify_pts(joined, frames, monitor.cancelled)
            original = [h for report in reports for h in report["verification"]["decoded_rgb_sha256"]]
            if verification["decoded_rgb_sha256"] != original:
                raise ValueError("Stream-copy result changed decoded shot frames")
        if monitor.cancelled.is_set() or not monitor.oom_telemetry_continuous:
            raise ValueError("Assembly resource guard failed")
        if final.exists() or final.is_symlink():
            raise ValueError("Film output already exists")
        joined.rename(final)
    report = {"frames": frames, "verification": verification, "timestamps": timestamps,
              "shots": reports, "assembly_memory": monitor.report()}
    (output / "film_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    world = commands.add_parser("world")
    world.add_argument("kit", choices=WORLD_KITS)
    world.add_argument("mood")
    world.add_argument("--actor", choices=(*PROFILES, "rowan_01"))
    world.add_argument("--action", choices=ACTIONS, default="idle")
    world.add_argument("--expression", choices=EXPRESSIONS, default="neutral")
    interaction = commands.add_parser("interaction")
    interaction.add_argument("request", type=Path)
    interaction.add_argument("--output-dir", type=Path, required=True)
    film_request = commands.add_parser("film-request")
    film_request.add_argument("request", type=Path)
    film_request.add_argument("--output-dir", type=Path, required=True)
    for name, choices in (("actor-reel", PROFILES), ("film", FILMS)):
        command = commands.add_parser(name)
        command.add_argument("identity", choices=choices)
        command.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = dict(worlds=WORLD_KITS, actors=list(PROFILES), actions=ACTIONS,
                          expressions=EXPRESSIONS, interactions={
                              k: vars(v) for k,v in INTERACTIONS.items()}, films=FILMS)
        elif args.command == "world":
            result = world_manifest(args.kit, args.mood, actor=args.actor,
                                    action=args.action, expression=args.expression)
        elif args.command == "interaction":
            plan = compile_interaction(read_request(args.request))
            report = render_scene(plan.scene, args.output_dir,
                                  frame_evaluator=lambda _, f: interaction_frame(plan, f))
            result = {"frames": report["frames"], "passed": report["verification"]["passed"]}
        elif args.command == "film-request":
            data = read_request(args.request)
            if (not isinstance(data, dict) or set(data) != {"schema_version", "film"}
                    or data["schema_version"] != "living-film-0.1"
                    or not isinstance(data["film"], str) or data["film"] not in FILMS):
                raise ValueError("Choose a registered living-film-0.1 preset")
            report = render_sequence(film_shots(data["film"]), args.output_dir)
            result = {"frames": report["frames"], "passed": report["verification"]["passed"]}
        else:
            shots = film_shots(args.identity) if args.command == "film" else [
                actor_shot(args.identity, action, expression)
                for action, expression in zip(ACTIONS, ("neutral","determined","concerned","happy","surprised"), strict=True)
            ]
            report = render_sequence(shots, args.output_dir)
            result = {"frames": report["frames"], "passed": report["verification"]["passed"]}
    except (ValueError, InputError, OperationError, OSError) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
