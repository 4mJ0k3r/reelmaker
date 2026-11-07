# ReelForge: portable agent-ready distribution

ReelForge is a CPU-only generator of vertical animated reels. Characters, places and props are
drawn by code with Cairo and streamed to FFmpeg: no AI images/video, no GPU, no browser.

This folder is the complete application. Hand it to an AI coding agent and describe a reel in
plain English; the agent follows `AGENTS.md` and runs the existing pipeline:

```
request -> planner (src/reelforge/mvp) -> production manifest -> contract validation
        -> chunked render workflow (episodes/productions) -> FFmpeg H.264 -> independent verification
```

| Start here | |
|---|---|
| `QUICK_START.md` | five-step walkthrough |
| `AGENTS.md` | operating instructions for AI agents |
| `docs/AGENT_CAPABILITIES.md` | exactly what can be requested |
| `docs/AUDIO_WORKFLOW.md` | registered audio workflow for legacy entry points |
| [Structured cinematic projects](docs/CINEMATIC_PROJECTS.md) | JSON projects, timed captions, registered audio, and verified reel packages |
| `run_reel.py` | the one-command entry point (`--help`) |
| `setup.sh` / `setup.ps1` | first-run environment setup (Linux/WSL, Windows) |

Layout: `src/reelforge/` (engine), `tools/` (supporting CLIs), `examples/` (sample manifests),
`assets/audio/` (registered diagnostic tones), `docs/` (architecture and contracts),
`tests/` (smoke tests), `outputs/` (your videos).

Prerequisites: Ubuntu 24.04 or WSL2 Ubuntu 24.04, Python 3.12, Cairo (`python3-cairo`), FFmpeg with
libx264, about 4 cores. First setup needs internet (the locked Python dependencies are downloaded, not bundled).

Smoke tests (optional, needs `pip install pytest`):
`python3 -m pytest tests --basetemp outputs/test-temp -q` (runs several minutes).

Verify file integrity with `PACKAGE_MANIFEST_SHA256.txt` (`sha256sum -c PACKAGE_MANIFEST_SHA256.txt`).
