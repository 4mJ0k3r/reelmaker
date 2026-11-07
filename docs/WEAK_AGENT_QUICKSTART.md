# Weak-agent quickstart — 1.0

Operate the installed engine through structured JSON and the existing CLI.
Do not edit Python source, invent IDs, generate artwork/voice, bypass admission,
reuse staging, overwrite an old film or push GitHub.

1. Run `python tools/cinematic_project.py capabilities` and select a listed
   operator example. Use `.venv/bin/python` with the documented Python 3.12
   renderer environment. No arbitrary natural-language script interpreter exists.
2. Copy the selected JSON into a new input directory. Change only supported
   schema fields. Current projects use 90-frame shots, 720×1280/30 fps. Audio
   stops at 30 seconds; 33–60 seconds is silent. Registered interactions keep
   their fixed staging/contact clocks. `intent` requires `camera: "auto"`.
3. Run `validate INPUT.json`. On failure, read code/path/message, select a
   listed valid alternative, fix that field and validate again. Never edit src.
4. Run `plan INPUT.json` and `inspect INPUT.json`; check beat coverage,
   admitted cameras, repetitions and mobile diagnostics.
5. Create a persistent output parent outside /tmp. Choose a NEW output leaf.
   Run `preflight INPUT.json OUTPUT`, then `render INPUT.json OUTPUT`.
6. Require success and verification.json. Run `verify OUTPUT`, inspect decoded
   mobile sheets, then deliver reel.mp4 plus the reproducible source/evidence.

Prefix every command above with `.venv/bin/python tools/cinematic_project.py`.
For the first command, that means `.venv/bin/python tools/cinematic_project.py capabilities`.

Known ready examples: single-character suspense (variant_misty_creek), paired
discovery (directed_discovery), prop interaction (pickup_refined), 30-second
registered audio (the_answering_light), 60-second silent story (before_the_storm).
Exact paths are in capability output; use them rather than guessing.

Stop on admission/telemetry or ownership errors. Restore a missing/corrupt
registered WAV from its trusted source; never relabel diagnostic tones as
narration. For ordinary corrected input, choose a fresh destination and retry.
On OUTPUT_EXISTS, leave it intact. Cancellation is SIGINT/SIGTERM. Cleanup
uncertainty preserves work for investigation. Do not sweep familiar prefixes.

Detailed setup, timing, audio registration, error recovery and limitations:
[Operator guide](REELMAKER_OPERATOR_GUIDE.md). The engine's output is a deliberate
vector/cutout style; media verification cannot establish artistic approval.
