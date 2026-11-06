# ReelMaker Living Worlds · Sprint B

## Scope and baseline

The development branch is `asset-b1-b6-living-cinematic-worlds`. It starts
at approved commit `8d71ea2b582c7cf7e1f579cdc7e1c5152c4f39d5`, tree
`0c3eaffcfe9fc024d70fd1c818fadcd934570b61`. GitHub read access confirmed
the published baseline branch points to that commit. This sprint remains
local. Hosted CI has yet to run.

The [architecture audit](docs/SPRINT_B_ARCHITECTURE_AUDIT.md) records the
existing extension points. The new director uses the existing validated
scene graph, Cairo renderer, encoder and production stream-copy helpers.
Historical blocking and storyboard admission retains its previous actors.
Local commits group audit, characters, interactions/effects/worlds, then
proofs and gallery. The delivery archive records the final commit and tree.

## Actors and contacts

| Actor | Artwork | Actions | Expressions |
| --- | --- | --- | --- |
| Mira Scout · `scout_01` | Narrow hood, amber scarf, travel satchel and slim boots | idle, walk, run, notice, react | neutral, happy, concerned, surprised, frightened, determined |
| Bram Mechanic · `mechanic_01` | Broad torso, work cap, utility bib, belt and gloves | idle, walk, run, notice, react | neutral, happy, concerned, surprised, frightened, determined |

The rigs share a trusted hierarchy and bounded planar two-bone solves.
Walk and run have independent stride lengths, rates, lift and arm swing.
Each foot has a fixed world footprint during its planted interval.
The second pass raised the resting pelvis and projects it only when reach
requires a correction. Expression geometry varies eyes, eyebrows and
mouths. Both actors use the authored right-facing profile. Actor reels
use editorial cuts between actions. A reusable seamless transition
interface and independent transition evidence for all requested action
pairs are outstanding.

| Interaction | Compatible actors | Prop variants |
| --- | --- | --- |
| `pickup_carry_place` | Scout, Mechanic | `parcel_01`: wrapped, utility |
| `sit_stand` | Rowan, Scout, Mechanic | `bench_01`: timber, painted, weathered |
| `push_cart` | Mechanic, Scout | `handcart_01`: empty, loaded |

Interactions use closed `interaction-0.1` requests. Ownership changes are
sampled from bounded phases. Parcel attachment and cart handle contact
use a near-hand solve in the same scene depth projection as the prop.
The cart's wheels rotate with travel distance. The existing Rowan artwork
and leg solver supply the Rowan sit. The seat reference is local y=−19.
Alternate pairings have contact tests, while the encoded proofs cover
Scout pickup, Rowan sit and Mechanic push. Cart hand contact is single-hand.
These are authored planar actions with fixed timing and placement.

## Atmosphere and world kits

| Registered effect | Variants |
| --- | --- |
| `rain_field_01` | light, steady, heavy |
| `wind_leaves_01` | gentle, gust, autumn |
| `smoke_wisp_01` | thin, rising, windblown |

These recipes are frame-index deterministic and bounded. Rain uses
depth-dependent rates. Leaves persist along authored trajectories.
Smoke opacity tapers to zero at the recycle boundary. Layer placement
remains author-controlled. Wind and rain are demonstrated in the world
videos. Rising smoke appears in the Creek Crossing ending. Each variant
has an offline gallery preview.

| Kit | Moods | Staging |
| --- | --- | --- |
| `village_lane` | daylight, evening, rainy_night | Roadside house and shop, curb, lamp and bench |
| `woodland_creek` | clear, misty, windy | Visible creek channel and banks beneath the existing timber span |

Each mood has a complete scene manifest, 720×1280 still and 360×640
preview. World selection returns validated scene JSON. Scout, Mechanic
and stationary Rowan are admitted. The creek and bridge are decorative.
Actor movement uses the existing supporting ground and stays on the
approach in the proofs. The rainy-night grade is localized and authored.

## Films and gallery

