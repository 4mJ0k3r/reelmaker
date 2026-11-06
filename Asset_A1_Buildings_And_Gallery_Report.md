# Asset A1 Buildings and Gallery Engineering Report

## Restoration

Restored the original commit from the handoff bundle after cloning the GitHub repository containing the approved baseline. Bundle verification passed and the working tree was clean.

| Item | Git identity |
| --- | --- |
| Approved baseline and restored commit parent | `d49dff105a60e6a2ed857ec756f0423eb2d9360f` |
| Development branch | `asset-a1-buildings-gallery` |
| Restored implementation | `d4d3a3c170648c069f848f2a8aa44d7b4f808500` |
| Restored tree | `15ecd4a64b24c7a2ce4aa66b725509e91e4ea53b` |

The accompanying Git identity file records the report commit, parent and tree after commit creation.

## Implementation

| ID | Variants | Drawing complexity |
| --- | --- | --- |
| `house_01` | `daylight`, `dusk`, `weathered` | 59–64 paths, 248–274 operations |
| `shop_01` | `open`, `closed`, `weathered` | 41–43 paths, 207–218 operations |

Trusted procedural architecture recipes feed scene registration, the catalog and the gallery. Both assets use a foundation-line ground origin, fixed three-quarter projection, uniform positive scale from 0.25 to 2 and zero composed rotation. Variant lighting, facade state and contact shadows are static. Doorway points provide placement references. Existing stories retain their authored asset selections. See [placement contracts](docs/ASSET_A1_BUILDINGS.md) and [example scenes](examples/asset-a1).

The [offline gallery](docs/asset-gallery/index.html) derives its 50 entries from the authoritative catalog. It provides search, category filtering, variant selection, image enlargement, ID copying with a manual fallback, and distinct unavailable-preview and independent-review states. Historical context images are labeled. Metadata-only generation works without Cairo.

```bash
PYTHONPATH=src python tools/asset_gallery.py build --output-dir docs/asset-gallery
```

## Visual evidence

The bundled preview directory includes six standalone PNGs and two variant contact sheets. The two Dusk Farm compositions each include a 720×1280 frame and a 360×640 mobile frame with Rowan as a scale reference. Visual inspection found the house glazing and shop canopy/shutter read distinctly by variant. The integrated foundations meet the path and ground shadow, and both silhouettes read at mobile size. Fine weathering details are clearest in the standalone sheets. Fixed perspective and lighting have visual coverage in Dusk Farm only.

The prior handoff records Chromium checks of search, filter, variant switching, enlargement, clipboard and fallback, unavailable states, mobile layout and zero HTTP requests. Its desktop and mobile captures are in `docs/visual-evidence/asset-a1/`. This session inspected the rendered images and reran gallery generation and automated metadata/reference tests. Interactive browser checks remain prior-session evidence.

## GitHub and review status

Read access confirmed via clone and the baseline was found on `origin/stage3c-validated-story-templates`. GitHub reports pull, push and admin permission. A prior authorized connector test published an empty commit on a separate branch. Direct CLI push credentials previously failed. This A1 turn used read-only GitHub operations. Hosted A1 CI did not run. Independent artistic and engineering review is pending. The environment used here has more headroom than the low-RAM target VM, so measured process-tree RSS should be interpreted alongside the unchanged software limits.

## Local verification

| Scope | Result |
| --- | --- |
| A1 assets and gallery, catalog, snowy mountain, Stages 1A–3C, encoder cleanup | 188 passed in 215.92 s |
| MVP planner and production compatibility | 34 passed in 263.57 s |
| Catalog validation and generated catalog drift check | 50 components, no drift |
| Full native gallery rebuild | Byte-identical HTML, metadata and preview directory |

Ran on Ubuntu 24.04, Python 3.12.3, system Pycairo 1.25.1, Cairo 1.18.0 and FFmpeg. Test output is in the review archive. Tests cover bounded and deterministic geometry, transforms and grounding, gallery metadata and safe escaping, valid image references and dimensions, deterministic regeneration and stale preview cleanup, historical assets and story digests, native episode publication and encoder cleanup. The native directed episode verified exact video timestamps, 90 decoded frames, zero audio streams, preservation of an existing output on retry and removal of the transaction directory. All tests ran without skips. No implementation corrections were required.

## Performance

| Measurement | House | Shop |
| --- | ---: | ---: |
| Standalone wall draw time across three variants | 1.85–3.38 ms | 0.97–1.90 ms |
| Integrated mean wall time per frame, 12 samples each | 25.44 ms | 26.51 ms |
| Integrated mean CPU time per frame | 27.40 ms | 28.32 ms |
| Integrated draw paths / geometry operations | 231 / 1733 | 215 / 1701 |

The sequential gallery build reached about 33.0 MiB sampled process-tree RSS. The 90-frame native transaction reached 131.5 MiB estimated simultaneous tree RSS. The transaction used strict telemetry, the unchanged 256 MiB job budget and 64 MiB reserve, and reported no limit event. Process-tree RSS is sampled and can miss transient peaks or count shared pages multiple times. These measurements apply to the verification host and sampled scenes. Raw gallery measurements, including pixel hashes, accompany the archive.
