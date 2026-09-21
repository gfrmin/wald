"""The surface against the reference checker, on mutations of the whole corpus.

The kit runs the corpus as written. This runs it mutated: every pack with each line deleted, each
line doubled, and a list of substitutions that break one rule apiece. My checker and the reference
must reach the same verdict -- the same refusal name, or the same World and the same census -- and
where they do not, the difference must be one the page settles and `QUESTIONS.md` records.

Skipped when the charter is not fetched: the reference is a definition to read, never a dependency.
"""
import os
import pathlib
import unittest

import _path
from wald.refusals import Refused
from wald.surface import census, check

S = _path.oracle()
LAWS = pathlib.Path(_path.CHARTER)
OK = str(LAWS / "packs" / "ok")

SUBSTITUTIONS = [('source="data"', 'source="guessed"'), ('source="elicited"', ''), ('1/5', '0.2'),
                 ('1/2', '1/0'), ('once=True', 'once=False'), ('once=True', 'once=1'),
                 ('reads=["health"]', 'reads=[]'), ('reads=["health"]', 'reads=["nope"]'),
                 ('closed=True', 'bottom="sick"'), ('closed=True', ''), ('9/10', '-9/10'),
                 ('"sick"', '"SICK"'), ('horizon(1', 'horizon(3/2'), ('depth(1', 'depth(0'),
                 ('table(', 'host('), ('point(', 'pointer('), ('{"sick"', '{"sick": 1/5, "sick"'),
                 ('prior(', 'prior(by('), ('act(', 'x = act('), ('9/10', 'max(9,10)'),
                 ('4/5', '4/5 if True else 1/5'), ('space(', 'space2('), ('utility(', 'utility(**'),
                 ('sha256=', 'sha='), ('think(fraction=1/2', 'think(fraction=3/2'),
                 ('rate(1/1000', 'rate(-1/1000'), ('depth_plus(2', 'depth_plus(2/3'),
                 ('cost([100, 200]', 'cost([100])'), ('source="elicited")\nthink', 'source="data")\nthink')]

# SURFACE K7: a pack that breaks several rules may be refused by any one of their names, so two
# checkers are allowed to differ here -- and one place they do. `build` reaches the World's own
# v0 rules before `_rulings` reaches CHARTER v0.1's, and `laws/surface_check.validate` is the
# other way round. Both names are of a rule the variant really breaks.
WORLD_FIRST = {"ZERO_EVIDENCE", "SHARED_SOURCE"}
THINK_ACT = {"FRACTION", "COST", "RATE", "DEPTH_PLUS", "UNSCORED", "TABLE_SOURCE"}


def variants(text):
    yield "as written", text
    lines = text.splitlines()
    for i in range(len(lines)):
        yield "minus line %d" % i, "\n".join(lines[:i] + lines[i + 1:]) + "\n"
        yield "line %d twice" % i, "\n".join(lines[:i + 1] + [lines[i]] + lines[i + 1:]) + "\n"
    for old, new in SUBSTITUTIONS:
        if old in text:
            yield "%r -> %r" % (old, new), text.replace(old, new, 1)


def corpus():
    for folder in ("ok", "poison"):
        directory = LAWS / "packs" / folder
        for name in sorted(os.listdir(directory)):
            if name.endswith(".py"):
                yield name, (directory / name).read_text(encoding="utf-8")


@unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
class AgainstTheReference(unittest.TestCase):
    def setUp(self):
        import surface_check
        self.reference = surface_check

    def their_verdict(self, text):
        try:
            return self.reference.check(text, {}, OK), self.reference.census(text, {}, OK)
        except self.reference.Refused as e:
            return e.name, None
        except Exception as e:                      # a crash is not a refusal: see QUESTIONS.md Q3
            return "raised " + type(e).__name__, None

    def my_verdict(self, text):
        try:
            return check(text, data_dir=OK), census(text, data_dir=OK)
        except Refused as e:
            return e.name, None

    def test_every_mutation_of_every_pack(self):
        checked, allowed = 0, 0
        for name, text in corpus():
            for label, variant in variants(text):
                checked += 1
                theirs, their_census = self.their_verdict(variant)
                mine, my_census = self.my_verdict(variant)
                if theirs == mine and their_census == my_census:
                    continue
                where = name + " :: " + label
                if theirs == "raised AttributeError" and mine == "MISSING":
                    allowed += 1                    # QUESTIONS.md Q3, closed at kit v0.8
                elif theirs != mine and not isinstance(theirs, str) and mine == "DUPLICATE":
                    allowed += 1                    # QUESTIONS.md Q1, closed at kit v0.8
                elif mine in WORLD_FIRST and theirs in THINK_ACT:
                    allowed += 1                    # SURFACE K7, above: two rules, two names
                else:
                    self.fail("%s: reference %r, mine %r" % (where, theirs, mine))
        self.assertGreater(checked, 2000, "the corpus should give thousands of mutations")
        self.assertLess(allowed, checked // 50, "only the recorded divergences may differ")
        # Q1 and Q3 stopped firing when the kit adopted both readings; the branches stay so that
        # a regression in either would be named rather than merely counted.

    def test_the_corpus_as_written_agrees_exactly(self):
        for name, text in corpus():
            theirs, their_census = self.their_verdict(text)
            mine, my_census = self.my_verdict(text)
            self.assertEqual(theirs, mine, name)
            self.assertEqual(their_census, my_census, name)
