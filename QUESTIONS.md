# QUESTIONS — for the author

Points where the pages, or a page and its reference checker, do not agree. Each carries the World or
the pack that shows it. The author amends; I do not guess.

---

## Q1 (brief 002). A key written twice in `utility(...)` is accepted by `laws/surface_check.py`

**Status: closed — the kit adopted the page's reading.** `laws/surface_check.py` now routes every
one of the three through `keys_once`, and `packs/poison` carries `b2_q1_ending_act_twice.py`,
`b2_q1_ending_outcome_twice.py` and `b2_q1_terminal_act_twice.py`. The differential in
`tests/test_surface_differential.py` no longer records a single divergence of this shape. The
finding, as it was made against the checker of kit v0.3:

**The page.** SURFACE §2, last paragraph: *"A key written twice in one dict, or a state listed twice
in a `data` file, is refused."*

**The reference.** `Checker.table` enforces it — a state written twice in `prior` is `DUPLICATE` —
but `Checker.d_utility` builds `T` and `ending` with dict comprehensions straight off the syntax
tree, so the rule is not enforced for a terminal act, an ending act, or an ending outcome. The last
key silently wins and the pack elaborates.

**The pack.** The appendix pack with one word changed: `leave` renamed to `treat`.

```python
world("p", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
space({"health": ["sick", "well"]})
prior({"sick": 1/5, "well": 4/5}, source="data")
utility({"treat": {"sick": 0, "well": -2}, "treat": {"sick": -10, "well": 0}}, source="elicited")
price({"test": 1/2}, source="elicited")
act("test", once=True, kernel=table({"sick": {"+": 9/10, "-": 1/10}, "well": {"+": 1/5, "-": 4/5}}, source="data"), reads=["health"])
```

`surface_check.check` **accepts** this, with `T = ['treat']` carrying the *second* table: a pack has
lost a terminal act and its utility, silently, and the menu it declared is not the menu it gets. The
same holds for `ending={"cat": {...}, "cat": {...}}` and for an outcome written twice inside one
act's `ending` (both shown against `packs/ok/wordle_mini.py`).

**What I did.** Followed the page: all three are `DUPLICATE`. No corpus pack writes a key twice, so
R2 and R3 are unaffected either way; `tests/test_surface.py` keeps all three cases.

---

## Q2 (brief 002). `param` may not be named after a declaration, which the page does not say

**Status:** as Q1 — recorded, and the page implemented.

**The page.** SURFACE §2, `param` row: *"The name is an identifier that is not a Python keyword; it is
declared once and read by cells declared after it."*

**The reference.** `d_param` refuses the name if `not nm.isidentifier() or keyword.iskeyword(nm) or
nm in DECLS` — that last clause is a third condition the page does not state. `param("world", …)`,
`param("act", …)`, `param("price", …)` are all `BAD_NAME` there.

**The pack.** The appendix pack with `param("world", 1/10, source="elicited")` added and the
parameter read in a cell. `world` is an identifier and is not a Python keyword, so by the page it is
a lawful name; `surface_check` refuses it `BAD_NAME`.

**What I did.** Followed the page: accepted. Nothing in a pack can confuse the two — a declaration is
a top-level call, a parameter is a name inside a cell, and the grammar gives a cell no calls at all.
If the author prefers the reference's rule, the page wants one more clause in the `param` row, and I
will add it.

---

## Q3 (brief 002). A pack with no `space` crashes `laws/surface_check.py` instead of being refused

**Status: closed — the kit adopted the page's reading.** `laws/surface_check.py` raises `MISSING`
now, and `packs/poison/b2_q3_no_space.py` pins it. The finding, as it was made:

**The page.** SURFACE §2: `space` is one of the seven declarations that "appear exactly once", and §5
gives `MISSING` for a declaration a pack must make and did not.

**The reference.** `Checker.spec` does raise `MISSING("space")` — but only if it is reached. `d_act`
and `d_utility` run first, and `comp()` reads `self.space`, which `d_space` is the only thing that
ever sets. So a pack that declares an act and no space raises `AttributeError: 'Checker' object has
no attribute 'space'`, which is not a `Refused` at all: `kit_surface.verdict` reports it as
`raised AttributeError`, and a pack author gets a traceback instead of a name.

