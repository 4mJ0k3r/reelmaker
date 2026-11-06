"""List, inspect and regenerate the visual inventory from a source checkout."""

import argparse
import json

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .inventory import FAMILIES, ROOT, inventory


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(document, schema, canonical):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(document)
    entries = document["components"]
    index = {entry["id"]: entry for entry in entries}
    if len(index) != len(entries):
        raise ValueError("Duplicate component ID")
    expected = {entry["id"]: entry for entry in canonical["components"]}
    if index.keys() != expected.keys():
        raise ValueError(
            f"Component IDs disagree with runtime: {sorted(index.keys() ^ expected.keys())}"
        )
    for key, entry in index.items():
        for source in entry["sources"]:
            if not (ROOT / source.split(":", 1)[0]).is_file():
                raise ValueError(f"Missing implementation source for {key}: {source}")
        if entry != expected[key]:
            raise ValueError(f"Metadata disagrees with the trusted adapter for {key}")


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def markdown(document):
    lines = [
        "# ReelForge visual catalog",
        "",
        "Generated from trusted runtime declarations. Candidate entries await artistic review.",
        "Selectable environments can be requested by keyword. Preset-only components appear in",
        "trusted shots and have no independent prompt selector.",
        "",
        "| ID | Name | Family | Type | Registration | Planner | Readiness | Variants | Sources |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in document["components"]:
        fields = [
            f"`{entry['id']}`",
            entry["name"],
            entry["family"],
            entry["type"],
            ", ".join(entry["registration"]) or "—",
            entry["planner_exposure"],
            entry["production_status"],
            ", ".join(entry["variants"]) or "—",
            "<br>".join(
                f"[{source.split(':')[1]}](../{source.split(':')[0]})"
                for source in entry["sources"]
            ),
        ]
        lines.append("| " + " | ".join(fields) + " |")
    return "\n".join(lines) + "\n"


def generate(document, directory, *, check):
    files = {"components.json": json_text(document), "components.md": markdown(document)}
    for name, content in files.items():
        path = directory / name
        data = content.encode("utf-8")
        if check:
            if not path.is_file() or path.read_bytes() != data:
                raise ValueError(f"Stale catalog output: {name}. Run catalog generate.")
        else:
            path.write_bytes(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list").add_argument("--family", choices=FAMILIES)
    commands.add_parser("show").add_argument("id")
    commands.add_parser("validate")
    commands.add_parser("generate").add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    directory = ROOT / "catalog"
    try:
        document = inventory()
        schema = read_json(directory / "schema.json")
        validate(document, schema, document)
        if args.command == "list":
            for entry in document["components"]:
                if args.family is None or entry["family"] == args.family:
                    print(
                        "\t".join(
                            entry[key]
                            for key in (
                                "id",
                                "type",
                                "family",
                                "production_status",
                                "planner_exposure",
                            )
                        )
                    )
        elif args.command == "show":
            for entry in document["components"]:
                if entry["id"] == args.id:
                    print(json_text(entry), end="")
                    break
            else:
                raise ValueError(f"Unknown component ID: {args.id}")
        elif args.command == "validate":
            validate(read_json(directory / "components.json"), schema, document)
            print(f"Validated {len(document['components'])} components")
        else:
            generate(document, directory, check=args.check)
    except (OSError, ValueError, SchemaError, ValidationError) as error:
        parser.exit(2, f"catalog: {getattr(error, 'message', str(error))}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
