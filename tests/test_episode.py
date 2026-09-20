"""The loop of section 2, in the page's order, against a scripted door."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from world_fixtures import act, appendix, spec
from wald import belief as B
from wald.episode import Door, run
from wald.world import declare


class Script(Door):
    "Plays back raw outcomes and records what the loop asked of it, in order."

    def __init__(self, *values):
        self.values = list(values)
        self.calls = []

    def outcome(self, a):
        self.calls.append(("outcome", a))
        return self.values.pop(0)

    def fire(self, a):
        self.calls.append(("fire", a))


def play(s, *values):
    door = Script(*values)
    return run(declare(s), door), door


class Order(unittest.TestCase):
    def test_the_appendix_episode(self):
        for value, terminal in (("+", "treat"), ("-", "leave")):
            r, door = play(appendix(), value)
            self.assertEqual(r.acts, ("test", terminal))
            self.assertEqual(r.outcomes, (value,))
            self.assertEqual(r.status, "TERMINAL")
            self.assertEqual(r.paid, F(1, 2))
            self.assertEqual(door.calls, [("outcome", "test"), ("fire", terminal)])

    def test_a_terminal_act_is_fired_by_the_door_and_nothing_is_paid(self):
        "Priced above the range of the utilities, the look is never bought (C9b)."
        r, door = play(appendix(F(11)))
        self.assertEqual(r.acts, ("treat",))
        self.assertEqual(r.paid, F(0))
        self.assertEqual(door.calls, [("fire", "treat")])

    def test_a_once_act_leaves_the_menu(self):
        r, _ = play(appendix(F(1, 10), True, 2, 2), "+")
        self.assertEqual(r.acts, ("test", "treat"))
        self.assertEqual(r.paid, F(1, 10))

    def test_a_fresh_act_may_be_executed_again(self):
        r, door = play(appendix(F(1, 10), False, 2, 2), "+", "+")
        self.assertEqual(r.acts[:2], ("test", "test"))
        self.assertEqual(r.paid, F(1, 5))
        self.assertEqual([c for c in door.calls if c[0] == "outcome"], [("outcome", "test")] * 2)

    def test_the_horizon_binds_and_the_floor_is_what_is_played(self):
        "N = 2, d = 1: two blank peeks at decide_1, then the terminal act (E3)."
        Kh = {"x": {"sx": F(1, 2), "sy": F(0), "blank": F(1, 2)},
              "y": {"sx": F(0), "sy": F(1, 2), "blank": F(1, 2)}}
        H = spec({"x": F(1, 2), "y": F(1, 2)},
                 {"X": {"x": F(1), "y": F(0)}, "Y": {"x": F(0), "y": F(1)}},
                 {"peek": act(Kh, F(1, 10), False)}, N=2, d=1)
        r, door = play(H, "blank", "blank")
        self.assertEqual(r.acts, ("peek", "peek", "X"))
        self.assertEqual(r.paid, F(1, 5))
        self.assertEqual(len([c for c in door.calls if c[0] == "outcome"]), 2)


SAY = {"say-a": {"a": F(1), "b": F(0)}, "say-b": {"a": F(0), "b": F(1)}}


class ZeroEvidenceAndEndings(unittest.TestCase):
    def test_a_zero_mass_outcome_falsifies_the_world_before_it_can_end_the_episode(self):
        "S5: the price is already paid, the belief is not touched, and nothing is fired."
        K = {"a": {"x": F(1), "y": F(0), "hit": F(0)}, "b": {"x": F(0), "y": F(1), "hit": F(0)}}
        Z = spec({"a": F(1, 2), "b": F(1, 2)}, SAY,
                 {"probe": act(K, F(1, 10), True, {"hit": {"a": F(100), "b": F(100)}})})
        r, door = play(Z, "hit")
        self.assertEqual(r.status, "WORLD_FALSIFIED")
        self.assertEqual(r.paid, F(1, 10))
        self.assertEqual(B.expect(r.final, {"a": F(1), "b": F(0)}), F(1, 2))
        self.assertNotIn(("fire", "say-a"), door.calls)
        self.assertEqual([c for c in door.calls if c[0] == "fire"], [])

    def test_an_ending_outcome_is_conditioned_on_first_then_ends_the_episode(self):
        K = {"a": {"hit": F(1), "miss": F(0)}, "b": {"hit": F(0), "miss": F(1)}}
        W = spec({"a": F(1, 2), "b": F(1, 2)}, SAY,
                 {"probe": act(K, F(1, 10), True, {"hit": {"a": F(1), "b": F(1)}})})
        r, door = play(W, "hit")
        self.assertEqual(r.status, "ENDED")
        self.assertEqual(B.expect(r.final, {"a": F(1), "b": F(0)}), F(1))
        self.assertEqual([c for c in door.calls if c[0] == "fire"], [])

    def test_a_non_ending_outcome_of_the_same_act_plays_on(self):
        K = {"a": {"hit": F(1, 2), "miss": F(1, 2)}, "b": {"hit": F(0), "miss": F(1)}}
        W = spec({"a": F(1, 2), "b": F(1, 2)}, SAY,
                 {"probe": act(K, F(1, 10), True, {"hit": {"a": F(1), "b": F(1)}})})
        r, _ = play(W, "miss")
        self.assertEqual(r.status, "TERMINAL")
        self.assertEqual(r.acts, ("probe", "say-b"))
