"""Brief 007: CHARTER v0.2 through `wald.plate` and the kernel's own modules. Appendix A end to end
-- (3/5, 2/5) after one right grade, 39/50 and 17/50 on the second episode, (3/11, 8/11) in either
order -- appendix K's falsified plate, and the kit's disclosure, E7 and Score Worlds against
`counts_check`. The kit judges; these are how I know before it does."""
import sys
import unittest
from collections import Counter
from fractions import Fraction as F

import _path
import wald
from wald import counts as C
from wald import disclose as D
from wald import plated as P
from wald.belief import _weights
from wald.decide import value
from wald.refusals import AFTER, GLOBAL, PLATE, UNSCORED, Refused, WorldFalsified

R = _path.oracle() and __import__("counts_check")
GOOD, POOR = ("9/10",), ("3/5",)


def pack(W):
    """A v0.2 dict as a host would declare it: closed, and every table sourced."""
    sources = {"prior": "elicited", "utility": "elicited", "price": "elicited", "horizon": "elicited",
               "depth": "elicited", "kernels": {k: ["elicited"] for k in W["O"]}}
    return dict(W, closed=True, table_sources=sources)


class Script(wald.Door):
    """Answers every observational act and the After-act from a list, in order; records the fires."""

    def __init__(self, *outs):
        self.outs, self.fired, self.asked = list(outs), [], []

    def outcome(self, act):
        self.asked.append(act)
        return self.outs.pop(0)

    def fire(self, act):
        self.fired.append(act)


def reliability(grid=(F(9, 10), F(3, 5)), prior=(F(1, 2), F(1, 2)), wrong=F(-2), verdict=True):
    """Appendix A's World, written here so the tests do not need the charter."""
    L = [("answer", ["a1", "a2"])]
    G = [("rel", [str(r) for r in grid])]
    ls, gs = [("a1",), ("a2",)], [(str(r),) for r in grid]
    other = {"a1": "a2", "a2": "a1"}
    K = {(l, g): {l[0]: F(g[0]), other[l[0]]: 1 - F(g[0])} for l in ls for g in gs}
    T = {"say a1": {(l, g): (F(1) if l == ("a1",) else wrong) for l in ls for g in gs},
         "say a2": {(l, g): (F(1) if l == ("a2",) else wrong) for l in ls for g in gs},
         "abstain": {(l, g): F(0) for l in ls for g in gs}}
    W = {"locals": L, "globals": G, "prior_global": dict(zip(gs, prior)),
         "prior_local": {g: {l: F(1, 2) for l in ls} for g in gs}, "T": T,
         "O": {"ask": {"K": K, "price": F(0), "once": True}}, "N": 1, "d": 1}
    if verdict:
        W["after"] = {"K": {t: {(l, g): {l[0]: F(1)} for l in ls for g in gs} for t in T}, "price": F(0)}
    return W


def global_marginal(plated, counts):
    return _weights(C.posterior_global(plated, counts))


class AppendixA(unittest.TestCase):
    """What one graded episode is worth, played through the public plate."""

    def setUp(self):
        self.world = wald.declare(pack(reliability()))
        self.plate = wald.plate(self.world)

    def test_episode_one_and_the_grade(self):
        door = Script("a1", "a1")
        r = self.plate.run(door)
        self.assertEqual(r.acts, ("ask", "say a1"))
        self.assertEqual(door.fired, ["say a1"])
        self.assertEqual(door.asked, ["ask", "after"])      # the After-act asked by name, after the fire
        self.assertEqual(r.record, ((("ask", "a1"),), "say a1", "a1"))
        self.assertEqual(dict(self.plate.counts()), {r.record: 1})
        self.assertEqual(global_marginal(self.world, self.plate.counts()), {GOOD: F(3, 5), POOR: F(2, 5)})
        wrong = Counter([((("ask", "a1"),), "say a1", "a2")])
        self.assertEqual(global_marginal(self.world, wrong), {GOOD: F(1, 5), POOR: F(4, 5)})

    def test_episode_two(self):
        self.plate.run(Script("a1", "a1"))
        r = self.plate.run(Script("a1", "a1"))
        self.assertEqual(r.acts, ("ask", "say a1"))
        # the belief after the report, before the grade: P(a1) = 39/50, and `say a1` is worth 17/50
        prior = C.episode_prior(self.world, Counter([((("ask", "a1"),), "say a1", "a1")]))
        from wald.belief import _update
        b = _update(prior, self.world.world.O["ask"].kernel, "a1")
        self.assertEqual(sum(p for s, p in _weights(b).items() if s[0] == ("a1",)), F(39, 50))
        self.assertEqual(value(b, self.world.world, 0), F(17, 50))
        # without Counts: 3/4 and 1/4
        b0 = _update(C.episode_prior(self.world, Counter()), self.world.world.O["ask"].kernel, "a1")
        self.assertEqual(value(b0, self.world.world, 0), F(1, 4))

    def test_order_invariance(self):
        right, wrong = ((("ask", "a1"),), "say a1", "a1"), ((("ask", "a1"),), "say a1", "a2")
        want = {GOOD: F(3, 11), POOR: F(8, 11)}
        for order in ([right, wrong], [wrong, right]):
            self.assertEqual(global_marginal(self.world, Counter(order)), want)

    def test_after_a_wrong_grade_it_abstains_without_asking(self):
        self.plate.run(Script("a1", "a2"))
        r = self.plate.run(Script("a1"))
        self.assertEqual(r.acts, ("abstain",))
        self.assertEqual(r.record, ((), "abstain", "a1"))     # graded all the same (J27)

    def test_A_prime_learns_nothing_and_says_so(self):
        w = wald.declare(pack(reliability(verdict=False)))
        nothing, shown = D.shown(w)
        self.assertTrue(nothing)
        self.assertEqual(len(shown), 1)
        self.assertIn("nothing this World declares as a Global can be learned", str(wald.plate(w).disclosure()))


