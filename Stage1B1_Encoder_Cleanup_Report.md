# Stage 1B.1 encoder cleanup report

Approved baseline `7a3cc73655deeacad67c194feb3cedb5c8daeb44` on
`stage1b-world-kit-motion-performance`. The local tracked tree matched
`12ad9806b0da4b3d05878804aa800a8ca4ee4bbf`. Correction branch
`stage1b1-encoder-cleanup-fix`.

## Diagnosis

The original 90-frame run verified its published media, then the later
`confirm_cleanup()` reported `TRANSACTION_CLEANUP` for
`.reelforge-encode-bdc7fqe4`. The original call to `cleanup()` had returned
successfully, which in that implementation requires successful `rmdir`
and an immediate absence check. The later check therefore found a path
that had reappeared after that absence check. Encoder finalization had
already reaped FFmpeg and drained its stderr. The verification processes
receive only the published MP4 pathname.

Read-only inspection found a 262,192-byte `pending.mp4` in the reappeared
directory, versus 752,901 bytes for the final MP4. Their inodes differed.
The original staging directory identity was not captured in the failed
run, so the later directory cannot be identified as the owned inode.
The component or process that restored or recreated the path was not
identified. The repository already documents a similar host symptom in
[AUDIO_SYNC.md](docs/AUDIO_SYNC.md). That history does not establish the
identity of the writer in this run.

An instrumented six-frame baseline run recorded staging directory identity
`(device 27, inode 532072)` at `.reelforge-encode-t0z8n4a3` before
finalization. Immediately after cleanup it was absent, FFmpeg had status
0, and the stderr reader was no longer alive. The path stayed absent
before and after both ffprobe and the decode FFmpeg subprocess and during
confirmation. That smaller run did not naturally reproduce restoration.

Deterministic fault injection reproduced the old gap by recreating the
path after cleanup and before confirmation. The assertion rejected it
and preserved the foreign contents. A second injection substituted a
directory during verification under the new ordering. Cleanup rejected
the changed inode and the scene report stayed unsuccessful. The confirmed
software defect was releasing the staging owner before the job's
remaining native verification work. The external cause of path
reappearance remains unresolved.

## Correction

- `src/reelforge/media/encoder.py` lets an existing encoder caller supply
  a verification callback to `finish()`. After no-clobber publication
  and encoder reaping, the scene verifier runs while the original staging
  descriptor is still held. The encoder releases it in its existing
  cleanup path even if verification fails.
- `src/reelforge/core/transaction.py` distinguishes confirmation from
  deletion. Confirmation requires that cleanup ran and preserves its
  original error. One `lstat` detects files, directories and dangling
  links. Access errors fail explicitly.
- `tools/scene.py` orders full verification before cleanup, confirms
  absence after its strict monitor exits and retains a separate failure
  report if verified media survived a cleanup error.
- `tests/test_encoder_cleanup.py` adds deterministic faults and short
  native success/failure fixtures. The existing GitHub catalog workflow
  runs the native-free cases.

Existing `finish()` calls with no callback keep their behavior. Borrowed
staging remains the external job owner's responsibility. Atomic hard-link
publication, identity checks, FD-relative file removal, cancellation,
process waits, log bounds, memory admission, artwork, and animation remain
unchanged. The fix does not reacquire a directory, retry deletion, or
ignore an unexpected pathname. A true replacement remains a failure.

## Tests

With `PYTHONPATH=src`, the focused Cairo run covered
`tests/test_encoder_cleanup.py`, `tests/test_stage1b_farm_motion.py`,
`tests/test_visual_catalog.py`, `tests/test_stage1a_world_kit.py`, and
the existing 15-second planning-only test. It ran with
`--basetemp outputs/stage1b1/pytest-focused` and passed **47 tests**.
The two planner no-clobber tests and the snowy-mountain regression suite
passed **26 tests**. Without Cairo, the cleanup, motion, World Kit and
catalog suites passed **44 tests**, with two native smoke tests skipped.

Fault cases include pending child startup failure, early exit, incomplete
input, cancellation, verification failure, directory and symlink
substitution, unknown content, late recreation and a competing final
filename. Both catalog validation and generation checks passed for all
48 entries. Ruff and the staged whitespace check passed. A hosted CI
result was unavailable at commit time.

## Full render

Used the unchanged Stage 1B farm-walk manifest via the
[standard blocking command](docs/visual-evidence/stage1b1/README.md).
The CLI returned **0**. The detailed scene report records
`success: true` and `cleanup_error: null`. Post-verification confirmation
succeeded and inspection found no staging directory. No-clobber rejected
the second request with exit 1 and `OUTPUT_EXISTS`, leaving the SHA-256
unchanged.

| Field | Result |
| --- | --- |
| Video | H.264/yuv420p, 720 × 1280, 30 FPS, 3.000 s, one video stream and no audio |
| Full decode | 90 of 90 frames, all distinct |
| Compatibility | All 90 source and decoded hashes and the complete MP4 bytes match Stage 1B |
| Blocking wall time | 4.972 s |
| Geometry / Cairo raster / pipe writes | 0.999 s / 2.320 s / 0.278 s |
| Elapsed through encoder publication | 3.900 s |
| Full verification | 1.054 s |
| Peak process-tree RSS | 97.92 MiB under the unchanged 256 MiB budget and 64 MiB reserve |
| Monitoring | Strict, no cancellation or changed OOM counters |
| Resource release | Encoder reaped, no live Cairo surfaces or surface bytes |

Host was Ubuntu 24.04.3 LTS, AMD EPYC 9V74, eight-vCPU quota, 8 GiB
cgroup memory limit, Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0 and
FFmpeg 6.1.1. See [compact verification](docs/visual-evidence/stage1b1/render-verification.json)
for exact measurements.

## Remaining limits

The verified run and injected faults support independent release-gate review
of this correction. One successful render cannot rule out intermittent
external restoration after cleanup. The writer of the original reappeared
path remains unknown, and the 0.4–1 GiB target host was unavailable. All
five World Kit assets retain their candidate status.
