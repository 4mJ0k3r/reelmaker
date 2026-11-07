"""Generate and render trusted Sprint B world, actor, interaction and film presets."""

import argparse
import json
from dataclasses import replace
from pathlib import Path
import os

from reelforge.contracts.project import load_project
from reelforge.core.transaction import OwnedDirectory

from reelforge.characters.living import ACTIONS, EXPRESSIONS, PROFILES, draw_pose
from reelforge.characters.living_transitions import TRANSITIONS, sample_transition
from reelforge.core.errors import InputError, OperationError
from reelforge.environments.scene import Camera
from reelforge.media.verify import verify_video
from reelforge.productions.workflow import _concat_copy, _verify_pts
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS, compile_interaction, framed_interaction_frame, interaction_camera, sample_interaction,
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



def transition_shot(identity, transition):
    from reelforge.scenes.graph import CharacterFrame, evaluate_layers

    data = world_manifest("village_lane", "evening", actor=identity, frames=90)
    compiled = compile_scene(validate_scene(data))

    def frame(scene, index):
        sample = sample_transition(identity, transition, index)
        node = next(n for n in scene.hierarchy if n.id == "actor")
        center_x = node.world.x + node.world.scale*sample.pose.root.x
        center_y = node.world.y - PROFILES[identity].height*node.world.scale*.48
        camera = Camera(2.05*(center_x-180),2.05*(center_y-400)+10,2.05)
        override = CharacterFrame("actor", node.world, draw_pose(identity,sample.pose,"concerned"))
        return tuple(c for layer in evaluate_layers(scene,index,character_override=override,
                                                    camera_override=camera) for c in layer.commands)

    return compiled, frame


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
        compiled = compile_scene(validate_scene(scene))
        endpoint = spec.frames - 1 if ending else 0
        camera = interaction_camera(plan, endpoint)
        if not ending:
            camera = Camera(camera.x*.64, camera.y*.64, 1+(camera.zoom-1)*.64)

        def bookend_shot(world, frame, *, fixed=camera, closing=ending):
            from reelforge.scenes.graph import evaluate_layers
            from reelforge.characters import living
            from reelforge.scenes.graph import CharacterFrame

            override = None
            if closing:
                node = next(n for n in world.hierarchy if n.id == "actor")
                # Give the viewer a short recognition hold before the reaction.
                time = max(0, (frame-10)/30)
                pose = living.sample_pose(actor, "react", time)
                override = CharacterFrame("actor", node.world, living.draw_pose(actor,pose,"surprised"))
            return tuple(c for layer in evaluate_layers(world,frame,character_override=override,
                                                        camera_override=fixed) for c in layer.commands)
        shots.append((compiled, bookend_shot))

    def close_shot(_scene, frame):
        return framed_interaction_frame(plan, frame)

    return [shots[0], (plan.scene, close_shot), shots[1]]


def read_request(path):
    return load_project(path)


def film_request(data):
    if (not isinstance(data, dict) or set(data) != {"schema_version", "film"}
            or data["schema_version"] != "living-film-0.1"
            or not isinstance(data["film"], str) or data["film"] not in FILMS):
        raise ValueError("Choose a registered living-film-0.1 preset")
    return data["film"]


