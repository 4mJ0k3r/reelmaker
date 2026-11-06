# Stage 2C · Character staging and mobile readability

Approved baseline [`3a039694478600a6b6b4ff619deed0b4e444a6d3`](https://github.com/4mJ0k3r/reelmaker/commit/3a039694478600a6b6b4ff619deed0b4e444a6d3). Development branch [`stage2c-character-staging-readability`](https://github.com/4mJ0k3r/reelmaker/tree/stage2c-character-staging-readability). Both 3-second hero clips are delivered separately with verification data. [Review evidence](docs/visual-evidence/stage2c/README.md)

## Baseline audit

The existing medium framing preserves geography but favors the environment throughout the beat. Yellow Mellow's white eyes and hand read as small shapes at 360 × 640. Rowan's posture already reads, though the farm background competes with the quieter expression.

| Approved medium at source frame 76 | Actor width × height | Focal object bbox width × height | Observed issue |
| --- | ---: | ---: | --- |
| Yellow Mellow, Cold Ridge | 75 × 164 px | Beacon 308 × 245 px | Beacon and mountain lead the shot, with little space for the face. |
| Yellow Mellow, Dusk Farm | 76 × 165 px | Barn 380 × 361 px | The investigative hand reads as a small silhouette. |
| Rowan, Dusk Farm | 226 × 464 px | Barn 380 × 361 px | Surprise is visible, but the shot gives it the same emphasis as walking. |
| Rowan, Cold Ridge | 224 × 461 px | Beacon 308 × 245 px | Beacon and actor remain legible, while the same camera holds through the reaction. |

Boxes are engine control hulls in output pixels. The beacon box includes its halo and attached paths. This audit sampled the exact Stage 2A and 2B builders. The original hero views are the matched medium references. The additional approved wide reference is included for the full-body scaling check.

## Implementation and camera safety

`visual_library/composition/character_staging.py` compiles the existing storyboard, reuses its blocking manifest and emits three admitted direction shots. The selector is `cinematic_character_staging(character, world)`, with character IDs `rowan_01` and `yellow_mellow_v2` and worlds `farm` and `cold_ridge`. The original character, scene, camera contracts, renderer and encoder code remain untouched. The catalog advertises the callable under the existing close-up component, and the new tests and evidence sampler cover all four combinations.

Context targets the real barn or beacon at 1.08×. The second shot follows the actor's route with full body framing at 1.55× for Rowan and 1.70× for Yellow Mellow. Reaction cuts after the stop into a declared feet crop, with an eased push on the same source timeline. Farm context-to-attention intentionally reframes more than the 60-unit limit of the storyboard wrapper. The direction validator admits the edit with its existing pan bounds, in-shot speed limits, crop checks and cut scale limit. The first cut happens during travel and advances one source frame. The second cut occurs at zero world displacement in all four combinations.

| Combination | Cut pairs | Zoom ratios | Reframe distance |
| --- | --- | --- | --- |
| Yellow Mellow, Cold Ridge | 21→22, 56→57 | 1.574, 1.794 | 38.9, 48.8 logical units |
| Rowan, Dusk Farm | 21→22, 61→62 | 1.435, 1.677 | 91.8, 41.6 logical units |
| Yellow Mellow, Dusk Farm | 21→22, 56→57 | 1.574, 1.794 | 110.3, 89.2 logical units |
| Rowan, Cold Ridge | 21→22, 61→62 | 1.435, 1.677 | 34.4, 46.2 logical units |

Every combination passed direction safety across all 90 frames. All sampled framing margins passed for the declared crop and conservative foreground overlap was zero at the reported shots. In context the beacon is fully inside the safe area and the barn's bbox coverage is 96.8%. The close shot prioritizes the actor and crops away much of the object. The [framing data](docs/visual-evidence/stage2c/framing.json) gives exact object fractions, shot tracking flags, safe margins and actor bounds.

## Actor size and mobile legibility

| Hero and beat | Approved medium height | Stage 2C visible height | Output height visible | Stage 2C zoom |
| --- | ---: | ---: | ---: | ---: |
| Yellow Mellow context, frame 12 | 167 px | 140 px | 10.9% | 1.08× |
| Yellow Mellow attention, frame 50 | 168 px | 222 px | 17.3% | 1.70× |
| Yellow Mellow reaction, frame 76 | 164 px | 416 px | 32.5% | 3.66× |
| Yellow Mellow settle, frame 89 | 168 px | 460 px | 36.0% | 4.00× |
| Rowan context, frame 12 | 469 px | 390 px | 30.4% | 1.08× |
| Rowan attention, frame 50 | 470 px | 561 px | 43.8% | 1.55× |
| Rowan reaction, frame 76 | 464 px | 927 px | 72.4% | 2.69× |
| Rowan settle, frame 89 | 474 px | 974 px | 76.1% | 2.78× |

At frame 50 the full-body Yellow Mellow is 1.70× his 131-pixel approved wide size and 1.32× his approved medium size. In the matched frame 76 phone panels, Yellow Mellow's visible reaction is 2.54× the approved hero height and Rowan's is 2.00×. At 360 × 640 the tilted beanie, eye openings, startle mouth and guarding hand read more clearly. Yellow Mellow still sits low in the strongest crop because the existing portrait projection places the floor below the frame. The widest context remains a geography shot. The two cuts are visible and intentional, especially the farm reframes.

## Parity, tests and determinism

The trusted camera edit retains identical local character commands, contact shadows, world position and actor scale for all 90 frames in all four combinations. Painter order and matched actor/ground depth remain identical. For the original unstaged views, cross-checking the approved source tree and Stage 2C produced identical ordered 90-frame scene and actor command hashes and four identical Cairo pixel samples per case. Repeat pixel hashes matched for each measured camera. Both encoded hero clips fully decoded to 90 distinct frames at 720 × 1280, H.264/yuv420p, 30 fps and three seconds, with a single video stream. Cleanup succeeded, with no staging directories or live Cairo surfaces. [Parity evidence](docs/visual-evidence/stage2c/legacy-parity.json) · [Clip verification](docs/visual-evidence/stage2c/clip-verification.json)

The focused run passed 129 tests, including 12 new Stage 2C cases and the native Stage 1B.1 encoder cleanup and no-clobber regressions.

Catalog generation, validation and freshness checks passed for 48 entries. Candidate and planner exposure statuses remain unchanged. The [branch CI workflow](https://github.com/4mJ0k3r/reelmaker/actions/workflows/visual-catalog.yml?query=branch%3Astage2c-character-staging-readability) runs the native-free regressions.

```bash
export PYTHONPATH=src
python -m reelforge.catalog generate
python -m reelforge.catalog validate
python -m reelforge.catalog generate --check
python -m pytest --basetemp=outputs/stage2c/pytest-native -q tests/test_stage2c_character_staging.py tests/test_stage2b_mellow_performance.py tests/test_stage2a_rowan_performance.py tests/test_stage1c_cold_ridge.py tests/test_snowy_mountain.py tests/test_stage1a_world_kit.py tests/test_stage1b_farm_motion.py tests/test_visual_catalog.py tests/test_encoder_cleanup.py tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary 'tests/test_mvp_prompt_to_reel.py::test_plan_and_manifest_compile[15-5]' tests/test_production.py::test_episode_contracts_unchanged
```

## CPU and memory

AMD EPYC 9V74, eight-vCPU quota, 8 GiB cgroup, Python 3.12.14, Pycairo 1.25.1 and Cairo 1.18.0. Matched Yellow Mellow Cold Ridge samples used 13 frames at 720 × 1280. Timed wall includes hashing and excludes compilation, PNG writing and video encoding.

| Camera | Camera solve | Geometry | Cairo raster | Total wall | Peak RSS | Paths / operations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Approved wide | 0.0006 s | 0.200 s | 0.156 s | 0.389 s | 81.18 MiB | 322 / 1797 |
| Approved medium | 0.0003 s | 0.191 s | 0.129 s | 0.350 s | 81.27 MiB | 322 / 1797 |
| Stage 2C edit | 0.0115 s | 0.177 s | 0.140 s | 0.357 s | 81.28 MiB | 322 / 1797 |

The staged sample used about 9% more raster time than the matched medium in this run. Geometry stayed within the existing allowance of 1,795 paths and 36,418 operations. Full render, encode and verify took 4.39 s for Yellow Mellow and 4.73 s for Rowan. The monitored jobs took 5.76 s and 5.54 s respectively and peaked at 101.55 MiB and 97.82 MiB. Strict monitoring passed with the existing 256 MiB limit and 64 MiB reserve. The low-memory four-vCPU target VM was unavailable. [Raw measurements](docs/visual-evidence/stage2c/performance.json)

## Provisional assessment

Composition and readability 4/5. Context makes the destination clear, while the reaction exposes acting detail that was small in the original Yellow Mellow edit. Silhouette, environment integration, grounding and motion 4/5 on the tested shots. The pose, shadows and color treatment retain continuity across the framing change. Technical performance 4/5 on the measured host. Camera motion and crops are designed for these authored approaches. The low placement of Yellow Mellow and stronger farm cuts are worth judging in playback. Independent review remains the next gate under the [visual rubric](docs/VISUAL_QUALITY_RUBRIC.md).
