"""The World of CHARTER v0.2: Omega as locals x Globals, the Prior as its two factors, the
After-act, and the Counts a declaration may ship. It is a layer around a v0 World and changes
nothing inside one. A state is the pair (l, g); the v0 World over those states is built by
`world.build` as any other, and every episode is played on it by v0's loop (C21).

`build` is the conversion and the refusals that are the conversion itself; `declare` adds the
rulings of S11-S14. S15 refuses nothing (`disclose.py`)."""
from collections import Counter
from fractions import Fraction
from itertools import product

from .dist import Dist
from .kernels import Kernel
from .refusals import (AFTER, GLOBAL, PLATE, PRICE, PRIOR, TABLE_SHAPE, UNSCORED, ZERO_EVIDENCE,
                       Refused)


class After:
    """The After-act: its name (the door answers it by name), its price, a kernel for every end."""

    __slots__ = ("name", "price", "kernels")

    def __init__(self, name, price, kernels):
        self.name = name
        self.price = price
        self.kernels = kernels


class Plated:
    """A declaration under CHARTER v0.2. `world` is the v0 World over Omega with the declared
    joint prior; `pg` is P(Global) and `pl` P(state | Global),
    over the states of Omega only; `counts` and `falsifier` are what the declaration shipped;
    `declares` says whether any Global dimension was declared (S15 speaks only then)."""

    __slots__ = ("world", "pg", "pl", "after", "counts", "falsifier", "score", "declares")

    def __init__(self, world, pg, pl, after, counts, falsifier, score, declares):
        self.world = world
        self.pg = pg
        self.pl = pl
        self.after = after
        self.counts = counts
        self.falsifier = falsifier
        self.score = score
        self.declares = declares


def wrap(world):
    """A v0 World as a plate sees it: one Global value, (), and no After-act. Its records move
    nothing, and every episode plays as v0.1 (C21)."""
    pl = {state: p for state, p in world.prior.items()}
    return Plated(world, {(): Fraction(1)}, {(): pl}, None, Counter(), None, None, False)


def _values(dims):
    return [tuple(v) for v in product(*[values for _, values in dims])]


def build(spec, floor=True):
    """The conversion: the two factors of the Prior, the tables restricted to Omega, the
    After-act's kernels. A table in the dict is over the product of the locals and the Globals;
    a state the Prior gives no mass is not in Omega, and what a table says there is read by
    nothing."""
    from .episode import ending
    from .world import build as build_v0

    locs, globs = _values(spec["locals"]), _values(spec["globals"])
    grid = set((l, g) for l in locs for g in globs)
    declared_g = spec["prior_global"]
    if set(declared_g) != set(globs):
        raise Refused(PRIOR, "P(Global) is not over the Global values")
    for g, p in declared_g.items():
        if p <= 0:
            raise Refused(PRIOR, "a Global value of prior zero is not in Omega: " + repr(g))
    pg = dict(Dist(declared_g, PRIOR).items())
    pl, joint = {}, {}
    for g in globs:
        row = spec["prior_local"].get(g)
        if row is None or any(l not in locs for l in row):
            raise Refused(PRIOR, "P(local | " + repr(g) + ") is not over the locals")
        row = Dist(row, PRIOR)
        pl[g] = {}
        for l in locs:
            if row.at(l) > 0:
                pl[g][(l, g)] = row.at(l)
                joint[(l, g)] = pg[g] * row.at(l)
    omega = list(joint)

    def over(table, what, refusal=TABLE_SHAPE):
        if set(table) != grid:
            raise Refused(refusal, what + " is not a table over the locals and the Globals")
        return {state: table[state] for state in omega}

    T = {t: over(u, "the utility of " + repr(t)) for t, u in spec["T"].items()}
    O = {}
    for name, s in spec["O"].items():
        u_end = s.get("u_end", {})
        ends = set(s.get("ends", ())) | set(u_end)
        if any(o not in u_end for o in ends):
            raise Refused(TABLE_SHAPE, "an ending outcome of " + repr(name) + " has no ending utility")
        O[name] = {"K": over(s["K"], "the kernel of " + repr(name)), "price": s["price"],
                   "once": s["once"], "ends": {o: {st: Fraction(u_end[o]) for st in omega} for o in ends}}

    after = None
    if spec.get("after") is not None:
        a = spec["after"]
        name = a.get("name", "after")
        if name in spec["T"] or name in spec["O"]:
            raise Refused(AFTER, "the After-act is named as an act of the menu: " + repr(name))
        want = set(spec["T"]) | set(ending(k, o) for k, s in O.items() for o in s["ends"])
        if set(a["K"]) != want:
            raise Refused(AFTER, "the After-act declares a kernel for every end, and only for the ends")
        if Fraction(a["price"]) < 0:
            raise Refused(PRICE, "the After-act is paid to be taken")
        after = After(name, Fraction(a["price"]),
                      {e: Kernel(over(K, "the After-act's kernel at " + repr(e), AFTER)) for e, K in a["K"].items()})

    inner = {key: spec[key] for key in ("N", "d", "table_sources", "sources", "components", "dplus",
                                        "fraction", "rate", "ops") if key in spec}
    inner.update(prior=joint, T=T, O=O, closed=True)
    bottom = spec.get("bottom")
    if bottom is None and not spec.get("closed", False):
        raise Refused(ZERO_EVIDENCE, "neither `closed` nor a catch-all local")
    world = build_v0(inner, floor)
    if bottom is not None:
        # v0 S5 with a catch-all local: every (bottom, g) is in Omega, and every kernel that mints a
        # report the World must absorb -- the menu's and the After-act's -- gives it all mass there.
        for g in globs:
            state = (tuple(bottom), g)
            if state not in joint:
                raise Refused(ZERO_EVIDENCE, "the catch-all local has no mass under " + repr(g))
            for name, act in world.O.items():
                if any(act.kernel.at(state, o) <= 0 for o in act.kernel.outcomes()):
                    raise Refused(ZERO_EVIDENCE, "the catch-all gives an outcome of " + repr(name) + " no mass")
            for e, K in (after.kernels.items() if after else ()):
                if any(K.at(state, o) <= 0 for o in K.outcomes()):
                    raise Refused(AFTER, "the catch-all gives an after-report under " + repr(e) + " no mass")

    counts = Counter(spec.get("counts") or {})
    return Plated(world, pg, pl, after, counts, spec.get("falsifier"), spec.get("score"),
                  bool(spec["globals"]))


def declare(spec):
    """Accept a v0.2 declaration, or refuse it by the name of the clause it breaks."""
    from . import counts as C
    from .world import _rulings

    plated = build(spec)
    globs = list(plated.pg)
    for t, u in spec["T"].items():
        for l in _values(spec["locals"]):
            if len(set(u[(l, g)] for g in globs)) > 1:
                raise Refused(GLOBAL, "the utility of " + repr(t) + " reads a Global (S11)")
    _rulings(plated.world)
    if plated.counts:
        shipped = plated.counts + (Counter([plated.falsifier]) if plated.falsifier else Counter())
        if spec.get("counts_sha") != C.counts_sha(plated.counts):
            raise Refused(PLATE, "the Counts do not hash to their declared digest (S13)")
        if not C.expressible(plated, shipped):
            raise Refused(PLATE, "no episode of this declaration could have written these Counts (S13)")
        if plated.score != C.score(plated, plated.counts):
            raise Refused(UNSCORED, "the shipped Score is not the leave-one-out predictive probability (S14)")
    return plated
