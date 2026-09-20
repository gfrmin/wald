"""E2, in my own harness: the kernel must play the oracle's act at every reachable (b, M, n).

The kit draws its own worlds from a seed I never see, so this is not the same test -- it is the
same *method* on shapes the kit does not draw: up to five states, up to four outcomes, ending
outcomes on several acts, three observational acts, and a horizon of three. It proves nothing
(the kit judges); it is how I find a failure before CI does. Skipped when the charter is not
fetched, since the oracle is a definition to read, never a dependency to ship.
"""
import random
import unittest
from fractions import Fraction as F

import _path
from wald.kit_adapter import make_agent

S = _path.oracle()


def rand_world(rng):
    states = ["w%d" % i for i in range(rng.choice([2, 3, 4, 5]))]
    raw = [rng.randint(1, 9) for _ in states]
    total = sum(raw)
    prior = {w: F(r, total) for w, r in zip(states, raw)}
    def utility():
        return {w: F(rng.randint(-9, 9), rng.choice([1, 1, 1, 2])) for w in states}
    T = {"t%d" % i: utility() for i in range(rng.choice([1, 2, 3]))}
    O = {}
    for j in range(rng.choice([1, 2, 3])):
        outs = ["o%d" % i for i in range(rng.choice([2, 2, 3, 4]))]
        K = {}
        for w in states:
            row = [rng.choice([0, 1, 1, 2, 5, 11]) for _ in outs]
            if not sum(row):
                row[rng.randrange(len(outs))] = 1
            z = sum(row)
            K[w] = {o: F(x, z) for o, x in zip(outs, row)}
        ends = {}
        if rng.random() < F(2, 5):
            ends[rng.choice(outs)] = utility()
        O["k%d" % j] = {"K": K, "price": F(rng.randint(0, 6), 4), "once": rng.random() < F(7, 10),
                        "ends": ends}
    return {"prior": prior, "T": T, "O": O}


def forced_ties(world, rng):
    "Random worlds almost never tie; J3 is only visible when they do."
    T = dict(world["T"])
    T["t_copy"] = dict(world["T"]["t0"])
    yield {"prior": world["prior"], "T": T, "O": world["O"]}
    O = dict(world["O"])
    O["k_copy"] = dict(world["O"]["k0"])
    yield {"prior": world["prior"], "T": world["T"], "O": O}
    O = dict(world["O"])
    flat = {w: {"o0": F(1, 2), "o1": F(1, 2)} for w in world["prior"]}
    O["k_flat"] = {"K": flat, "price": F(0), "once": True, "ends": {}}
    yield {"prior": world["prior"], "T": world["T"], "O": O}


class Wrapped:
    "What kit.py does: translate the kernel's WorldFalsified into the oracle's, by class name."

    def __init__(self, agent):
        self.a = agent

    def _call(self, f, *args):
        try:
            return f(*args)
        except Exception as e:
            if type(e).__name__ == "WorldFalsified":
                raise S.WorldFalsified(str(e))
            raise

    def push(self, b, K):
        return self._call(self.a.push, b, K)

    def condition(self, b, K, o):
        return self._call(self.a.condition, b, K, o)

    def expect(self, b, f):
        return self._call(self.a.expect, b, f)

    def decide(self, b, world, n, used=frozenset()):
        return self._call(self.a.decide, b, world, n, used)


def show(world):
    "The failing world, printed the way the kit prints it."
    fr = lambda d: {str(k): (fr(v) if isinstance(v, dict) else str(v)) for k, v in d.items()}
    return str(fr({"prior": world["prior"], "T": world["T"],
                   "O": {k: {"K": s["K"], "price": s["price"], "once": str(s["once"]), "ends": s["ends"]}
                         for k, s in world["O"].items()}}))


def every_outcome_has_mass(world):
    """C1 conditions on every outcome of the predictive, zero-mass ones included, so it is only
    contracted for worlds that have none -- the kit's own generator never draws one (its rows are
    built from 1, 2, 5 and 12). The oracle raises WorldFalsified on such a world exactly as the
    kernel does, so these worlds go to the act differential, where a zero-mass outcome is the
    point ("every sum_o runs over the outcomes with P_b(o|k) > 0"), and not to C1."""
    return all(po > 0 for s in world["O"].values()
               for po in S.REF.push(world["prior"], s["K"]).values())


@unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
class Differential(unittest.TestCase):
    def setUp(self):
        self.agent = Wrapped(make_agent())

    def worlds(self, seed, count):
        rng = random.Random(seed)
        return [rand_world(rng) for _ in range(count)]

    def test_the_three_verbs_agree_with_the_oracle(self):
        for world in self.worlds(7717, 120):
            b = world["prior"]
            for spec in world["O"].values():
                K = spec["K"]
                self.assertEqual(self.agent.push(b, K), S.REF.push(b, K))
                for o, po in S.REF.push(b, K).items():
                    if po == 0:
                        continue
                    self.assertEqual(self.agent.condition(b, K, o), S.REF.condition(b, K, o))
                f = {w: F(1, 3) for w in b}
                self.assertEqual(self.agent.expect(b, f), S.REF.expect(b, f))

    def test_the_act_at_every_reachable_node(self):
        for n in (0, 1, 2):
            for world in self.worlds(31337 + n, 40):
                self.assertTrue(S.same_acts(self.agent, world, n), (n, show(world)))

    def test_the_act_at_every_reachable_node_of_a_deeper_horizon(self):
        for world in self.worlds(4242, 12):
            self.assertTrue(S.same_acts(self.agent, world, 3), show(world))

    def test_ties_go_to_menu_order_terminal_acts_first(self):
        rng = random.Random(555)
        for world in self.worlds(555, 25):
            for variant in forced_ties(world, rng):
                self.assertTrue(S.same_acts(self.agent, variant, 2), show(variant))

    def test_the_policy_earns_what_the_oracle_earns(self):
        for world in self.worlds(90210, 30):
            self.assertEqual(S.policy_value(self.agent, world, 2), S.policy_value(S.REF, world, 2))

    def test_the_consequences_on_my_own_worlds(self):
        for i, world in enumerate(self.worlds(60613, 40)):
            if len(world["O"]) < 2 or len(world["T"]) < 3:
                continue          # C2 and C9a name k0, k1 and t1 by hand
            if not every_outcome_has_mass(world):
                continue          # see every_outcome_has_mass: C1 is not contracted for these
            for name, check in S.CHECKS:
                self.assertTrue(check(self.agent, world, random.Random(i)), (name, show(world)))
