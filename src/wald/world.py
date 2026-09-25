"""The World: the whole declaration of section 1, and every validation that refuses it by name.
Nothing runs until `declare` has accepted the pack."""
from fractions import Fraction

from .dist import Dist
from .kernels import Kernel
from .same import Sameness
from .refusals import (COST, DEPTH, DEPTH_PLUS, EMPTY_T, FRACTION, KERNEL_ROW, PRICE, PRIOR,
                       RATE, SHARED_SOURCE, TABLE_SHAPE, TABLE_SOURCE, UNSCORED, ZERO_EVIDENCE,
                       Refused)

TAGS = ("data", "elicited", "fitted")
OWNED = ("elicited", "fitted")
TABLES = ("prior", "utility", "price", "horizon", "depth")


class Act:
    """An observational act: its kernel, its price, whether it is `once`, and its ending outcomes."""

    __slots__ = ("name", "kernel", "price", "once", "ends", "sources")

    def __init__(self, name, kernel, price, once, ends, sources):
        self.name = name
        self.kernel = kernel
        self.price = price
        self.once = once
        self.ends = ends
        self.sources = sources


class World:
    """The declaration: Omega through its Prior, the menu M as T then O, and the clock."""

    __slots__ = ("prior", "T", "O", "N", "d", "closed", "bottom", "table_sources", "components",
                 "dplus", "fraction", "rate", "ops", "score", "_work")

    def __init__(self, prior, T, O, N, d, closed, bottom, table_sources, components, meta):
        self._work = None
        self.prior = prior
        self.T = T
        self.O = O
        self.N = N
        self.d = d
        self.closed = closed
        self.bottom = bottom
        self.table_sources = table_sources
        self.components = components
        # CHARTER v0.1 section 1: the think act's five tables. A World that declares no Depth+
        # is a v0 World -- `dplus` is None, and then nothing reads the other four.
        self.dplus, self.fraction, self.rate, self.ops, self.score = meta

    def omega(self):
        return tuple(self.prior.carrier())

    def work(self):
        """What the lookahead may work out once and keep: which acts are copies of which, and
        the values already found. Both are facts about a World, and a World does not change once
        it is declared, so they are built on its first decision and then belong to it."""
        if self._work is None:
            self._work = (Sameness(self), {})
        return self._work

    def menu(self, used):
        """M without the `once` acts already executed. T is not here: it never leaves."""
        return [name for name, act in self.O.items() if not (act.once and name in used)]


def _total(table, omega, what):
    """A table over Omega is a function on Omega: defined at every state, and at nothing else.
    A gap is a state the pack forgot; a stranger is a state that is not in the small world."""
    missing = [state for state in omega if state not in table]
    strangers = [state for state in table if state not in omega]
    if missing:
        raise Refused(TABLE_SHAPE, what + " says nothing at " + ", ".join(repr(s) for s in missing))
    if strangers:
        raise Refused(TABLE_SHAPE, what + " speaks of " + ", ".join(repr(s) for s in strangers)
                      + ", which is not in Omega")


def build(spec, floor=True, sourced=True):
    """The World of section 1, out of a spec: the conversion, and the refusals that are the
    conversion itself -- a prior that is not one, a row that does not sum to 1, a table that is
    not a function on Omega.

    `declare` is this plus the rulings a pack must satisfy. The kit's shim stops here, because a
    kit World dict is a probe and not a pack: C19 of CHARTER v0.1 hands the kernel a d+ that J11
    refuses in a pack, to prove that the cap does not read d+. For the same reason a probe may pass
    `floor=False`: kit v0.11's levels World has N = 0 and d = 1, where every decision is V_0
    whatever d says. A pack never can -- `declare` rules on the floor, in its place in this list.

    `sourced=False` is CHARTER v0.2's dict as SURFACE v0.2 elaborates a pack to it (laws/model.py):
    it carries no sources, because the surface has already judged every one, so none is asked for
    and none is ruled on. Every other rule stands."""
    T = spec["T"]
    if not T:
        raise Refused(EMPTY_T, "a World with nothing to do")

    prior_spec = spec["prior"]
    if not prior_spec:
        raise Refused(PRIOR, "Omega is empty")
    for state, p in prior_spec.items():
        if p <= 0:
            raise Refused(PRIOR, "a state of prior zero is not in Omega: " + repr(state))
    prior = Dist(prior_spec, PRIOR)
    omega = prior.carrier()

    for t_name, u in T.items():
        _total(u, omega, "the utility of terminal act " + repr(t_name))

    acts = {}
    declared_sources = spec.get("sources", {})
    for name, s in spec["O"].items():
        kernel = Kernel(s["K"], KERNEL_ROW)
        _total(kernel.states(), omega, "the kernel of " + repr(name))
        price = Fraction(s["price"])
        if price < 0:
            raise Refused(PRICE, "act " + repr(name) + " is paid to be looked at")
        for o, u_end in s["ends"].items():
            if o not in kernel.outcomes():
                raise Refused(TABLE_SHAPE, "the ending outcome " + repr(o) + " is not in B_k, so the kernel"
                              + " of " + repr(name) + " cannot emit it")
            _total(u_end, omega, "the u_end of " + repr(o) + " of " + repr(name))
        sources = tuple(declared_sources.get(name, ()))
        acts[name] = Act(name, kernel, price, bool(s["once"]), dict(s["ends"]), sources)

    N, d = spec["N"], spec["d"]
    if floor and not 1 <= d <= N:
        raise Refused(DEPTH, "d = " + str(d) + " with N = " + str(N))

    closed = bool(spec.get("closed", False))
    bottom = spec.get("bottom", None)
    if not closed:
        if bottom is None:
            raise Refused(ZERO_EVIDENCE, "neither `closed` nor a catch-all state")
        if bottom not in prior_spec:
            raise Refused(ZERO_EVIDENCE, "the catch-all state is not in Omega: " + repr(bottom))
        for name, act in acts.items():
            for o in act.kernel.outcomes():
                if act.kernel.at(bottom, o) <= 0:
                    raise Refused(ZERO_EVIDENCE,
                                  "the catch-all state gives " + repr(o) + " of " + repr(name) + " no mass")

    table_sources = spec.get("table_sources", None)
    if sourced:
        if table_sources is None:
            raise Refused(TABLE_SOURCE, "no table names its source")
        for table in TABLES:
            if table_sources.get(table, None) not in TAGS:
                raise Refused(TABLE_SOURCE, "the " + table + " table names no source in " + str(TAGS))
        kernel_sources = table_sources.get("kernels", {})
        for name in acts:
            tags = kernel_sources.get(name, None)
            # A kernel draws on every table inside it, so it names a list of sources -- empty when
            # it holds no number at all, as `point` does.
            if not isinstance(tags, (list, tuple)) or any(tag not in TAGS for tag in tags):
                raise Refused(TABLE_SOURCE, "the kernel of " + repr(name)
                              + " names no list of sources in " + str(TAGS))

    components = frozenset(spec.get("components", ()))
    read_by = {}
    for name, act in acts.items():
        for source in act.sources:
            if source in components:
                continue
            if source in read_by:
                raise Refused(SHARED_SOURCE, repr(read_by[source]) + " and " + repr(name) + " both read "
                              + repr(source) + ", which is not a component of Omega")
            read_by[source] = name
            if not act.once:
                raise Refused(SHARED_SOURCE, repr(name) + " is `fresh` and reads " + repr(source)
                              + " at every execution, and it is not a component of Omega")

    meta = (spec.get("dplus", None), spec.get("fraction", None), spec.get("rate", None),
            dict(spec.get("ops", None) or {}), dict(spec.get("score", None) or {}))
    return World(prior, dict(T), acts, N, d, closed, bottom,
                 dict(table_sources) if sourced else None, components, meta)


