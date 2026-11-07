import json
from pathlib import Path

import pytest

from reelforge.characters import living, living_transitions
from reelforge.cinematic_projects.contract import compile_project
from reelforge.cinematic_projects.sampling import state_at, visual_frame
from reelforge.cinematic_projects.staging import PACING, Performer, performer_clock, pose_at
from reelforge.core.errors import InputError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/audio'


def data(style):
    d = json.loads((ROOT / 'examples/sprint-d8-d9/directed_discovery.json').read_text())
    d['beats'][0]['pacing'] = style
    return d


def test_pacing_has_real_distinct_clocks_and_held_endpoints():
    poses = []
    for style in PACING:
        performer = Performer('scout_01', 'idle_to_notice', 'concerned', 'right', 0, style)
        poses.append(pose_at(performer, 30, refined=True))
        assert pose_at(performer, 300, refined=True) == pose_at(performer, 359, refined=True)
    assert len(set(poses)) == 3


@pytest.mark.parametrize('style', PACING)
def test_clocks_do_not_reset_at_cut_and_sampling_is_random_access(style):
    p = compile_project(data(style), REGISTRY)
    for index in (89, 90, 179, 180, 269, 270):
        s = state_at(p, index)
        assert s['beat_frame'] == index
    sample = visual_frame(p, 270)
    visual_frame(p, 3)
    assert visual_frame(p, 270) == sample
    assert p.frames == 360
    assert p.timeline() == compile_project(data(style), REGISTRY).timeline()
    assert state_at(p, 179)['root_world'] == state_at(p, 180)['root_world']


@pytest.mark.parametrize('actor', living.PROFILES)
@pytest.mark.parametrize('style', PACING)
def test_paced_transition_keeps_planted_world_feet(actor, style):
    for transition in living_transitions.TRANSITIONS:
        performer = Performer(actor, transition, 'concerned', 'right', 0, style)
        previous = None
        for local in range(180):
            clock, active = performer_clock(performer, local)
            if not active:
                continue
            sample = living_transitions.sample_transition(actor, transition, min(89, clock), refined=True)
            if previous:
                for index in range(2):
                    if previous.planted[index] and sample.planted[index]:
                        assert sample.feet[index] == pytest.approx(previous.feet[index], abs=1e-8)
            previous = sample


def test_interactions_reject_pacing_instead_of_moving_contact_clocks():
    d = json.loads((ROOT / 'examples/sprint-d/pickup_refined.json').read_text())
    d['beats'][0]['pacing'] = 'urgent'
    with pytest.raises(InputError, match='fixed contact clock'):
        compile_project(d, REGISTRY)


def test_partner_can_override_pacing_without_changing_lead_clock():
    d = data('measured')
    p = compile_project(d, REGISTRY)
    before = state_at(p, 110)
    d['beats'][0]['partner']['pacing'] = 'urgent'
    after = state_at(compile_project(d, REGISTRY), 110)
    assert before['root_world'] == after['root_world']
    assert before['partner']['authored_frame'] != after['partner']['authored_frame']
