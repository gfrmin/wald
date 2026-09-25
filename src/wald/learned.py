"""SURFACE v0.2: the declarations of what is learned between episodes, read into CHARTER v0.2's dict.

Six declarations -- `globals`, the prior read as P(Global), `local_prior`, `after`, `counts`,
`falsifiers` -- and `score(of="counts")`. A pack that writes any of them elaborates in two steps:
first the joint World over Omega's states as SURFACE v0 spells them, judged by v0's and v0.1's
rules exactly as any pack is (`surface.Pack.joint`); then the dict of laws/model.py, each state
the pair (local, Global), judged by CHARTER v0.2's (`plated.declare`). The dict is what
`load_pack` returns. Every refusal here names its rule, `[V2.k]`, as the reference's do."""
import ast
from collections import Counter
from fractions import Fraction
from itertools import product

from .digits import long_int
from .refusals import (DUPLICATE, FLOAT, MISSING, NOT_A_DECLARATION, PRIOR, TABLE_SHAPE,
                       TABLE_SOURCE, UNDECLARED_READ, UNKNOWN_NAME, Refused)

LEARNED = ("globals", "local_prior", "after", "counts", "falsifiers")     # V2.0: each at most once
RESERVED = "end:"                   # V2.6: the ends of ending outcomes, and no terminal's name


def _tuple(x):
    return x if isinstance(x, tuple) else (x,)


def _digits(text):
    """V2.6: a multiplicity as written -- decimal digits, the first not 0. `True`, `0x1` and `1_0`
    are all Python ints, so the source text is what is read, not the value."""
    return bool(text) and text[0] in "123456789" and all(c in "0123456789" for c in text)


