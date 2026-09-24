"""The plate of CHARTER v0.2: every episode run under one declaration, and the Counts they write.
A Plate holds its Counts and, once falsified, its falsifying record -- nothing else: no log, no
belief, no cache with a meaning (S13).

One episode is the prior from the Counts, v0's loop at the floor unchanged, the terminal fired,
then -- if an After-act is declared -- its report, asked of the door by name after the fire and
taken whenever declared (S12, J27). `decide` never sees the After-act. The record enters the
Counts. A report of probability zero, in the episode or after it, ends the plate (J26)."""
from collections import Counter

from . import counts as C
from . import disclose
from .belief import _condition
from .episode import WORLD_FALSIFIED, Result, _play
from .plated import Plated, wrap
from .refusals import WorldFalsified


class Plate:
    """A plate over one declaration. Its Counts are facts, so a host may hold them (S1)."""

    __slots__ = ("_plated", "_counts", "_falsifier")

    def __init__(self, plated):
        self._plated = plated
        self._counts = Counter(plated.counts)
        self._falsifier = None

    def run(self, door):
        """One episode. Refused, as WorldFalsified, once the plate has ended."""
        if self._falsifier is not None:
            raise WorldFalsified("this plate ended WORLD_FALSIFIED; its Counts stand and it runs no more")
        plated = self._plated
        evidence = self._counts + (Counter([plated.falsifier]) if plated.falsifier else Counter())
        r = _play(plated.world, C.episode_prior(plated, evidence), door)
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
        """The record that falsified this plate, or None."""
        return self._falsifier

    def disclosure(self):
        """S15's disclosure, as inert text (S1)."""
        return disclose.disclosure(self._plated)


def plate(world):
    """A new plate over a declared World: one of CHARTER v0.2, or a v0 World, which plays as v0.1
    save that a falsifying report ends the plate (C21)."""
    return Plate(world if isinstance(world, Plated) else wrap(world))
