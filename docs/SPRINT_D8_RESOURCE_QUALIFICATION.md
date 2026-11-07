# D8 host resource qualification

Host diagnostics passed on the development host: Ubuntu 24.04 x86_64, Python
3.12.14, Pycairo 1.29.2, Cairo 1.18.0, FFmpeg/libx264 and ffprobe. Exact native
versions, CPU quota, cgroup topology/limits/OOM counters, memory, persistent
storage and /tmp are recorded in outputs/d8-d9/host-preflight.json.

This is NOT the intended target VM. Observed CPU quota is eight cores, affinity
nine, host RAM about ten GiB, no swap, and /tmp shares roughly 63 GiB storage.
The run is root. Target four-vCPU/0.4–1.0 GiB-available/no-swap/~512 MiB /tmp,
and ordinary-user operation there, remain NOT TESTED. No affinity trick,
simulated cap, missing-telemetry inference or memory override is certification.

Sequential native host cases completed:

| Case | Frames | Wall seconds | Sampled tree peak MiB |
| --- | --- | --- | --- |
| Repetitive authored coverage baseline | 360 | 21.50 | 100.58 |
| Intention-directed discovery | 360 | 19.58 | 100.64 |
| Measured pacing | 180 | 10.03 | 100.55 |
| Tense pacing | 180 | 11.08 | 100.54 |
| Urgent pacing | 180 | 10.16 | 100.48 |
| Operator atomic verification package | 180 | 13.53 | 100.66 |
| Traced operator production | 180 | 13.23 | 100.55 |

The package/trace cases include the new final independent package verification;
earlier comparison cases were produced before that additive package check.
This accounts for extra wall time without claiming a backend slowdown or speedup.
D7B approved evidence remains 900/1800 final frames, 40.93/104.42s and
102.52/108.39 MiB on the earlier pipeline. D9 acceptance records current
15/30-second operator measurements and re-verifies approved long media rather
than repeatedly rendering the same 60-second film.

All jobs retained 256 MiB process-tree budget + 64 MiB reserve. Samples can miss
transient peaks and double-count shared pages. Cgroup counters are a shared
host observation, not a delegated per-job hard limit. Raw reports include CPU,
initial/final OOM counts, sampled logical storage/space, and child return codes;
only observable unchanged counters support a no-observed-OOM statement.

Invalid input, occupied destination, native first/middle/final-frame failure,
startup/nonzero exit, cancellation, SIGTERM and stage-replacement cases have
specific tests/traces. The corrected ownership uncertainty path preserves
forensic work rather than deleting foreign replacement content. Delayed
old-name staging recurrence remains an unresolved cleanup qualification limit.
Host media success is suitable development evidence, not production certification.
