"""The one `decide`. V_0, Q_n, V_n and the argmax of section 2 exist here and nowhere else:
packs and fast paths supply beliefs and values, never choices (E5). Beside it, and made of it,
is CHARTER v0.1's `decide+`: the same argmax over a menu with one more entry on it, the think
act, whose value is the room a deeper look could find priced against what it costs (S8).

Under the loop are E2's three fast paths, and none of them is a choice. The belief is carried
unnormalised, so `push`, `condition` and expectation happen in one pass and no division is done
(`belief._split`). The menu is read as one act per group of acts the belief cannot tell apart,
which is J3's act and a shorter list of the same acts (`same`). And a value already worked out
for a measure, a menu and an n is looked up (`world.work`). Nothing is approximate: no threshold,
no sample, no bound, no float. The argmax below is the page's, written once.

Inside the lookahead every number is an int (brief 013). The measure is ints `a` over a denominator
`c` (`belief._integers`), the World's tables are ints (`scaled.py`), and a value n looks from the
end is U D^n mass(a) V_n(a): the page's value times one positive whole number, the same for every
entry a node compares, so every comparison is the page's comparison, ties included (J3). A value
leaves the lookahead -- in `value`, `quantities`, `step` and the cap -- as one `Fraction`, divided
back. Each node keys the memo on (a, c) with their gcd taken out: exactly the measure a/c, so
a value is found again exactly when the same measure comes round, by whatever path."""
from fractions import Fraction
from math import gcd

from .belief import (_count_reset, _count_restore, _counted, _dot, _integers, _mass, _measure,
                     _split)
from .same import Sameness

FLOOR = "floor"
STRUCK_N = "struck_n"
STRUCK_CAP = "struck_cap"
REFUSED = "refused"
THINK = "think"


def _q(measure, c, mass, world, name, n, used, same, memo, reps, sc):
    """Q_n(b,M,k) x mass, over the outcomes of positive mass: the price is paid on the whole mass,
    and each part of the split is already P_b(o|k) mass (b|k,o), so it carries its own weight.
    An ending outcome earns E_{b|k,o}[u_end] -- the belief is conditioned first, always -- and
    every other outcome earns V_{n-1}(b|k,o, M'), M' dropping k only if k is `once`.

    In units: each part is D_k times the page's, over c D_k, so the sum is in U D^(n-1) D_k, and
    D / D_k brings it to the U D^n of every other entry at this node."""
    act = sc.O[name]
    below = sc.power(n - 1)
    v = -act.price * mass * act.full * below
    ahead = used | {name}
    under = c * act.full
    for o, part in _split(measure, act.rows, act.full).items():
        u_end = act.ends.get(o)
        if u_end is None:
            v += _value(part, under, world, n - 1, ahead, same, memo, reps, sc)[0]
        else:
            v += _dot(part, u_end) * below
    return v * act.up


def _key(measure, c, n, used):
    """A measure, a menu and an n name a value. At n = 0 the menu is not in the answer: only the
    terminal acts are in reach, and T never leaves the menu. The measure is a/c with the gcd of c
    and a already out, which writes each measure one way: the key is the measure itself."""
    states = (frozenset(measure.items()), c)
    return (states, n, used) if n else (states, n)


