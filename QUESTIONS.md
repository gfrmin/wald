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

**Status: answered in brief 008** (the owner's numbers): `wald.law` is `{"charter": "charter-v0.2",
"surface": "surface-v0.2", "kit": "kit-v0.12"}`, and kit v0.12's L1 asks exactly that. The record
below is kept as it was.

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

**Status: answered at kit v0.12, the page's way.** `counts_check.ends_of` asks a kernel for each
terminal and each `end:k=o`, and SURFACE v0.2 V2.5 writes it: rows for exactly the ends. The record
below is kept as it was.

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

**Status: answered at kit v0.12:** SURFACE v0.2 V2.7 makes a prefix `[draws, None, None]` a
falsifying record, `counts_check.realisable` accepts it, and K7 checks it ships. The second half
below -- what `Plate.falsifier()` returns on a plate that was shipped falsifiers -- INTERFACE's kit
v0.12 section does not say; mine still returns only the plate's own. One case of the first half is
still open: Q15.

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


---

## Q10 (brief 008). The After-act's kernel and price: five rules of the pages `surface_check` does not apply

**Status: open. The pages' readings are taken; no corpus pack breaks any of them, so the kit is green either way.**

**The pages.** V2.5: the After-act is `after(name, kernel=table({end: {state: {outcome: p}}}, source=…), reads=[…])`,
"a kernel with rows for exactly the ends … each with a row for every state", and "a price, the cell of `price` under
its name". SURFACE v0 §4: "Every row of probabilities is checked where it is written: each cell non-negative, each
row summing to 1 — in a `table` …" (`KERNEL_ROW`). SURFACE v0 §2, which V2.4 carries to every table over states:
"exactly the states of Ω as its keys, no fewer and no more"; "a key written twice in one dict … is refused".
CHARTER v0 §1: price : O → ℚ≥0; CHARTER v0.2 §3: "Price's domain is O and the After-act". C2.S12: a pack "which
declares ⊥ and gives some after-outcome probability 0 at ⊥, is refused by the name AFTER".

**The reference.** `Checker.d_after` reads the kernel with `table(…, 3)` and never calls `rows_ok`; `spec_v02` pops
the After-act's price before `validate`, so no price rule sees it; `counts_check.refuse` asks only that every end's
rows cover Ω. Each pack below is **accepted**:

| | the pack | reference | mine |
|---|---|---|---|
| a | `monitor_all_global.py` with `"pass": 9/10` → `"pass": -9/10` (a row of −9/10 and 1/10) | a World | `KERNEL_ROW` |
| b | `appendix_a.py` with `("a3", "9/10"): {"a1": 1},` added to the `"abstain"` rows | a World | `TABLE_SHAPE` |
| c | `appendix_a.py` with `"grade": 0` → `"grade": -1` in `price` | a World | `PRICE` |
| d | `after_without_globals.py` with `closed=True` → `bottom=("a1", "9/10")` (`grade` gives `a2` no mass there) | a World | `AFTER` |
| e | `tests/test_learned.py`'s `PEEK` (Q8's `peek`) with both `("peek", "drop")` and `"end:peek=drop"` rows | a World, the second row silently replacing the first | `DUPLICATE` |

And one the other way round: (f) `appendix_a.py` with the after-outcomes under `"say a2"` written as tuples,
`{("a1", "x"): 1}`, is accepted by the reference and by me — and `model.check_world` of the reference's own dict raises
`ShapeError: an after-outcome is a name`. No record could hold such an after-report (V2.6), so the plate would
write records no digest can encode.

**What I did.** (a)–(e): the pages' names, each message citing this entry. (f): accepted, as the reference does; if
tuple after-outcomes are unsayable, V2.5 wants the words and the refusal is one line in `learned.py`.

**Which gate check.** `model.check_world` checks types; checking values too — every row a distribution, every table
over states keyed by exactly Ω, every price at least 0, After-act included — would have caught (a)–(d) on the
corpus's mutations; (e) is Q1's class again, one level down.

---

## Q11 (brief 008). A Global value the prior does not name: lawful by V2.3 and V2.4, a crash in the reference

**Status: open. The page's reading is taken.**

**The page.** V2.3: `local_prior` "has one row for exactly the Global values the prior names" — so a prior may name
fewer than the space holds. V2.4: "The states are the pairs (local, Global) to which V2.2 and V2.3 together give
positive probability." As SURFACE v0 K10 has it for states, a value the prior leaves out is not in Ω.

**The pack.** `appendix_a.py` with its space written `"rel": ["9/10", "3/5", "1/2"]` and nothing else changed.

**The reference.** `raised KeyError ('1/2',)`: `counts_check.refuse` loops over every Global value of the space and
reads `W["prior_local"][g]` for each (and so do `classes`, `design_dist`, `post_global`).

**What I did.** Accepted: Ω is the four states the prior names, as in appendix A. `plated.build` takes the Global
values from P(Global), refuses one outside the space, and requires `prior_local` rows for exactly those.

**Which gate check.** An invariance: adding a value to a component, which the prior does not name, changes no
verdict, act or belief — K10's rule, as `invariance_check.py` already pads with a one-valued component.

---

## Q12 (brief 008). `score(of="counts")` in a pack with nothing to score is accepted, the Score dropped

**Status: open. The page's reading is taken.**

**The page.** V2.8: "`score(value, of="counts", source="data")`, only with `counts` … Refused MISSING".

**The pack.** `appendix.py` (SURFACE v0's appendix) with `score(1, of="counts", source="data")` appended.

**The reference.** Accepts it. `Checker.spec` goes to `spec_v01` for a pack with no `globals`, `after`, `counts` or
`falsifiers`, and `spec_v01` never looks at `counts_score`; only `spec_v02` refuses it. The corpus's poison
`v02_score_of_counts_without_counts.py` declares Globals, so it takes the other road.

**What I did.** `MISSING`, citing this entry: a pack that writes any of the v0.2 declarations, `score(of="counts")`
included, is read as SURFACE v0.2's.

**Which gate check.** `page_check.py`'s traceability counts poisons per rule; one per route through the checker —
with Globals, V2.9's World with none, and a v0 pack — would have found it.

---

## Q13 (brief 008). `falsifiers` before `counts`: V2.7 states no order, the reference requires one

**Status: open. The page's reading is taken.**

**The page.** V2.7: "`falsifiers([[draws, end, after], ...])`, only with `counts`". Where this page means an order it
says so: V2.1 "It comes after `space` and before `prior`", V2.3 "It comes after `prior`". SURFACE v0 orders only
tables over states after the prior, and a parameter before the cells that read it.

**The pack.** `falsified_refit.py` with its `counts(…)` and `falsifiers(…)` lines swapped.

**The reference.** `MISSING: [V2.7] counts: falsifying records travel with the Counts they ended` —
`d_falsifiers` asks whether `counts` has been *seen*. `score(of="counts")` before `counts` it accepts.

**What I did.** Accepted, the same World as the pack as written; `falsifiers` with no `counts` anywhere is `MISSING`
when the pack is complete. The differential test allows the reference's order-refusal by this entry.

**Which gate check.** The mutation differential in `tests/test_surface_differential.py` swaps neighbouring lines of
every corpus pack; run against the page's stated orders it separates "refused by order" from "refused by absence".

---

## Q14 (brief 008). A record whose end names an ending outcome its draws never reach

**Status: open. The rule's own words ("could have written every record itself") are taken over its list.**

**The page.** C2.S13: "the declaration **could have written every record itself** under v0's episode mechanics …
— its acts and end declared here, at most N draws, each `once` act at most once, an ending outcome only as the last
draw and then as the end, an after-report exactly when an After-act is declared". V2.7 leaves this to C2.S13.

**The World.** Q8's: appendix A with a free `once` act `peek` whose outcome `drop` ends the episode, N = 2, and an
After-act row for `end:peek=drop`. Shipped Counts: one record `((), "end:peek=drop", "a1")` — no draw at all, yet it
ends at `peek`'s ending outcome.

**The reference.** `counts_check.realisable` returns True (every item of the list holds: `end:peek=drop` is an end,
no draw breaks a rule), and `refuse` accepts the shipment with its digest and Score. No run of v0's loop writes that
record: an episode ends at `end:peek=drop` only by drawing `drop` from `peek` last.

**What I did.** `PLATE`: `counts.realisable` also asks that an end which is not a terminal be the ending outcome
drawn last (`tests/test_learned.py`, Q14).

**Which gate check.** Realisability checked against the loop itself: a record is realisable iff some design and
outcome sequence of `counts_check.designs` and `_walk` — the enumeration S15 already uses — produces its draws and end.

---

## Q15 (brief 008). A prefix falsifier whose falsifying report is an ending outcome can never travel

**Status: open. Both checkers refuse it; J26 says it travels.**

**The page.** V2.7: a falsifying record is "a prefix `[draws, None, None]` ending at the report that falsified". The
loop checks zero mass before it checks an ending outcome (v0.1 §2: "if P_b(o|a) = 0 the episode ends as
WORLD_FALSIFIED; else …; then if o is an ending outcome the episode ends"), so a report of zero mass that is also an
ending outcome falsifies, and its prefix ends with it. C2.S13: "an ending outcome only as the last draw **and then as
the end**" — and a prefix has no end. J26: the falsifying record "is kept beside them and travels with them".

**The World.** Appendix A with its one act `peek` reporting the answer with the reliability and `drop` — an ending
outcome — with mass 0 in every state (so `drop` is in B_k, lawful), an After-act row for `end:peek=drop`. A plate
whose door reports `drop` ends `WORLD_FALSIFIED` with `falsifier() == ((("peek", "drop"),), None, None)`.

**The reference, and mine.** `counts_check.realisable(W, f, falsifier=True)` is False, so shipping it is `PLATE`;
mine is the same. The falsifier the plate itself wrote cannot be shipped into the very declaration that wrote it.

**What I did.** Nothing different from the reference: the question is which of V2.7 and C2.S13's "then as the end"
decides.

**Which gate check.** A round trip: every falsifier the reference plate (`kit_counts._RefWald`) writes is shippable
into its own declaration.

---

## Q16 (brief 008). V2.11's text: which comment is a coding declaration, and a byte-order mark

**Status: open. The reference's readings are taken for (a); Python's parser's for (b).**

**The page.** V2.11: "A coding declaration naming another encoding … is refused NOT_A_DECLARATION." Python's
language reference defines one: a comment on line 1 or 2 matching `coding[=:]\s*([-\w.]+)`, "If it is the second
line, the first line must also be a comment-only line."

**(a) The pack.** `appendix_a.py` without its two comment lines, and `# coding: latin-1` inserted as line 2, after
`world(…)`. By Python's definition this is no coding declaration; the reference refuses it (`_plain_text` scans the
first two lines of `splitlines()`, whatever line 1 is — and `splitlines` also breaks lines at `\f`, `\v`, `\x1c`–`\x1e`,
`\x85`, U+2028 and U+2029, which Python's tokenizer does not). Mine refuses it too: I follow the reference.

