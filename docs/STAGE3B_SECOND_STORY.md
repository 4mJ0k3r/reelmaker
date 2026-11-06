# Stage 3B · The Empty Doorway

Rowan approaches a solitary barn along the Dusk Farm path. A dark shape
crosses the open doorway from right to left. Rowan recoils. The film
returns to the opening and holds on the empty recess.

`cinematic_farm_story("the_empty_doorway")` returns a deterministic,
standalone `episode-0.3` manifest. It uses Rowan Vale's approved
`notice_and_react` performance with the `surprised` reaction, the existing
farm geography and one opt-in variant, `barn_01:doorway_shadow`. The
renderer, encoder, episode schema, character registry and planner are
shared with the previous film.

## Edit

Ranges are inclusive. Each segment has an independent local clock.

| Segment | Global frames | Local frames | Picture |
|---|---:|---:|---|
| Arrival | 0–89 | 0–89 | Rowan and barn share one slowly tightening wide shot. |
| Movement | 90–111 | 0–21 | Match the camera and actor world origin as the approved walk begins. |
| Movement | 112–120 | 22–30 | Follow Rowan on the path toward the barn. |
| Movement | 121–124 | 31–34 | Cut to the doorway from the same side of the path. The recess is empty. |
| Movement | 125–145 | 35–55 | One clipped shadow traverses the doorway, entering from the right and leaving at the left. |
| Movement | 146–151 | 56–61 | The entrance is empty again. |
| Movement | 152–179 | 62–89 | The approved close reaction shows recognition, recoil and recovery. |
| Empty doorway | 180–269 | 0–89 | Return to the insert's camera, then ease closer and hold. |

The cut at 90 matches the opening camera, position and rightward facing.
The first scene uses the stationary Rowan recipe and the walk takes over
on the cut. The event insert excludes Rowan by framing while the approved
blocking continues underneath. The last shot uses the ordinary graded barn
at the same world transform. Its scene contains no moving actor.

The opt-in variant adds one graded contour to the barn's visible recess.
The inner aperture clips the shadow before it can touch the jambs or
threshold. The path is positioned by the existing scene-local timestamp.
At and outside local frames 34 and 56 the overlay emits no paths. The
default and dusk-graded variants retain their original artwork and caps.

## Reproduce

Use the existing Python 3.12, Cairo/Pycairo and FFmpeg environment from the
repository root. Choose a fresh render directory.

```bash
export PYTHONPATH=src
mkdir -p outputs/stage3b
python tools/stage3b_story.py outputs/stage3b/story.json
python tools/episode.py validate outputs/stage3b/story.json
python tools/episode.py render outputs/stage3b/story.json --output-dir outputs/stage3b/review
```

The output is a silent 720 × 1280 H.264/yuv420p MP4 at 30 fps, 270 frames.
The workflow uses one continuous encode under the 256 MiB process-tree
budget and 64 MiB admission reserve. The manifest holds the exact scene,
blocking, camera and variant selections. Its trusted recipe is fixed.
The planner has no new exposure, and the episode has no arbitrary event
scripts, extra characters or dynamic door mechanics.

[Decoded evidence](visual-evidence/stage3b/README.md) ·
[Engineering and artistic report](../Stage3B_Second_Cinematic_Story_Report.md)
