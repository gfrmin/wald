"""SURFACE sections 1, 2 and 4: what a pack is, its declarations and the seven kernel forms.

SURFACE v0.1 adds five declarations to the nine -- `depth_plus`, `think`, `cost`, `rate` and
`score` -- one for each table CHARTER v0.1's think act needs. They come together or not at all;
a pack that writes none of them is a v0 pack and elaborates exactly as before.

A pack is a text file in Python's syntax, **parsed and never executed** (K1). This module reads
the syntax tree and builds the World spec of laws/INTERFACE.md; `declare` then has the last word,
so the World's own rules are not written twice. What the grammar gives no form, a pack cannot
say: in particular it cannot choose (CHARTER E5), compare a probability (S1) or update a
belief (section 2) -- there is nowhere to put any of them."""
import ast
import itertools
from fractions import Fraction

from .cells import Cells, where
from .datafile import rows as data_rows
from .refusals import (COST, DEPTH, DEPTH_PLUS, DUPLICATE, FRACTION, KERNEL_ROW, MISSING,
                       NOT_A_DECLARATION, RATE, SYNTAX, TABLE_SHAPE, TABLE_SOURCE, UNDECLARED_READ,
                       UNKNOWN_NAME, UNSCORED, Refused)
from .world import declare

DECLARATIONS = ("world", "horizon", "depth", "space", "param", "prior", "utility", "price", "act",
                "depth_plus", "think", "cost", "rate", "score")
ONCE = ("world", "horizon", "depth", "space", "prior", "utility", "price")
# SURFACE v0.1: the think act's four, each at most once and all four or none. `score` is not one
# of them -- there are two tables that can be fitted, so there can be two scores.
META = ("depth_plus", "think", "cost", "rate")
OWNED = ("elicited", "fitted")      # a meta-belief is the owner's number or a fit, and nothing else
SCORED = ("fraction", "cost")       # the two meta-tables a Score can be of (K14)
KERNEL_FORMS = ("table", "by", "point", "data", "mixture", "product", "compose")


