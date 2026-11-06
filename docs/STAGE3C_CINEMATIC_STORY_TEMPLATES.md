# Stage 3C · Cinematic story templates

A template selects one registered cinematic episode. It lets an operator
discover, validate and generate a complete episode without authoring
camera paths, actor movement or effects. It is separate from the MVP
natural-language planner.

| Template ID | Character | World | Default | Alternative |
| --- | --- | --- | --- | --- |
| `other_light` | `yellow_mellow_v2` | `cold_ridge` | `approved` reproduces Stage 3A.1 | `ridge_watch` replaces the opening cuts with a slow wide view and uses a wider ridge reveal |
| `empty_doorway` | `rowan_01` | `farm` | `approved` reproduces Stage 3B | `threshold_hold` starts the closing push sooner and ends tighter on the empty threshold |

Each is a development candidate. All four selections are silent, 9 seconds,
270 frames, 720 × 1280, 30 fps and H.264/yuv420p via the existing renderer.
Each emits a standalone `episode-0.3` manifest. Character, world, event
timing and duration are fixed within each template. Camera edits use the
same admitted directional contract. The original builders and their CLIs
remain available.

## Request

Supply exactly five string fields. The default variant in discovery is a
recommendation. The request must still name a variant explicitly.

```json
{
  "schema_version": "cinematic-template-request-0.1",
  "template_id": "empty_doorway",
  "variant": "threshold_hold",
  "character": "rowan_01",
  "world": "farm"
}
```

The four files in `examples/story_templates/` cover every selection shown
above. The existing project loader bounds requests to 1,048,576 bytes and
32 container levels. It rejects malformed or non-UTF-8 input, duplicate
keys and non-finite numbers. Unlisted fields and character/world pairings
fail explicitly. Requests have no arbitrary paths, camera parameters,
module names, commands or timeline controls.

## Agent quick-start

Run from the repository root with the normal runtime installed and
`PYTHONPATH=src`. All template commands run without Pycairo or FFmpeg.

```bash
export PYTHONPATH=src
mkdir -p outputs/template-demo
python tools/story_templates.py list
python tools/story_templates.py schema
python tools/story_templates.py validate examples/story_templates/other_light_ridge_watch.json
python tools/story_templates.py inspect examples/story_templates/other_light_ridge_watch.json
python tools/story_templates.py generate examples/story_templates/other_light_ridge_watch.json --output outputs/template-demo/story.json
python tools/episode.py render outputs/template-demo/story.json --output-dir outputs/template-demo/render
```

Use a fresh manifest name and an existing output parent. Generation
serializes to a private sibling directory and publishes only a complete
file through an atomic no-clobber link. A successful output is UTF-8 and
deterministically serialized. A request failure exits 2 with an issue
code, message and JSON Pointer. For example, requesting Rowan in
`other_light` returns `TEMPLATE_INCOMPATIBLE` at `/character`.
Output failures exit 1, including `OUTPUT_EXISTS` for an existing file.

`validate` checks selection only. `inspect` and `generate` compile the
episode and return its actual segments, cut frames and registered event
nodes. `renderable: true` means the compiler admitted the episode.
`native_preflight_run: false` indicates that the render host has yet to
be checked. Use the existing episode renderer with a fresh output
directory and inspect its `report.json` for final media and cleanup status.
The existing 256 MiB process-tree budget and 64 MiB admission reserve apply.

## Developer extension

Create a trusted builder that returns a complete episode and add its
`Template` and `Edit` entries to `story_templates/registry.py`. Describe
the fixed character and world, list the supported registered event
variants, supply a default option, and add request, admission and
review evidence. Discovery and request schema derive their combinations
from the registry. Tests exercise a source-owned test template without
changing the CLI or renderer. The request cannot select an import
path or invoke an arbitrary builder.

[Rendered review evidence](visual-evidence/stage3c/README.md) ·
[Engineering report](../Stage3C_Cinematic_Story_Templates_Report.md)
