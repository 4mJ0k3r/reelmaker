# Cinematic proof films

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

The Forgotten Parcel and The Creek Crossing are three-shot, 270-frame
silent proofs. The scene renderer validates and renders each shot under
its existing budget. The production stream-copy helper joins and verifies
the encoded frames. These presets are separate from the episode contract.

```sh
PYTHONPATH=src:. python -m tools.living_worlds film-request examples/living-worlds/the_forgotten_parcel.film.json --output-dir outputs/forgotten-parcel
```

Inspect film_report.json for decoded frames, exact timestamp verification,
per-shot resource reports and assembly telemetry.
