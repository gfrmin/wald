"""The three fast paths of CHARTER E2, each held to the thing it replaces.

They are allowed to replace `push`, `condition` and expectation and nothing else, and they must
be exact: not close, not close enough to pick the same act on the worlds I happened to try. The
act differential against the oracle (test_differential.py) is the real net; these are the traps I
set where each fast path could be wrong on its own terms.
"""
import pathlib
import random
import unittest
from fractions import Fraction as F

import _path
import world_fixtures as W
from wald.belief import _dot, _mass, _measure, _split, _update, _weights, expect, prior, push
from wald.decide import decide, value
from wald.world import declare

S = _path.oracle()


def _world(spec):
    return declare(spec)


class TheUnnormalisedMeasure(unittest.TestCase):
    """`_split` is `push` and `condition` in one pass with the division left out. Putting the
    division back must give exactly what the two verbs give."""

    def worlds(self, seed, count):
        import test_differential as D
        rng = random.Random(seed)
        return [D.rand_world(rng) for _ in range(count)]

    @unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
    def test_a_split_is_the_predictive_and_every_posterior(self):
        for spec in self.worlds(90210, 120):
            world = _world(W.spec(spec["prior"], spec["T"], spec["O"]))
            b = prior(world)
            for name, act in world.O.items():
                parts = _split(_measure(b), act.kernel.rows())
                predictive = {o: p for o, p in push(b, act.kernel).items() if p}
                self.assertEqual({o: _mass(part) for o, part in parts.items()}, predictive)
                for o, part in parts.items():
                    mass = _mass(part)
                    self.assertEqual({w: p / mass for w, p in part.items()},
                                     _weights(_update(b, act.kernel, o)))

    def test_a_part_carries_its_own_weight_so_no_value_is_normalised(self):
        """U_n(m) = mass(m) V_n(m/mass(m)). At an ending outcome that is the whole of the branch:
        P_b(o|k) E_{b|k,o}[u] is the dot product of the unnormalised part with u, and nothing is
        divided on the way."""
        world = _world(W.appendix())
        b = prior(world)
        act = world.O["test"]
        for o, part in _split(_measure(b), act.kernel.rows()).items():
            posterior = _update(b, act.kernel, o)
            for u in world.T.values():
                self.assertEqual(_dot(part, u), push(b, act.kernel)[o] * expect(posterior, u))

    def test_a_state_of_mass_zero_is_dropped_and_never_comes_back(self):
        K = {"a": {"o": F(1), "x": F(0)}, "b": {"o": F(0), "x": F(1)}}
        world = _world(W.spec({"a": F(1, 3), "b": F(2, 3)},
                              {"t": {"a": F(1), "b": F(0)}}, {"k": W.act(K, F(0))}))
        posterior = _update(prior(world), world.O["k"].kernel, "o")
        self.assertEqual(_weights(posterior), {"a": F(1)})
        self.assertEqual(expect(posterior, {"a": F(3), "b": F(100)}), F(3))
        self.assertEqual(_measure(posterior), {"a": F(1)})


