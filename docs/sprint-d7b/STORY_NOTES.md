# Sprint D7B: original films

Both films use cinematic-project-0.2, CPU Cairo, 720 x 1280, 30 fps and the
published D7A engine unchanged. They have no captions. Story descriptions
are editorial intent; the supplied contact sheets and MP4s are the evidence
for independent artistic review. No deployment or final release is claimed.

## The Answering Light — 30 seconds

Mira reaches a dark ravine lamp at night. It gives her no answer. She takes
the upper path to the rainbound outpost, where Bram is still waiting. They
recognize one another; the post lamp comes on and they stay together.

| Seconds | Direction | Visible story beat |
| --- | --- | --- |
| 0–6 | Ravine wide, then tracking medium | Mira walks, stops and searches |
| 6–9 | Held lamp insert | The lamp is dark |
| 9–12 | Follow | Mira chooses to continue |
| 12–15 | New geographic wide | The road reaches a stormy outpost |
| 15–21 | Reverse reactions | Bram notices Mira; she sees him |
| 21–24 | Held lamp insert | The post answers with light |
| 24–30 | Shared coverage | Both look at the lamp, then relax |

Audio uses the existing registered diagnostic `diag_suspense` and
`diag_fence` files, at low gain, at frames 180 and 630. These are synthetic
test cues used as a restrained electronic pulse, not human narration,
recorded environmental sound, or a finished production soundscape. No new
audio is generated. The visible story must also work muted.

## Before the Storm — 60 seconds, silent

Mira and Bram leave the ravine together in morning light. Incoming mist
makes them choose separate routes. Bram pushes the supply cart across the
woodland bridge while Mira takes the upper path to the outpost. She waits
in rain beside a dead lamp. Bram makes the village supply drop, then returns.
The post lights as he arrives. Sunset replaces the storm; both are safe.

| Seconds | Direction | Visible story beat |
| --- | --- | --- |
| 0–12 | Wide, shared, then reverse reactions | Together at dawn; notice mist |
| 12–18 | Cart medium and hand/wheel detail | Bram takes supplies across creek |
| 18–24 | Ravine wide and follow | Mira takes the upper path |
| 24–36 | Outpost arrival, lamp and reaction | Rain arrives; Mira waits alone |
| 36–45 | Village pickup/place and prop reveal | Bram completes the drop |
| 45–48 | Reaction | Mira fears he will not return |
| 48–54 | Bram arrival, lamp insert | Reunion and returning light |
| 54–60 | Shared sunset frames | Both home after the storm |

The cart and parcel use different registered props. The cut from creek to
village elides the transfer; no unloading action or continuous geography is
claimed. The final change to sunset is a time ellipsis. Each new beat is
explicit authored blocking; only cuts within one beat share an acting clock.
The 900-frame chunk join falls inside Mira's outpost waiting sequence.

## Reproduce

Use Python 3.12 and the locked renderer extra (`uv sync --frozen --extra renderer`).
Do not overwrite a delivered directory. From the repository root:

```sh
.venv/bin/python tools/cinematic_project.py validate examples/sprint-d7b/the_answering_light.json
.venv/bin/python tools/cinematic_project.py render examples/sprint-d7b/the_answering_light.json outputs/d7b-new-30
.venv/bin/python tools/cinematic_project.py verify outputs/d7b-new-30
.venv/bin/python tools/cinematic_project.py validate examples/sprint-d7b/before_the_storm.json
.venv/bin/python tools/cinematic_project.py render examples/sprint-d7b/before_the_storm.json outputs/d7b-new-60
.venv/bin/python tools/cinematic_project.py verify outputs/d7b-new-60
```

Run sequentially under the unchanged 256 MiB budget plus 64 MiB reserve.
The 60-second route is silent and uses two verified chunks. Inspect the
first/middle/last decoded frame of every shot in the delivered mobile sheets.
D8 retains ownership of staging recurrence and actual target VM qualification.
D9 retains final independent engineering/artistic acceptance.
