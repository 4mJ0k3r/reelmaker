# Sprint F3–F4 progress

## Stage 0

Verified the published F1–F2 tip `6395bca82459ed82139f90558afac630daa20c7b`
and tree `4180dfe16b50a9ac95c99061fcdb1ff05b0d45f1` by read-only fetch.
The previous workspace held the Sprint E checkout, which is an ancestor.
The local branch is `sprint-f3-f4-cinematic-storytelling-quality`.
The baseline worktree was clean. The F1–F2 report, handoff and operator
guide were reviewed. The pre-change motion, acting, direction and camera
selection passed 26 tests on Python 3.12.

Decoded the integrated 60-second film and both F2 motion studies. The
forest repeats at frames 45/135. Frame 585 clips Bram at the right edge.
Frames 765/855 repeat the approach framing. At 1215 and 1645, a cropped
Bram distracts from Mira. The cart at 495 and parcel at 945 appear in
separate setups and require a legible editorial handoff. At 1529/1530
the small lamp competes with already lit windows. In the F2 studies the
stop at frame 68 and shoulder response around 188/205 are visible side
by side but subtle at phone size.

Keep the 20-shot grid and world sequence. Use admitted camera coverage
and a more legible rightward approach, then shorten visual repetition in
the wait. Test a reusable stationary recognition gesture with planted
feet and unchanged historical defaults. Preview the lamp in matching
off/on framing at frame 1530 before committing to a full render. Keep
the existing registered-audio path and supply only a synthetic timing
signal until a real private recording arrives.

## F3.1 motion

Added the opt-in `relief_recognize` stationary cue. Mira initiates the
gesture with a stronger arm lift and Bram answers on his own delayed
clock. The camera, horizontal root, foot contacts and settled endpoints
match the existing relief study. The existing `walk_to_settle` handles
the approach. The motion/operator selection passed 16 tests. Matching
camera motion clips are being produced from the same study, with silence
in both versions so the change is isolated.

## F3.2 geography and continuity

The derivative keeps all 20 shot boundaries. Wide views establish the
forest, creek bridge and village before cutting in to action. The ridge
travel remains right-facing. The cart crossing and village pickup are
separate editorial setups. The village pickup, place and dressed parcel
remain in the same world and mood, with Bram's follow-up anchor near
his interaction endpoint. Caption revisions name the route and distinguish
the cart crossing from the pickup. Early stills exposed edge crops, so
ridge coverage returns to the pair. The lamp coverage is refined next.

## F3.3 lamp

Existing object-reveal coverage enlarged the lamp but cropped Mira.
An explicit `signal_two_shot` camera balances both stationary actors and
the registered lamp, with shared focus and unchanged world lighting.
The matched camera holds at frames 1529/1530. Mira and Bram lift their
arms on separate authored clocks. The camera can only be selected for a
grounded paired signal cue. The caption still starts at 1530. The authored
plan validates, repeats byte for byte, and the F3 selection passed 40 tests.
Six historical plans and 36 sampled Cairo frames still match archived
digests. Catalog validation found 77 components and no generated drift.

## F4.1 operator worksheet

Added a private WAV, supplied script and authored timing worksheet with an
explicit 20-shot map and the admitted synthetic example. No human take was
supplied. Registration, preflight, production and verification continue
through the existing F1 audio path.

## F4.2 decoded correction

The first complete decode confirmed the 1,800 frames, 18 caption clocks,
lamp edge and sample clock. It also showed the lower caption band crossing
faces in the forest, creek, village and wait wides at frames 45, 405, 765
and 1305. Native preview confirmed the existing upper chapter layout
cleared those actors, so four caption styles changed. The timing, wording
and lamp reveal remain fixed. The only corrective full render uses a
fresh destination and preserves the first pass.

The full regression exposed stale gallery metadata for the additional
staged camera. Regenerated the JSON and embedded HTML metadata from
the current catalog and existing preview references. The camera list is
the only gallery change. The focused gallery retest passed 10 and the
corrected manifest, motion and operator retest passed 18.

## F4.3 acceptance

Reviewed the corrected 360×640 decode and actual original/refined
comparisons. The final MP4 contains 1,800 frames at exact 30 fps,
18 timed native captions, no detected black frames and one global
synthetic AAC stream. The original frame-1530 lamp and caption clocks
match. Its final video SHA-256 is `2f50f28a31af5a9280edb71eb1e70a466ef80dea70b2a1ed1cfd6d0162740cd2`.

The full local run executed 494 tests with 492
passing, two gallery metadata failures and zero skips. Both failures
passed in the targeted rerun after regenerating metadata. The
corrected benchmark passed 18 focused tests. Catalog 77 and zero
drift are confirmed. Nine historical or existing F1–F2 plans and
61 sampled frames match their references. The full and matching
motion study comparisons are exported with the native package.

Independent artistic acceptance, a user-supplied voice take and
low-memory target-VM qualification remain open. The historical
staging-name recurrence remains unattributed.
