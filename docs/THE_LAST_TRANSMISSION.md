# The Last Transmission — D9.5 operator demonstration

Source: `examples/sprint-d8-d9/the_last_transmission.json`.
Accepted refined plan SHA-256:
`6d954670512bd6ce11de3b9f08507dddfef52e9b1820b579bf72bb77c0806d44`.
Final MP4 SHA-256:
`eaaeff92563c90b205a3dec8ec5c525899c2224d68c603ca4a8e6c963690afd4`.

The 900-frame / 30-second film uses Scout and Mechanic, Abandoned Outpost in a
storm and Forest Ravine at night. The post flashes, dies, and another lamp
answers after a geographic cut. Registered intentions, independent timing
styles, explicit shared coverage and a visible frightened reaction are used.
The film is caption-free. Four existing registered diagnostic cues are accurately
labelled as synthetic signals; no human narration or generated artwork is used.

| Seconds | Visible direction |
| --- | --- |
| 0–3 | Establish the storm and Bram's attention |
| 3–6 | Mira arrives in shared tracked coverage |
| 6–9 | Bram's delayed reaction |
| 9–12 | Environmental wait beside the dead post |
| 12–15 | Practical light flashes; attention follows |
| 15–18 | Blackout and explicit Mira fear response |
| 18–21 | Establish the lower ravine path |
| 21–24 | Shared bank coverage |
| 24–27 | Bram waits beside the unlit lamp |
| 27–30 | Lamp answers; visual cliffhanger |

Production used the documented clean-checkout CLI with operator inputs and
trusted registry, not a custom renderer. The first pass is preserved; one
focused source-only refinement corrected partial partners and reaction focus.
Seven refinement commands include validate, plan, inspect, preflight, render,
verify and an occupied-target no-clobber refusal with unchanged MP4 hash.
The refined request plans identically in the clean checkout and development tree.
The clean operator checkout is 93fc500; later hardening is qualified by final
regression and a separate final restored-tree native smoke test. Do not present
this earlier operator checkout as the final Git SHA.

The final package contains project/timeline/report/verification/storyboard and
engine evidence. Independent verification decoded all 900 frames, H.264/yuv420p,
720×1280, exact 30/1 fps with rational PTS F/30, zero flagged black frames and
stereo 48 kHz AAC. AAC timing passed with -2 samples measured drift. Full raw
waveform/timing, CPU/RSS, cgroup/OOM and storage figures are supplied.

Measured wall: 71.24s. CPU: parent 36.31s + child user 62.14s + child system 2.61s.
Render-stage sampled tree peak was 103.32 MiB; the final independent verification
phase has its own monitor and a higher peak, so use the maximum across phases,
not only the render-stage figure. All phases retained the 256 MiB + 64 MiB policy.
The measurement is sampled RSS, not a hard OS limit or target-VM certification.

Exact repeatable primary command from the checkout root, choosing a new leaf:

```sh
mkdir -p outputs/operator
.venv/bin/python tools/cinematic_project.py preflight examples/sprint-d8-d9/the_last_transmission.json outputs/operator/transmission
.venv/bin/python tools/cinematic_project.py render examples/sprint-d8-d9/the_last_transmission.json outputs/operator/transmission
.venv/bin/python tools/cinematic_project.py verify outputs/operator/transmission
```

Artistic scores, remaining causal/acting limitations and actual before/after
review are in SPRINT_D9_ARTISTIC_REVIEW.md. Successful media verification does
not confer independent artistic acceptance or unconditional production readiness.
