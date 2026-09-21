"""CHARTER v0.1: the two frozen vectors of the appendix, worked from the page's own numbers, and
the Worlds the attack sessions pinned. The kit judges; these are how I know before it does.

The last class is the differential of v0.1's E2 in my own harness: my step must be the reference's
step -- the same act and the same one of S7's buckets -- at every node my own play reaches, on
Worlds drawn here rather than by the kit. Skipped when the charter is not fetched, since the
reference is a definition to read and never a dependency to ship."""
import random
import unittest
from fractions import Fraction as F

import _path
from world_fixtures import APPX_K, APPX_T, act, spec
from wald import belief as B
from wald.decide import (FLOOR, REFUSED, STRUCK_CAP, STRUCK_N, THINK, _cap, decide,
                         step, value)
from wald.episode import Door, run
from wald.refusals import Refused
from wald.world import build, declare

SCAN_K = {"sick": {"y": F(9, 10), "n": F(1, 10)}, "well": {"y": F(2, 5), "n": F(3, 5)}}
META = {"N": 2, "d": 1, "dplus": 2, "fraction": F(1, 2), "rate": F(1, 1000),
        "ops": {1: F(100), 2: F(200)}}
META_SRC = {"fraction": "elicited", "cost": "elicited", "rate": "elicited"}


def thinker(O, **kw):
    """A World that declares a think act: the spec of the fixtures plus CHARTER v0.1's five."""
    s = spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T, O, **dict(META, **kw))
    s["table_sources"].update(META_SRC)
    return s


def vector_A(**kw):
    return thinker({"test": act(APPX_K, F(1, 2), once=False)}, **kw)


def vector_B(**kw):
    return thinker({"test": act(APPX_K, F(1, 2)), "scan": act(SCAN_K, F(1, 5))}, **kw)


def root(world):
    return B.prior(world)


class AppendixA(unittest.TestCase):
    """A. The thought that changes nothing: it is bought, it returns the same act, it costs 1/5."""

    def setUp(self):
        self.w = declare(vector_A())
        self.b = root(self.w)

    def test_the_floor_and_the_depth_it_would_buy(self):
        self.assertEqual((value(self.b, self.w, 1), value(self.b, self.w, 2)), (F(-51, 50), F(-51, 50)))
        self.assertEqual(value(self.b, self.w, 0), F(-8, 5))

    def test_the_cap_and_the_room_it_leaves(self):
        # best(w) = 0 in either state: `treat` in sick, `leave` in well, and no ending outcome.
        measure = B._measure(self.b)
        cap = _cap(measure, B._mass(measure), self.w, self.w.menu(frozenset()), F(-8, 5))
        self.assertEqual(cap, F(-1, 2))                       # max(-8/5, 0 - 1/2)
        self.assertEqual(cap - F(-51, 50), F(13, 25))         # ghat

    def test_theta_is_bought_and_returns_test(self):
        self.assertEqual(step(self.b, self.w, 2), ("test", THINK, F(1, 5)))

    def test_a_dearer_thought_is_struck_by_the_bounds_alone(self):
        w = declare(vector_A(rate=F(1, 100)))                 # c = 2 > 13/25
        self.assertEqual(step(root(w), w, 2), ("test", STRUCK_CAP, F(0)))

    def test_a_worthless_thought_is_refused_with_Q_formed(self):
        w = declare(vector_A(fraction=F(0)))
        self.assertEqual(step(root(w), w, 2), ("test", REFUSED, F(0)))

    def test_a_free_and_certain_thought_is_bought(self):
        w = declare(vector_A(fraction=F(1), rate=F(0)))
        self.assertEqual(step(root(w), w, 2)[1], THINK)

    def test_the_second_step_is_struck_because_n_is_at_the_floor(self):
        plus = B._update(self.b, self.w.O["test"].kernel, "+")
        self.assertEqual(step(plus, self.w, 1), ("treat", STRUCK_N, F(0)))


class AppendixB(unittest.TestCase):
    """B. The thought that changes the act -- and loses 69/500 of policy value doing it (C18)."""

    def setUp(self):
        self.w = declare(vector_B())
        self.b = root(self.w)

    def test_the_two_depths_disagree(self):
        self.assertEqual((value(self.b, self.w, 1), value(self.b, self.w, 2)), (F(-51, 50), F(-479, 500)))

    def test_the_cap_and_the_room_it_leaves(self):
        measure = B._measure(self.b)
        cap = _cap(measure, B._mass(measure), self.w, self.w.menu(frozenset()), F(-8, 5))
        self.assertEqual(cap, F(-1, 5))                       # max(-8/5, 0 - 1/5)
        self.assertEqual(cap - F(-51, 50), F(41, 50))

    def test_theta_is_bought_and_scan_is_played(self):
        self.assertEqual(step(self.b, self.w, 2), ("scan", THINK, F(1, 5)))

    def test_the_two_rates_the_page_names(self):
        w = declare(vector_B(rate=F(1, 400)))                 # c = 1/2 > f*ghat = 41/100
        self.assertEqual(step(root(w), w, 2)[:2], ("test", REFUSED))
        w = declare(vector_B(rate=F(1, 200)))                 # c = 1 > ghat = 41/50
        self.assertEqual(step(root(w), w, 2)[:2], ("test", STRUCK_CAP))

    def test_the_thought_is_worth_less_than_it_costs(self):
        self.assertEqual(F(-479, 500) - F(-51, 50), F(31, 500))
        self.assertLess(F(31, 500), F(1, 5))


