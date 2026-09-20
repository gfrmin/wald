"""One test per violator in laws/violators.md that brief 001 owns. A rule that forbids nothing
says nothing, so each of these is a pack or a line the kernel must refuse, by name.
(S3's unhoused numerals and unread parameters, and refusing a pack that chooses, need the
surface syntax: they are brief 002's.)"""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from world_fixtures import APPX_K, act, appendix, spec
import wald
from wald import belief as B
from wald.refusals import ObsSpent, Refused, WorldFalsified
from wald.world import declare


def refusal(s):
    try:
        declare(s)
    except Refused as e:
        return e.name
    return "ACCEPTED"


def amended(**kw):
    s = appendix()
    s.update(kw)
    return s


class S1SingleExit(unittest.TestCase):
    "out.confidence < 0.8 -- a display value reaching control flow."

    def test_a_display_value_cannot_be_compared(self):
        d = wald.report(B.prior(declare(appendix())))
        with self.assertRaises(TypeError):
            d < F(4, 5)

    def test_a_display_value_is_not_a_number_and_has_no_truth(self):
        d = wald.report(B.prior(declare(appendix())))
        for f in (lambda: float(d), lambda: int(d), lambda: bool(d), lambda: d + 1, lambda: hash(d)):
            with self.assertRaises(TypeError):
                f()

    def test_the_verbs_are_not_exported_so_a_host_never_holds_a_probability(self):
        self.assertEqual(set(wald.__all__), {"declare", "run", "Door", "report", "Display", "refusals"})
        for verb in ("push", "condition", "expect", "decide", "Belief"):
            self.assertNotIn(verb, wald.__all__)


class S2IndependentEvidence(unittest.TestCase):
    "One token used twice; two acts reading one draw that is not a component of Omega."

    def test_a_token_is_consumed_at_most_once(self):
        w = declare(appendix())
        b = B.prior(w)
        obs = _door(w, "+").observe("test")
        B.condition(b, w, obs)
        with self.assertRaises(ObsSpent):
            B.condition(b, w, obs)

    def test_two_acts_reading_one_source_are_refused(self):
        s = appendix(N=2, d=1)
        s["O"]["re-reading"] = act(APPX_K, F(1, 2))
        s["table_sources"]["kernels"]["re-reading"] = "data"
        s["sources"] = {"test": ["the_draw"], "re-reading": ["the_draw"]}
        self.assertEqual(refusal(s), "SHARED_SOURCE")

    def test_the_same_pack_with_the_draw_in_omega_is_accepted(self):
        s = appendix(N=2, d=1)
        s["O"]["re-reading"] = act(APPX_K, F(1, 2))
        s["table_sources"]["kernels"]["re-reading"] = "data"
        s["sources"] = {"test": ["the_draw"], "re-reading": ["the_draw"]}
        s["components"] = ["the_draw"]
        self.assertEqual(refusal(s), "ACCEPTED")

    def test_a_fresh_act_reading_a_named_source_is_refused(self):
        "Two executions of a `fresh` act read it twice, which is the same violation."
        s = appendix(F(1, 2), False, 2, 1)
        s["sources"] = {"test": ["the_draw"]}
        self.assertEqual(refusal(s), "SHARED_SOURCE")
        s["components"] = ["the_draw"]
        self.assertEqual(refusal(s), "ACCEPTED")

    def test_identical_kernels_are_not_a_shared_source(self):
        s = appendix(N=2, d=1)
        s["O"]["copy"] = act(APPX_K, F(1, 2))
        s["table_sources"]["kernels"]["copy"] = "data"
        self.assertEqual(refusal(s), "ACCEPTED")


class S4NormalisedKernels(unittest.TestCase):
    "abbreviate: {St: 0.5, Str: 0.2} -- the row sums to 0.7; where is the rest?"

    def test_a_short_row_is_refused(self):
        short = {"sick": {"+": F(1, 2), "-": F(1, 5)}, "well": APPX_K["well"]}
        self.assertEqual(refusal(amended(O={"test": act(short, F(1, 2))})), "KERNEL_ROW")

    def test_saying_the_remainder_is_accepted(self):
        full = {"sick": {"+": F(1, 2), "-": F(1, 5), "in full": F(3, 10)}, "well": APPX_K["well"]}
        self.assertEqual(refusal(amended(O={"test": act(full, F(1, 2))})), "ACCEPTED")


class S5ZeroEvidence(unittest.TestCase):
    "if z == 0: return prior -- or z = max(z, 1e-12)."

    def test_zero_evidence_is_never_silently_handled(self):
        w = declare(appendix())
        b = B.prior(w)
        dead = {"sick": {"+": F(1), "never": F(0)}, "well": {"+": F(1), "never": F(0)}}
        from wald.kernels import Kernel
        with self.assertRaises(WorldFalsified):
            B._update(b, Kernel(dead), "never")

    def test_a_world_that_is_neither_closed_nor_bottomed_is_refused(self):
        s = appendix()
        del s["closed"]
        self.assertEqual(refusal(s), "ZERO_EVIDENCE")

    def test_a_bottom_state_must_have_full_support(self):
        s = appendix()
        del s["closed"]
        s["bottom"] = "well"
        self.assertEqual(refusal(s), "ACCEPTED")
        s["O"] = {"test": act({"sick": {"+": F(1), "-": F(0)}, "well": {"+": F(0), "-": F(1)}}, F(1, 2))}
        self.assertEqual(refusal(s), "ZERO_EVIDENCE")