class AppendixK(unittest.TestCase):
    """The falsified plate (J26), and the refit that ships its falsifier."""

    def test_after_report_of_probability_zero(self):
        W = railed()
        plate = wald.plate(wald.declare(pack(W)))
        r = plate.run(Script("0"))
        self.assertEqual(r.status, "WORLD_FALSIFIED")
        self.assertEqual(dict(plate.counts()), {})
        self.assertEqual(plate.falsifier(), ((), "useB", "0"))
        with self.assertRaises(WorldFalsified):
            plate.run(Script("1"))

    def test_report_of_probability_zero_in_the_episode(self):
        plate = wald.plate(wald.declare(pack(reliability())))
        plate.run(Script("a1", "a1"))
        r = plate.run(Script("a3"))                      # a report `ask` cannot emit
        self.assertEqual(r.status, "WORLD_FALSIFIED")
        self.assertEqual(plate.falsifier(), ((("ask", "a3"),), None, None))
        self.assertEqual(dict(plate.counts()), {((("ask", "a1"),), "say a1", "a1"): 1})

    def test_the_refit_learns_from_its_falsifier(self):
        if R is None:
            self.skipTest("the charter is not fetched")
        good = Counter({R.rec("a1", "a1", "say a1"): 16, R.rec("a2", "a2", "say a2"): 4})
        fals = R.rec("a2", "a1", "say a2")
        for falsifier, want in ((None, "say a2"), (fals, "abstain")):
            W = R.falsified_refit_world()
            W.update(counts=good, counts_sha=C.counts_sha(good), score=R.loo_score(W, good))
            if falsifier:
                W["falsifier"] = falsifier
            r = wald.plate(wald.declare(pack(W))).run(Script("a2", "a2"))
            self.assertEqual(r.acts, ("ask", want))


def railed():
    """Appendix G's World with s_B declared 1 everywhere (the kit's K6 World)."""
    gs = [("x",), ("y",)]
    ls = [(a, b) for a in ("1", "0") for b in ("1", "0")]
    pA = {("x",): F(7, 10), ("y",): F(3, 10)}
    pl = {g: {l: (pA[g] if l[0] == "1" else 1 - pA[g]) * (F(1) if l[1] == "1" else F(0)) for l in ls} for g in gs}
    return {"locals": [("sA", ["1", "0"]), ("sB", ["1", "0"])], "globals": [("g", ["x", "y"])],
            "prior_global": {g: F(1, 2) for g in gs}, "prior_local": pl,
            "T": {"useA": {(l, g): (F(1) if l[0] == "1" else F(-1)) for l in ls for g in gs},
                  "useB": {(l, g): (F(1) if l[1] == "1" else F(-1)) for l in ls for g in gs}},
            "O": {}, "after": {"K": {"useA": {(l, g): {l[0]: F(1)} for l in ls for g in gs},
                                     "useB": {(l, g): {l[1]: F(1)} for l in ls for g in gs}}, "price": F(0)},
            "N": 1, "d": 1}