def _rulings(world):
    """CHARTER v0.1's tables, refused by name. A World that declares no Depth+ is a v0 World:
    it reads none of them, and none of these names can speak to it."""
    if world.dplus is None:
        return
    # A World built unsourced (CHARTER v0.2's dict, `build`) has had its sources judged by the
    # surface; the ranges below are still the World's to rule on.
    sources = world.table_sources
    sourced = sources is not None
    sources = sources or {}
    if world.fraction is None or not 0 <= world.fraction <= 1:
        raise Refused(FRACTION, "f = " + str(world.fraction) + " is not a share of the room (S6)")
    if sourced and sources.get("fraction", None) not in OWNED:
        raise Refused(FRACTION, "the Fraction is a meta-belief, so it is `elicited` or `fitted`")
    states = len(world.prior.carrier())
    if set(world.ops) != set(range(1, states + 1)):
        raise Refused(COST, "the Cost says nothing at some s in 1.." + str(states)
                      + ": it is a cell for each count of live states")
    if any(cell < 0 for cell in world.ops.values()):
        raise Refused(COST, "a thought that takes fewer than no operations")
    if sourced and sources.get("cost", None) not in OWNED:
        raise Refused(COST, "the Cost is a meta-belief, so it is `elicited` or `fitted`")
    if sourced and sources.get("rate", None) != "elicited":
        raise Refused(RATE, "the Rate is the owner's exchange rate, so it is `elicited`")
    # CHARTER v0.1 section 1 forbids a Rate below zero and names no clause for it (QUESTIONS.md
    # Q4). The author has now answered: ERRATA queues RATE for CHARTER v0.2 and SURFACE v0.1 K15
    # supplies it meanwhile, under the name the Rate's own row already uses.
    if world.rate is None or world.rate < 0:
        raise Refused(RATE, "the owner is paid to think: r = " + str(world.rate))
    if sourced and sources.get("dplus", None) != "elicited":
        raise Refused(TABLE_SOURCE, "Depth+ is the owner's, fixed by J11, so it is `elicited`"
                      + " (SURFACE v0.1 K18)")
    if not (world.d == 1 and world.dplus == 2 and world.N >= 2):
        raise Refused(DEPTH_PLUS, "a World with a think act declares d = 1, d+ = 2 and N >= 2 (J11),"
                      + " not d = " + str(world.d) + ", d+ = " + str(world.dplus)
                      + ", N = " + str(world.N))
    unscored = sorted(table for table in ("fraction", "cost")
                      if sources.get(table, None) == "fitted" and table not in world.score)
    if unscored:
        raise Refused(UNSCORED, "the fitted " + unscored[0] + " is fenced, and carries its"
                      + " held-out Score (J18, SURFACE v0.1 K14)")


def declare(spec):
    """Accept a pack, or refuse it by the name of the clause it breaks. A dict that declares
    `globals` is one of CHARTER v0.2 (`plated.py`); one that does not is a v0.1 World, as before."""
    if "globals" in spec:
        from .plated import declare as declare_plated
        return declare_plated(spec)
    world = build(spec)
    _rulings(world)
    return world
