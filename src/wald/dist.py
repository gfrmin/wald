"""A finite distribution over the rationals. It is the one place mass is checked to sum to one,
so a kernel row that does not (S4) cannot come into existence anywhere in the kernel."""
from fractions import Fraction

from .refusals import Refused


class Dist:
    """Mass over a finite carrier, summing to one. Refused by the name its caller gives."""

    __slots__ = ("_mass",)

    def __init__(self, mass, refusal):
        m = {}
        for point, q in mass.items():
            q = Fraction(q)
            if q < 0:
                raise Refused(refusal, "negative mass on " + repr(point))
            m[point] = q
        if sum(m.values(), Fraction(0)) != 1:
            raise Refused(refusal, "mass sums to " + str(sum(m.values(), Fraction(0))) + ", not 1")
        self._mass = m

    def __setattr__(self, name, value):
        if name in self.__slots__ and not hasattr(self, name):
            return object.__setattr__(self, name, value)
        raise AttributeError("a distribution is immutable")

    def at(self, point):
        return self._mass.get(point, Fraction(0))

    def items(self):
        return self._mass.items()

    def carrier(self):
        return tuple(self._mass)

    def __repr__(self):
        return "Dist(" + ", ".join(repr(p) + ": " + str(q) for p, q in self._mass.items()) + ")"
