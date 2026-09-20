"""Two acts a belief cannot tell apart are one act, and J3 already says which of them is played:
the first in menu order (E2). This module decides sameness and nothing else. It never compares a
value and never picks an act -- it hands `decide` a shorter menu of exactly the same acts.

Sameness has to be cheaper than the values it saves, so every cell, row, u_end table and price of
a World is read once into a small integer. Two rationals are then compared once, here, and never
again inside the lookahead: a signature is a tuple of integers."""


def _intern(pool, key):
    """One small integer per distinct thing. Equal things get equal integers."""
    got = pool.get(key)
    if got is None:
        got = pool[key] = len(pool)
    return got


def _cell(pool, q):
    return _intern(pool, (q.numerator, q.denominator))


def _table(pool, table, omega):
    return _intern(pool, frozenset((state, _cell(pool, table[state])) for state in omega))


def _row(pool, dist):
    """A kernel row. A mass of zero is left out: an outcome the row cannot emit is not a
    difference between two rows, and B_k is a property of the act, carried in `fixed` below."""
    return _intern(pool, frozenset((o, _cell(pool, q)) for o, q in dist.items() if q))


class Sameness:
    """A World's tables, read once into integers, and the two questions asked of them."""

    __slots__ = ("cell", "row", "fixed")

    def __init__(self, world):
        pool = {}
        omega = world.prior.carrier()
        self.cell = {t: {state: _cell(pool, u[state]) for state in omega} for t, u in world.T.items()}
        self.row, self.fixed = {}, {}
        for name, act in world.O.items():
            kernel = act.kernel
            self.row[name] = {state: _row(pool, kernel.row(state)) for state in omega}
            ends = frozenset((o, _table(pool, u_end, omega)) for o, u_end in act.ends.items())
            self.fixed[name] = (_cell(pool, act.price), act.once, _intern(pool, ends))

    def terminals(self, reps, states):
        """The first of each group of terminal acts that agree at every state of `states`.

        `reps` may be the answer for any superset of `states`: restricting to fewer states can
        only merge groups, never split one, and the first act of a merged group is the first act
        of one of the groups it merged, so it is already in `reps`. The chain therefore sifts four
        representatives where the World has two hundred acts."""
        cell, seen, out = self.cell, set(), []
        for t in reps:
            u = cell[t]
            key = tuple([u[state] for state in states])
            if key not in seen:
                seen.add(key)
                out.append(t)
        return out

    def acts(self, names, states):
        """The first of each group of observational acts that agree on `states`: the same price,
        the same `once`, the same ending outcomes with the same u_end, and the same row at every
        state the belief still carries. What they do at a state of mass zero cannot matter: no
        conditioning revives one, so every support in reach is inside this one."""
        row, fixed, seen, out = self.row, self.fixed, set(), []
        for name in names:
            r = row[name]
            key = (fixed[name], tuple([r[state] for state in states]))
            if key not in seen:
                seen.add(key)
                out.append(name)
        return out
