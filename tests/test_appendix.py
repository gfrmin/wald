"""The frozen vector of the appendix, worked by hand on the page and recomputed here."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from world_fixtures import APPX_K, appendix
from wald import belief as B
from wald.decide import decide, value
from wald.kernels import Kernel
from wald.world import declare


class Appendix(unittest.TestCase):
    def setUp(self):
        self.w = declare(appendix())
        self.b = B.prior(self.w)
        self.K = Kernel(APPX_K)

    def test_expectations_of_the_terminal_acts(self):
        self.assertEqual(B.expect(self.b, self.w.T["treat"]), F(-8, 5))
        self.assertEqual(B.expect(self.b, self.w.T["leave"]), F(-2))

    def test_v0_is_treat(self):
        self.assertEqual(value(self.b, self.w, 0), F(-8, 5))
        self.assertEqual(decide(self.b, self.w, 0), "treat")

    def test_predictive(self):
        self.assertEqual(B.push(self.b, self.K)["+"], F(17, 50))
        self.assertEqual(B.push(self.b, self.K)["-"], F(33, 50))

    def test_posteriors_and_the_acts_they_take(self):
        plus = B._update(self.b, self.K, "+")
        minus = B._update(self.b, self.K, "-")
        self.assertEqual(B._weights(plus)["sick"], F(9, 17))
        self.assertEqual(B._weights(minus)["sick"], F(1, 33))
        self.assertEqual(decide(plus, self.w, 0), "treat")
        self.assertEqual(value(plus, self.w, 0), F(-16, 17))
        self.assertEqual(decide(minus, self.w, 0), "leave")
        self.assertEqual(value(minus, self.w, 0), F(-10, 33))

    def test_q1_and_the_act(self):
        self.assertEqual(value(self.b, self.w, 1), F(-51, 50))
        self.assertEqual(decide(self.b, self.w, 1), "test")

    def test_the_price_is_paid_out_of_the_value(self):
        "Q_1 is the value of looking NET of the price: -51/50 = -8/17*... - 1/2 (J2)."
        free = declare(appendix(F(0)))
        self.assertEqual(value(B.prior(free), free, 1), F(-51, 50) + F(1, 2))

    def test_attack_1_finding_5_the_regret_of_never_looking(self):
        "Never looking earns V_0; the page's regret for it is 29/50."
        self.assertEqual(value(self.b, self.w, 1) - value(self.b, self.w, 0), F(29, 50))
