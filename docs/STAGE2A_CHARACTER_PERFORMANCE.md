# Rowan's notice and reaction

Use Rowan Vale (`rowan_01`) with a validated approach to an object staged in his facing direction. The opt-in performance owns the local acting and facial contours during the approach, brake and hold. The route, speed profile, camera, grading, painter order and foot targets still come from the existing workflow.

Add this top-level property to a `blocking-0.2` manifest, or place the same property inside `rowan` in a `storyboard-0.1` manifest.

```json
"performance": {
  "name": "notice_and_react",
  "reaction": "surprised"
}
```

- Select `surprised` for an open, rounded startle or `frightened` for a wider tense mouth, asymmetric brows and slightly stronger recoil. Timing and intensity are authored. The trusted interface accepts these two fields only.
- Use optional initial idle, one or more contiguous `walk` segments, `stop`, then one terminal `idle` beginning between frames 48 and 60. The timeline is 90 frames at 30 FPS. The original segment fields still validate. While selected, the performance supplies expression and acting in place of those segment fields.
- Keep the same left/right facing for the whole route, with the point of interest ahead. Gaze is bounded in local head coordinates and mirrors with the existing facing. The system does not track a target coordinate or steer the actor toward it.
- Gaze starts seven frames before braking, followed by a head tilt and gradual change from calm to concern. The first startle shows on the face six frames after stopping. Head, torso and hands respond in that order. One blink falls during the release into the final watchful hold.
- Keep the original `level_field` corridor and actor/ground depth agreement. Preserve the accepted 0.35–0.75 world scale and omit any static decal below the actor. Medium framing belongs in the direction camera so it projects the same route and support together.
- Existing scene and preset selectors, legacy blocking, and Yellow Mellow V2 use their original artwork and action vocabularies. Performance is a candidate for the trusted development tools and has no one-command planner route. The 256 MiB tree cap and 64 MiB admission reserve still apply.

## Reproduce the examples

With Python 3.12, Cairo/Pycairo, FFmpeg and Pillow for sheet assembly, run from the repository root.

```bash
mkdir -p outputs/stage2a
export PYTHONPATH=src
python - <<'PY'
import json
from pathlib import Path
from reelforge.visual_library.composition.rowan_approach import rowan_storyboard

Path("outputs/stage2a/farm-medium.json").write_text(
    json.dumps(rowan_storyboard("farm", "medium"), indent=2) + "\n"
)
PY
python tools/storyboard.py validate outputs/stage2a/farm-medium.json
python tools/storyboard.py render outputs/stage2a/farm-medium.json --output-dir outputs/stage2a/farm-clip
python tools/stage2a_character_evidence.py outputs/stage2a/evidence
```

Use fresh output directories. The sampler builds both worlds and views from the same approach recipe. Use `rowan_approach("farm")` to get its native blocking manifest or `rowan_storyboard("cold_ridge", "medium")` for the beacon study. See the [evidence index](visual-evidence/stage2a/README.md).
