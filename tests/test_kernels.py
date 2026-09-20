"""S4: the five combinators, and that each one preserves row sums by construction."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from wald.kernels import Kernel, composition, mixture, point, product, table
from wald.refusals import Refused


def sums_to_one(k):
    return all(sum((q for _, q in k.row(s).items()), F(0)) == 1 for s in k.states())


FLIP = table({"x": {"heads": F(3, 4), "tails": F(1, 4)}, "y": {"heads": F(1, 4), "tails": F(3, 4)}})


class Combinators(unittest.TestCase):
    def test_point(self):
        k = point({"x": "here", "y": "there"})
        self.assertEqual(k.at("x", "here"), F(1))
        self.assertEqual(k.at("x", "there"), F(0))
        self.assertTrue(sums_to_one(k))

    def test_table_refuses_a_row_that_does_not_sum_to_one(self):
        with self.assertRaises(Refused) as caught:
            table({"x": {"heads": F(1, 2), "tails": F(1, 5)}})
        self.assertEqual(caught.exception.name, "KERNEL_ROW")

    def test_table_refuses_negative_mass(self):
        with self.assertRaises(Refused):
            table({"x": {"heads": F(3, 2), "tails": F(-1, 2)}})

    def test_mixture(self):
        k = mixture([(F(1, 3), FLIP), (F(2, 3), point({"x": "heads", "y": "heads"}))])
        self.assertEqual(k.at("x", "heads"), F(1, 3) * F(3, 4) + F(2, 3))
        self.assertTrue(sums_to_one(k))

    def test_mixture_refuses_weights_that_are_not_a_distribution(self):
        with self.assertRaises(Refused):
            mixture([(F(1, 3), FLIP), (F(1, 3), FLIP)])

    def test_product(self):
        k = product(FLIP, FLIP)
        self.assertEqual(k.at("x", ("heads", "tails")), F(3, 4) * F(1, 4))
        self.assertTrue(sums_to_one(k))

    def test_composition(self):
        blur = table({"heads": {"h": F(9, 10), "?": F(1, 10)}, "tails": {"t": F(9, 10), "?": F(1, 10)}})
        k = composition(FLIP, blur)
        self.assertEqual(k.at("x", "h"), F(3, 4) * F(9, 10))
        self.assertEqual(k.at("x", "?"), F(1, 10))
        self.assertTrue(sums_to_one(k))

    def test_a_kernel_is_immutable(self):
        with self.assertRaises(AttributeError):
            FLIP._rows = {}
