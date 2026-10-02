"""Brief 013: the lookahead over integer weights against the lookahead over `Fraction`s it replaced
(`fraction_lookahead.py`, master at bc6fd60). On random Worlds -- ending outcomes, `fresh` and `once`
acts, forced ties, think acts -- and on plates whose Counts move the prior every episode, written
by the plate and shipped: every act, every outcome, S7's buckets, every thought paid, every E6 count,
the counter `report` prints after every episode, every value and `Plate.values()`'s text are the
same. And P(Global | Counts), normalised once, is the per-record posterior it replaced."""
import random
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
import fraction_lookahead as FL
import test_differential as D
import wald
from wald import belief as B
from wald import counts as C
from wald.decide import quantities, value
from wald.episode import ending, run
from wald.refusals import WorldFalsified
from wald.same import Sameness
from wald.world import declare
from world_fixtures import spec
from test_counts import pack, reliability

META = {"fraction": "elicited", "cost": "elicited", "rate": "elicited", "dplus": "elicited"}


class Truth(wald.Door):
    """A door over a hidden state, one per episode: every report is drawn from the kernel's row
    there, from a seed that names the episode, the act and the draw, so two doors given the same
    seed answer alike however many reports each is asked."""

    def __init__(self, world, seed, after=None):
        self.world, self.seed, self.after = world, seed, after
        self.episode, self.state, self.draws, self.end = 0, None, 0, None

    def begin(self, episode, state):
        self.episode, self.state, self.draws, self.end = episode, state, 0, None

    def _draw(self, row, act):
        self.draws += 1
        rng = random.Random("%s/%d/%s/%d" % (self.seed, self.episode, act, self.draws))
        outs = [o for o, q in sorted(row.items(), key=lambda x: repr(x[0])) if q]
        return rng.choices(outs, weights=[row[o] for o in outs])[0]

    def outcome(self, act):
        if act in self.world.O:
            o = self._draw(dict(self.world.O[act].kernel.row(self.state).items()), act)
            if o in self.world.O[act].ends:
                self.end = ending(act, o)
            return o
        return self._draw(dict(self.after.kernels[self.end].row(self.state).items()), act)

    def fire(self, act):
        self.end = act


def thinker(s, rng):
    """CHARTER v0.1's tables on a spec: d = 1, d+ = 2 (J11), a Rate that sometimes buys."""
    states = len(s["prior"])
    s = dict(s, d=1, N=max(2, s["N"]), dplus=2, fraction=rng.choice([F(0), F(1, 2), F(1)]),
             rate=rng.choice([F(0), F(1, 1000), F(1, 100), F(1, 10)]),
             ops={i: F(rng.randint(1, 30) * i) for i in range(1, states + 1)})
    s["table_sources"] = dict(s["table_sources"], **META)
    return s


def v0_worlds(seed, count):
    rng = random.Random(seed)
    for _ in range(count):
        raw = D.rand_world(rng)
        shapes = [raw] + list(D.forced_ties(raw, rng))
        for w in shapes:
            N = rng.choice([1, 2, 3])
            s = spec(w["prior"], w["T"], w["O"], N=N, d=rng.randint(1, N))
            yield s
            yield thinker(s, rng)