class TheCapIsAnUpperBound(unittest.TestCase):
    """FIXED_CAP of `meta_check.py`: the World that decided the shape of the cap. A cap that
    values ending branches at the root posterior gives 10, which is below V_5 = 40951/2000."""

    def setUp(self):
        s = spec({"A": F(1, 2), "B": F(1, 2)}, {"t0": {"A": F(0), "B": F(0)}},
                 {"reveal": act({"A": {"a": F(1)}, "B": {"b": F(1)}}, F(1, 100)),
                  "lottery": act({"A": {"o": F(1, 10), "x": F(9, 10)}, "B": {"o": F(9, 10), "x": F(1, 10)}},
                                 F(0), once=False, ends={"o": {"A": F(100), "B": F(0)}})},
                 N=5, d=1, dplus=2, fraction=F(1, 2), rate=F(0), ops={1: F(1), 2: F(1)})
        s["table_sources"].update(META_SRC)
        self.w = declare(s)

    def test_the_cap_is_above_the_exact_value(self):
        b = root(self.w)
        measure = B._measure(b)
        cap = _cap(measure, B._mass(measure), self.w, self.w.menu(frozenset()), value(b, self.w, 0))
        # best(A) = 100 (the lottery's ending outcome, which A can emit), best(B) = 0.
        self.assertEqual(cap, F(50))
        self.assertGreaterEqual(cap, F(40951, 2000))
        self.assertEqual(value(b, self.w, 5), F(40951, 2000))


class WhatTheStepReads(unittest.TestCase):
    def test_a_v0_world_is_the_floor_and_nothing_else(self):
        w = declare(spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T,
                         {"test": act(APPX_K, F(1, 2), once=False)}, N=3, d=1))
        self.assertIsNone(w.dplus)
        for n in (0, 1, 2, 3):
            act_, how, paid = step(root(w), w, n)
            self.assertEqual((how, paid), (FLOOR, F(0)))
            self.assertEqual(act_, self.floor(w, n))

    def floor(self, w, n):
        return decide(root(w), w, min(w.d, n))

    def test_the_cap_does_not_read_the_depth_it_would_buy(self):
        """C19. A d+ of N is not a lawful pack (J11) -- it is a probe of the function, so it is
        built and not declared, exactly as the kit builds it."""
        hows = set()
        for dplus in (2, 3):
            w = build(dict(vector_A(N=3), dplus=dplus))
            hows.add(step(root(w), w, 3)[1])
        self.assertEqual(len(hows), 1)

    def test_theta_is_struck_where_the_menu_has_no_look_left(self):
        w = declare(dict(vector_A(), O={"test": act(APPX_K, F(1, 2))}))    # `once`
        self.assertEqual(step(root(w), w, 2, frozenset(["test"]))[1], STRUCK_N)


class TheOperationCounter(unittest.TestCase):
    """E6. Counted by the evaluator that runs, printed, and read by no verb."""

    def test_a_thought_is_counted_and_the_count_is_not_the_prediction(self):
        w = declare(vector_B())
        act_, how, paid = step(root(w), w, 2)
        self.assertEqual(how, THINK)
        counted = B._counted()
        self.assertGreater(counted, 0)
        self.assertNotEqual(counted, w.ops[2])        # a prediction is not a measurement

    def test_report_prints_both_beside_each_other(self):
        w = declare(vector_B())
        step(root(w), w, 2)
        text = str(B.report(root(w), w))
        self.assertIn("200 operations predicted", text)
        self.assertIn("2 live", text)

    def test_report_of_a_v0_world_says_nothing_of_thought(self):
        w = declare(spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T,
                         {"test": act(APPX_K, F(1, 2))}, N=2, d=1))
        self.assertNotIn("predicted", str(B.report(root(w), w)))


class Script(Door):
    def __init__(self, outcomes):
        self.left = list(outcomes)
        self.fired = None

    def outcome(self, act):
        return self.left.pop(0)

    def fire(self, act):
        self.fired = act


