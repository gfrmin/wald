"""Brief 010: the plate owns the lookahead's memo. Over a plate whose prior moves every episode, the
values found are dropped before each episode -- and every act and every value is what a memo kept
for the plate's life gives. Where the prior does not move the memo is kept; `run` keeps the World's."""
import os
import sys
import unittest
from fractions import Fraction as F

import _path
import wald
from wald.plate import Plate
from wald.plated import Plated, wrap
from world_fixtures import appendix
from test_counts import Script, pack, reliability

sys.path.insert(0, os.path.join(_path.ROOT, "tools"))
import plate_memory  # noqa: E402  the brief's World: appendix A on 100 Global values

EPISODES = 60


class Kept(Plate):
    """The plate as it was: one memo for its life, whatever the prior."""

    def __init__(self, plated):
        super().__init__(plated)
        self.life = {}

    def _work(self, prior):
        return self.life


def plates(world):
    plated = world if isinstance(world, Plated) else wrap(world)
    return Plate(plated), Kept(plated)


def same(test, r, s):
    test.assertEqual(r.acts, s.acts)
    test.assertEqual(r.outcomes, s.outcomes)
    test.assertEqual(r.status, s.status)
    test.assertEqual(r.paid, s.paid)
    test.assertEqual(str(wald.report(r.final)), str(wald.report(s.final)))
    test.assertEqual(r.thought, s.thought)
    test.assertEqual(r.steps, s.steps)
    test.assertEqual(r.record, s.record)
    # E6's operations measure the work done, which the memo changes by design; how many thoughts
    # there were is a choice, and that is the same.
    test.assertEqual(len(r.operations), len(s.operations))


class LearningPlate(unittest.TestCase):

    def test_kept_and_dropped_give_every_act_and_value(self):
        world = wald.declare(plate_memory.world())
        dropped, kept = plates(world)
        d1, d2 = plate_memory.Coin(7), plate_memory.Coin(7)
        priors, memos = [], []
        for _ in range(EPISODES):
            r, s = dropped.run(d1), kept.run(d2)
            same(self, r, s)
            self.assertEqual(r.acts[0], "ask")          # every record moves P(Global | Counts)
            priors.append(dropped._since)
            memos.append(dropped._memo)
        self.assertEqual(dropped.counts(), kept.counts())
        # The prior moved every episode, so every episode began with nothing found before it.
        self.assertTrue(all(a != b for a, b in zip(priors, priors[1:])))
        self.assertEqual(len(set(map(id, memos))), EPISODES)
        self.assertGreater(len(kept.life), len(dropped._memo))
        # The episode's values are the ones a fresh lookahead finds: the memo holds only the
        # last prior's beliefs, and its root is that prior.
        self.assertTrue(all(len(m) <= len(memos[0]) + 2 for m in memos))

    def test_the_world_memo_is_not_the_plates(self):
        world = wald.declare(plate_memory.world())
        p = wald.plate(world)
        p.run(plate_memory.Coin(1))
        self.assertEqual(world.world.work()[1], {})


class StillPrior(unittest.TestCase):

    def test_no_global_keeps_the_memo(self):
        world = wald.declare(appendix())
        dropped, kept = plates(world)
        door = [Script(*"+-+-+-"), Script(*"+-+-+-")]
        memo = None
        for _ in range(6):
            same(self, dropped.run(door[0]), kept.run(door[1]))
            memo = memo or dropped._memo
            self.assertIs(dropped._memo, memo)
        self.assertTrue(memo)

    def test_a_record_that_moves_nothing_keeps_the_memo(self):
        # Appendix A after one wrong grade: the kernel abstains without asking (appendix J 2.2),
        # and a record with no draw moves no Global value.
        p = wald.plate(wald.declare(pack(reliability())))
        r = p.run(Script("a1", "a2"))
        self.assertEqual(r.acts, ("ask", "say a1"))
        first = p._memo
        r = p.run(Script("a1"))
        self.assertEqual(r.acts, ("abstain",))
        second = p._memo
        self.assertIsNot(first, second)                 # the wrong grade moved the prior
        p.run(Script("a2"))
        self.assertIs(p._memo, second)                  # the abstention did not

    def test_run_keeps_the_worlds_memo(self):
        world = wald.declare(appendix(N=2, d=2))
        wald.run(world, Script("+", "+"))
        memo = world.work()[1]
        size = len(memo)
        self.assertTrue(size)
        wald.run(world, Script("-", "-"))
        self.assertIs(world.work()[1], memo)
        self.assertGreaterEqual(len(memo), size)


if __name__ == "__main__":
    unittest.main()
