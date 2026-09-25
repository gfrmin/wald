"""Brief 008: SURFACE v0.2 through `wald.load_pack` and `wald.plate`. Appendix A's pack and its
shipped twin, end to end; V2.13's five digest vectors from their bytes; V2.11's text; V2.6's
multiplicities; V2.7's falsifiers and V2.8's Score; and each reading `QUESTIONS.md` records, pinned
so that changing one is a decision. The packs are written here, so these run without the charter.
The kit judges; these are how I know before it does."""
import hashlib
import unittest
from collections import Counter
from fractions import Fraction as F

import _path  # noqa: F401 -- puts src on the path
import wald
from wald import counts as C
from wald.belief import _weights
from wald.decide import decide, value
from wald.digest import canonical, digest
from wald.refusals import Refused

GOOD, POOR = ("9/10",), ("3/5",)
ROWS = '{("a1", "9/10"): {"a1": 1}, ("a2", "9/10"): {"a2": 1}, ("a1", "3/5"): {"a1": 1}, ("a2", "3/5"): {"a2": 1}}'

# SURFACE v0.2's appendix: CHARTER v0.2's appendix A as a pack (laws/packs/ok/appendix_a.py).
APPENDIX_A = '''world("appendix-a", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
space({"answer": ["a1", "a2"], "rel": ["9/10", "3/5"]})
globals(["rel"])
prior({"9/10": 1/2, "3/5": 1/2}, source="elicited")
local_prior({"9/10": {"a1": 1/2, "a2": 1/2}, "3/5": {"a1": 1/2, "a2": 1/2}}, source="elicited")
utility({"say a1": by("answer", {"a1": 1, "a2": -2}), "say a2": by("answer", {"a1": -2, "a2": 1}), "abstain": by("answer", {"a1": 0, "a2": 0})}, source="elicited")
price({"ask": 0, "grade": 0}, source="elicited")
act("ask", once=True, kernel=table({("a1", "9/10"): {"a1": 9/10, "a2": 1/10}, ("a2", "9/10"): {"a2": 9/10, "a1": 1/10}, ("a1", "3/5"): {"a1": 3/5, "a2": 2/5}, ("a2", "3/5"): {"a2": 3/5, "a1": 2/5}}, source="elicited"), reads=["answer", "rel"])
after("grade", kernel=table({"say a1": ROWS, "say a2": ROWS, "abstain": ROWS}, source="data"), reads=["answer"])
'''.replace("ROWS", ROWS)

# ... and its shipped twin: two lines added, nothing else changed (appendix_a_shipped.py).
SHIPPED = APPENDIX_A + '''counts([[[["ask", "a1"]], "say a1", "a1", 1]], sha256="c0cd11a6dbce579fb5a0ccc1e157fd2316358b4d31bcb47889e8072c50b53dba", source="data")
score(3/8, of="counts", source="data")
'''

# V2.13's five vectors: the bytes, and their SHA-256, exactly as the page prints them.
VECTORS = [
    (Counter([((("ask", "a1"),), "say a1", "a1")]), [],
     '[[[[["ask","a1"]],"say a1","a1",1]],[]]',
     "c0cd11a6dbce579fb5a0ccc1e157fd2316358b4d31bcb47889e8072c50b53dba"),
    (Counter({((("ask", "a1"),), "abstain", None): 2}), [],
     '[[[[["ask","a1"]],"abstain",null,2]],[]]',
     "0b23b8d5964a7ca207fc9c3c2a19a2126e60368254c493b1896cf4538bee6bf9"),
    (Counter([((("ask", "é"),), "say é", "é")]), [],
     '[[[[["ask","\\u00e9"]],"say \\u00e9","\\u00e9",1]],[]]',
     "d9fa0f5f5548a1aa1e95c10b51a5cfdc9f6b02ab0bf8e0a6725565f956f7ffeb"),
    (Counter([((("ask", "a1"),), "say a1", "a1")]), [((("ask", "a3"),), None, None)],
     '[[[[["ask","a1"]],"say a1","a1",1]],[[[["ask","a3"]],null,null]]]',
     "dd1eaa3a4086b8bdf45c0c114f9b3505a15d69daa233c9940fa5984d5af519d0"),
    (Counter([((("ask", "a/b\t"),), "say a1", "a1")]), [],
     '[[[[["ask","a/b\\t"]],"say a1","a1",1]],[]]',
     "710e0cda6e91f6f52f4b8a6ef6898adb2948075a12fd29b4889908abfb55e8e9"),
]


