# reel-production-0.1 (Sprint J P0)

This is a bounded data orchestration contract, not arbitrary language interpretation.
Use `python tools/reel_production.py schema` for the strict machine-readable schema.

## Inputs

Required fields: schema_version, id, title, backend, script, duration_seconds,
tail_policy, allow_trim, narration, events, subtitles, cinematic. Unknown keys fail.
Scripts are approved UTF-8 text plus SHA-256; scripts never execute. Titles are ASCII.
No data-selected file paths, URLs, modules, source snippets or shaders are evaluated.
Registry and output locations are operator arguments. Manifest loading is bounded to 1 MiB.
Existing JSON depth, duplicate-key and finite-number admission remains in force.

Director backend: one world/mood per event and explicit ordered shot recipes. Each
shot selects a registered preset/style/variant/weather combination. The adapter
calls the unchanged Director V3 builder/dressing functions and keeps Yellow Mellow
reference_slim, camera and native storyboard sampling. Labels do not infer actions.
Required assets must be staged within their event, forbidden assets must not be
staged in any shot of that event. Scene presence is not pixel/readability proof.
Parcel observation is not pickup; ridge running is horizontal. No mixed backends.

Cinematic backend: embed a validated cinematic-project-0.2 document with audio:null
and captions:[]; its existing beat IDs/ranges must match the unified event mapping.
Existing actors/partners/interaction clocks remain unchanged. This cannot substitute
Yellow Mellow for Scout/Mechanic. Unified narration/captions are authored at top level.

## Time

Durations: 6..60 seconds in steps of 3. Every visual cut remains 90 frames.
Timestamp syntax: unsigned decimal seconds as JSON strings, up to nine decimals.
Convert using Decimal * 30 and ROUND_HALF_UP; half-open frame spans [start,end).
Plans retain original event/subtitle timestamps, converted frames, signed error and
maximum absolute error. Non-grid event edges return TIMING_CONFLICT with nearest
legal suggestions and signed frame errors; the compiler NEVER applies suggestions.
Events must cover the film without gaps/overlaps. Subtitle spans may lie between cuts.
Narration offset/trim timestamps use the same conversion; audio uses 1600 samples
per frame at 48 kHz. Full untrimmed source tail survives short as well as long reels.
No speech speed/pitch/normalization/denoising/transcription/generation is performed.

## Narration and subtitles

Narration is null (explicit silence) or asset_id/sha256/start/trim_start/trim_end/gain/
provenance. Provenance is user_finished_recording or synthetic_timing_fixture.
One trusted PCM16 WAV in an operator-owned private registry. Metadata is checked
cheaply in plans; complete WAV/hash/decoder checks and a private immutable snapshot
are mandatory before visuals. Recordings are <=60s; accepted rates 16/24/44.1/48kHz,
mono/stereo. Narration gain is EXPLICIT in 0.05..0.8 (use 0.8 for historical policy).
Unity gain is rejected, not silently attenuated; support remains unqualified/deferred.
Default trim is disabled: allow_trim:false, trim_start:"0", trim_end:null.
Overlong recording/offset fails; pad_silence permits reported trailing silence;
exact demands zero trailing padding samples. No implicit truncation.

Subtitles are English ASCII only: at most 24 cues, up to two mobile-safe 32-character
lines each. Unique IDs, sorted non-overlapping spans. Hindi is rejected explicitly.
Hindi shaping, 120s limits and word highlighting are NOT implemented or advertised.

## Output and trust

Output must be a new leaf beneath an existing persistent non-symlink parent outside
/tmp. Existing ownership, sequential encoding, resource admission and cancellation
rules apply. Memory policy remains strict: 256 MiB budget +64 MiB reserve; no bypass.
One silent visual assembly, one global AAC mux (video stream copy). Verification
recompiles request, compares plans/media identities, full-decodes source/final/chunks,
checks rational PTS, bitstream identity, AAC sample clock, independent waveform proof,
black-frame criteria and resource observability before atomic package publication.

Local package includes request.json (private text), plan.json, report.json,
verification.json, private_inventory.json (hashes/metadata, no raw source audio),
engine evidence, decoded storyboards, reel.mp4, and Director asset audit when supported.
Treat the complete local package as private. Do not publicly export real scripts,
narration or private assets. The Sprint J review archive contains synthetic examples
only. Pixel audit describes sampled source frames before subtitles/encoding.

Identical data/pinned runtime produce identical plans/source frames. MP4 bytes are
not claimed portable across FFmpeg/font/Cairo versions. Media identity is not artistic
or subjective narration alignment acceptance. Deployment qualification is separate.
