# Trusted object interactions

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

Pick a registered pairing using `python -m tools.living_worlds list`.
All request fields are closed identifiers. Source-owned timing and
placements are fixed per preset.

| Preset | Actors | Prop |
| --- | --- | --- |
| pickup_carry_place | Scout, Mechanic | parcel_01 |
| sit_stand | Rowan, Scout, Mechanic | bench_01 |
| push_cart | Mechanic, Scout | handcart_01 |

The bench seat uses a local height of −19 units. Parcel grasp uses
`(0, -16)` and cart handle uses `(-51, -41)`. The near hand is
the measured contact for parcel and cart. Wheels roll at a distance-linked
angle. Contact is an authored planar solve.

```sh
PYTHONPATH=src:. python -m tools.living_worlds interaction examples/living-worlds/pickup_carry_place.json --output-dir outputs/parcel-proof
```
