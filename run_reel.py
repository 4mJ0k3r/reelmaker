#!/usr/bin/env python3
"""ReelForge one-command reel generator (portable entry point).

    python3 run_reel.py "Yellow Mellow discovers an emergency signal in snowy mountains"
    python3 run_reel.py --prompt "..." --duration 15
    python3 run_reel.py --prompt-file my_prompt.txt
    python3 run_reel.py --list-support | --check | --plan-only --prompt "..."

Pipeline (no hand-written JSON): prompt -> deterministic planner (reelforge.mvp.planner) ->
production-0.1 manifest -> full contract validation -> the audited chunked production workflow
(reelforge.productions.workflow.render_production) -> verified MP4 in a fresh job folder.

Every project path is resolved from this file's location, so the folder can be extracted anywhere.
No video is ever published unless it passes verification; existing jobs are never overwritten.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
REGISTRY_ROOT = ROOT / "assets" / "audio"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs"
DEFAULT_PROMPT_FILE_HINT = "outputs/_prompt.txt"

EXIT_OK = 0
EXIT_BAD_ARGS = 1
EXIT_UNSUPPORTED = 2  # prompt/duration outside the supported vocabulary
EXIT_INVALID = 3  # planner output failed contract validation
EXIT_ENVIRONMENT = 4  # python/cairo/ffmpeg/memory blocker
EXIT_RENDER = 5
EXIT_VERIFY = 6
EXIT_EXISTS = 7  # requested job folder already exists


# ---------------------------------------------------------------- interpreter selection
def _preferred_python() -> str | None:
    marker = ROOT / ".reelforge_python"
    if marker.is_file():
        candidate = marker.read_text().strip()
        if candidate and Path(candidate).exists():
            return candidate
    venv_python = ROOT / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else None


def _already_in(target: str) -> bool:
    venv = (ROOT / ".venv").resolve()
    target_path = Path(target)
    if venv in target_path.resolve().parents or venv in target_path.parents:
        return Path(sys.prefix).resolve() == venv
    return os.path.realpath(sys.executable) == os.path.realpath(target)


def _reexec_if_needed() -> None:
    """Re-run under the interpreter prepared by setup.sh (.venv or recorded system python)."""
    if os.environ.get("REELFORGE_REEXEC") == "1":
        return
    target = _preferred_python()
    if target is None or _already_in(target):
        return
    env = dict(os.environ, REELFORGE_REEXEC="1")
    os.execve(target, [target, str(Path(__file__).resolve()), *sys.argv[1:]], env)


def _use_package_source() -> None:
    """Import reelforge from THIS folder's src/ only (never from another checkout)."""
    src = str(SRC)
    sys.path[:] = [p for p in sys.path if p != src]
    sys.path.insert(0, src)


# ---------------------------------------------------------------- environment
def _run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def environment_status(output_root: Path) -> dict:
    status: dict = {
        "package_root": str(ROOT),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
    }
    blockers: list[str] = []
    warnings: list[str] = []

    status["python_ok"] = sys.version_info[:2] == (3, 12)
    if not status["python_ok"]:
        blockers.append(f"Python 3.12 is required (running {status['python']}). Run setup.sh.")
    for module in ("jsonschema", "cairo"):
        try:
            imported = __import__(module)
            if module == "jsonschema":
                from importlib import metadata

                status[module] = metadata.version("jsonschema")
            else:
                status[module] = getattr(imported, "version", "ok")
        except Exception as error:  # noqa: BLE001 - report any import failure
            status[module] = None
            blockers.append(f"Python module '{module}' is not importable ({error}). Run setup.sh.")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    status["ffmpeg"] = ffmpeg
    status["ffprobe"] = ffprobe
    libx264 = False
    if ffmpeg:
        libx264 = "libx264" in _run([ffmpeg, "-hide_banner", "-encoders"]).stdout
    status["libx264"] = libx264
    if not ffmpeg or not ffprobe:
        blockers.append("ffmpeg/ffprobe not found (sudo apt-get install -y ffmpeg).")
    elif not libx264:
        blockers.append("This ffmpeg lacks the libx264 encoder (install a full ffmpeg build).")

    try:
        meminfo = Path("/proc/meminfo").read_text()
        available = int(re.search(r"MemAvailable:\s+(\d+) kB", meminfo).group(1)) // 1024
        status["mem_available_mib"] = available
        warnings.append(
            "ReelForge enforces its own memory admission (256 MiB job budget + 64 MiB reserve); "
            "it will refuse to start if the machine cannot satisfy it."
        )
    except Exception:  # noqa: BLE001
        status["mem_available_mib"] = None
        warnings.append("Could not read /proc/meminfo (not Linux/WSL?).")

    resolved_out = output_root.resolve()
    if str(resolved_out) == "/tmp" or str(resolved_out).startswith("/tmp/"):
        blockers.append("Outputs may not live under /tmp (engine policy). Use a project folder.")
    try:
        output_root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output_root, prefix=".probe_"):
            pass
        status["outputs_writable"] = True
    except OSError as error:
        status["outputs_writable"] = False
        blockers.append(f"Output folder {output_root} is not writable ({error}).")

    _use_package_source()
    try:
        import reelforge

        package_file = Path(reelforge.__file__).resolve()
        status["reelforge_file"] = str(package_file)
        status["reelforge_inside_package"] = ROOT in package_file.parents
        if not status["reelforge_inside_package"]:
            blockers.append(f"reelforge imported from outside this package: {package_file}")
    except Exception as error:  # noqa: BLE001
        status["reelforge_file"] = None
        blockers.append(f"reelforge package import failed ({error}).")

    status["blockers"] = blockers
    status["warnings"] = warnings
    status["rendering_available"] = not blockers
    return status


