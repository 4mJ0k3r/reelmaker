# D8–D9 progress

Starting approved commit: dc0b4a2f5e44536376ad0f9c7ca8704e46b85bce.
Starting tree: 4190c1669a2d80f4e252b915f02be2f00dfb7f58.
Branch: sprint-d8-d9-autonomous-production-hardening.

D8.0: baseline ref, clean checkout and approved ancestry verified; architecture
audit written. Existing ignored D7B evidence and native SDK preserved. Runtime
is being restored from the locked dependency set. No engine edits yet.
Next: confirm 77-component catalog, then implement finite opt-in direction and
pacing using existing 0.2 compilation/sampling paths. All D8.1–D9.6 gates remain
pending. Staging recurrence unresolved; target VM not tested. No publication.

D8.0 checkpoint: 3ccd8f2. Restored pinned Python 3.12/Cairo renderer environment;
77 components validate and catalog drift check passes.
D8.1: opt-in finite shot intentions extend existing auto coverage; deliberate
holds are explicit. Plan explanations and all-frame sampled camera/root metrics
are available without Cairo. Historical D7B plan digests remain unchanged.
Before/after native evidence remains scheduled with the D8.2 comparison pass.
Next: bounded pacing styles on independent performer clocks; no interaction
retiming or historical sampling changes.

D8.1 correction: first tests exposed a fixture retaining a paired-only cue
when removing its partner, and a repetition audit treating world-camera focus
as a composition difference even though the sampler ignores it. Corrected
fixture and canonicalized world-camera audit focus. 40 focused tests pass;
the initial 2-failure log is retained, not counted as a pass.

D8.2: opt-in measured/tense/urgent clocks now select finite anticipation and
rational clip speed independently per performer, with explicit partner override.
Transitions hold frame 89; ordinary clips hold the admitted twelve-second endpoint.
Interactions reject pacing rather than changing contact clocks. Historical
requests retain their clocks/digests. Initial tests found out-of-bounds accelerated
clocks and a fixture sampled before its own delay; corrected, with failed log
retained. Native short comparisons and full release gates follow.

D8.3: existing CLI now discovers resource/output/duration policy and five valid
operator examples. inspect adds actual all-frame camera/root diagnostics without
changing plan digest; preflight reuses the existing deployment doctor and audio
registry validation. Invalid CLI arguments and manifest failures are structured.
Output destination helper rejects traversal, symlink ancestors and occupied leaves.
Native-free planning and operator/example/diagnostic tests pass. No new brief
contract or duplicate production renderer was introduced.
Next: integrate safe destination checks and persistent verification into atomic
production, then instrument ownership/process faults.

D8.3 checkpoint: dc68dd0. D8.4: primary render command now applies destination
validation, checks parent identity, and independently verifies the private
package before writing verification.json and atomic publication. Report adds
input identity, output/audio format, whole-job CPU/wall and final-verifier RSS.
Native six-second operator production succeeded. 28 production/operator tests
pass, including injected final-verification failure and verification-before-
publication. Existing transaction assertions were retained; its fake engine
fixture mocks final verification rather than pretending its bytes are media.
Next: early recovery bundle, then bounded transaction/process lifecycle tracing
and controlled faults. Target deployment is still untested.

D8.4 checkpoint: a0d2a51; full-history D8.4 recovery bundle and status exported
and saved successfully before further development.
D8.5: bounded lifecycle tracing reproduced delayed old-name recurrence with a
different inode after successful publication and no observed live descendants.
Root cause remains unresolved; no foreign path was deleted by the observer.
A separate nested ownership-error cleanup defect was reproduced and corrected:
the outer work transaction now preserves its tree rather than deleting a
child's replacement content. Native first/middle/final frame, startup, nonzero
exit, cancellation, replacement and SIGTERM cases plus transaction tests pass.
See docs/SPRINT_D8_STAGING_INVESTIGATION.md and native traces for distinctions
between simulated boundary faults and real media-process faults. Next: host
resource qualification, fresh operator acceptance and versioned documentation.

D8.5 checkpoint: d6817ee. Native/transaction ownership fault set: 27 passed in
21.60s, including actual replacement preservation and active-encoder SIGTERM.
D8.6: host deployment doctor passes with unchanged memory policy. Actual CPU,
RAM and /tmp differ from target; root host run does not establish ordinary-user
or target-VM qualification. Seven sequential representative native results and
D7B comparison are documented in docs/SPRINT_D8_RESOURCE_QUALIFICATION.md.
Next: fresh-checkout operator acceptance (invalid correction, no-clobber,
controlled failure recovery), final current-interface 30s demonstration, then
full security/regression/gallery qualification and final archive.

