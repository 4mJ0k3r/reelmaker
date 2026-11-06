# Stage 1B motion and performance report

Baseline `f761c4e4429f0f7d14848c2bd6be2db0236f166f` was verified on
`stage1a1-world-kit-polish`. This work is on
`stage1b-world-kit-motion-performance`. The locally measured Stage 1B
implementation is `002fb5d5df987753dc0442bef360ab447151841b`. Its source
tree is `0a0996223af7f5314e701d8855fdc0fa17b5e48d` before evidence and report
files. The published review commit contains the same implementation.

## Integration audit and changes

The farm scene is a stationary scene-0.1 assembly. Blocking-0.1 is the
smallest existing workflow that admits Rowan's horizontal Hermite route,
gait, planted contacts and character-frame override. Its level-field
admission gate recognizes only named ground assets. The farm track already
declares a support envelope and shares the actor's layer depth. Adding this
specific ID to the gate admits the existing default level corridor without
widening bounds, changing validation or adding terrain physics.

`farm.py` exposes the same scene data through `farm_manifest`.
`farm_motion.py` composes that data into a trusted blocking manifest for
either layout. `blocking/contract.py` adds the support ID. The adapter
removes the stationary Rowan decal and retains tree and barn contact
marks. Blocking solves the existing Rowan feet, draws his local sole
shadows from the pose, and supplies a world-space override to
`evaluate_layers`. Existing camera projection applies the same transform
to the actor and his shadows. No rig, planner or scene-schema change.

`scenes/assets.py` and `nature/dusk.py` contain bounded optimizations.
`tools/blocking.py` documents the admitted grounds. Targeted tests and the
existing catalog workflow cover the new path. No catalog input or readiness
field changed. The [evidence index](docs/visual-evidence/stage1b/README.md)
contains the exact reproduction command and artifact paths.

## Motion

The original route runs from (91, 524) to (147.2, 524). The alternate runs
from (269, 524) to (212.8, 524). Both are within the admitted corridor
(40, 500) to (320, 570) and both preserve support and actor scale 0.72.
The path crosses the near shoulder toward the barn. It does not follow
the curved centerline or advance in depth.

| Frames | Action |
| --- | --- |
| 0–8 | Stationary opening pose and look |
| 9–59 | 49-unit rightward walk in the original layout |
| 60–71 | 7.2-unit controlled stop |
| 72–89 | Held planted stance and surprised reaction |

Both camera modes compiled for both layouts. The native blocking camera
uses the validated scene approach with near-layer depth 1.4 and sky depth
0. The storyboard compiler also accepted the same original scene, route
and beats through its own validated camera. The full encoded proof uses
the blocking approach. The alternate is sampled once at frame 51.

Across all 90 frames the maximum measured planted-pivot residual was
2.84e−14 world units in the original layout and 5.68e−14 in the alternate,
below the existing 1e−7 threshold. The compiler also applies its continuous
foot sweep bound. Frame 36 catches far heel contact, frame 51 catches near
heel contact, and frame 66 catches braking. The rig's shadow cues remain
under the supported soles as they change position. Painter order and camera
projection are checked in the focused tests.

The key frames, reduced mobile frames and 12 consecutive decoded frames
32–43 show weight transfer, stable background, a readable stop and a clear
final gesture. The start is close to left foliage in screen space, and
the movement is a short lateral approach across the track shoulder. The
shadows are small contact cues. Curved traversal, a sloped plane and
walking all the way to the door remain outside the verified scope.

## Performance investigation

AMD EPYC 9V74, eight-vCPU cgroup quota, 8 GiB cgroup memory limit.
Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0 and FFmpeg 6.1.1.
Static measurements used the same existing sampler, same 12 frame indices,
720 × 1280 resolution and one reused Cairo surface. Timed work includes
evaluation and rasterization. It excludes compilation, PNG writes and
video encoding. Exact measurements are in
[performance.json](docs/visual-evidence/stage1b/performance.json).