class Section1TableShape(unittest.TestCase):
    """A table over Omega is a function on Omega, and an ending outcome is an outcome of its act.
    Each of these is a pack that would run and would mean nothing where the table is silent."""

    def test_a_utility_that_is_not_total_over_omega(self):
        self.assertEqual(refusal(amended(T={"treat": {"sick": F(0)}, "leave": {"sick": F(-10), "well": F(0)}})),
                         "TABLE_SHAPE")

    def test_a_utility_that_names_a_state_outside_omega(self):
        s = amended()
        s["T"] = {"treat": {"sick": F(0), "well": F(-2), "undead": F(-1)}, "leave": s["T"]["leave"]}
        self.assertEqual(refusal(s), "TABLE_SHAPE")

    def test_a_kernel_that_is_not_total_over_omega(self):
        self.assertEqual(refusal(amended(O={"test": act({"sick": APPX_K["sick"]}, F(1, 2))})), "TABLE_SHAPE")

    def test_an_ending_outcome_the_kernel_cannot_emit(self):
        ends = {"boom": {"sick": F(0), "well": F(0)}}
        self.assertEqual(refusal(amended(O={"test": act(APPX_K, F(1, 2), True, ends)})), "TABLE_SHAPE")

    def test_a_u_end_that_is_not_total_over_omega(self):
        self.assertEqual(refusal(amended(O={"test": act(APPX_K, F(1, 2), True, {"+": {"sick": F(0)}})})),
                         "TABLE_SHAPE")

    def test_an_ending_outcome_in_B_k_with_no_mass_anywhere_is_accepted(self):
        """`cannot emit` is `not in B_k`, not `has no mass`. A declared outcome of zero mass in
        every state is in B_k: the pack has said what it is worth should the World turn out to
        allow it, and the sums of section 2 skip it. The kit's own generator draws such worlds
        (its rows are built from 0, 1, 2, 5 and 12), so refusing them would refuse a lawful pack."""
        K = {"sick": {"+": F(1), "-": F(0)}, "well": {"+": F(1), "-": F(0)}}
        s = amended(O={"test": act(K, F(1, 2), True, {"-": {"sick": F(1), "well": F(1)}})})
        self.assertEqual(refusal(s), "ACCEPTED")

    def test_the_appendix_tables_are_total(self):
        self.assertEqual(refusal(amended()), "ACCEPTED")


class E3TheFloor(unittest.TestCase):
    "depth: 0 -- never looks; every one-sided consequence passes."

    def test_depth_zero_is_refused(self):
        self.assertEqual(refusal(amended(d=0)), "DEPTH")

    def test_depth_beyond_the_horizon_is_refused(self):
        self.assertEqual(refusal(amended(d=2)), "DEPTH")
        self.assertEqual(refusal(amended(N=2, d=2)), "ACCEPTED")


class Section1Nouns(unittest.TestCase):
    def test_empty_T_is_refused(self):
        self.assertEqual(refusal(amended(T={})), "EMPTY_T")

    def test_a_state_of_prior_zero_is_not_in_omega(self):
        self.assertEqual(refusal(amended(prior={"sick": F(1), "well": F(0)})), "PRIOR")

    def test_a_prior_that_does_not_sum_to_one_is_refused(self):
        self.assertEqual(refusal(amended(prior={"sick": F(1, 5), "well": F(3, 5)})), "PRIOR")

    def test_a_price_is_not_negative(self):
        self.assertEqual(refusal(amended(O={"test": act(APPX_K, F(-1, 2))})), "PRICE")

    def test_every_table_names_its_source(self):
        self.assertEqual(refusal(amended(table_sources={"kernels": {"test": "data"}})), "TABLE_SOURCE")

    def test_a_source_outside_data_elicited_fitted_is_refused(self):
        s = amended()
        s["table_sources"]["kernels"]["test"] = "guessed"
        self.assertEqual(refusal(s), "TABLE_SOURCE")

    def test_a_belief_cannot_be_made_or_changed_from_outside(self):
        with self.assertRaises(TypeError):
            B.Belief({"sick": F(1)})
        b = B.prior(declare(appendix()))
        with self.assertRaises(AttributeError):
            b._w = {}
        self.assertEqual([a for a in dir(b) if not a.startswith("_")], [])


def _door(world, *values):
    from wald.episode import Door

    class Script(Door):
        def __init__(self, outs):
            self.outs = list(outs)

        def outcome(self, act):
            return self.outs.pop(0)

        def fire(self, act):
            pass

    return Script(values)