class Pack:
    """A pack, read. Every refusal below names the rule of the page that refused it."""

    def __init__(self, text, data_dir):
        self.data_dir = data_dir
        self.cells = Cells()
        self.said = set()
        self.space = None
        self.prior = None
        self.T = None
        self.ending = {}
        self.prices = None
        self.acts = {}
        self.kernel_tags = {}
        self.named = set()
        self.closed = False
        self.bottom = None
        self.scores = {}
        try:
            tree = ast.parse(text)
        except SyntaxError as e:
            raise Refused(SYNTAX, str(e))
        for statement in tree.body:
            self.declaration(statement)

    # ---- the shape of a pack (section 1)
    def declaration(self, statement):
        if not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
                and isinstance(statement.value.func, ast.Name)
                and statement.value.func.id in DECLARATIONS):
            raise Refused(NOT_A_DECLARATION, where(statement)
                          + ": a pack is a list of declarations and nothing else")
        call = statement.value
        said = call.func.id
        if (said in ONCE or said in META) and said in self.said:
            raise Refused(DUPLICATE, said + " is declared twice")
        self.said.add(said)
        # One `say_` per name in DECLARATIONS, and a statement that is not one of those names
        # never reaches here: the grammar is that tuple, and nothing else can be dispatched.
        getattr(self, "say_" + said)(call)

    def arguments(self, call, positional, keywords, required=()):
        """Nothing in a pack has a default: what is not written is refused, never assumed."""
        if len(call.args) > len(positional) or any(isinstance(a, ast.Starred) for a in call.args):
            raise Refused(NOT_A_DECLARATION, where(call) + ": too many arguments")
        given = dict(zip(positional, call.args))
        for keyword_ in call.keywords:
            if keyword_.arg is None or keyword_.arg not in keywords:
                raise Refused(NOT_A_DECLARATION, where(call) + ": no keyword "
                              + repr(keyword_.arg) + " here")
            if keyword_.arg in given:
                raise Refused(DUPLICATE, where(call) + ": " + keyword_.arg + " is given twice")
            given[keyword_.arg] = keyword_.value
        for need in required:
            if need not in given:
                raise Refused(NOT_A_DECLARATION, where(call) + ": " + need + " is not written")
        return given

    def source(self, given, call):
        if "source" not in given:
            raise Refused(TABLE_SOURCE, where(call) + ": every table names its source")
        return self.cells.tag(given["source"])

    def flag(self, node, what):
        value = self.cells.plain(node)
        if not isinstance(value, bool):
            raise Refused(NOT_A_DECLARATION, where(node) + ": " + what)
        return value

    def name_key(self, node):
        key = self.cells.plain(node)
        if not isinstance(key, (str, tuple)):
            raise Refused(NOT_A_DECLARATION, where(node) + ": a key is a name or a tuple of names")
        return key

    # ---- the space and the states
    def components(self):
        if self.space is None:
            raise Refused(MISSING, "space: a component is named before it is read")
        return self.space

    def states(self):
        if self.prior is None:
            raise Refused(MISSING, "prior: every table over states comes after the prior,"
                          + " which is what says the states are these")
        return list(self.prior)

    def value_of(self, state, component):
        """The value a state gives one component of the space."""
        space = self.components()
        if component not in space:
            raise Refused(UNKNOWN_NAME, "the component " + repr(component) + " is not in the space")
        if len(space) == 1:
            return state
        if not isinstance(state, tuple) or len(state) != len(space):
            raise Refused(TABLE_SHAPE, "the state " + repr(state) + " is not a tuple of the space's "
                          + str(len(space)) + " components")
        return state[list(space).index(component)]

    def product(self):
        space = self.components()
        return [values[0] if len(space) == 1 else values
                for values in itertools.product(*space.values())]

    # ---- tables
    def table(self, node, tag, depth):
        """A dict literal written out, `depth` levels of keys above the numbers."""
        if depth == 0:
            self.cells.count(tag)
            return self.cells.number(node, tag)
        if not isinstance(node, ast.Dict) or any(k is None for k in node.keys):
            raise Refused(NOT_A_DECLARATION, where(node) + ": a table is a dict written out")
        out = {}
        for key_node, value_node in zip(node.keys, node.values):
            key = self.name_key(key_node)
            if key in out:
                raise Refused(DUPLICATE, where(key_node) + ": the key " + repr(key)
                              + " is written twice")
            out[key] = self.table(value_node, tag, depth - 1)
        return out

    def keyed(self, node, build, what):
        """A dict of tables, keyed by act or by outcome. A key written twice is refused here
        too: the second would silently replace the first."""
        if not isinstance(node, ast.Dict) or any(k is None for k in node.keys):
            raise Refused(NOT_A_DECLARATION, where(node) + ": " + what)
        out = {}
        for key_node, value_node in zip(node.keys, node.values):
            key = self.name_key(key_node)
            if key in out:
                raise Refused(DUPLICATE, where(key_node) + ": the key " + repr(key)
                              + " is written twice")
            out[key] = build(value_node)
        return out

    def spread(self, component, rows, node):
        """`by(component, ...)`: one row per value the component takes in Omega, no more, no
        fewer, spread over the states that take it."""
        need = {self.value_of(state, component) for state in self.states()}
        if set(rows) != need:
            raise Refused(TABLE_SHAPE, where(node) + ": by(" + repr(component)
                          + ") needs a row for exactly " + ", ".join(sorted(repr(v) for v in need)))
        return {state: rows[self.value_of(state, component)] for state in self.states()}

    def over(self, node, tag, depth):
        """A table over states: a dict keyed by state, or `by` when it turns on one component."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "by":
            given = self.arguments(node, ("component", "rows"), (), ("component", "rows"))
            component = self.cells.plain(given["component"])
            return self.spread(component, self.table(given["rows"], tag, depth), node)
        return self.table(node, tag, depth)

    # ---- the nine declarations (section 2)
    def say_world(self, call):
        given = self.arguments(call, ("name",), ("closed", "bottom"), ("name",))
        self.name = self.cells.plain(given["name"])
        if "closed" in given:
            self.closed = self.flag(given["closed"], "closed=True")
        if "bottom" in given:
            self.bottom = self.name_key(given["bottom"])

    def say_horizon(self, call):
        given = self.arguments(call, ("n",), ("source",), ("n",))
        self.horizon_source = self.source(given, call)
        self.N = self.cells.number(given["n"], self.horizon_source)
        self.cells.count(self.horizon_source)

    def say_depth(self, call):
        given = self.arguments(call, ("d",), ("source",), ("d",))
        self.depth_source = self.source(given, call)
        self.d = self.cells.number(given["d"], self.depth_source)
        self.cells.count(self.depth_source)

    def say_space(self, call):
        given = self.arguments(call, ("components",), (), ("components",))
        node = given["components"]
        if not isinstance(node, ast.Dict) or not node.keys or any(k is None for k in node.keys):
            raise Refused(NOT_A_DECLARATION, where(node) + ': space({"component": [names], ...})')
        space = {}
        for key_node, value_node in zip(node.keys, node.values):
            component = self.cells.plain(key_node)
            values = self.cells.plain(value_node)
            if not isinstance(component, str) or not isinstance(values, list) or not values \
                    or not all(isinstance(v, str) for v in values):
                raise Refused(NOT_A_DECLARATION, where(key_node)
                              + ": a component is a name and a non-empty list of names")
            if component in space:
                raise Refused(DUPLICATE, "the component " + repr(component) + " is declared twice")
            if len(set(values)) != len(values):
                raise Refused(DUPLICATE, "a value of the component " + repr(component)
                              + " is listed twice")
            space[component] = values
        self.space = space

    def say_param(self, call):
        given = self.arguments(call, ("name", "value"), ("source",), ("name", "value"))
        self.cells.declare_param(given["name"], given["value"], self.source(given, call))

    def say_prior(self, call):
        self.components()   # the prior's keys are states of the space, so the space is named first
        given = self.arguments(call, ("table",), ("source",), ("table",))
        self.prior_source = self.source(given, call)
        if not isinstance(given["table"], ast.Dict):
            raise Refused(NOT_A_DECLARATION, where(call) + ": the prior is written out state by"
                          + " state -- it is what says which states there are")
        self.prior = self.table(given["table"], self.prior_source, 1)

    def say_utility(self, call):
        self.states()
        given = self.arguments(call, ("terminal",), ("ending", "source"), ("terminal",))
        tag = self.source(given, call)
        self.utility_source = tag
        self.T = self.keyed(given["terminal"], lambda v: self.over(v, tag, 1),
                            "utility({act: table over states}, ...)")
        if "ending" in given:
            self.ending = self.keyed(
                given["ending"],
                lambda per_act: self.keyed(per_act, lambda u: self.over(u, tag, 1),
                                           "ending={act: {outcome: table over states}}"),
                "ending={act: {outcome: table over states}}")

    def say_price(self, call):
        given = self.arguments(call, ("table",), ("source",), ("table",))
        self.price_source = self.source(given, call)
        self.prices = self.table(given["table"], self.price_source, 1)

    def say_act(self, call):
        self.states()
        given = self.arguments(call, ("name",), ("kernel", "once", "reads"),
                               ("name", "kernel", "once", "reads"))
        name = self.cells.plain(given["name"])
        if name in self.acts:
            raise Refused(DUPLICATE, "the act " + repr(name) + " is declared twice")
        once = self.flag(given["once"], "once=True, or once=False for a fresh act")
        tags = set()
        self.named = set()
        K = self.kernel(given["kernel"], tags)
        reads = self.cells.plain(given["reads"])
        if not isinstance(reads, list) or not reads or not all(isinstance(r, str) for r in reads):
            raise Refused(NOT_A_DECLARATION, "act " + repr(name)
                          + ": reads=[source, ...], at least one (CHARTER S2)")
        self.refuse_undeclared_read(name, K, reads)
        self.kernel_tags[name] = sorted(tags)
        self.acts[name] = {"K": K, "once": once, "reads": reads}

    def refuse_undeclared_read(self, name, K, reads):
        """K9, both halves: a component the kernel names is in `reads`, and the kernel depends
        on no component outside it -- states that agree on what the act reads have one row."""
        unsaid = sorted(self.named - set(reads))
        if unsaid:
            raise Refused(UNDECLARED_READ, "act " + repr(name) + " names "
                          + ", ".join(repr(c) for c in unsaid) + " in its kernel but does not"
                          + " say it reads it")
        components = list(self.components())
        read = [c for c in components if c in reads]
        rows = {}
        for state, row in K.items():
            seen = tuple(self.value_of(state, c) for c in read)
            if rows.setdefault(seen, row) != row:
                raise Refused(UNDECLARED_READ, "act " + repr(name) + " depends on a component"
                              + " outside reads=" + repr(reads))

    # ---- the five declarations of SURFACE v0.1 (section 1)
    def say_depth_plus(self, call):
        """Depth+, written out although J11 fixes it at 2: a pack has no defaults (K13). Its one
        admissible source is `elicited` -- it is the owner's (K18)."""
        given = self.arguments(call, ("d",), ("source",), ("d",))
        tag = self.source(given, call)
        if tag != "elicited":
            raise Refused(TABLE_SOURCE, where(call) + ": Depth+ is the owner's (J11), so it is"
                          + " `elicited`, not " + repr(tag))
        self.dplus_source = tag
        self.dplus = self.cells.owned(given["d"], tag, ("elicited",), TABLE_SOURCE)
        self.cells.count(tag)

    def say_think(self, call):
        """The think act and its Fraction f: a meta-belief, so `elicited` or `fitted` (K13)."""
        given = self.arguments(call, (), ("fraction", "source"), ("fraction",))
        tag = self.source(given, call)
        if tag not in OWNED:
            raise Refused(FRACTION, where(call) + ": a Fraction is a meta-belief -- `elicited` or"
                          + " `fitted`, not " + repr(tag))
        self.fraction_source = tag
        self.fraction = self.cells.owned(given["fraction"], tag, OWNED, FRACTION)
        self.cells.count(tag)

    def say_cost(self, call):
        """The Cost table: ops(s) for s = 1 .. |Omega|, positional. The positions are keys and no
        numeral stands for one (K12), so the list's length is what is checked, against the states
        the prior names (K10) -- which is why the prior comes first."""
        states = self.states()
        given = self.arguments(call, ("table",), ("source",), ("table",))
        tag = self.source(given, call)
        if tag not in OWNED:
            raise Refused(COST, where(call) + ": a Cost is a meta-belief -- `elicited` or"
                          + " `fitted`, not " + repr(tag))
        if not isinstance(given["table"], ast.List):
            raise Refused(NOT_A_DECLARATION, where(call) + ": the Cost is a list, one cell for"
                          + " each count of live states, in order")
        cells = [self.cells.owned(e, tag, OWNED, COST) for e in given["table"].elts]
        if len(cells) != len(states):
            raise Refused(COST, where(call) + ": " + str(len(cells)) + " cells for "
                          + str(len(states)) + " states")
        self.ops = {s: cell for s, cell in enumerate(cells, 1)}
        self.cost_source = tag
        self.cells.count(tag, len(cells))

    def say_rate(self, call):
        """The Rate r, utility per operation: the owner's exchange rate, so `elicited`."""
        given = self.arguments(call, ("r",), ("source",), ("r",))
        tag = self.source(given, call)
        if tag != "elicited":
            raise Refused(RATE, where(call) + ": the Rate is the owner's exchange rate, so it is"
                          + " `elicited`, not " + repr(tag))
        self.rate_source = tag
        self.rate = self.cells.owned(given["r"], tag, ("elicited",), RATE)
        self.cells.count(tag)

    def say_score(self, call):
        """The held-out Score of one fitted meta-table, named by `of` (K14). It is a measurement,
        so its source is `data`; the rounding a rational needs is part of the measurement."""
        given = self.arguments(call, ("value",), ("of", "source"), ("value", "of"))
        tag = self.source(given, call)
        of = self.cells.plain(given["of"])
        if tag != "data":
            raise Refused(TABLE_SOURCE, where(call) + ": a Score is measured, so it is `data`,"
                          + " not " + repr(tag))
        if of not in SCORED:
            raise Refused(NOT_A_DECLARATION, where(call) + ": a Score is of the Fraction or of"
                          + " the Cost, not of " + repr(of))
        if of in self.scores:
            raise Refused(DUPLICATE, "the Score of the " + of + " is declared twice")
        self.scores[of] = self.cells.owned(given["value"], tag, ("data",), TABLE_SOURCE)
        self.cells.count(tag)

    # ---- the seven kernel forms (section 4)
    def distributions(self, rows, what):
        """Every row of probabilities is checked where it is written (S4)."""
        for state, row in rows.items():
            if any(q < 0 for q in row.values()) or sum(row.values(), Fraction(0)) != 1:
                raise Refused(KERNEL_ROW, what + ": the row " + repr(state)
                              + " is not a distribution")
        return rows

    def kernel(self, node, tags):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in KERNEL_FORMS):
            raise Refused(NOT_A_DECLARATION, where(node) + ": a kernel is table, by, point, data,"
                          + " mixture, product or compose, and nothing else")
        form = node.func.id
        if form == "table":
            given = self.arguments(node, ("rows",), ("source",), ("rows",))
            tag = self.source(given, node)
            tags.add(tag)
            return self.distributions(self.table(given["rows"], tag, 2), "table")
        if form == "by":
            given = self.arguments(node, ("component", "rows"), ("source",), ("component", "rows"))
            tag = self.source(given, node)
            tags.add(tag)
            component = self.cells.plain(given["component"])
            rows = self.distributions(self.table(given["rows"], tag, 2), "by")
            self.named.add(component)
            return {s: dict(row) for s, row in self.spread(component, rows, node).items()}
        if form == "point":
            given = self.arguments(node, ("component",), (), ("component",))
            component = self.cells.plain(given["component"])
            self.named.add(component)
            return {s: {self.value_of(s, component): Fraction(1)} for s in self.states()}
        if form == "data":
            given = self.arguments(node, ("file",), ("source", "sha256"), ("file", "sha256"))
            tag = self.source(given, node)
            if tag == "elicited":
                raise Refused(TABLE_SOURCE, where(node) + ": an elicited number is written in the"
                              + " pack, where its owner can see it")
            tags.add(tag)
            K, count = data_rows(self.data_dir, self.cells.plain(given["file"]),
                                 self.cells.plain(given["sha256"]))
            self.cells.count(tag, count)
            return self.distributions(K, "the data file")
        if form == "mixture":
            given = self.arguments(node, ("parts",), ("source",), ("parts",))
            tag = self.source(given, node)
            tags.add(tag)
            if not isinstance(given["parts"], ast.List):
                raise Refused(NOT_A_DECLARATION, where(node)
                              + ": mixture([(weight, kernel), ...], source=...)")
            parts = []
            for element in given["parts"].elts:
                if not (isinstance(element, ast.Tuple) and len(element.elts) == 2):
                    raise Refused(NOT_A_DECLARATION, where(element) + ": mixture([(weight, kernel), ...])")
                self.cells.count(tag)
                weight = self.cells.number(element.elts[0], tag)
                parts.append((weight, self.kernel(element.elts[1], tags)))
            if any(w < 0 for w, _ in parts) or sum((w for w, _ in parts), Fraction(0)) != 1:
                raise Refused(KERNEL_ROW, where(node)
                              + ": mixture weights are non-negative and sum to one")
            out = {state: {} for state in self.states()}
            for weight, K in parts:
                for state in out:
                    for outcome, q in K.get(state, {}).items():
                        out[state][outcome] = out[state].get(outcome, Fraction(0)) + weight * q
            return out
        if form == "product":
            given = self.arguments(node, ("left", "right"), (), ("left", "right"))
            left = self.kernel(given["left"], tags)
            right = self.kernel(given["right"], tags)
            return {state: {(a, b): p * q
                            for a, p in left.get(state, {}).items()
                            for b, q in right.get(state, {}).items()}
                    for state in self.states()}
        given = self.arguments(node, ("first", "then"), ("source",), ("first", "then"))
        tag = self.source(given, node)
        tags.add(tag)
        first = self.kernel(given["first"], tags)
        garbling = self.distributions(self.table(given["then"], tag, 2), "garbling")
        out = {}
        for state, row in first.items():
            seen = {}
            for emitted, p in row.items():
                if emitted not in garbling:
                    raise Refused(TABLE_SHAPE, where(node) + ": compose has no row for the"
                                  + " outcome " + repr(emitted))
                for shown, q in garbling[emitted].items():
                    seen[shown] = seen.get(shown, Fraction(0)) + p * q
            out[state] = seen
        return out

    # ---- the World spec of laws/INTERFACE.md
    def spec(self):
        for said in ONCE:
            if said not in self.said:
                raise Refused(MISSING, said + " is not declared")
        O = {}
        for name, act in self.acts.items():
            if name not in self.prices:
                raise Refused(TABLE_SHAPE, "no price for the act " + repr(name))
            O[name] = {"K": act["K"], "price": self.prices[name], "once": act["once"],
                       "ends": self.ending.get(name, {})}
        both = sorted(set(self.T) & set(O))
        if both:
            raise Refused(DUPLICATE, ", ".join(repr(n) for n in both)
                          + " names both a terminal and an observational act")
        strays = sorted((set(self.prices) - set(O)) | (set(self.ending) - set(O)))
        if strays:
            raise Refused(TABLE_SHAPE, "a price or an ending for no act: "
                          + ", ".join(repr(n) for n in strays))
        self.cells.refuse_unread()
        if self.N.denominator != 1 or self.d.denominator != 1:
            raise Refused(DEPTH, "the horizon and the depth are whole numbers")
        spec = {"prior": self.prior, "T": self.T, "O": O,
                "N": int(self.N), "d": int(self.d),
                "table_sources": {"prior": self.prior_source, "utility": self.utility_source,
                                  "price": self.price_source, "horizon": self.horizon_source,
                                  "depth": self.depth_source, "kernels": dict(self.kernel_tags)},
                "sources": {name: act["reads"] for name, act in self.acts.items()},
                "components": list(self.components())}
        self.say_the_think_act(spec)
        if self.closed:
            spec["closed"] = True
        if self.bottom is not None:
            spec["bottom"] = self.bottom
        # Last of the surface's own, so that a pack breaking this rule and one of the think act's
        # is refused by the same one of the two names the reference gives it (K7 allows either).
        if not set(self.prior) <= set(self.product()):
            raise Refused(TABLE_SHAPE, "the prior names a state that is not in the space")
        declare(spec)
        return spec


    def say_the_think_act(self, spec):
        """The four declarations come together or not at all, and a Score comes with the fitted
        table it scores. What the World then makes of the numbers is `declare`'s, not ours."""
        declared = [name for name in META if name in self.said]
        if not declared and not self.scores:
            return                                  # a v0 pack: it says nothing of a think act
        unsaid = [name for name in META if name not in self.said]
        if unsaid:
            raise Refused(MISSING, unsaid[0] + ": the think act's four tables come together"
                          + " or not at all")
        if self.dplus.denominator != 1:
            raise Refused(DEPTH_PLUS, "Depth+ is a whole number")
        spec.update({"dplus": int(self.dplus), "fraction": self.fraction, "rate": self.rate,
                     "ops": self.ops})
        spec["table_sources"].update({"dplus": self.dplus_source, "fraction": self.fraction_source,
                                      "cost": self.cost_source, "rate": self.rate_source})
        fitted = {table for table, tag in (("fraction", self.fraction_source),
                                           ("cost", self.cost_source)) if tag == "fitted"}
        unscored = sorted(fitted - set(self.scores))
        if unscored:
            raise Refused(UNSCORED, "the fitted " + unscored[0] + " carries its held-out Score")
        stray = sorted(set(self.scores) - fitted)
        if stray:
            raise Refused(MISSING, "a Score of the " + stray[0] + ", which is not fitted")
        if self.scores:
            spec["score"] = dict(self.scores)


def check(text, data_dir="."):
    """A pack, read and elaborated to the World spec of laws/INTERFACE.md, or Refused by name."""
    return Pack(text, data_dir).spec()


def census(text, data_dir="."):
    """The count of quantities by source (section 3): each cell, parameter, weight, price, the
    horizon and the depth counts once, however it is written."""
    pack = Pack(text, data_dir)
    pack.spec()
    return dict(pack.cells.census)
