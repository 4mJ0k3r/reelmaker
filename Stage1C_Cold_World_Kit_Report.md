# Stage 1C · Cold Environment World Kit

The Cold Ridge is a candidate World Kit for independent engineering and art review. The approved baseline is [Stage 1B.1](https://github.com/4mJ0k3r/reelmaker/commit/7a7401bc004655642fe586ba79380040a148aaba), on `stage1b1-encoder-cleanup-fix`. The development branch is `stage1c-cold-world-transfer`.

## Frost Peak audit

The historical art shows repeated triangular peaks, conifers built from similar stacked wedges, wide beacon and storm accents, and sharp snowfield bands. The [matched clear comparison](docs/visual-evidence/stage1c/before-after.jpg) isolates the visual opt-ins by holding the camera, placements, frame and weather constant.

| Existing asset | Historical variants | Registry anchor | Paths / operations | Stage 1C decision |
| --- | --- | --- | ---: | --- |
| `frost_sky_01` | `default` | (0, 0) | 128 / 2400 | Reuse the cold sky as-is. |
| `frost_peaks_01` | `far`, `mid` | (180, 300) | 160 / 3000 | Add `cinematic_far` and `cinematic_massif` for two deliberately different depth profiles. |
| `frost_ridge_01` | `default` | (0, 0) | 320 / 6000 | Add `sculpted`. Keep the local support envelope at (-250, -90, 250, 220). |
| `pine_snow_01` | `tall`, `short`, `cluster` | (0, 0) | 64 / 1200 | Add `pinnacle` and `windshear` with different proportions, crowns and contact silhouettes. |
| `frost_rocks_01` | `cliff`, `drift` | (0, 0) | 48 / 900 | Reuse `cliff` at ground and foreground depths. Use the existing dusk prop decal at the ground outcrop. |
| `beacon_01` | `buried`, `active` | (0, 0) | 96 / 1600 | Add `local_signal` with three halo layers, no wide beam and compact ground falloff. Keep the interaction socket. |
| `answer_light_01` | `default` | (0, 0) | 24 / 400 | Retain for existing scenes. The proof shot uses the beacon alone. |
| `frost_foreground_01` | `default`, `storm` | (180, 640) | 160 / 3000 | Add `ridge_wind` with 24 authored wind strokes and clear space around the action. |

A reusable cold composition with independent framing, layout and mood was the missing capability. Trusted builders now validate it through scene-0.1 and blocking-0.1. Camera math, renderer, encoder and planner vocabulary use the existing implementations. Stage 1C does not add a weather simulator, slope navigation, new registered IDs or catalog promotion.

## Visual and character review

- The offset massif and subdued distant ridge break the legacy peak repetition. Snow catches the upper faces, exposed rock forms the darker planes, and low haze separates the massif from the drifts. The tree crowns and trunk proportions remain distinguishable at 360 × 640.
- Rowan and the amber beacon read in both phone-size moods. The beacon remains the only concentrated warm light. Wind stays out of their staging band, with its greatest visibility high in the sky. At phone size the storm reads as light wind, with a smaller contrast change than the mountain and terrain upgrade.
- The ledge and outcrop stage depth from opposite corners across the two layouts. The saddle reuses the same mountain profiles, so it demonstrates rearrangement within the same location. The inherited sky ribbons and cliff facets remain more graphic than the refined terrain, and the conifers still read as stylized cut shapes in the close study.
- The level route moves Rowan from (110, 480) to (166.2, 480) with terrain and actor at depth 1. The transformed support is (-70, 380, 430, 690) and the level corridor is (30, 440, 330, 560). Existing walking shadows move with Rowan. Across 90 evaluated frames, maximum recorded planted contact error was 2.84 × 10⁻¹⁴ logical units. The [walk sheet](docs/visual-evidence/stage1c/level-walk.jpg) provides three consecutive frames and two later samples. Motion evidence is limited to that sample and the measured contacts.

Review the [full evidence index](docs/visual-evidence/stage1c/README.md) using the [visual rubric](docs/VISUAL_QUALITY_RUBRIC.md). Independent scores and an approval decision remain open.

## CPU and memory

Ubuntu 24.04.3, AMD EPYC 9V74, eight-vCPU quota, 8 GiB cgroup, Python 3.12.14, Pycairo 1.25.1 and Cairo 1.18.0. Eight frames per case at 720 × 1280, sampled at 0, 12, 24, 36, 48, 60, 72 and 89 of the 30 FPS timeline. Timing includes scene frame evaluation, Cairo rasterization and pixel hash readback. Compilation, PNG writes and encoding are outside the timed region. The existing monitor samples process-tree RSS.

| Case | Wall s | CPU s | Wall ms/frame | Peak tree RSS | Max paths / ops | Scene allowance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Refined establishing clear | 0.166 | 0.176 | 20.73 | 30.63 MiB | 258 / 1587 | 1411 / 27418 |
| Refined medium storm | 0.173 | 0.182 | 21.67 | 30.68 MiB | 282 / 1635 | 1571 / 30418 |
| Legacy medium storm, highest sampled command cost | 0.211 | 0.220 | 26.41 | 31.16 MiB | 455 / 1848 | 1571 / 30418 |

Monitoring completed under the 256 MiB process-tree cap with the 64 MiB admission reserve, strict memory policy, zero OOM event deltas and no cancellation. The sampler repeated frame 36 in each case and obtained identical pixel SHA-256 hashes. See [raw results](docs/visual-evidence/stage1c/performance.json). The four-vCPU deployment VM with 0.4–1.0 GiB available memory was unavailable. These are short Cairo measurements on the development host.

## Verification

- The focused regression run passed 89 tests across Stage 1C, historical snowy scenes, the dusk World Kit, blocking motion, catalog, planner vocabulary and compilation, episode contracts, and encoder cleanup.
- All 18 Stage 1C tests also passed in the Cairo-free workflow environment. The catalog generated from registry and companion metadata, validated all 48 entries, and passed `generate --check`. New variants remain `candidate` and `not_assessed`.
- A separate baseline comparison hashed the command stream for each of the 14 historical Frost Peak variants with identical inputs. Every hash matched the Stage 1B.1 source tree.
- The [Visual catalog workflow](https://github.com/4mJ0k3r/reelmaker/actions/workflows/visual-catalog.yml?query=branch%3Astage1c-cold-world-transfer) runs the catalog and focused checks on the published revision.

```bash
export PYTHONPATH=src
python -m reelforge.catalog generate
python -m reelforge.catalog validate
python -m reelforge.catalog generate --check
python -m pytest -q tests/test_stage1c_cold_ridge.py tests/test_snowy_mountain.py tests/test_stage1a_world_kit.py tests/test_stage1b_farm_motion.py tests/test_visual_catalog.py tests/test_encoder_cleanup.py tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary 'tests/test_mvp_prompt_to_reel.py::test_plan_and_manifest_compile[15-5]' tests/test_production.py::test_episode_contracts_unchanged
```
