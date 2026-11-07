# Sprint B.1 reliability, motion and cinematic quality gate

## Provenance and scope

The branch `sprint-b1-reliability-motion-quality` starts from exact Sprint B
commit `e3c683320d6a64327b07bd951405d9ff026abb4c`, tree
`3be2a92f943921cdbcd358dda052a646f87c0838`. The initial working tree was
clean. All work is local. The final archive contains an identity file and
a complete-history Git bundle verified by restoration.

## Strict requests

All film and interaction request files now enter through the existing
`load_project` reader. It reads at most the established 1 MiB bound,
decodes UTF-8 strictly, rejects duplicate keys, nonfinite constants,
floating-point overflow and nesting beyond 32 containers. Closed preset
validators reject extra fields, non-object requests and unsupported
actor/prop/variant combinations. Tests exercise malformed input and
the actual film-request CLI dispatch.

## Transactions and stale encoder investigation

The original sequence implementation reserved an output directory but
left it behind on failure. Its publication path could expose a film
before the report was written. The corrected transaction stages every
shot and both output files in an inode-owned directory, verifies media,
decoded shot hashes and timestamps, then hard-links the results through an open directory descriptor into
its reserved output. An error removes only this invocation's published
inodes and its original empty reservation. Replacement directories and
foreign files survive. A monitor now spans the complete sequence, in
addition to the renderer's per-shot monitors.

The first B.1 post-render evidence scan again found encoder staging
directories, despite successful in-process cleanup reports. Their file
birth times were later than the encoded files' modification times. This
establishes a discrepancy between the renderer's cleanup observation
and a later workspace scan. It does not establish the original cause.
No broad reconciliation or prefix deletion was introduced.

All Sprint B commands now render inside the owned transaction, including
single-scene interactions and transitions. Same-filesystem private staging
prefers /var/tmp, outside the review workspace. Each owner retains its
directory identity through cleanup. Single-scene publication retains
scene.mp4 and render_report.json. The final evidence scan verifies the
output tree contains no encoder staging directories.

Fault tests inject failures at the beginning, middle and last shot,
joining, decoding, timestamp checks and partial publication. Native faults
at frames 0, 15 and 29 confirm FFmpeg process exit, closed streams, a
finished stderr thread and temporary-path absence. Existing user output,
foreign files and replacement paths have preservation tests.

## Continuous action transitions

Both Mira Scout and Bram Mechanic support:

- idle_to_walk
- walk_to_stop
- idle_to_notice
- notice_to_react
- react_to_idle

Each proof is a single 90-frame sequence with no internal cut. The
transition sampler evaluates arbitrary integer frames directly. It
reuses the established rigs and artwork. Idle-to-walk uses alternating
footprints and eased swing arcs. Walk-to-stop decelerates its gait clock
to a double-support phase. Stationary action blends re-solve the legs
against fixed floor targets.

These are reusable fixed transition presets with authored source phases
and duration. They are available through the transition CLI and gallery.
They do not implement an arbitrary-state motion graph.

## Interaction and film readability

The camera targets the measured actor/prop group. Pickup and sit/stand
use 2.15× framing, and cart push uses 1.95× framing. The camera follows
travel while holding the ground and contact region in view. This makes
the hands, seat, parcel and handle readable at the actual 360×640 frame
size. Original characters, prop artwork and contact sampling are retained.

The Forgotten Parcel and The Creek Crossing retain three-shot, nine-second
structure. Opening framing establishes the object and actor more clearly.
The middle shot uses the same interaction camera as its proof. The
ending uses related framing and a ten-frame recognition hold before
body recoil. Rain and mist remain the authored story cues.

The comparison videos place the original and corrected 360×640 streams
side by side. Mobile stills are decoded from the actual encoded MP4s.
The review package includes every original comparison source.
Independent playback and artistic approval are still required.

## Gallery and browser verification

The offline gallery retains the 71-component catalog. It adds
registry-derived transition preview links and updates the three
interaction motion previews. Static verification checks local links,
variant metadata, motion-file presence and JavaScript syntax.
The motion previews are local animated WebPs.

A fresh Playwright Chromium installation was attempted. The downloaded
archive was corrupt, and the browser launch then failed because the
executable was absent. Real desktop/mobile layout, filter interaction,
clipboard and motion-control browser checks remain blocked. The archive
contains the installation log and launch error. Static checks are
reported separately from interactive browser checks.

## Runtime and verification evidence

