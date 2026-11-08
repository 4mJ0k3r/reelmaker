"""Native-free production contracts, timing and historical planner identities."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
import pytest
from reelforge.core.errors import InputError
from reelforge.unified.contract import compile_request, frame
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'assets/audio'


def request(name='orchard_parcel'):
    return json.loads((ROOT/f'examples/sprint-j/{name}.json').read_text())


@pytest.mark.parametrize('name',['orchard_parcel','white_wind','cinematic_pickup'])
def test_deterministic_plan(name):
    d=request(name)
    a=compile_request(d,REG);b=compile_request(deepcopy(d),REG)
    assert a.timeline==b.timeline
    assert a.frames==d['duration_seconds']*30
    assert d==request(name)


@pytest.mark.parametrize('value,expected',[('0.05',2),('0.016666666',0),('0.016666667',1),('30',900)])
def test_decimal_half_up(value,expected):
    assert frame(value)==expected


@pytest.mark.parametrize('mutation',[
 lambda d:d.update(extra='bad'),
 lambda d:d.update(duration_seconds=120),
 lambda d:d['events'][1].update(start='3.1'),
 lambda d:d['events'][1].update(id=d['events'][0]['id']),
 lambda d:d['events'][0]['required_assets'].append('parcel_01'),
 lambda d:d['events'][0]['forbidden_assets'].append('cinematic_dusk_sky_01'),
 lambda d:d['events'][0]['shots'][0].update(style='run_exit'),
 lambda d:d['events'][0]['shots'][0].update(preset='eval'),
 lambda d:d['script'].update(sha256='0'*64),
 lambda d:d['subtitles'][0].update(lines=['हिन्दी']),
 lambda d:d['subtitles'].append(deepcopy(d['subtitles'][0])),
 lambda d:d['events'][0].update(start='-1'),
 lambda d:d.update(backend='mixed'),
])
def test_reject_before_render(mutation):
    d=request();mutation(d)
    with pytest.raises(InputError):compile_request(d,REG)


def test_parcel_and_escape_coverage():
    a=compile_request(request(),REG).timeline
    assert 'parcel_01' in a['events'][1]['assets']
    b=compile_request(request('white_wind'),REG).timeline
    running=[s for e in b['events'] for s in e['shots'] if 'run_to' in s['actions']]
    assert running and max(s['end_frame'] for s in running)<=900
    assert all('beacon_01' not in e['assets'] for e in b['events'])
