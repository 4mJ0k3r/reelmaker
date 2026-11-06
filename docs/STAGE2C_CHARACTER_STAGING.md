# Cinematic character staging

Call `cinematic_character_staging(character, world)` in
`reelforge.visual_library.composition.character_staging`. Supported characters are
`rowan_01` and `yellow_mellow_v2`. Supported worlds are `farm` (Dusk Farm) and
`cold_ridge`. The function returns an admitted `direction-0.1` manifest with the
original Stage 2A or 2B blocking base.

| Shot | Frames | Existing behavior | Composition |
| --- | --- | --- | --- |
| Context | 0–21 | `establishing` | Full body at 1.08×, targeting the registered barn or beacon node. The character and destination share the frame. |
| Attention | 22–61 for Rowan, 22–56 for Yellow Mellow | `follow` | Route-aware actor tracking at fixed 1.55× or 1.70× respectively. Boots and shadows stay in frame. |
| Reaction and settle | 62–89 for Rowan, 57–89 for Yellow Mellow | `close_up` | Route-aware actor targeting and a bounded zoom of 2.60→2.78× or 3.05→4.00×. `feet_crop` intentionally allows the shoes to leave the frame. |

The second cut occurs three frames after the accepted stop. This lets the
audience see the ensuing facial beat and its settle. Horizontal framing leaves
space in the direction of the look. The reaction isolates the character.
The barn or beacon can leave the frame in this shot. The earlier shots establish
its location, and the actor's facing continues toward that side.

The edit reuses the original world scale, contact shadow commands, grading and
source frames. Character scale differences are handled by camera choice.
Render at 720 × 1280 and check a 360 × 640 copy. Look for the face, hand and hat
silhouette in reaction and the feet in attention.

The helper emits direction directly, since certain farm cuts exceed the
storyboard wrapper's 60-unit editorial pan allowance. Direction admission
still checks target depth, frame spans, safe margins, foreground, zoom, pan and
the 1.8 cut scale ratio. It supports the authored approach for each pair.
The interface accepts two IDs and has no arbitrary camera tracks, actor turns
or automatic target tracking. The one-command prompt planner has no selector.

## Reproduce

Use the pinned Python 3.12 CPU renderer with Cairo/Pycairo and FFmpeg. Pillow is
used for evidence sheets. Run from the repository root with fresh output paths.

```bash
mkdir -p outputs/stage2c
export PYTHONPATH=src
python - <<'PY'
import json
from pathlib import Path
from reelforge.visual_library.composition.character_staging import cinematic_character_staging

doc = cinematic_character_staging("yellow_mellow_v2", "cold_ridge")
Path("outputs/stage2c/yellow-ridge.json").write_text(json.dumps(doc, indent=2) + "\n")
PY
python tools/direction.py validate outputs/stage2c/yellow-ridge.json
python tools/direction.py render outputs/stage2c/yellow-ridge.json --output-dir outputs/stage2c/ridge-clip
python tools/stage2c_staging_evidence.py outputs/stage2c/evidence
```

The process-tree budget remains 256 MiB with a 64 MiB admission reserve.
See the [review stills and diagnostics](visual-evidence/stage2c/README.md).
