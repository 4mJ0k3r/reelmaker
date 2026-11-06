# Stage 3A.1 editorial polish

The revised *The Other Light* uses the original Cold Ridge and Yellow Mellow
V2 in the same three 90-frame `episode-0.3` segments. Select
`the_other_light_refined` to reproduce this edit. The default
`the_other_light` still generates the Stage 3A manifest.

## Frame map

All ranges are inclusive and use the delivered film's 30 fps global frame
indices. The assets themselves use the scene-local frame clock.

| Frames | Beat |
| --- | --- |
| 0–27 | Traveler and warm beacon share the first composition. |
| 28–89 | The wider cut shows how they sit in the ridge geography and eases to the next shot's camera. |
| 90–111 | The traveler starts walking from the established position. |
| 112–146 | The camera follows the approach and braking. The beacon's white-gold surge occupies 134–146 and peaks at 140. |
| 147–179 | The original face and body performance takes over. The recoil is clearly visible at 166. |
| 180–203 | The cut holds the near beacon against a dark distant ridge. |
| 204–218 | A white-gold point rises from the ridge and reaches full intensity. |
| 219–269 | The outer bloom eases back. The point and near beacon remain in frame. |

The scene's idle traveler uses the original node, right-facing state, scale,
ground and starting coordinates. The camera at 89 matches frame 90 exactly.
The Stage 2C cameras, character performance and moving contact shadows are
reused through the middle. The beacon has returned to its ordinary amber
appearance before the last scene. Segment clocks remain independent.

Two registered, fixed-timing variants carry the events. `beacon_01:ridge_surge`
adds a single expanding ring, halo and brighter core over the established
amber lamp. `answer_light_01:ridge_reveal` contributes no geometry through
local frame 23, then fades in one distant core and a controlled bloom. It
holds the core at full intensity from local frame 38. Both are opt-in.
No new component IDs, user-scripted effects or episode fields are required.

## Reproduce

Use the existing supported Python 3.12, Cairo/Pycairo and FFmpeg setup from
the repository root. Choose a fresh render directory.

```bash
export PYTHONPATH=src
mkdir -p outputs/stage3a1
python tools/stage3a_story.py outputs/stage3a1/story.json --story the_other_light_refined
python tools/episode.py validate outputs/stage3a1/story.json
python tools/episode.py render outputs/stage3a1/story.json --output-dir outputs/stage3a1/review
```

The manifest contains the complete three-segment direction and asset
selection. The completed film is delivered separately for continuous playback.
See the [decoded comparisons](visual-evidence/stage3a1/README.md) and the
[editorial and engineering report](../Stage3A1_Editorial_And_Storytelling_Report.md).
