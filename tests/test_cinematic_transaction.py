"""Failure injection at the cinematic package boundary and trusted render adapter."""

from pathlib import Path

import pytest

from reelforge.cinematic_projects import workflow
from reelforge.cinematic_projects.contract import load_cinematic_project
from reelforge.core.errors import OperationError
from reelforge.core.transaction import OwnedDirectory

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples/cinematic-projects/pickup_proof.json"
REGISTRY = ROOT / "assets/audio"


def boom(*args, **kwargs):
    raise OperationError("INJECTED", "Injected fault")


class Monitor:
    initial = final = {}
    oom_telemetry_continuous = True

    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def report(self):
        return {}


@pytest.fixture
def staged(monkeypatch):
    def engine(project, stage, registry, cancelled):
        directory = stage / "engine"
        directory.mkdir()
        (directory / "reel.mp4").write_bytes(b"fixture payload")
        (directory / "report.json").write_text("{}")
        return dict(success=True, streams={}, verification={})

    for name, substitute in {
        "preflight_memory": lambda: None,
        "check_workspace": lambda path: None,
        "JobMonitor": Monitor,
        "memory_observability": lambda a, b: {"oom_events_changed": False},
        "_engine": engine,
        "black_frames": lambda *a: {},
        "write_storyboard": lambda *a: [],
        "verify_project": lambda *a, **kw: {"verified": True},
    }.items():
        monkeypatch.setattr(workflow, name, substitute)


@pytest.mark.parametrize(
    "stage",
    [
        "preflight_memory",
        "_engine",
        "stream_check",
        "black_frames",
        "write_storyboard",
        "verify_project",
        "_write_json",
        "report",
        "publish_as",
    ],
)
def test_fault_leaves_no_successful_package_or_staging(tmp_path, monkeypatch, staged, stage):
    if stage == "publish_as":
        monkeypatch.setattr(OwnedDirectory, stage, boom)
    elif stage == "report":
        real = workflow._write_json

        def writer(path, content):
            if path == path.parent / "report.json":
                boom()
            real(path, content)

        monkeypatch.setattr(workflow, "_write_json", writer)
    elif stage == "stream_check":
        engine = workflow._engine

        def without_streams(*args):
            result = engine(*args)
            del result["streams"]
            return result

        monkeypatch.setattr(workflow, "_engine", without_streams)
        monkeypatch.setattr(workflow, stage, boom)
    else:
        monkeypatch.setattr(workflow, stage, boom)
    foreign = tmp_path / "foreign.mp4"
    foreign.write_bytes(b"untouched")
    with pytest.raises(OperationError, match="Injected fault"):
        workflow.render_project(
            load_cinematic_project(REQUEST, REGISTRY), tmp_path / "final", registry_root=REGISTRY
        )
    assert list(tmp_path.iterdir()) == [foreign]
    assert foreign.read_bytes() == b"untouched"


def test_rename_refuses_even_empty_directory_that_appears_at_publication(
    tmp_path, monkeypatch, staged
):
    target = tmp_path / "final"
    publish = OwnedDirectory.publish_as

    def race(owner, destination):
        destination.mkdir()
        return publish(owner, destination)

    monkeypatch.setattr(OwnedDirectory, "publish_as", race)
    with pytest.raises(OperationError, match="Choose a new output directory"):
        workflow.render_project(
            load_cinematic_project(REQUEST, REGISTRY), target, registry_root=REGISTRY
        )
    assert target.is_dir() and list(target.iterdir()) == []
    assert list(tmp_path.iterdir()) == [target]


def test_replaced_stage_is_neither_removed_nor_published(tmp_path):
    owner = OwnedDirectory(tmp_path, ".test-")
    moved = tmp_path / "moved"
    owner.path.rename(moved)
    owner.path.mkdir()
    (owner.path / "foreign").write_text("preserve")
    with pytest.raises(OperationError, match="identity changed"):
        owner.publish_as(tmp_path / "final")
    with pytest.raises(OperationError, match="identity changed"):
        owner.cleanup()
    assert moved.is_dir()
    assert (owner.path / "foreign").read_text() == "preserve"
    assert not (tmp_path / "final").exists()