D8.6 checkpoint: 10d1b85. Operator guide/quickstart and final task checkpoint:
93fc500. D9.1: clean cached-wheel install and three fresh input workflows passed
20 documented CLI invocations: 15s production, structured-invalid correction,
no-clobber hash preservation, registered-WAV failure/restoration with 30s AAC
production, and approved 60s full decode/chunk re-verification. No engine edits
were needed in the operator checkout. See operator acceptance and command log.
D9.2: decoded review found partial non-focal partners in arrival/wait/bank shots;
a single source-level coverage refinement is underway, preserving first media.
D9.3 docs/gallery are updated; browser interaction is NOT TESTED (no local
browser/Playwright). Static checks resolve 175 references and preserve all 77
historical component metadata records. Full regression/security/restore gates
and final qualification remain pending. No GitHub mutations.

D9.3: versioned operator guide 1.0 and weak-agent quickstart are linked from the
offline gallery; all 77 component preview records are preserved and 175 local
references resolve. Real browser interaction remains NOT TESTED, with explicit
follow-up procedure. D9.4 CI selections now include direction, pacing, operator,
trace, native-fault and security suites; no per-push 60s render is added.
An oversized security-test parameter initially exceeded the OS environment
argument limit before reaching the CLI. A short explicit pytest case ID fixes
the harness without relaxing the 1 MiB input test. Its failed raw log is retained
compressed; 37 security/direction/operator cases pass after correction.

D9.2: the single focused final-demo refinement is fully encoded/verified and
no-clobber checked through the clean operator CLI (seven additional commands).
All final decoded mobile shot rows were inspected. Shared arrival/bank views,
environmental wait and explicit Mira blackout focus fix actual cropped-partner
and reaction-readability defects. Discovery/pacing examples received matching
source-only coverage corrections. Actual encoded before/after sheets are saved.
Finite direction now varies redundant same-beat wides and same-subject reactions;
explicit holds and authored repetition remain supported. Submitter rubric scores
include 3s for motion, facial range, rhythm, clarity/coherence and polish; final
artistic approval is pending, not inferred from tests. No rig redesign.

D9.4 security hardening: source inspection identified the legacy workspace
write probe's unconditional pathname unlink. It now retains its original fd
through removal, compares device/inode, and preserves a replacement with
WORKSPACE_IDENTITY. The new real-fsync substitution test plus operator/security
selection passes (28 cases). No numeric/security/resource assertion was weakened.
The full-suite capture is being completed with JUnit evidence; final qualification
will use the post-hardening source and a fresh-tree native smoke check.

D9.5: The Last Transmission final operator demonstration is complete: 900 decoded
frames, 720×1280/30 fps H.264/yuv420p, registered stereo AAC, exact rational PTS,
zero flagged black frames, independent package verification and no-clobber pass.
Final video eaaeff92563c90b205a3dec8ec5c525899c2224d68c603ca4a8e6c963690afd4.
Recorded wall 71.24s; CPU 36.31 + 62.14 + 2.61s; render and final-verifier RSS
are reported separately and qualification uses their maximum. The clean
operator run was at 93fc500; final-source restoration/smoke remains a separate
gate. No 60s narration, human voice or studio-quality claim is made.

Release gate results: complete 461-test sweep passed, zero skipped, with JUnit
completion. After the narrow probe fix, native CI-equivalent selection passed
194/194 and native-free contracts 120/120; catalog job selections passed with
three expected Cairo skips. Passing JUnit IDs cover all 462 currently collected
cases; these overlapping counts are not summed. Catalog remains 77 with no drift.
A final discovery correction adds an explicit recommended 0.2 contract while
preserving the legacy contract field, exposes staged cameras in the gallery,
and links original diagnostic fixture setup. Related metadata/operator/direction
checks pass; final exports will use the current discovery output.

Final qualification: outcome B is recommended — host engineering validated,
cleanup/deployment blockers explicit. The tracked qualification table covers
all required categories. Staging root cause remains unresolved; target VM and
real browser are NOT TESTED; artistic acceptance remains independent/pending.
Complete passing evidence covers all 462 final collected test IDs without
summing overlapping runs. New branch hosted CI is NOT RUN because no publication
is authorized. Latest code/discovery checkpoint: 70097f2; final documentation
and identity are captured in the review packet.
Next exact action: create full-history final bundle, restore it fresh, install
locked runtime, compare plan/native frame proof, run short native operator smoke,
verify archive checksums, and save complete report/ZIP/bundle/handoff. These
post-commit results and exact final SHA/tree belong in the external identity
report and handoff rather than a self-referential commit hash in this file.