# ---------------------------------------------------------------- planning
def build_plan(prompt: str, duration: int, title: str | None, *, strategy: str = "legacy"):
    """Return (plan, manifest, compiled). Raises PlanError or InputError."""
    from reelforge.mvp.planner import build_production_manifest, plan_story
    from reelforge.productions.contract import compile_production

    plan = plan_story(prompt, duration, title=title, strategy=strategy)
    manifest = build_production_manifest(plan)
    compiled = compile_production(manifest)
    return plan, manifest, compiled


def support_summary() -> dict:
    from reelforge.mvp import planner
    from reelforge.mvp.storylib import _MOODS

    info = planner.supported()
    info["prompt_keywords"] = {
        "environments": planner.ENV_KEYWORDS,
        "story_actions": planner.ACTION_KEYWORDS,
        "moods": planner.MOOD_KEYWORDS,
    }
    info["moods"] = sorted(_MOODS)
    info["planner_strategies"] = ["legacy", "director-v2"]
    info["audio"] = "silent output only (no audio streams)"
    info["output"] = "720x1280 (9:16), 30 fps, H.264 yuv420p"
    return info


# ---------------------------------------------------------------- job folder + publishing
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class JobExists(FileExistsError):
    pass


def make_job_dir(output_root: Path, name: str | None = None) -> Path:
    """Atomically create a fresh job folder. Never reuses or overwrites an existing one."""
    output_root.mkdir(parents=True, exist_ok=True)
    if name:
        if not _NAME.match(name):
            raise ValueError("--name must be 1-64 chars of letters, digits, '_', '.', '-'")
        job = output_root / name
        try:
            job.mkdir()
        except FileExistsError as error:
            raise JobExists(f"{job} already exists; choose another --name") from error
        return job
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for attempt in range(1000):
        job = output_root / (f"reel_{stamp}" if attempt == 0 else f"reel_{stamp}_{attempt:03d}")
        try:
            job.mkdir()  # atomic: exactly one concurrent caller wins each name
            return job
        except FileExistsError:
            continue
    raise RuntimeError("could not allocate a unique job folder")


def publish_final(source: Path, final: Path) -> None:
    """Copy to a partial file, fsync, then link into place without ever replacing a file."""
    if final.exists() or final.is_symlink():
        raise FileExistsError(f"{final} already exists")
    partial = final.with_name(final.name + ".partial")
    with source.open("rb") as src, partial.open("xb") as dst:
        shutil.copyfileobj(src, dst, 1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    try:
        os.link(partial, final)  # fails if final appeared meanwhile: no clobber
    except FileExistsError:
        partial.unlink(missing_ok=True)
        raise
    except OSError:  # filesystem without hard links
        if final.exists():
            partial.unlink(missing_ok=True)
            raise FileExistsError(f"{final} already exists") from None
        partial.rename(final)
        return
    partial.unlink(missing_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------- verification
def verify_mp4(path: Path, frames: int) -> dict:
    """Independent ffprobe/ffmpeg verification of the published MP4."""
    probe = _run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        timeout=120,
    )
    meta = json.loads(probe.stdout or "{}")
    streams = meta.get("streams", [])
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    v = video[0] if video else {}
    counted = _run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
         "stream=nb_read_frames", "-of", "csv=p=0", str(path)],
        timeout=600,
    )
    try:
        decoded_frames = int(counted.stdout.strip().rstrip(","))
    except ValueError:
        decoded_frames = -1
    decode = _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"],
                  timeout=900)
    duration = float(meta.get("format", {}).get("duration", 0) or 0)
    checks = {
        "one_video_stream": len(video) == 1,
        "codec_h264": v.get("codec_name") == "h264",
        "pix_fmt_yuv420p": v.get("pix_fmt") == "yuv420p",
        "resolution_720x1280": (v.get("width"), v.get("height")) == (720, 1280),
        "frame_rate_30": v.get("avg_frame_rate") == "30/1",
        "decoded_frames_expected": decoded_frames == frames,
        "duration_expected": abs(duration - frames / 30) < 0.01,
        "no_audio_stream": len(audio) == 0,
        "decode_clean": decode.returncode == 0 and not decode.stderr.strip(),
    }
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "expected_frames": frames,
        "decoded_frames": decoded_frames,
        "duration_seconds": duration,
        "codec": v.get("codec_name"),
        "pix_fmt": v.get("pix_fmt"),
        "width": v.get("width"),
        "height": v.get("height"),
        "avg_frame_rate": v.get("avg_frame_rate"),
        "audio_streams": len(audio),
        "checks": checks,
        "passed": all(checks.values()),
    }


