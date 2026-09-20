"""The World: the whole declaration of section 1, and every validation that refuses it by name.
Nothing runs until `declare` has accepted the pack."""
from fractions import Fraction

from .dist import Dist
from .kernels import Kernel
from .refusals import (DEPTH, EMPTY_T, KERNEL_ROW, PRICE, PRIOR, SHARED_SOURCE, TABLE_SHAPE,
                       TABLE_SOURCE, ZERO_EVIDENCE, Refused)

TAGS = ("data", "elicited", "fitted")
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

    __slots__ = ("prior", "T", "O", "N", "d", "closed", "bottom", "table_sources", "components")

    def __init__(self, prior, T, O, N, d, closed, bottom, table_sources, components):
        self.prior = prior
        self.T = T
        self.O = O
        self.N = N
        self.d = d
        self.closed = closed
        self.bottom = bottom
        self.table_sources = table_sources
        self.components = components

    def omega(self):
        return tuple(self.prior.carrier())

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


def declare(spec):
    """Accept a pack, or refuse it by the name of the clause it breaks."""
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
    if not 1 <= d <= N:
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
    if table_sources is None:
        raise Refused(TABLE_SOURCE, "no table names its source")
    for table in TABLES:
        if table_sources.get(table, None) not in TAGS:
            raise Refused(TABLE_SOURCE, "the " + table + " table names no source in " + str(TAGS))
    kernel_sources = table_sources.get("kernels", {})
    for name in acts:
        if kernel_sources.get(name, None) not in TAGS:
            raise Refused(TABLE_SOURCE, "the kernel of " + repr(name) + " names no source in " + str(TAGS))

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

    return World(prior, dict(T), acts, N, d, closed, bottom, dict(table_sources), components)
