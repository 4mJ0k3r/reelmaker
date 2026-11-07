#!/usr/bin/env python3
"""Operator entry point for structured cinematic projects."""

import argparse
import json
import signal
import sys
from pathlib import Path
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reelforge.cinematic_projects.contract import capabilities, load_cinematic_project
from reelforge.cinematic_projects.schema import project_schema
from reelforge.core.errors import InputError, OperationError

ROOT = Path(__file__).resolve().parents[1]


class OperatorParser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({"valid": False, "error": {"code": "CINEMATIC_ARGUMENT",
                          "path": "", "message": message}}), file=sys.stderr)
        raise SystemExit(2)


def main():
    parser = OperatorParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "assets/audio")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("schema").add_argument("--version", default="cinematic-project-0.1",
        choices=("cinematic-project-0.1", "cinematic-project-0.2"))
    for name in ("capabilities", "list"):
        commands.add_parser(name)
    for name in ("validate", "plan", "inspect"):
        command = commands.add_parser(name)
        command.add_argument("request", type=Path)
    frame = commands.add_parser("frame")
    frame.add_argument("request", type=Path)
    frame.add_argument("index", type=int)
    frame.add_argument("--png", type=Path)
    render = commands.add_parser("render")
    render.add_argument("request", type=Path)
    render.add_argument("directory", type=Path)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("request", type=Path)
    preflight.add_argument("directory", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("directory", type=Path)
    args = parser.parse_args()
    cancellation = Event()
    if args.command in ("render", "verify", "preflight"):
        signal.signal(signal.SIGTERM, lambda *_: cancellation.set())
        signal.signal(signal.SIGINT, lambda *_: cancellation.set())
    try:
        if args.command == "schema":
            result = project_schema(args.version)
        elif args.command in ("capabilities", "list"):
            result = capabilities(args.registry)
        elif args.command == "preflight":
            from deployment_check import inspect_deployment
            from reelforge.audio.registry import AudioRegistry
            from reelforge.cinematic_projects.operator import output_destination
            from reelforge.core.transaction import OwnedDirectory

            project = load_cinematic_project(args.request, args.registry)
            output = output_destination(args.directory)
            result = inspect_deployment(output.parent)
            if result["ok"] and project.audio:
                owner = OwnedDirectory(output.parent, ".reelforge-preflight-")
                try:
                    AudioRegistry(args.registry).resolve(project.audio, project.frames,
                        cancelled=cancellation, validation_root=owner.path)
                finally:
                    owner.cleanup()
            result.update(plan_sha256=project.timeline()["plan_sha256"], frames=project.frames,
                          output=str(output), advisory=True)
            print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
            return 0 if result["ok"] else 2
        elif args.command == "verify":
            from reelforge.cinematic_projects.workflow import verify_project

            result = verify_project(
                args.directory, registry_root=args.registry, cancelled=cancellation
            )
        elif args.command == "render":
            from reelforge.cinematic_projects.workflow import render_project

            project = load_cinematic_project(args.request, args.registry)
            report = render_project(
                project, args.directory, registry_root=args.registry, cancelled=cancellation
            )
            result = {k: report[k] for k in ("success", "frames", "plan_sha256", "video_sha256")}
            result["output"] = str(args.directory)
        elif args.command == "frame":
            from reelforge.cinematic_projects.sampling import state_at

            project = load_cinematic_project(args.request, args.registry)
            result = state_at(project, args.index)
            if args.png:
                from reelforge.cinematic_projects.workflow import frame_sampler
                from reelforge.rendering.backends.cairo import CairoRenderer
                from reelforge.rendering.diagnostic import color

                renderer = CairoRenderer()
                with renderer.surface(360, 640) as surface:
                    renderer.draw(
                        surface,
                        frame_sampler(project)(args.index),
                        background=color("243e49"),
                        logical_size=(360, 640),
                    )
                    with args.png.open("xb") as handle:
                        surface.write_png(handle)
        else:
            project = load_cinematic_project(args.request, args.registry)
            plan = project.timeline()
            if args.command == "inspect":
                from reelforge.cinematic_projects.direction import composition_audit

                plan = {**plan, "composition_audit": composition_audit(project)}
            result = (
                {"valid": True, "frames": plan["frames"], "plan_sha256": plan["plan_sha256"]}
                if args.command == "validate"
                else plan
            )
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (InputError, OperationError, OSError, KeyboardInterrupt, ImportError) as error:
        result = (
            error.issue.as_dict()
            if isinstance(error, InputError)
            else {"code": getattr(error, "code", "NATIVE_DEPENDENCY" if isinstance(error, ImportError)
                                  else "CINEMATIC_IO"), "path": "", "message": str(error)}
        )
        print(json.dumps({"valid": False, "error": result}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
