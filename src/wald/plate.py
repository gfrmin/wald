"""The plate of CHARTER v0.2: every episode run under one declaration, and the Counts they write.
A Plate holds its Counts and, once falsified, its falsifying record -- and the values its
lookahead has found, which mean nothing: no act and no value changes if they are dropped. No log,
no belief, no cache with a meaning (S13).

Those values are kept only while the episodes' prior recurs. `_value` reads the World and the
belief, never the Counts, so a value found under one prior is the same value under it again; but
on a plate that learns no prior recurs, and every belief the lookahead reaches is new. So before an
episode whose prior differs from the last one's, what was found is dropped, and the kernel holds no
belief of a past episode once the next begins. Where the prior cannot move -- no Global, or records
that move none -- the values are kept for the plate's life, as `run` keeps the World's.

One episode is the prior from the Counts, v0's loop at the floor unchanged, the terminal fired,
then -- if an After-act is declared -- its report, asked of the door by name after the fire and
taken whenever declared (S12, J27). `decide` never sees the After-act. The record enters the
Counts. A report of probability zero, in the episode or after it, ends the plate (J26)."""
from collections import Counter

from . import counts as C
from . import disclose
from .belief import _condition, _measure
from .episode import WORLD_FALSIFIED, Result, _play
from .plated import Plated, wrap
from .refusals import WorldFalsified


class Plate:
    """A plate over one declaration. Its Counts are facts, so a host may hold them (S1)."""

    __slots__ = ("_plated", "_counts", "_falsifier", "_since", "_memo")

    def __init__(self, plated):
        self._plated = plated
        self._counts = Counter(plated.counts)
        self._falsifier = None
        self._since, self._memo = None, {}

    def _work(self, prior):
        """The values found under this prior: the last episode's, if its prior was this one, and
        none otherwise. The prior is held only to be compared with the next one; nothing reads it."""
        measure = _measure(prior)
        if measure != self._since:
            self._since, self._memo = measure, {}
        return self._memo

    def run(self, door):
        """One episode. Refused, as WorldFalsified, once the plate has ended."""
        if self._falsifier is not None:
            raise WorldFalsified("this plate ended WORLD_FALSIFIED; its Counts stand and it runs no more")
        plated = self._plated
        # The prior conditions on the Counts and on every falsifying record shipped with them (J26)
        evidence = self._counts + Counter(plated.falsifiers)
        prior = C.episode_prior(plated, evidence)
        r = _play(plated.world, prior, door, self._work(prior))
        if r.status == WORLD_FALSIFIED:
            self._falsifier = r.record
            return r
        draws, end, _ = r.record
        final, paid, record = r.final, r.paid, r.record
        if plated.after is not None:
            obs = door.observe(plated.after.name)
            paid += plated.after.price
            record = (draws, end, obs.value)
            try:
                final = _condition(final, plated.after.kernels[end], obs)
            except WorldFalsified:
                self._falsifier = record
                return Result(r.acts, r.outcomes, WORLD_FALSIFIED, paid, final, r.thought, r.steps,
                              r.operations, record)
        self._counts[record] += 1
        return Result(r.acts, r.outcomes, r.status, paid, final, r.thought, r.steps, r.operations, record)

    def counts(self):
        return Counter(self._counts)

    def falsifier(self):
        """The record that falsified this plate, or None. The falsifying records it was shipped
        are its declaration's, and in the evidence of every episode's prior."""
        return self._falsifier

    def disclosure(self):
        """S15's disclosure, as inert text (S1)."""
        return disclose.disclosure(self._plated)


def plate(world):
    """A new plate over a declared World: one of CHARTER v0.2, or a v0 World, which plays as v0.1
    save that a falsifying report ends the plate (C21)."""
    return Plate(world if isinstance(world, Plated) else wrap(world))