**The pack.** Any lawful pack with its `space(...)` line deleted — all twelve of `packs/ok` do it,
which is how I found it: a fuzz over 2,748 one-line mutations of the corpus produced exactly two
kinds of difference between this kernel and the reference, this one (34 of them) and Q1 (one).

```python
world("p", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
prior({"sick": 1/5, "well": 4/5}, source="data")
utility({"treat": {"sick": 0, "well": -2}, "leave": {"sick": -10, "well": 0}}, source="elicited")
price({"test": 1/2}, source="elicited")
act("test", once=True, kernel=table({"sick": {"+": 9/10, "-": 1/10}, "well": {"+": 1/5, "-": 4/5}}, source="data"), reads=["health"])
```

**What I did.** Followed the page: `MISSING`, raised the moment a component is asked for before the
space is declared, in the same voice as the prior's (`"prior: every table over states comes after the
prior"`). No corpus pack omits `space`, so R2 and R3 are unaffected.

---

## Q4 (brief 005a). A negative Rate is forbidden by CHARTER v0.1 §1 but no clause is named for it

**Status: answered — `RATE`.** The author has ruled, in brief 005b's charter. `charter/ERRATA.md`,
under *Queued for CHARTER v0.2*: *"§1 of v0.1 names no clause for a Rate below zero, though it
writes r ∈ ℚ≥0. Found by the builder in brief 005a (`QUESTIONS.md` Q4, with the World). Reading in
force meanwhile: a negative Rate is refused by the name RATE, the name the row already gives the
Rate's source; SURFACE v0.1 says so, `meta_check.refuse_meta` moves to it at kit v0.8, and the
kernel's one string follows in brief 005b. No act changes."* SURFACE v0.1 K15 is the ruling:
*"where CHARTER v0.1 has none (r below 0) the surface supplies RATE, and CHARTER v0.2 is to adopt
it."* `src/wald/world.py` moved the string in brief 005b, and `tests/test_think.py` pins it.

The record below is what was asked and why, kept as it was written.

---

**The page.** CHARTER v0.1 §1: *"Rate r ∈ ℚ≥0, utility per operation: the owner's exchange rate.
Housed; its source is `elicited`, any other is refused by the name RATE."* The sentence names
`RATE` for the **source** and says nothing about the name for a value below zero. S6 names
`FRACTION` and `COST` for the two meta-beliefs' values, and r is neither: it is the owner's price,
not a belief about the agent's computation.

**The reference.** `laws/meta_check.refuse_meta` refuses it, with the Cost table, in one line:

```python
if world["rate"] < 0 or set(world["ops"]) != set(range(1, len(world["prior"]) + 1)) \
        or min(world["ops"].values()) < 0:
    raise Refused("COST")
```

`laws/INTERFACE.md`'s kit v0.7 section glosses the two names the other way — `COST` as "a missing
or negative cell", `RATE` as "a rate whose source is not `elicited`" — and so names nothing for a
negative rate at all. `kit_think.refusal_cases()` does not test it, so the kit is green under
either reading.

**The World.** Appendix A with one number changed:

```python
{"prior": {"sick": F(1, 5), "well": F(4, 5)}, "T": APPX_T,
 "O": {"test": act(APPX_K, F(1, 2), False)},
 "N": 2, "d": 1, "dplus": 2, "fraction": F(1, 2), "rate": F(-1, 1000),
 "ops": {1: F(100), 2: F(200)}}                      # r < 0: the owner is paid to think
```

**What I did.** Took the reference's name, `COST`, since INTERFACE calls `meta_check.py` the
reference and the definition for kit v0.7 — as this kernel took `PRICE` and the `fresh` half of
`SHARED_SOURCE` under kit v0.1, both of which kit v0.2 then adopted. If the author prefers `RATE`
to cover the Rate table's value as well as its source, the §1 row wants the same half-sentence the
Fraction and Cost rows have, and I will move it.

**What happened.** The author preferred `RATE`, and the §1 row is to get that half-sentence at
CHARTER v0.2. Moved in brief 005b; no act of any World changed with the name, as expected.

