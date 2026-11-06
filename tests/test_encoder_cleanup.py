"""Deterministic transaction faults and a short native scene smoke test."""

import io
from pathlib import Path
from threading import Event

import pytest

from reelforge.core.errors import OperationError
from reelforge.core.transaction import OwnedDirectory
from reelforge.media import encoder as media


class InputPipe(io.BytesIO):
    def fileno(self):
        return 123


class FakeFFmpeg:
    def __init__(self, command, **_kwargs):
        self.stdin = InputPipe()
        self.stderr = io.BytesIO(b"")
        self.returncode = None
        self.pid = 456
        Path(command[-1]).write_bytes(b"encoded output")

    def poll(self):
        return self.returncode


@pytest.fixture
def encoder_factory(monkeypatch, tmp_path):
    monkeypatch.setattr(media.shutil, "which", lambda path: path)
    monkeypatch.setattr(media, "run_bounded", lambda *a, **k: (0, b"V..... libx264", b""))
    monkeypatch.setattr(media.subprocess, "Popen", FakeFFmpeg)
    monkeypatch.setattr(media.os, "set_blocking", lambda *_: None)

    def stop(proc):
        proc.returncode = -15

    monkeypatch.setattr(media, "stop_process", stop)
    return lambda **kwargs: media.FFmpegEncoder(
        tmp_path / "final.mp4", width=360, height=640, frames=1, **kwargs
    )


def complete(encoder, returncode=0):
    encoder.frames_written = 1
    encoder.proc.returncode = returncode


def test_encoder_owns_staging_through_verification(encoder_factory):
    encoder = encoder_factory()
    with encoder:
        owner = encoder._transaction
        before = owner.path.stat()
        assert before.st_mode & 0o777 == 0o700
        complete(encoder)

        def verify():
            assert encoder.proc.returncode == 0
            assert encoder.proc.stdin.closed and encoder.proc.stderr.closed
            assert not encoder._reader.is_alive()
            assert encoder.output.read_bytes() == b"encoded output"
            assert owner._key(owner.path.stat()) == owner._key(before)
            with pytest.raises(OperationError, match="cleanup did not run"):
                encoder.confirm_cleanup()

        encoder.finish(verify_published=verify)
    assert not owner.path.exists()
    encoder.confirm_cleanup()
    encoder.confirm_cleanup()


def test_external_recreation_after_cleanup_is_preserved(encoder_factory):
    encoder = encoder_factory()
    with encoder:
        owner = encoder._transaction
        complete(encoder)
    assert not owner.path.exists()
    owner.path.mkdir()
    sentinel = owner.path / "foreign"
    sentinel.write_bytes(b"keep")
    with pytest.raises(OperationError, match="reappeared"):
        encoder.confirm_cleanup()
    assert sentinel.read_bytes() == b"keep"


@pytest.mark.parametrize("substitution", ["directory", "symlink", "content"])
def test_unsafe_staging_is_rejected_and_never_swept(tmp_path, substitution):
    owner = OwnedDirectory(tmp_path, "owned-", files=frozenset({"pending.mp4"}))
    original = tmp_path / "original"
    if substitution == "content":
        sentinel = owner.path / "foreign"
        code = "TRANSACTION_CONTENT"
    else:
        owner.path.rename(original)
        sentinel = original / "foreign"
        if substitution == "directory":
            owner.path.mkdir()
            sentinel = owner.path / "foreign"
        else:
            owner.path.symlink_to(original, target_is_directory=True)
        code = "TRANSACTION_IDENTITY"
    sentinel.write_bytes(b"keep")
    with pytest.raises(OperationError) as failure:
        owner.cleanup()
    assert failure.value.code == code
    with pytest.raises(OperationError) as confirmation:
        owner.confirm_cleanup()
    assert confirmation.value is failure.value
    assert sentinel.read_bytes() == b"keep"
    if substitution == "symlink":
        assert owner.path.is_symlink()


