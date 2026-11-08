# Sprint J qualification packet — Ubuntu operator procedure

Status: J3/J4 remain UNQUALIFIED until all three real films pass. This is a reusable
CLI operator, not a substitute renderer. No Hindi/120s changes are admitted yet.
All packet WAVs are synthetic event timing signals, never human narration.

## Host prerequisites

Use Ubuntu24.04 x86_64, CPython3.12, FFmpeg/FFprobe with libx264, and Cairo.
Provision OS dependencies once on the user's host (not during a job):

```
sudo apt-get update
sudo apt-get install -y python3.12-venv python3-dev build-essential pkg-config libcairo2-dev ffmpeg fonts-dejavu-core
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-runtime.txt -r requirements-renderer.txt pytest==8.4.2
```

Python runtime pins are in requirements files. See docs/NATIVE_SETUP.md. Host/source
versions are recorded by the existing engine. No network/API is required for rendering
after provisioning. Existing silent ASCII caption fonts must be present too.

Required: real memory-controller membership/mounts, readable memory limits/current
and memory.events (OOM/OOM-kill) for strict accounting; 256MiB process-tree budget
plus64MiB reserve; disk preflight and persistent non-symlink workspace outside /tmp.
Visible guest RAM alone cannot replace cgroup/OOM accounting. Never fabricate files,
mount synthetic telemetry, enable an unsupported fallback, or monkeypatch checks.
If the system hides controllers, ask its administrator to provide a properly delegated
supported environment; do not assume systemd-run or Docker automatically solves it.

## Restore

Extract the completion review ZIP OUTSIDE the engine checkout. Clone its full-history
bundle to a clean engine directory, checkout sprint-j-unified-narration-production,
and compare exact commit/tree against packet.json and the completion handoff.
The packet runner refuses changed commit/tree or tracked source changes.
Keep packet productions/registry and output parent outside the engine checkout.
Review request data and manifest/plan fingerprints before any render.

## Run

The packet contains packet.json, productions/, and operator copies. Use absolute
Linux paths. Create the output parent once; the runner chooses a fresh timestamped
qualification directory and never reuses a film destination.

```
/ABS/engine/.venv/bin/python /ABS/engine/tools/render_sprint_j_packet.py --engine /ABS/engine --packet /ABS/packet --output-root /ABS/private-output --python /ABS/engine/.venv/bin/python --check-only
/ABS/engine/.venv/bin/python /ABS/engine/tools/render_sprint_j_packet.py --engine /ABS/engine --packet /ABS/packet --output-root /ABS/private-output --python /ABS/engine/.venv/bin/python
```

The wrapper verifies file SHA-256, synthetic provenance, engine commit/tree and plans.
It invokes the SAME tools/reel_production.py CLI for capabilities, validate, plan,
inspect, preflight for ALL films, then render/verify sequentially. A failed preflight
stops before the first render; a later failure preserves earlier completed films.
Ctrl+C/SIGTERM forwards cancellation to the CLI. Do not delete an uncertain native
workspace; record its error and investigate. Logs and packet_result.json survive.
check-only still requires TRUE preflight; it is not an admission bypass.

Film A:15s/450frames parcel in orchard. Film B:60s/1800frames ridge escape before
orchard safety, no beacon. Film C:6s/180frames registered cinematic pickup.
The wrapper logs native CLI output rather than implementing animation/audio itself.
Delivery requires success, independent verify, report.json and verification.json,
mobile storyboards, actual asset audit where supported, AAC sample/clock and chunk
seam evidence, PTS/frame identities and sampled process-tree memory measurements.
Mark tones synthetic. Human-voice alignment and artistic approval require human review.

## Tests and remaining gates

Run a fresh full applicable suite on the admitted host and retain its complete log:

```
PYTHONPATH=src .venv/bin/python -m pytest -q --basetemp outputs/ci-completion --tb=short --durations=20
PYTHONPATH=src .venv/bin/python -m reelforge.catalog validate
PYTHONPATH=src .venv/bin/python -m reelforge.catalog generate --check
```

Do not reuse stale pytest staging. Old native tests can fail earlier at strict
admission on an incompatible host; report those failures, not an all-green result.
After three films pass, create checkpoint bundle/ZIP before Hindi shaping work.
Do not publish GitHub. Do not add WAVs/MP4s to source history.

## Windows / WSL2 launcher

`tools/render_sprint_j_packet.bat` is UNTESTED ON WINDOWS/WSL2. It invokes actual
`wsl.exe -d Ubuntu`; it does not emulate Linux. Check `wsl --list --verbose` shows
Ubuntu running WSL2 and verify the prerequisites/telemetry INSIDE that distribution.
Pass four absolute LINUX paths: engine, packet, output parent, venv Python. Optional
fifth argument --check-only. If the distro has a different registered name, adjust
the launcher copy's -d argument. This wrapper does not certify WSL2/NTFS/low-memory VM.
