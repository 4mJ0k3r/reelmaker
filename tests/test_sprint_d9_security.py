import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/audio'


def source():
    return json.loads((ROOT/'examples/sprint-d8-d9/directed_discovery.json').read_text())


@pytest.mark.parametrize('case', ['unknown_key','duplicate_id','same_actor','version','duration',
                                  'camera','audio_id','traversal_audio','long_text','mood','nonfinite'])
def test_rejects_untrusted_or_unbounded_project_values(case):
    d=source()
    if case=='unknown_key':d['execute']='os.system'
    elif case=='duplicate_id':d['shots'][1]['id']=d['shots'][0]['id']
    elif case=='same_actor':d['beats'][0]['partner']['actor']=d['beats'][0]['actor']
    elif case=='version':d['schema_version']='cinematic-project-untrusted'
    elif case=='duration':d['shots']=d['shots']*30
    elif case=='camera':d['shots'][0]['camera']={'zoom':1e30}
    elif case in ('audio_id','traversal_audio'):
        d['audio']={'sample_rate':48000,'channels':2,'codec':'aac','bitrate':128000,'narration':None,
                    'cues':[{'asset_id':'missing' if case=='audio_id' else '../foreign',
                             'start_frame':0,'trim_start_frame':0,'trim_end_frame':1,'gain':.1}]}
    elif case=='long_text':d['captions']=[{'start':0,'end':90,'style':'subtitle','lines':['X'*10000]}]
    elif case=='mood':d['beats'][0]['mood']='morning'
    else:d['beats'][0]['stage_x']=float('nan')
    with pytest.raises((InputError,ValueError)):
        compile_project(d,REGISTRY)


@pytest.mark.parametrize('payload', ['{"schema_version":NaN}', '{"a":1,"a":2}', '{"a":1e999}', '['*40+']'*40, 'x'*1048577],
                         ids=['nan', 'duplicate-key', 'numeric-overflow', 'deep-nesting', 'oversized'])
def test_cli_bounds_json_and_returns_actionable_error(tmp_path,payload):
    path=tmp_path/'input.json';path.write_text(payload)
    r=subprocess.run([sys.executable,str(ROOT/'tools/cinematic_project.py'),'validate',str(path)],
                     capture_output=True,text=True)
    assert r.returncode==2
    error=json.loads(r.stderr)['error']
    assert error['code'] in ('JSON_NONFINITE','JSON_DUPLICATE_KEY','JSON_INVALID','INPUT_TOO_LARGE')


def test_legacy_schema_does_not_admit_new_pacing_or_intentions():
    d=json.loads((ROOT/'examples/cinematic-projects/variant_misty_creek.json').read_text())
    d['beats'][0]['pacing']='urgent'
    with pytest.raises(InputError):compile_project(copy.deepcopy(d),REGISTRY)


def test_workspace_write_probe_never_removes_a_replaced_foreign_file(monkeypatch):
    import tempfile
    from reelforge.resources import deployment
    from reelforge.core.errors import OperationError

    with tempfile.TemporaryDirectory(prefix='probe-test-', dir=ROOT / 'outputs') as folder:
        workspace = Path(folder)
        real = deployment.os.fsync
        replaced = []
        def substitute(fd):
            real(fd)
            [path] = workspace.glob('.reelforge-write-check-*')
            path.rename(workspace / 'original-probe')
            path.write_bytes(b'foreign replacement')
            replaced.append(path)
        monkeypatch.setattr(deployment.os, 'fsync', substitute)
        with pytest.raises(OperationError) as error:
            deployment.check_workspace(workspace, minimum_free_bytes=0)
        assert error.value.code == 'WORKSPACE_IDENTITY'
        assert replaced[0].read_bytes() == b'foreign replacement'
