"""The one `decide`. V_0, Q_n, V_n and the argmax of section 2 exist here and nowhere else:
packs and fast paths supply beliefs and values, never choices (E5).

Under the loop are E2's three fast paths, and none of them is a choice. The belief is carried
unnormalised, so `push`, `condition` and expectation happen in one pass and no division is done
(`belief._split`). The menu is read as one act per group of acts the belief cannot tell apart,
which is J3's act and a shorter list of the same acts (`same`). And a value already worked out
for a measure, a menu and an n is looked up (`world.work`). Nothing is approximate: no threshold,
no sample, no bound, no float. The argmax below is the page's, written once."""
from fractions import Fraction

from .belief import _dot, _mass, _measure, _split


def _q(measure, mass, world, name, n, used, same, memo, reps):
    """Q_n(b,M,k) x mass, over the outcomes of positive mass: the price is paid on the whole mass,
    and each part of the split is already P_b(o|k) mass (b|k,o), so it carries its own weight.
    An ending outcome earns E_{b|k,o}[u_end] -- the belief is conditioned first, always -- and
    every other outcome earns V_{n-1}(b|k,o, M'), M' dropping k only if k is `once`."""
    act = world.O[name]
    v = -act.price * mass
    ahead = used | {name}
    for o, part in _split(measure, act.kernel.rows()).items():
        u_end = act.ends.get(o)
        if u_end is None:
            v += _value(part, world, n - 1, ahead, same, memo, reps)[0]
        else:
            v += _dot(part, u_end)
    return v


def _key(measure, n, used):
    """A measure, a menu and an n name a value. At n = 0 the menu is not in the answer: only the
    terminal acts are in reach, and T never leaves the menu."""
    states = frozenset([(state, p.numerator, p.denominator) for state, p in measure.items()])
    return (states, n, used) if n else (states, n)


def _value(measure, world, n, used, same, memo, reps):
    """(V_n(b,M) x mass, the first entry of M attaining it). T first, then O, each in declared
    order; a later entry takes the act only by beating the incumbent, so a tie keeps the earlier
    one and the earliest of all is a terminal act (J3). The entries not scanned are the ones an
    entry that is scanned is identical to, so the first attaining entry is among them."""
    key = _key(measure, n, used)
    got = memo.get(key)
    if got is not None:
        return got
    states = tuple(measure)
    reps = same.terminals(reps, states)
    best, arg = None, None
    for t in reps:
        v = _dot(measure, world.T[t])
        if best is None or v > best:
            best, arg = v, t
    if n > 0:
        menu = world.menu(used)
        if menu:
            mass = _mass(measure)
            for name in same.acts(menu, states):
                v = _q(measure, mass, world, name, n, used, same, memo, reps)
                if v > best:
                    best, arg = v, name
    got = (best, arg)
    memo[key] = got
    return got


def _solve(belief, world, n, used):
    same, memo = world.work()
    measure = _measure(belief)
    return measure, _value(measure, world, n, frozenset(used), same, memo, tuple(world.T))


def value(belief, world, n, used=frozenset()):
    """V_n(b,M)."""
    measure, (v, _) = _solve(belief, world, n, used)
    return v / _mass(measure)


def decide(belief, world, n, used=frozenset()):
    """decide_n(b,M). The single exit: only this turns a belief into an act (S1)."""
    return _solve(belief, world, n, used)[1][1]