def test_verifier_time_replacement_is_rejected(encoder_factory):
    encoder = encoder_factory()
    with pytest.raises(OperationError) as failure:
        with encoder:
            owner = encoder._transaction
            complete(encoder)

            def verify():
                owner.path.rename(owner.path.with_name("moved"))
                owner.path.mkdir()
                (owner.path / "foreign").write_bytes(b"keep")

            encoder.finish(verify_published=verify)
    assert failure.value.code == "TRANSACTION_IDENTITY"
    assert (owner.path / "foreign").read_bytes() == b"keep"


def test_destination_created_during_encode_is_not_clobbered(encoder_factory):
    encoder = encoder_factory()
    with pytest.raises(media.VideoError) as failure:
        with encoder:
            complete(encoder)
            encoder.output.write_bytes(b"existing")
    assert failure.value.code == "OUTPUT_IO"
    assert encoder.output.read_bytes() == b"existing"
    encoder.confirm_cleanup()


@pytest.mark.parametrize(
    ("case", "code"),
    [("early_exit", "ENCODER_EXIT"), ("incomplete", "FRAME_COUNT"), ("cancel", "CANCELLED")],
)
def test_unsuccessful_encode_is_not_published(encoder_factory, case, code):
    event = Event()
    encoder = encoder_factory(cancelled=event)
    with pytest.raises(OperationError) as failure:
        with encoder:
            if case != "incomplete":
                complete(encoder, returncode=1 if case == "early_exit" else 0)
            if case == "cancel":
                event.set()
    assert failure.value.code == code
    assert not encoder.output.exists()
    encoder.confirm_cleanup()


def test_failed_verification_releases_owned_staging(encoder_factory):
    encoder = encoder_factory()
    with pytest.raises(media.VideoError, match="decode failed"):
        with encoder:
            complete(encoder)

            def reject():
                raise media.VideoError("DECODE_FAILED", "decode failed")

            encoder.finish(verify_published=reject)
    encoder.confirm_cleanup()


def test_failed_child_start_cleans_partial_initialization(encoder_factory, monkeypatch):
    encoder = encoder_factory()

    def fail(*_args, **_kwargs):
        raise OSError("cannot spawn")

    monkeypatch.setattr(media.subprocess, "Popen", fail)
    with pytest.raises(OSError, match="cannot spawn"):
        with encoder:
            pytest.fail("entry should fail")
    assert not encoder.output.exists()
    encoder.confirm_cleanup()


@pytest.mark.parametrize("replace_staging", [False, True])
def test_scene_caller_reports_cleanup_outcome(tmp_path, monkeypatch, replace_staging):
    import shutil
    import sys
    from dataclasses import replace

    pytest.importorskip("cairo")
    if Path("/tmp") in tmp_path.resolve().parents:
        pytest.skip("Use --basetemp outside /tmp for the native workspace preflight")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg tools are required")
    from reelforge.scenes.graph import compile_scene
    from reelforge.visual_library.composition.farm import farm_scene

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "tools"))
    monkeypatch.delitem(sys.modules, "scene", raising=False)
    from scene import render_scene

    # Normal render path with three genuinely distinct, changing frames.
    scene = compile_scene(replace(farm_scene("approach"), frames=3))
    output = tmp_path / "scene"
    if replace_staging:
        import json

        from reelforge.media import verify

        original_verify = verify.verify_video

        def inject(*args, **kwargs):
            result = original_verify(*args, **kwargs)
            (stage,) = output.glob(".reelforge-encode-*")
            stage.rename(output / "retained-original")
            stage.mkdir()
            (stage / "foreign").write_bytes(b"keep")
            return result

        monkeypatch.setattr(verify, "verify_video", inject)
        with pytest.raises(OperationError) as failure:
            render_scene(scene, output)
        assert failure.value.code == "TRANSACTION_IDENTITY"
        result = json.loads((output / "render_report.json").read_text())
        assert not result["success"]
        assert result["cleanup_error"]["code"] == failure.value.code
        assert next(output.glob(".reelforge-encode-*/foreign")).read_bytes() == b"keep"
    else:
        result = render_scene(scene, output)
        assert result["success"] and result["cleanup_error"] is None
        assert not list(output.glob(".reelforge-encode-*"))
    assert result["verification"]["decoded_frames"] == 3
    assert result["live_surfaces_after"] == 0
