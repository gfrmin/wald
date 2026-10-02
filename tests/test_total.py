"""Brief 011: `_total` asks both sides as sets, and still names every gap and every stranger,
in the order the pack wrote them."""
import unittest
from fractions import Fraction as F

import _path  # noqa: F401
from wald.refusals import TABLE_SHAPE, Refused
from wald.world import _total

OMEGA = (("a", 1), ("b", 2), ("c", 3))


class Total(unittest.TestCase):
    def refusal(self, table):
        with self.assertRaises(Refused) as caught:
            _total(table, OMEGA, "t")
        self.assertEqual(caught.exception.name, TABLE_SHAPE)
        return str(caught.exception)

    def test_a_function_on_omega_passes_as_a_dict_or_a_tuple(self):
        self.assertIsNone(_total({s: F(0) for s in reversed(OMEGA)}, OMEGA, "t"))
        self.assertIsNone(_total(tuple(reversed(OMEGA)), OMEGA, "t"))

    def test_the_gaps_are_named_in_omegas_order(self):
        self.assertIn("says nothing at ('a', 1), ('c', 3)", self.refusal((("b", 2),)))

    def test_the_strangers_are_named_in_the_tables_order(self):
        said = OMEGA + (("z", 9), ("y", 8))
        self.assertIn("speaks of ('z', 9), ('y', 8), which is not in Omega", self.refusal(said))

    def test_a_gap_is_named_before_a_stranger(self):
        self.assertIn("says nothing at ('c', 3)", self.refusal((("a", 1), ("b", 2), ("z", 9))))


if __name__ == "__main__":
    unittest.main()
