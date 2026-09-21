"""The two adaptive packs, and the curves I compute against the ones the author's oracle does.

`laws/kit_wordle_think.py` is the judge. These are how I know before it runs: that the packs say
what the brief told the generator to say, that an episode's own record of its steps survives being
told twice, and that `tools/curves.py` -- my kernel's acts, my arithmetic -- lands on the same five
numbers as `laws/wordle_meta_oracle.py` at every rate on the grid.

The heavy ones are skipped unless WALD_SLOW is set: a cold depth-2 evaluation of 200 words is
forty seconds, and the kit pays that already. Skipped altogether when the charter is not fetched.
"""
import os
import pathlib
import unittest
from fractions import Fraction as F

import _path
from wald.surface import census, check
from wald.world import declare

ROOT = pathlib.Path(_path.ROOT)
SLOW = os.environ.get("WALD_SLOW")
PACKS = {"words200": ROOT / "packs" / "wordle200" / "adaptive.py",
         "twins124": ROOT / "packs" / "twins" / "adaptive.py"}
# briefs/005c-packs.md: the owner's f, the author's r, and the author's fit, one per lexicon.
FRACTION = F(1, 2)
RATE = F(1, 10 ** 7)
FIT = {"words200": (F("11930007676619916058/36661206089336597"),
                    F("-43860132154564000/1929537162596663"), F(41, 200)),
       "twins124": (F("99613375741023143/629231233233738"),
                    F("22716401291570095/314615616616869"), F(149, 500))}


def spec_of(name):
    path = PACKS[name]
    return check(path.read_text(encoding="utf-8"), data_dir=str(path.parent))


class ThePacksSayWhatTheyWereTold(unittest.TestCase):
    """T1 of the kit, in my own words: the five declarations, and the cost table cell by cell."""

    def test_the_think_act_is_the_briefs_numbers(self):
        for name, (a, b, score) in FIT.items():
            spec = spec_of(name)
            n = len(spec["prior"])
            self.assertEqual(spec["dplus"], 2, name)
            self.assertEqual(spec["d"], 1, name)
            self.assertEqual(spec["N"], 5, name)
            self.assertEqual(spec["fraction"], FRACTION, name)
            self.assertEqual(spec["rate"], RATE, name)
            self.assertEqual(spec["score"], {"cost": score}, name)
            self.assertEqual(spec["table_sources"]["cost"], "fitted", name)
            self.assertEqual(spec["table_sources"]["fraction"], "elicited", name)
            self.assertEqual(spec["table_sources"]["dplus"], "elicited", name)
            self.assertEqual(spec["table_sources"]["rate"], "elicited", name)
            want = {s: a * s * s + b * s ** 3 / n for s in range(1, n + 1)}
            self.assertEqual(spec["ops"], want, name + ": ops(s) = a*s^2 + b*s^3/n, every cell")
            declare(spec)

    def test_the_cost_is_fitted_and_carries_its_score(self):
        "K14 and K16: two fitted params, |Omega| fitted cells, and a data Score for the table."
        for name in PACKS:
            spec, count = spec_of(name), census(PACKS[name].read_text(encoding="utf-8"),
                                                data_dir=str(PACKS[name].parent))
            n = len(spec["prior"])
            self.assertEqual(count["fitted"], n + 2, name + ": the cells and the two params")
            self.assertEqual(spec["score"]["cost"], FIT[name][2], name)

    def test_the_adaptive_pack_is_d1_plus_five_lines(self):
        "The only pack it may differ from d1.py in is those five declarations."
        mine = PACKS["words200"].read_text(encoding="utf-8").splitlines()
        plain = (ROOT / "packs" / "wordle200" / "d1.py").read_text(encoding="utf-8").splitlines()
        self.assertEqual(mine[:len(plain)], plain, "the v0 half of the pack is d1.py, line for line")
        added = [ln for ln in mine[len(plain):] if ln and not ln.startswith(("#", " "))]
        self.assertEqual([ln.split("(")[0] for ln in added],
                         ["depth_plus", "think", "param", "param", "cost", "rate", "score"])


@unittest.skipIf(_path.oracle() is None, "charter not fetched: run sh cage/fetch_charter.sh")
class AgainstTheAuthorsOracle(unittest.TestCase):
    """My curves are mine -- my kernel's acts, my expectation, my backward induction. They must
    be the oracle's numbers exactly, at every rate on the kit's grid."""

    def curves(self, name, rates):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from curves import Tree
        tree = Tree(PACKS[name])
        return {r: tree.curves(r) for r in rates}

    def theirs(self, name, rates):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from wordle_meta_oracle import MetaOracle
        words = (ROOT / "charter" / "laws" / "wordle" / (name + ".txt")).read_text().split()
        a, b, _ = FIT[name]
        n = len(words)
        ops = {s: a * s * s + b * s ** 3 / n for s in range(1, n + 1)}
        base, out = None, {}
        for r in rates:
            oracle = MetaOracle(words, -7, FRACTION, ops, r)
            if base is not None:
                oracle.fb, oracle.memo = base.fb, base.memo
            base = oracle
            out[r] = oracle.curves()
        return out

    def compare(self, name, rates):
        mine, theirs = self.curves(name, rates), self.theirs(name, rates)
        for r in rates:
            for curve in ("fixed d=1", "always d=2", "best fixed", "adaptive", "omniscient"):
                self.assertEqual(mine[r][curve], theirs[r][curve],
                                 "%s at r = %s: %s" % (name, r, curve))

    def test_the_twins_curves_are_the_oracles(self):
        self.compare("twins124", [F(0), RATE, F(1, 10 ** 6)])

    @unittest.skipUnless(SLOW, "WALD_SLOW unset: a cold depth-2 look at 200 words is ~40 s")
    def test_the_words200_curves_are_the_oracles(self):
        self.compare("words200", [F(0), RATE, F(1, 10 ** 6)])


if __name__ == "__main__":
    unittest.main()
