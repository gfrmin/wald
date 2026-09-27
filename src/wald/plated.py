"""The World of CHARTER v0.2: Omega as locals x Globals, the Prior as its two factors, the
After-act, and the Counts a declaration may ship with their falsifying records. It is a layer
around a v0 World and changes nothing inside one. A state is the pair (l, g); the v0 World over
those states is built by `world.build` as any other, and every episode is played on it by v0's
loop (C21).

The dict is laws/model.py's World. A table in it is over Omega's states -- the pairs P(Global)
and P(local | Global) give positive mass (SURFACE v0.2 V2.4) -- and may say more: kit v0.11
writes its tables over the whole product, and what a table says off Omega is read by nothing.

`build` is the conversion and the refusals that are the conversion itself; `declare` adds the
rulings of S11-S14, S13 and S14 as SURFACE v0.2 V2.7, V2.8 and V2.13 decide them. S15 refuses
nothing (`disclose.py`)."""
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
    joint prior; `pg` is P(Global) and `pl` P(state | Global), over the states of Omega only;
    `counts` and `falsifiers` are what the declaration shipped, and `ships` whether it shipped
    anything at all -- empty Counts are Counts (V2.6); `declares` says whether any Global
    dimension was declared (S15 speaks only then)."""

    __slots__ = ("world", "pg", "pl", "after", "counts", "falsifiers", "score", "ships", "declares")

    def __init__(self, world, pg, pl, after, counts, falsifiers, score, ships, declares):
        self.world = world
        self.pg = pg
        self.pl = pl
        self.after = after
        self.counts = counts
        self.falsifiers = falsifiers
        self.score = score
        self.ships = ships
        self.declares = declares

    def evidence(self):
        """Everything the plate's prior conditions on: the Counts and every falsifying record
        shipped with them (S13, J26)."""
        return self.counts + Counter(self.falsifiers)


def wrap(world):
    """A v0 World as a plate sees it: one Global value, (), and no After-act. Its records move
    nothing, and every episode plays as v0.1 (C21)."""
    pl = {state: p for state, p in world.prior.items()}
    return Plated(world, {(): Fraction(1)}, {(): pl}, None, Counter(), (), None, False, False)


def _values(dims):
    return [tuple(v) for v in product(*[values for _, values in dims])]


def _local(bottom):
    """The catch-all local, spelt as a pack spells a state: a name, or a tuple of names."""
    return bottom if isinstance(bottom, tuple) else tuple(bottom) if isinstance(bottom, list) else (bottom,)


def build(spec, floor=True):
    """The conversion: the two factors of the Prior, the tables restricted to Omega, the
    After-act's kernels. A dict with `table_sources` has them checked as any spec's; the dict
    SURFACE v0.2 elaborates a pack to has none -- the surface has already judged every source --
    and is judged on everything else."""
    from .episode import ending
    from .world import build as build_v0

    locs, grid_g = _values(spec["locals"]), _values(spec["globals"])
    grid = set((l, g) for l in locs for g in grid_g)
    declared_g = spec["prior_global"]
    # The Global values are those P(Global) names (V2.3): a value it leaves out is not in Omega,
    # as a state the prior leaves out is not (SURFACE v0 K10). A zero cell is refused (V2.2).
    strangers = [g for g in declared_g if g not in grid_g]
    if not declared_g or strangers:
        raise Refused(PRIOR, "P(Global) is over Global values of the space")
    for g, p in declared_g.items():
        if p <= 0:
            raise Refused(PRIOR, "a Global value of prior zero is not in Omega: " + repr(g))
    pg = dict(Dist(declared_g, PRIOR).items())
    if set(spec["prior_local"]) != set(pg):
        raise Refused(PRIOR, "P(local | Global) has a row for exactly the Global values P(Global) names")
    pl, joint = {}, {}
    for g in pg:
        row = spec["prior_local"][g]
        if any(l not in locs for l in row):
            raise Refused(PRIOR, "P(local | " + repr(g) + ") is not over the locals")
        row = Dist(row, PRIOR)
        pl[g] = {}
        for l in locs:
            if row.at(l) > 0:
                pl[g][(l, g)] = row.at(l)
                joint[(l, g)] = pg[g] * row.at(l)
    omega = list(joint)

    def over(table, what, refusal=TABLE_SHAPE):
        missing = [state for state in omega if state not in table]
        if missing or any(state not in grid for state in table):
            raise Refused(refusal, what + " is not a table over Omega's states")
        return {state: table[state] for state in omega}

    def ending_utility(u, what):
        # laws/model.py: an ending utility is a per-state table; kit v0.11's probes write a number
        if isinstance(u, dict):
            return over(u, what)
        return {state: Fraction(u) for state in omega}

    T = {t: over(u, "the utility of " + repr(t)) for t, u in spec["T"].items()}
    O = {}
    for name, s in spec["O"].items():
        u_end = s.get("u_end", {})
        ends = set(s.get("ends", ())) | set(u_end)
        if any(o not in u_end for o in ends):
            raise Refused(TABLE_SHAPE, "an ending outcome of " + repr(name) + " has no ending utility")
        O[name] = {"K": over(s["K"], "the kernel of " + repr(name)), "price": s["price"],
                   "once": s["once"],
                   "ends": {o: ending_utility(u_end[o], "the ending utility of " + repr(o)) for o in ends}}

    after = None
    if spec.get("after") is not None:
        a = spec["after"]
        name = a.get("name", "after")
        if name in spec["O"]:
            raise Refused(AFTER, "the After-act is named as an observational act, which the door"
                          + " answers by the same name: " + repr(name))
        want = set(spec["T"]) | set(ending(k, o) for k, s in O.items() for o in s["ends"])
        if set(a["K"]) != want:
            raise Refused(AFTER, "the After-act declares a kernel for every end, and only for the ends")
        if Fraction(a["price"]) < 0:
            raise Refused(PRICE, "the After-act is paid to be taken: Price's domain is O and the"
                          + " After-act, and a price is never negative (QUESTIONS.md Q10)")
        after = After(name, Fraction(a["price"]),
                      {e: Kernel(over(K, "the After-act's kernel at " + repr(e), AFTER)) for e, K in a["K"].items()})

    inner = {key: spec[key] for key in ("N", "d", "table_sources", "sources", "components", "dplus",
                                        "fraction", "rate", "ops") if key in spec}
    inner.update(prior=joint, T=T, O=O, closed=True)
    bottom = spec.get("bottom")
    if bottom is None and not spec.get("closed", False):
        raise Refused(ZERO_EVIDENCE, "neither `closed` nor a catch-all local")
    world = build_v0(inner, floor, sourced="table_sources" in spec)
    if bottom is not None:
        # v0 S5 with a catch-all local: every (bottom, g) is in Omega, and every kernel that mints a
        # report the World must absorb -- the menu's and the After-act's -- gives it all mass there.
        for g in pg:
            state = (_local(bottom), g)
            if state not in joint:
                raise Refused(ZERO_EVIDENCE, "the catch-all local has no mass under " + repr(g))
            for name, act in world.O.items():
                if any(act.kernel.at(state, o) <= 0 for o in act.kernel.outcomes()):
                    raise Refused(ZERO_EVIDENCE, "the catch-all gives an outcome of " + repr(name) + " no mass")
            for e, K in (after.kernels.items() if after else ()):
                if any(K.at(state, o) <= 0 for o in K.outcomes()):
                    raise Refused(AFTER, "the catch-all gives an after-report under " + repr(e) + " no mass"
                                  + " (S12; QUESTIONS.md Q10)")

    ships = spec.get("counts") is not None or bool(spec.get("falsifiers"))
    return Plated(world, pg, pl, after, Counter(spec.get("counts") or {}),
                  tuple(spec.get("falsifiers") or ()), spec.get("score"), ships, bool(spec["globals"]))


def _unpaid(table, locs, globs, what):
    """S11 is one of form: at each local, the table says one thing whatever the Global."""
    for l in locs:
        if len(set(table[(l, g)] for g in globs if (l, g) in table)) > 1:
            raise Refused(GLOBAL, what + " reads a Global (S11)")


def declare(spec):
    """Accept a v0.2 declaration, or refuse it by the name of the clause it breaks."""
    from . import counts as C
    from .canonical import digest
    from .world import _rulings

    plated = build(spec)
    locs, globs = _values(spec["locals"]), list(plated.pg)
    for t, u in spec["T"].items():
        _unpaid(u, locs, globs, "the utility of " + repr(t))
    for k, s in spec["O"].items():
        for o, u in s.get("u_end", {}).items():
            if isinstance(u, dict):
                _unpaid(u, locs, globs, "the ending utility of " + repr(o) + " of " + repr(k))
    _rulings(plated.world)
    if plated.ships:
        if spec.get("counts_sha") != digest(plated.counts, plated.falsifiers):
            raise Refused(PLATE, "the Counts and falsifying records do not hash to their declared"
                          + " digest (S13, SURFACE v0.2 V2.13)")
        if not C.expressible(plated, plated.counts, plated.falsifiers):
            raise Refused(PLATE, "no episode of this declaration could have written these records,"
                          + " or no Global value all of them together (S13, V2.7)")
        if plated.score != C.score(plated, plated.counts, plated.falsifiers):
            raise Refused(UNSCORED, "the shipped Score is not the leave-one-out predictive"
                          + " probability of every record and falsifying record (S14, V2.8)")
    return plated
