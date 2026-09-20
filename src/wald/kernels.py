"""K_k : Omega -> Dist(B_k), and the only five ways to build one (S4). Every combinator returns
rows that are Dists, so a row summing to anything but one cannot be constructed, only refused."""
from fractions import Fraction

from .dist import Dist
from .refusals import KERNEL_ROW


class Kernel:
    """A row per state. `at` reads a mass; an outcome absent from a row has mass zero."""

    __slots__ = ("_rows", "_outcomes", "_plain")

    def __init__(self, rows, refusal=KERNEL_ROW):
        r = {}
        for state, row in rows.items():
            r[state] = row if isinstance(row, Dist) else Dist(row, refusal)
        outcomes = []
        for row in r.values():
            for o in row.carrier():
                if o not in outcomes:
                    outcomes.append(o)
        self._rows = r
        self._outcomes = tuple(outcomes)
        self._plain = {state: dict(row.items()) for state, row in r.items()}

    def __setattr__(self, name, value):
        if name in self.__slots__ and not hasattr(self, name):
            return object.__setattr__(self, name, value)
        raise AttributeError("a kernel is immutable")

    def at(self, state, outcome):
        return self._rows[state].at(outcome)

    def row(self, state):
        return self._rows[state]

    def rows(self):
        """Every row at once, as plain mappings outcome -> mass. The rows themselves are Dists
        and stay Dists: this is the same numbers without a lookup and a method call per state,
        for the one loop (`belief._split`) that walks all of them."""
        return self._plain

    def states(self):
        return tuple(self._rows)

    def outcomes(self):
        return self._outcomes


def point(outcome_of):
    """The kernel that returns a fixed outcome in each state. `outcome_of` maps state -> outcome."""
    return Kernel({state: {o: Fraction(1)} for state, o in outcome_of.items()})


def table(rows):
    """The kernel written out: a declared row per state, each one a distribution or refused."""
    return Kernel(rows)


def mixture(parts):
    """Sum_i w_i K_i, over pairs (weight, kernel) whose weights are a distribution. Rows sum to
    one because each K_i's does and the weights do."""
    weights = Dist({i: w for i, (w, _) in enumerate(parts)}, KERNEL_ROW)
    kernels = [k for _, k in parts]
    states = kernels[0].states()
    rows = {}
    for state in states:
        row = {}
        for i, kernel in enumerate(kernels):
            for o, q in kernel.row(state).items():
                row[o] = row.get(o, Fraction(0)) + weights.at(i) * q
        rows[state] = row
    return Kernel(rows)


def product(left, right):
    """One act reading two independent channels at once: outcomes are pairs, masses multiply.
    Rows sum to one because (sum of a row)(sum of a row) = 1."""
    rows = {}
    for state in left.states():
        row = {}
        for a, p in left.row(state).items():
            for b, q in right.row(state).items():
                row[(a, b)] = row.get((a, b), Fraction(0)) + p * q
        rows[state] = row
    return Kernel(rows)


def composition(kernel, channel):
    """K then a channel out of B_k: sum_o K(o|w) L(c|o). Rows sum to one because a convex
    combination of distributions is a distribution."""
    rows = {}
    for state in kernel.states():
        row = {}
        for o, p in kernel.row(state).items():
            for c, q in channel.row(o).items():
                row[c] = row.get(c, Fraction(0)) + p * q
        rows[state] = row
    return Kernel(rows)
