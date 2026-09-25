"""S15: what no plate can learn is shown, not refused. Nothing here refuses or chooses.

A realisable design is a sequence of acts within N, each `once` act at most once, an ending
outcome ending it, then an end, then the After-act. Two Global values are inseparable when every
such design gives every record the same probability under both; they fall into classes. A class
is shown when its members disagree, under some design, about what an act can feel of the state --
the differences between terminal utilities, and best(state) when the think act is declared --
jointly with that design's draws, the after-report left out.

This is exponential in N: every design is enumerated, and under each every sequence of outcomes
at every state. It is exact and it is not approximated (KERNEL.md)."""
from fractions import Fraction

from .digits import rational
from .display import render
from .episode import ending


def designs(world):
    """Every sequence of acts within the horizon, each `once` act at most once."""
    out = []

    def grow(seq, used, n):
        out.append(tuple(seq))
        if n:
            for name, act in world.O.items():
                if not (act.once and name in used):
                    grow(seq + [name], used | {name}, n - 1)

    grow([], frozenset(), world.N)
    return out


def _walk(world, state, seq, p, drawn, emit):
    """Every run of `seq` at `state`: its draws and mass, cut short by an ending outcome."""
    if not seq:
        emit(tuple(drawn), None, p)
        return
    act = world.O[seq[0]]
    for o, q in act.kernel.row(state).items():
        if q:
            if o in act.ends:
                emit(tuple(drawn + [(seq[0], o)]), ending(seq[0], o), p * q)
            else:
                _walk(world, state, seq[1:], p * q, drawn + [(seq[0], o)], emit)


def _law(plated, g, seq, t, key):
    """The law, under g, of `key(state, draws, end, after-report)` for the design (seq, then t)."""
    world, after, dist = plated.world, plated.after, {}

    for state, pl in plated.pl[g].items():
        def emit(drawn, end, p):
            end = t if end is None else end
            reports = after.kernels[end].row(state).items() if (after and end is not None) else [(None, 1)]
            for oa, qa in reports:
                if qa:
                    k = key(state, drawn, end, oa)
                    dist[k] = dist.get(k, Fraction(0)) + p * qa
        _walk(world, state, seq, pl, [], emit)
    return frozenset(dist.items())


def felt(world, state):
    """What an act can feel of a state: each terminal's utility less the first's -- a per-state
    constant changes no act (v0 C4) -- and best(state) when the think act is declared."""
    u = [table[state] for table in world.T.values()]
    part = tuple(x - u[0] for x in u)
    if world.dplus is not None:
        best = max(u)
        for act in world.O.values():
            for o, u_end in act.ends.items():
                if act.kernel.at(state, o) > 0:
                    best = max(best, u_end[state])
        part += (best,)
    return part


def classes(plated):
    """The Global values, grouped by what every realisable design's records say of them."""
    world = plated.world
    ends = list(world.T) if plated.after else [None]
    ds = designs(world)
    groups = {}
    for g in plated.pg:
        sig = tuple(_law(plated, g, seq, t, lambda s, d, e, oa: (d, e, oa)) for seq in ds for t in ends)
        groups.setdefault(sig, []).append(g)
    return list(groups.values())


def shown(plated):
    """(nothing can be learned, the classes shown, each as {g: its declared prior mass})."""
    world = plated.world
    cs = classes(plated)
    ds = designs(world)
    out = []
    for c in cs:
        kinds = set(tuple(_law(plated, g, seq, None, lambda s, d, e, oa: (felt(world, s), d)) for seq in ds)
                    for g in c)
        if len(kinds) > 1:
            out.append({g: plated.pg[g] for g in c})
    return plated.declares and len(plated.pg) > 1 and len(cs) == 1, out


def text(plated):
    """S15's disclosure as E7 prints it at declaration, with each class's declared prior mass."""
    if not plated.declares:
        return "no Global is declared: nothing is learned between episodes, and nothing is disclosed"
    nothing, cs = shown(plated)
    lines = []
    if nothing:
        lines.append("nothing this World declares as a Global can be learned")
    for c in cs:
        lines.append("no plate can tell these apart, and they disagree about what an act can feel; the declared"
                     " prior settles it forever: " + ", ".join(str(g) + " " + rational(p) for g, p in c.items()))
    if not cs:
        lines.append("no class of inseparable Global values settles anything an act can feel")
    return "\n".join(lines)


def disclosure(plated):
    return render(text(plated))
