# ReelMaker World Asset Sprint

## Scope and provenance

Development branch `asset-a2-a4-world-building-sprint` starts from A1
`4e88b3968c5b05cb3062c736b74bd2035fed9371`, tree
`52cee7d7f619e45c9a365daef3403c4fbf2a9d96`. GitHub read access and
the published A1 head were verified. The sprint has no remote write authorization.
The prior direct push probe lacked terminal credentials. The earlier API preview
transfer limitation is still relevant to the binary gallery files.

Local verification used Ubuntu 24.04, CPython 3.12.3, Pycairo 1.25.1,
Cairo 1.18.0 and FFmpeg 6.1.1. Git history groups the implementation in one
checkpoint and measured evidence in a second checkpoint.

## Inventory and architecture

| Workstream | Asset | Variants |
| --- | --- | --- |
| A2 | road_surface_01 | packed_dirt, worn_asphalt, cobblestone |
| A2 | road_junction_01 | t_junction, crossroads |
| A2 | sidewalk_01 | stone, concrete, cracked |
| A2 | small_bridge_01 | timber, weathered |
| A3 | deciduous_tree_01 | broad, leaning, autumn |
| A3 | shrub_cluster_01 | lush, sparse |
| A3 | rock_group_01 | rounded, angular |
| A4 | streetlamp_01 | unlit, lit, weathered |
| A4 | bench_01 | timber, painted, weathered |
| A4 | crate_stack_01 | neat, uneven |
| A4 | signpost_01 | blank, directional, weathered |
| A7 | ground_mist_01 | thin, dense |

Twelve IDs and 30 variants enter the existing trusted scene asset registry.
The shared world asset table provides the draw callable, bounds, local transform
policy and complexity envelope. It is consumed by the scene registry,
catalog and preview builder. Canvas geometry uses the existing immutable
Cairo command model and bounded cached recipes. Neither the manifest
compiler nor the encoder gained a new execution path.

Variants use material, construction and silhouette differences where useful.
The junction variants are single joined outlines with three or four approaches.
The bridge rails now follow the trail depth so the approach reads as open
on a phone. The deciduous tree's leaning trunk and shifted canopy alter
its silhouette. Crates keep their top box above the lower row.
Mist is static and confined to a low strip. Lamp glow is localized artwork.
Roads and bridges provide decorative geometry with explicit placement and
grant no navigable or collision support. The placement documents under
`docs/ASSET_*.md` cover the per-family conventions.

## A9 gallery and composition

The offline [gallery](docs/asset-gallery/index.html) contains 62 catalog
entries, with preview coverage for all 30 new variants and all six A1
building variants. Historical entries retain explicit context and unavailable
states. Copy selection emits a JSON asset fragment with the active variant.
Both validated showcase manifests are linked from the gallery. Metadata-only
generation runs without Cairo. Relative links assume the extracted tree layout.

Gallery command from the repository root:

```bash
PYTHONPATH=src python tools/asset_gallery.py build
```

The [combined sheet](docs/visual-evidence/asset-sprint-a2-a4/combined-contact-sheet.png)
and family sheets compare isolated recipes. Village Roadside uses Rowan for
scale, a warm shop window as the focal point, and an asphalt plane with an
authored curb. Woodland Crossing uses the farm skyline with a timber bridge,
two distinct crowns, ground props and thin mist. Foreground props sit in front
of the scene action. Both scenes include 720×1280 and 360×640 stills plus
machine-readable placement and layer breakdowns. Local visual review used
the mobile comparison and family sheets. The road end and bridge transitions
are authored per shot. New viewing angles and wider layout variation remain
art-review tasks.

## Motion, determinism and resources

The Woodland Crossing motion proof used the existing scene renderer and
FFmpeg path. The report verified 90 decoded, unique frames at 720×1280,
30 fps, H.264/yuv420p. Separate FFprobe frame timestamps matched
`i / 30` exactly for all 90 frames. A repeated command against the same
output returned `OUTPUT_EXISTS`. The encoder reported clean cleanup, and
zero Cairo surfaces and allocated bytes remained. The evidence ZIP includes
the MP4, while the Git branch contains the source and still evidence.

Scene command tests cover out-of-order sampling and repeats. The gallery
rebuild test compares output byte hashes and verifies stale-preview removal.
The same test checks deterministic per-variant pixel hashes. Historical
manifests and render recipes are outside the source diff.

The gallery build used 36.80 MiB sampled process-tree RSS.
Motion verification used 96.98 MiB,
took 3.12 s wall time and 4.60 s
combined CPU time. The scene peaked at 157 paths and
1028 geometry operations. Both runs retained the 256 MiB
budget and 64 MiB reserve. No resource limit event was reported.
Sampled RSS can miss brief peaks and may count shared pages more than once.

| Asset | Paths | Operations | Preview wall draw ms |
| --- | ---: | ---: | ---: |
| road_surface_01 | 14–29 | 34–64 | 0.39–0.80 |
| road_junction_01 | 6–6 | 28–34 | 0.16–0.26 |
| sidewalk_01 | 7–11 | 23–31 | 0.15–0.29 |
| small_bridge_01 | 24–26 | 100–106 | 0.31–0.33 |
| deciduous_tree_01 | 15–15 | 85–85 | 0.69–0.82 |
| shrub_cluster_01 | 11–13 | 63–78 | 0.28–1.05 |
| rock_group_01 | 10–10 | 60–60 | 0.18–0.25 |
| streetlamp_01 | 8–11 | 42–60 | 0.15–0.36 |
| bench_01 | 10–12 | 49–54 | 0.15–0.64 |
| crate_stack_01 | 22–22 | 93–93 | 0.28–0.62 |
| signpost_01 | 6–8 | 33–41 | 0.14–0.22 |
| ground_mist_01 | 3–3 | 18–18 | 0.40–0.45 |

## Verification results

| Command (repository root, `PYTHONPATH=src`) | Result |
| --- | --- |
| `python -m pytest -q --basetemp outputs/sprint-final-regression` | 237 passed, 0 skipped, 452.32 s |
| `python -m pytest -q --basetemp outputs/sprint-final-focused tests/test_asset_a1_gallery.py tests/test_world_assets.py tests/test_visual_catalog.py` | 35 passed, 0 skipped, 6.50 s |
| `python -m reelforge.catalog validate` | 62 components |
| `python -m reelforge.catalog generate --check` | Passed |
| `python tools/scene.py validate` for each showcase manifest | Both passed |
| `python tools/scene.py render examples/asset-sprint/woodland-crossing.scene.json --output-dir outputs/asset-sprint/motion` | 90 verified frames |
| `node --check` on the gallery script | Passed |

An initial regression run exposed leftover gallery staging directories in
the workspace. The final builder uses same-filesystem staging outside the
browseable gallery. The focused and complete reruns passed after the fix.
The historical environment, Rowan, Yellow Mellow, encoder, A1 gallery and
Stage 3A–3C regression tests all passed. The pinned historical story digests
and barn draw-command hashes are included in those checks.

The browser installer timed out, so fresh interactive desktop and mobile
browser smoke tests and gallery UI screenshots remain outstanding. Automated
tests verified HTML/metadata integrity and native-free generation, and visual
inspection covered the rendered scene evidence. The new branch remains local.
Hosted CI has not run for this sprint.

A2, A3, A4, the A7 starter and the A9 gallery foundation are available for
independent review with the browser verification limitation above. The
showcases are experimental scene proofs. This review package makes no
production readiness claim.
