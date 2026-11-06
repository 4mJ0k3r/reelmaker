# Stage 3B · The Empty Doorway

## Baseline and scope

This work starts on the exact approved Stage 3A.1 commit
`11d0b8a0cde3880c2f80735f961e110a9655881c` on
`stage3b-second-cinematic-story`. The commit SHA is the branch head
(`git rev-parse HEAD`). This report, source, generated catalog, tests and
decoded evidence share that commit.

| File | Role |
| --- | --- |
| `src/reelforge/visual_library/composition/farm_story.py` | New fixed story recipe over admitted Rowan/Farm direction. |
| `src/reelforge/environments/polish.py` | One opt-in shadow path and doorway clip. |
| `src/reelforge/scenes/assets.py` | Variant registration and dispatch over the existing cached graded barn. |
| `src/reelforge/catalog/inventory.py` | Variant metadata. |
| `tools/stage3b_story.py` | Deterministic manifest export. |

The support files update the generated catalog, focused tests, CI invocation,
operator documentation and review evidence. There are no changes to shared
episode, renderer, encoder, camera admission, blocking or resource interfaces.

## Story and architecture reuse

Rowan spots a barn on the Dusk Farm path and starts toward it. A dark shape
slides across the recess, crossing right to left behind the jambs. He
recoils. The final cut returns to the same entrance and holds on its emptiness.

| System | The Other Light | The Empty Doorway |
| --- | --- | --- |
| Contract and output | Silent `episode-0.3`, three 90-frame segments | Same compiler, Cairo renderer and continuous FFmpeg encode |
| Actor and world | Yellow Mellow V2, Cold Ridge | Rowan Vale, Dusk Farm, using the same scene and character registries |
| Performance and camera | Investigation, recoil and a ridge reveal | Approved Rowan route, concern and surprise, with a doorway insert admitted by the same camera validator |
| Incident | White-gold surge | One moving occlusion in the barn's existing recess |
| Payoff | A new light appears in the distance | The same entrance returns empty |

Both historical story manifest digests match the baseline. The new recipe
compiles to a complete standalone episode using registered assets and
existing scene-local timing. It requires no external files or shared
narrative state.

## Doorway event and continuity

The baseline mobile audit showed that the barn's nominal 54-unit entrance
is narrowed by its jambs. In the shared approach shot the visible recess
measures about 40 pixels wide on the 360 × 640 canvas. The 2.42× insert
gives the event a 58 × 121 px inset at mobile scale. The existing lower
interior gradient provides enough separation for a darker contour without
adding an interior light. The shadow is one curved, slanted shape with
top-to-bottom opacity. The inset clip preserves the jambs and threshold.
It adds one path and 12 path/clip operations at most. Registration retains
the original 256-path and 4,000-operation asset envelope.

| Global | Local | Picture |
| ---: | ---: | --- |
| 0–89 | 0–89 | Wide arrival and a slow push toward Rowan and the barn. |
| 90–111 | 0–21 | The approved walk begins on a matched camera and world origin. |
| 112–120 | 22–30 | Brief follow establishes the route and screen direction. |
| 121–124 | 31–34 | The doorway insert starts empty. |
| 125–145 | 35–55 | The shadow traverses right to left. Rowan's early notice begins underneath the insert. |
| 146–151 | 56–61 | The shape clears the doorway before the cut back to Rowan. |
| 152–179 | 62–89 | Concern, visible surprise and recoil. The expression reads clearly at 165. |
| 180–269 | 0–89 | Return to the matched doorway angle, ease closer, then hold on the empty entrance. |

The preliminary insert admitted the camera but let Rowan's hat enter at the
left edge late in the shot. The final frame adjustment places his maximum
right bound at −4.45 logical pixels over all 31 insert frames. The camera
continues to pass the existing safety limits. The approved middle performance
matches across all 90 frames, including the actor commands and their shadows,
position, facing, reaction and foot contact diagnostics. Camera sampling
matches outside the insert. Both historical barn variants match the approved
drawing-command hashes at frames 0, 44 and 89.