class C21(unittest.TestCase):
    """A World with no Global plays as v0.1 on a plate, save that a falsifying report ends it."""

    def test_a_v0_world_on_a_plate(self):
        from world_fixtures import appendix
        world = wald.declare(appendix(once=False, N=2, d=2))
        plate = wald.plate(world)
        for outs in (["+", "+"], ["-", "+"], ["+", "-"]):
            alone, plated = wald.run(world, Script(*outs)), plate.run(Script(*outs))
            self.assertEqual((alone.acts, alone.outcomes, alone.status, alone.paid),
                             (plated.acts, plated.outcomes, plated.status, plated.paid))
        self.assertEqual(sum(plate.counts().values()), 3)
        self.assertIn("no Global is declared", str(plate.disclosure()))


class Refusals(unittest.TestCase):

    def refused(self, W, name):
        with self.assertRaises(Refused) as got:
            wald.declare(pack(W))
        self.assertEqual(got.exception.name, name)

    def test_global(self):
        W = reliability()
        W["T"]["say a1"][(("a1",), GOOD)] = F(2)
        self.refused(W, GLOBAL)

    def test_after_omits_an_end(self):
        W = reliability()
        del W["after"]["K"]["abstain"]
        self.refused(W, AFTER)

    def test_plate_and_unscored(self):
        one = Counter([((("ask", "a1"),), "abstain", "a1")])
        W = reliability()
        W.update(counts=one, counts_sha="0" * 64, score=F(1))
        self.refused(W, PLATE)
        W.update(counts_sha=C.counts_sha(one))
        self.refused(W, UNSCORED)
        W["score"] = C.score(P.build(pack(W)), one)
        wald.declare(pack(W))
        two = Counter([((("ask", "a1"), ("ask", "a1")), "say a1", "a1")])      # N = 1
        W.update(counts=two, counts_sha=C.counts_sha(two))
        self.refused(W, PLATE)

    def test_the_score_of_appendix_I(self):
        c3 = Counter({((("ask", "a1"),), "say a1", "a1"): 2, ((("ask", "a1"),), "say a1", "a2"): 1})
        self.assertEqual(C.score(P.build(pack(reliability())), c3), F(1125, 100672))

    def test_an_ending_outcome_needs_its_after_kernel(self):
        """The page asks a kernel for every end, an ending outcome's included (QUESTIONS.md Q8)."""
        W = reliability()
        ls, gs = [("a1",), ("a2",)], [GOOD, POOR]
        W["O"]["peek"] = {"K": {(l, g): {"drop": F(1, 2), "go": F(1, 2)} for l in ls for g in gs},
                          "price": F(0), "once": True, "u_end": {"drop": F(0)}}
        W["N"] = 2
        self.refused(W, AFTER)
        W["after"]["K"]["end:peek=drop"] = {(l, g): {l[0]: F(1)} for l in ls for g in gs}
        wald.declare(pack(W))


@unittest.skipIf(R is None, "the charter is not fetched")
class AgainstTheReference(unittest.TestCase):
    """S15 and E7 on the Worlds the kit names, class for class and line for line."""

    def test_disclosure(self):
        worlds = [R.router_world(False, credence_prior=True), R.router_world(True, credence_prior=True),
                  R.two_world(), R.stakes_world(), R.stakes_world(rel_fixed=True), R.cap_world(F(9, 10)),
                  R.echo_world(), R.bonus_world(), R.twin_world(F(1, 3), F(1, 6)), R.colour_world(),
                  R.grader_global_world(), R.confounded_world()]
        canon = lambda cs: sorted(sorted(c.items()) for c in cs)
        for W in worlds:
            plated = P.build(pack_any(W))
            nothing, shown = D.shown(plated)
            self.assertEqual(canon(shown), canon(R.unwashable(W)))
            self.assertEqual(nothing, R.learns_nothing(W))

    def test_e7(self):
        Wg = R.reliability_world([F(1, 2), F(9, 10)], [F(1, 2), F(1, 2)], F(-2))
        g1 = Counter({R.rec("a1", "a1", "say a1"): 99, R.rec("a2", "a2", "say a2"): 99,
                      R.rec("a1", "a2", "say a1"): 1, R.rec("a2", "a1", "say a2"): 1})
        from wald.kit_adapter import make_agent
        self.assertEqual(make_agent().e7(Wg, g1), R.diagnostic(Wg, g1))
        osc = Counter({((), "useA", "A1"): 16, ((), "useA", "A0"): 24, ((), "useB", "B1"): 16, ((), "useB", "B0"): 24})
        self.assertEqual(make_agent().e7(R.oscillating_world(), osc), R.diagnostic(R.oscillating_world(), osc))


def pack_any(W):
    out = pack(W)
    if "dplus" in W:
        out["table_sources"].update(dplus="elicited", fraction="elicited", cost="elicited", rate="elicited")
    return out


if __name__ == "__main__":
    unittest.main()