def rand_plated(rng):
    """A random CHARTER v0.2 dict: a local and a Global, kernels reading both, utilities and ending
    utilities reading the local only (S11), sometimes an After-act, sometimes a think act."""
    ls = [(x,) for x in ["x0", "x1", "x2"][:rng.choice([2, 3])]]
    gs = [(g,) for g in ["g%d" % i for i in range(rng.choice([2, 3, 4]))]]
    states = [(l, g) for l in ls for g in gs]

    def dist(keys):
        raw = [rng.randint(1, 9) for _ in keys]
        return {k: F(r, sum(raw)) for k, r in zip(keys, raw)}

    def local():
        u = {l: F(rng.randint(-9, 9), rng.choice([1, 1, 2, 3])) for l in ls}
        return {(l, g): u[l] for l in ls for g in gs}

    T = {"t%d" % i: local() for i in range(rng.choice([1, 2, 3]))}
    O = {}
    for j in range(rng.choice([1, 2, 3])):
        outs = ["o%d" % i for i in range(rng.choice([2, 3]))]
        K = {}
        for w in states:
            row = [rng.choice([0, 1, 1, 2, 5, 11]) for _ in outs]
            if not sum(row):
                row[rng.randrange(len(outs))] = 1
            K[w] = {o: F(x, sum(row)) for o, x in zip(outs, row)}
        act = {"K": K, "price": F(rng.randint(0, 6), 4), "once": rng.random() < 0.7}
        if rng.random() < 0.3:
            o = rng.choice(outs)
            act["ends"], act["u_end"] = {o}, {o: local()}
        O["k%d" % j] = act
    N = rng.choice([1, 2, 3])
    W = {"locals": [("x", [l[0] for l in ls])], "globals": [("g", [g[0] for g in gs])],
         "prior_global": dist(gs), "prior_local": {g: dist(ls) for g in gs}, "T": T, "O": O,
         "N": N, "d": rng.randint(1, N)}
    if rng.random() < 0.5:
        ends = list(T) + [ending(k, o) for k, a in O.items() for o in a.get("ends", ())]
        W["after"] = {"K": {e: {w: dist(["r0", "r1"]) for w in states} for e in ends},
                      "price": F(rng.randint(0, 2), 4)}
    W = pack(W)
    if rng.random() < 0.4:
        W.update(d=1, N=max(2, N), dplus=2, fraction=rng.choice([F(1, 2), F(1)]),
                 rate=rng.choice([F(0), F(1, 1000), F(1, 100)]),
                 ops={i: F(rng.randint(1, 30) * i) for i in range(1, len(states) + 1)})
        W["table_sources"] = dict(W["table_sources"], **META)
    return W


def text(q):
    """`Plate.values()`'s lines from quantities' six numbers."""
    n, v0, T, O, vn, act = q
    lines = ["n " + str(n), "V_0 " + str(v0)] + ["T %s %s" % (t, v) for t, v in T]
    lines += ["O %s %s %s" % (k, v, v - v0) for k, v in O] + ["V_n %s %s" % (vn, act)]
    return "\n".join(lines)


class Twins:
    """Asserts for one episode played twice, once by each lookahead."""

    def same_episode(self, r, old):
        acts, outcomes, status, paid, thought, steps, operations, final, _ = old
        self.assertEqual(r.acts, tuple(acts))
        self.assertEqual(r.outcomes, tuple(outcomes))
        self.assertEqual(r.status, status)
        self.assertEqual(r.thought, thought)
        self.assertEqual(r.steps, steps)
        self.assertEqual(r.operations, tuple(operations))     # E6, thought by thought
        self.assertEqual(B._counted(), FL.OPS[0])             # every tally since the last thought
        return paid, final


class RandomWorlds(Twins, unittest.TestCase):

    def test_every_act_value_and_count(self):
        checked = thoughts = 0
        for s in v0_worlds(1013, 70):
            world = declare(s)
            B._count_reset()
            FL.OPS[0] = 0
            same, memo = Sameness(world), {}
            self.assertEqual(quantities(B.prior(world), world), FL.quantities(B.prior(world), world))
            omega = list(world.prior.carrier())
            for episode in range(4):
                truth = omega[episode % len(omega)]
                d1, d2 = Truth(world, 7), Truth(world, 7)
                d1.begin(episode, truth)
                d2.begin(episode, truth)
                old = FL.play(world, B.prior(world), d1, same, memo)
                r = run(world, d2)
                paid, final = self.same_episode(r, old)
                self.assertEqual(r.paid, paid)
                self.assertEqual(B._weights(r.final), B._weights(final))
                self.assertEqual(str(B.report(r.final, world)).split(" | ")[0],
                                 str(B.report(final, world)).split(" | ")[0])
                checked += 1
                thoughts += len(r.operations)
            for n in range(world.N + 1):
                self.assertEqual(value(B.prior(world), world, n), FL.value(B.prior(world), world, n))
        self.assertGreater(thoughts, 20)       # the Worlds think, so E6 is exercised
        self.assertGreater(checked, 1000)


