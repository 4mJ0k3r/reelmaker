# Stage 3A.1 · The Other Light

## Editorial diagnosis

The baseline is published commit `1d7dfde2e3de82605d94fee1353a52b41766e16b`.
I ran the original MP4 at its 30 fps clock using offscreen FFplay and inspected
decoded frames and the Stage 3A review evidence. The host has no directly
viewable playback display, so the visual comparison is frame-based.

| Frames | What the original shows | Intended reading |
| --- | --- | --- |
| 0–89 | The beacon is legible immediately. A slow push spends the entire first three seconds on the already glowing lamp. | Show who is here and establish the distance to the beacon during the first second. |
| 90–143 | The traveler first appears and starts his approach at 90. The cut at 112 brings the two subjects closer. The glow stays visibly amber. | Make an unusual change in the light legible while the traveler and beacon share the frame. |
| 144–179 | After braking, the glance begins around 144–150. The close-up at 147 isolates the face. Widening eyes around 160–163 and recoil around 166 read clearly, without a clear visible cause. | Keep the performance and place the abnormal signal immediately before the glance. |
| 180–269 | The distant light is visible on the first frame of the ridge cut. The last image shows two lights, but the shot itself does not show the distant light appear. | Hold the geography, let the distant light emerge, and hold the two lights together. |

## Edit and implementation

| Refined global frames | Picture and action |
| --- | --- |
| 0–27 | A medium-wide composition opens on Yellow Mellow and the amber beacon together. |
| 28–89 | A wider ridge view settles toward the approved approach camera. |
| 90–133 | The existing walk starts at the opening's actor location, facing right. |
| 134–146 | The lamp emits one white-gold surge. The halo ring peaks at 140 during braking and settles as the gaze begins. |
| 147–179 | The original close-up, facial timing and recoil play out. |
| 180–203 | The near lamp anchors the frame while the distant ridge stays dark. |
| 204–218 | A distant point rises and blooms in the ridge's saddle. |
| 219–269 | The bloom eases back and both lights hold. |

`cinematic_story("the_other_light_refined")` adds an opt-in edit.
The CLI retains the original as the default and accepts `--story` to choose the
refinement. The opening uses the existing stationary Yellow Mellow scene
recipe at the approach's initial location, facing and scale. The camera
matches at frames 89/90. The cut introduces the original walking rig, which
has a small stance change from the opening's neutral standing pose. Middle
camera cuts at 112 and 147 retain the original motion and framing.

The two new registered variants are `beacon_01:ridge_surge` and
`answer_light_01:ridge_reveal`. The surge adds three paths, 18 operations at
peak, over the existing `local_signal` artwork. The ridge effect begins with
zero paths, then draws five bounded paths. The registered scene recipe
evaluates both from the existing segment-local timestamp. Each event is
single, bounded and stateless. By the end cut the nearby light is amber
again. No physical contact is shown. The episode format, renderer, route,
rig, camera admission, planner, and resource limits retain their original
implementations.

Source changes are confined to the snowy asset recipes, asset registry,
catalog descriptions, story recipe and CLI selector. Generated catalog files,
focused tests, their CI entry, these notes and decoded evidence complete the
change. Existing beacon and answer-light variants matched the original
ordered drawing-command hashes for all 90 local frames per variant. The
original manifest digest and ten original Cairo pixel samples match Stage 3A.
All 90 middle-frame actor overrides, pose and contact diagnostics, facial
samples, facing, positions, shadows and camera samples match the original.

## Visual review