class ActsTheBeliefCannotTellApart(unittest.TestCase):
    """One act per group, and J3 says which: the first in menu order. The menu still carries the
    others, so a copy is still a second look."""

    def test_a_tie_between_copies_goes_to_the_earlier_one(self):
        T = {"t0": {"w": F(0)}, "t_copy": {"w": F(0)}}
        world = _world(W.spec({"w": F(1)}, T, {}))
        self.assertEqual(decide(prior(world), world, 0), "t0")

    def test_an_act_is_a_copy_only_where_the_belief_still_has_mass(self):
        """k0 and k1 differ only at w2, and w2 is ruled out by the first outcome. After that they
        are one act, and the earlier one is played (J3). Before that they are two."""
        far = {"w0": F(1), "w1": F(-1), "w2": F(0)}
        near = {"w0": F(-1), "w1": F(1), "w2": F(0)}
        rule_out = {"w0": {"o": F(1)}, "w1": {"o": F(1)}, "w2": {"x": F(1)}}
        split = {"w0": {"a": F(1)}, "w1": {"b": F(1)}, "w2": {"a": F(1)}}
        other = {"w0": {"a": F(1)}, "w1": {"b": F(1)}, "w2": {"b": F(1)}}
        spec = W.spec({"w0": F(1, 3), "w1": F(1, 3), "w2": F(1, 3)},
                      {"far": far, "near": near},
                      {"rule_out": W.act(rule_out, F(0)), "k0": W.act(split, F(0)),
                       "k1": W.act(other, F(0))}, N=2, d=2)
        world = _world(spec)
        b = prior(world)
        after = _update(b, world.O["rule_out"].kernel, "o")
        self.assertEqual(sorted(_weights(after)), ["w0", "w1"])
        self.assertEqual(decide(after, world, 1, frozenset({"rule_out"})), "k0")

    @unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
    def test_two_identical_once_acts_are_two_looks_not_one(self):
        """Found by search over three-state worlds: here a second look is worth 1/48, and the only
        way to take it is the copy. Collapsing the copy out of the *menu* -- rather than only out
        of the acts evaluated -- would lose it, and would lose it silently."""
        states = ["w0", "w1", "w2"]
        T = {"t0": {"w0": F(-1), "w1": F(1), "w2": F(-3)},
             "t1": {"w0": F(-1), "w1": F(-3), "w2": F(0)},
             "t2": {"w0": F(-2), "w1": F(-1), "w2": F(3)}}
        K = {"w0": {"o0": F(1, 2), "o1": F(1, 2)},
             "w1": {"o0": F(0), "o1": F(1)},
             "w2": {"o0": F(1, 4), "o1": F(3, 4)}}
        p = {w: F(1, 3) for w in states}
        one = _world(W.spec(p, T, {"k": W.act(K, F(0))}, N=2, d=2))
        two = _world(W.spec(p, T, {"k": W.act(K, F(0)), "k_copy": W.act(dict(K), F(0))}, N=2, d=2))
        self.assertEqual(value(prior(one), one, 2), F(0))
        self.assertEqual(value(prior(two), two, 2), F(1, 48))
        self.assertEqual(decide(prior(two), two, 2), "k")
        after = _update(prior(two), two.O["k"].kernel, "o0")
        self.assertEqual(decide(after, two, 1, frozenset({"k"})), "k_copy")

    def test_a_copy_that_is_fresh_is_not_spent_by_playing_the_first(self):
        """`once` is part of being the same act: a `fresh` twin and a `once` act are two acts."""
        K = {"w0": {"o0": F(1), "o1": F(0)}, "w1": {"o0": F(0), "o1": F(1)}}
        spec = W.spec({"w0": F(1, 2), "w1": F(1, 2)},
                      {"t0": {"w0": F(1), "w1": F(-1)}, "t1": {"w0": F(-1), "w1": F(1)}},
                      {"once_k": W.act(K, F(0), once=True), "fresh_k": W.act(dict(K), F(0), once=False)},
                      N=2, d=2, sources={"once_k": ["e"], "fresh_k": ["e"]}, components=["e"])
        world = _world(spec)
        self.assertEqual(world.menu(frozenset({"once_k"})), ["fresh_k"])
        self.assertEqual(world.menu(frozenset({"fresh_k"})), ["once_k", "fresh_k"])