@pytest.mark.parametrize("fault_frame", [0, 90, 179])
def test_episode_adapter_propagates_errors_at_any_render_frame(monkeypatch, tmp_path, fault_frame):
    project = load_cinematic_project(REQUEST, REGISTRY)

    def frames(project, frame):
        if frame == fault_frame:
            boom()
        return ()

    def encode(count, sample, *_args, **_kwargs):
        for frame in range(count):
            sample(frame)

    def av(plan, output, *, visual_plan, render_silent, cancelled, **kwargs):
        return render_silent(visual_plan, output, encoder_staging=tmp_path, cancelled=cancelled)

    monkeypatch.setattr(workflow, "visual_frame", frames)
    monkeypatch.setattr(workflow, "encode_episode_frames", encode)
    monkeypatch.setattr(workflow, "render_av", av)
    with pytest.raises(OperationError, match="Injected fault"):
        workflow.render_episode_slice(
            workflow.EpisodeSlice(project, 0, 180), tmp_path, registry_root=REGISTRY, cancelled=None
        )


def test_package_allowlist_excludes_native_staging(tmp_path):
    source = tmp_path / "native"
    source.mkdir()
    for name in ("report.json", "reel.mp4", ".stray-staging"):
        (source / name).write_text(name)
    destination = tmp_path / "package"
    workflow._collect_engine(source, destination, {})
    assert {p.name for p in destination.iterdir()} == {"report.json", "reel.mp4"}
    assert (source / ".stray-staging").read_text() == ".stray-staging"


@pytest.mark.parametrize("damage", ["missing", "corrupt"])
def test_native_audio_registry_damage_refuses_publication(damage):
    import shutil
    import tempfile

    from reelforge.cinematic_projects.contract import compile_project
    from reelforge.contracts.project import load_project

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and ffprobe are required")
    request = load_project(REQUEST)
    request["audio"] = {
        "sample_rate": 48000,
        "channels": 2,
        "codec": "aac",
        "bitrate": 128000,
        "narration": None,
        "cues": [
            {
                "asset_id": "diag_fence",
                "start_frame": 87,
                "trim_start_frame": 0,
                "trim_end_frame": 10,
                "gain": 0.25,
            }
        ],
    }
    with tempfile.TemporaryDirectory(prefix="cinematic-audio-test-", dir=ROOT / "outputs") as tmp:
        root = Path(tmp)
        registry = root / "registry"
        shutil.copytree(REGISTRY, registry)
        project = compile_project(request, registry)
        audio = registry / "diag_fence.wav"
        if damage == "missing":
            audio.unlink()
        else:
            with audio.open("r+b") as handle:
                handle.seek(100)
                sample = handle.read(1)
                handle.seek(100)
                handle.write(bytes([sample[0] ^ 1]))
        with pytest.raises(OperationError, match="registry_validation"):
            workflow.render_project(project, root / "final", registry_root=registry)
        assert list(root.iterdir()) == [registry]


def test_success_contains_verification_before_atomic_publish(tmp_path, monkeypatch, staged):
    publish = OwnedDirectory.publish_as
    observed = []

    def inspect(owner, destination):
        import json
        assert json.loads((owner.path / 'verification.json').read_text())['verified']
        assert (owner.path / 'report.json').is_file()
        observed.append(True)
        return publish(owner, destination)

    monkeypatch.setattr(OwnedDirectory, 'publish_as', inspect)
    workflow.render_project(load_cinematic_project(REQUEST, REGISTRY), tmp_path / 'final',
                            registry_root=REGISTRY)
    assert observed == [True]
    assert (tmp_path / 'final/verification.json').exists()
