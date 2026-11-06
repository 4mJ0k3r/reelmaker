# The Cold Ridge World Kit

The Cold Ridge stages Rowan approaching an emergency beacon on a snowy mountain pass. It uses the existing scene registry, painter order, and Cairo projection. See the [review stills](visual-evidence/stage1c/README.md) and [engineering report](../Stage1C_Cold_World_Kit_Report.md).

| Existing asset | Opt-in variant | Use |
| --- | --- | --- |
| `frost_peaks_01` | `cinematic_far`, `cinematic_massif` | Lower-contrast distant range and an asymmetric near massif with exposed rock and snow planes. Place at separate depths. |
| `pine_snow_01` | `pinnacle`, `windshear` | Tall, tapered conifer and lower, leaning conifer with asymmetric snow shelves. Place at the trunk base. |
| `frost_ridge_01` | `sculpted` | Continuous snow support with shallow drift shapes, sparse facets and cooler shadow-facing snow. |
| `beacon_01` | `local_signal` | Amber lens with short falloff and a ground accent. Uses the existing beacon origin and socket. |
| `frost_foreground_01` | `ridge_wind` | Sparse, coherent diagonal wind. The authored action band is kept clear of streaks. |

`cold_ridge_scene(view="establishing", *, layout="pass", weather="clear", legacy=False)` returns a validated scene. `cold_ridge_manifest` accepts the same arguments and returns scene-0.1 data for the trusted pipeline. Both views accept either layout and either weather setting. Use `legacy=True` for comparisons with the historical assets in the same staging. `cold_ridge_walk()` supplies a blocking-0.1 manifest for the sampled level approach.

- `establishing` uses the base 360 × 640 logical frame. `medium` uses the existing depth projection with camera offsets `(10, 12)` and zoom `1.29`. Both use fixed framing and render at 720 × 1280.
- Place the sky at depth 0, distant mountains at 0.22, and the near massif at 0.52. The two ranges are centered around logical `(180, 292)` and `(180, 300)`. Their silhouettes overlap the valley haze before the snow support begins around y=470.
- The ground anchor is `(180, 470)`. Rowan, trees, middle-distance rock and beacon share depth 1 with the ground. Place Rowan at scale 0.72 and the beacon at 0.83. Plant the tree trunks and rock origins at their terrain contact points. The near ledge crops into a lower corner at depth 1.4. Weather is drawn last at depth 1.25.
- In `pass`, Rowan is left of the beacon, with a tall conifer on the left, a shorter wind-shaped tree and outcrop on the right, and the ledge low left. In `saddle`, Rowan faces left toward the relocated beacon. The rock and conifer grouping shifts left and the near ledge moves to the right.
- Cool fill and blue-gray shadow planes dominate, with the brightest exposed faces on the upper left of the landforms. The beacon provides the warm local accent. `clear` uses atmosphere 0.51 and breeze 0.05. `storm` raises them to 0.73 and 0.85 and adds the sparse wind layer. Both use warmth 0.18.
- The terrain retains its registered support envelope and horizontal `level_field` corridor. The sample walk uses the existing motion-aware shadow. The kit supports fixed views, static conifers and authored wind. Slope following, collision, depth navigation and a moving camera are outside the supported demonstration.

Reproduce the stills and measurement JSON from the repository root after installing the existing Cairo runtime and evidence dependencies.

```bash
mkdir -p outputs/stage1c
PYTHONPATH=src python tools/stage1c_cold_stills.py outputs/stage1c/local > outputs/stage1c/local-performance.json
PYTHONPATH=src python -m reelforge.catalog validate
PYTHONPATH=src python -m reelforge.catalog generate --check
```

Use a fresh output path for each run. The sampler writes individual Cairo PNGs. The review sheets combine or annotate those PNGs for inspection.
