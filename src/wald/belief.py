"""The sealed Belief and the verbs of section 2 that may touch it. A belief is introduced only
from a World's Prior and changed only by `condition`; its weights leave it only as a predictive
mass (`push`), an expectation (`expect`) or text (`report`)."""
from fractions import Fraction

from .display import render
from .obs import check_unspent, spend
from .refusals import WorldFalsified

_SEAL = object()


class Belief:
    """Sealed. No public name on it, nothing to set, and no way to make one from outside."""

    __slots__ = ("_w",)

    def __init__(self, weights=None, seal=None):
        if seal is not _SEAL:
            raise TypeError("a Belief is introduced from the Prior and changed only by `condition`")
        object.__setattr__(self, "_w", weights)

    def __setattr__(self, name, value):
        raise AttributeError("a belief changes only by `condition`")

    def __delattr__(self, name):
        raise AttributeError("a belief changes only by `condition`")

    def __repr__(self):
        return "<Belief over " + str(len(self._w)) + " states>"


def _sealed(weights):
    return Belief(weights, _SEAL)


def _weights(belief):
    """Package-private. The seal is against hosts and packs, not against the kernel itself."""
    return belief._w


def prior(world):
    """b <- P0. The only way a belief comes into being."""
    return _sealed({state: p for state, p in world.prior.items()})


def push(belief, kernel):
    """P_b(o|k) = sum_w b(w) K_k(o|w)."""
    out = {}
    for state, p in belief._w.items():
        for o, q in kernel.row(state).items():
            out[o] = out.get(o, Fraction(0)) + p * q
    return out


def expect(belief, f):
    """E_b[f] = sum_w b(w) f(w)."""
    return sum((p * f[state] for state, p in belief._w.items()), Fraction(0))


def _update(belief, kernel, value):
    """(b|k,o)(w) = b(w) K_k(o|w) / P_b(o|k). The belief update of section 2, which exists once:
    the verb below is this plus the token, and nothing else in the kernel updates a belief."""
    w = belief._w
    z = sum((p * kernel.at(state, value) for state, p in w.items()), Fraction(0))
    if z == 0:
        raise WorldFalsified("the World gives " + repr(value) + " no mass under this belief")
    return _sealed({state: p * kernel.at(state, value) / z for state, p in w.items()})


def condition(belief, world, obs):
    """b <- b|k,o, spending the token. A token that falsifies the World is not consumed: the
    episode ends before anything is done with it (S5), so only a surviving Obs is spent (S2)."""
    check_unspent(obs)
    posterior = _update(belief, world.O[obs.act].kernel, obs.value)
    spend(obs)
    return posterior


def report(belief):
    """Render a belief for display. What comes back has no operations (S1)."""
    return render(", ".join(str(state) + " " + str(p) for state, p in belief._w.items()))