def _value(measure, c, world, n, used, same, memo, reps, sc):
    """(V_n(b,M) x mass in units U D^n, the first entry of M attaining it). T first, then O, each
    in declared order; a later entry takes the act only by beating the incumbent, so a tie keeps
    the earlier one and the earliest of all is a terminal act (J3). The entries not scanned are the
    ones an entry that is scanned is identical to, so the first attaining entry is among them.

    The measure comes in as ints over c; their gcd g is taken out first, the value is worked out
    and kept for what is left, and g times it is what comes back: the value is homogeneous in the
    measure, and every entry is scaled alike."""
    g = gcd(c, *measure.values())
    if g != 1:
        measure = {state: p // g for state, p in measure.items()}
        c //= g
    key = _key(measure, c, n, used)
    got = memo.get(key)
    if got is None:
        states = tuple(measure)
        reps = same.terminals(reps, states)
        here = sc.power(n)
        best, arg = None, None
        for t in reps:
            v = _dot(measure, sc.T[t]) * here
            if best is None or v > best:
                best, arg = v, t
        if n > 0:
            menu = world.menu(used)
            if menu:
                mass = _mass(measure)
                for name in same.acts(menu, states):
                    v = _q(measure, c, mass, world, name, n, used, same, memo, reps, sc)
                    if v > best:
                        best, arg = v, name
        got = memo[key] = (best, arg)
    return (got[0] * g, got[1]) if g != 1 else got


def _solve(belief, world, n, used):
    same, memo = world.work()
    sc = world.scaled()
    measure, c = _integers(_measure(belief))
    return measure, sc.scale(n), _value(measure, c, world, n, frozenset(used), same, memo,
                                        tuple(world.T), sc)


def value(belief, world, n, used=frozenset()):
    """V_n(b,M)."""
    measure, scale, (v, _) = _solve(belief, world, n, used)
    return Fraction(v, scale * _mass(measure))


def decide(belief, world, n, used=frozenset()):
    """decide_n(b,M). The single exit: only this turns a belief into an act (S1)."""
    return _solve(belief, world, n, used)[2][1]


def quantities(belief, world):
    """Section 2's quantities at a belief, the full menu and n = min(d, N), the floor's depth at an
    episode's first step (E3), for a host to read and not to choose by (kit v0.14): n; V_0; E_b[u]
    for each terminal act; Q_n(b,M,k) for each observational act, none when n = 0; and V_n with
    decide_n. Every act gets its own Q_n, a copy of an earlier act included: `same` is for the
    scan below a decision, and here no entry is skipped. The act is `_value`'s answer, the one
    lookahead's, not a second argmax. The memo is made for this call and dropped with it: the
    lookahead's values are kept by whoever plays the World (briefs 004, 010), not by a report."""
    counted = _counted()                        # E6 counts thoughts, and this is not one
    same, memo, sc = Sameness(world), {}, world.scaled()
    measure, c = _integers(_measure(belief))
    mass = _mass(measure)
    n = min(world.d, world.N)
    reps = tuple(world.T)
    T = [(t, Fraction(_dot(measure, sc.T[t]), sc.unit * mass)) for t in reps]
    O = [(name, Fraction(_q(measure, c, mass, world, name, n, frozenset(), same, memo, reps, sc),
                         sc.scale(n) * mass))
         for name in world.menu(frozenset())] if n > 0 else []
    v, act = _value(measure, c, world, n, frozenset(), same, memo, reps, sc)
    _count_restore(counted)
    return n, max([u for _, u in T]), T, O, Fraction(v, sc.scale(n) * mass), act


def _best(measure, sc, menu):
    """best(w) of the cap, times U: the most state w can still earn -- the best terminal act there,
    or the best ending outcome of a menu act whose kernel can emit it in w [J12]. Acts whose
    endings w cannot see are not in this max: the outcome is chosen, but only among the ones that
    can happen in w, which is what makes the cap a bound and not a wish."""
    out = {}
    for state in measure:
        top = max([u[state] for u in sc.T.values()])
        for name in menu:
            act = sc.O[name]
            for o, u_end in act.ends.items():
                if u_end[state] > top and act.rows[state].get(o, 0) > 0:
                    top = u_end[state]
        out[state] = top
    return out


def _cap(measure, mass, sc, world, menu, v0):
    """cap(b,M) = max( V_0(b,M), sum_w b(w) best(w) - the cheapest price in M ), and V_0 alone
    when M holds no observational act [J12]. An episode either stops at once, earning at most
    V_0, or pays at least the cheapest price and ends on some utility its state can earn: told
    the state and handed the best of those, it earns this and no more, so V_m <= cap for every m.

    One pass over the live states and the menu. V_0 is the max over terminal acts and no
    lookahead at all; nothing here evaluates V_n for n > 0, and nothing here reads d+ (S9, C19):
    the cap is a scale for f, not deliberation about deliberation."""
    if not menu:
        return v0
    reach = Fraction(_dot(measure, _best(measure, sc, menu)), sc.unit * mass)
    return max(v0, reach - min([world.O[name].price for name in menu]))


def step(belief, world, n, used=frozenset(), memo=None):
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
    given, and this is the step that knows which n that is (E3).

    The values already found are the World's (`world.work`) unless the caller brings its own: a
    plate does, and keeps it only while its episodes' prior recurs (`plate.py`)."""
    same, kept = world.work()
    sc = world.scaled()
    if memo is None:
        memo = kept
    reps = tuple(world.T)
    used = frozenset(used)
    measure, c = _integers(_measure(belief))
    v, act = _value(measure, c, world, min(world.d, n), used, same, memo, reps, sc)
    if world.dplus is None:
        return act, FLOOR, Fraction(0)          # a v0 World: the step is the floor, and no more
    menu = world.menu(used)
    if n <= world.d or not menu:
        return act, STRUCK_N, Fraction(0)
    mass = _mass(measure)                       # c, for a belief, and asked for only here
    v_d = Fraction(v, sc.scale(min(world.d, n)) * mass)
    v_0 = Fraction(_value(measure, c, world, 0, used, same, memo, reps, sc)[0], sc.unit * mass)
    gain = _cap(measure, mass, sc, world, menu, v_0) - v_d
    cost = world.rate * world.ops[len(measure)]
    if gain <= cost:
        return act, STRUCK_CAP, Fraction(0)
    if v_d + world.fraction * gain - cost > v_d:
        _count_reset()                                              # E6: the thought starts here
        deeper = _value(measure, c, world, min(world.dplus, n), used, same, memo, reps, sc)[1]
        return deeper, THINK, cost                                  # C17: what is bought is played
    return act, REFUSED, Fraction(0)
