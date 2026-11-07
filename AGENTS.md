# ReelMaker agent instructions

For production requests, use the installed structured cinematic-project CLI.
The package namespace remains `reelforge`. Do not edit src, schemas, assets or
lock files to satisfy an ordinary production request. Explicit engine-development
assignments are separate and may authorize narrow, tested changes.

Read [docs/WEAK_AGENT_QUICKSTART.md](docs/WEAK_AGENT_QUICKSTART.md), then use
capabilities → select/copy an admitted example → validate → plan/inspect →
preflight → render → verify → deliver. Details and exact commands are in
[docs/REELMAKER_OPERATOR_GUIDE.md](docs/REELMAKER_OPERATOR_GUIDE.md).
Do not invent IDs or assume unrestricted script interpretation/choreography.

Preserve CPU Cairo, Python 3.12, 720×1280, 30 fps, H.264/yuv420p, sequential
streaming, strict versioned JSON, and 256 MiB process-tree budget + 64 MiB reserve.
Audio uses registered PCM16 WAV. Staged 33–60-second projects admit silence
or one finished narration recording. Do not generate AI artwork/video/voice or
introduce a browser renderer.

Use a new output leaf under an existing persistent non-symlink parent outside
/tmp. Never overwrite films, reuse native staging, lower limits, delete foreign
or replaced paths, or claim an incomplete output succeeded. Stop and investigate
ownership/admission failures. The legacy `run_reel.py` prompt route remains
available with its narrower Yellow Mellow rules documented in QUICK_START.md;
do not confuse it with the current cinematic workflow.

No GitHub push, merge, PR, force/rebase or release without explicit user
instruction. The D8–D9 development assignment forbids publication; produce local
checkpoint commits and reviewed recovery artifacts. Never certify the real
low-memory target VM or offline browser interaction without testing there.