class TheEpisodeBuysAndRecords(unittest.TestCase):
    def test_appendix_A_plays_test_then_treats_and_the_thought_is_not_a_price(self):
        w = declare(vector_A())
        r = run(w, Script(["+"]))
        self.assertEqual(r.acts, ("test", "treat"))
        self.assertEqual(r.paid, F(1, 2))             # the price of the look, not of the thought
        self.assertEqual(r.thought, F(1, 5))          # one think act, at the root
        # Two steps in this episode: the root buys a thought, and the step after the look is at
        # n = 1 = d, where the deeper evaluation is the same evaluation and theta is struck.
        self.assertEqual(r.steps, {STRUCK_N: 1, STRUCK_CAP: 0, REFUSED: 0, THINK: 1})
        self.assertEqual(len(r.operations), 1)

    def test_a_v0_world_thinks_nothing_and_counts_nothing(self):
        w = declare(spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T,
                         {"test": act(APPX_K, F(1, 2))}, N=2, d=1))
        r = run(w, Script(["+"]))
        self.assertEqual(r.thought, F(0))
        self.assertEqual(r.operations, ())
        self.assertEqual(sum(r.steps.values()), 0)    # every step was "floor"


class TheTablesAreRefusedByName(unittest.TestCase):
    """INTERFACE's thirteen cases, and the reading the page leaves to the reference."""

    def refuse(self, s):
        try:
            declare(s)
        except Refused as e:
            return e.name
        return "ACCEPTED"

    def test_the_fraction(self):
        self.assertEqual(self.refuse(vector_A(fraction=F(3, 2))), "FRACTION")
        self.assertEqual(self.refuse(vector_A(fraction=F(-1, 4))), "FRACTION")
        s = vector_A()
        s["table_sources"]["fraction"] = "data"
        self.assertEqual(self.refuse(s), "FRACTION")

    def test_the_cost(self):
        self.assertEqual(self.refuse(vector_A(ops={2: F(1)})), "COST")
        self.assertEqual(self.refuse(vector_A(ops={1: F(1), 2: F(-1)})), "COST")
        s = vector_A()
        s["table_sources"]["cost"] = "data"
        self.assertEqual(self.refuse(s), "COST")
        # The page forbids r < 0 (section 1) and names no clause; `meta_check.refuse_meta`,
        # which is the definition, refuses it with the Cost table.
        self.assertEqual(self.refuse(vector_A(rate=F(-1, 1000))), "COST")

    def test_the_depth_it_buys(self):
        for bad in (vector_A(dplus=1), vector_A(dplus=3, N=3), vector_A(d=2, N=3, dplus=3),
                    vector_A(N=1, dplus=2)):
            self.assertEqual(self.refuse(bad), "DEPTH_PLUS")

    def test_the_rate(self):
        s = vector_A()
        s["table_sources"]["rate"] = "fitted"
        self.assertEqual(self.refuse(s), "RATE")

    def test_a_fitted_meta_table_carries_its_score(self):
        for table in ("fraction", "cost"):
            s = vector_A()
            s["table_sources"][table] = "fitted"
            self.assertEqual(self.refuse(s), "UNSCORED")
            s["score"] = F(-3, 2)
            self.assertEqual(self.refuse(s), "ACCEPTED")

    def test_a_v0_world_is_refused_by_none_of_them(self):
        s = spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T, {"test": act(APPX_K, F(1, 2))}, N=2, d=2)
        self.assertEqual(self.refuse(s), "ACCEPTED")          # d = 2 is lawful without a think act


def _meta_check():
    "laws/meta_check.py, if the charter is fetched: the reference for the amendment."
    if _path.oracle() is None:
        return None
    import meta_check
    return meta_check


M = _meta_check()


@unittest.skipIf(M is None, "charter not fetched: run sh cage/fetch_charter.sh")
class TheStepIsTheReferences(unittest.TestCase):
    """E2 under theta: the same act and the same bucket at every node the agent reaches, and the
    same value for the policy net of what it paid to think."""

    def worlds(self, seed, count):
        rng = random.Random(seed)
        out = [M.rand_meta_world(rng) for _ in range(count)]
        # Worlds where depth 2 changes an act somewhere the floor reaches: where the buckets bite.
        out += [w for w in (M.rand_meta_world(rng) for _ in range(2000)) if M.forced(w)][:count]
        return out + list(M.fixed_worlds().values())

    def test_every_node_and_every_bucket(self):
        from wald.kit_adapter import make_agent
        agent = make_agent()

        class Wrapped:
            def step(self, b, world, n, used=frozenset()):
                a, how, paid = agent.step(b, world, n, used)
                return a, how, F(paid)

            def decide(self, b, world, n, used=frozenset()):
                return self.step(b, world, n, used)[0]

        mine = Wrapped()
        seen = {}
        for w in self.worlds(20260921, 12):
            for b, used, n, a, how in M.reachable(mine, w):
                seen[how] = seen.get(how, 0) + 1
                self.assertEqual((a, how), M.DPLUS.step(b, w, n, used)[:2])
            self.assertEqual(M.value_net(mine, w), M.value_net(M.DPLUS, w))
        # Every bucket of S7 was actually exercised, or this test proves less than it looks.
        self.assertEqual(sorted(seen), ["refused", "struck_cap", "struck_n", "think"])


if __name__ == "__main__":
    unittest.main()
