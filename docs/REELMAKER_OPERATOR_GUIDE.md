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
sampling. A lamp cue without a style remains an internal editorial cut in a paired beat
with a lit signal. A moving left-facing performer cannot pivot at that cue.

For a stationary paired beat, opt in with `cue_style: "alert"` or
`cue_style: "relief"`. Use two idle actors and set `cue_frame` relative to the
beat. It can now fall inside a shot while the 90-frame shot grid stays fixed.
The lamp starts in the opposite state and switches to the requested `signal`
at that frame. Alert supports either edge. Relief requires a lit final state.
The response retains the authored facing and both planted feet. Each actor's
`delay_frames` and pacing anticipation offset the cue response independently.
The reaction gesture plays once at its authored 1× speed. Leave time for both
actors to respond. See the discoverable `grounded_signal_story_30s` example.

For opt-in motion polish, use `walk_to_settle` on a staged actor or partner.
It keeps the original walk-to-stop travel, contact targets and endpoints,
adding a brief weight transfer near the last step. Use `alert_settle` or
`relief_settle` on a paired stationary lamp cue for a small listening pose
and a grounded response. Authored partner delays still set the stagger.
The older action and cue names retain their original motion.

`inspect` adds explanations, repeated-composition warnings, all-frame camera
envelopes and mobile root/head diagnostics to the plan. The plan digest is
unchanged by inspection. Root/standing-head metrics are not silhouette,
occlusion or artistic certification; inspect decoded 360×640 sheets too.

## Audio and captions

The short route supports registered narration and sound-effect cues. Staged
`cinematic-project-0.2` projects of 33–60 seconds accept one finished narration
with an empty `cues` list, or silence. The renderer assembles its silent video
chunks, then applies one global AAC-LC mux. Legacy `0.1` keeps the 30-second
audio limit. The engine uses the operator's authored scene and caption timings.
Provide those timings separately if precise semantic alignment matters. There
is no voice generation, transcription, or inference of scenes from speech.
Diagnostic assets are test signals.

Receive the finished take and keep its original. If a separate format conversion
is needed, write to a new file:

```sh
ffmpeg -nostdin -v error -i supplied.m4a -map 0:a:0 -vn -sn -dn \
  -c:a pcm_s16le -ar 48000 -ac 2 -n prepared.wav
PYTHONPATH=src .venv/bin/python tools/register_audio.py prepared.wav \
  --id my_narration --role narration --registry /persistent/private-audio
```

Use a private, operator-owned registry outside the repository. PCM16 sources may
be mono or stereo at 16/24/44.1/48 kHz. A narration can be at most 60 seconds and
11,585,536 bytes (the largest supported PCM16 payload plus 64 KiB RIFF overhead).
The registry pins the file hash and measured metadata. Project JSON references
the ID, with explicit linear gain. Keep the existing source unchanged.

Copy `examples/sprint-f/the_light_in_the_empty_town_narration_test.json` and
replace its test ID with `my_narration`. Author scene and caption timing as
needed. On this long route the default `start_frame` is 0. An authored offset
uses exactly 1,600 output samples per frame. With `trim_end_frame: null` the
take includes the final sub-frame source tail, subject to resampling. Shorter
recordings leave silence at the end. An overlong take or offset that would
truncate it is rejected. An intentional trim requires explicit frame bounds.
The renderer never adjusts playback speed.

Use `tools/cinematic_project.py --registry /persistent/private-audio` followed
by `validate INPUT`, `plan INPUT`, `inspect INPUT`, `preflight INPUT OUTPUT`,
`render INPUT OUTPUT`, then `verify OUTPUT`. Confirm the narration entry and
AAC clock in the reports before delivering `reel.mp4`. Keep both the
private recording and registry outside public exports. For a reproducible
synthetic test, run `tools/sprint_f_audio_fixture.py NEW.wav` and register it
as `f_timing_signal` using the same procedure.

Historical examples using test_wood_pulse/test_creek_signal need their separate
original fixture registry. Run `.venv/bin/python tools/cinematic_fixture_audio.py outputs/test-audio`,
then select it with `--registry outputs/test-audio` before the CLI subcommand.
See [CINEMATIC_PROJECTS.md](CINEMATIC_PROJECTS.md) for the original setup.

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
see [Sprint E1](SPRINT_E1_STAGING_RELIABILITY.md). Choose a user-controlled
durable output parent outside synchronized workspace paths and qualify its
retention, identity and ordinary-user access. The alternate review path stayed
clear only during bounded observation. The bounded optional engineering trace:

```sh
.venv/bin/python tools/trace_cinematic.py PROJECT.json OUTPUT TRACE.json --observe-seconds 2
```

Exit 3 means delayed recurrence detected even if the MP4 is valid. The observer
never deletes recreated names. The target VM and real offline-gallery browser
interaction must be qualified independently when those environments are available.
