"""Discover and generate complete episodes from trusted story selections."""

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from reelforge.core.errors import InputError, OperationError
from reelforge.story_templates import contract, registry


def publish(document: dict, output: Path) -> None:
    payload = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n"
    try:
        with TemporaryDirectory(prefix=".story-template-", dir=output.parent) as directory:
            pending = Path(directory) / "manifest.json"
            with pending.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(pending, output)
    except FileExistsError as error:
        raise OperationError("OUTPUT_EXISTS", "Choose a fresh manifest path") from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "schema"):
        commands.add_parser(name)
    for name in ("validate", "inspect", "generate"):
        command = commands.add_parser(name)
        command.add_argument("request", type=Path)
        if name == "generate":
            command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            result = {
                "request_contract": contract.VERSION,
                "templates": [t.discovery() for t in registry.TEMPLATES],
            }
        elif args.command == "schema":
            result = contract.request_schema()
        else:
            template, edit = contract.load_request(args.request)
            result = {"valid": True, "template_id": template.id, "variant": edit.id}
            if args.command != "validate":
                document, plan = contract.build(template, edit)
                result.update(contract.inspect(template, edit, document, plan))
                if args.command == "generate":
                    publish(document, args.output)
                    result["manifest"] = str(args.output)
    except InputError as error:
        print(json.dumps({"ok": False, "issue": error.issue.as_dict()}))
        return 2
    except (OSError, OperationError, ValueError) as error:
        print(json.dumps({"ok": False, "error": {
            "code": getattr(error, "code", "TEMPLATE_RUNTIME"), "message": str(error),
        }}))
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
