"""Short sequential real-Cairo/FFmpeg failures; never render a long film in CI."""
import json
import shutil
from pathlib import Path
from threading import Event

import pytest

from reelforge.cinematic_projects import workflow
from reelforge.cinematic_projects.contract import load_cinematic_project
from reelforge.core.errors import OperationError
from reelforge.core.trace import LifecycleTrace
from reelforge.media import encoder

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / 'examples/cinematic-projects/pickup_proof.json'
REGISTRY = ROOT / 'assets/audio'


@pytest.mark.parametrize('fault', ['first', 'middle', 'last', 'startup', 'nonzero', 'cancel', 'replace_stage'])
def test_native_fault_is_reaped_unpublished_and_does_not_delete_foreign(tmp_path, monkeypatch, fault):
    pytest.importorskip('cairo')
    if Path('/tmp') in tmp_path.resolve().parents:
        pytest.skip('Use a persistent --basetemp for native admission')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('FFmpeg required')
    project = load_cinematic_project(REQUEST, REGISTRY)
    cancellation = Event()
    sample = workflow.visual_frame
    frame = {'first': 0, 'middle': 90, 'last': 179}.get(fault)

    def draw(plan, index):
        if frame is not None and index == frame:
            raise OperationError('INJECTED_FRAME', f'Fault at {index}')
        if fault == 'cancel' and index == 3:
            cancellation.set()
        if fault == 'replace_stage' and index == 5:
            [stage] = tmp_path.rglob('.reelforge-audio-*')
            stage.rename(stage.with_name(stage.name + '-moved'))
            stage.mkdir()
            (stage / 'foreign-replacement').write_bytes(b'preserve replacement')
        return sample(plan, index)

    monkeypatch.setattr(workflow, 'visual_frame', draw)
    if fault == 'startup':
        def unavailable(*args, **kwargs):
            raise OSError('Controlled startup failure')
        monkeypatch.setattr(encoder.subprocess, 'Popen', unavailable)
    if fault == 'nonzero':
        command = encoder.encoder_command
        monkeypatch.setattr(encoder, 'encoder_command',
                            lambda *a: [*command(*a), '-reelforge-controlled-invalid-option'])
    foreign = tmp_path / 'foreign'
    foreign.write_bytes(b'keep')
    with LifecycleTrace() as trace:
        with pytest.raises(OperationError):
            workflow.render_project(project, tmp_path / 'result', registry_root=REGISTRY,
                                    cancelled=cancellation)
    assert foreign.read_bytes() == b'keep'
    assert not (tmp_path / 'result').exists()
    if fault == 'replace_stage':
        [replacement] = tmp_path.rglob('foreign-replacement')
        assert replacement.read_bytes() == b'preserve replacement'
    else:
        assert list(tmp_path.iterdir()) == [foreign]
    started = {e['child_pid'] for e in trace.events if e['event'] == 'encoder_started'}
    reaped = {e['child_pid'] for e in trace.events if e['event'] == 'encoder_reaped'}
    assert started <= reaped
    # CI artifacts retain exact process/ownership event ordering for every fault.
    evidence = ROOT / 'outputs/d8-d9/native-fault-traces'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / f'{fault}.json').write_text(json.dumps(trace.report(), indent=2)+'\n')


def test_native_cli_sigterm_reaps_encoder_and_refuses_partial_publication(tmp_path):
    import signal
    import subprocess
    import sys
    import time

    pytest.importorskip('cairo')
    if Path('/tmp') in tmp_path.resolve().parents or not shutil.which('ffmpeg'):
        pytest.skip('Persistent native workspace and FFmpeg required')
    output = tmp_path / 'cancelled'
    foreign = tmp_path / 'foreign'
    foreign.write_bytes(b'keep')
    proc = subprocess.Popen([sys.executable, str(ROOT / 'tools/cinematic_project.py'), 'render',
                             str(REQUEST), str(output)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 15
        while not list(tmp_path.rglob('pending.mp4')):
            assert proc.poll() is None, 'Producer exited before signal injection'
            assert time.monotonic() < deadline, 'Encoder did not start within test bound'
            time.sleep(.02)
        proc.send_signal(signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=15)
        assert proc.returncode == 2, (stdout, stderr)
        assert json.loads(stderr)['valid'] is False
        assert not output.exists()
        assert foreign.read_bytes() == b'keep'
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate(timeout=5)
