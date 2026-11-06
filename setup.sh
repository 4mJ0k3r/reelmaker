#!/usr/bin/env bash
# ReelForge first-run setup for Ubuntu 24.04 / WSL2 Ubuntu 24.04 (Python 3.12, CPU Cairo, FFmpeg).
#
#   bash setup.sh
#
# It checks the system, prepares a project-local Python environment (.venv) from the locked
# dependencies, verifies the package imports, runs a planning smoke test and reports whether video
# rendering is available. It never lowers ReelForge's memory/safety limits. Nothing is installed
# system-wide: missing system packages are reported with the exact apt command to run.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

PASS="[ ok ]"; FAIL="[FAIL]"; INFO="[info]"
problems=0
say() { printf '%s %s\n' "$1" "$2"; }
bad() { say "$FAIL" "$1"; problems=$((problems + 1)); }

echo "== ReelForge setup in: $ROOT"

# 1. Operating environment ------------------------------------------------------------------
if [ "$(uname -s)" != "Linux" ]; then
  bad "This script needs Linux or WSL2 Ubuntu 24.04 (found $(uname -s)). On Windows run setup.ps1."
  exit 1
fi
if grep -qi microsoft /proc/version 2>/dev/null; then say "$PASS" "WSL2 Linux detected"; else say "$PASS" "Linux detected"; fi
case "$ROOT" in
  /mnt/*) say "$INFO" "Project is on a Windows drive (/mnt/...). It works, but a folder inside the WSL home (~/) is faster." ;;
esac
case "$ROOT" in
  /tmp|/tmp/*) bad "Do not place the project under /tmp (ReelForge refuses /tmp workspaces)." ;;
esac

# 2. Python 3.12 ----------------------------------------------------------------------------
PY=""
for candidate in python3.12 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; then
      PY="$(command -v "$candidate")"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  bad "Python 3.12 not found. Ubuntu 24.04 ships it: sudo apt-get install -y python3 python3-venv"
  exit 1
fi
say "$PASS" "Python 3.12 at $PY"

# 3. System tools: Cairo, FFmpeg + libx264 ---------------------------------------------------
cairo_system=0
"$PY" -c 'import cairo' 2>/dev/null && cairo_system=1
if [ $cairo_system -eq 1 ]; then say "$PASS" "Pycairo available in system Python"; else
  say "$INFO" "Pycairo not in system Python (will try to install it in the project environment)"; fi

if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264; then
    say "$PASS" "FFmpeg with libx264 ($(ffmpeg -version | head -1 | cut -d' ' -f1-3))"
  else
    bad "FFmpeg has no libx264 encoder. Install a full build: sudo apt-get install -y ffmpeg"
  fi
else
  bad "ffmpeg/ffprobe missing. Run: sudo apt-get update && sudo apt-get install -y ffmpeg"
fi

mem_kb=$(awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)
say "$INFO" "Available memory: $((mem_kb / 1024)) MiB (ReelForge applies its own admission limits; it will refuse to start if they cannot be met)"
say "$INFO" "CPU cores: $(nproc 2>/dev/null || echo '?')"

# 4. Python environment from the locked dependencies -------------------------------------------
ENV_PY=""
if [ "${REELFORGE_NO_UV:-0}" != "1" ] && command -v uv >/dev/null 2>&1; then
  say "$INFO" "uv found: restoring the locked environment (uv sync --frozen --extra renderer)"
  if UV_PROJECT_ENVIRONMENT="$ROOT/.venv" uv sync --frozen --extra renderer --python "$PY" >/tmp/reelforge_uv.log 2>&1; then
    ENV_PY="$ROOT/.venv/bin/python"; say "$PASS" "Locked environment restored with uv"
  else
    say "$INFO" "uv sync failed (usually missing libcairo2-dev); falling back to pip. Details: /tmp/reelforge_uv.log"
  fi
fi
if [ -z "$ENV_PY" ]; then
  if "$PY" -m venv --system-site-packages "$ROOT/.venv" >/dev/null 2>&1; then
    ENV_PY="$ROOT/.venv/bin/python"
    say "$PASS" "Created project environment .venv (inherits system packages such as python3-cairo)"
    if "$ENV_PY" -m pip install --quiet --disable-pip-version-check -r "$ROOT/requirements-runtime.txt"; then
      say "$PASS" "Installed pinned runtime dependencies (jsonschema stack)"
    else
      bad "pip could not install requirements-runtime.txt (network needed for first install)."
    fi
  else
    rm -rf "$ROOT/.venv"
    if "$PY" -c 'import jsonschema' 2>/dev/null; then
      ENV_PY="$PY"
      say "$INFO" "python3-venv unavailable; using system Python (jsonschema already installed)"
    else
      bad "Cannot create .venv and jsonschema is missing. Run: sudo apt-get install -y python3-venv   then re-run setup.sh"
      exit 1
    fi
  fi
fi
if ! "$ENV_PY" -c 'import cairo' 2>/dev/null; then
  say "$INFO" "Trying to install pycairo into the project environment..."
  "$ENV_PY" -m pip install --quiet --disable-pip-version-check -r "$ROOT/requirements-renderer.txt" >/dev/null 2>&1 || true
fi
if ! "$ENV_PY" -c 'import cairo' 2>/dev/null; then
  bad "Pycairo is not importable. Fix with ONE of:  sudo apt-get install -y python3-cairo   (then re-run setup.sh)   or   sudo apt-get install -y libcairo2-dev pkg-config python3-dev build-essential"
else
  say "$PASS" "Pycairo $("$ENV_PY" -c 'import cairo; print(cairo.version)')"
fi
printf '%s\n' "$ENV_PY" > "$ROOT/.reelforge_python"
say "$INFO" "Interpreter recorded in .reelforge_python (run_reel.py uses it automatically)"

# 5. Package import + readiness check --------------------------------------------------------------
echo "== Verifying the ReelForge package"
if "$ENV_PY" "$ROOT/run_reel.py" --check --no-reexec >/tmp/reelforge_check.json 2>&1; then
  say "$PASS" "run_reel.py --check: rendering environment ready"
  rendering=1
else
  rendering=0
  say "$FAIL" "run_reel.py --check reported blockers:"
  "$ENV_PY" - <<'PYEOF'
import json
try:
    data = json.load(open("/tmp/reelforge_check.json"))
    for b in data.get("blockers", []):
        print("   -", b)
except Exception:
    print(open("/tmp/reelforge_check.json").read())
PYEOF
  problems=$((problems + 1))
fi

# 6. Lightweight planning smoke test ------------------------------------------------------------------
echo "== Planning smoke test (no rendering)"
if "$ENV_PY" "$ROOT/run_reel.py" --no-reexec --plan-only --duration 15 \
     --prompt "Yellow Mellow finds an emergency signal in the snowy mountains." >/tmp/reelforge_plan.json 2>&1; then
  say "$PASS" "Planner produced and validated a 15 s production plan"
else
  bad "Planning smoke test failed (see /tmp/reelforge_plan.json)"
fi

echo
if [ $problems -eq 0 ] && [ $rendering -eq 1 ]; then
  say "$PASS" "SETUP COMPLETE. Video rendering is AVAILABLE."
  echo "Next:  python3 run_reel.py \"Yellow Mellow discovers an emergency signal in snowy mountains\""
  exit 0
fi
say "$FAIL" "SETUP INCOMPLETE ($problems problem(s)). Planning may work, but video rendering is NOT available until the items above are fixed."
exit 1
