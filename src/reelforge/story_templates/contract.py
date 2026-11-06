"""Validate data selections and compile the selected trusted episode."""

from pathlib import Path

from reelforge.contracts.project import load_project, project_digest
from reelforge.core.errors import InputError, Issue, OperationError
from reelforge.episodes.contract import Episode, compile_episode, inspect_segment

from . import registry

VERSION = "cinematic-template-request-0.1"
FIELDS = ("schema_version", "template_id", "variant", "character", "world")


def request_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": list(FIELDS),
        "additionalProperties": False,
        "properties": {
            **{field: {"type": "string"} for field in FIELDS},
            "schema_version": {"const": VERSION},
        },
        "oneOf": [
            {
                "properties": {
                    "template_id": {"const": template.id},
                    "character": {"const": template.character},
                    "world": {"const": template.world},
                    "variant": {"enum": [edit.id for edit in template.edits]},
                }
            }
            for template in registry.TEMPLATES
        ],
    }


def _reject(code: str, path: str, message: str) -> None:
    raise InputError(Issue(code, path, message))


def resolve(data: object) -> tuple[registry.Template, registry.Edit]:
    if not isinstance(data, dict):
        _reject("REQUEST_TYPE", "", "Expected a JSON object")
    for key in FIELDS:
        if key not in data:
            _reject("REQUEST_REQUIRED", f"/{key}", "Required field is missing")
        if not isinstance(data[key], str):
            _reject("REQUEST_TYPE", f"/{key}", "Expected a string")
    for key in data:
        if key not in FIELDS:
            escaped = key.replace("~", "~0").replace("/", "~1")
            _reject("REQUEST_FIELD", f"/{escaped}", "Unexpected request field")
    if data["schema_version"] != VERSION:
        _reject("REQUEST_VERSION", "/schema_version", f"Use {VERSION}")
    template = next((t for t in registry.TEMPLATES if t.id == data["template_id"]), None)
    if template is None:
        _reject("TEMPLATE_UNKNOWN", "/template_id", "Select a template returned by list")
    for key in ("character", "world"):
        allowed = getattr(template, key)
        if data[key] != allowed:
            _reject("TEMPLATE_INCOMPATIBLE", f"/{key}", f"{template.id} requires {allowed}")
    edit = next((e for e in template.edits if e.id == data["variant"]), None)
    if edit is None:
        choices = ", ".join(e.id for e in template.edits)
        _reject("TEMPLATE_VARIANT", "/variant", f"{template.id} supports {choices}")
    return template, edit


def load_request(path: Path) -> tuple[registry.Template, registry.Edit]:
    return resolve(load_project(path))


def build(template: registry.Template, edit: registry.Edit) -> tuple[dict, Episode]:
    document = edit.builder()
    plan = compile_episode(document)
    actors = [
        segment.direction.blocking.character
        for segment in plan.segments
        if segment.direction.blocking
    ]
    if (
        plan.schema_version != registry.EPISODE_CONTRACT
        or not plan.silent
        or plan.frames != registry.FRAMES
        or actors != [template.character]
    ):
        raise OperationError("TEMPLATE_CONTRACT", "Trusted builder disagrees with template metadata")
    return document, plan


def inspect(template: registry.Template, edit: registry.Edit, document: dict, plan: Episode) -> dict:
    segments = []
    events = []
    cuts = []
    for i, segment in enumerate(plan.segments):
        start = i * 90
        segments.append({"id": segment.id, "start_frame": start, **inspect_segment(segment)})
        cuts.extend(start + shot.start for shot in segment.direction.shots if start + shot.start)
        for node in segment.direction.compiled.scene.nodes:
            if node.visible and (node.asset_id, node.variant) in template.events:
                events.append(
                    {"segment": segment.id, "node": node.id,
                     "asset_id": node.asset_id, "variant": node.variant}
                )
    return {
        **template.discovery(),
        "variant": edit.id,
        "episode_contract": plan.schema_version,
        "duration_frames": plan.frames,
        "seconds": plan.frames / registry.FPS,
        "audio": "silent" if plan.silent else "present",
        "segments": segments,
        "episode_cut_frames": [i * 90 for i in range(1, len(plan.segments))],
        "global_cut_frames": cuts,
        "events": events,
        "manifest_digest": project_digest(document),
        "renderable": True,
        "native_preflight_run": False,
    }
