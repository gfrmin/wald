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
from . import belief as B
from .decide import decide, step
from .kernels import Kernel
from .world import build

_TAGS = {"prior": "data", "utility": "data", "price": "data", "horizon": "data", "depth": "data"}
_META = {"fraction": "elicited", "cost": "elicited", "rate": "elicited"}


def _world(spec):
    d = spec.get("d", 1)
    sources = dict(_TAGS, kernels={k: ["data"] for k in spec["O"]})
    out = {"prior": spec["prior"], "T": spec["T"], "O": spec["O"],
           "N": spec.get("N", d), "d": d, "closed": True, "table_sources": sources}
    if "dplus" in spec:
        # The meta-tables, as the dict gives them. Their sources are the kit's, not a pack's:
        # a meta-belief is the owner's opinion, so `elicited` is the only tag that can be right.
        sources.update(_META)
        for key in ("dplus", "fraction", "rate", "ops"):
            out[key] = spec[key]
    return build(out)


class _Agent:
    """The five methods of INTERFACE.md, each one line of conversion around one kernel call."""

    def push(self, b, K):
        return B.push(B._sealed(dict(b)), Kernel(K))

    def condition(self, b, K, o):
        return dict(B._weights(B._update(B._sealed(dict(b)), Kernel(K), o)))

    def expect(self, b, f):
        return B.expect(B._sealed(dict(b)), f)

    def decide(self, b, world, n, used=frozenset()):
        return decide(B._sealed(dict(b)), _world(world), n, frozenset(used))

    def step(self, b, world, n, used=frozenset()):
        return step(B._sealed(dict(b)), _world(world), n, frozenset(used))


def make_agent():
    return _Agent()