The environment is Ubuntu 24.04 with CPython 3.12.3, Pycairo 1.25.1,
Cairo 1.18.0 and FFmpeg 6.1.1. Resource limits remain 256 MiB sampled
process-tree RSS and 64 MiB reserve. Sampled RSS can miss transient peaks
and count shared pages more than once.

The archive includes raw media reports, exact timestamp checks, contact
measurements, transition pose deltas and repeated raster hashes. The
render wall/CPU figures sum shot rendering and per-shot verification.
Whole-sequence monitoring also covers assembly and final decode.

| Final proof | Frames | Render wall s | Render CPU s | Peak process tree MiB |
| --- | ---: | ---: | ---: | ---: |
| mechanic_01-idle_to_notice | 90 | 5.01 | 7.59 | 98.68 |
| mechanic_01-idle_to_walk | 90 | 5.11 | 7.95 | 98.88 |
| mechanic_01-notice_to_react | 90 | 5.57 | 8.34 | 98.74 |
| mechanic_01-react_to_idle | 90 | 5.98 | 9.13 | 98.71 |
| mechanic_01-walk_to_stop | 90 | 5.41 | 8.48 | 98.84 |
| pickup_carry_place | 180 | 10.63 | 16.12 | 98.39 |
| push_cart | 150 | 11.38 | 17.54 | 99.12 |
| scout_01-idle_to_notice | 90 | 6.17 | 9.30 | 98.73 |
| scout_01-idle_to_walk | 90 | 4.80 | 7.43 | 98.89 |
| scout_01-notice_to_react | 90 | 5.60 | 8.52 | 98.74 |
| scout_01-react_to_idle | 90 | 5.31 | 7.98 | 98.71 |
| scout_01-walk_to_stop | 90 | 5.57 | 8.84 | 98.87 |
| sit_stand | 150 | 10.51 | 15.82 | 99.12 |
| the_creek_crossing | 270 | 17.53 | 26.82 | 106.07 |
| the_forgotten_parcel | 270 | 17.32 | 26.22 | 106.22 |

Across all ten transition clips, maximum joint displacement was 5.1646 local units per frame.
Maximum planted-foot drift was 4.52e-09 local units.
Maximum hand-to-socket error was 2.84e-14 local units.
Repeated raster samples at frames 0, 45 and 89 matched their original pixel hashes.
All fifteen corrected MP4s and five encoded comparison MP4s passed full decode and exact PTS verification.

## Test results and review status

| Check | Actual result |
| --- | --- |
| `PYTHONPATH=src:. python -m pytest -q --basetemp outputs/b1-regression` | 325 passed, 0 skipped, 791.09 s |
| Final native three-shot fault checks at first, middle and last shot | 3 passed, 10.52 s |
| `python -m reelforge.catalog validate` | 71 components |
| `python -m reelforge.catalog generate --check` | Passed |
| Baseline catalog file comparison | Exact byte match with Sprint B |
| Generated gallery JavaScript syntax | Passed |
| Corrected media | 15 MP4s fully decoded with exact 30 fps PTS |
| Encoded before/after comparisons | 5 MP4s fully decoded with exact 30 fps PTS |
| Final output-tree cleanup scans | No encoder staging directories found |
| Browser checks | Blocked by corrupt download and missing executable |

The full regression includes historical story digest, original artwork,
character, world, catalog, episode and encoder cleanup checks. After that
run, the native fault test was strengthened to cover three actual shots
and rerun separately. It confirmed both completed earlier encoders and the
faulting encoder had exited and released their streams and staging.

The corrected source, proofs and evidence are ready for independent
engineering and artistic review. The interactive browser gate remains
explicitly blocked. The original cause of the earlier workspace directory
reappearance remains unconfirmed; the owned transaction path passed
fault, replacement, publication-race and subsequent output-scan checks.

Reproduce the main entry points from the repository root:

```sh
export PYTHONPATH=src:.
python -m tools.living_worlds transition scout_01 idle_to_walk --output-dir outputs/new-transition
python -m tools.living_worlds interaction examples/living-worlds/pickup_carry_place.json --output-dir outputs/new-pickup
python -m tools.living_worlds film-request examples/living-worlds/the_forgotten_parcel.film.json --output-dir outputs/new-film
python -m tools.asset_gallery build
```

Each output directory must be new. The evidence exporter accepts an output
root with the fifteen proof directories and a before directory containing
the five original MP4s:

```sh
python -m tools.sprint_b1_evidence --before-dir ../evidence/before --output-root outputs/new-b1-proofs
```

No remote publication or independent approval is claimed.
