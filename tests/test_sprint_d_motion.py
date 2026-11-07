"""Measured contacts for both authored rigs and their preserved transitions."""

import pytest

from reelforge.characters import living, living_transitions
from tools.sprint_d_contacts import evaluate


def test_refined_gait_improves_interactions_without_moving_the_hand_socket():
    before, after = evaluate(False), evaluate(True)
    for actor in living.PROFILES:
        for action in ("pickup_carry_place", "push_cart"):
            original, refined = before[actor][action], after[actor][action]
            assert original["max_adjacent_drift"] > 1.0
            assert refined["max_adjacent_drift"] < 1e-8
            assert refined["grounded_pairs"] >= original["grounded_pairs"]
            assert refined["max_hand_socket_error"] < 1e-8


@pytest.mark.parametrize("actor", living.PROFILES)
@pytest.mark.parametrize("transition", living_transitions.TRANSITIONS)
def test_refined_transitions_are_finite_and_hold_grounded_feet(actor, transition):
    previous = None
    for frame in range(90):
        sample = living_transitions.sample_transition(actor, transition, frame, refined=True)
        assert max(abs(sample.pose.root.x), abs(sample.pose.root.y)) < 120
        for index, planted in enumerate(sample.planted):
            if planted and previous and previous.planted[index]:
                assert sample.feet[index] == pytest.approx(previous.feet[index], abs=1e-8)
        previous = sample