# ---------------------------------------------------------------- reporting
def write_report(job: Path, info: dict) -> None:
    lines = [
        f"# ReelForge production report: {info.get('title', '')}",
        "",
        f"- Status: **{info['status'].upper()}**",
        f"- Prompt: {info['prompt']}",
        f"- Duration: {info['duration']} s ({info.get('frames', '?')} frames, 30 fps, 720x1280)",
        f"- Environments: {', '.join(info.get('environments', [])) or 'n/a'}",
        "- Audio: none (this one-command workflow produces a silent MP4)",
        f"- Job folder: `{job}`",
    ]
    if info.get("final_video"):
        lines.append(f"- Final video: `{info['final_video']}`")
    if info.get("error"):
        lines += ["", "## Error", "", f"`{info['error']}`"]
    verification = info.get("verification")
    if verification:
        lines += ["", "## Verification", ""]
        lines.append(f"- passed: {verification['passed']}")
        for key, ok in verification["checks"].items():
            lines.append(f"- {key}: {'ok' if ok else 'FAILED'}")
        lines.append(f"- sha256: {verification['sha256']}")
    lines += ["", "## Shot plan", "", "| # | shot | environment | mood | variant |",
              "|---|------|-------------|------|---------|"]
    for beat in info.get("beats", []):
        lines.append(
            f"| {beat['index']} | {beat['preset']} | {beat['environment']} | {beat['mood']} "
            f"| {beat.get('variant', 0)} |"
        )
    if info.get("timing"):
        lines += ["", "## Timing / resources", ""]
        for key, value in info["timing"].items():
            lines.append(f"- {key}: {value}")
    lines.append("")
    (job / "production_report.md").write_text("\n".join(lines))


def emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