class Script(wald.Door):
    """Answers every observational act and the After-act from a list, in order; records the fires."""

    def __init__(self, *outs):
        self.outs, self.fired, self.asked = list(outs), [], []

    def outcome(self, act):
        self.asked.append(act)
        return self.outs.pop(0)

    def fire(self, act):
        self.fired.append(act)


def refusal(text):
    try:
        wald.load_pack(text, ".")
    except Refused as e:
        return e.name
    return None


def scored(text, counts, falsifiers=(), score=None):
    """`text` shipping these Counts and falsifying records, with their digest and -- unless one is
    given -- the Score the kernel computes for them."""
    rows = ", ".join("[" + repr([list(d) for d in draws]) + ", " + repr(end) + ", " + repr(report)
                     + ", " + str(n) + "]" for (draws, end, report), n in counts.items())
    out = text + 'counts([' + rows + '], sha256="' + digest(counts, falsifiers) + '", source="data")\n'
    if falsifiers:
        out += "falsifiers([" + ", ".join("[" + repr([list(d) for d in draws]) + ", " + repr(end) + ", "
                                          + repr(report) + "]" for draws, end, report in falsifiers) + "])\n"
    if score is None:
        world = wald.plate(wald.declare(wald.load_pack(text, ".")))._plated
        score = C.score(world, counts, tuple(falsifiers))
    return out + "score(" + str(score.numerator) + "/" + str(score.denominator) + ', of="counts", source="data")\n'


class AppendixA(unittest.TestCase):
    """SURFACE v0.2's appendix, through `load_pack`, `declare` and `plate`."""

    def test_the_pack_elaborates_to_the_reliability_world(self):
        W = wald.load_pack(APPENDIX_A, ".")
        self.assertEqual(W["locals"], [("answer", ["a1", "a2"])])
        self.assertEqual(W["globals"], [("rel", ["9/10", "3/5"])])
        self.assertEqual(W["prior_global"], {GOOD: F(1, 2), POOR: F(1, 2)})
        self.assertEqual(W["prior_local"], {g: {("a1",): F(1, 2), ("a2",): F(1, 2)} for g in (GOOD, POOR)})
        self.assertEqual(W["O"]["ask"]["K"][(("a1",), GOOD)], {"a1": F(9, 10), "a2": F(1, 10)})
        self.assertEqual(W["T"]["say a1"][(("a2",), POOR)], F(-2))
        self.assertEqual(W["after"]["name"], "grade")
        self.assertEqual(set(W["after"]["K"]), {"say a1", "say a2", "abstain"})
        self.assertNotIn("counts", W)
        self.assertNotIn("table_sources", W, "the kit v0.11 dict carries no sources")

    def test_census(self):
        self.assertEqual(wald.surface.census(APPENDIX_A, "."), {"data": 12, "elicited": 24, "fitted": 0})
        self.assertEqual(wald.surface.census(SHIPPED, "."), {"data": 14, "elicited": 24, "fitted": 0})

    def test_first_act_and_one_right_grade(self):
        plated = wald.declare(wald.load_pack(APPENDIX_A, "."))
        b = C.episode_prior(plated, Counter())
        self.assertEqual((value(b, plated.world, 1), decide(b, plated.world, 1)), (F(1, 4), "ask"))
        plate = wald.plate(plated)
        r = plate.run(Script("a1", "a1"))
        self.assertEqual((r.acts, r.record), (("ask", "say a1"), ((("ask", "a1"),), "say a1", "a1")))
        self.assertEqual(dict(_weights(C.posterior_global(plated, plate.counts()))), {GOOD: F(3, 5), POOR: F(2, 5)})

    def test_the_shipped_twin_starts_where_one_right_grade_leaves_it(self):
        plated = wald.declare(wald.load_pack(SHIPPED, "."))
        self.assertEqual(dict(plated.counts), {((("ask", "a1"),), "say a1", "a1"): 1})
        self.assertEqual(plated.score, F(3, 8))
        self.assertEqual(dict(_weights(C.posterior_global(plated, plated.evidence()))), {GOOD: F(3, 5), POOR: F(2, 5)})
        b = C.episode_prior(plated, plated.evidence())
        self.assertEqual((value(b, plated.world, 1), decide(b, plated.world, 1)), (F(17, 50), "ask"))
        plate = wald.plate(plated)
        r = plate.run(Script("a1", "a1"))
        self.assertEqual(r.acts, ("ask", "say a1"))
        self.assertEqual(dict(plate.counts()), {((("ask", "a1"),), "say a1", "a1"): 2})

    def test_the_reference_agrees(self):
        oracle = _path.oracle()
        if oracle is None:
            self.skipTest("the charter is not fetched")
        import surface_check
        for text in (APPENDIX_A, SHIPPED):
            self.assertEqual(wald.load_pack(text, "."), surface_check.check(text, {}, "."))


