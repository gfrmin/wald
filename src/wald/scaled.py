"""A World's tables in units where every number the lookahead adds or multiplies is an int (brief
013). Nothing here is a value or a choice: it is the same tables, each multiplied by one positive
whole number, so that `decide` can do with `int`s the sums it did with `Fraction`s, whose every
addition took a gcd.

    U    the lcm of the denominators of every terminal utility, every u_end and every price
    D_k  the lcm of the denominators of act k's kernel rows;  R_k = D_k K_k
    D    the lcm of the D_k

A measure is then a vector of ints `a` over a denominator `c`, and `decide._value` gives
U D^n mass(m) V_n(m) for it: U_n of `belief.py` is homogeneous of degree one in the measure, so
scaling the measure scales the value, and every entry compared at a node is scaled by the same
positive number. Built once per World, as `Sameness` is, and kept with it: a fact about the World,
not about any belief."""
from math import lcm


def _over(table, unit):
    """A table times `unit`, which clears every denominator in it."""
    return {key: q.numerator * (unit // q.denominator) for key, q in table.items()}


class Act:
    """One observational act in these units: its rows R_k, D_k itself, D / D_k, its price times U,
    and each ending outcome's u_end times U."""

    __slots__ = ("rows", "full", "up", "price", "ends")

    def __init__(self, act, unit, full, up):
        self.full, self.up = full, up
        self.rows = {state: _over(row, full) for state, row in act.kernel.rows().items()}
        self.price = act.price.numerator * (unit // act.price.denominator)
        self.ends = {o: _over(u_end, unit) for o, u_end in act.ends.items()}


class Scaled:
    """The World's tables over U and the D_k, and the powers of D the lookahead asks for."""

    __slots__ = ("unit", "D", "T", "O", "_powers")

    def __init__(self, world):
        dens = {q.denominator for u in world.T.values() for q in u.values()}
        for act in world.O.values():
            dens.add(act.price.denominator)
            dens.update(q.denominator for u_end in act.ends.values() for q in u_end.values())
        self.unit = lcm(*dens)
        fulls = {name: lcm(*{q.denominator for row in act.kernel.rows().values() for q in row.values()})
                 for name, act in world.O.items()}
        self.D = lcm(*fulls.values()) if fulls else 1
        self.T = {t: _over(u, self.unit) for t, u in world.T.items()}
        self.O = {name: Act(act, self.unit, fulls[name], self.D // fulls[name])
                  for name, act in world.O.items()}
        self._powers = [1]

    def power(self, n):
        """D^n."""
        powers = self._powers
        while len(powers) <= n:
            powers.append(powers[-1] * self.D)
        return powers[n]

    def scale(self, n):
        """U D^n: the units of a value n looks from the end."""
        return self.unit * self.power(n)
