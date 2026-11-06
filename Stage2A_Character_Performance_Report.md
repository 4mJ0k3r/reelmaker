# Stage 2A · Rowan Vale character performance

Approved baseline [`81363883858c4d360a111ec60cba61276db7f66f`](https://github.com/4mJ0k3r/reelmaker/commit/81363883858c4d360a111ec60cba61276db7f66f). Development branch [`stage2a-cinematic-character-performance`](https://github.com/4mJ0k3r/reelmaker/tree/stage2a-cinematic-character-performance). Candidate evidence is indexed in [Stage 2A stills](docs/visual-evidence/stage2a/README.md). The independent reviewer supplies the artistic decision.

## Audit and changes

| Historical sample | Observation | Decision |
| --- | --- | --- |
| Neutral stand and concern | Rowan's hat, face, jacket and stance already identify him. Concern relies on small brow and mouth changes. | Preserve the figure and face coordinates. Give the opt-in face a clearer lid and brow asymmetry and a shaped mouth. |
| Look-around | The standing preset starts with a generic arm extension and a loose periodic gaze. | Lead with the eyes, tilt the head, then bring the torso and arm into the concern. |
| Surprise and fright | The same body motion carries both expressions. They mainly differ in mouth width. | Use a round opening and raised brows for surprise, a wider tense mouth and stronger guarded recoil for fright. |
| Walk, brake and stop | Rowan has an accepted analytic route, roll and planted-foot solve. The stationary reaction swaps facial expression at the segment boundary. | Keep the gait and route. Blend the opt-in facial contours over multiple frames, stage the recoil after the stop and finish with one settle blink. |
| Medium and establishing | Fine eye and mouth detail loses contrast at mobile width. Feet, hat angle and hands remain stronger cues. | Use fixed camera, distinct lean and gesture, and verify both views in both World Kits. |

`characters/rowan.py` adds a matched contour drawer for the opt-in face. `characters/rowan_performance.py` supplies absolute-time cues, bounded joint offsets and delayed accessory response. `blocking/{contract,sampling,schema}.py` select the preset, keep the existing feet and route, and use the existing solver for local balance adjustments. `storyboards/{compiler,schema}.py` forward the option through the existing direction adapter. The two proof worlds use one `visual_library/composition/rowan_approach.py` staging helper. The blocking CLI and authoritative catalog advertise the executable interface. Renderer, encoder, planner, Yellow Mellow artwork and both environment kits retain their existing code.

The exact selector is `performance: {"name":"notice_and_react","reaction":"surprised"}` in blocking-0.2 or under storyboard `rowan`. The alternate `frightened` uses the same sequence. See the [usage guide](docs/STAGE2A_CHARACTER_PERFORMANCE.md). All 48 catalog records validate, and the Rowan record remains `candidate` / `not_assessed`.

## Motion and regression

- Both authored right-facing routes share identical position and velocity with their matched legacy route at every frame. Maximum join discontinuities were zero position and 8.88 × 10⁻¹⁵ world units/s velocity. Fixed camera and scale are retained through both stops. A left-facing Cold Ridge saddle route also passes.
- Across 90 frames for each of three cases, maximum planted contact residual and consecutive same-stance flat-foot drift were 2.84 × 10⁻¹⁴ world units each, against the existing 1 × 10⁻⁷ contact gate. Maximum segment limb-length error was 7.11 × 10⁻¹⁵ rig units. The two-bone solver accepted all sampled reaches. Rowan's rigid skeleton has no independent anatomical joint limits. Tests check sampled joints at cue boundaries against the existing continuity tolerances.
- The largest sampled near-forearm step was 0.219 rad for surprise and 0.252 rad for fear during the guarding gesture. Maximum hat and bag rotations were 0.022 and 0.044 rad, within their respective 0.055 and 0.14 rad bounds. Gaze reached 0.92 of the allowed local range. Only the existing contact shadow follows the feet.
- Against the verified baseline tree, all 90 command streams matched for the historical farm walk, historical ridge walk, historical Yellow Mellow snowy storyboard and the matched legacy Stage 2A staging. Sampled Cairo pixels also matched at five frames per case. The opt-in benchmark reproduced frame 76 pixel hashes. See [legacy parity](docs/visual-evidence/stage2a/legacy-parity.json) and [raw measurements](docs/visual-evidence/stage2a/measurements.json).
- The farm medium proof encoded as silent 720 × 1280 H.264/yuv420p at 30 FPS. Full verification decoded 90 frames with 90 distinct hashes. The encoder reported successful cleanup, no staging directory remained and the renderer released all surfaces. See [clip verification](docs/visual-evidence/stage2a/clip-verification.json).

The focused run passed 105 tests, including 14 Stage 2A cases and native Stage 1B.1 encoder cleanup cases. Catalog generation, validation and regeneration check passed.

## CPU and memory

Intel Xeon Platinum 8573C, eight-vCPU quota, 8 GiB cgroup, Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0. Matched farm medium shots have identical route, camera and world. Timings for 13 sampled frames at 720 × 1280 exclude compilation, PNG and encoding, and wall time includes pixel hashes. A single sample does not establish a speedup.

| Case | Geometry | Cairo raster | Total wall | Peak tree RSS | Peak paths / ops |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical | 0.140 s | 0.482 s | 0.672 s | 63.20 MiB | 362 / 2111 |
| Refined | 0.126 s | 0.448 s | 0.622 s | 63.22 MiB | 364 / 2121 |

The sampled scene allowance was 885 paths and 17,442 operations for both cases. Strict monitoring completed without cancellation or OOM event deltas. The continuous proof took 15.16 s to render, encode and verify and 16.56 s for the monitored storyboard job including compilation. Estimated simultaneous peak tree RSS was 98.16 MiB, below 256 MiB with a 64 MiB admission reserve. The four-vCPU low-memory deployment VM was unavailable.

## Provisional art assessment

| Criterion | Assessment |
| --- | --- |
| Silhouette and composition | 4/5 in medium. Concern's forward head angle and surprise's guarded arm read on mobile. At the establishing distance the eye and mouth differences are subtle. |
| Materials and integration | 4/5. The same artwork and beat read against both warm and cool backgrounds with the original grading. |
| Grounding | 4/5. Pose sheets, consecutive frames and numerical checks agree on foot placement. |
| Motion | 4/5 provisional. The face leads recoil, and the hand, scarf and attachments follow. The hold remains an alert posture with residual breathing. Exact object tracking and full head yaw are outside this planar performance. |
| Technical performance | 4/5 on the measured host. Deployment validation remains open. |

The [branch CI workflow](https://github.com/4mJ0k3r/reelmaker/actions/workflows/visual-catalog.yml?query=branch%3Astage2a-cinematic-character-performance) tracks the submitted revision. The branch is intended for independent review, with production promotion governed by the [visual rubric](docs/VISUAL_QUALITY_RUBRIC.md).
