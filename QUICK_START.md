# ReelForge quick start

ReelForge turns a plain-English story request into a vertical MP4 (720x1280, 30 fps, silent).
It runs on Linux or **Windows via WSL2 Ubuntu 24.04**, on the CPU only.

## 1. Extract
Unzip `ReelForge_AgentReady_Pipeline.zip` anywhere (for best speed on Windows, put it inside the WSL home).
Do not put it under `/tmp`.

## 2. Open the folder in your AI coding agent
Open the extracted `ReelForge` folder in Kiro (or another coding agent). The agent reads `AGENTS.md`
automatically. If it does not, tell it once: *"Read AGENTS.md and follow it."*

## 3. One-time setup (the agent can do this for you)
- Linux / WSL:  `bash setup.sh`
- Windows:      `powershell -ExecutionPolicy Bypass -File .\setup.ps1`

It checks Python 3.12, Cairo, FFmpeg (libx264), restores the locked dependencies into `.venv`, runs a
planning test and prints **"Video rendering is AVAILABLE"** when ready. If something is missing it
prints the exact `apt` command to run. (Internet is needed for this first step.)

## 4. Ask for a reel
Just write a normal request in the agent chat, for example:

> Create a 60-second animated reel where Yellow Mellow discovers an emergency signal in snowy mountains.

The agent plans, renders and verifies it for you. To do the same by hand:

```
python3 run_reel.py "Yellow Mellow discovers an emergency signal in snowy mountains"
python3 run_reel.py --prompt "Yellow Mellow explores an orchard and runs to safety" --duration 15
```
(From Windows PowerShell prefix with: `wsl -d Ubuntu-24.04 --cd "<this folder>" -- `)

Useful switches: `--plan-only` (check the story plan, no video), `--list-support`, `--check`.

## 5. Find the video
`outputs/reel_<date>_<time>/final.mp4` next to `verification.json`, `production_manifest.json` and
`production_report.md`. Existing videos are never overwritten.

## What to expect
- Durations: **15 s** (about a minute to render) or **60 s** (several minutes).
- Characters / places: Yellow Mellow in a snowy mountain and/or a dusk orchard (see `docs/AGENT_CAPABILITIES.md`).
- Output is **silent**. Sound is a separate workflow: `docs/AUDIO_WORKFLOW.md`.
- Unsupported stories are reported honestly with the closest supported version; they are not faked.
