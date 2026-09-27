"""What a host needs to write the pack that ships its Counts, with `wald` alone (kit v0.13).

A host that plays a plate holds its Counts and its falsifying record (`Plate.counts`,
`Plate.falsifier`): facts, which S1 lets it hold. To ship them it writes `counts(...)`,
`falsifiers(...)`, the digest and the Score. The digest is a name and the Score a measurement a
pack writes as a cell; neither is a belief a host acts on, and the Score is text here, as the
pack writes it, not a number a host could compare. E7's lines are shown, as `report` shows a
belief (S1)."""
from collections import Counter

from . import canonical
from . import counts as C
from .digits import rational
from .display import render
from .plated import Plated, wrap


def _plated(world):
    return world if isinstance(world, Plated) else wrap(world)


def digest(counts, falsifiers=()):
    """SURFACE v0.2 V2.13's digest of the Counts and falsifying records: lowercase hex."""
    return canonical.digest(Counter(counts), tuple(falsifiers))


def score(world, counts, falsifiers=()):
    """V2.8's Score of these Counts and falsifying records under `world`, as `wald.declare`
    returns it, written as a pack writes the cell: "p/q", or "p" when q is 1, in decimal
    digits however many."""
    return rational(C.score(_plated(world), Counter(counts), tuple(falsifiers)))


def e7(world, counts):
    """E7's lines for these Counts, as inert text: for every draw, grouped by the history within
    its episode that led to it, the total variation between the empirical law of its outcome
    and its posterior predictive, an exact rational."""
    plated = _plated(world)
    lines = C.e7(plated, Counter(counts))
    text = ["E7: total variation between each draw's outcomes in Counts and its posterior"
            " predictive, by the history that led to it"]
    for key in sorted(lines, key=lambda key: (len(key[0]), repr(key))):
        history, act, end = key
        before = "; ".join(str(k) + "=" + str(o) for k, o in history) or "the start"
        after = ", then " + str(end) if end is not None else ""
        text.append("after " + before + after + ": " + str(act) + " " + rational(lines[key]))
    return render("\n".join(text))
