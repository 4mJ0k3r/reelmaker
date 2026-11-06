# Stage 3C · Validated cinematic story templates

## Baseline and pre-implementation audit

The checkout starts at published Stage 3B commit
`b396e3cdb049f1524eced5bdbc679a2149f87d3f` on
`stage3c-validated-story-templates`.

`cinematic_story` accepts `the_other_light` and
`the_other_light_refined`. Both pair Yellow Mellow V2 with Cold Ridge.
The original begins with an object insert. The refined version introduces
the traveler immediately and uses the registered beacon surge and delayed
ridge reveal. `cinematic_farm_story` accepts `the_empty_doorway` for Rowan
on Dusk Farm. It holds a wide opening, inserts the moving doorway shadow,
cuts to the reaction, and returns to the doorway. The historical farm
manifest digest measured before edits is
`d3f67b2b8512c3d61390c427e26bebae18654580445e7554fc34e2fd8533687c`.

The Stage 2C staging helper admits more actor/world pairs than either
complete story, so it cannot serve as the compatibility matrix.
The existing recipe CLIs export complete JSON. `tools/episode.py` validates
and renders it, with `episode-0.3` accepting registered direction or
storyboard segments. It bounds episodes to ten 90-frame segments. A
direction allows at most six shots per segment and validates pan, zoom,
cut ratios, framing and motion. Template edits should reuse these checks.

The existing project loader bounds JSON at 1,048,576 bytes and 32 container
levels, rejects invalid UTF-8, duplicate keys and non-finite numbers, and
never follows asset paths. Existing CLI errors use JSON Pointer issues and
nonzero status. The encoder owns transactions and monitors the 256 MiB
process-tree budget and 64 MiB admission reserve. The visual catalog lists
48 registered components and their evidence. The MVP prompt planner has a
separate vocabulary. Neither is the right place to add story IDs.

The proposed layer is a source-owned registry and a strict selection
contract. It wraps the two existing builders, applies only fixed camera
edits, recompiles the result, and delegates rendering to the current
episode CLI. A plugin system, arbitrary timing controls and a second
render pipeline would duplicate existing trust and admission boundaries.

## Registry and request contract

| Template | Character | World | Recommended | Alternate |
| --- | --- | --- | --- | --- |
| `other_light` | `yellow_mellow_v2` | `cold_ridge` | `approved` | `ridge_watch` |
| `empty_doorway` | `rowan_01` | `farm` | `approved` | `threshold_hold` |

The new `story_templates/registry.py` owns the callable references,
descriptions, event pairs and allowed edits. `contract.py` builds the schema
from those entries and implements selection diagnostics and episode admission.
The code keeps builder references out of JSON. Templates are marked
`candidate`, with `production_ready: false`. There are no catalog additions.

`cinematic-template-request-0.1` takes exactly `schema_version`,
`template_id`, `variant`, `character` and `world`, all strings. Its
schema uses an exclusive branch per template, including that template's
character, world and variant enum. Semantic validation uses those same
records for acceptance and field-level errors. Missing fields get
`REQUEST_REQUIRED`, extra fields get `REQUEST_FIELD`, and cross-story
pairings get `TEMPLATE_INCOMPATIBLE`, with the failing JSON Pointer.
Malformed, oversized, deeply nested, duplicate-key and non-finite
inputs fail in the existing bounded loader before dispatch.

## CLI and file publication

`tools/story_templates.py` exposes `list`, `schema`, `validate`,
`inspect`, and `generate REQUEST --output PATH`. The four checked
examples under `examples/story_templates/` exercise both options of
each story. `validate` checks the selection. `inspect` and `generate`
compile the episode and report actual segment IDs, global cuts and
registered event nodes. For example, the farm alternative reports
`global_cut_frames: [90,112,121,152,180]` and
`barn_01:doorway_shadow` in the movement segment.
`renderable: true` is compiler admission and is paired with
`native_preflight_run: false`.

Generation serializes the complete JSON, writes and fsyncs it inside a
private sibling directory, then publishes it using the existing
hard-link no-clobber pattern. Invalid input exits 2 with a structured
issue. I/O failures exit 1, including `OUTPUT_EXISTS` for existing
targets. The tests simulate a failed link and confirm that no manifest
or staging directory remains. Output paths are CLI arguments. No file
path or executable value is read from the request.

## Compatibility

| Historical manifest | Canonical SHA-256 |
| --- | --- |
| Original Other Light | `8d276d403f48f9768a19bca2f902e7a26afaf4984933d906ff76a50bad4b0cbd` |
| Refined Other Light and approved template | `7e2d4ff954eac140589d4a182459a2e3550afffe8e70284e08e131faea504f1d` |
| Empty Doorway and approved template | `d3f67b2b8512c3d61390c427e26bebae18654580445e7554fc34e2fd8533687c` |

