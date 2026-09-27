"""Brief 009: a host ships its plate's Counts with `wald` alone, and numbers of any length.

API.md's worked example is run here exactly as API.md prints it, so the page cannot drift from the
library. Then long literals: a Score of tens of thousands of digits through `load_pack`, a cell,
a multiplicity, and the places a long literal is refused -- and Python's limit on integer
conversion, the same after every call as before it, including under the least limit a host may
set (640 digits)."""
import contextlib
import io
import os
import random
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from fractions import Fraction as F

import _path
import wald
from test_learned import APPENDIX_A
from wald.canonical import canonical
from wald.surface import Pack
from wald.refusals import SYNTAX, UNHOUSED_NUMERAL, Refused

HUGE = "7" * 5000                              # past Python's default limit of 4,300 digits


def api_blocks():
    with open(os.path.join(_path.ROOT, "API.md"), encoding="utf-8") as f:
        text = f.read()
    section = text[text.index("## Shipping a plate's Counts"):text.index("## The wire")]
    return re.findall(r"```(\w*)\n(.*?)```", section, re.S)


def graded(n, seed=1):
    """Appendix A's records as the kit's L5 draws them: `ask`, say what it reports, graded."""
    rng, recs = random.Random(seed), Counter()
    for _ in range(n):
        a = rng.choice(["a1", "a2"])
        truth = a if rng.random() < 0.8 else {"a1": "a2", "a2": "a1"}[a]
        recs[((("ask", a),), "say " + a, truth)] += 1
    return recs


def shipped(bare, counts, falsifiers, sha, score):
    rows = ", ".join("[" + repr([list(d) for d in draws]) + ", " + repr(end) + ", " + repr(after)
                     + ", " + str(n) + "]" for (draws, end, after), n in counts.items())
    text = bare + "counts([" + rows + "], sha256=" + repr(sha) + ', source="data")\n'
    if falsifiers:
        text += "falsifiers([" + ", ".join("[" + repr([list(d) for d in draws]) + ", " + repr(end)
                                           + ", " + repr(after) + "]"
                                           for draws, end, after in falsifiers) + "])\n"
    return text + "score(" + score + ', of="counts", source="data")\n'


class TheWorkedExample(unittest.TestCase):
    def test_api_md_runs_as_printed_and_prints_what_it_says(self):
        (lang, code), (_, printed) = api_blocks()[:2]
        self.assertEqual(lang, "python")
        limit = sys.get_int_max_str_digits()
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "appendix_a.py"), "w", encoding="utf-8", newline="") as f:
                f.write(APPENDIX_A)
            out, here = io.StringIO(), os.getcwd()
            os.chdir(d)
            try:
                with contextlib.redirect_stdout(out):
                    exec(compile(code, "API.md", "exec"), {"__name__": "api_example"})
            finally:
                os.chdir(here)
        self.assertIn(printed.strip(), out.getvalue())
        self.assertEqual(sys.get_int_max_str_digits(), limit)

    def test_a_falsified_plate_ships_its_falsifier_and_the_refit_declares(self):
        """A World that believes `ask` perfect, falsified by a wrong report; the refit that
        admits error ships its Counts and falsifying record, digest and Score from `wald`."""
        perfect = APPENDIX_A.replace('"9/10": 1/2, "3/5": 1/2}, source="elicited")\nlocal',
                                     '"9/10": 1/2, "3/5": 1/2}, source="elicited")\nlocal')
        perfect = perfect.replace('{"a1": 9/10, "a2": 1/10}', '{"a1": 1}').replace(
            '{"a2": 9/10, "a1": 1/10}', '{"a2": 1}').replace('{"a1": 3/5, "a2": 2/5}', '{"a1": 1}').replace(
            '{"a2": 3/5, "a1": 2/5}', '{"a2": 1}')
        world = wald.declare(wald.load_pack(perfect, "."))

        class Door(wald.Door):
            def __init__(self, answer, report):
                self.answer, self.report = answer, report

            def outcome(self, act):
                return self.report if act == "ask" else self.answer

            def fire(self, act):
                pass

        p = wald.plate(world)
        p.run(Door("a1", "a1"))
        r = p.run(Door("a1", "a2"))                  # a perfect ask reported wrong: falsified
        self.assertEqual(r.status, "WORLD_FALSIFIED")
        counts, falsifiers = p.counts(), [p.falsifier()]
        refit = wald.declare(wald.load_pack(APPENDIX_A, "."))
        text = shipped(APPENDIX_A, counts, falsifiers, wald.digest(counts, falsifiers),
                       wald.score(refit, counts, falsifiers))
        spec = wald.load_pack(text, ".")
        self.assertEqual(spec["falsifiers"], falsifiers)
        wald.declare(spec)