---

## Q5 (brief 006). The brief puts ten names in `wald.__all__`; kit v0.10's ST1 allows six

**Status: answered at kit v0.11** (ST1 allows the ten and `plate`; brief 007 item 8). `__all__`
lists all eleven. The record below is kept as it was.

**The brief.** `briefs/006-library.md` item 3: *"`src/wald/__init__.py` exports `load_pack`
(= `surface.check`), `from_json`, `to_json`, `law` beside the existing six names; `__all__` lists
all ten."*

**The page.** `laws/INTERFACE.md`, the structural surface (kit v0.1): *"`wald.__all__` ⊆
`{declare, run, Door, report, Display, refusals}`."* The kit v0.10 section says `import wald`
*exposes* the six "and three more" (it then names four), and does not amend the first section.
`kit_structural.py` at `kit-v0.10` still has `ALLOWED_TOP` = the six, and ST1 is `top <= ALLOWED_TOP`.
`kit_library.py` L1 checks `hasattr(wald, n)` for the ten and never reads `__all__`.

**The World that exposes it.** Not a World: the package itself. With `__all__` as the brief gives it,

    FAIL ST1 wald.__all__ exports nothing beyond ['Display', 'Door', 'declare', 'refusals', 'report', 'run']   ['from_json', 'law', 'load_pack', 'to_json']
    structural: 36/37 pass

and the cage is red; with `__all__` the six, both kits are green.

**What I did.** Nothing I chose: the kit is the judge, so the four names are bound on `wald`
(which L1 asks) and left out of `__all__` (which ST1 asks). `src/wald/__init__.py` says so in a
comment pointing here, and `tests/test_library.py` and `tests/test_violators.py` pin the six. If
the author means the ten, `ALLOWED_TOP` wants the four more (and INTERFACE's first section the same
words); it is a one-line change on my side.

---

## Q6 (brief 006). `WIRE` is named for "a reply out of order"; a malformed wire spec has no name

**Status: open, a reading taken; the kit is green under any reading.**

**The page.** `laws/INTERFACE.md`, kit v0.10: *"An unknown op answers `{"refused":"UNKNOWN_OP"}`;
an unknown world id `{"refused":"UNKNOWN_WORLD"}`; a reply out of order is `WIRE`."* It says every
rational on the wire is `"p/q"`, and names nothing for a spec that is not INTERFACE's dict — a
rational written as a JSON number, a key the dict does not have, a count written `"2"`, a line
that is not JSON. `kit_library.py` sends none of these.

**The Worlds.** Appendix A as `kit_library.wire_spec` writes it, then one change each:

```python
spec["prior"]["sick"] = 0.2      # a float where a rational is meant
spec["dplsu"] = 2                # a misspelt Depth+: ignored, it would declare a v0 World
spec["N"] = "2"                  # a count as a string: `declare` crashed on it with TypeError
```

**What I did.** A float or a decimal string (`0.2`, `"0.2"`, `"1e-3"`) is `FLOAT`, SURFACE §5's
name for "a decimal, where only exact rationals are meant", which is exactly the fault. Everything
else the wire can get wrong — not JSON, not an object, a missing or unknown key, a JSON type
INTERFACE does not give, a reply with the wrong id or key — is `WIRE`, read as the wire's refusal
in general, of which a reply out of order is one case. An unknown key is refused rather than
ignored because ignoring it turns a misspelt `dplus` into a v0 World without a word. If the author
wants these apart, they are names in `src/wald/wire.py` and `tools/serve.py` and nowhere else.

---

## Q7 (brief 007). `wald.law["charter"]`: L1 asks `charter-v0.1`, and CHARTER v0.2 is signed

**Status: open. The kit's reading is taken; the kit is green.**

**The page.** INTERFACE, kit v0.10: `law` is *"a dict naming the signed tags and the kit tag this
package conforms to"*. Brief 007 implements `charter-v0.2`. `kit_library.py` L1 still asks
`law["charter"] == "charter-v0.1"`.

