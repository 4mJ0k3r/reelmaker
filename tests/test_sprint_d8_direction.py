import copy
import json
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.direction import composition_audit
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/audio'


def meeting():
    data = json.loads((ROOT / 'examples/sprint-d/unexpected_meeting.json').read_text())
    for shot, intent in zip(data['shots'], ('establish', 'react', 'reveal', 'resolve'), strict=True):
        shot['camera'] = 'auto'
        shot['intent'] = intent
    return data


def test_direction_is_deterministic_explained_and_on_existing_grid():
    a = compile_project(meeting(), REGISTRY)
    b = compile_project(meeting(), REGISTRY)
    assert a.timeline() == b.timeline()
    assert [(s.camera, s.focus) for s in a.shots] == [
        ('establishing', 'actor'), ('reaction', 'partner'),
        ('object_reveal', 'actor'), ('two_shot', 'actor')]
    assert all(row['direction']['reason'] for row in a.timeline()['shots'])
    audit = composition_audit(a)
    assert audit == composition_audit(b)
    assert audit['frames_sampled'] == 360
    assert len(audit['shots'][0]['camera_samples']) == 3
    assert all(s.end - s.start == 90 for s in a.shots)


@pytest.mark.parametrize('change', ['unknown', 'movement', 'interaction', 'camera', 'hold', 'focus'])
def test_invalid_intentions_are_actionable(change):
    data = meeting()
    shot = data['shots'][1]
    if change == 'unknown':
        shot['intent'] = 'invent_a_fight'
    elif change == 'movement':
        shot.update(intent='pursue', focus='partner')
    elif change == 'interaction':
        shot['intent'] = 'interact'
    elif change == 'camera':
        shot['camera'] = 'medium'
    elif change == 'hold':
        data['shots'][0]['hold'] = True
    else:
        data['beats'][0].pop('partner')
        data['beats'][0].pop('cue_frame')
        shot['focus'] = 'partner'
    with pytest.raises(InputError) as error:
        compile_project(data, REGISTRY)
    assert error.value.issue.path.startswith('/shots/')


def test_repetition_is_a_warning_and_hold_is_explicit():
    data = meeting()
    data['shots'][1].update(intent='establish', hold=True)
    plan = compile_project(data, REGISTRY)
    row = composition_audit(plan)['shots'][1]
    assert row['repeats_previous_composition'] and row['intentional_hold']
    assert not row['review_repetition']
    data['shots'][1].pop('hold')
    assert composition_audit(compile_project(data, REGISTRY))['shots'][1]['review_repetition']


@pytest.mark.parametrize('file,digest', [
    ('the_answering_light', 'd64f090e1f6ea44133657318105d04ff47ebaf2058b36f6f9b2fa1687ca174f9'),
    ('before_the_storm', '9940d3e5f3e1fddc6d4d1b0a73ceceee398b3e26bfa27cca021c0bd8169d6ef9'),
])
def test_published_d7b_plan_digests_are_preserved(file, digest):
    data = json.loads((ROOT / f'examples/sprint-d7b/{file}.json').read_text())
    assert compile_project(copy.deepcopy(data), REGISTRY).timeline()['plan_sha256'] == digest
