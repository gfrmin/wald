"""The lookahead as it was before brief 013, over `Fraction`s: master at bc6fd60's `decide._q`,
`_key`, `_value`, `_best`, `_cap`, `step` and `quantities`, and `belief._split`, `_dot` and `_mass`,
copied whole, with an operation counter of their own. Kept to judge the integer lookahead against:
every act, every value and every E6 count must come out the same. Not the kernel's; a test's.

A plate's episode loop is here too (`play`), `episode._play` as it was, so that a run can be
played twice from one belief, once by each lookahead, with the same door."""
from fractions import Fraction

from wald.belief import _measure, condition
from wald.decide import FLOOR, REFUSED, STRUCK_CAP, STRUCK_N, THINK
from wald.episode import ENDED, TERMINAL, WORLD_FALSIFIED, ending
from wald.refusals import WorldFalsified
from wald.same import Sameness

OPS = [0]


def _tally(done):
    OPS[0] += done


def _split(measure, rows):
    parts = {}
    done = 0
    for state, p in measure.items():
        for o, q in rows[state].items():
            if not q:
                continue
            part = parts.get(o)
            if part is None:
                part = parts[o] = {}
            if q == 1:
                part[state] = p
            else:
                part[state] = p * q
                done += 1
    _tally(done)
    return parts


def _dot(measure, f):
    _tally(2 * len(measure))
    return sum([p * f[state] for state, p in measure.items()], Fraction(0))


def _mass(measure):
    _tally(len(measure))
    return sum(measure.values(), Fraction(0))


def _q(measure, mass, world, name, n, used, same, memo, reps):
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
    states = frozenset([(state, p.numerator, p.denominator) for state, p in measure.items()])
    return (states, n, used) if n else (states, n)


def _value(measure, world, n, used, same, memo, reps):
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


def value(belief, world, n, used=frozenset()):
    measure = _measure(belief)
    v = _value(measure, world, n, frozenset(used), Sameness(world), {}, tuple(world.T))[0]
    return v / _mass(measure)


def quantities(belief, world):
    counted = OPS[0]
    same, memo = Sameness(world), {}
    measure = _measure(belief)
    mass = _mass(measure)
    n = min(world.d, world.N)
    reps = tuple(world.T)
    T = [(t, _dot(measure, world.T[t]) / mass) for t in reps]
    O = [(name, _q(measure, mass, world, name, n, frozenset(), same, memo, reps) / mass)
         for name in world.menu(frozenset())] if n > 0 else []
    v, act = _value(measure, world, n, frozenset(), same, memo, reps)
    OPS[0] = counted
    return n, max([u for _, u in T]), T, O, v / mass, act


def _best(measure, world, menu):
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
    if not menu:
        return v0
    reach = _dot(measure, _best(measure, world, menu)) / mass
    return max(v0, reach - min([world.O[name].price for name in menu]))


def step(belief, world, n, used, same, memo):
    reps = tuple(world.T)
    used = frozenset(used)
    measure = _measure(belief)
    v, act = _value(measure, world, min(world.d, n), used, same, memo, reps)
    if world.dplus is None:
        return act, FLOOR, Fraction(0)
    menu = world.menu(used)
    if n <= world.d or not menu:
        return act, STRUCK_N, Fraction(0)
    mass = _mass(measure)
    v_d = v / mass
    v_0 = _value(measure, world, 0, used, same, memo, reps)[0] / mass
    gain = _cap(measure, mass, world, menu, v_0) - v_d
    cost = world.rate * world.ops[len(measure)]
    if gain <= cost:
        return act, STRUCK_CAP, Fraction(0)
    if v_d + world.fraction * gain - cost > v_d:
        OPS[0] = 0
        deeper = _value(measure, world, min(world.dplus, n), used, same, memo, reps)[1]
        return deeper, THINK, cost
    return act, REFUSED, Fraction(0)


def play(world, belief, door, same, memo):
    """`episode._play` as it was, on this lookahead: (acts, outcomes, status, paid, thought, steps,
    operations, the final belief, the end)."""
    n = world.N
    used = set()
    acts, outcomes, paid = [], [], Fraction(0)
    thought, operations = Fraction(0), []
    steps = {STRUCK_N: 0, STRUCK_CAP: 0, REFUSED: 0, THINK: 0}
    while True:
        act, how, cost = step(belief, world, n, frozenset(used), same, memo)
        if how in steps:
            steps[how] += 1
        if how == THINK:
            thought += cost
            operations.append(OPS[0])
        acts.append(act)
        if act in world.T:
            door.fire(act)
            return acts, outcomes, TERMINAL, paid, thought, steps, operations, belief, act
        spec = world.O[act]
        paid += spec.price
        obs = door.observe(act)
        outcomes.append(obs.value)
        try:
            belief = condition(belief, world, obs)
        except WorldFalsified:
            return acts, outcomes, WORLD_FALSIFIED, paid, thought, steps, operations, belief, None
        if obs.value in spec.ends:
            return acts, outcomes, ENDED, paid, thought, steps, operations, belief, ending(act, obs.value)
        if spec.once:
            used.add(act)
        n -= 1
