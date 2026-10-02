"""The plate of CHARTER v0.2: every episode run under one declaration, and the Counts they write.
A Plate holds its Counts and, once falsified, its falsifying record -- nothing else: no log, no
belief, no cache with a meaning (S13).

One episode is the prior from the Counts, v0's loop at the floor unchanged, the terminal fired,
then -- if an After-act is declared -- its report, asked of the door by name after the fire and
taken whenever declared (S12, J27). `decide` never sees the After-act. The record enters the
Counts. A report of probability zero, in the episode or after it, ends the plate (J26)."""
import json
from collections import Counter

from . import counts as C
from . import disclose
from .belief import _condition
from .decide import quantities
from .digits import rational
from .display import render
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
        plated = self._plated
        r = _play(plated.world, self._prior(), door)
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

    def _prior(self):
        """The belief the next episode starts from. It conditions on the Counts and on every
        falsifying record shipped with them (J26); once the plate is falsified there is none."""
        if self._falsifier is not None:
            raise WorldFalsified("this plate ended WORLD_FALSIFIED; its Counts stand and it runs no more")
        plated = self._plated
        return C.episode_prior(plated, self._counts + Counter(plated.falsifiers))

    def prior(self):
        """The belief `run` would start the next episode from, sealed (kit v0.14). A host may
        `report` it, over any components it names, and do nothing else with it (S1)."""
        return self._prior()

    def values(self):
        """CHARTER v0 section 2's quantities at `prior()`, as inert text (kit v0.14): what the
        next episode's first decision at the floor weighs, and the act it takes, one line each:
        `n`; `V_0`; `T <name> <E_b[u]>`; `O <name> <Q_n> <Q_n - V_0>`; `V_n <V_n> <decide_n>`. The
        last line names an act and fires nothing: only `run` fires, through the door. θ is not
        run here, so in a World with a think act the episode may play the deeper look's act."""
        n, v0, T, O, vn, act = quantities(self._prior(), self._plated.world)
        lines = ["n " + str(n), "V_0 " + rational(v0)]
        lines += ["T " + _name(t) + " " + rational(v) for t, v in T]
        lines += ["O " + _name(k) + " " + rational(v) + " " + rational(v - v0) for k, v in O]
        lines.append("V_n " + rational(vn) + " " + _name(act))
        return render("\n".join(lines))

    def counts(self):
        return Counter(self._counts)

    def falsifier(self):
        """The record that falsified this plate, or None. The falsifying records it was shipped
        are its declaration's, and in the evidence of every episode's prior."""
        return self._falsifier

    def disclosure(self):
        """S15's disclosure, as inert text (S1)."""
        return disclose.disclosure(self._plated)


def _name(name):
    """A name as compact JSON, with V2.13's escapes: any name is written unambiguously."""
    return json.dumps(name, separators=(",", ":"), ensure_ascii=True)


def plate(world):
    """A new plate over a declared World: one of CHARTER v0.2, or a v0 World, which plays as v0.1
    save that a falsifying report ends the plate (C21)."""
    return Plate(world if isinstance(world, Plated) else wrap(world))
