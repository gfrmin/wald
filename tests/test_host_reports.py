"""Brief 012: what a host may ask of a plate -- `Plate.prior()`, `report(..., over=)` and
`Plate.values()` -- with nothing but the names it already holds."""
import contextlib
import io
import os
import re
import tempfile
import unittest
from fractions import Fraction as F

import _path
import wald
from test_learned import APPENDIX_A
from world_fixtures import APPX_K, act, appendix, spec
from wald.refusals import UNKNOWN_NAME, Refused, WorldFalsified


class Question(wald.Door):
    def __init__(self, answer, report):
        self.answer, self.report = answer, report

    def outcome(self, act):
        return self.report if act == "ask" else self.answer

    def fire(self, act):
        pass


def appendix_a():
    world = wald.declare(wald.load_pack(APPENDIX_A, "."))
    return world, wald.plate(world)


class Values(unittest.TestCase):
    def test_charter_v0_appendix_on_a_plate(self):
        v = wald.plate(wald.declare(appendix())).values()
        self.assertIsInstance(v, wald.Display)
        self.assertEqual(str(v), 'n 1\nV_0 -8/5\nT "treat" -8/5\nT "leave" -2\n'
                                 'O "test" -51/50 29/50\nV_n -51/50 "test"')

    def test_a_right_grade_makes_the_next_episode_worth_17_50(self):
        "CHARTER v0.2 appendix A, as its pack's header says: 1/4 before, 17/50 after."
        _, p = appendix_a()
        self.assertTrue(str(p.values()).endswith('O "ask" 1/4 1/4\nV_n 1/4 "ask"'))
        p.run(Question("a1", "a1"))
        self.assertTrue(str(p.values()).endswith('O "ask" 17/50 17/50\nV_n 17/50 "ask"'))

    def test_a_copy_of_an_act_keeps_its_own_line(self):
        "The lookahead reads one act per group of copies; `values` writes every act."
        W = appendix(F(1, 10))
        W["O"]["again"] = act(APPX_K, F(1, 10))
        W["table_sources"]["kernels"]["again"] = ["data"]
        lines = str(wald.plate(wald.declare(W)).values()).split("\n")
        self.assertEqual([l.split()[1] for l in lines if l.startswith("O ")], ['"test"', '"again"'])
        self.assertEqual(len(set(" ".join(l.split()[2:]) for l in lines if l.startswith("O "))), 1)
        self.assertEqual(lines[-1].split()[-1], '"test"')

    def test_the_last_line_is_the_act_run_takes_first(self):
        for price in (F(1, 10), F(1, 2), F(11)):
            p = wald.plate(wald.declare(appendix(price)))
            first = str(p.values()).split("\n")[-1].split()[-1].strip('"')

            class Door(wald.Door):
                def outcome(self, act):
                    return "+"

                def fire(self, act):
                    pass
            self.assertEqual(p.run(Door()).acts[0], first)

    def test_n_is_zero_without_observational_lines(self):
        W = spec({"a": F(1, 2), "b": F(1, 2)}, {"x": {"a": F(1), "b": F(0)}}, {}, N=1, d=1)
        self.assertEqual(str(wald.plate(wald.declare(W)).values()), 'n 1\nV_0 1/2\nT "x" 1/2\nV_n 1/2 "x"')


class Prior(unittest.TestCase):
    def test_prior_is_sealed_and_is_what_run_starts_from(self):
        world, p = appendix_a()
        p.run(Question("a1", "a1"))
        b = p.prior()
        self.assertEqual([a for a in dir(b) if not a.startswith("_")], [])
        self.assertEqual(str(wald.report(b, world, over=["rel"])), '["9/10"] 3/5\n["3/5"] 2/5')

    def test_report_without_over_on_a_v02_world(self):
        world, p = appendix_a()
        self.assertIn("1/4", str(wald.report(p.prior(), world)))

    def test_marginals_in_declared_order(self):
        world, p = appendix_a()
        p.run(Question("a1", "a1"))
        b = p.prior()
        self.assertEqual(str(wald.report(b, world, over=["answer"])), '["a1"] 1/2\n["a2"] 1/2')
        self.assertEqual(str(wald.report(b, world, over=["rel", "answer"])),
                         '["9/10","a1"] 3/10\n["9/10","a2"] 3/10\n["3/5","a1"] 1/5\n["3/5","a2"] 1/5')

    def test_over_names_distinct_components(self):
        world, p = appendix_a()
        b = p.prior()
        for over in ([], ["rel", "rel"], ["no such"], "rel"):
            with self.assertRaises(Refused) as e:
                wald.report(b, world, over=over)
            self.assertEqual(e.exception.name, UNKNOWN_NAME)

    def test_a_v0_world_has_no_components(self):
        world = wald.declare(appendix())
        with self.assertRaises(Refused) as e:
            wald.report(wald.plate(world).prior(), world, over=["s"])
        self.assertEqual(e.exception.name, UNKNOWN_NAME)


class Falsified(unittest.TestCase):
    def test_a_falsified_plate_has_no_prior_and_no_values(self):
        perfect = APPENDIX_A.replace('{"a1": 9/10, "a2": 1/10}', '{"a1": 1}').replace(
            '{"a2": 9/10, "a1": 1/10}', '{"a2": 1}').replace('{"a1": 3/5, "a2": 2/5}', '{"a1": 1}').replace(
            '{"a2": 3/5, "a1": 2/5}', '{"a2": 1}')
        p = wald.plate(wald.declare(wald.load_pack(perfect, ".")))
        self.assertEqual(p.run(Question("a2", "a1")).status, "WORLD_FALSIFIED")
        self.assertRaises(WorldFalsified, p.prior)
        self.assertRaises(WorldFalsified, p.values)


class TheWorkedExample(unittest.TestCase):
    def test_api_md_runs_as_printed_and_prints_what_it_says(self):
        with open(os.path.join(_path.ROOT, "API.md"), encoding="utf-8") as f:
            text = f.read()
        section = text[text.index("## What a host may ask of a plate"):text.index("## Declaring what is learned")]
        (lang, code), (_, printed) = re.findall(r"```(\w*)\n(.*?)```", section, re.S)[:2]
        self.assertEqual(lang, "python")
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
        self.assertEqual(out.getvalue().strip(), printed.strip())


class OneConvention(unittest.TestCase):
    def test_declare_raises(self):
        W = appendix()
        W["T"] = {}
        self.assertRaises(Refused, wald.declare, W)


if __name__ == "__main__":
    unittest.main()