Both approved template manifests match their historical recipes. The
alternatives preserve all three scene bases exactly and retain the
entire middle direction segment. Actor overrides matched at all 90
middle frames per film, including poses, world placement and shadows.
Because the blocking and registered event scenes are identical, timing,
facing, support and visual-effect recipes are preserved. Legacy episode,
direction, storyboard and audio implementation files are untouched.

## Editorial alternatives

**Ridge Watch.** The opening uses one slow wide move and matches the
middle segment at the handoff. The original internal opening cut is
removed. The ending shows more snow and mountain geography around both
lights. It still holds a dark ridge before the reveal. The wider
opening makes Yellow Mellow smaller at phone size, and the stationary
opening reads more deliberately than the approved close opening.
The surge, reaction and payoff remain readable in decoded frames.
[Mobile comparison](docs/visual-evidence/stage3c/other-light-mobile.jpg) ·
[Storyboard](docs/visual-evidence/stage3c/other-light-storyboard.jpg)

**Threshold Hold.** The closing camera begins on the same doorway
composition as the shadow insert, then starts moving sooner and pushes
to 3.12× instead of 2.60×. The surrounding barn takes up more of the
screen, while the empty threshold remains legible. The side wall is
more tightly cropped. The shadow at frame 135 and the return at 180
matched the approved decode at mobile size.
[Mobile comparison](docs/visual-evidence/stage3c/empty-doorway-mobile.jpg) ·
[Storyboard](docs/visual-evidence/stage3c/empty-doorway-storyboard.jpg)

Both camera plans pass the existing admission limits. The comparisons
use decoded 360 × 640 frames from the approved and alternate MP4s.
Headless playback ran at the films' normal clock, and the artistic
review used decoded frames. Direct visual assessment at normal speed
remains an independent review item.

## Verification and measurements

The native-free suite ran with Pycairo unavailable and passed **64 tests
with 1 skip**. The skipped historical test requires Cairo. The command
from the repository root was:

```bash
python -m pytest -q tests/test_stage3c_story_templates.py tests/test_stage3b_farm_story.py tests/test_stage3a1_editorial_polish.py tests/test_stage3a_cinematic_story.py tests/test_visual_catalog.py tests/test_production.py::test_episode_contracts_unchanged --basetemp outputs/stage3c/pytest
```

All five template commands ran in that native-free environment. The
test suite also blocks process launching for the native-free CLI path.
All four configurations compiled, and repeated generation matched
manifest bytes. Approved digest parity and actual discovery, schema,
command timings and generation sizes are recorded in
[native-free evidence](docs/visual-evidence/stage3c/native-free.json).
Catalog validation still reports 48 components and the generated
catalog check passes.

Each full alternate went through `tools/episode.py render` with exit 0,
published and verified locally, and cleaned its owned transaction.
Both fully decoded to 270 frames, 9.000 seconds, 720 × 1280,
H.264/yuv420p, exact 30 fps timestamps, zero audio streams and no black
frames. No-clobber retries returned `OUTPUT_EXISTS` and preserved the
MP4 checksums. Selected Cairo pixels reproduced their source hashes.
Held frames can share hashes. [Render verification](docs/visual-evidence/stage3c/verification.json)

| Metric | Ridge Watch | Threshold Hold |
| --- | ---: | ---: |
| Generated manifest size | 33,462 B | 30,620 B |
| Render and encode | 7.96 s | 10.43 s |
| Monitored wall time | 16.06 s | 19.08 s |
| Peak process-tree RSS | 102.48 MiB | 99.75 MiB |
| Mean sampled geometry | 15.97 ms | 10.71 ms |
| Mean sampled rasterization | 13.81 ms | 32.99 ms |
| Maximum paths / operations | 324 / 1,801 | 365 / 2,133 |
| Peak sampled logical staging | 3,298,440 B | 3,643,514 B |

Measurements used Ubuntu 24.04.3, AMD EPYC 9V74 with an eight-vCPU
quota, Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0 and FFmpeg 6.1.1.
The monitored 256 MiB budget and 64 MiB reserve remained in place.
The target four-vCPU low-memory VM remains untested. The one-off
geometry and raster samples describe this host and are not benchmarks.

## Extension and review readiness

A future developer adds a trusted builder, its explicit registry
metadata and tests. A test-only registered definition uses the same
schema, dispatch and compiler without editing CLI logic or rendering.
The stage supports only the four documented selections.

This is ready for independent engineering and artistic review. Source,
examples, CLI, generated evidence and tests are committed locally.
GitHub publication and hosted CI are pending Stage 3C authorization.
The prior GitHub authorization applied to Stage 3B.
