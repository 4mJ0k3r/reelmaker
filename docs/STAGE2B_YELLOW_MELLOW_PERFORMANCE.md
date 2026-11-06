# Yellow Mellow investigates a signal

Use `yellow_mellow_v2` with this selector at the top level of `blocking-0.2` or inside the existing `rowan` actor object in `storyboard-0.1`.

```json
"character": "yellow_mellow_v2",
"performance": {"name": "investigate_and_react", "reaction": "surprised"}
```

The selector has one reaction choice. It uses native Yellow Mellow gaze, face contours, `look` and `head_tilt` targets, keyed pose interpolation, walk and stop planning, and a clip-scheduled blink. The continuous curve is character-specific. Rowan's `notice_and_react` uses his own rig and remains separately selectable.

- Author one or more contiguous `walk` segments from frame 0, a `stop`, then a single terminal `idle` starting between frames 45 and 54. The timeline is 90 frames at 30 FPS. The authored performance supplies expression and acting during this route. Segment expressions still validate against the registered V2 vocabulary.
- Stage a point of interest ahead of the fixed facing, left or right. The eyes lead a small tilt, the near hand investigates, then the face leads the recoil. The hand releases into a planted, attentive hold. The only blink begins 27 frames after stopping. Gaze is local and mirrors with the actor.
- Use a `level_field` supporting ground with matched actor and terrain depth. No static character decal belongs under this route. The actor transform multiplies the existing V2 episode draw scale (95/142.5). The proof uses 0.64 × 95/142.5, or about 60.8 logical units of nominal standing height before camera projection.
- Route x remains the validated world position. The V2 gait now uses that same displacement for this selector. Placement subtracts route displacement once and keeps local pelvis weight shifts. The existing shadow drawer follows the same solved feet.
- This preset covers a horizontal walk and planted investigation. Running, turns inside the route, slope traversal, target tracking, prop contact and arbitrary pose channels are outside its scope. Existing V2 actions remain available through their previous interfaces. The one-command prompt planner keeps its existing vocabulary.
- Existing resource limits remain 256 MiB for the process tree plus a 64 MiB admission reserve. The per-performance primary-state cache remains at 48 entries.

## Reproduce

Use the repository's Python 3.12, Cairo/Pycairo and FFmpeg setup, plus Pillow for evidence sheets. Run from the repository root with fresh destinations.

```bash
mkdir -p outputs/stage2b
export PYTHONPATH=src
python - <<'PY'
import json
from pathlib import Path
from reelforge.visual_library.composition.mellow_approach import mellow_storyboard

Path("outputs/stage2b/ridge-medium.json").write_text(
    json.dumps(mellow_storyboard("cold_ridge", "medium"), indent=2) + "\n"
)
PY
python tools/storyboard.py validate outputs/stage2b/ridge-medium.json
python tools/storyboard.py render outputs/stage2b/ridge-medium.json --output-dir outputs/stage2b/ridge-clip
python tools/stage2b_mellow_evidence.py outputs/stage2b/evidence
```

The sample builder also accepts `"farm"`, `"establishing"` and `legacy=True` for the matched comparison. See the [review evidence](visual-evidence/stage2b/README.md).
