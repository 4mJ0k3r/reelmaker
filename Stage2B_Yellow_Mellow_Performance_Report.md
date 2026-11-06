# Stage 2B · Yellow Mellow V2 investigates a signal

Approved baseline [`636272221bd44dfba0dbc0308f320236bb2be2c0`](https://github.com/4mJ0k3r/reelmaker/commit/636272221bd44dfba0dbc0308f320236bb2be2c0). Development branch [`stage2b-yellow-mellow-performance`](https://github.com/4mJ0k3r/reelmaker/tree/stage2b-yellow-mellow-performance). Review the [stills, motion data and verified clip metadata](docs/visual-evidence/stage2b/README.md). The three-second Cold Ridge MP4 is delivered separately.

## Audit and implementation

| Area | Historical behavior | Observed weakness | Stage 2B correction |
| --- | --- | --- | --- |
| Face | Existing white eyes, numeric brow and lid controls, short expression blends | Curious and surprised both use a round mouth in the historical sample | A small sideways smile, asymmetric brow and lowered lid distinguish inquiry from the open startle and worried mouth. |
| Head and gaze | The native look clip already leads with gaze | In the historical scene the effect is subtle at wide scale | Preserve eye-first order, keep the head tilt through the investigation and hold attention after the recoil. |
| Gesture | Both hands open wide in surprise | The bilateral gesture dominates even after the visible peak | Investigate with the near hand, recoil through the head and torso, then bring the forearms into a compact asymmetrical guard. |
| Recovery | Native `recover` windmills both arms and can regather the feet | That action competes with the prior startle in a three-second shot | Release arm tension, keep both feet fixed, settle the eyes with one blink and hold. |
| Walk and stop | V2 already plans foot roll, contacts and secondary motion | Its legacy drawer overlays an independent gait on the scene route, so flat feet can drift in the rendered world | Feed accepted route velocity and distance to the existing V2 foot planner for the new selector. Seed the opening walk stance to allow the far foot time to swing. |

The new `characters/yellow_mellow_v2/investigation.py` builds one native `Performance` from route-driven `LocomotionClip` and a planted `KeyedClip` using the existing look and tilt targets. `motions.py` exposes the opening phase as a hook with its original default. `character.py` makes natural blinks optional for the single authored blink. `episode.py` adjusts only the opt-in drawer's root placement. Blocking validation and sampling admit and inspect the native pose, and schema updates expose the executable V2 option in blocking, scene and storyboard. The two proofs use one `mellow_approach.py` composition helper. The existing character art, rig, Rowan pose mathematics, renderer, encoder and planner remain in their prior implementations.

The exact selector is `"performance": {"name":"investigate_and_react","reaction":"surprised"}` with `"character":"yellow_mellow_v2"`. See the [usage guide](docs/STAGE2B_YELLOW_MELLOW_PERFORMANCE.md). All 48 catalog entries validated and the V2 record remains `candidate` / `not_assessed`.

## Motion and regression evidence

The [native quality analysis and rendered-world diagnostics](docs/visual-evidence/stage2b/measurements.json) cover all 90 frames for the matched legacy ridge, refined ridge and refined farm.

| Measurement | Legacy ridge | Refined ridge and farm |
| --- | ---: | ---: |
| Native planted slide, ground penetration, leg reach error | 0, 0, 0 rig units | 0, 0, 0 rig units |
| Largest flat stance step in the rendered world | 0.812 logical units | 5.68 × 10⁻¹⁴ logical units |
| Maximum adjacent-frame joint displacement | 29.544 rig units | 17.278 rig units |
| Clamped pose channels / knee flips / airborne frames | 0 / 0 / 0 | 0 / 0 / 0 |

Both refined routes travel 50.767 logical units. Position at the walk/brake and brake/hold joins is continuous, with at most 7.11 × 10⁻¹⁵ units/s sampled join mismatch. At the refined plant-to-notice boundary the largest joint step was 4.62 rig units against a nearby median of 1.50. The reviewed adjacent frames show the last boot coming down as the body settles. This boundary is visibly busier than the subsequent facial transition. The largest hat response reached its existing 0.10 rad cap. Pom horizontal travel peaked at 2.384 rig units, inside the 3.5-unit bound. The only visible blink spans frames 82–86 in the proof, after the reaction peak.

The [baseline comparison](docs/visual-evidence/stage2b/legacy-parity.json) matched all 90 ordered command frames and five Cairo pixel samples per case for default Rowan, Stage 2A Rowan in both World Kits, historical Yellow Mellow on snow, and the matched legacy Yellow Mellow shot. The opt-in repeated frame hash matched. The V2 primary-state cache remained at 48 entries.

117 focused tests passed, including 12 new Stage 2B tests and native encoder cleanup/no-clobber coverage. The published [branch workflow](https://github.com/4mJ0k3r/reelmaker/actions/workflows/visual-catalog.yml?query=branch%3Astage2b-yellow-mellow-performance) runs the native-free catalog and selected regressions.

```bash
export PYTHONPATH=src
python -m reelforge.catalog generate
python -m reelforge.catalog validate
python -m reelforge.catalog generate --check
python -m pytest --basetemp=outputs/stage2b/pytest-native -q tests/test_stage2b_mellow_performance.py tests/test_stage2a_rowan_performance.py tests/test_stage1c_cold_ridge.py tests/test_snowy_mountain.py tests/test_stage1a_world_kit.py tests/test_stage1b_farm_motion.py tests/test_visual_catalog.py tests/test_encoder_cleanup.py tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary 'tests/test_mvp_prompt_to_reel.py::test_plan_and_manifest_compile[15-5]' tests/test_production.py::test_episode_contracts_unchanged
```

## CPU and memory

Intel Xeon Platinum 8573C, eight-vCPU quota, 8 GiB cgroup, Python 3.12.14, Pycairo 1.25.1 and Cairo 1.18.0. The matched ridge medium shots used frames 3, 20, 34, 46, 47, 58, 59, 64, 65, 70, 76, 83 and 89 at 720 × 1280. Wall time includes hashing and excludes compile, PNG writing and encoding.

| Case | Geometry | Cairo raster | Total wall | Peak tree RSS | Paths / operations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Legacy | 0.264 s | 0.229 s | 0.537 s | 44.68 MiB | 322 / 1797 |
| Refined | 0.287 s | 0.224 s | 0.560 s | 44.78 MiB | 323 / 1797 |

The refined sample cost approximately 4% more wall time in this run. Both fit the existing scene allowance of 1,795 paths and 36,418 operations. Strict monitoring completed without cancellation or OOM deltas. The [continuous proof](docs/visual-evidence/stage2b/clip-verification.json) took 5.78 s to render, encode and verify and 7.26 s for the monitored job, with 101.30 MiB estimated peak process-tree RSS. Full decode produced 90 distinct frames at 30 fps in silent 720 × 1280 H.264/yuv420p. Cleanup succeeded and left zero staging directories and live surfaces. The four-vCPU low-memory deployment VM was unavailable.

## Provisional artistic assessment

| Criterion | Assessment |
| --- | --- |
| Silhouette/design | 4/5 at medium scale. The investigative tilt and asymmetric recoil read without face detail. |
| Materials | 4/5. Existing saturated clothing reads in both grades. |
| Grounding | 4/5. Scene feet and shadows stay together through the stop. |
| Composition | 4/5 in medium. Eye and brow nuance is hard to resolve in the widest mobile view. |
| Integration | 4/5. Both worlds use the same rig, timing and performance implementation. |
| Motion | 4/5 provisional. The face leads and the arms release. The short format leaves only a brief recovered hold, and the startle overlaps a compact forearm silhouette. |
| Technical performance | 4/5 on the measured host, pending the target VM. |

Independent engineering and artistic review can proceed using the actual artwork and motion clip. Production promotion remains subject to the [visual quality rubric](docs/VISUAL_QUALITY_RUBRIC.md).