class TheThreeFunctions(unittest.TestCase):
    def setUp(self):
        self.world = wald.declare(wald.load_pack(APPENDIX_A, "."))

    def test_digest_is_the_first_vector(self):
        one = Counter([((("ask", "a1"),), "say a1", "a1")])
        self.assertEqual(wald.digest(one),
                         "c0cd11a6dbce579fb5a0ccc1e157fd2316358b4d31bcb47889e8072c50b53dba")
        self.assertEqual(wald.digest(dict(one), ()), wald.digest(one, []))

    def test_score_is_text_as_a_pack_writes_it(self):
        one = Counter([((("ask", "a1"),), "say a1", "a1")])
        self.assertEqual(wald.score(self.world, one), "3/8")
        self.assertEqual(wald.score(self.world, Counter()), "1")

    def test_e7_is_inert(self):
        d = wald.e7(self.world, graded(10))
        self.assertIsInstance(d, wald.Display)
        with self.assertRaises(TypeError):
            d == d
        self.assertIn("after the start: ask ", str(d))

    def test_score_of_a_v0_world(self):
        """A v0 World has one Global value, (): its Counts move nothing, every term is its
        likelihood, and the Score is written all the same (C21)."""
        from pack_fixtures import APPENDIX
        v0 = wald.declare(wald.load_pack(APPENDIX, "."))
        self.assertEqual(wald.score(v0, Counter()), "1")
        self.assertEqual(wald.score(v0, Counter([((("test", "+"),), "treat", None)])), "17/50")


class LongNumbers(unittest.TestCase):
    def setUp(self):
        self.limit = sys.get_int_max_str_digits()

    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), self.limit, "the host's limit moved")

    def test_a_score_of_tens_of_thousands_of_digits_reads_back(self):
        world = wald.declare(wald.load_pack(APPENDIX_A, "."))
        recs = graded(300)
        score = wald.score(world, recs)
        self.assertEqual(len(score.split("/")[1]), 34486)       # brief 009's number
        spec = wald.load_pack(shipped(APPENDIX_A, recs, [], wald.digest(recs), score), ".")
        wald.declare(spec)
        self.assertEqual(wald.score(world, recs), score)
        self.assertGreater(spec["score"].denominator.bit_length(), 4300 * 3)

    def test_a_long_cell_is_its_value(self):
        long_ = APPENDIX_A.replace('prior({"9/10": 1/2, "3/5": 1/2}',
                                   'prior({"9/10": ' + HUGE + '/(2*' + HUGE + '), "3/5": 1/2}')
        self.assertEqual(wald.load_pack(long_, "."), wald.load_pack(APPENDIX_A, "."))

    def test_a_long_multiplicity_is_read_and_written_as_digits(self):
        """Read by the reader alone: no one can score it, since its Score raises a likelihood to
        a power of 5,000 digits (`load_pack` would declare, and so compute it)."""
        rec = ((("ask", "a1"),), "say a1", "a1")
        n = int(HUGE[:4000]) * 10 ** 1000 + int(HUGE[:1000])     # 5,000 sevens, built without str
        text = shipped(APPENDIX_A, Counter(), [], "x", "1").replace(
            "counts([]", "counts([[[['ask', 'a1']], 'say a1', 'a1', " + HUGE + "]]")
        self.assertEqual(Pack(text, ".").counts_, Counter({rec: n}))
        self.assertTrue(canonical(Counter({rec: n})).endswith(b"," + HUGE.encode() + b"]],[]]"))
        with self.assertRaises(Refused) as e:                   # and a wrong digest, before any Score
            wald.load_pack(text, ".")
        self.assertEqual(e.exception.name, "PLATE")

    def test_a_long_literal_where_no_number_may_stand_is_unhoused(self):
        with self.assertRaises(Refused) as e:
            wald.load_pack(APPENDIX_A.replace('once=True', 'once=' + HUGE), ".")
        self.assertEqual(e.exception.name, UNHOUSED_NUMERAL)

    def test_a_long_literal_python_would_not_read_is_syntax(self):
        for bad in ("1_" + HUGE, "0" + HUGE):
            with self.assertRaises(Refused) as e:
                wald.load_pack(APPENDIX_A.replace('prior({"9/10": 1/2', 'prior({"9/10": ' + bad + '/' + bad), ".")
            self.assertEqual(e.exception.name, SYNTAX, bad[:4])

    def test_long_digits_in_a_comment_or_a_name_are_not_numbers(self):
        commented = "# " + HUGE + "\n" + APPENDIX_A.replace('world("appendix-a"', 'world("' + HUGE + '"')
        spec = wald.load_pack(commented, ".")
        self.assertEqual(spec["O"], wald.load_pack(APPENDIX_A, ".")["O"])

    def test_under_the_least_limit_a_host_may_set(self):
        """-X int_max_str_digits=640: the kernel reads and writes the same Score."""
        code = ("import sys, wald; from test_ship import *; from test_learned import APPENDIX_A\n"
                "w = wald.declare(wald.load_pack(APPENDIX_A, '.')); r = graded(300); s = wald.score(w, r)\n"
                "wald.declare(wald.load_pack(shipped(APPENDIX_A, r, [], wald.digest(r), s), '.'))\n"
                "print(sys.get_int_max_str_digits(), len(s))")
        here = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.run([sys.executable, "-X", "int_max_str_digits=640", "-c", code],
                             capture_output=True, text=True, cwd=here,
                             env={"PYTHONPATH": here + os.pathsep + os.path.join(_path.ROOT, "src")})
        self.assertEqual(out.stdout.split(), ["640", "68811"], out.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