class Digest(unittest.TestCase):
    """V2.13, from its bytes: the page's five vectors, and the one trap."""

    def test_the_five_vectors(self):
        for counts, falsifiers, written, sha in VECTORS:
            self.assertEqual(canonical(counts, falsifiers), written.encode("ascii"))
            self.assertEqual(hashlib.sha256(written.encode("ascii")).hexdigest(), sha)
            self.assertEqual(digest(counts, falsifiers), sha)

    def test_del_is_escaped_and_slash_is_not(self):
        c = Counter([((("ask", "a\x7f/"),), "say a1", None)])
        self.assertIn(b'"a\\u007f/"', canonical(c))

    def test_astral_as_a_surrogate_pair_and_arrays_in_byte_order(self):
        c = Counter({((("ask", "\U0001f600"),), "z", None): 1, ((("ask", "b"),), "a", None): 12})
        self.assertEqual(canonical(c), b'[[[[["ask","\\ud83d\\ude00"]],"z",null,1],[[["ask","b"]],"a",null,12]],[]]')

    def test_the_adapter_hands_back_the_digest(self):
        from wald.kit_adapter import make_agent
        counts, falsifiers, _, sha = VECTORS[3]
        self.assertEqual(make_agent().digest(counts, falsifiers), sha)


class Text(unittest.TestCase):
    """V2.11: one pack's bytes are one pack."""

    def test_no_cr(self):
        self.assertEqual(refusal(APPENDIX_A.replace("\n", "\r\n")), "NOT_A_DECLARATION")
        self.assertEqual(refusal(SHIPPED.replace('"say a1": by', '"""say\r\na1""": by')), "NOT_A_DECLARATION")

    def test_coding_declarations(self):
        self.assertEqual(refusal("# -*- coding: latin-1 -*-\n" + APPENDIX_A), "NOT_A_DECLARATION")
        self.assertEqual(refusal("# vim: set fileencoding=cp1252 :\n" + APPENDIX_A), "NOT_A_DECLARATION")
        self.assertIsNone(refusal("# -*- coding: utf-8 -*-\n" + APPENDIX_A))
        self.assertIsNone(refusal("# coding=UTF_8\n" + APPENDIX_A))

    def test_identifiers_are_ascii(self):
        self.assertEqual(refusal(SHIPPED.replace("score(", "ſcore(")), "NOT_A_DECLARATION")
        fi = SHIPPED.replace("score(3/8", 'param("ﬁ", 3/8, source="data")\nscore(ﬁ')
        self.assertEqual(refusal(fi), "NOT_A_DECLARATION")
        # Python's parser raises ValueError, not SyntaxError, on a full-width None
        self.assertEqual(refusal(SHIPPED.replace("score(3/8", 'falsifiers([[[["ask", "a1"]], Ｎｏｎｅ, None]])\nscore(3/8')),
                         "NOT_A_DECLARATION")
        self.assertIsNone(refusal("# été — a comment may say anything\n" + APPENDIX_A))

    def test_no_surrogate_spelt_any_way(self):
        for name in ('"\\ud800"', '"\\ud83d\\ude00"', '"\\U0000dc00"'):
            self.assertEqual(refusal(APPENDIX_A.replace('"a1"', name, 1)), "NOT_A_DECLARATION", name)
        self.assertEqual(refusal(APPENDIX_A.replace('"a1"', '"\ud800"', 1)), "NOT_A_DECLARATION")

    def test_a_bom_is_not_text_python_reads(self):
        self.assertEqual(refusal("﻿" + APPENDIX_A), "SYNTAX")          # QUESTIONS.md Q16


