# ReelMaker operator guide — 1.0 (D8–D9)

ReelMaker draws registered vector scenes with CPU Cairo and streams 720×1280,
30 fps H.264/yuv420p to FFmpeg. A requesting agent authors bounded JSON; the
engine does not interpret arbitrary scripts. Supported deployment platform:
Ubuntu 24.04 x86_64 / CPython 3.12. Target low-memory VM qualification remains
separate from a successful development-host run.

## Install and discover

On a provisioned build/development host:

```sh
sudo apt-get update
sudo apt-get install -y libcairo2-dev pkg-config python3-dev build-essential ffmpeg
uv sync --frozen --extra renderer
.venv/bin/python tools/cinematic_project.py capabilities
.venv/bin/python tools/cinematic_project.py schema --version cinematic-project-0.2
```

See NATIVE_SETUP.md for the pinned stack and low-memory wheel provisioning.
Build native wheels on a roomier compatible host when necessary. Runtime
production does not require sudo. No GPU, browser, image service or TTS is used.
Do not install or change dependencies while another render is active.

Capabilities is the authoritative machine-readable selection menu: project
versions, actions/expressions, per-world moods, interaction restrictions,
effects, signal/dressing, camera motions, shot intentions, timing styles,
audio IDs, examples, durations and resource policy. The catalog has 77
components; registration alone does not imply unrestricted planner exposure
or independent artistic approval.

## Discover → Select → Validate → Plan → Preflight → Render → Verify → Deliver

Use a new output leaf beneath an existing persistent directory outside /tmp.
Do not use traversal or symlink paths. Run jobs sequentially.

```sh
mkdir -p outputs/operator
.venv/bin/python tools/cinematic_project.py validate examples/sprint-d8-d9/the_last_transmission.json
.venv/bin/python tools/cinematic_project.py plan examples/sprint-d8-d9/the_last_transmission.json
.venv/bin/python tools/cinematic_project.py inspect examples/sprint-d8-d9/the_last_transmission.json
.venv/bin/python tools/cinematic_project.py preflight examples/sprint-d8-d9/the_last_transmission.json outputs/operator/transmission
.venv/bin/python tools/cinematic_project.py render examples/sprint-d8-d9/the_last_transmission.json outputs/operator/transmission
.venv/bin/python tools/cinematic_project.py verify outputs/operator/transmission
```

`render` is the single production command; it already coordinates rendering,
audio, full decode, storyboard, final package verification and atomic publication.
Preflight is advisory and repeats admission at production time. A successful
package is published only after verification, never as a partial success.
Validation/plan/inspect are native-free. Frame PNG inspection and production
require the pinned Cairo/FFmpeg stack.

## Input timing, staging and direction

Use cinematic-project-0.2 for current staged work; 0.1 remains supported with
its historical semantics. Shots occupy exactly 90 frames each. Beats cover
all shots contiguously, with integer half-open start/end. Current 0.2 beats
span 1–4 shots; interactions always reserve their fixed 180-frame staging.
Actor clocks continue across camera cuts inside a beat; a new beat is an
explicit authored blocking cut. This is not a physics/choreography system.

Scout/Mechanic can share disjoint swept lanes at least 42 logical units apart.
Stage anchors are integers 36–276; complete travel must stay in the admitted
32–320 lane. Interactions choose their own staging, compatible actor, world,
mood and variant. Do not add a second actor, custom geometry, placement,
expression or timing override to an interaction recipe.

Optional shot `intent` is admitted only with `camera: "auto"`. Choices:
establish, approach, observe, react, reveal, interact, pursue, wait, depart,
resolve, cliffhanger. Movement intentions require a locomotion action;
interact requires an interaction; reveal requires a signal or prop. Optional
focus selects actor/partner when admitted. Explicit cameras still work.
The resolver chooses only registered cameras. An explicit motion overrides
its bounded default. A true `hold` repeats the same intention within one beat;
repetition without a hold remains a diagnostic, not a hard rejection.

Optional beat/partner `pacing` selects actual anticipation and clip speed:

| Style | Anticipation | Speed |
| --- | --- | --- |
| measured | 12 frames | 1× |
| tense | 24 frames | 1.5× |
| urgent | 0 frames | 2× |

An explicit delay precedes anticipation. A partner inherits beat pacing unless
it overrides it. Transitions hold frame 89, ordinary clips hold their supported
12-second endpoint. Pacing never resets at a cut. Registered interactions
reject pacing and retain their contact clock. Omitted pacing preserves legacy
sampling. A lamp cue is an internal editorial cut in a paired beat with a lit
signal; a moving left-facing performer cannot pivot at the cue.

`inspect` adds explanations, repeated-composition warnings, all-frame camera
envelopes and mobile root/head diagnostics to the plan. The plan digest is
unchanged by inspection. Root/standing-head metrics are not silhouette,
occlusion or artistic certification; inspect decoded 360×640 sheets too.

