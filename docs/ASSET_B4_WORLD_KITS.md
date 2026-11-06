# Reusable world kits

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

Village Lane admits daylight, evening and rainy_night. Woodland Creek
admits clear, misty and windy. Both kits return validated scene-0.1 JSON.
The creek is decorative and its bridge grants no new support surface.

```sh
export PYTHONPATH=src:.
python -m tools.living_worlds world woodland_creek windy --actor mechanic_01 --action walk
python -m tools.scene render examples/living-worlds/woodland_creek-windy.scene.json --output-dir outputs/windy-proof
```
