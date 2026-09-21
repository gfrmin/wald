"""SURFACE v0.1: the five declarations that give the think act a syntax, K16's provenance and
K17's census. The corpus in charter/laws/packs is the judge; these say what I meant."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from pack_fixtures import THINKER, instead, with_param, without
from wald.refusals import Refused
from wald.surface import census, check
from wald.world import declare


def refusal(text):
    try:
        check(text)
    except Refused as e:
        return e.name
    return "ACCEPTED"


FRACTION_LINE = "think(fraction"
RATE_LINE = "rate(1/1000"
DPLUS_LINE = "depth_plus(2"
COST_LINE = "cost([100, 200]"


class TheFiveDeclarations(unittest.TestCase):
    """Section 1: what each one says, and what the spec carries away."""

    def test_the_appendix_pack_carries_the_think_act(self):
        s = check(THINKER)
        self.assertEqual(s["dplus"], 2)
        self.assertEqual(s["fraction"], F(1, 2))
        self.assertEqual(s["rate"], F(1, 1000))
        self.assertEqual(s["ops"], {1: F(100), 2: F(200)})
        self.assertEqual(s["table_sources"]["dplus"], "elicited")
        self.assertEqual(s["table_sources"]["fraction"], "elicited")
        self.assertEqual(s["table_sources"]["cost"], "elicited")
        self.assertEqual(s["table_sources"]["rate"], "elicited")
        self.assertNotIn("score", s, "nothing here is fitted, so nothing is scored")
        world = declare(s)
        self.assertEqual(world.dplus, 2)

    def test_a_pack_without_them_is_a_v0_pack(self):
        v0 = without(without(without(without(THINKER, "depth_plus"), "think("), "cost("), "rate(")
        s = check(v0)
        for name in ("dplus", "fraction", "rate", "ops", "score"):
            self.assertNotIn(name, s)
        for name in ("dplus", "fraction", "cost", "rate"):
            self.assertNotIn(name, s["table_sources"])
        self.assertIsNone(declare(s).dplus)

    def test_they_come_together_or_not_at_all(self):
        for line in ("depth_plus", "think(", "cost(", "rate("):
            self.assertEqual(refusal(without(THINKER, line)), "MISSING", line)

    def test_each_is_written_at_most_once(self):
        for line in ('depth_plus(2, source="elicited")', 'think(fraction=1/2, source="elicited")',
                     'cost([100, 200], source="elicited")', 'rate(1/1000, source="elicited")'):
            self.assertEqual(refusal(THINKER.replace(line, line + "\n" + line, 1)),
                             "DUPLICATE", line)

    def test_the_cost_is_positional_and_as_long_as_omega(self):
        self.assertEqual(refusal(instead(THINKER, COST_LINE, 'cost([100], source="elicited")')),
                         "COST")
        self.assertEqual(refusal(instead(THINKER, COST_LINE,
                                         'cost([100, 200, 300], source="elicited")')), "COST")
        self.assertEqual(refusal(instead(THINKER, COST_LINE,
                                         'cost({1: 100, 2: 200}, source="elicited")')),
                         "NOT_A_DECLARATION", "a key is a position, not a numeral (K12)")

    def test_the_cost_comes_after_the_prior_that_counts_its_states(self):
        early = instead(THINKER, COST_LINE, "")
        early = early.replace('prior({"sick"', 'cost([100, 200], source="elicited")\nprior({"sick"')
        self.assertEqual(refusal(early), "MISSING")

    def test_each_source_is_the_one_the_page_fixes(self):
        self.assertEqual(refusal(instead(THINKER, DPLUS_LINE,
                                         'depth_plus(2, source="data")')), "TABLE_SOURCE")
        self.assertEqual(refusal(instead(THINKER, RATE_LINE,
                                         'rate(1/1000, source="fitted")')), "RATE")
        self.assertEqual(refusal(instead(THINKER, FRACTION_LINE,
                                         'think(fraction=1/2, source="data")')), "FRACTION")
        self.assertEqual(refusal(instead(THINKER, COST_LINE,
                                         'cost([100, 200], source="data")')), "COST")

    def test_the_kernel_still_has_the_last_word(self):
        "The surface does not repeat declare's range and depth checks under its own names (K15)."
        self.assertEqual(refusal(instead(THINKER, FRACTION_LINE,
                                         'think(fraction=3/2, source="elicited")')), "FRACTION")
        self.assertEqual(refusal(instead(THINKER, RATE_LINE,
                                         'rate(-1/1000, source="elicited")')), "RATE")
        self.assertEqual(refusal(instead(THINKER, DPLUS_LINE,
                                         'depth_plus(3, source="elicited")')), "DEPTH_PLUS")
        self.assertEqual(refusal(instead(THINKER, "depth(1", 'depth(2, source="elicited")')),
                         "DEPTH_PLUS")
        self.assertEqual(refusal(instead(THINKER, DPLUS_LINE,
                                         'depth_plus(2/3, source="elicited")')), "DEPTH_PLUS")


class TheScore(unittest.TestCase):
    """K14: one Score per fitted meta-table, named by the table it is of, measured, so `data`."""

    def fitted(self, table, *scores):
        line = {"fraction": (FRACTION_LINE, 'think(fraction=1/2, source="fitted")'),
                "cost": (COST_LINE, 'cost([100, 200], source="fitted")')}[table]
        return instead(THINKER, line[0], line[1]) + "".join(s + "\n" for s in scores)

    def test_a_fitted_table_without_its_score_is_unscored(self):
        self.assertEqual(refusal(self.fitted("fraction")), "UNSCORED")
        self.assertEqual(refusal(self.fitted("cost")), "UNSCORED")

    def test_the_score_names_the_table_it_is_of(self):
        self.assertEqual(refusal(self.fitted("fraction", 'score(17/20, of="cost", source="data")')),
                         "UNSCORED", "the Cost is not fitted, and the Fraction is unscored")
        s = check(self.fitted("fraction", 'score(17/20, of="fraction", source="data")'))
        self.assertEqual(s["score"], {"fraction": F(17, 20)})
        self.assertEqual(s["table_sources"]["fraction"], "fitted")

    def test_a_score_of_a_table_that_is_not_fitted_is_missing(self):
        self.assertEqual(refusal(THINKER + 'score(17/20, of="fraction", source="data")\n'),
                         "MISSING")

    def test_a_score_of_nothing_the_page_names(self):
        self.assertEqual(refusal(self.fitted("cost", 'score(3/4, of="rate", source="data")')),
                         "NOT_A_DECLARATION")

    def test_a_score_is_measured(self):
        self.assertEqual(refusal(self.fitted("cost", 'score(3/4, of="cost", source="elicited")')),
                         "TABLE_SOURCE")

    def test_one_score_per_table(self):
        self.assertEqual(refusal(self.fitted("cost", 'score(3/4, of="cost", source="data")',
                                             'score(1/2, of="cost", source="data")')), "DUPLICATE")

    def test_both_tables_fitted_need_both_scores(self):
        both = instead(instead(THINKER, FRACTION_LINE, 'think(fraction=1/2, source="fitted")'),
                       COST_LINE, 'cost([100, 200], source="fitted")')
        one = both + 'score(17/20, of="fraction", source="data")\n'
        self.assertEqual(refusal(one), "UNSCORED")
        s = check(one + 'score(3/4, of="cost", source="data")\n')
        self.assertEqual(s["score"], {"fraction": F(17, 20), "cost": F(3, 4)})


class Provenance(unittest.TestCase):
    """K16: a meta-table admits a parameter only if every source it descends from is one the
    table could have declared for itself. A second `param` is not a laundry."""

    def reading(self, declaration, line, replacement):
        return with_param(THINKER, declaration, line, replacement)

    def test_a_data_number_cannot_become_the_owners_rate(self):
        direct = self.reading('param("r0", 1/1000, source="data")', RATE_LINE,
                              'rate(r0, source="elicited")')
        self.assertEqual(refusal(direct), "RATE")
        hopped = self.reading('param("r0", 1/1000, source="data")\n'
                              'param("r1", r0, source="elicited")', RATE_LINE,
                              'rate(r1, source="elicited")')
        self.assertEqual(refusal(hopped), "RATE", "routing it through a second param changes nothing")

    def test_a_data_number_cannot_become_the_fraction(self):
        self.assertEqual(refusal(self.reading('param("f0", 1/2, source="data")', FRACTION_LINE,
                                              'think(fraction=f0, source="elicited")')), "FRACTION")
        self.assertEqual(refusal(self.reading('param("c0", 100, source="data")', COST_LINE,
                                              'cost([c0, 200], source="elicited")')), "COST")

    def test_depth_plus_admits_the_owner_alone(self):
        self.assertEqual(refusal(self.reading('param("two", 2, source="data")', DPLUS_LINE,
                                              'depth_plus(two, source="elicited")')), "TABLE_SOURCE")
        ok = self.reading('param("two", 2, source="elicited")', DPLUS_LINE,
                          'depth_plus(two, source="elicited")')
        self.assertEqual(check(ok)["dplus"], 2)

    def test_an_elicited_number_cannot_become_a_measurement(self):
        fitted = instead(THINKER, FRACTION_LINE, 'think(fraction=1/2, source="fitted")')
        laundered = fitted.replace('depth_plus(2',
                                   'param("e", 17/20, source="elicited")\n'
                                   'param("d", e, source="data")\ndepth_plus(2', 1)
        self.assertEqual(refusal(laundered + 'score(d, of="fraction", source="data")\n'),
                         "TABLE_SOURCE")

    def test_the_owners_two_sources_pass_both_ways(self):
        "think and cost admit elicited and fitted: a fit may read the owner, and the page says so."
        pack = self.reading('param("f0", 1/2, source="elicited")', FRACTION_LINE,
                            'think(fraction=f0, source="fitted")')
        pack += 'score(17/20, of="fraction", source="data")\n'
        self.assertEqual(check(pack)["fraction"], F(1, 2))

    def test_v0s_fence_is_underneath_and_unchanged(self):
        "A fitted param in a table that does not say fitted: TABLE_SOURCE, wherever it is."
        self.assertEqual(refusal(self.reading('param("f0", 1/2, source="fitted")', FRACTION_LINE,
                                              'think(fraction=f0, source="elicited")')),
                         "TABLE_SOURCE")
        self.assertEqual(refusal(self.reading('param("c0", 100, source="fitted")', COST_LINE,
                                              'cost([c0, 200], source="elicited")')),
                         "TABLE_SOURCE")


class Census(unittest.TestCase):
    """K17: a parameter counts once at its declaration under its own source; a cell counts once
    under its table's source, written in place or read from a parameter."""

    def test_the_appendix_census_is_the_pages(self):
        # SURFACE v0.1's appendix: data 6, elicited 12 (horizon, depth, 4 utilities, 1 price,
        # depth+, fraction, 2 cost cells, rate), fitted 0.
        self.assertEqual(census(THINKER), {"data": 6, "elicited": 12, "fitted": 0})

    def test_a_fitted_cell_reading_an_elicited_param_counts_on_both_sides(self):
        # packs/ok/fitted_think_reads_elicited.py: data 7, elicited 12, fitted 1.
        pack = with_param(THINKER, 'param("f0", 1/2, source="elicited")', FRACTION_LINE,
                          'think(fraction=f0, source="fitted")')
        pack += 'score(17/20, of="fraction", source="data")\n'
        self.assertEqual(census(pack), {"data": 7, "elicited": 12, "fitted": 1})

    def test_the_positions_of_the_cost_list_are_not_numbers(self):
        "K12: |Omega| cells, and the positions count for nothing."
        three = instead(instead(THINKER, 'prior({"sick"',
                                'prior({"sick": 1/5, "well": 3/5, "odd": 1/5}, source="data")'),
                        COST_LINE, 'cost([100, 200, 300], source="elicited")')
        three = three.replace('["sick", "well"]', '["sick", "well", "odd"]')
        three = three.replace('{"sick": 0, "well": -2}', '{"sick": 0, "well": -2, "odd": -1}')
        three = three.replace('{"sick": -10, "well": 0}', '{"sick": -10, "well": 0, "odd": -1}')
        three = three.replace('"well": {"+": 1/5, "-": 4/5}',
                              '"well": {"+": 1/5, "-": 4/5}, "odd": {"+": 1/2, "-": 1/2}')
        self.assertEqual(check(three)["ops"], {1: F(100), 2: F(200), 3: F(300)})
        # The appendix's 12, and a third state adds one Cost cell and two utilities. The
        # positions 1, 2, 3 are keys and count for nothing.
        self.assertEqual(census(three)["elicited"], 15)


if __name__ == "__main__":
    unittest.main()
