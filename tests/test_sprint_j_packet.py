"""Operator runner tests use a FAKE CLI, no native render or production claims."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('packet_runner',ROOT/'tools/render_sprint_j_packet.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def build(tmp_path,refuse=False):
    engine=tmp_path/'engine';(engine/'tools').mkdir(parents=True)
    # The untracked calls log is deliberate; renderer invocation is only a test sentinel.
    source='''import sys,json
from pathlib import Path
phase=sys.argv[3]
with Path('calls.txt').open('a') as f:f.write(phase+'\\n')
if phase=='plan':print(json.dumps({'plan_sha256':'approved'}))
else:print('{}')
if phase=='preflight' and REFUSE:sys.exit(2)
if phase=='render':raise AssertionError('FAKE CLI must never render in operator tests')
'''.replace('REFUSE',str(refuse))
    (engine/'tools/reel_production.py').write_text(source)
    subprocess.run(['git','init','-q',str(engine)],check=True)
    subprocess.run(['git','-C',str(engine),'add','.'],check=True)
    subprocess.run(['git','-C',str(engine),'-c','user.name=Unit','-c','user.email=unit@example.invalid','commit','-qm','fake CLI unit fixture'],check=True)
    rev=lambda r:subprocess.check_output(['git','-C',str(engine),'rev-parse',r],text=True).strip()
    packet=tmp_path/'packet';(packet/'productions/synthetic_registry').mkdir(parents=True)
    request=packet/'productions/story.json'
    request.write_text(json.dumps({'narration':{'provenance':'synthetic_timing_fixture'}}))
    data={'schema_version':'sprint-j-qualification-packet-0.1','engine_commit':rev('HEAD'),'engine_tree':rev('HEAD^{tree}'),
          'requests':['story'],'plan_sha256':{'story':'approved'},'sha256':{'productions/story.json':runner.sha(request)}}
    (packet/'packet.json').write_text(json.dumps(data))
    output=tmp_path/'output';output.mkdir()
    return engine,packet,output,data


def test_refused_preflight_never_reaches_render(tmp_path):
    engine,packet,out,_=build(tmp_path,refuse=True)
    with pytest.raises(RuntimeError,match='preflight failed'):
        runner.run_packet(engine,packet,out,Path(sys.executable))
    calls=(engine/'calls.txt').read_text().splitlines()
    assert calls==['capabilities','validate','plan','inspect','preflight']
    result=json.loads(next(out.glob('*/packet_result.json')).read_text())
    assert result['success'] is False and result['completed_films']==[]


def test_check_only_requires_preflight_and_preserves_logs(tmp_path):
    engine,packet,out,_=build(tmp_path)
    result=runner.run_packet(engine,packet,out,Path(sys.executable),check_only=True)
    assert result['success'] and result['completed_films']==[]
    assert 'render' not in (engine/'calls.txt').read_text().splitlines()


@pytest.mark.parametrize('damage',['hash','commit','dirty','voice'])
def test_invalid_packet_refused_before_cli(tmp_path,damage):
    engine,packet,out,data=build(tmp_path)
    request=packet/'productions/story.json'
    if damage=='hash':request.write_text('{}')
    if damage=='commit':data['engine_commit']='0'*40
    if damage=='dirty':(engine/'tools/reel_production.py').write_text('changed')
    if damage=='voice':
        request.write_text(json.dumps({'narration':{'provenance':'user_finished_recording'}}))
        data['sha256']['productions/story.json']=runner.sha(request)
    (packet/'packet.json').write_text(json.dumps(data))
    with pytest.raises(ValueError):runner.run_packet(engine,packet,out,Path(sys.executable),check_only=True)
    assert not (engine/'calls.txt').exists()
    assert not list(out.iterdir())


def test_symlink_operator_path_refused(tmp_path):
    engine,packet,out,_=build(tmp_path)
    link=tmp_path/'link';link.symlink_to(packet,target_is_directory=True)
    with pytest.raises(ValueError):runner.run_packet(engine,link,out,Path(sys.executable),check_only=True)