def render_sequence(shots, output, *, single_scene=False):
    """Verify in an owned subtree, then publish into a reserved output directory."""
    output = output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    output_identity = OwnedDirectory._key(output.lstat())
    published = {}
    complete = False
    reports = []
    owner = None
    output_fd = None
    try:
        output_fd = os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        if OwnedDirectory._key(os.fstat(output_fd)) != output_identity:
            raise ValueError("Reserved film output identity changed")
        scratch_root = Path("/var/tmp")
        if not scratch_root.is_dir() or scratch_root.stat().st_dev != output.parent.stat().st_dev:
            scratch_root = output.parent
        owner = OwnedDirectory(scratch_root, ".reelforge-shots-")
        scratch = owner.path
        with JobMonitor(workspace=scratch) as job_monitor:
            paths = []
            for index, (scene, evaluator) in enumerate(shots):
                shot = scratch / f"shot_{index}"
                report = render_scene(scene, shot, frame_evaluator=evaluator)
                reports.append(report)
                paths.append(shot / "scene.mp4")
                job_monitor.sample()
                if job_monitor.cancelled.is_set():
                    raise ValueError(f"Sequence resource guard failed: {job_monitor.limit_reason}")
            frames = sum(r["frames"] for r in reports)
            joined = scratch / "film.mp4"
            _concat_copy(paths, joined, job_monitor.cancelled)
            verification = verify_video(joined, width=720, height=1280, frames=frames,
                                        cancelled=job_monitor.cancelled)
            timestamps = _verify_pts(joined, frames, job_monitor.cancelled)
            original = [h for report in reports for h in report["verification"]["decoded_rgb_sha256"]]
            if verification["decoded_rgb_sha256"] != original:
                raise ValueError("Stream-copy result changed decoded shot frames")
            job_monitor.sample()
        if job_monitor.cancelled.is_set() or not job_monitor.oom_telemetry_continuous:
            raise ValueError("Sequence resource guard failed")
        report = {"frames": frames, "verification": verification, "timestamps": timestamps,
                  "shots": reports, "assembly_memory": job_monitor.report()}
        video_name, report_name = "film.mp4", "film_report.json"
        if single_scene:
            if len(reports) != 1:
                raise ValueError("A scene publication requires exactly one shot")
            report = {**reports[0], "verification": verification, "timestamps": timestamps,
                      "sequence_memory": job_monitor.report()}
            video_name, report_name = "scene.mp4", "render_report.json"
        (scratch / "film_report.json").write_text(json.dumps(report, indent=2) + "\n")
        if output.is_symlink() or OwnedDirectory._key(output.lstat()) != output_identity:
            raise ValueError("Reserved film output identity changed")
        for source_name, target_name in (("film.mp4", video_name), ("film_report.json", report_name)):
            source = scratch / source_name
            os.link(source, target_name, dst_dir_fd=output_fd)
            published[target_name] = OwnedDirectory._key(source.stat())
        if output.is_symlink() or OwnedDirectory._key(output.lstat()) != output_identity:
            raise ValueError("Reserved film output identity changed during publication")
        owner.cleanup()
        owner.confirm_cleanup()
        complete = True
        return report
    finally:
        try:
            if owner is not None:
                owner.cleanup()
                owner.confirm_cleanup()
        finally:
            # Only remove files this invocation published into its original directory.
            # A replaced path or foreign file is left for its owner.
            try:
                if not complete and output_fd is not None:
                    for name, identity in published.items():
                        try:
                            info = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
                        except FileNotFoundError:
                            continue
                        if OwnedDirectory._key(info) == identity:
                            os.unlink(name, dir_fd=output_fd)
                    if (not output.is_symlink() and output.exists()
                            and OwnedDirectory._key(output.lstat()) == output_identity):
                        try:
                            output.rmdir()
                        except OSError:
                            if not os.listdir(output_fd):
                                raise
            finally:
                if output_fd is not None:
                    os.close(output_fd)


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
    transition = commands.add_parser("transition")
    transition.add_argument("actor", choices=PROFILES)
    transition.add_argument("transition", choices=TRANSITIONS)
    transition.add_argument("--output-dir", type=Path, required=True)
    film_parser = commands.add_parser("film-request")
    film_parser.add_argument("request", type=Path)
    film_parser.add_argument("--output-dir", type=Path, required=True)
    for name, choices in (("actor-reel", PROFILES), ("film", FILMS)):
        command = commands.add_parser(name)
        command.add_argument("identity", choices=choices)
        command.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = dict(worlds=WORLD_KITS, actors=list(PROFILES), actions=ACTIONS,
                          expressions=EXPRESSIONS, interactions={
                              k: vars(v) for k,v in INTERACTIONS.items()}, films=FILMS,
                          transitions=TRANSITIONS)
        elif args.command == "world":
            result = world_manifest(args.kit, args.mood, actor=args.actor,
                                    action=args.action, expression=args.expression)
        elif args.command == "interaction":
            plan = compile_interaction(read_request(args.request))
            report = render_sequence(
                [(plan.scene, lambda _, f: framed_interaction_frame(plan, f))],
                args.output_dir, single_scene=True)
            result = {"frames": report["frames"], "passed": report["verification"]["passed"]}
        elif args.command == "transition":
            scene, evaluator = transition_shot(args.actor, args.transition)
            report = render_sequence([(scene,evaluator)], args.output_dir, single_scene=True)
            result = {"frames": report["frames"], "passed": report["verification"]["passed"]}
        elif args.command == "film-request":
            identity = film_request(read_request(args.request))
            report = render_sequence(film_shots(identity), args.output_dir)
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
