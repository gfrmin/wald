"""The sealed Belief and the verbs of section 2 that may touch it. A belief is introduced only
from a World's Prior and changed only by `condition`; its weights leave it only as a predictive
mass (`push`), an expectation (`expect`) or text (`report`).

Underneath those three verbs, and replacing them and nothing else, is E2's fast path: the same
mass unnormalised. `_split` is `push` and `condition` in one pass, with the division left out
because the lookahead multiplies it straight back in; `_dot` is expectation over what comes out.
The belief a host or an episode holds is still normalised, and still changes only by `condition`.

The operations counted here are the operations of CHARTER v0.1 E6: one for each arithmetic
operation on Q that `push`, `condition` and expectation perform in the evaluator that runs. In
this evaluator those three are `_split`, `_dot` and `_mass`, so every multiplication and addition
those three do is counted, and no thought passes through the public `push` and `expect` at all.
The count is a scoreboard measurement -- `decide` zeroes it as a thought begins and never reads
it; `episode.run` reads it when the thought is done. It is not a clock and it is in no value.
"""
from fractions import Fraction

from .display import render
from .obs import check_unspent, spend
from .refusals import WorldFalsified

_SEAL = object()

_OPS = 0


def _count_reset():
    """E6: the thought starts here. `decide` calls this and reads nothing."""
    global _OPS
    _OPS = 0


def _counted():
    """The operations since the count was zeroed. Read by the episode and by `report`, and by
    nothing that decides anything."""
    return _OPS


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
    the verb below is this plus the token, and nothing else in the kernel updates a belief.
    A state of mass zero is left out of what comes back: it weighed nothing in the sum above, and
    it will weigh nothing in any sum after it, because no conditioning can revive it."""
    w = belief._w
    z = sum((p * kernel.at(state, value) for state, p in w.items()), Fraction(0))
    if z == 0:
        raise WorldFalsified("the World gives " + repr(value) + " no mass under this belief")
    posterior = {}
    for state, p in w.items():
        q = p * kernel.at(state, value)
        if q:
            posterior[state] = q / z
    return _sealed(posterior)


def _measure(belief):
    """E2's belief: the same mass, without the states that carry none of it."""
    return {state: p for state, p in belief._w.items() if p}


def _tally(done):
    """One integer add per call, not per operation: counting must not be dearer than the
    arithmetic it counts."""
    global _OPS
    _OPS += done


def _split(measure, rows):
    """`push` and `condition` in one pass, unnormalised: for every outcome of positive mass, the
    mass m(w) K_k(o|w) over the states that can emit it.

    Dividing each part by its own total would give P_b(o|k) and the posterior b|k,o. The value of
    the branch is P_b(o|k) V(b|k,o), which multiplies that total straight back in, so the division
    is written down and taken away again in the same line: it is not done. Nothing is dropped but
    a zero, and a zero is not a number the page ever adds."""
    parts = {}
    done = 0
    for state, p in measure.items():
        for o, q in rows[state].items():
            if not q:
                continue
            part = parts.get(o)
            if part is None:
                part = parts[o] = {}
            # m(w) K(o|w). Not multiplying by one is arithmetic, not a special case for a
            # kernel that happens to be deterministic: it is the same number either way -- and
            # an operation not performed is an operation not counted (E6).
            if q == 1:
                part[state] = p
            else:
                part[state] = p * q
                done += 1
    _tally(done)
    return parts


def _dot(measure, f):
    """sum_w m(w) f(w). Expectation when the mass is one, and what stands in its place when it
    is not: mass(m) E_{m/mass(m)}[f]."""
    _tally(2 * len(measure))                      # one product and one sum per state (E6)
    return sum([p * f[state] for state, p in measure.items()], Fraction(0))


def _mass(measure):
    """sum_w m(w). Needed only where a price is paid, so it is asked for and not carried."""
    _tally(len(measure))
    return sum(measure.values(), Fraction(0))


def condition(belief, world, obs):
    """b <- b|k,o, spending the token. A token that falsifies the World is not consumed: the
    episode ends before anything is done with it (S5), so only a surviving Obs is spent (S2)."""
    check_unspent(obs)
    posterior = _update(belief, world.O[obs.act].kernel, obs.value)
    spend(obs)
    return posterior


def report(belief, world=None):
    """Render a belief for display. What comes back has no operations (S1).

    Given the World as well, it renders what the World predicted a thought about this belief would
    cost and what the last one actually took (E6): a measurement printed side by side, never a
    number any verb reads."""
    text = ", ".join(str(state) + " " + str(p) for state, p in belief._w.items())
    if world is not None and world.dplus is not None:
        live = len(_measure(belief))
        text += (" | " + str(live) + " live: " + str(world.ops[live]) + " operations predicted, "
                 + str(_counted()) + " counted")
    return render(text)