## Audio and captions

Audio is supported for 3–30 seconds (1–10 shots). Longer 33–60-second projects
are silent and use verified sequential chunk assembly. There is no automatic
60-second narration or TTS. The existing diag_* assets are synthetic diagnostic
signals; never call them human narration or recorded environmental sound.

An operator with a real PCM16 WAV can register it using the trusted local tool:

```sh
PYTHONPATH=src .venv/bin/python tools/register_audio.py supplied.wav --id my_narration --role narration
```

Registration changes the local trusted audio registry, not project-selected
executable code. Project JSON references IDs only. Supported WAV rates are
16/24/44.1/48 kHz, one or two channels, bounded to 8 MiB. The existing workflow
validates hashes/metadata, snapshots WAVs, mixes globally at 48 kHz stereo and
verifies AAC timing. Cue starts/trims are frame aligned; output has 1600 samples
per frame. Use at most one narration and four SFX cues; observe admitted gain
and overlap restrictions. A CLI-selected `--registry DIRECTORY` must contain a
valid trusted registry and its pinned WAVs. Do not edit registered bytes.

Captions use admitted ASCII, short mobile-safe lines, sorted non-overlapping
frame spans and registered styles. Use no captions when testing visual story
clarity. Unsupported Hindi glyph overlays require separate future work; do not
silently claim the ASCII contract supports them.

## Output and verification

A completed directory contains reel.mp4, project.json, timeline.json,
report.json, verification.json, storyboard/ and allowlisted engine/ evidence.
The report names contract/input/plan/video identities, output/audio format,
frame count, duration, verification, resource measurements and warnings.
Storyboards use decoded first/middle/last frames for every shot.
The final atomic package verification checks source/timeline/video identity,
full decode, stream count/codec, exact rational PTS, faststart and black-frame
criteria. Long assembly compares every decoded frame to the chunk sequence.
Audio waveform/timing evidence is in report.json from the registered mix gate.
`verify` independently rechecks a delivered package without overwriting it.
Successful encoding alone is not an artistic or deployment acceptance decision.

## Errors, cancellation and recovery

The CLI returns 0 on success, 2 on structured error. Inspect stderr JSON:
`error.code`, `error.path` (JSON Pointer where applicable), `error.message`.
Enum errors list valid alternatives; validate again after correction.

| Error | Action |
| --- | --- |
| CINEMATIC_PROJECT / JSON_* / INPUT_TOO_LARGE | Correct the identified bounded field; use capabilities/schema |
| CINEMATIC_ARGUMENT | Correct CLI arguments using --help |
| OUTPUT_EXISTS | Preserve previous output and choose a new leaf |
| OUTPUT_PATH / OUTPUT_SYMLINK | Use a direct new output under a non-symlink persistent parent |
| MEMORY_PREFLIGHT / RESOURCE_GUARD | Stop; restore capacity/telemetry. Never override limits |
| AUDIO_ASSET / AUDIO_CHANGED / CINEMATIC_ENGINE registry_validation | Restore pinned WAV/registry or register a new legitimate ID |
| NATIVE_DEPENDENCY / TOOL_UNAVAILABLE | Provision the documented pinned runtime |
| REEL_CANCELLED / PRODUCTION_CANCELLED / CANCELLED | Treat as cancellation; preserve prior completed outputs |
| CINEMATIC_OWNERSHIP / WORKSPACE_IDENTITY / TRANSACTION_IDENTITY / TRANSACTION_PRESERVED | Stop and investigate the reported preserved work; never delete by prefix |
| CINEMATIC_INTEGRITY / CINEMATIC_DECODE | Treat the package as rejected; preserve evidence |

SIGINT/SIGTERM set cooperative cancellation through the existing process
supervision; native child groups are stopped and reaped within finite waits.
No partial result is published. A child ownership uncertainty preserves work
rather than recursively deleting replacement content. Fix an ordinary input
or missing dependency, validate/preflight, and retry with a new output name.
Do not change source to make a production request pass. Never reuse failed
encoder staging or erase a foreign/replaced path.

The memory policy is 256 MiB process-tree budget plus 64 MiB reserve, with
strict guest/cgroup observations, no hidden override and no swap assumption.
RSS is sampled, not an exact OS hard limit. Missing OOM telemetry is unknown,
not zero. Historical delayed staging-name recurrence remains unresolved;
see SPRINT_D8_STAGING_INVESTIGATION.md. The bounded optional engineering trace:

```sh
.venv/bin/python tools/trace_cinematic.py PROJECT.json OUTPUT TRACE.json --observe-seconds 2
```

Exit 3 means delayed recurrence detected even if the MP4 is valid. The observer
never deletes recreated names. The target VM and real offline-gallery browser
interaction must be qualified independently when those environments are available.