class Learned:
    """The v0.2 half of a pack. `surface.Pack` inherits it; nothing here is used alone."""

    def start_learning(self):
        self.globals_ = None            # the Global components, in the space's order, once declared
        self.locals_ = None
        self.prior_g = None             # P(Global), keyed as the pack writes a Global value
        self.prior_l = None             # P(local | Global)
        self.after = None
        self.counts_ = None
        self.counts_sha = None
        self.falsifiers_ = None
        self.counts_score = None
        self.paying = False             # inside `utility`, where no `by` may turn on a Global

    def learns(self):
        """Whether this pack is one of SURFACE v0.2's: a Global, an After-act, or Counts."""
        return (self.globals_ is not None or self.after is not None or self.counts_ is not None
                or self.falsifiers_ is not None or self.counts_score is not None)

    # ---- values of the space, as a pack writes them
    def global_values(self):
        """A Global value is a name when one component is Global, a tuple when several are (V2.2)."""
        values = [tuple(v) for v in self.value_product(self.globals_)]
        return [v[0] if len(self.globals_) == 1 else v for v in values]

    def local_values(self):
        if not self.locals_:
            return [()]
        values = [tuple(v) for v in self.value_product(self.locals_)]
        return [v[0] if len(self.locals_) == 1 else v for v in values]

    def value_product(self, components):
        return product(*[self.space[c] for c in components])

    def split(self, state):
        """A state as SURFACE v0 spells it, into the pair (local, Global) of laws/model.py."""
        return (tuple(self.value_of(state, c) for c in self.locals_),
                tuple(self.value_of(state, c) for c in self.globals_))

    def join(self, local, global_):
        """The pair back into a state of the space, in the space's order."""
        of = dict(zip(self.locals_, local))
        of.update(zip(self.globals_, global_))
        state = tuple(of[c] for c in self.space)
        return state[0] if len(state) == 1 else state

    # ---- V2.1
    def say_globals(self, call):
        if self.space is None:
            raise Refused(MISSING, "[V2.1] space: the Globals are components of the space")
        if "prior" in self.said:
            raise Refused(MISSING, "[V2.1] globals: which components persist is said before the prior")
        given = self.arguments(call, ("components",), (), ("components",))
        names = self.cells.plain(given["components"])
        if not isinstance(names, list) or not names or not all(isinstance(c, str) for c in names):
            raise Refused(NOT_A_DECLARATION, '[V2.1] globals(["component", ...]), at least one:'
                          + " a World with no Global omits `globals`")
        if len(set(names)) != len(names):
            raise Refused(DUPLICATE, "[V2.1] a Global component is named twice")
        for c in names:
            if c not in self.space:
                raise Refused(UNKNOWN_NAME, "[V2.1] the component " + repr(c) + " is not in the space")
        # K19: every component may be Global -- a monitor, whose one local value is ()
        self.globals_ = [c for c in self.space if c in names]
        self.locals_ = [c for c in self.space if c not in names]

    # ---- V2.2
    def say_global_prior(self, call):
        given = self.arguments(call, ("table",), ("source",), ("table",))
        self.prior_source = self.source(given, call)
        if not isinstance(given["table"], ast.Dict):
            raise Refused(NOT_A_DECLARATION, "[V2.2] with Globals, the prior is a dict keyed by Global value")
        self.prior_g = self.table(given["table"], self.prior_source, 1)
        values = set(self.global_values())
        strangers = [g for g in self.prior_g if g not in values]
        if strangers:
            raise Refused(TABLE_SHAPE, "[V2.2] the prior names a Global value outside the space: "
                          + ", ".join(repr(g) for g in strangers))
        if any(p <= 0 for p in self.prior_g.values()) or sum(self.prior_g.values()) != 1:
            raise Refused(PRIOR, "[V2.2] P(Global) is strictly positive and sums to 1")
        if not self.locals_:
            # every component Global: the joint is the prior, and the one local value is ()
            self.prior_l = {g: {(): Fraction(1)} for g in self.prior_g}
            self.prior = dict(self.prior_g)

    # ---- V2.3
    def say_local_prior(self, call):
        if self.globals_ is None:
            raise Refused(MISSING, "[V2.3] globals: P(local | Global) needs the Globals")
        if not self.locals_:
            raise Refused(NOT_A_DECLARATION, "[V2.3] a World whose every component is Global has no"
                          + " local to give a law")
        if self.prior_g is None:
            raise Refused(MISSING, "[V2.3] prior: P(local | Global) comes after P(Global)")
        given = self.arguments(call, ("table",), ("source",), ("table",))
        tag = self.source(given, call)
        rows = self.table(given["table"], tag, 2)
        if set(rows) != set(self.prior_g):
            raise Refused(TABLE_SHAPE, "[V2.3] local_prior has a row for exactly the Global values"
                          + " the prior names")
        values = set(self.local_values())
        for g, row in rows.items():
            if set(row) - values:
                raise Refused(TABLE_SHAPE, "[V2.3] the row " + repr(g) + " names a local value"
                              + " outside the space")
            if any(p < 0 for p in row.values()) or sum(row.values()) != 1:
                raise Refused(PRIOR, "[V2.3] the row " + repr(g) + ": cells never negative, summing to 1")
        self.prior_l = rows
        # V2.4: the states are the pairs to which the two factors give positive mass
        self.prior = {}
        for g, pg in self.prior_g.items():
            for l, pl in rows[g].items():
                if pg * pl > 0:
                    self.prior[self.join(_tuple(l), _tuple(g))] = pg * pl

    # ---- V2.5
    def say_after(self, call):
        given = self.arguments(call, ("name",), ("kernel", "reads"), ("name", "kernel", "reads"))
        name = self.cells.plain(given["name"])
        reads = self.cells.plain(given["reads"])
        if not isinstance(name, str):
            raise Refused(NOT_A_DECLARATION, "[V2.5] after(name, kernel=table(...), reads=[...])")
        if not isinstance(reads, list) or not all(isinstance(c, str) for c in reads):
            raise Refused(NOT_A_DECLARATION, "[V2.5] an After-act's reads is a list of components")
        space = self.components()
        for c in reads:
            if c not in space:
                raise Refused(UNKNOWN_NAME, "[V2.5] the After-act reads " + repr(c)
                              + ", which is not a component of the space")
        node = given["kernel"]
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "table"):
            raise Refused(NOT_A_DECLARATION, "[V2.5] an After-act's kernel is"
                          + " table({end: {state: {outcome: p}}}, source=...)")
        rows_given = self.arguments(node, ("rows",), ("source",), ("rows",))
        tag = self.source(rows_given, node)
        K = self.table(rows_given["rows"], tag, 3)
        read = [c for c in space if c in reads]
        for end, rows in K.items():
            # V0.reads, as for an act: states that agree on what it reads have one row, per end
            seen = {}
            for state, row in rows.items():
                if seen.setdefault(tuple(self.value_of(state, c) for c in read), row) != row:
                    raise Refused(UNDECLARED_READ, "[V2.5] the After-act " + repr(name)
                                  + " depends on a component outside reads=" + repr(reads))
        # SURFACE v0 section 4: every row written in a `table` is checked where it is written, and
        # the After-act's kernel is written in one (QUESTIONS.md Q10: the reference does not ask)
        self.distributions({(end, state): row for end, rows in K.items() for state, row in rows.items()},
                           "[V2.5] the After-act's kernel (QUESTIONS.md Q10)")
        self.after = {"name": name, "K": K}

    # ---- V2.6, V2.7
    def record(self, node, falsifier=False):
        """[[[act, outcome], ...], end, after]: names, and None for an absent end (a falsifier's
        only) or after-report. Every outcome is a name (K27): a tuple cannot be written."""
        shape = Refused(NOT_A_DECLARATION, "[V2.6] line " + str(getattr(node, "lineno", "?"))
                        + ": a record is [[[act, outcome], ...], end, after-report or None]")
        if not (isinstance(node, ast.List) and len(node.elts) == 3):
            raise shape
        none = lambda n: isinstance(n, ast.Constant) and n.value is None
        draws = self.cells.plain(node.elts[0])
        end = None if none(node.elts[1]) else self.cells.plain(node.elts[1])
        report = None if none(node.elts[2]) else self.cells.plain(node.elts[2])
        if not (isinstance(draws, list) and all(isinstance(d, list) and len(d) == 2
                                                and all(isinstance(x, str) for x in d) for d in draws)):
            raise shape
        if not (isinstance(end, str) or (falsifier and end is None)):
            raise shape
        if not (report is None or isinstance(report, str)):
            raise shape
        return (tuple(tuple(d) for d in draws), end, report)

    def say_counts(self, call):
        given = self.arguments(call, ("rows",), ("sha256", "source"), ("rows", "sha256"))
        tag = self.source(given, call)
        if tag != "data":
            raise Refused(TABLE_SOURCE, "[V2.6] Counts are facts, so their source is `data`, not " + repr(tag))
        if not isinstance(given["rows"], ast.List):
            raise Refused(NOT_A_DECLARATION, "[V2.6] counts([[draws, end, after, n], ...], sha256=...)")
        counts = Counter()
        for row in given["rows"].elts:
            if not (isinstance(row, ast.List) and len(row.elts) == 4):
                raise Refused(NOT_A_DECLARATION, "[V2.6] line " + str(getattr(row, "lineno", "?"))
                              + ": a row of Counts is [draws, end, after, n]")
            n = row.elts[3]
            if isinstance(n, ast.Constant) and isinstance(n.value, float):
                raise Refused(FLOAT, "[V2.6] line " + str(n.lineno) + ": a multiplicity is a whole number")
            long = isinstance(n, ast.Name) and n.id in self.cells.longs
            written = self.cells.longs[n.id] if long else ast.get_source_segment(self.text, n)
            if written is not None and not _digits(written):
                raise Refused(NOT_A_DECLARATION, "[V2.6] line " + str(n.lineno) + ": a multiplicity"
                              + " is written as decimal digits, not " + repr(written))
            if not (long or isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 1):
                raise Refused(NOT_A_DECLARATION, "[V2.6] line " + str(getattr(n, "lineno", "?"))
                              + ": a multiplicity is a whole number at least 1, written out")
            record = self.record(ast.List(elts=row.elts[:3], ctx=ast.Load(), lineno=row.lineno))
            if record in counts:
                raise Refused(DUPLICATE, "[V2.6] line " + str(row.lineno) + ": a record written twice")
            counts[record] = long_int(written) if long else n.value
            self.cells.count(tag)                    # V2.12: a multiplicity, under `data`
        sha = self.cells.plain(given["sha256"])
        if not isinstance(sha, str):
            raise Refused(NOT_A_DECLARATION, "[V2.6] sha256 is the digest's hex, a name")
        self.counts_, self.counts_sha = counts, sha

    def say_falsifiers(self, call):
        # V2.7 says "only with counts" and gives no order, as V2.1 and V2.3 do for theirs; so the
        # Counts are asked for when the pack is complete (`learned_spec`). QUESTIONS.md Q13.
        given = self.arguments(call, ("records",), (), ("records",))
        if not isinstance(given["records"], ast.List):
            raise Refused(NOT_A_DECLARATION, "[V2.7] falsifiers([[draws, end, after], ...])")
        out = [self.record(e, falsifier=True) for e in given["records"].elts]
        if len(set(out)) != len(out):
            raise Refused(DUPLICATE, "[V2.7] a falsifying record written twice")
        self.falsifiers_ = out

    # ---- V2.8
    def say_counts_score(self, given, tag):
        if self.counts_score is not None:
            raise Refused(DUPLICATE, "[V2.8] the Score of the Counts is declared twice")
        self.counts_score = self.cells.owned(given["value"], tag, ("data",), TABLE_SOURCE)
        self.cells.count(tag)

    # ---- the dict of laws/model.py
    def end_of(self, key):
        """An After-act's row key as a record names the end (V2.5, V2.6): a terminal as itself,
        and an ending outcome's `(act, outcome)` as "end:act=outcome"."""
        if isinstance(key, tuple) and len(key) == 2 and all(isinstance(x, str) for x in key):
            from .episode import ending
            return ending(key[0], key[1])
        return key

    def learned_spec(self):
        """V2.0-V2.14: the joint World judged as any pack's, then CHARTER v0.2's dict judged by
        CHARTER v0.2's rules. Returns the dict."""
        from .plated import declare as declare_plated
        if self.globals_ and self.locals_ and self.prior_l is None:
            raise Refused(MISSING, "[V2.3] local_prior: with a local component, P(local | Global) is required")
        name = self.after["name"] if self.after is not None else None
        held = None
        if name is not None and self.prices is not None:
            if name not in self.prices:
                raise Refused(MISSING, "[V2.5] the After-act " + repr(name) + " has no cell in `price`")
            held = self.prices.pop(name)            # the menu's prices; the After-act is not in M
        try:
            joint = self.joint()
        finally:
            if held is not None:
                self.prices[name] = held
        if self.globals_ and joint.get("bottom") is not None:
            raise Refused(NOT_A_DECLARATION, "[V2.14] a catch-all state beside Globals is not"
                          + " sayable in v0.2 (K25)")
        for t in self.T:
            if isinstance(t, str) and t.startswith(RESERVED):
                raise Refused(NOT_A_DECLARATION, "[V2.6] the terminal " + repr(t) + ": a name beginning"
                              + " 'end:' is reserved for the ends of ending outcomes")
        globals_ = self.globals_ or []
        if self.globals_ is None:
            self.globals_, self.locals_ = [], list(self.space)          # V2.9: one Global value, ()
        W = {"locals": [(c, list(self.space[c])) for c in self.locals_],
             "globals": [(c, list(self.space[c])) for c in self.globals_]}
        if globals_:
            W["prior_global"] = {_tuple(g): p for g, p in self.prior_g.items()}
            W["prior_local"] = {_tuple(g): {_tuple(l): p for l, p in row.items() if p > 0}
                                for g, row in self.prior_l.items()}
        else:
            W["prior_global"] = {(): Fraction(1)}
            W["prior_local"] = {(): {_tuple(state): p for state, p in self.prior.items()}}
        W["T"] = {t: {self.split(s): u for s, u in table.items()} for t, table in joint["T"].items()}
        W["O"] = {}
        for k, act in joint["O"].items():
            W["O"][k] = {"K": {self.split(s): row for s, row in act["K"].items()},
                         "price": act["price"], "once": act["once"]}
            if act["ends"]:
                W["O"][k]["ends"] = set(act["ends"])
                W["O"][k]["u_end"] = {o: {self.split(s): u for s, u in table.items()}
                                      for o, table in act["ends"].items()}
        W["N"], W["d"] = joint["N"], joint["d"]
        for key in ("closed", "bottom", "dplus", "fraction", "rate", "ops"):
            if key in joint:
                W[key] = joint[key]
        if self.after is not None:
            states = set(self.states())
            K = {}
            for key, rows in self.after["K"].items():
                strangers = [s for s in rows if s not in states]
                if strangers:
                    raise Refused(TABLE_SHAPE, "[V2.4] the After-act's rows at " + repr(key)
                                  + " name " + repr(strangers[0]) + ", which is not a state"
                                  + " (QUESTIONS.md Q10)")
                end = self.end_of(key)
                if end in K:
                    raise Refused(DUPLICATE, "[V2.5] two rows of the After-act's kernel name the end "
                                  + repr(end) + " (QUESTIONS.md Q10)")
                K[end] = {self.split(s): row for s, row in rows.items()}
            W["after"] = {"K": K, "price": self.prices[name], "name": name}
        if self.counts_ is not None:
            W["counts"], W["counts_sha"] = self.counts_, self.counts_sha
            if self.counts_score is not None:
                W["score"] = self.counts_score
            if self.falsifiers_ is not None:
                W["falsifiers"] = self.falsifiers_
        elif self.counts_score is not None:
            raise Refused(MISSING, "[V2.8] counts: a Score of Counts, and no Counts (QUESTIONS.md Q12)")
        elif self.falsifiers_ is not None:
            raise Refused(MISSING, "[V2.7] counts: falsifying records travel with the Counts they ended")
        declare_plated(W)
        return W
