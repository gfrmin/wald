"""The surface: what a pack may say, what it may not, and what it elaborates to."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from pack_fixtures import (APPENDIX, ENDING_AND_BOTTOM, PRODUCT_AND_MIXTURE, TWO_COMPONENTS,
                           instead, without)
from wald.refusals import Refused
from wald.surface import census, check
from wald.world import declare


def refusal(text, data_dir="."):
    try:
        check(text, data_dir=data_dir)
    except Refused as e:
        return e.name
    return "ACCEPTED"


class Elaboration(unittest.TestCase):
    def test_the_appendix_pack_is_the_appendix_world(self):
        s = check(APPENDIX)
        self.assertEqual(s["prior"], {"sick": F(1, 5), "well": F(4, 5)})
        self.assertEqual(list(s["T"]), ["treat", "leave"])
        self.assertEqual(s["T"]["leave"], {"sick": F(-10), "well": F(0)})
        self.assertEqual(s["O"]["test"]["price"], F(1, 2))
        self.assertEqual(s["O"]["test"]["K"]["sick"], {"+": F(9, 10), "-": F(1, 10)})
        self.assertEqual(s["N"], 1)
        self.assertEqual(s["d"], 1)
        self.assertEqual(s["closed"], True)
        self.assertEqual(s["components"], ["health"])
        self.assertEqual(s["sources"], {"test": ["health"]})
        self.assertEqual(s["table_sources"]["kernels"], {"test": ["data"]})

    def test_the_menu_keeps_the_order_the_pack_declared(self):
        "J3: ties go to menu order, so the order a pack writes is part of what it says."
        s = check(TWO_COMPONENTS)
        self.assertEqual(list(s["T"]), ["go", "hold"])
        self.assertEqual(list(s["O"]), ["peek", "again"])
        flipped = check(instead(TWO_COMPONENTS, 'price({"peek"',
                                'price({"again": 1/20, "peek": 1/20}, source="elicited")'))
        self.assertEqual(list(flipped["O"]), ["peek", "again"], "the acts, not the prices, are the menu")

    def test_by_spreads_over_the_states_that_take_the_value(self):
        s = check(TWO_COMPONENTS)
        self.assertEqual(s["T"]["go"], {("x", "p"): F(1), ("x", "m"): F(1),
                                        ("y", "p"): F(-4), ("y", "m"): F(-4)})
        self.assertEqual(s["O"]["again"]["K"][("x", "m")], {"L": F(3, 4), "R": F(1, 4)})

    def test_point_emits_the_component(self):
        s = check(TWO_COMPONENTS)
        self.assertEqual(s["O"]["peek"]["K"][("y", "p")], {"p": F(1)})
        self.assertEqual(s["table_sources"]["kernels"]["peek"], [], "point holds no number")

    def test_product_mixture_and_compose_build_one_kernel(self):
        s = check(PRODUCT_AND_MIXTURE)
        K = s["O"]["both"]["K"]
        for state, row in K.items():
            self.assertEqual(sum(row.values()), F(1), state)
        lie = F(1, 10)
        clean, noisy = F(1) - lie, lie
        self.assertEqual(K["sick"][("sick", "+")], clean + noisy * (F(1, 2) * (1 - lie) + F(1, 2) * lie))
        self.assertEqual(sorted(s["table_sources"]["kernels"]["both"]), ["data", "elicited"])

    def test_an_ending_outcome_and_a_bottom_world(self):
        s = check(ENDING_AND_BOTTOM)
        self.assertEqual(s["bottom"], "rest")
        self.assertNotIn("closed", s)
        self.assertEqual(s["O"]["say a"]["ends"], {"hit": {"a": F(0), "b": F(0), "rest": F(0)}})
        declare(s)

    def test_a_fresh_act_stays_fresh(self):
        s = check(TWO_COMPONENTS)
        self.assertIs(s["O"]["again"]["once"], False)
        self.assertIs(s["O"]["peek"]["once"], True)

    def test_every_lawful_pack_here_is_a_World(self):
        for pack in (APPENDIX, TWO_COMPONENTS, PRODUCT_AND_MIXTURE, ENDING_AND_BOTTOM):
            declare(check(pack))


class Census(unittest.TestCase):
    """SURFACE section 3: the count is of quantities, not of numerals."""

    def test_the_appendix_counts_its_quantities(self):
        self.assertEqual(census(APPENDIX), {"data": 6, "elicited": 7, "fitted": 0})

    def test_the_same_world_written_in_ones_counts_the_same(self):
        "The appendix with every number built out of a single parameter u."
        in_ones = '''
world("p", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
space({"health": ["sick", "well"]})
param("u", 1, source="elicited")
prior({"sick": u/(u+u+u+u+u), "well": (u+u+u+u)/(u+u+u+u+u)}, source="elicited")
utility({"treat": {"sick": u-u, "well": -u-u}, "leave": {"sick": -(u+u+u+u+u)*(u+u), "well": u-u}}, source="elicited")
price({"test": u/(u+u)}, source="elicited")
act("test", once=True, kernel=table({"sick": {"+": u-u/((u+u+u+u+u)*(u+u)), "-": u/((u+u+u+u+u)*(u+u))}, "well": {"+": u/(u+u+u+u+u), "-": (u+u+u+u)/(u+u+u+u+u)}}, source="elicited"), reads=["health"])
'''
        self.assertEqual(sum(census(in_ones).values()), 14)
        self.assertEqual(check(in_ones)["prior"], check(APPENDIX)["prior"])

    def test_a_by_row_counts_where_it_is_written_not_once_per_state(self):
        """TWO_COMPONENTS is elicited everywhere but its prior: horizon 1, depth 1, two `by`
        utilities of 2 rows each, 2 prices, and a `by` kernel of 2 rows x 2 outcomes. Each `by`
        row counts once where it is written, though it covers two of the four states."""
        self.assertEqual(census(TWO_COMPONENTS), {"data": 4, "elicited": 1 + 1 + 4 + 2 + 4, "fitted": 0})

    def test_a_parameter_keeps_its_own_source(self):
        s = census(PRODUCT_AND_MIXTURE)
        self.assertEqual(s["fitted"], 0)
        self.assertEqual(s["data"], 2 + 4 + 4)            # the prior, and the two tables that say data
        self.assertEqual(s["elicited"], 1 + 1 + 1 + 4 + 1 + 2 + 4)  # horizon, depth, param, u, price,
        self.assertEqual(sum(s.values()), 24)             # the two weights, the garbling


class Grammar(unittest.TestCase):
    """Anything the grammar gives no form is NOT_A_DECLARATION, wherever it stands (K7)."""

    def test_forms_the_grammar_lacks(self):
        for tail in ('if True:\n    pass',
                     'x = 1',
                     'import os',
                     'print("hi")',
                     'act("t2", once=True, kernel=table({"sick": {"+": 1}}, source="data"), reads=[c for c in "h"])',
                     'act("t2", once=True, kernel=table({"sick": {"+": 1}}, source="data"), reads=["health"], extra=1)'):
            self.assertEqual(refusal(APPENDIX + tail + "\n"), "NOT_A_DECLARATION", tail)
        self.assertEqual(refusal(instead(APPENDIX, "price(",
                                         'price({"test": (lambda: 1/2)()}, source="elicited")')),
                         "NOT_A_DECLARATION")

    def test_a_cell_holds_no_call_no_branch_no_attribute(self):
        for cell in ("max(0, 1)", "1/5 if True else 1/2", "os.environ", "[1/5][0]", "f'{1}'"):
            bad = instead(APPENDIX, "prior(", 'prior({"sick": ' + cell + ', "well": 4/5}, source="data")')
            self.assertEqual(refusal(bad), "NOT_A_DECLARATION", cell)

    def test_a_decimal_is_refused_and_a_ratio_is_not(self):
        self.assertEqual(refusal(instead(APPENDIX, "price(", 'price({"test": 0.5}, source="elicited")')),
                         "FLOAT")
        self.assertEqual(refusal(instead(APPENDIX, "price(", 'price({"test": 1/2}, source="elicited")')),
                         "ACCEPTED")

    def test_a_numeral_outside_a_table_is_unhoused(self):
        self.assertEqual(refusal(instead(APPENDIX, "space(",
                                         'space({"health": ["sick", "well", 3]})')),
                         "UNHOUSED_NUMERAL")

    def test_division_by_zero(self):
        self.assertEqual(refusal(instead(APPENDIX, "price(",
                                         'price({"test": 1/(2-2)}, source="elicited")')),
                         "DIVISION_BY_ZERO")

    def test_syntax(self):
        self.assertEqual(refusal("world('p', closed=True"), "SYNTAX")

    def test_an_unknown_name_in_a_cell(self):
        self.assertEqual(refusal(instead(APPENDIX, "price(",
                                         'price({"test": 1 - p_test}, source="elicited")')),
                         "UNKNOWN_NAME")

    def test_nothing_has_a_default(self):
        for line, what in (("act(", "reads"), ("act(", "once")):
            bad = instead(APPENDIX, line, 'act("test", %s=True, kernel=table({"sick": {"+": 9/10, "-": 1/10}, "well": {"+": 1/5, "-": 4/5}}, source="data"))'
                          % ("once" if what == "reads" else "once"))
            self.assertEqual(refusal(bad), "NOT_A_DECLARATION", what)

    def test_a_declaration_that_is_not_made(self):
        for line in ("horizon(", "depth(", "space(", "prior(", "utility(", "price(", "world("):
            self.assertEqual(refusal(without(APPENDIX, line)), "MISSING", line)

    def test_a_declaration_made_twice(self):
        self.assertEqual(refusal(APPENDIX + 'depth(1, source="elicited")\n'), "DUPLICATE")

    def test_a_table_over_states_comes_after_the_prior(self):
        out_of_order = without(APPENDIX, "prior(") + 'prior({"sick": 1/5, "well": 4/5}, source="data")\n'
        self.assertEqual(refusal(out_of_order), "MISSING")


class Housing(unittest.TestCase):
    """Sources, parameters and the fitted fence (section 3)."""

    def test_every_table_names_its_source(self):
        self.assertEqual(refusal(instead(APPENDIX, "price(", 'price({"test": 1/2})')), "TABLE_SOURCE")

    def test_a_source_must_be_one_of_the_three(self):
        self.assertEqual(refusal(instead(APPENDIX, "price(",
                                         'price({"test": 1/2}, source="guessed")')), "TABLE_SOURCE")

    def test_a_parameter_nobody_reads(self):
        self.assertEqual(refusal(APPENDIX + 'param("spare", 1/10, source="data")\n'),
                         "UNREAD_PARAMETER")

    def test_a_parameter_read_twice_is_read(self):
        pack = instead(APPENDIX, "price(", 'price({"test": half}, source="elicited")')
        pack = 'param("half", 1/2, source="elicited")\n' + pack
        self.assertEqual(refusal(pack), "ACCEPTED")

    def test_fitted_does_not_promote(self):
        fenced = 'param("s", 9/10, source="fitted")\n' + instead(
            APPENDIX, "act(",
            'act("test", once=True, kernel=table({"sick": {"+": s, "-": 1 - s}, "well": {"+": 1/5, "-": 4/5}}, source="data"), reads=["health"])')
        self.assertEqual(refusal(fenced), "TABLE_SOURCE")
        self.assertEqual(refusal(fenced.replace('source="data"), reads', 'source="fitted"), reads')),
                         "ACCEPTED")

    def test_fitted_may_read_data(self):
        "The fence is one-way: a fitted table may read a data parameter."
        pack = 'param("s", 9/10, source="data")\n' + instead(
            APPENDIX, "act(",
            'act("test", once=True, kernel=table({"sick": {"+": s, "-": 1 - s}, "well": {"+": 1/5, "-": 4/5}}, source="fitted"), reads=["health"])')
        self.assertEqual(refusal(pack), "ACCEPTED")

    def test_a_parameter_is_declared_once(self):
        twice = 'param("s", 1/10, source="data")\nparam("s", 1/5, source="data")\n' + APPENDIX
        self.assertEqual(refusal(twice), "DUPLICATE")

    def test_a_parameter_name_that_no_cell_can_read(self):
        self.assertEqual(refusal('param("lambda", 1/10, source="data")\n' + APPENDIX), "BAD_NAME")


class Reads(unittest.TestCase):
    """K9: an act says what it reads, and the checker holds it to that."""

    def test_a_kernel_that_names_what_it_does_not_read(self):
        bad = instead(TWO_COMPONENTS, 'act("peek"',
                      'act("peek", once=True, kernel=point("draw"), reads=["side"])')
        self.assertEqual(refusal(bad), "UNDECLARED_READ")

    def test_a_kernel_that_depends_on_what_it_does_not_name(self):
        "The table names no component, but its rows vary with one the act does not read."
        bad = instead(TWO_COMPONENTS, 'act("again"',
                      'act("again", once=False, kernel=table({("x", "p"): {"L": 1}, ("x", "m"): {"L": 1}, ("y", "p"): {"L": 1}, ("y", "m"): {"R": 1}}, source="data"), reads=["side"])')
        self.assertEqual(refusal(bad), "UNDECLARED_READ")

    def test_a_shared_source_must_be_a_component(self):
        shared = instead(TWO_COMPONENTS, 'act("peek"',
                         'act("peek", once=True, kernel=point("draw"), reads=["draw", "the_lab"])')
        shared = instead(shared, 'act("again"',
                         'act("again", once=True, kernel=point("draw"), reads=["draw", "the_lab"])')
        self.assertEqual(refusal(shared), "SHARED_SOURCE")

    def test_a_component_read_by_two_acts_is_lawful(self):
        self.assertEqual(refusal(TWO_COMPONENTS), "ACCEPTED")

    def test_a_fresh_act_may_name_only_components(self):
        bad = instead(TWO_COMPONENTS, 'act("again"',
                      'act("again", once=False, kernel=by("side", {"x": {"L": 3/4, "R": 1/4}, "y": {"L": 1/4, "R": 3/4}}, source="elicited"), reads=["side", "the_lab"])')
        self.assertEqual(refusal(bad), "SHARED_SOURCE")


class Kernels(unittest.TestCase):
    """S4: every row is checked where it is written."""

    def test_a_row_that_does_not_sum_to_one(self):
        self.assertEqual(refusal(instead(APPENDIX, "act(",
                                         'act("test", once=True, kernel=table({"sick": {"+": 9/10, "-": 1/20}, "well": {"+": 1/5, "-": 4/5}}, source="data"), reads=["health"])')),
                         "KERNEL_ROW")

    def test_a_negative_cell_in_a_garbling(self):
        bad = 'param("lie", -1/10, source="elicited")\n' + instead(
            APPENDIX, "act(",
            'act("test", once=True, kernel=compose(table({"sick": {"+": 9/10, "-": 1/10}, "well": {"+": 1/5, "-": 4/5}}, source="data"), {"+": {"+": 1 - lie, "-": lie}, "-": {"+": lie, "-": 1 - lie}}, source="elicited"), reads=["health"])')
        self.assertEqual(refusal(bad), "KERNEL_ROW")

    def test_mixture_weights_are_a_distribution(self):
        over = instead(APPENDIX, "act(",
                       'act("test", once=True, kernel=mixture([(9/10, table({"sick": {"+": 1, "-": 0}, "well": {"+": 0, "-": 1}}, source="data")), (1/5, table({"sick": {"+": 1, "-": 0}, "well": {"+": 0, "-": 1}}, source="data"))], source="data"), reads=["health"])')
        self.assertEqual(refusal(over), "KERNEL_ROW")

    def test_a_form_that_is_not_a_kernel(self):
        self.assertEqual(refusal(instead(APPENDIX, "act(",
                                         'act("test", once=True, kernel=host("over_star", source="data"), reads=["health"])')),
                         "NOT_A_DECLARATION")

    def test_a_by_needs_a_row_for_exactly_the_values_in_omega(self):
        bad = instead(TWO_COMPONENTS, 'act("again"',
                      'act("again", once=False, kernel=by("side", {"x": {"L": 3/4, "R": 1/4}}, source="elicited"), reads=["side"])')
        self.assertEqual(refusal(bad), "TABLE_SHAPE")


class KeysWrittenTwice(unittest.TestCase):
    """SURFACE section 2: a key written twice in one dict is refused. See QUESTIONS.md Q1: the
    reference checker accepts all three of these, and the page says it should not."""

    def test_a_state_written_twice_in_the_prior(self):
        self.assertEqual(refusal(instead(APPENDIX, "prior(",
                                         'prior({"sick": 1/5, "sick": 1/2, "well": 4/5}, source="data")')),
                         "DUPLICATE")

    def test_a_terminal_act_written_twice(self):
        self.assertEqual(refusal(instead(APPENDIX, "utility(",
                                         'utility({"treat": {"sick": 0, "well": -2}, "treat": {"sick": -10, "well": 0}}, source="elicited")')),
                         "DUPLICATE")

    def test_an_ending_act_written_twice(self):
        bad = instead(ENDING_AND_BOTTOM, 'utility(',
                      'utility({"give up": {"a": -8, "b": -8, "rest": -8}}, ending={"say a": {"hit": {"a": 0, "b": 0, "rest": 0}}, "say a": {"hit": {"a": -1, "b": -1, "rest": -1}}}, source="elicited")')
        self.assertEqual(refusal(bad), "DUPLICATE")

    def test_an_ending_outcome_written_twice(self):
        bad = instead(ENDING_AND_BOTTOM, 'utility(',
                      'utility({"give up": {"a": -8, "b": -8, "rest": -8}}, ending={"say a": {"hit": {"a": 0, "b": 0, "rest": 0}, "hit": {"a": -1, "b": -1, "rest": -1}}}, source="elicited")')
        self.assertEqual(refusal(bad), "DUPLICATE")


class Inertness(unittest.TestCase):
    """R4: checking a pack runs nothing. These are texts, not programs."""

    def test_a_pack_that_would_delete_a_file_is_refused_as_text(self):
        import pathlib
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            victim = pathlib.Path(tmp) / "keep_me"
            victim.write_text("still here")
            pack = ('import pathlib\npathlib.Path(%r).unlink()\n' % str(victim)) + APPENDIX
            self.assertEqual(refusal(pack), "NOT_A_DECLARATION")
            self.assertTrue(victim.is_file(), "checking a pack must not run it")
            self.assertEqual(victim.read_text(), "still here")

    def test_a_pack_is_never_imported(self):
        "A pack whose text would raise on import is merely refused."
        self.assertEqual(refusal("raise SystemExit(1)\n"), "NOT_A_DECLARATION")
