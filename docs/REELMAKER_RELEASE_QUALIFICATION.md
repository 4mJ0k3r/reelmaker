# D9.6 release qualification — development-host evidence

**Recommended outcome B: engineering validation on the verified host, with
unresolved deployment/cleanup blockers.** This is a submission for independent
review, not final release authorization. Archive restoration and final smoke
results are recorded in the supplied engineering report and recovery handoff.

| Category | Result | Evidence / scope |
| --- | --- | --- |
| Structured project contracts | PASS | Historical 0.1/0.2 plans preserved; strict finite new selections and security cases |
| Character animation | PASS / LIMITATION | Registered rigs/transitions and planted contact tests; finite cutout acting |
| Two-character staging | PASS / LIMITATION | Independent clocks and swept lanes; no arbitrary physical choreography |
| Environment integration | PASS / LIMITATION | Four cinematic worlds and all 77 registered records preserved |
| Camera and pacing | PASS / LIMITATION | Deterministic finite intentions, shared/reveal coverage, three real timing maps; 90-frame grid retained |
| Audio workflow | PASS / LIMITATION | Pinned PCM16/WAV → verified stereo AAC through 30s; longer projects silent; demonstration uses diagnostic cues |
| Native rendering | PASS | CPU Cairo/FFmpeg, normal/fault/signal cases, current host |
| Media verification | PASS | Full decode, exact rational PTS, streams, faststart, black-frame criterion and chunk equality |
| Resource admission | PASS on host | Unchanged 256 MiB budget + 64 MiB reserve, strict observations; sampled RSS caveats retained |
| Cleanup and ownership | UNRESOLVED | Nested replacement and probe deletion protections pass; delayed old-name recurrence root cause remains open |
| Determinism | PASS / LIMITATION | Canonical plans and native random-access/frame proof; cross-native-stack H.264 bytes not promised |
| Operator workflow | PASS | Fresh-input scripted CLI simulation, correction, no-clobber, real pinned-WAV failure/restoration |
| Offline gallery | PASS static / NOT TESTED browser | 175 local references, 77 unchanged component records; no local browser runtime |
| Target low-memory VM | NOT TESTED | Development host has different CPU/RAM/tmp and runs as root |
| Historical regression | PASS | Complete 461-case sweep; post-hardening native/contract gates and all 462 final collected IDs covered |
| Artistic quality | REVIEWER ASSESSMENT PENDING | Submitter scores include 3s; suggested all-4 approval floor not met everywhere |

## Test accounting

A complete 461-case sweep passed with zero skips and a JUnit completion record.
The final probe-hardening substitution case was added after that sweep collected.
Post-hardening CI-equivalent runs pass: native 194/194, native-free contracts
120/120, catalog 100 passed + 2 skipped, 3 passed, and 52 passed + 1 skipped.
The three catalog skips are expected Cairo cases exercised in native work.
Passing JUnit IDs cover all 462 cases in the final collection; these counts
are overlapping selections and must not be added as unique test totals.
A final pure discovery/gallery correction passed 46 relevant tests.

The existing contracts/native/catalog workflow jobs are preserved and include
new suites. There is no new 60-second render on every push. The new branch is
unpublished: hosted CI is NOT RUN for it. The approved D7B baseline's hosted
run 42367722550 passed at dc0b4a2; that is not CI evidence for this branch.

## Blocking and deferred qualification

1. Recurrence: a successfully renamed stage name later returned as a new inode.
   No descendants were observed at producer return; the external creator is
   unidentified. Preserve unexpected paths, retain traces and monitor storage.
   Never adopt/reuse/delete old prefixes. This blocks unconditional unattended
   cleanup/deployment certification.
2. The real four-vCPU, low-MemAvailable, no-swap target VM and ordinary-user
   runtime there are unavailable. A roomier root host and cached-wheel clean
   installation do not establish target qualification or cold native building.
3. Offline browser interaction requires a real supported local browser and
   console/network inspection; static metadata checks are not that gate.
4. Independent artistic review is pending. Limited expressions, endpoint holds,
   fixed three-second rhythm and geographic/prop elisions remain visible.
5. The separate authenticated local agent must publish the exact approved
   commits and verify hosted CI later. No push, PR, merge or release occurred.

The two ownership fixes prevent specific destructive failure paths and have
regression evidence; they are not a claimed fix for external staging recurrence.
No critical failing test is hidden and no assertion/resource cap was weakened.
Final independent approval and deployment/release authorization remain with the user.
