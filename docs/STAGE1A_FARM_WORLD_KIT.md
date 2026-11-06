# Stage 1A farm world kit

Five candidate assets resolve through the existing trusted scene registry.
They emit immutable vector paths. Use the existing `scene-0.1` node kinds,
transforms, variant choices and bounded art direction. The prompt planner
does not select these assets.

| Asset ID | Node kind and variants | Controls and placement |
| --- | --- | --- |
| `cinematic_dusk_sky_01` | Background · `default` | Scene warmth and atmosphere in 0–1. Start at the top-left canvas origin on depth 0. Sun is placed left. |
| `cinematic_dusk_hills_01` | Background · `rolling`, `folded` | Scene atmosphere in 0–1 grades three separated planes. Place the origin at the authored horizon reference. |
| `cinematic_farm_track_01` | Environment · `default` | Scene warmth in 0–1. Local ground origin at (0, 0). The admitted character support envelope is (−200, −76) to (200, 220). The track bends toward a left-facing doorway near local (60, −84). |
| `cinematic_farm_tree_01` | Asset · `broad`, `leaning` | Scene warmth in 0–1. The root flare is at (0, 0). Broad forks low into a spreading crown. Leaning rises on a narrow, asymmetric trunk with a high rightward crown. |
| `cinematic_dusk_contact_01` | Asset · `foot`, `trunk`, `prop` | Match the subject's base and depth. Order before the subject and after ground. Soft contact overlaps a rightward ground-plane cast shape. Size with the scene transform. |

The existing local scale range is 0.25–2, with a composed scale range of
0.1–3. Use variant and transform for variation. The silhouettes are authored
and deterministic. No arbitrary seed or wind control is exposed. Keep the
upright assets unrotated. A support envelope constrains actor placement.
It does not determine whether a point falls on the drawn track.

## Farm assembly

Use `reelforge.visual_library.composition.farm.farm_scene("establishing")`
or `farm_scene("medium")` to get a validated scene. The function shares one
world layout between views and applies the engine's existing depth projection
as validated per-layer transforms for the closer view. A locked scene camera
then evaluates each view. Use `compile_scene` and `scene_frame` as with other
scenes.

The sky is depth 0. The hills use reference (180, 353) at depth 0.18. The ground
anchor (180, 500), Rowan (132, 541), barn (262, 422), and two midground trees
share depth 1. The left foreground tree uses depth 1.4. Rowan's registered
standing reference, multiplied by 0.72, is approximately 68 logical units.
The route narrows from the foreground toward the existing barn entrance.
Contact decals share the base and depth of their stationary subjects. The
foreground tree is clipped by the frame and has no separately placed decal.

The sun and contact direction are authored for a left-hand dusk key. These
static decals do not track moving feet, follow terrain slopes or change the
existing rig shadows. Place the prop profile under a compatible rock or
other static prop. The farm demonstrates the barn and trees but contains
no rock. A future walk needs a tracked solution or the existing rig contacts.

## Reproduce the stills

From the checkout with Python 3.12 and the existing Pycairo renderer installed:

```sh
PYTHONPATH=src python tools/stage1a_farm_stills.py outputs/stage1a-proof
```

Use a new output directory. The command samples selected frames and uses the
existing strict resource monitor. It emits PNGs and a JSON report to stdout.
The [review images](visual-evidence/stage1a/README.md) are compact JPEG copies.
The source catalog regenerates through `python -m reelforge.catalog generate`
with `PYTHONPATH=src`.