**(b) The pack.** `appendix_a.py` preceded by U+FEFF, which is what a UTF-8 file with a BOM decodes to. The reference:
`NOT_A_DECLARATION: an identifier is ASCII; '﻿' would be folded` — `tokenize` reads `﻿world` as one name.
Python's parser: `SyntaxError: invalid non-printable character U+FEFF`; U+FEFF is not an identifier character. Mine
says `SYNTAX`. One fault, two names; K7 promises one rule's name for one fault.

**Which gate check.** `invariance_check.py`'s hostile renaming reaches every name; the same for the text around the
names — a comment line moved, a BOM added — would have shown both.

---

## Q17 (brief 008). Four v0.2 packs make `surface_check` raise instead of refuse

**Status: open. Not a reading: a crash is not a verdict (Q3).**

| the pack | reference | mine |
|---|---|---|
| `appendix_a.py` without its `price(…)` line | `AttributeError: 'Checker' object has no attribute 'prices'` (`spec_v02` reads the After-act's price first) | `MISSING` |
| `appendix_a.py` with `after(…)` moved before `space(…)` | `AttributeError: … 'space'` (`d_after` reads `self.space`) | `MISSING` |
| `appendix_a.py` with the think act's four declarations, `cost` before `local_prior` | `AttributeError: … 'prior'` (`d_cost` reads `len(self.prior)`) | `MISSING` |
| `appendix_a.py` with a raw U+D800 in a name, handed over as a `str` | `UnicodeEncodeError` (`ast.parse` encodes before `_plain_text` looks) | `NOT_A_DECLARATION` |

And Q11's `KeyError`. The first is 27 of the 13,445 mutations in `tests/test_surface_differential.py`.

**Which gate check.** That differential, run by the gate against the reference alone: any exception that is not
`Refused` on a mutation of the corpus fails the gate.
