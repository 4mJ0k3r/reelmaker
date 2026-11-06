# Stage 1B review evidence

| Evidence | Scope |
| --- | --- |
| `rowan-farm-approach.mp4` in the complete download | Continuous 90-frame silent H.264 proof, 720 × 1280 at 30 FPS. The engine decoded and verified all 90 frames. The runner returned a staging-directory cleanup error after verification. |
| [Key frames](key-frames.jpg) | Frames 0, 36, 45, 51, 66 and 89 sampled from the encoded clip. |
| [Foot contacts](foot-contacts.jpg) | Crops from frames 36 and 51, with different planted feet and actor positions. |
| [Alternate layout sample](alternate-frame-51.jpg) | Mirrored walk with the left-bend track and relocated barn. |
| [Measurements](performance.json) | Static and animated workloads, exact source revisions, timing and strict memory observations. |
| [Stage 1A.1 establishing baseline](../stage1a1/farm-establishing.jpg) | Its original Cairo frame-36 hash matches the Stage 1B establishing render. See the report for comparisons in the other views. |

## Reproduce

From the repository root with the existing Cairo/FFmpeg stack:

```sh
export PYTHONPATH=src
mkdir -p outputs/stage1b
python - <<'PY'
import json
from reelforge.visual_library.composition.farm_motion import farm_walk
with open("outputs/stage1b/approach.json", "x") as handle:
    json.dump(farm_walk(moving_camera=True), handle, indent=2)
PY
python tools/blocking.py render outputs/stage1b/approach.json --output-dir outputs/stage1b/walk
python tools/stage1a_farm_stills.py outputs/stage1b/static-proof
```

Use fresh output paths. See the
[engineering report](../../../Stage1B_Motion_And_Performance_Report.md) for
the approved baselines, motion checks, profiling and remaining gates.