## Artistic review

The [decoded shadow progression](docs/visual-evidence/stage3b/shadow-progression.jpg)
shows the empty doorway, entrance from the right, passage, exit and empty
recess. In the 360 × 640 decode the darkened region's centroid moves from
x 142.19 at frame 129 to x 88.71 at 145. At 135, 3,021 pixels darken by at
least 14 luma levels versus frame 123. At 149 and the matching return at
180, no pixel in that patch crosses the threshold. The shadow is visible
without a label or extra light. Its source stays ambiguous.

The opening uses a three-second environmental push with a stationary
actor. A small stance change is visible at the walk handoff even though
the camera and origin match. The follow is deliberately brief. The sharp
cut to the doorway and the visual return after the close reaction give
the film a different rhythm from the first film's rising light reveal.
The barn reads clearly on the phone-size panels, though the moving shape
is concentrated in the darker lower portion of the recess. Headless FFplay
ran the complete file at its 30 fps clock. Visual review used decoded
chronological frames and cut pairs. Direct normal-speed visual assessment
remains open for the independent reviewer.

## Technical verification

The CLI completed with exit 0. The local output published and verified
successfully, and the owned transaction directory was absent. Full decode
confirmed silent 720 × 1280 H.264/yuv420p, 270 frames, 30 fps, nine seconds
and exact presentation timestamps. The black-frame scan found none.
Twenty-three repeated Cairo source samples matched the original render
hashes. Independently evaluated frames can match during fixed compositions
and holds. There were 225 distinct source images and 266 distinct decoded
images across 270 timestamps. The no-clobber retry returned `OUTPUT_EXISTS`
and the MP4 checksum stayed identical.

| Measurement | Stage 3B |
| --- | ---: |
| Mean geometry evaluation, 23-frame sample | 7.78 ms/frame |
| Mean Cairo rasterization, same sample | 20.61 ms/frame |
| Render and encode | 12.13 s |
| Monitored wall time | 20.80 s |
| Peak process-tree RSS | 99.80 MiB |
| Maximum observed geometry | 365 paths / 2,133 operations |
| Shadow overhead | 1 path / 12 operations |
| Peak sampled logical staging | 3,520,396 B |

Host was Ubuntu 24.04.3 on AMD EPYC 9V74 with an eight-vCPU quota.
Runtime was Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0 and FFmpeg 6.1.1.
No resource or cleanup error was reported. The host stayed within the
256 MiB process-tree budget and 64 MiB admission reserve. The specific
four-vCPU low-memory deployment environment remains untested.

The catalog validates all 48 components and generated outputs match.
The final targeted suite passed 95 tests. It covers the new story, both first-film versions, Rowan,
camera staging, farm, episode compatibility, catalog and encoder cleanup:

```bash
python -m pytest -q tests/test_stage3b_farm_story.py tests/test_stage3a1_editorial_polish.py tests/test_stage3a_cinematic_story.py tests/test_stage2a_rowan_performance.py tests/test_stage2c_character_staging.py tests/test_stage1a_world_kit.py tests/test_visual_catalog.py tests/test_encoder_cleanup.py tests/test_production.py::test_episode_contracts_unchanged --basetemp outputs/stage3b/pytest-final
```

The [verification JSON](docs/visual-evidence/stage3b/verification.json)
records media and manifest hashes, mobile pixel samples, cut points and
resource data. Automatic review rejected the first rendered evidence upload
because it recognized only the earlier Stage 3A.1 publication authorization.
Stage 3B is committed locally, and the complete source and evidence archive
includes the standalone manifest. There is no Stage 3B hosted CI result.

## Independent review readiness

The decoded evidence supports submitting the film for independent
engineering and artistic review. The stationary opening, brief follow and
held ending are the main pacing choices to assess on playback. This stage
makes no production-readiness promotion.
