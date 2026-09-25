"""The shim of laws/INTERFACE.md: plain dicts in, the kernel's own types out. It converts and
calls. It does not choose, update or compute anything of its own (E5).

The kit's World dict declares no S5 stance and no sources, and often no clock, because the kit
keeps the floor to itself for `decide` (it passes n = min(d,n) when it tests one) and never
declares a pack. So the conversion supplies them: the shortest lawful clock the dict allows,
`closed` -- which is what the kit's S5 check asks for -- and no named sources, i.e. the default
private source per act.

It converts rather than declares, and that is deliberate: a kit World dict is a probe, not a
pack. C19 of CHARTER v0.1 hands the kernel a World whose d+ is N, which J11 refuses in a pack, to
prove that the cap does not read d+ -- so the shim stops at `build`, section 1's conversion, and
the refusals by name are judged where they belong, on `declare` itself.
"""
from collections import Counter

from . import belief as B
from . import counts as C
from . import disclose as D
from . import plated as P
from .decide import decide, step
from .canonical import digest
from .kernels import Kernel
from .world import build

_TAGS = {"prior": "data", "utility": "data", "price": "data", "horizon": "data", "depth": "data"}
_META = {"fraction": "elicited", "cost": "elicited", "rate": "elicited"}


def _on(table, prior):
    return {state: table[state] for state in prior}


def _world(spec):
    """The tables are read at the prior's states only: kit v0.11 builds an episode's World over the
    whole product of locals and Globals and hands it a prior that leaves some of them out of Omega,
    and what a table says there is read by nothing."""
    d = spec.get("d", 1)
    sources = dict(_TAGS, kernels={k: ["data"] for k in spec["O"]})
    prior = spec["prior"]
    T = {t: _on(u, prior) for t, u in spec["T"].items()}
    O = {k: dict(s, K=_on(s["K"], prior), ends={o: _on(u, prior) for o, u in s["ends"].items()})
         for k, s in spec["O"].items()}
    out = {"prior": prior, "T": T, "O": O,
           "N": spec.get("N", d), "d": d, "closed": True, "table_sources": sources}
    if "dplus" in spec:
        # The meta-tables, as the dict gives them. Their sources are the kit's, not a pack's:
        # a meta-belief is the owner's opinion, so `elicited` is the only tag that can be right.
        sources.update(_META)
        for key in ("dplus", "fraction", "rate", "ops"):
            out[key] = spec[key]
    return build(out, floor=False)


def _spec(W):
    """A kit v0.11 dict with what a pack would add: `closed`, and the kit's sources."""
    sources = dict(_TAGS, kernels={k: ["data"] for k in W["O"]})
    if "dplus" in W:
        sources.update(_META, dplus="elicited")
    return dict(W, closed=True, table_sources=sources)


def _plated(W):
    return P.build(_spec(W), floor=False)


class _Agent:
    """The thirteen methods of INTERFACE.md, each one line of conversion around one kernel call."""

    def push(self, b, K):
        return B.push(B._sealed(dict(b)), Kernel(K))

    def condition(self, b, K, o):
        return dict(B._weights(B._update(B._sealed(dict(b)), Kernel(K), o)))

    def expect(self, b, f):
        return B.expect(B._sealed(dict(b)), f)

    def decide(self, b, world, n, used=frozenset()):
        # A dict that carries its floor d is played as the episode plays it: decide equals
        # step(...)[0] (INTERFACE, kit v0.7), and step is where min(d, n) is applied. A v0 dict
        # carries none, and the kit floors n itself: decide_n.
        if "d" in world:
            return self.step(b, world, n, used)[0]
        return decide(B._sealed(dict(b)), _world(world), n, frozenset(used))

    def step(self, b, world, n, used=frozenset()):
        return step(B._sealed(dict(b)), _world(world), n, frozenset(used))

    # CHARTER v0.2 (kit v0.11). A v0.2 dict is a probe too: `world` and the readers stop at
    # `plated.build`; `declare` is the one that rules.
    def prior(self, W, records):
        return dict(B._weights(C.episode_prior(_plated(W), Counter(records))))

    def persist(self, records):
        return C.tally(records)

    def declare(self, W):
        return P.declare(_spec(W))

    def disclose(self, W):
        return D.shown(_plated(W))[1]

    def e7(self, W, counts):
        return {(h, "<after>" if end is not None else k, end): v
                for (h, k, end), v in C.e7(_plated(W), Counter(counts)).items()}

    def score(self, W, counts, falsifiers=()):
        return C.score(_plated(W), Counter(counts), tuple(falsifiers))

    def digest(self, counts, falsifiers=()):
        return digest(Counter(counts), tuple(falsifiers))

    def world(self, W):
        return _plated(W)


def make_agent():
    return _Agent()
