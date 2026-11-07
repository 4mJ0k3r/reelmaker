# Sprint D7B progress

Started from verified published D7A `d6677e54bbf0307e0028f49ccf34f7a1b6668956`,
tree `6d7a174e5d1eb0dd6ebc28c7c711978a47af963a`. Local branch:
`sprint-d7b-original-cinematic-films`. No publication authorized from this host.

Checkpoint 1: The Answering Light is authored and rendered with the existing
0.2 engine: 900 frames, caption-free, registered diagnostic SFX only, no narration.
The complete decoded first/middle/last mobile storyboard was inspected.
Its package is under `outputs/d7b/the-answering-light`. Independent media
verification, resource figures and final review status are included in the
D7B recovery export. Before the Storm is authored; its render/review follows.

No engine, schema, registry, memory policy or historical phase was changed.
D8 staging diagnosis/deployment and D9 final acceptance remain outstanding.

Checkpoint 2: Before the Storm is rendered as 1,800 silent frames. The first
preview was corrected to remove partial partner cameos. Decoded review then
found a clipped Mira at the opening of Bram's return shot; the corrected
manifest uses two_shot/track. Original and corrected MP4s are preserved in
separate directories. Final: `outputs/d7b/before-the-storm-corrected/reel.mp4`.
Both complete decoded mobile storyboards were inspected; before/after frames
1440 and 1485 are included in the recovery packet.

Final independent media verification passed all 900/1,800 frames, exact PTS,
durations, streams, faststart, black-frame checks and silent chunk assembly.
Plan bytes and fresh-compile shuffled-order preview pixels match. Both
occupied-target renders refused without changing the MP4s. Active interaction
hand/socket error was at most 2.84e-14 logical units. The 30-second film uses
existing diagnostic SFX, not narration or a finished soundscape. Its AAC
verification passed, including gapless decoded clock and unchanged video PTS.

Focused native regression plus two final catalog cases: 131 passed in 11.07s.
An optional broader invocation returned 0 but emitted 395 pass markers without
a final pytest summary; it is preserved as incomplete evidence and is not
claimed as a full-suite pass. The earlier 66-test baseline overlaps the focused
run and must not be added to its count.

Final render wall/RSS: short 40.93s / 102.52 MiB; corrected long 104.42s /
108.39 MiB sampled tree peak. The original 256 MiB + 64 MiB policy was used.
Staging recurrence was observed again and recorded without arbitrary deletion.
Target VM not tested. D8/D9 remain open; stop for independent review.
