# Stage 1B.1 evidence

[Render verification](render-verification.json) records the full decode,
output identity comparison, cleanup and no-clobber outcomes. The MP4 is
provided separately for review. Its SHA-256 is
`e6c876b180aed19b96220d45efa433ac6437d157cf89ad087fe6dd177e3eecfc`.

The Stage 1B key frames and contact sheets remain representative because all
90 source and decoded frames and the complete encoded file matched.

## Reproduce

Use Python 3.12 with Cairo and FFmpeg. Run from the repository root and choose
fresh output paths under the workspace.

```sh
export PYTHONPATH=src
mkdir -p outputs/stage1b1
python - <<'PY'
import json
from pathlib import Path
from reelforge.visual_library.composition.farm_motion import farm_walk
with Path("outputs/stage1b1/approach.json").open("x", encoding="utf-8") as handle:
    json.dump(farm_walk(moving_camera=True), handle, indent=2)
PY
python tools/blocking.py render outputs/stage1b1/approach.json --output-dir outputs/stage1b1/walk
```

See the [engineering report](../../../Stage1B1_Encoder_Cleanup_Report.md) for
the baseline diagnosis, controlled fault injection and remaining limits.