| Static sample | Wall | CPU | Wall/frame | Peak tree RSS | Paths / operations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stage 1A, current host | 0.315 s | 0.335 s | 26.3 ms | 29.68 MiB | 378 / 2,207 |
| Stage 1A.1, current host | 0.580 s | 0.616 s | 48.3 ms | 29.65 MiB | 365 / 2,124 |
| Stage 1B, first sample | 0.373 s | 0.399 s | 31.1 ms | 29.56 MiB | 365 / 2,124 |
| Stage 1B, confirmation | 0.453 s | 0.487 s | 37.7 ms | 29.45 MiB | 365 / 2,124 |

This reproduces the previously reported 27.6 → 43.2 ms/frame direction of
change. A separate 12-frame timing split measured 13.4 ms geometry and
17.2 ms raster for Stage 1A, versus 16.8 ms and 32.2 ms for Stage 1A.1.
Rasterization was the larger contributor. Skipping the polished sky in an
isolation run reduced raster time to 23.1 ms. That ablation removes the
whole sky and measures its workload, so it does not isolate a single
gradient. The sky's broad fills and the layered terrain are real raster
work despite low path counts. Temporarily bypassing the barn grade reduced
geometry time to 11.7 ms. A CPU profile independently identified per-frame
paint reconstruction, immutable command replacement and transform copies.
These probes have scheduler noise and are directional measurements.

Stage 1B caps the graded barn recipe cache at eight immutable local
results, keyed by two validated scene controls. It stores no manifests,
surfaces or rendered frames. Zero-anchor recipe evaluation skips an
identity transform copy. The farther two opaque hill fills stop under the
next opaque layer, avoiding covered shading. Static samples recover a
meaningful portion of the regression. The 35 ms stretch target was met on
the first run and missed on confirmation. Cairo still dominates the
optimized split at about 28.1 ms raster versus 9.3 ms geometry.

The matched establishing frame 36 retained pixel SHA-256
`f398b3b35f78f90de3abaaa6437a1badc031211641c373f6ec94ac502b88fab7`.
The establishing, alternate, isolated sky and tree PNGs also matched byte
for byte. The medium view had two pixels differ by at most one 8-bit
channel value at fractional projection. There was no intended art change.
Full sequence visual inspection was limited to the sampled decoded frames.

## Encoded proof and resource gate

The separate animated workload had 90 unique decoded frames, H.264
yuv420p, 720 × 1280, 30 FPS, exactly 3.0 seconds and no audio.
Geometry took 1.001 s and rasterization took 2.282 s, about 36.5 ms/frame
combined. Streaming writes took 0.292 s. End-to-end render, encoding and
decode verification took 5.054 s wall, with 4.588 s parent CPU and
2.696 s child CPU. Peak process-tree RSS was 98.38 MiB. The maximum was
362 paths and 2,111 operations. Strict monitoring remained active, with
no cancellation or OOM event changes. The 256 MiB process-tree cap and
64 MiB reserve were retained.

The standard runner returned `TRANSACTION_CLEANUP` after successful media
verification because a completed encoder staging directory reappeared.
The existing safety policy retained the verified media and marked the run
failed. The proof is review evidence, and the cleanup issue remains a
release blocker. A no-clobber retry rejected the existing output directory
and left the video checksum unchanged. No additional full render was run.

## Verification and readiness

With `PYTHONPATH=src`, ran the motion, Stage 1A, catalog and snowy-mountain
tests plus the existing 15-second planning and vocabulary tests. All
58 passed. The 32 catalog and World Kit/motion tests also passed without
Cairo. The seven motion tests passed again with a strengthened shadow
projection assertion. Catalog validation and regeneration check passed for
48 entries, and Ruff and staged whitespace checks passed. The hosted CI
result was unavailable at publication time.

| Gate | Status |
| --- | --- |
| Static World Kit | Technically ready for review, with matched establishing pixels and bounded resource use |
| Animated-scene integration | Ready for independent review of the validated level walk and existing camera, with a verified review clip and a runner cleanup blocker |
| Low-memory target host | Unverified. The 0.4–1 GiB deployment host was unavailable. |
| Artistic approval | Pending. All five assets remain candidates. |

Provisional rubric assessment is 4/5 for gait/contact, layer stability,
static visual preservation and sampled CPU/memory, and 3/5 for staging
breadth and framing. The latter reflects the narrow lateral route and
nearby foliage at the opening. Reviewers should assess the actual clip at
normal speed before approving the movement or integration.