class Records(unittest.TestCase):
    """V2.6: a multiplicity as written; V2.7: what a falsifying record may be."""

    def test_multiplicities(self):
        for written, name in (("True", "NOT_A_DECLARATION"), ("0x1", "NOT_A_DECLARATION"),
                              ("1_0", "NOT_A_DECLARATION"), ("+1", "NOT_A_DECLARATION"),
                              ("0", "NOT_A_DECLARATION"), ("1/1", "NOT_A_DECLARATION"),
                              ("1.0", "FLOAT"), ("01", "SYNTAX")):
            self.assertEqual(refusal(SHIPPED.replace('"a1", 1]]', '"a1", ' + written + "]]")), name, written)

    def test_the_reserved_prefix(self):
        self.assertEqual(refusal(SHIPPED.replace('"say a1"', '"end:ask=a1"')), "NOT_A_DECLARATION")

    def test_a_record_holds_names(self):
        self.assertEqual(refusal(SHIPPED.replace('[[["ask", "a1"]], "say a1"', '[[["ask", ["a1", "a1"]]], "say a1"')),
                         "NOT_A_DECLARATION")

    def test_empty_counts_are_counts(self):
        self.assertIsNotNone(wald.load_pack(scored(APPENDIX_A, Counter()), "."))
        self.assertEqual(refusal(APPENDIX_A + 'counts([], sha256="' + "0" * 64 + '", source="data")\n'
                                 + 'score(1, of="counts", source="data")\n'), "PLATE")

    def test_falsifiers(self):
        one = Counter([((("ask", "a1"),), "say a1", "a1")])
        self.assertIsNotNone(wald.load_pack(scored(APPENDIX_A, one, [((("ask", "a1"),), "say a1", "a2")]), "."))
        full_without_report = [((("ask", "a1"),), "say a1", None)]
        self.assertEqual(refusal(scored(APPENDIX_A, one, full_without_report, score=F(1))), "PLATE")
        self.assertEqual(refusal(scored(APPENDIX_A, one, [((), None, None)], score=F(1))), "PLATE")


class TheScore(unittest.TestCase):
    """V2.8: every copy of every record and every falsifying record, each under the prior
    conditioned on all the others -- attack session 5's refit, and signed S14's two readings."""

    REFIT = APPENDIX_A.replace('{"a1": 9/10, "a2": 1/10}', '{"a1": 9/10, "a2": 1/20, "a3": 1/20}') \
                      .replace('{"a2": 9/10, "a1": 1/10}', '{"a2": 9/10, "a1": 1/20, "a3": 1/20}') \
                      .replace('{"a1": 3/5, "a2": 2/5}', '{"a1": 3/5, "a2": 1/5, "a3": 1/5}') \
                      .replace('{"a2": 3/5, "a1": 2/5}', '{"a2": 3/5, "a1": 1/5, "a3": 1/5}')
    ONE = Counter([((("ask", "a1"),), "say a1", "a1")])
    PREFIX = [((("ask", "a3"),), None, None)]

    def test_the_refit_at_363_over_10000(self):
        text = scored(self.REFIT, self.ONE, self.PREFIX, score=F(363, 10000))
        self.assertIn("dd1eaa3a4086b8bd", text, "V2.13's fourth vector")
        plated = wald.declare(wald.load_pack(text, "."))
        self.assertEqual(C.score(plated, plated.counts, plated.falsifiers), F(363, 10000))

    def test_signed_S14_is_refused_both_ways(self):
        for s14 in (F(3, 8), F(33, 100)):
            self.assertEqual(refusal(scored(self.REFIT, self.ONE, self.PREFIX, score=s14)), "UNSCORED", s14)


