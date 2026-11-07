#!/usr/bin/env python3
"""Operator entry point for structured cinematic projects."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reelforge.cinematic_projects.contract import capabilities, load_cinematic_project
from reelforge.cinematic_projects.schema import project_schema
from reelforge.core.errors import InputError, OperationError

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "assets/audio")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("schema", "capabilities", "list"):
        commands.add_parser(name)
    for name in ("validate", "plan", "inspect"):
        command = commands.add_parser(name)
        command.add_argument("request", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "schema":
            result = project_schema()
        elif args.command in ("capabilities", "list"):
            result = capabilities(args.registry)
        else:
            plan = load_cinematic_project(args.request, args.registry).timeline()
            result = ({"valid": True, "frames": plan["frames"], "plan_sha256": plan["plan_sha256"]}
                      if args.command == "validate" else plan)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (InputError, OperationError, OSError, KeyboardInterrupt) as error:
        result = (error.issue.as_dict() if isinstance(error, InputError)
                  else {"code": getattr(error, "code", "CINEMATIC_IO"), "message": str(error)})
        print(json.dumps({"valid": False, "error": result}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
