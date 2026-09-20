"""The shim of laws/INTERFACE.md: plain dicts in, the kernel's own types out. It converts and
calls. It does not choose, update or compute anything of its own (E5).

The kit's World dict declares no clock, no S5 stance and no sources, because the kit keeps the
floor to itself (it passes n = min(d,n) when it tests one) and never declares a pack. So the
conversion supplies the three: the shortest lawful clock, `closed` -- which is what the kit's S5
check asks for -- and no named sources, i.e. the default private source per act. None of the
three is visible to the kit, and `decide` reads none of them: it is given its n."""
from . import belief as B
from .decide import decide
from .kernels import Kernel
from .world import declare

_TAGS = {"prior": "data", "utility": "data", "price": "data", "horizon": "data", "depth": "data"}


def _world(spec):
    return declare({"prior": spec["prior"], "T": spec["T"], "O": spec["O"],
                    "N": 1, "d": 1, "closed": True,
                    "table_sources": dict(_TAGS, kernels={k: ["data"] for k in spec["O"]})})


class _Agent:
    """The four methods of INTERFACE.md, each one line of conversion around one kernel call."""

    def push(self, b, K):
        return B.push(B._sealed(dict(b)), Kernel(K))

    def condition(self, b, K, o):
        return dict(B._weights(B._update(B._sealed(dict(b)), Kernel(K), o)))

    def expect(self, b, f):
        return B.expect(B._sealed(dict(b)), f)

    def decide(self, b, world, n, used=frozenset()):
        return decide(B._sealed(dict(b)), _world(world), n, frozenset(used))


def make_agent():
    return _Agent()
