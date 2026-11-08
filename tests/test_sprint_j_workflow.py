"""Transaction fault tests with fake media; never represent these as render qualification."""
import json
from copy import deepcopy
from pathlib import Path
from threading import Event
import pytest
from reelforge.core.errors import OperationError, InputError
from reelforge.unified import workflow as w
from reelforge.unified.contract import compile_request
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def plan():
    return compile_request(json.loads((ROOT/'examples/sprint-j/orchard_parcel.json').read_text()),ROOT/'assets/audio')


def test_json_roundtrip_plan(plan):
    assert json.loads(json.dumps(plan.timeline))==plan.timeline


def test_actual_host_admission_refuses_without_publication(tmp_path,plan):
    from reelforge.resources.monitor import memory_snapshot
    if memory_snapshot()['effective_available_bytes']>=320*1024**2:
        pytest.skip('This host can admit a job; refusal test requires absent/insufficient telemetry')
    target=tmp_path/'blocked'
    with pytest.raises(OperationError,match='headroom'):
        w.render(plan,target,ROOT/'assets/audio')
    assert not target.exists()
    assert not list(tmp_path.glob('.reelforge-*'))


def test_preflight_does_not_probe_native_before_memory_admission(tmp_path,plan,monkeypatch):
    def refuse():raise OperationError('MEMORY_PREFLIGHT','injected missing telemetry')
    monkeypatch.setattr(w,'preflight_memory',refuse)
    monkeypatch.setattr(w,'resolve_audio',lambda *a,**k:pytest.fail('audio before memory admission'))
    with pytest.raises(OperationError,match='telemetry'):
        w.preflight(plan,tmp_path/'new',ROOT/'assets/audio')


@pytest.mark.parametrize('stage',['engine','storyboard','verify','cancel'])
def test_faults_publish_nothing_and_preserve_foreign(tmp_path,plan,monkeypatch,stage):
    class Monitor:
        def __init__(self,**kw):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def report(self):return {'test_only':True}
    cancellation=Event()
    monkeypatch.setattr(w,'compile_request',lambda *a:deepcopy(plan))
    monkeypatch.setattr(w,'preflight_memory',lambda:None)
    monkeypatch.setattr(w,'check_narration_storage',lambda *a:None)
    monkeypatch.setattr(w,'JobMonitor',Monitor)
    monkeypatch.setattr(w,'_resource_gate',lambda *a:None)
    def fault(*args,**kwargs):raise OperationError('INJECTED',stage)
    def engine(p,out,*a):
        out.mkdir();(out/'reel.mp4').write_bytes(b'fake-unit-media')
        if stage=='cancel':cancellation.set()
        return {'success':True}
    monkeypatch.setattr(w,'_visual',fault if stage=='engine' else engine)
    monkeypatch.setattr(w,'write_storyboard',fault if stage=='storyboard' else lambda *a:[])
    monkeypatch.setattr(w,'verify',fault)
    from reelforge.mvp import asset_audit
    monkeypatch.setattr(asset_audit,'audit_assets',lambda *a:{'test_only':True})
    foreign=tmp_path/'foreign';foreign.write_text('keep')
    with pytest.raises(OperationError):
        w.render(plan,tmp_path/'delivery',ROOT/'assets/audio',cancellation)
    assert not (tmp_path/'delivery').exists()
    assert foreign.read_text()=='keep'
    assert not list(tmp_path.glob('.reelforge-*'))


def test_occupied_output_untouched(tmp_path,plan):
    out=tmp_path/'occupied';out.mkdir();(out/'keep').write_text('keep')
    with pytest.raises(OperationError,match='new output'):
        w.render(plan,out,ROOT/'assets/audio')
    assert (out/'keep').read_text()=='keep'


def test_symlink_and_traversal(tmp_path,plan):
    from reelforge.cinematic_projects.operator import output_destination
    (tmp_path/'link').symlink_to(tmp_path,target_is_directory=True)
    for path in (tmp_path/'link'/'new', tmp_path/'..'/'new'):
        with pytest.raises(OperationError):output_destination(path)


def test_production_path_outside_engine(plan):
    with pytest.raises(OperationError,match='outside the engine'):
        w.private_destination(plan,ROOT/'outputs'/'sprint_j_forbidden',ROOT/'assets/audio')