# ---------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ReelForge prompt-to-reel (portable)")
    parser.add_argument("prompt_positional", nargs="?", metavar="PROMPT")
    parser.add_argument("--prompt", help="story prompt text")
    parser.add_argument("--prompt-file", help="read the prompt from a UTF-8 text file")
    parser.add_argument("--duration", type=int, default=60, help="15 or 60 seconds (default 60)")
    parser.add_argument("--title", default=None)
    parser.add_argument("--strategy", choices=("legacy", "director-v2"), default="legacy",
                        help="use the opt-in chronological story director (default: legacy)")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--name", default=None, help="job folder name (refused if it exists)")
    parser.add_argument("--plan-only", action="store_true", help="validate the plan, do not render")
    parser.add_argument("--list-support", action="store_true")
    parser.add_argument("--check", action="store_true", help="report environment readiness")
    parser.add_argument("--no-reexec", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if not args.no_reexec:
        _reexec_if_needed()
    _use_package_source()
    output_root = Path(args.output_root).resolve()

    if args.check:
        status = environment_status(output_root)
        emit(status)
        return EXIT_OK if status["rendering_available"] else EXIT_ENVIRONMENT
    if args.list_support:
        emit(support_summary())
        return EXIT_OK

    sources = [s for s in (args.prompt_positional, args.prompt, args.prompt_file) if s]
    if len(sources) != 1:
        emit({"ok": False, "stage": "arguments",
              "error": "Provide exactly one of: PROMPT, --prompt, --prompt-file"})
        return EXIT_BAD_ARGS
    prompt = args.prompt_positional or args.prompt
    if args.prompt_file:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        except OSError as error:
            emit({"ok": False, "stage": "arguments", "error": f"cannot read prompt file: {error}"})
            return EXIT_BAD_ARGS

    from reelforge.core.errors import InputError
    from reelforge.mvp.planner import PlanError, plan_summary

    try:
        plan, manifest, compiled = build_plan(prompt, args.duration, args.title, strategy=args.strategy)
    except PlanError as error:
        emit({"ok": False, "stage": "planning", "error": str(error),
              "supported": support_summary()})
        return EXIT_UNSUPPORTED
    except InputError as error:
        emit({"ok": False, "stage": "validation",
              "error": f"{error.issue.code} at {error.issue.path}: {error.issue.message}"})
        return EXIT_INVALID

    summary = plan_summary(plan)
    if args.strategy == "director-v2":
        from reelforge.mvp.director import inspect_directed_manifest

        try:
            summary["observed_staging"] = inspect_directed_manifest(plan, manifest)
        except PlanError as error:
            emit({"ok": False, "stage": "constraints", "error": str(error)})
            return EXIT_INVALID
    summary["compiled"] = {"frames": compiled.frames, "seconds": compiled.seconds,
                           "segments": len(compiled.segments), "chunks": len(compiled.chunks)}
    if args.plan_only:
        emit({"ok": True, "stage": "plan-only", "plan": summary})
        return EXIT_OK

    status = environment_status(output_root)
    if not status["rendering_available"]:
        emit({"ok": False, "stage": "environment", "blockers": status["blockers"],
              "hint": "Run setup.sh (Linux/WSL) or setup.ps1 (Windows), then retry."})
        return EXIT_ENVIRONMENT

    try:
        job = make_job_dir(output_root, args.name)
    except JobExists as error:
        emit({"ok": False, "stage": "output", "error": str(error)})
        return EXIT_EXISTS
    except ValueError as error:
        emit({"ok": False, "stage": "arguments", "error": str(error)})
        return EXIT_BAD_ARGS

    (job / "production_manifest.json").write_text(json.dumps(manifest, indent=2))
    if args.strategy == "director-v2":
        (job / "story_plan.json").write_text(json.dumps(summary, indent=2) + "\n")
    info = {
        "status": "failed", "title": plan.title, "prompt": prompt, "duration": args.duration,
        "frames": compiled.frames, "environments": plan.environments, "beats": summary["beats"],
        "final_video": None, "error": None, "verification": None, "timing": {},
    }
    started = time.perf_counter()
    exit_code = EXIT_RENDER
    work = job / "_work"
    try:
        from threading import Event

        from reelforge.productions.workflow import render_production

        report = render_production(compiled, work, registry_root=REGISTRY_ROOT, cancelled=Event())
        info["timing"]["render_seconds"] = round(time.perf_counter() - started, 1)
        peaks = [c.get("peak_rss") for c in report.get("chunk_reports", []) if c.get("peak_rss")]
        if peaks:
            info["timing"]["max_chunk_peak_rss_mib"] = round(max(peaks) / 1048576, 1)
        if (work / "report.json").is_file():
            shutil.copy2(work / "report.json", job / "render_report.json")
        if not report.get("success"):
            info["error"] = json.dumps(report.get("error"))
        else:
            final = job / "final.mp4"
            publish_final(work / "reel.mp4", final)
            verification = verify_mp4(final, compiled.frames)
            info["verification"] = verification
            (job / "verification.json").write_text(json.dumps(verification, indent=2))
            if verification["passed"]:
                info["status"] = "success"
                info["final_video"] = str(final)
                exit_code = EXIT_OK
            else:
                final.rename(job / "rejected_failed_verification.mp4")
                info["error"] = "Published MP4 failed independent verification and was rejected."
                exit_code = EXIT_VERIFY
    except Exception as error:  # noqa: BLE001 - always leave an honest report
        info["error"] = f"{type(error).__name__}: {error}"
        exit_code = EXIT_RENDER
    finally:
        shutil.rmtree(work, ignore_errors=True)  # private workspace; chunk MP4s are redundant
        for leftover in job.glob("final.mp4.partial"):
            leftover.unlink(missing_ok=True)

    if info["status"] != "success":
        (job / "verification.json").write_text(
            json.dumps({"passed": False, "status": "failed", "error": info["error"],
                        "verification": info["verification"]}, indent=2))
    write_report(job, info)
    emit({"ok": info["status"] == "success", "stage": "complete" if exit_code == 0 else "failed",
          "final_video": info["final_video"], "job_dir": str(job),
          "verification_passed": bool(info["verification"] and info["verification"]["passed"]),
          "error": info["error"], "timing": info["timing"], "report": str(job / "production_report.md")})
    if exit_code == EXIT_OK:
        print(f"\nFINAL VIDEO: {info['final_video']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