class Plates(Twins, unittest.TestCase):

    def plate_twice(self, W, seed, episodes):
        """A plate played by the kernel, and the same episodes by the old lookahead from the same
        priors, with the memo the plate keeps: dropped whenever the prior moves (brief 010)."""
        world = wald.declare(W)
        plate = wald.plate(world)
        plated = plate._plated
        rng = random.Random(seed)
        B._count_reset()
        FL.OPS[0] = 0
        same, memo, since = Sameness(plated.world), {}, None
        d1 = Truth(plated.world, seed, plated.after)
        d2 = Truth(plated.world, seed, plated.after)
        thoughts = 0
        for episode in range(episodes):
            prior = plate.prior()
            self.assertEqual(str(plate.values()).replace('"', ""),
                             text(FL.quantities(prior, plated.world)))
            if B._measure(prior) != since:
                since, memo = B._measure(prior), {}
            omega = list(B._weights(prior))
            truth = rng.choices(omega, weights=list(B._weights(prior).values()))[0]
            d1.begin(episode, truth)
            d2.begin(episode, truth)
            old = FL.play(plated.world, prior, d1, same, memo)
            r = plate.run(d2)
            self.same_episode(r, old)
            thoughts += len(r.operations)
        return world, plate, thoughts

    def test_plates_that_learn_and_ship(self):
        rng = random.Random(2013)
        learned = shipped = thoughts = 0
        for i in range(40):
            W = rand_plated(rng)
            try:
                world, plate, t = self.plate_twice(W, i, 12)
            except WorldFalsified:
                continue
            thoughts += t
            counts = plate.counts()
            learned += sum(counts.values())
            # The same declaration shipping the Counts it wrote: a plate that starts from them.
            S = dict(W, counts=counts, counts_sha=wald.digest(counts), score=F(wald.score(world, counts)))
            _, _, t = self.plate_twice(S, 100 + i, 6)
            thoughts += t
            shipped += 1
        self.assertGreater(shipped, 30)
        self.assertGreater(learned, 300)
        self.assertGreater(thoughts, 0)

    def test_appendix_A_on_a_plate(self):
        self.plate_twice(pack(reliability()), 5, 30)


class OneNormalisation(unittest.TestCase):
    """P(Global | Counts) normalised once is the per-record posterior, and a multiset no Global
    value can have written names the record the per-record form named."""

    class _Record:
        """The likelihood as master read it: one token (record, count) at a time."""

        def __init__(self, plated):
            self.plated = plated

        def at(self, g, token):
            record, n = token
            return C.likelihood(self.plated, record, g) ** n

    def per_record(self, plated, counts):
        """P(Global | Counts) as master formed it: normalised after every record."""
        b = B._sealed(dict(plated.pg))
        for token in counts.items():
            b = B._update(b, self._Record(plated), token)
        return b

    def test_the_same_rationals(self):
        rng = random.Random(14)
        for i in range(30):
            W = rand_plated(rng)
            world = wald.declare(W)
            plate = wald.plate(world)
            door = Truth(plate._plated.world, i, plate._plated.after)
            for episode in range(8):
                prior = plate.prior()
                door.begin(episode, rng.choices(list(B._weights(prior)), list(B._weights(prior).values()))[0])
                plate.run(door)
            plated, counts = plate._plated, plate.counts()
            self.assertEqual(B._weights(C.posterior_global(plated, counts)),
                             B._weights(self.per_record(plated, counts)))

    def test_the_same_refusal(self):
        # `ask` always right, or always wrong: a right grade and a wrong one, together, no Global
        # value can have written, and which record is named depends on which came first.
        plated = wald.plate(wald.declare(pack(reliability(grid=(F(1), F(0))))))._plated
        right = ((("ask", "a1"),), "say a1", "a1")
        wrong = ((("ask", "a2"),), "say a2", "a1")
        for records in ([right, right, wrong, right], [wrong, right, right], [right, wrong, wrong]):
            counts = C.tally(records)
            with self.assertRaises(WorldFalsified) as new:
                C.posterior_global(plated, counts)
            with self.assertRaises(WorldFalsified) as old:
                self.per_record(plated, counts)
            self.assertEqual(str(new.exception), str(old.exception))


if __name__ == "__main__":
    unittest.main()
