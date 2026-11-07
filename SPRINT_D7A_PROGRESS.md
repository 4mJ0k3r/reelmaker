# Sprint D7A progress

The clean D1–D6 checkout and existing full-history bundle were verified before
branching. D7A starts from commit `a8dedeedbf3f37b7829e75bf8acb1a41428bb2bd`
and tree `9ce39aff24b6a91fe28580eaf8452afddb6c5601` in the separate
`reelmaker-sprint-d7a` worktree on `sprint-d7a-cinematic-film-pilot`.

This checkpoint reserves a single caption-free 450-frame film, The Last Signal,
using the existing cinematic-project-0.2 contract. Render and review evidence
belongs under the ignored outputs directory until recovery export. D7B–D9 and
publication are outside this assignment.

The first authored manifest is `examples/sprint-d7a/the_last_signal.json`.
The story uses a solo approach, a paired signal beat and an editorial blackout
beat. The first render targets `outputs/d7a/first-pass`.

The accepted film is `outputs/d7a/final/reel.mp4`. The artistic pass reframed
Mira's reaction and held her alarm through the lamp blackout. Frames 90 and
360 intentionally start new authored beats. Frames 180 and 270 are cuts
within the paired beat. The report and decoded mobile storyboard describe
the final frames. The film is silent and caption-free.

Independent verification decoded all 450 frames with exact 30 fps timestamps,
720 × 1280 H.264/yuv420p, and zero flagged black frames. Two plan runs matched
byte for byte. No-clobber refused the occupied final destination. Focused tests
passed 64/64. Final render measured 24.21 s wall, 34.93 s CPU and 100.35 MiB
peak sampled process-tree RSS under the original 256 MiB budget and 64 MiB
reserve.

Both renderer transaction reports marked cleanup successful. Staging paths
later appeared again. Their exact paths and provenance are recorded in
`outputs/d7a/staging-audit.json`. The paths were isolated separately and the
active output root was checked clear. The historical recurrence remains open
for D8. Recovery packages include the audit and approved output files.
