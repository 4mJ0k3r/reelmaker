# Stage 3A · The Other Light

Approved baseline [`e0f271c4b217`](https://github.com/4mJ0k3r/reelmaker/commit/e0f271c4b217a5f1c1000f46462925e509bc99dc).
Development branch [`stage3a-cinematic-story-assembly`](https://github.com/4mJ0k3r/reelmaker/tree/stage3a-cinematic-story-assembly).
The verified local baseline tree matches the published tree
`14106d126bfbe046d0f44a28faf8e77ee74f9222`.

## Architecture audit

The episode workflow already compiled complete 90-frame storyboards to direction plans,
mapped global frames with `divmod(frame, 90)`, streamed one Cairo surface into one encoder,
and applied global audio and transactional verification. Stage 2C independently compiles
`direction-0.1`. The selected Cold Ridge pans are approximately 38.86 and 48.80 logical units,
within the 60-unit storyboard cap. The obstacle is timing. Storyboard views change at beat
boundaries, but the existing motion beats break at local frames 40 and 54, and the approved
camera cuts are at 22 and 57. Splitting or moving those motion beats would change the
accepted blocking timeline. The object-only inserts also have no travel bout, which
the storyboard compiler requires.

`episode-0.3` therefore adds an exclusive directed segment alongside the storyboard
source. Both use their existing compilers. The new version admits registered scenes and
procedural environments, including those under blocking. It excludes user-authored
geometry compositions, raw commands and external paths. The old episode contracts
retain their existing scene and audio admission. Rendering samples the admitted direction
in both cases, with no changes to the encoder, muxer, character, world art, planner,
production chunking, or resource policy. No catalog promotions or new registrations.

Changed files are the episode contract, schema and workflow, the episode CLI, the production schema’s storyboard reference, the trusted
recipe and its generator, episode and Stage 3A documentation, focused tests, the existing
CI workflow and compact review evidence.

## Story and continuity

A lit beacon stands alone in a snowy pass. Yellow Mellow walks toward it, slows, and
recoils during his investigation. After he settles, the film cuts back toward the beacon,
revealing a smaller white-gold light on the ridge. The edit leaves the connection between
the two lights unresolved. The soundtrack is silent.

| Segment | Global frames | Local frames | Acting and editorial purpose |
| --- | --- | --- | --- |
| `beacon` | 0–89 | 0–89 | Object push. The familiar orange lamp establishes the focal object. |
| `approach` | 90–111 | 0–21 | Context introduces Yellow Mellow on the left, walking toward the beacon. |
| `approach` | 112–146 | 22–56 | Full-body follow preserves the rightward route and slows with him. |
| `approach` | 147–179 | 57–89 | Close-up on the one-handed investigation, recoil and recovery. |
| `ridge` | 180–269 | 0–89 | The cutaway links the near beacon to the distant light in one image. |

The recipe embeds the exact Stage 2C direction in the middle segment. All 90 frame
command lists match the separately compiled approved direction, including body,
route, contact shadow and landscape commands. The inserts share the near beacon's
world transform and the ridge's depth layers. They omit the actor, so an independent
scene clock never produces a new visible actor position or pose across the two
episode cuts. Exact adjacent frames, staging coordinates and the mobile review are
in the [visual evidence](docs/visual-evidence/stage3a/README.md).

## Provisional art assessment

The near orange lamp stays identifiable across scales. The follow has room for the
boots and the direction of travel. The close-up gives the tilted hat, wide eyes and
raised hand enough space to read at phone size. The ridge reveal separates the smaller
light from the moon and keeps the near beacon low on the left to preserve geography.
The palette and ground lighting carry across all three segments.

The opening gives the beacon a full three seconds before the traveler appears,
which makes it the slowest beat. The close-up places Yellow Mellow low in the frame
and largely removes the beacon. The final shot invites a connection between the
lights, while the near beacon remains lit throughout and no contact, activation
or confirmed reply is shown. The reason for his startle can therefore remain
ambiguous to a first-time viewer. The large cut from close-up to the ridge is
intentional. Independent visual playback at normal speed is still required.
The development review inspected the decoded film's timed progression and exact cut
pairs. A 30 fps offscreen playback check exited 0 in 9.31 s. The headless host did
not provide a directly viewable real-time display. See the [quality rubric](docs/VISUAL_QUALITY_RUBRIC.md).

## Verification and measured cost

One CLI run encoded and published the complete silent film. It returned exit 0,
decoded all 270 frames and reported exact timestamps at frame/30, H.264/yuv420p,
720 × 1280, 30 fps and 9.000 seconds. All 270 source hashes and all 270 decoded
frame hashes were unique. The full decoded luma check found zero black frames.
Re-evaluating 13 source frames reproduced their exact pixel hashes, including all
eight frames adjacent to the episode and camera cuts. A second render request at
the existing destination returned `OUTPUT_EXISTS` with the MP4 SHA-256 unchanged.
The transaction directory and its encoder staging were absent after success.
There were no resource cancellations or recorded OOM events.

| Measurement | Result |
| --- | --- |
| Host | Ubuntu 24.04.3 x86-64, AMD EPYC 9V74, cgroup quota equivalent to 8 vCPUs |
| Native versions | Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0, FFmpeg 6.1.1 |
| Geometry and Cairo, 13-frame sample | 16.20 and 12.78 ms/frame respectively |
| Maximum geometry | 324 paths, 1,801 operations |
| Render and continuous encode | 7.39 s |
| Silent stage with its full decode | 10.22 s |
| Publication-stage verification | 3.37 s |
| Shared workflow / outer CLI monitored wall time | 13.61 s / 15.11 s |
| CPU time | 9.56 s parent, 10.86 s child user, 0.53 s child system |
| Peak sampled process-tree RSS | 102.55 MiB, with 256 MiB budget and 64 MiB reserve |
| Peak sampled logical staging | 3,451,698 bytes, including hard-link double-counting |
| Published MP4 size | 1,725,849 bytes |

The native test selection covers Stage 3A, Stages 2A–2C, encoder cleanup, catalog,
the legacy episode contract and the existing planner vocabulary and 15-second
planning case. The run passed 77 tests. The corrected native transaction assertion passed on a
focused rerun, and the production schema compatibility test passed separately,
for 79 distinct passing tests. The catalog validates 48 entries and both generated
files match.
The [branch CI](https://github.com/4mJ0k3r/reelmaker/actions?query=branch%3Astage3a-cinematic-story-assembly)
is the authoritative hosted result.

The target low-memory VM was unavailable. Local resource measurements describe the
measured host and cannot certify target deployment. The film is submitted for
independent engineering and artistic review. All visual components retain candidate
status. See the [reproduction commands](docs/STAGE3A_CINEMATIC_STORY_ASSEMBLY.md)
and [verification data](docs/visual-evidence/stage3a/verification.json).
