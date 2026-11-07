# ReelMaker Sprint F1–F2 engineering report

The local branch is `sprint-f1-f2-narration-and-motion`. The approved E1–E6
baseline is commit `a6cb1d57b67b681207989a7db43014a787f81f47` with tree
`34b7878074a6b15e562bccba97607a2c6695e45b`. The final identity and all
checkpoint SHAs are in the exported identity section and `GIT_IDENTITY.json`.
No remote refs were changed. No new WAV or MP4 was committed.

## F1 architecture and workflow

A staged 33–60-second cinematic project accepts one registered narration
and an empty SFX list, or silent output. The shared legacy and short routes
keep their previous frame limits and published defaults. The visual pipeline
renders sequential silent slices, verifies each slice and their assembled
decoded sequence, then stream-copies the complete H.264 video during one
AAC-LC mux. The global narration passes through the existing mixer and
supervised FFmpeg processes. It remains in a private owned workspace through
verification and is cleaned up before atomic publication.

Registration accepts a finished mono or stereo PCM16 WAV at 16, 24, 44.1 or
48 kHz. The 60-second input cap is 11,585,536 bytes including a 64 KiB RIFF
allowance above the largest admitted PCM payload. An external private registry
is selected by the operator. The project names only the registered ID. The
registry checks WAV framing, size, codec, metadata, complete decode and SHA-256.
The long route mixes from that validated private snapshot. Both source and
snapshot hashes, sample rate, channels, count, offset and padding are reported.
The operator guide documents a separate no-overwrite FFmpeg conversion for
other recording formats.

The authored 30 fps grid maps to 1,600 samples per frame. A missing long-form
start defaults to zero. Explicit starts and trims use frame indices. A null
end preserves the take through its final sub-frame tail after resampling.
Silence fills unused intervals. Overflow is rejected unless the operator
supplies a valid intentional trim. There is no speed or pitch alteration.
Authored scene and caption timings control alignment. Word-level alignment
requires external timing data. The engine creates no speech.

The narration storage preflight for the 60-second job required 328,214,528
free bytes. Its allowance accounts for two 900-frame silent chunks, the
silent concat and final mux, the private WAV and two stereo float PCM files,
and disk reserve. Rendering stayed under the original 256 MiB process-tree
budget and 64 MiB admission reserve. The workspace was chosen outside the
synchronized path. No owned staging paths were visible at the post-run check.

## F1 60-second audiovisual checkpoint

The film uses the approved `The Light in the Empty Town` manifest with a
registered deterministic timing signal. **No real narration was supplied.**
The original storyboard, motion choices and all 18 burned-in captions are
preserved. Every decoded frame matches the approved silent film. The checkpoint isolates the audio change before the motion work.

| Check | Result |
| --- | --- |
| Final video | 1,800 frames, 720×1280, 30 fps exact, H.264/yuv420p |
| Independent stream check | 60.000 s, one H.264 stream and one AAC-LC 48 kHz stereo stream |
| Chunks | Two video-only 900-frame chunks. Verified decoded frame identity across concat and mux. |
| Sample clock | Start tick 0. Exact contiguous decoded AAC ticks. 2,880,000 presentation samples per channel. |
| Codec tail | 512 terminal samples outside the presentation interval |
| Audible timing | Zero measured onset-to-end drift. The AAC audible comparison uses a one-packet tolerance. |
| Frame-900 seam | Sample 1,440,000. Correlation above 0.999998 per channel over a 4,096-sample window across the boundary. |
| Source pin | Source and private WAV snapshot SHA-256 match. |
| H.264 mux | Stream-copy digest and exact video PTS unchanged. |
| Timing and memory | 175.00 s for render and in-job verification. 125.41 MiB peak sampled process-tree RSS including verification. |
| Output ownership | Published once. Occupied-output retry returned `OUTPUT_EXISTS` with the MP4 hash unchanged. |

The sample-clock and waveform checks measure timing and content agreement.
AAC is lossy. These checks do not establish subjective playback quality.

## F3 combined acceptance

F3 changes only the first forest walk-to-stop action to `walk_to_settle`
and the final relief cue to `relief_settle`. It keeps the approved scene
structure, cameras, signal timing and all 18 caption intervals. The exported
`audiovisual-package/project.json` is the exact integrated request.

The integrated film verified at 1,800 frames with two silent 900-frame
chunks, exact video PTS and one AAC-LC stereo stream at 48 kHz. The audio
bitstream and exact 2,880,000-sample presentation clock match F1. The
approved subtitle masks matched across all 1,800 decoded frames with a
minimum intersection-over-union of 0.9989.
The integrated render and in-job verification took 185.67 s.
Peak sampled process-tree RSS was 125.37 MiB.
No owned staging directories remained at the post-run inspection. The
occupied-output retry left the MP4 hash unchanged.

## F2 motion and compatibility

`walk_to_settle` adds a short downward weight transfer and upper-body follow
through the final step. Tests confirm the same horizontal root, exact foot
targets, same transition endpoints and no change to camera framing. The
`alert_settle` and `relief_settle` variants add a brief listening posture
and actor-specific shoulder and torso response. Independent authored delays
still apply. Both feet stay planted and response clocks continue across cuts.

The two 12-second studies use matching camera motion, background and
byte-identical synthetic AAC. At frame 68 the new stop has a small knee and
torso compression. Around frame 150 the characters lean into the wait. Mira
recoils first and Bram's shoulders respond later. By frame 300 the two cuts
are settled into the same hold. The motion changes are modest at mobile
scale. The stride length, facial rig and overall art style are unchanged.
Six historical plan and sampled-frame digests match the E evidence exactly.
The catalog still validates all 77 components with no drift.

## Tests and deployment disposition

The pre-change baseline selection passed 60 tests. The F1 focused selection
passed 46 and the F2 selection passed 42. These selections overlap the
complete suite and each other. New coverage includes mono and stereo at the
60-second limit, non-grid tails, offsets and silence, clock and stream copy,
bad registry metadata and media, occupied output, injected mixing and muxing
cancellation, FFmpeg and verifier failure, and preservation of foreign paths.
The native 60-second mono probe resampled 16 kHz mono to 48 kHz stereo. Its
presentation clock was exact and the source audio fit without trimming.

The complete local Python 3.12 regression suite passed **491 tests** with zero failures, errors or skips. See the archived JUnit report.

Development-host acceptance passed for the demonstrated workflows. The
actual constrained target VM and ordinary-user qualification remain open.
The historical workspace staging recurrence remains unattributed. This work
does not certify unattended production.
