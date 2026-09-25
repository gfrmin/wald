"""The surface against the reference checker, on mutations of the whole corpus.

The kit runs the corpus as written. This runs it mutated: every pack with each line deleted, each
line doubled, each pair of neighbouring lines swapped, and a list of substitutions that break one
rule apiece. My checker and the reference must reach the same verdict -- the same refusal name,
or the same World and the same census -- and where they do not, the difference must be one the
page settles and `QUESTIONS.md` records. Every divergence is collected, not just the first.

Packs are read as their bytes are written, with no newline translation (SURFACE v0.2 V2.11).
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
                 ('cost([100, 200]', 'cost([100])'), ('source="elicited")\nthink', 'source="data")\nthink'),
                 # SURFACE v0.2
                 ('globals(["rel"])', 'globals(["rel", "rel"])'), ('globals(["rel"])', 'globals([])'),
                 ('globals(["rel"])', 'globals("rel")'), ('globals(["rel"])', 'globals(["answer", "rel"])'),
                 ('globals(["rel"])', 'globals(["nope"])'), ('"a1": 1/2, "a2": 1/2}', '"a1": 1, "a2": 0}'),
                 ('"a1": 1/2, "a2": 1/2}', '"a1": 3/2, "a2": -1/2}'), ('"a1": 1/2, "a2": 1/2}', '"a1": 1/2}'),
                 ('prior({"9/10": 1/2, "3/5": 1/2}', 'prior({("9/10",): 1/2, "3/5": 1/2}'),
                 ('prior({"9/10": 1/2, "3/5": 1/2}', 'prior({"9/10": 1/2, "3/5": 1/2, "1/2": 0}'),
                 ('reads=["answer"])', 'reads=["nope"])'), ('reads=["answer"])', 'reads=["rel"])'),
                 ('"a1", 1]]', '"a1", 2]]'), ('"a1", 1]]', '"a1", 0]]'), ('"a1", 1]]', '"a1", 1.0]]'),
                 ('"a1", 1]]', '"a1", True]]'), ('"a1", 1]]', '"a1", 0x1]]'), ('"a1", 1]]', '"a1", 1_0]]'),
                 ('"a1", 1]]', '"a1", +1]]'), ('"a1", 1]]', '"a1", 1/1]]'),
                 ('"a1", 1]]', '"a1", 1], [[["ask", "a1"]], "say a1", "a1", 1]]'),
                 ('[[["ask", "a1"]], "say a1", "a1"', '[[["ask", "a1"]], None, "a1"'),
                 ('[[["ask", "a1"]], "say a1", "a1"', '[[["ask", "a1"]], "say a1", None'),
                 ('[[["ask", "a1"]], "say a1", "a1"', '[[["ask", "a1"]], "end:ask=a1", "a1"'),
                 ('score(3/8', 'score(3/7'), ('of="counts"', 'of="count"'),
                 ('after("grade"', 'after(1'), ('after("grade"', 'after("ask"'),
                 ('"abstain": {("a1", "9/10"): {"a1": 1}', '"abstain": {("a1", "9/10"): {"a1": 1/2}'),
                 ('"abstain": {("a1", "9/10"): {"a1": 1}', '"abstain": {("a1", "1/2"): {"a1": 1}, ("a1", "9/10"): {"a1": 1}'),
                 ('"grade": 0}', '"grade": -1}'), ('"say a1"', '"end:ask=a1"'),
                 ('by("answer", {"a1": 1, "a2": -2})', 'by("rel", {"9/10": 1, "3/5": -2})'),
                 ('falsifiers([[[["ask", "a3"]], None, None]])', 'falsifiers([[[["ask", "a3"]], "say a1", None]])'),
                 ('falsifiers([[[["ask", "a3"]], None, None]])', 'falsifiers([[[], None, None]])'),
                 ('"a1"', '"\\ud800"'), ('score(', 'ſcore('), ('\n', '\r\n'),
                 ('world(', '# -*- coding: latin-1 -*-\nworld(')]

# SURFACE K7: a pack that breaks several rules may be refused by any one of their names, so two
# checkers are allowed to differ here -- and one place they do. `build` reaches the World's own
# v0 rules before `_rulings` reaches CHARTER v0.1's, and `laws/surface_check.validate` is the
# other way round. Both names are of a rule the variant really breaks.
WORLD_FIRST = {"ZERO_EVIDENCE", "SHARED_SOURCE"}
THINK_ACT = {"FRACTION", "COST", "RATE", "DEPTH_PLUS", "UNSCORED", "TABLE_SOURCE"}
# The same for CHARTER v0.2's names: `plated.build` rules AFTER while it converts, before
# `plated.declare` rules GLOBAL; `counts_check.refuse` rules GLOBAL first.
CHARTER_V02 = {"GLOBAL", "AFTER", "PLATE", "UNSCORED"}
# The divergences QUESTIONS.md records: my refusal names its entry.
RECORDED = ("QUESTIONS.md Q10", "QUESTIONS.md Q12")


def variants(text):
    yield "as written", text
    lines = text.split("\n")
    for i in range(len(lines)):
        yield "minus line %d" % i, "\n".join(lines[:i] + lines[i + 1:])
        yield "line %d twice" % i, "\n".join(lines[:i + 1] + [lines[i]] + lines[i + 1:])
        if i + 1 < len(lines):
            yield "lines %d, %d swapped" % (i, i + 1), "\n".join(lines[:i] + [lines[i + 1], lines[i]] + lines[i + 2:])
    for old, new in SUBSTITUTIONS:
        if old in text:
            yield "%r -> %r" % (old, new), text.replace(old, new, 1)


def corpus():
    for folder in ("ok", "poison"):
        directory = LAWS / "packs" / folder
        for name in sorted(os.listdir(directory)):
            if name.endswith(".py"):
                yield name, (directory / name).read_bytes().decode("utf-8")     # V2.11: as written


@unittest.skipIf(S is None, "charter not fetched: run sh cage/fetch_charter.sh")
class AgainstTheReference(unittest.TestCase):
    def setUp(self):
        import surface_check
        self.reference = surface_check

    def their_verdict(self, text):
        try:
            return self.reference.check(text, {}, OK), self.reference.census(text, {}, OK), ""
        except self.reference.Refused as e:
            return e.name, None, str(e)
        except Exception as e:                      # a crash is not a refusal: QUESTIONS.md Q3, Q17
            return "raised " + type(e).__name__, None, str(e)

    def my_verdict(self, text):
        try:
            return check(text, data_dir=OK), census(text, data_dir=OK), ""
        except Refused as e:
            return e.name, None, str(e)

    def recorded(self, theirs, their_why, mine, my_why):
        """Why a divergence is allowed, or None."""
        if isinstance(theirs, str) and theirs.startswith("raised "):
            return "Q3, Q17: the reference raises where the page refuses or accepts"
        if not isinstance(theirs, str) and mine == "DUPLICATE" and "Q10" not in my_why:
            return "Q1"
        if any(q in my_why for q in RECORDED):
            return my_why[my_why.index("QUESTIONS.md"):]
        if theirs == "MISSING" and "[V2.7] counts:" in their_why:
            return "Q13: falsifying records before their Counts"
        if isinstance(mine, str) and isinstance(theirs, str):
            if mine in WORLD_FIRST and theirs in THINK_ACT:
                return "SURFACE K7: two rules, two names"
            if mine in CHARTER_V02 and theirs in CHARTER_V02:
                return "SURFACE K7: two of CHARTER v0.2's rules, two names"
        return None

    def test_every_mutation_of_every_pack(self):
        checked, allowed, unrecorded = 0, {}, []
        for name, text in corpus():
            for label, variant in variants(text):
                checked += 1
                theirs, their_census, their_why = self.their_verdict(variant)
                mine, my_census, my_why = self.my_verdict(variant)
                if theirs == mine and their_census == my_census:
                    continue
                why = self.recorded(theirs, their_why, mine, my_why)
                if why is None:
                    unrecorded.append("%s :: %s: reference %r, mine %r %s" % (
                        name, label, theirs if isinstance(theirs, str) else "a World",
                        mine if isinstance(mine, str) else "a World", my_why[:120]))
                else:
                    allowed[why] = allowed.get(why, 0) + 1
        self.assertEqual(unrecorded, [], "%d unrecorded divergences" % len(unrecorded))
        self.assertGreater(checked, 10000, "the corpus should give thousands of mutations")
        self.assertLess(sum(allowed.values()), checked // 50, "only the recorded divergences may differ")

    def test_the_corpus_as_written_agrees_exactly(self):
        for name, text in corpus():
            theirs, their_census, _ = self.their_verdict(text)
            mine, my_census, _ = self.my_verdict(text)
            self.assertEqual(theirs, mine, name)
            self.assertEqual(their_census, my_census, name)
