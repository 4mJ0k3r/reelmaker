"""Long-route contract, native sample timing, and failure isolation."""

import json
import shutil
import subprocess
import wave
from dataclasses import asdict
from pathlib import Path
from threading import Event

import pytest

from reelforge.audio.processing import mix_pcm, pcm_stats, verify_aac_clock
from reelforge.audio.registry import AudioRegistry, MAX_NARRATION_FILE_BYTES, register_asset
from reelforge.cinematic_projects import narration, workflow
from reelforge.cinematic_projects.contract import compile_project
from reelforge.core.errors import InputError, OperationError

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples/sprint-f/the_light_in_the_empty_town_narration_test.json"


def write_wav(path, *, rate=48000, channels=2, count=None, width=2):
    count = rate * 60 if count is None else count
    with wave.open(str(path), "wb") as output:
        output.setparams((channels, width, rate, count, "NONE", ""))
        for start in range(0, count, 4096):
            size = min(4096, count - start)
            output.writeframesraw(b"\x22\x10"[:width] * channels * size)


@pytest.fixture
def registered(tmp_path):
    if not all(shutil.which(cmd) for cmd in ("ffmpeg", "ffprobe")):
        pytest.skip("FFmpeg and ffprobe required")
    root = tmp_path / "registry"
    source = tmp_path / "source.wav"
    write_wav(source)
    asset = register_asset(root, source, "f_timing_signal", "narration")
    return root, asset


@pytest.mark.parametrize(("rate", "channels"), [(48000, 1), (48000, 2), (16000, 1), (44100, 2)])
def test_register_full_sixty_seconds(tmp_path, rate, channels):
    if not all(shutil.which(cmd) for cmd in ("ffmpeg", "ffprobe")):
        pytest.skip("FFmpeg and ffprobe required")
    path = tmp_path / "full.wav"
    write_wav(path, rate=rate, channels=channels)
    asset = register_asset(tmp_path / "registry", path, "take", "narration")
    assert asset.samples == rate * 60
    assert asset.size_bytes == rate * 60 * channels * 2 + 44
    assert asset.sha256 == AudioRegistry(tmp_path / "registry").assets["take"].sha256


def test_reject_invalid_inputs(tmp_path):
    source = tmp_path / "bad.wav"
    for kind in ("oversized", "too_long", "corrupt", "codec"):
        if kind == "oversized":
            with source.open("wb") as f:
                f.truncate(MAX_NARRATION_FILE_BYTES + 1)
        elif kind == "too_long":
            write_wav(source, count=48000 * 60 + 1)
        elif kind == "corrupt":
            source.write_bytes(b"bad RIFF" * 10)
        else:
            write_wav(source, count=1600, width=1)
        with pytest.raises(OperationError) as exc:
            register_asset(tmp_path / "registry", source, "take", "narration")
        assert exc.value.code == "AUDIO_ASSET"
    assert not (tmp_path / "registry/registry.json").exists()


def test_long_contract_and_explicit_trim(registered):
    root, _ = registered
    data = json.loads(REQUEST.read_text())
    project = compile_project(data, root)
    assert project.frames == 1800 and project.audio.narration.start_frame == 0
    assert project.audio_cues[0]["end_sample"] == 2_880_000
    assert project.timeline()["chunk_boundaries"] == [900]
    with pytest.raises(InputError, match="available interval"):
        data["audio"]["narration"]["start_frame"] = 1
        compile_project(data, root)
    data["audio"]["narration"]["trim_end_frame"] = 1799
    assert compile_project(data, root).audio_cues[0]["end_sample"] == 2_880_000
    data["audio"]["cues"] = [dict(data["audio"]["narration"])]
    with pytest.raises(InputError, match="no sound-effect"):
        compile_project(data, root)


@pytest.mark.parametrize("damage", ["missing", "hash", "metadata"])
def test_bad_registry_cannot_reach_video_render(tmp_path, registered, monkeypatch, damage):
    root, asset = registered
    data = json.loads(REQUEST.read_text())
    project = compile_project(data, root)
    path = root / asset.file
    if damage == "missing":
        path.unlink()
    elif damage == "hash":
        with path.open("r+b") as f:
            f.seek(64)
            f.write(b"XX")
    else:
        row = asdict(asset)
        row["channels"] = 3
        (root / "registry.json").write_text(json.dumps({"schema_version": "audio-assets-0.1", "assets": [row]}))
    for name in ("check_narration_storage", "preflight_memory"):
        monkeypatch.setattr(workflow, name, lambda *a: None)
    monkeypatch.setattr(workflow, "_engine", lambda *a: pytest.fail("render called after invalid audio"))
    with pytest.raises(OperationError):
        workflow.render_project(project, tmp_path / "final", registry_root=root)
    assert not (tmp_path / "final").exists()
    assert not list(tmp_path.glob(".reelforge-*"))


