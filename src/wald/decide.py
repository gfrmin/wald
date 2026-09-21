"""The one `decide`. V_0, Q_n, V_n and the argmax of section 2 exist here and nowhere else:
packs and fast paths supply beliefs and values, never choices (E5). Beside it, and made of it,
is CHARTER v0.1's `decide+`: the same argmax over a menu with one more entry on it, the think
act, whose value is the room a deeper look could find priced against what it costs (S8).

Under the loop are E2's three fast paths, and none of them is a choice. The belief is carried
unnormalised, so `push`, `condition` and expectation happen in one pass and no division is done
(`belief._split`). The menu is read as one act per group of acts the belief cannot tell apart,
which is J3's act and a shorter list of the same acts (`same`). And a value already worked out
for a measure, a menu and an n is looked up (`world.work`). Nothing is approximate: no threshold,
no sample, no bound, no float. The argmax below is the page's, written once."""
from fractions import Fraction

from .belief import _count_reset, _dot, _mass, _measure, _split

FLOOR = "floor"
STRUCK_N = "struck_n"
STRUCK_CAP = "struck_cap"
REFUSED = "refused"
THINK = "think"


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


def _best(measure, world, menu):
    """best(w) of the cap: the most state w can still earn -- the best terminal act there, or the
    best ending outcome of a menu act whose kernel can emit it in w [J12]. Acts whose endings w
    cannot see are not in this max: the outcome is chosen, but only among the ones that can
    happen in w, which is what makes the cap a bound and not a wish."""
    out = {}
    for state in measure:
        top = max([u[state] for u in world.T.values()])
        for name in menu:
            act = world.O[name]
            for o, u_end in act.ends.items():
                if u_end[state] > top and act.kernel.at(state, o) > 0:
                    top = u_end[state]
        out[state] = top
    return out


def _cap(measure, mass, world, menu, v0):
    """cap(b,M) = max( V_0(b,M), sum_w b(w) best(w) - the cheapest price in M ), and V_0 alone
    when M holds no observational act [J12]. An episode either stops at once, earning at most
    V_0, or pays at least the cheapest price and ends on some utility its state can earn: told
    the state and handed the best of those, it earns this and no more, so V_m <= cap for every m.

    One pass over the live states and the menu. V_0 is the max over terminal acts and no
    lookahead at all; nothing here evaluates V_n for n > 0, and nothing here reads d+ (S9, C19):
    the cap is a scale for f, not deliberation about deliberation."""
    if not menu:
        return v0
    reach = _dot(measure, _best(measure, world, menu)) / mass
    return max(v0, reach - min([world.O[name].price for name in menu]))


def step(belief, world, n, used=frozenset()):
    """decide+(b,M,n) of CHARTER v0.1 section 2: (the act, S7's bucket, the predicted cost paid).

        a v0 World (no Depth+)   -> the floor's act, "floor",      0
        n <= d, or M has no O    -> the floor's act, "struck_n",   0    ghat = 0 exactly
        ghat = cap - V_d <= c    -> the floor's act, "struck_cap", 0    bounds settle it, f unread
        V_d + f*ghat - c > V_d   -> decide_{d+}(b,M), "think",     c    theta is last in M (J14)
        otherwise                -> the floor's act, "refused",    0

    In that order, which is S7's order of precedence. Only the fourth line looks deeper, and only
    after the cost is charged (S9). The deeper look is the lookahead below with a different n --
    there is no second lookahead and no second World (E5, S8) -- so what brief 004's memo already
    worked out at depth d it does not work out again.

    The floor is applied here, and here only, because ghat reads the raw n: at n <= d the deeper
    evaluation is the same evaluation. `decide` is unchanged -- it is decide_n at the n it is
    given, and this is the step that knows which n that is (E3)."""
    same, memo = world.work()
    reps = tuple(world.T)
    used = frozenset(used)
    measure = _measure(belief)
    v, act = _value(measure, world, min(world.d, n), used, same, memo, reps)
    if world.dplus is None:
        return act, FLOOR, Fraction(0)          # a v0 World: the step is the floor, and no more
    menu = world.menu(used)
    if n <= world.d or not menu:
        return act, STRUCK_N, Fraction(0)
    mass = _mass(measure)                       # one, for a belief, and asked for only here
    v_d = v / mass
    v_0 = _value(measure, world, 0, used, same, memo, reps)[0] / mass
    gain = _cap(measure, mass, world, menu, v_0) - v_d
    cost = world.rate * world.ops[len(measure)]
    if gain <= cost:
        return act, STRUCK_CAP, Fraction(0)
    if v_d + world.fraction * gain - cost > v_d:
        _count_reset()                                              # E6: the thought starts here
        deeper = _value(measure, world, min(world.dplus, n), used, same, memo, reps)[1]
        return deeper, THINK, cost                                  # C17: what is bought is played
    return act, REFUSED, Fraction(0)
