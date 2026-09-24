"""What persists between episodes, and what it is worth: CHARTER v0.2 sections 4 and 7.

The prior of an episode is P(Global | Counts) P(local | Global), and P(Global | Counts) is v0's
Bayes' theorem applied to each record: `belief._update`, the one update, with the record's
likelihood L(record | Global) raised to its count. The record is the unit, never the draw, because
the draws of one episode share its local, which L sums out. Nothing is fitted, nothing is
forgotten, and a multiset has no order (C22, C23).

Counts are facts, not beliefs: a multiset of records `((act, outcome), ...), end, after-report)`."""
import hashlib
import json
from collections import Counter
from fractions import Fraction

from .belief import _sealed, _update, _weights, expect, push
from .episode import ending
from .refusals import WorldFalsified


def tally(records):
    """The Counts of these records: all that persists, bounded by the distinct records (S13)."""
    return Counter(records)


def likelihood(plated, record, g):
    """L(record | g) = sum over the states of g of P(state | g) prod K_k(o | state), times the
    After-act's K(o_a | state, end) when an after-report was taken."""
    draws, end, report = record
    O = plated.world.O
    total = Fraction(0)
    for state, p in plated.pl[g].items():
        for k, o in draws:
            if not p:
                break
            p *= O[k].kernel.at(state, o)
        if p and report is not None:
            p *= plated.after.kernels[end].at(state, report)
        total += p
    return total


class _Records:
    """The likelihood of a multiset of records, as `_update` reads a kernel: at a Global value,
    a token (record, count) weighs L(record | g) to the count."""

    __slots__ = ("plated",)

    def __init__(self, plated):
        self.plated = plated

    def at(self, g, token):
        record, n = token
        return likelihood(self.plated, record, g) ** n


def posterior_global(plated, counts):
    """P(Global | Counts), a Belief over the Global values. A multiset no Global value can have
    written raises WorldFalsified, as any observation of zero mass does."""
    b = _sealed(dict(plated.pg))
    lik = _Records(plated)
    for token in counts.items():
        b = _update(b, lik, token)
    return b


def episode_prior(plated, counts):
    """The prior of the next episode: P(Global | Counts) P(local | Global). No local is carried."""
    pg = _weights(posterior_global(plated, counts))
    return _sealed({state: pg[g] * p for g in pg for state, p in plated.pl[g].items()})


def counts_sha(counts):
    """The digest of Counts, in the encoding SURFACE v0.2 will adopt (counts_check.counts_sha)."""
    rows = sorted([[[list(x) for x in draws], end, report, n] for (draws, end, report), n in counts.items()],
                  key=json.dumps)
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def realisable(plated, record):
    """A record an episode of this declaration can write under v0's loop, whatever its policy:
    its acts declared, at most N draws, each `once` act at most once, an ending outcome only as
    the last draw and then as the end, an after-report exactly when an After-act is declared (S13)."""
    draws, end, report = record
    world = plated.world
    if len(draws) > world.N:
        return False
    seen = set()
    for i, (k, o) in enumerate(draws):
        act = world.O.get(k)
        if act is None or (act.once and k in seen):
            return False
        seen.add(k)
        if o in act.ends and (i != len(draws) - 1 or end != ending(k, o)):
            return False
    if end not in world.T:
        if not draws:
            return False
        k, o = draws[-1]
        if o not in world.O[k].ends or end != ending(k, o):
            return False
    return (report is not None) == (plated.after is not None)


def expressible(plated, counts):
    """Every record realisable here, and the whole multiset of positive probability under some
    Global value (S13)."""
    if not all(realisable(plated, r) for r in counts):
        return False
    return any(all(likelihood(plated, r, g) > 0 for r in counts) for g in plated.pg)


def score(plated, counts):
    """S14: the leave-one-out predictive probability -- for each copy of each record, its
    likelihood under the Prior conditioned on all the others, multiplied together."""
    total = Fraction(1)
    for r, n in counts.items():
        rest = Counter(counts)
        rest[r] -= 1
        rest = +rest
        b = posterior_global(plated, rest)
        total *= expect(b, {g: likelihood(plated, r, g) for g in _weights(b)}) ** n
    return total


def e7(plated, counts):
    """E7's lines: for every draw in Counts, grouped by the history within its episode that led
    to it, the total variation between the empirical law of its outcome and its posterior
    predictive -- the Global weighted by P(Global | all Counts), the history conditioning the
    local only. Keyed (history, act, end): `end` is the terminal fired for an after-report,
    and None for a report."""
    pg = _weights(posterior_global(plated, counts))
    groups = {}
    for (draws, end, report), n in counts.items():
        seq = list(draws)
        for j, (k, o) in enumerate(seq):
            groups.setdefault((tuple(seq[:j]), k, None), Counter())[o] += n
        if report is not None:
            groups.setdefault((tuple(seq), plated.after.name, end), Counter())[report] += n
    lines = {}
    for (hist, k, end), seen in groups.items():
        kernel = plated.after.kernels[end] if end is not None else plated.world.O[k].kernel
        total = sum(seen.values())
        pred, live = {}, Fraction(0)
        for g, w in pg.items():
            b = _sealed(dict(plated.pl[g]))
            try:
                for hk, ho in hist:
                    b = _update(b, plated.world.O[hk].kernel, ho)
            except WorldFalsified:
                continue                                    # this Global cannot have led here
            live += w
            for o, q in push(b, kernel).items():
                pred[o] = pred.get(o, Fraction(0)) + w * q
        outs = set(kernel.outcomes()) | set(seen)
        lines[(hist, k, end)] = sum((abs(Fraction(seen.get(o, 0), total) - pred.get(o, Fraction(0)) / live)
                                     for o in outs), Fraction(0)) / 2
    return lines
