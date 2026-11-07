# D8–D9 baseline architecture audit (2026-11-07)

Baseline: branch `sprint-d7b-original-cinematic-films`, commit
`dc0b4a2f5e44536376ad0f9c7ca8704e46b85bce`, tree
`4190c1669a2d80f4e252b915f02be2f00dfb7f58`. Remote ref and clean local
checkout match. D7A and D1–D6 are ancestors. Ignored D7B media, exports and
native build SDK are preserved; no unrelated tracked changes were found.

## Existing operator path

`tools/cinematic_project.py` already exposes capabilities, schema, validate,
plan/inspect, frame, render and verify. Use this path; `run_reel.py` is an
older prompt/Yellow Mellow route with narrower capabilities. AGENTS.md must
be reconciled with the current structured operator guide during D9.3.
The engine does not interpret arbitrary scripts. The requesting agent authors
strict JSON choosing trusted actors, actions, worlds, audio and camera IDs.

The contracts support 1–20 fixed 90-frame shots; 0.1 retains original
sampling. 0.2 adds two performers, four-shot beats, facing, delays, signal
cues and bounded camera motions. Cuts do not drive acting clocks. Registered
interactions have fixed staging and cannot pair a second actor. An internal
`_coverage` resolver already handles auto wide/reaction/reveal/shared ending.
Extend this resolver, with opt-in fields; preserve requests without new fields.
No new brief contract or timeline rewrite is justified by this audit.

Audio is restricted to at most 900 frames (30 seconds), registered PCM16
WAV, global frame-aligned mix and verified stereo AAC. Longer 33–60 second
projects are silent, with sequential two-chunk verified stream-copy assembly.
The checked-in registry holds three diagnostic assets, not human narration.

## Production, resources and transactions

`render_project` creates private output and engine-work OwnedDirectory objects,
streams through the existing episode AV workflow, verifies black frames,
streams and storyboard, writes report/source/timeline, then atomically renames
with Linux renameat2 RENAME_NOREPLACE. Engine evidence is copied by allowlist.
`verify_project` independently checks source/timeline/video identity, every
decoded frame, exact PTS and silent chunk equality. It currently returns JSON
but does not persist `verification.json` inside the initial atomic package.

Strict memory admission uses observed MemAvailable and cgroup bounds: 256 MiB
job plus 64 MiB reserve. JobMonitor samples summed process-tree RSS at 10ms,
periodically resamples availability, and cancels on pressure/telemetry loss.
OOM counters are observed, not simulated; missing data is uncertainty. Storage
admission requires persistent output outside /tmp. No limit changes are planned.

OwnedDirectory retains an original fd/device/inode and refuses replaced paths.
Cleanup is fd-based; it never reconciles earlier-job prefixes and has no GC
finalizer. Publication checks parent/source identity and refuses occupied targets.
The CLI currently resolves destination parents; output-path/symlink validation
needs focused adversarial tests before exposing stronger operator guarantees.

Cancellation propagates a threading Event from CLI SIGTERM/SIGINT through
render/mix/verification; child supervision is in media.process and encoder.
No unrestricted concurrent render stress is warranted.

## Known risks and scope

D7B recorded removed/renamed staging paths later reappearing despite clean
transaction reports. No root cause is established. Trace original fd identity,
monotonic events, processes, immediate and delayed directory observations;
never delete foreign/replaced paths. An unresolved environmental recurrence
must remain a qualification blocker/limitation, not be hidden by prefix cleanup.
The current host is not the specified low-memory four-vCPU deployment VM.

D7B full-suite output ended without a final summary; 131 focused native tests
were confirmed. Historical tests cover contracts, clock continuity, foot/hand
contact, camera envelopes, six world moods, audio/encoder transactions and
ownership substitution. D8–D9 must add intent/pacing, preflight/CLI, output
security, persistent verification and fault/trace coverage, and capture complete
full regression results. CI has contracts, native and catalog jobs; add new
suites without a per-push 60-second render.

## Narrow implementation sequence

1. Extend 0.2 with finite opt-in shot intention and finite beat pacing; resolve
   cameras using existing `_coverage`, preserving historical semantics/digests.
2. Add explainable plan evidence and sampled camera/mobile metrics; reuse
   bounded sampling instead of a second director or renderer.
3. Extend existing CLI discovery and add preflight; keep render the primary
   production command. Add verification.json before atomic publication.
4. Instrument controlled ownership/process lifecycle and test native faults.
5. Document the full operator path and run fresh-input acceptance workflows,
   reusing approved D7B evidence where applicable.
6. Qualify host resources, review art/gallery, run security/regression/restore
   gates, and produce The Last Transmission through the documented CLI.

Catalog must remain 77 components with all historical records intact.
Artistic acceptance is independent reviewer assessment; tests cannot confer
studio quality or final production certification. No GitHub mutation is authorized.