def test_insufficient_storage_creates_nothing(tmp_path,plan,monkeypatch):
    monkeypatch.setattr(w,'compile_request',lambda *a:deepcopy(plan))
    monkeypatch.setattr(w,'preflight_memory',lambda:None)
    def full(*args):raise OperationError('WORKSPACE_SPACE','injected disk full')
    monkeypatch.setattr(w,'check_narration_storage',full)
    with pytest.raises(OperationError,match='disk full'):
        w.render(plan,tmp_path/'new',ROOT/'assets/audio')
    assert not list(tmp_path.iterdir())


def test_atomic_success_with_fake_media_only(tmp_path,plan,monkeypatch):
    class Monitor:
        def __init__(self,**kw):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def report(self):return {'fake_media_unit_test':True}
    monkeypatch.setattr(w,'compile_request',lambda *a:deepcopy(plan))
    monkeypatch.setattr(w,'preflight_memory',lambda:None)
    monkeypatch.setattr(w,'check_narration_storage',lambda *a:None)
    monkeypatch.setattr(w,'JobMonitor',Monitor)
    monkeypatch.setattr(w,'_resource_gate',lambda *a:None)
    def engine(p,out,*a):
        out.mkdir();(out/'reel.mp4').write_bytes(b'fake-media-not-a-film')
        return {'success':True}
    monkeypatch.setattr(w,'_visual',engine)
    monkeypatch.setattr(w,'write_storyboard',lambda *a:[])
    monkeypatch.setattr(w,'verify',lambda *a,**k:{'unit_test_only':True})
    from reelforge.mvp import asset_audit
    monkeypatch.setattr(asset_audit,'audit_assets',lambda *a:{'unit_test_only':True})
    out=tmp_path/'complete'
    report=w.render(plan,out,ROOT/'assets/audio')
    assert report['success']
    assert (out/'verification.json').is_file()
    assert (out/'reel.mp4').read_bytes()==b'fake-media-not-a-film'
    assert json.loads((out/'plan.json').read_text())==plan.timeline
    assert not list(tmp_path.glob('.reelforge-*'))


@pytest.mark.parametrize('kind',['exception','report'])
def test_nested_ownership_uncertainty_preserves_child_work(tmp_path,plan,monkeypatch,kind):
    """No native media: a child renderer can preserve a subtree inside our stage."""
    class Monitor:
        def __init__(self,**kw):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
    monkeypatch.setattr(w,'compile_request',lambda *a:deepcopy(plan))
    monkeypatch.setattr(w,'preflight_memory',lambda:None)
    monkeypatch.setattr(w,'check_narration_storage',lambda *a:None)
    monkeypatch.setattr(w,'JobMonitor',Monitor)
    retained=[]
    def engine(p,out,*args):
        out.mkdir()
        child=out.parent/'child-preserved'
        child.mkdir();(child/'ownership-evidence').write_text('must survive')
        retained.append(child)
        if kind=='exception':
            raise OperationError('CINEMATIC_OWNERSHIP','child native ownership uncertain')
        return {'success':False,'cleanup_error':{'code':'TRANSACTION_PRESERVED'}}
    monkeypatch.setattr(w,'_visual',engine)
    with pytest.raises(OperationError):w.render(plan,tmp_path/'delivery',ROOT/'assets/audio')
    assert not (tmp_path/'delivery').exists()
    assert (retained[0]/'ownership-evidence').read_text()=='must survive'
    # Preserved resources belong to investigation; the production code must not delete them.


def test_preflight_requires_continuous_oom_accounting(tmp_path,plan,monkeypatch):
    class Monitor:
        oom_telemetry_continuous=False
        def __init__(self,**kw):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
    monkeypatch.setattr(w,'preflight_memory',lambda:None)
    monkeypatch.setattr(w,'check_narration_storage',lambda *a:None)
    monkeypatch.setattr(w,'JobMonitor',Monitor)
    with pytest.raises(OperationError,match='OOM telemetry'):
        w.preflight(plan,tmp_path/'delivery',ROOT/'assets/audio')
    assert not list(tmp_path.iterdir())