The [opening comparison](docs/visual-evidence/stage3a1/opening-before-after.jpg)
shows Yellow Mellow at frame 0, three seconds earlier. The wide part of the
opening still holds the actor in place until the walk starts, so it gives
the viewer geography rather than extra character action. The
[beacon comparison](docs/visual-evidence/stage3a1/beacon-event.jpg) shows an
expanding ring and brighter lamp before the expressive close-up. There is
roughly a second between the pulse peak and the clearest recoil, with braking
and investigation in between. A viewer must still connect those beats through
proximity and the edit. The [ridge progression](docs/visual-evidence/stage3a1/distant-reveal.jpg)
shows the light absent, appearing and held apart from the moon. The
[closing comparison](docs/visual-evidence/stage3a1/ending-before-after.jpg)
keeps the near lamp and recognizable peaks in frame.

| Review category | Provisional self-assessment |
| --- | --- |
| Story clarity, pacing | 4/5 on decoded frames. Early character introduction helps. The opening's second view is deliberately still. |
| Visual event, acting | 4/5. The local ring is visible while both subjects share the shot. The existing reaction is clear in close-up. |
| Camera, continuity | 4/5. Five transitions were checked at their adjacent frames. The opening handoff matches the world position and camera. |
| Final reveal, art integration | 4/5. The distant core rises within the shot and holds. Its source remains unresolved. |
| Technical performance | 4/5 on the development host. The target four-vCPU low-memory VM was unavailable. |

The original and revised files each ran at their 30 fps clocks using offscreen
FFplay. Direct visual playback on this headless host was unavailable. The
mobile review uses decoded 360 × 640 frame panels. An independent viewer should
judge whether the pause in the opening and the interval between surge and
recoil work at speed. This is a review submission without production approval.

## Verification

The render command exited 0 and reported successful publication of the local
output, media verification and transaction cleanup. Full decode confirmed
270 distinct decoded frames, exact 30 fps presentation times, nine seconds,
720 × 1280 H.264/yuv420p and zero audio streams. The black-frame scan found
none. Selected source pixels reproduced exactly. The source evaluated all
270 indices independently. Two pairs of non-adjacent source hashes coincide
during the closing hold. No frames were inserted to extend the film.
The no-clobber retry exited 1 with `OUTPUT_EXISTS` and the MP4 checksum
matched before and after. The owned staging directory was absent.

At phone resolution, 3,427 pixels in the local region around the frame-140
beacon differed by more than 30 in at least one channel from the original
frame. The distant core's 9 × 9 patch measured mean RGB 124/148/170 at
frame 180 and 254/244/224 at 218. See [verification data](docs/visual-evidence/stage3a1/verification.json)
for hashes, frame positions and telemetry.

| Metric | Stage 3A | Stage 3A.1 |
| --- | ---: | ---: |
| Render and encode | 7.39 s | 9.25 s |
| Monitored end-to-end wall time | 15.11 s | 17.98 s |
| Peak estimated process-tree RSS | 102.55 MiB | 101.37 MiB |
| Maximum paths and operations | 324 / 1,801 | 324 / 1,801 |
| Peak sampled logical staging | 3,451,698 B | 2,979,634 B |

Both measurements used the same class of development host and workflow.
This run used Ubuntu 24.04.3, AMD EPYC 9V74, an eight-vCPU cgroup quota,
Python 3.12.14, Pycairo 1.25.1 and Cairo 1.18.0. The original opening did
not render a character. The revision does for 90 extra frames, so the
single-run timing difference cannot be assigned to the new light paths.
Admission stayed within the 256 MiB process-tree budget and 64 MiB reserve.

The catalog validates all 48 components and the generated files match.
The native regression run passed 89 tests using:

```bash
python -m pytest -q tests/test_stage3a1_editorial_polish.py tests/test_stage3a_cinematic_story.py tests/test_stage2b_mellow_performance.py tests/test_stage2c_character_staging.py tests/test_stage1c_cold_ridge.py tests/test_visual_catalog.py tests/test_encoder_cleanup.py tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary tests/test_production.py::test_episode_contracts_unchanged --basetemp outputs/stage3a1/pytest
```

The new tests are wired into the Visual catalog workflow. Hosted CI is
pending publication of the Stage 3A.1 branch.