**The World that exposes it.** Not a World: `echo '{"op":"hello"}' | python3 tools/serve.py`
prints `{"charter": "charter-v0.1", "surface": "surface-v0.1", "kit": "kit-v0.11"}` from a package
that implements CHARTER v0.2.

**What I did.** `law.CHARTER` stays `charter-v0.1` (L1) and `law.KIT` follows the lock. If the
dict should name the newest charter this package conforms to, it is one string in
`src/wald/law.py` and one in L1.

---

## Q8 (brief 007). The After-act's kernel "for every end": the page counts ending outcomes, `counts_check.refuse` does not

**Status: open. The page's reading is taken; no kit World has both an ending outcome and an After-act.**

**The page.** CHARTER v0.2 §3, After-act: *"taken once the episode has ended — the end being the
terminal fired, or the pair (act, outcome) of the ending outcome reached — with kernel
K_after(o | ω, e) reading the state and the end e, declared for every end"*. S12 refuses *"an
after-act kernel [that] omits an end"* as AFTER.

**The reference.** `counts_check.refuse` refuses AFTER unless `set(W["after"]["K"]) == set(W["T"])`,
so it asks a kernel for each terminal, and refuses one keyed by an ending end `"end:k=o"`. Then
`record_lik`, `diagnostic` and `plate_value` read `W["after"]["K"][t]` with `t = "end:k=o"` for an
episode that ended on its ending outcome, and raise KeyError. `designs` and `design_dist` never cut
a design at an ending outcome, although S15 says *"an ending outcome ending it"*.

**The World.** Appendix A with a second `once` act `peek`, free, emitting `drop` (an ending
outcome, u_end 0) or `go` with 1/2 each, and N = 2:

```python
W = counts_check.reliability_world([F(9, 10), F(3, 5)], [F(1, 2), F(1, 2)], F(-2))
W["O"]["peek"] = {"K": {(l, g): {"drop": F(1, 2), "go": F(1, 2)} for l in ls for g in gs},
                  "price": F(0), "once": True, "ends": {"drop"}, "u_end": {"drop": F(0)}}
W["N"] = 2
```

The reference accepts it with no kernel for the end `end:peek=drop`. A plate on it that draws
`drop` has no After-kernel to grade under. With `W["after"]["K"]["end:peek=drop"]` added, the
reference refuses it AFTER.

**What I did.** The page: `plated.build` asks for a kernel at every terminal and at every
`end:k=o`, and refuses AFTER otherwise. `disclose.py` cuts a design at an ending outcome.
`tests/test_counts.py` holds both halves. On a World with no ending outcome, which is every World
the kit draws, the two readings are the same.

---

## Q9 (brief 007). The falsifying record of a report inside an episode has no end, and S13 checks it as a record

**Status: open. The stand-in's reading is taken; the kit does not ship such a falsifier.**

**The page.** J26: a report that falsifies the World *"during the episode or after it"* ends the
plate, *"the falsifying record is kept beside them and travels with them"*. S13: *"Counts shipped
from a plate that ended WORLD_FALSIFIED carry its falsifying record, which PLATE checks with them"*
— checks that *"the declaration could have written every record itself … an ending outcome only as
the last draw and then as the end, an after-report exactly when an After-act is declared"*.

**The World.** Appendix A. Episode 1 reports `a1`, graded `a1`. In episode 2 the door reports `a3`,
which `ask` cannot emit. The plate ends, and its falsifying record is the episode up to that
report. There is no end, because no terminal was fired, and no after-report. `kit_counts._RefWald`
writes `((("ask", "a3"),), None, None)`, and so do I. Shipped with the Counts into a refit, that
record fails `counts_check.realisable` (its end is neither a terminal nor `end:k=o`, and appendix
A declares an After-act), so the refit is refused PLATE. Every falsifier from inside an episode is
unshippable, although J26 says it travels.

**What I did.** The stand-in's record, and the reference's `realisable` applied to it unchanged, so
such a shipment is refused PLATE. Also open under the same J26: whether `Plate.falsifier()` of a
plate that started from shipped Counts and their falsifier should return that shipped falsifier.
Mine returns only the plate's own; the shipped one is in the evidence of every episode's prior.