The Forgotten Parcel stages notice, pickup, carry, placement and
a surprised reaction as rain reaches the lane. The Creek Crossing
stages an equipment push toward a span, then a pause and reaction as
the creek fills with mist. Each is three scene shots, 270 frames and
nine seconds. These fixed source-owned film presets use a strict
`living-film-0.1` selection request. They render through the scene path
and verified stream-copy assembly. Episode contract integration is
outside the delivered interface.

The final [evidence folder](docs/visual-evidence/sprint-b) contains the
creek comparison, before/after parcel framing, neutral actor stills,
pose sheets and mood images. Review used decoded sampled frames from
the encoded videos. The tighter middle camera makes contact more
readable, although facial acting and the final story cues still benefit
from independent playback review.

The [offline gallery](docs/asset-gallery/index.html) lists 71 catalog
components. All 62 prior records remain intact. New scene actors, props
and weather derive their metadata from the trusted registries. World
and interaction requests appear in a separate section. Motion previews
are local animated WebPs. The archive supplies the nine full MP4s.
Browser runtime checks remain outstanding because this workspace has
no supported browser executable. JavaScript syntax, metadata generation,
preview references and native-free discovery were checked locally.

## Media verification and resources

Each delivered MP4 was fully decoded and verified at 720×1280, exact
30 fps timestamps, H.264/yuv420p. Both films and both actor reels
preserved decoded shot hashes during the stream-copy join. All shot
reports showed zero retained Cairo surfaces and no resource limit events.
A stale encoder directory was observed outside the renderer's reported
cleanup result in the workspace. It was quarantined, and the package
contains only the verified MP4s and reports. Local tests cover the
existing encoder cleanup and output no-clobber paths.

Measurements use the existing sampled process-tree RSS monitor and
the unchanged 256 MiB budget with 64 MiB reserve. CPU time sums the
scene process and observed children. Multi-shot wall measurements below
sum rendering and per-shot verification and exclude final assembly.

| Proof | Frames | Wall render s | CPU render s | Peak tree MiB |
| --- | ---: | ---: | ---: | ---: |
| mechanic_01 | 225 | 9.49 | 12.79 | 106.34 |
| pickup_carry_place | 180 | 6.48 | 9.37 | 99.28 |
| push_cart | 150 | 5.88 | 8.46 | 99.07 |
| scout_01 | 225 | 9.87 | 13.39 | 106.29 |
| sit_stand | 150 | 5.57 | 7.98 | 99.16 |
| the_creek_crossing | 270 | 10.70 | 15.53 | 106.32 |
| the_forgotten_parcel | 270 | 10.36 | 14.96 | 106.31 |
| village_lane | 90 | 3.49 | 5.05 | 96.81 |
| woodland_creek | 90 | 3.06 | 4.43 | 96.62 |

Maximum measured near-hand socket error across the four tested actor/interaction pairings: 2.84e-14 local units.
The gallery build peaked at 33.12 MiB sampled tree RSS.

## Local verification

Ubuntu 24.04, CPython 3.12.3, Pycairo 1.25.1, Cairo 1.18.0, FFmpeg
6.1.1. Local tests ran with `PYTHONPATH=src:.`.

- `python -m pytest -q --basetemp outputs/b-regression` passed 276 tests
  in 453.49 seconds, with zero skips and zero failures.
- `python -m reelforge.catalog validate` reported 71 components.
- `python -m reelforge.catalog generate --check` passed.
- All 62 baseline catalog records matched the approved JSON records.
- Existing historical story digest, Rowan and Yellow Mellow, A1–A4,
  encoder transaction and no-clobber checks passed in the full suite.
- The new tests cover pinned stance, deterministic random frame access,
  scene schema parity, all admitted interaction variants, reach alignment,
  bounded weather, world moods, gallery references and film no-clobber.
- `node --check` passed on the generated gallery script.

The strongest independent review candidates are the fixed interaction
presets, atmosphere variants and six world moods. The two actor rigs and
nine encoded proofs are available for review with the transition and
playback limitations above. The gallery is ready for source and static
evidence review. Interactive browser review is outstanding.