class ValuesAlreadyFound(unittest.TestCase):
    """A table on the World, which is immutable once declared. It may not change an answer."""

    def setUp(self):
        self.spec = W.appendix(price=F(1, 10), N=3, d=3)

    def test_a_warm_world_answers_as_a_cold_one_does(self):
        cold = [decide(prior(_world(self.spec)), _world(self.spec), n) for n in (0, 1, 2, 3)]
        warm_world = _world(self.spec)
        b = prior(warm_world)
        for _ in range(3):
            warm = [decide(b, warm_world, n) for n in (0, 1, 2, 3)]
            self.assertEqual(warm, cold)

    def test_the_table_answers_for_a_belief_not_for_a_support(self):
        """Two beliefs over the same states are two entries: the measure is the key, not its
        support. A table keyed by the support alone would answer the second with the first."""
        world = _world(self.spec)
        sure = _update(prior(world), world.O["test"].kernel, "+")
        self.assertEqual(sorted(_weights(sure)), ["sick", "well"])
        self.assertNotEqual(_weights(sure), _weights(prior(world)))
        self.assertNotEqual(value(sure, world, 0), value(prior(world), world, 0))

    @unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
    def test_the_menu_is_in_the_key_when_there_is_one_to_read(self):
        """The same belief, the same n, a different menu: a `once` act already spent changes the
        answer, so `used` has to be part of what a value is remembered under."""
        K = {"w0": {"o0": F(3, 4), "o1": F(1, 4)}, "w1": {"o0": F(1, 4), "o1": F(3, 4)}}
        world = _world(W.spec({"w0": F(1, 2), "w1": F(1, 2)},
                              {"t0": {"w0": F(1), "w1": F(-1)}, "t1": {"w0": F(-1), "w1": F(1)}},
                              {"k": W.act(K, F(0))}, N=2, d=2))
        b = prior(world)
        self.assertEqual(decide(b, world, 1), "k")
        self.assertIn(decide(b, world, 1, frozenset({"k"})), world.T)
        self.assertEqual(value(b, world, 1, frozenset({"k"})), value(b, world, 0))


@unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
class TheThreeTogether(unittest.TestCase):
    """The fast paths interact: a copy changes the menu, the menu is part of what a value is
    remembered under, and a dropped state is what makes two acts copies. This is the act
    differential against the oracle on worlds built to make all three bite at once -- copies of
    every kind, rows of mass zero, and three looks, which is deeper than the kit goes."""

    def worlds(self, seed, count):
        import test_differential as D
        rng = random.Random(seed)
        out = []
        for world in (D.rand_world(rng) for _ in range(count)):
            out.append(world)
            out.extend(D.forced_ties(world, rng))
        return out

    def test_the_act_at_every_reachable_node_of_worlds_full_of_copies(self):
        from wald.kit_adapter import make_agent
        import test_differential as D
        agent = D.Wrapped(make_agent())
        for n in (2, 3):
            for world in self.worlds(1904 + n, 12):
                self.assertTrue(S.same_acts(agent, world, n), (n, D.show(world)))


class TheTwoHundredWordPacks(unittest.TestCase):
    """Brief 004's packs: the same World twice, differing in one line."""

    def setUp(self):
        self.dir = pathlib.Path(_path.ROOT) / "packs" / "wordle200"
        if not self.dir.is_dir():
            self.skipTest("packs/wordle200 not generated")

    def _read(self, *parts):
        return pathlib.Path(*parts).read_text(encoding="utf-8")

    def test_they_differ_in_their_depth_and_in_nothing_else(self):
        one = self._read(self.dir, "d1.py").splitlines()
        two = self._read(self.dir, "d2.py").splitlines()
        self.assertEqual(len(one), len(two))
        differ = [(a, b) for a, b in zip(one, two) if a != b]
        self.assertEqual(differ, [('depth(1, source="elicited")', 'depth(2, source="elicited")')])

    def test_the_words_are_the_charters_list_in_its_order(self):
        from wald.surface import check
        words = self._read(_path.CHARTER, "wordle", "words200.txt").split()
        spec = check(self._read(self.dir, "d1.py"), data_dir=self.dir)
        self.assertEqual(list(spec["prior"]), words)
        self.assertEqual(list(spec["O"]), words)
        self.assertEqual(list(spec["T"]), ["claim " + w for w in words])
        self.assertEqual(words[:40], self._read(_path.CHARTER, "wordle", "words.txt").split())


if __name__ == "__main__":
    unittest.main()