def test_non_frame_tail_and_offset_preserve_source_samples(tmp_path, registered):
    root, _ = registered
    source = tmp_path / "short.wav"
    samples = 44100 * 2 + 29
    write_wav(source, rate=44100, channels=1, count=samples)
    asset = register_asset(root, source, "short_take", "narration")
    data = json.loads(REQUEST.read_text())
    data["audio"]["narration"].update(asset_id=asset.id, start_frame=31)
    project = compile_project(data, root)
    cancelled = Event()
    track, snapshot = narration.prepare_narration(project, root, tmp_path / "private", cancelled)
    assert track.output_samples == (samples * 48000 + 44099) // 44100
    output = tmp_path / "mix.f32"
    mix_pcm((track,), 1800, {asset.id: snapshot}, output, cancelled=cancelled)
    assert pcm_stats(output)["samples_per_channel"] == 2_880_000
    with output.open("rb") as f:
        assert not any(f.read(31 * 1600 * 8))
        f.seek((31 * 1600 + track.output_samples - 1) * 8)
        assert any(f.read(8))
        assert not any(f.read(256))


def test_native_global_aac_sample_clock_and_video_copy(tmp_path, registered):
    root, _ = registered
    project = compile_project(json.loads(REQUEST.read_text()), root)
    cancelled = Event()
    private = tmp_path / "private"
    track, snapshot = narration.prepare_narration(project, root, private, cancelled)
    silent = tmp_path / "silent.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi",
                    "-i", "color=c=red:s=64x64:r=30:d=60", "-threads", "1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(silent)], check=True, timeout=30)
    final = tmp_path / "final.mp4"
    proof = narration.mux_narration(track, snapshot, 1800, silent, final, private, cancelled)
    assert proof["passed"] and proof["video_pts_unchanged"] and proof["h264_bitstream_unchanged"]
    assert len(proof["video_pts"]) == 1800
    assert proof["narration"]["trailing_silence_samples"] == 0
    assert proof["effective_samples_per_channel"] == 2_880_000
    assert abs(proof["audible_drift_samples"]) <= 1024
    assert verify_aac_clock(final, 1800)["decoded_audio_clock_gapless"]
    with (private / "decoded.f32").open("rb") as audio:
        audio.seek((900 * 1600 - 1024) * 8)
        assert all(any(audio.read(8 * 1024)) for _ in range(2))
    with pytest.raises(OperationError):
        narration.mux_audio(silent, private / "reference.f32", final, 1800)


@pytest.mark.parametrize("stage", ["mix_pcm", "mux_audio", "verify_audio", "cancel_mix", "cancel_mux"])
def test_global_failures_leave_no_published_or_owned_paths(tmp_path, registered, monkeypatch, stage):
    root, _ = registered
    project = compile_project(json.loads(REQUEST.read_text()), root)
    cancelled = Event()
    def engine(project, parent, registry, cancellation):
        path = parent / "engine"
        path.mkdir()
        (path / "reel.mp4").write_bytes(b"stub")
        (path / "report.json").write_text("{}")
        return {"success": True}

    def fail(*args, **kwargs):
        raise OperationError("INJECTED", "Fault injection")

    monkeypatch.setattr(workflow, "_engine", engine)
    monkeypatch.setattr(workflow, "check_narration_storage", lambda *a: None)
    monkeypatch.setattr(narration, "mix_pcm", lambda *a, **k: None)
    monkeypatch.setattr(narration, "mux_audio", lambda video, pcm, output, *a, **k: output.touch())
    if stage.startswith("cancel"):
        monkeypatch.setattr(narration, "mix_pcm" if stage == "cancel_mix" else "mux_audio",
                            lambda *a, **k: (a[2].touch() if stage == "cancel_mux" else None, cancelled.set()))
    else:
        monkeypatch.setattr(narration, stage, fail)
    foreign = tmp_path / "foreign"
    foreign.write_text("preserve")
    with pytest.raises(OperationError, match="Fault injection|cancelled"):
        workflow.render_project(project, tmp_path / "final", registry_root=root, cancelled=cancelled)
    assert foreign.read_text() == "preserve"
    assert not (tmp_path / "final").exists()
    assert not list(tmp_path.glob(".reelforge-*"))
