# Stage 0C visual evidence

The [palette and shape board](palette.svg) is an original code-authored
reference for future work. Its colors match the [style guide](../../VISUAL_STYLE_GUIDE.md).
It depicts a target direction.

The four stills below were sampled from the approved Stage 0A/0B source tree
using its existing frame evaluators and Cairo backend. Each is a 720 × 1280
JPEG preview of the inspected PNG. Frame numbers are zero-based. No temporal
claims are made from these samples.

| Still | Existing source | Frame |
| --- | --- | ---: |
| [Orchard establishing](orchard-establish.jpg) | `build_shot("establish", "orchard", mood="warm")`, default staging | 20 |
| [Frost Peak threat](frost-threat.jpg) | `build_shot("threat", "frost_peak", mood="storm")` | 24 |
| [Rowan at the barn](rowan-barn.jpg) | `examples/scenes/barn_approach.json` | 45 |
| [Rowan in the settlement](rowan-settlement.jpg) | `examples/procedural/settlement_street_33.json` | 45 |

Storyboard samples used `compile_storyboard` and `direction_frame`. Scene and
procedural samples used the corresponding existing compiler and `scene_frame`.
Each selected frame was drawn on one Cairo surface under the existing job
monitor. See the [report](../../../Stage0C_Art_Direction_Report.md) for the
visual assessment and limitations.