class Readings(unittest.TestCase):
    """What QUESTIONS.md records, pinned: each is the page's reading where it disagrees with the
    reference, and the reference's where the page is silent."""

    def test_Q10_the_after_act_is_a_kernel_and_its_price_a_price(self):
        reads_both = APPENDIX_A.replace('reads=["answer"])', 'reads=["answer", "rel"])')
        self.assertIsNotNone(wald.load_pack(reads_both, "."))
        self.assertEqual(refusal(reads_both.replace('"abstain": {("a1", "9/10"): {"a1": 1}',
                                                    '"abstain": {("a1", "9/10"): {"a1": 1/2}')), "KERNEL_ROW")
        self.assertEqual(refusal(reads_both.replace('"abstain": {("a1", "9/10"): {"a1": 1}',
                                                    '"abstain": {("a1", "9/10"): {"a1": 3/2, "a2": -1/2}')), "KERNEL_ROW")
        self.assertEqual(refusal(APPENDIX_A.replace('"abstain": {("a1", "9/10"): {"a1": 1}',
                                                    '"abstain": {("a3", "9/10"): {"a1": 1}, ("a1", "9/10"): {"a1": 1}')),
                         "TABLE_SHAPE")
        self.assertEqual(refusal(APPENDIX_A.replace('"grade": 0}', '"grade": -1}')), "PRICE")
        self.assertEqual(refusal(APPENDIX_A.replace('globals(["rel"])\n', '').replace(
            'prior({"9/10": 1/2, "3/5": 1/2}, source="elicited")\nlocal_prior({"9/10": {"a1": 1/2, "a2": 1/2}, "3/5": {"a1": 1/2, "a2": 1/2}}, source="elicited")',
            'prior({("a1", "9/10"): 1/4, ("a2", "9/10"): 1/4, ("a1", "3/5"): 1/4, ("a2", "3/5"): 1/4}, source="elicited")').replace(
            'closed=True', 'bottom=("a1", "9/10")')), "AFTER")

    def test_Q11_a_global_value_the_prior_does_not_name_is_not_in_omega(self):
        W = wald.load_pack(APPENDIX_A.replace('"rel": ["9/10", "3/5"]', '"rel": ["9/10", "3/5", "1/2"]'), ".")
        self.assertEqual(set(W["prior_global"]), {GOOD, POOR})

    def test_Q12_a_score_of_counts_needs_counts(self):
        v0 = APPENDIX_A.replace('globals(["rel"])\n', '').replace(
            'prior({"9/10": 1/2, "3/5": 1/2}, source="elicited")\nlocal_prior({"9/10": {"a1": 1/2, "a2": 1/2}, "3/5": {"a1": 1/2, "a2": 1/2}}, source="elicited")',
            'prior({("a1", "9/10"): 1/4, ("a2", "9/10"): 1/4, ("a1", "3/5"): 1/4, ("a2", "3/5"): 1/4}, source="elicited")')
        v0 = v0[:v0.index("after(")] + "\n"
        v0 = v0.replace(', "grade": 0}', "}")
        self.assertIsNotNone(wald.load_pack(v0, "."))
        self.assertEqual(refusal(v0 + 'score(1, of="counts", source="data")\n'), "MISSING")

    def test_Q13_falsifiers_may_come_before_their_counts(self):
        text = scored(APPENDIX_A, self_one(), [((("ask", "a1"),), "say a1", "a2")])
        lines = text.split("\n")
        at = [i for i, l in enumerate(lines) if l.startswith("counts(")][0]
        lines[at], lines[at + 1] = lines[at + 1], lines[at]
        self.assertIsNotNone(wald.load_pack("\n".join(lines), "."))
        self.assertEqual(refusal(APPENDIX_A + 'falsifiers([[[["ask", "a1"]], "say a1", "a2"]])\n'), "MISSING")

    def test_Q14_an_end_is_reached_by_its_draws(self):
        plated = wald.declare(wald.load_pack(PEEK, "."))
        self.assertTrue(C.realisable(plated, ((("peek", "drop"),), "end:peek=drop", "a1")))
        self.assertTrue(C.realisable(plated, ((), "abstain", "a1")))              # a terminal needs no draw
        self.assertFalse(C.realisable(plated, ((), "end:peek=drop", "a1")))       # an ending end does
        self.assertFalse(C.realisable(plated, ((("peek", "go"),), "end:peek=drop", "a1")))

    def test_Q15_a_prefix_falsifier_ends_at_its_report(self):
        plated = wald.declare(wald.load_pack(PEEK, "."))
        self.assertTrue(C.realisable(plated, ((("peek", "go"),), None, None), falsifier=True))
        self.assertFalse(C.realisable(plated, ((("peek", "drop"),), None, None), falsifier=True))


# Appendix A with a second act `peek`, whose outcome `drop` ends the episode (QUESTIONS.md Q8).
PEEK = APPENDIX_A.replace('horizon(1,', 'horizon(2,').replace('depth(1,', 'depth(2,') \
    .replace('price({"ask": 0, "grade": 0}', 'price({"ask": 0, "peek": 0, "grade": 0}') \
    .replace('"abstain": by("answer", {"a1": 0, "a2": 0})}, source="elicited")',
             '"abstain": by("answer", {"a1": 0, "a2": 0})}, ending={"peek": {"drop": by("answer", {"a1": 0, "a2": 0})}},'
             ' source="elicited")') \
    .replace('\nafter(', '\nact("peek", once=True, kernel=table({("a1", "9/10"): {"drop": 1/2, "go": 1/2},'
             ' ("a2", "9/10"): {"drop": 1/2, "go": 1/2}, ("a1", "3/5"): {"drop": 1/2, "go": 1/2}, ("a2", "3/5"):'
             ' {"drop": 1/2, "go": 1/2}}, source="elicited"), reads=["answer"])\nafter(') \
    .replace('"abstain": ' + ROWS + '}', '"abstain": ' + ROWS + ', ("peek", "drop"): ' + ROWS + '}')


def self_one():
    return Counter([((("ask", "a1"),), "say a1", "a1")])


if __name__ == "__main__":
    unittest.main()
