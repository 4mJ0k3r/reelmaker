# Articulated scene actors

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

Choose Mira Scout (`scout_01`) or Bram Mechanic (`mechanic_01`). Scene
actions are `idle`, `walk`, `run`, `notice` and `react`. Expressions
are neutral, happy, concerned, surprised, frightened and determined.
The authored profile faces right. Generated worlds validate support and
admit only travel that fits the bounded ground envelope.

```sh
PYTHONPATH=src:. python -m tools.living_worlds actor-reel scout_01 --output-dir outputs/mira-proof
```

The action reel uses cuts between individual action samples. New actors
are scene-only and are excluded from historical blocking and storyboards.
