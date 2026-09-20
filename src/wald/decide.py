"""The one `decide`. V_0, Q_n, V_n and the argmax of section 2 exist here and nowhere else:
packs and fast paths supply beliefs and values, never choices (E5)."""
from fractions import Fraction

from .belief import _update, expect, push


def _q(belief, world, name, n, used):
    """Q_n(b,M,k) = sum_o P_b(o|k) W - price(k), over the outcomes of positive mass.
    W is E_{b|k,o}[u_end] at an ending outcome -- the belief is conditioned first, always --
    and V_{n-1}(b|k,o, M') otherwise, M' dropping k only if k is `once`."""
    act = world.O[name]
    v = -act.price
    for o, po in push(belief, act.kernel).items():
        if po == 0:
            continue
        posterior = _update(belief, act.kernel, o)
        if o in act.ends:
            v += po * expect(posterior, act.ends[o])
        else:
            v += po * _value(posterior, world, n - 1, used | {name})[0]
    return v


def _value(belief, world, n, used):
    """(V_n(b,M), the first entry of M attaining it). T first, then O, each in declared order;
    a later entry takes the act only by beating the incumbent, so a tie keeps the earlier one
    and the earliest of all is a terminal act (J3)."""
    best, arg = None, None
    for t, u in world.T.items():
        v = expect(belief, u)
        if best is None or v > best:
            best, arg = v, t
    if n > 0:
        for name in world.menu(used):
            v = _q(belief, world, name, n, used)
            if v > best:
                best, arg = v, name
    return best, arg


def value(belief, world, n, used=frozenset()):
    """V_n(b,M)."""
    return _value(belief, world, n, used)[0]


def decide(belief, world, n, used=frozenset()):
    """decide_n(b,M). The single exit: only this turns a belief into an act (S1)."""
    return _value(belief, world, n, used)[1]
