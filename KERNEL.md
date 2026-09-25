# KERNEL.md — every module, and its one reason to exist

The kernel of CHARTER v0 and SURFACE v0, of their amendments v0.1, and of their amendments v0.2. Twenty-six
modules; if one of them cannot keep its line here, it should not exist. Standard library only, exact rationals
only, and the list in `cage/lint_imports.py` is the whole of what `src/wald` may import.

## The fourteen names a host gets

`import wald` is the whole of the library (brief 006; `API.md` is the consumer's page). What a
host may have from each name, and what it may not:

| name | a host gets | a host does not get |
|---|---|---|
| `declare` | a sealed World, or `Refused` by name | a World built past a refusal |
| `run` | a Result: acts, outcomes, status, prices and thought paid, S7's counts, E6's counts, the final Belief | the belief's weights: `final` is sealed |
| `Door` | the class to subclass: `outcome` and `fire` are the host's | a way to mint an Obs other than `observe` |
| `report` | a `Display` of a belief, and of E6's counts beside it | a number — the text is inert (S1) |
| `Display` | `str()` | comparison, arithmetic, truth, hashing, length, indexing |
| `refusals` | the exception classes and every refusal name | — |
| `load_pack` | a pack's World spec, the pack parsed and never run | anything a pack could execute |
| `from_json` | the wire's spec as INTERFACE's dict, rationals exact | a float: the wire refuses one as `FLOAT` |
| `to_json` | a Result as text, rationals as `"p/q"`, the belief as `report`'s text | the belief as values: `wire.py` never opens a Belief |
| `law` | the signed tags and kit tag this package was judged under | — |
| `plate` | a Plate over a declared World: `run(door)` one episode at a time, its Counts, its falsifying record, S15's disclosure as a `Display` | P(Global \| Counts): Counts are facts a host may hold, the belief they give is not |
| `digest` | V2.13's digest of Counts and falsifying records, the hex a pack writes | — it is a name, not a numeral (V2.12) |
| `score` | V2.8's Score as a pack writes the cell, `"p/q"` text in decimal digits however many | a Fraction: the Score is a measurement a pack writes and `declare` checks, not a number a host acts on |
| `e7` | E7's lines as a `Display`, each an exact rational | the lines as values (S1) |

`__all__` lists all fourteen (ST1 as of kit v0.13). With `plate`, the last three are what a host
needs to write the pack that ships its Counts without the kit (brief 009, API.md's worked example).

Not among them: `push`, `condition`, `expect`, `decide`, `step`, `Belief`. A host never holds a
probability and never chooses (S1, E5). The submodules are reachable, as anything in Python is;
they are the kernel's, and nothing in `API.md` names them.

| module | why it exists |
|---|---|
| `wald/__init__.py` | the host's whole surface, the fourteen names above — and not the verbs, so a host never holds a probability and never chooses (S1, E5) |
| `wald/refusals.py` | `Refused` carries the **name** of the clause that refused a pack, so a refusal says which rule spoke; `WorldFalsified` and `ObsSpent` are the two things the kernel refuses at run time (S5, S2) |
| `wald/dist.py` | the one place mass is checked to sum to one, so a row that does not (S4) cannot come into existence anywhere else |
| `wald/kernels.py` | `Kernel`, and the only five ways to build one — point, table, mixture, product, composition — each preserving row sums by construction (S4) |
| `wald/world.py` | `declare`: the World of §1 with its tables and their `data`/`elicited`/`fitted` tags, and every validation that refuses a pack by name before anything runs — `build` is that without the rulings, for the kit's probes |
| `wald/obs.py` | the Obs token, minted only by a door and consumed by exactly one `condition`; a token is not a record to be read twice (§1, S2) |
| `wald/display.py` | `Display`: it renders and does nothing else, so a display value cannot reach control flow or a belief (S1) |
| `wald/belief.py` | the sealed `Belief` and the verbs allowed to touch it — `prior`, `push`, `condition`, `expect`, `report`; the belief update of §2 is written once, here, and so is E2's unnormalised stand-in for the three of them, and so is the operation counter that watches it (v0.1 E6) |
| `wald/decide.py` | the one `decide`: V₀, Qₙ, Vₙ and the argmax exist here and nowhere else (E5), with E2's fast paths underneath them — and `step`, v0.1's `decide⁺`, which is that same argmax over a menu with θ on the end of it (S8) |
| `wald/same.py` | which acts a belief cannot tell apart, so the lookahead evaluates one of each group and J3 takes the first (E2) — it decides sameness and never a value |
| `wald/episode.py` | `Door` and `run`: the episode of §2 in the page's order, the only place a think act is charged and its operations read, and — through `step` — the only place the floor `min(d, n)` is applied (E3) |
| `wald/kit_adapter.py` | the `laws/INTERFACE.md` shim: plain dicts in, kernel types out, no logic of its own |
| `wald/plated.py` | CHARTER v0.2's World: Ω as locals × Globals around a v0 World over the pairs (l, g), the Prior's two factors, the After-act, shipped Counts and their falsifying records — and GLOBAL, AFTER, PLATE, UNSCORED |
| `wald/counts.py` | the prior from Counts — `belief._update` once per distinct record, the record's likelihood to its count, so it is v0's update and not a second one — S13's realisability as v0's loop has it (a prefix falsifier may end at an ending outcome, since the loop checks zero mass first: Q15), falsifying records as V2.7 has them, **S14's Score as V2.8 corrects it** (a term for every copy of every record *and every falsifying record*) and E7's lines |
| `wald/canonical.py` | SURFACE v0.2 V2.13: the digest defined by its bytes — V2.13's escape table as a declared table, row for row, the first matching row deciding, so DEL is escaped and `/` is not because the page says so and not because a JSON library does |
| `wald/disclose.py` | S15: the Global values no realisable design separates, and the classes of them that settle something an act can feel; it refuses nothing |
| `wald/ship.py` | the three names a host ships Counts with — `digest`, `score` written as a pack writes it, `e7` as a `Display` — each a conversion around `canonical`, `counts` and `digits`, so a host needs no kit (brief 009) |
| `wald/digits.py` | whole numbers of any length read from and written to decimal digits a piece at a time, so a Score of tens of thousands of digits is read and written without lifting Python's interpreter-wide limit on integer conversion, which the kernel never touches |
| `wald/plate.py` | `Plate`: its Counts and its falsifying record and nothing else; one episode is the prior from Counts, `episode._play` unchanged, the After-act asked by name after the fire, the record in (S12, S13, J26) |
| `wald/cells.py` | SURFACE §3: what a number may be, where it is housed, the `fitted` fence, the census of quantities by source, and v0.1's K16 provenance — what sources a cell descends from, so a meta-table cannot be handed one it could not have declared |
| `wald/datafile.py` | SURFACE K5: a kernel's rows read from a JSON file beside the pack, pinned by the SHA-256 of its bytes — the only file the kernel ever reads |
| `wald/law.py` | the three tags this package was judged under, in one place, so a consumer can print which law its wald obeys and the kit can hold it to the lock |
| `wald/wire.py` | `from_json` and `to_json`: the World spec and the Result as JSON text, every rational `"p/q"` both ways, read by position so a name spelled like a number stays a name — and the belief out only as `report`'s text (S1) |
| `wald/surface.py` | SURFACE §1, §2 and §4: the nine declarations and the seven kernel forms, parsed with `ast` and never executed, elaborated to a World spec — and SURFACE v0.1's five more, `depth_plus`, `think`, `cost`, `rate` and `score`, which come together or not at all |
| `wald/learned.py` | **the v0.2 reader**: SURFACE v0.2's `globals`, the prior as P(Global), `local_prior`, `after` with its `reads`, `counts`, `falsifiers` and `score(of="counts")`, read into CHARTER v0.2's dict — the joint World judged as any pack's, then the dict judged by `plated.declare` |
| `wald/text.py` | SURFACE v0.2 V2.11: a pack's text before it is parsed — UTF-8 with LF, no coding declaration but UTF-8, no surrogate, no identifier outside ASCII — so that one pack's bytes are one pack to every reader; and a decimal literal too long for Python to read, swapped for a fresh name before parsing and its digits kept for `cells.py` |
| `tools/wald_check.py` | outside `src/`: `python3 tools/wald_check.py pack.py` — the write, check, repair loop for every pack author; it reads the pack's bytes as written (V2.11) |
| `tools/make_wordle_pack.py` | outside `src/`: writes a Wordle pack from one of the charter's word lists at a given depth, the game's feedback rule included — and, with `--think`, the five declarations of SURFACE v0.1 |
| `tools/play_wordle.py` | outside `src/`: plays every answer of one or more packs through `wald.episode.run` behind a door that is the game, and writes the scoreboard — S7's four buckets, the thought charged and E6's two operation counts included |
| `tools/serve.py` | outside `src/`: the wire as a process — JSON lines on stdin/stdout, the server the kernel's side of the Door and the client the world's; every client error refused by name, and all of the kernel's I/O is here; a World of CHARTER v0.2 loads over it but does not run, because the wire has no plate op |
| `tools/curves.py` | outside `src/`: CHARTER E3 when thinking has a price — the five policy values along a grid of rates, exactly, from the kernel's own acts |

## The three things that exist exactly once

- **The choice.** `decide.py`. The argmax, the lookahead and the episode loop's call to it. Packs and
  fast paths supply beliefs and values, never acts (E5, J10).
- **The belief update.** `belief._update`. The public verb `condition` is that plus the token; the
  adapter is that without one, because the kit hands it raw outcomes rather than minted Obs.
- **The floor.** `decide.step`, as `min(world.d, n)`, called by `episode.run` and by nothing else.
  `decide` is always exactly decide_n: an evaluator is compared with the reference *at the same d*
  (E3), so the depth is never baked into it. The floor moved from the loop into the step when v0.1
  gave the step a second depth to weigh, because ĝ reads the raw n and the value reads the floored
  one.

## The refusals, and one reading that had to be chosen

`declare` refuses a pack by the name of the clause it breaks: `EMPTY_T`, `PRIOR`, `KERNEL_ROW`,
`PRICE`, `DEPTH`, `ZERO_EVIDENCE`, `TABLE_SOURCE`, `TABLE_SHAPE`, `SHARED_SOURCE`. (`PRICE` and the
`fresh` half of `SHARED_SOURCE` were this kernel's readings under kit v0.1; kit v0.2 adopted both.
A negative Rate was `COST` under kit v0.7, on the same grounds; SURFACE v0.1 K15 named it `RATE`
instead, and it has moved — QUESTIONS.md Q4.)

`TABLE_SHAPE` says a table over Ω is a function on Ω — defined at every state and at no other — and
that an ending outcome is an outcome of its own act. Four packs are refused by it: a terminal
utility, a kernel or a u_end that is not total over Ω, and an ending outcome the kernel cannot emit.

**"Cannot emit" is "not in B_k", not "has no mass".** An outcome declared in the kernel's rows with
mass zero in every one of them is in B_k: the pack has said what it is worth, the sums of §2 skip it
(`Σ_o` runs over outcomes of positive mass), and no belief can ever reach it — but the declaration is
lawful, and S5 is what speaks when such an outcome is nonetheless observed. The stricter reading
would refuse lawful packs, including ones the kit itself draws, now that its generator builds kernel
rows from 0, 1, 2, 5 and 12. `tests/test_violators.py` keeps both halves of this.

## A pack is read, never run

`surface.py` parses with `ast` and walks the tree. Nothing in `src/wald` calls `eval`, `exec`,
`compile` or `__import__` — the lint forbids all four, and `open` besides, so the one file the kernel
reads goes through `pathlib` in `datafile.py`. A pack that says `import os` or `pathlib.Path(x).unlink()`
is refused as the text it is; `tests/test_surface.py` checks that by leaving a file in place.

The unhoused numerals and unread parameters of CHARTER S3 now have their home: a number lives in a
cell, a mixture weight, a price, the horizon or the depth, or once as a `param` read by name. A pack
cannot choose, compare a probability or update a belief because the grammar has no form for any of
them (E5, S1) — there is nowhere in a pack to put one.

## The first pack, and what it costs

`packs/wordle/pack.py` is Wordle on forty words: 1,270 lines, 4,883 quantities, nothing `fitted`.
It is generated and committed, so every number in the World is in the repository.

Its terminal acts are claims — `claim <word>`, −1 if right and `loss` if wrong — because a World
whose only terminal act is "give up" is **degenerate at depth 1**, and that is a fact about the
declared World rather than something to fix in code. One look ahead values the frontier at V₀, so
with m candidates, a loss L and c non-green feedback classes,

    Q_1 − V_0 = [ |L| + (|L| − 1)(c − 1) − m ] / m

which is negative for every guess when the only terminal value is a constant. `tests/test_wordle.py`
keeps that as a test: with "give up" alone the kernel gives up at once, and the oracle agrees.
`loss = −7` because five guesses and a claim cost 6, so a wrong claim is one worse than playing the
game out honestly — the only `elicited` opinion in the pack besides the depth.

**Measured before the fast paths:** `decide` at the root took about 2 s, being V₀ over 40 claims
inside Q₁ over 40 guesses — roughly 1.3 M exact-rational operations; all forty answers took about
90 s, and the work per `decide` barely fell as the game was won, because a belief kept all forty
states. That measurement is what brief 004 was for. The same forty answers now take **0.1 s**.

## The three fast paths, and why each is exact

CHARTER E2 allows an exact fast path to replace `push`, `condition` and expectation, and nothing
else; `decide`, the lookahead and the episode loop stay written once (E5). Three of them are here.
None is approximate: no threshold, no sampling, no float, no bound carried for unevaluated mass.
`packs/wordle200/` is what they were built for — the same World at 200 words, at depth 1 and at
depth 2, which is 200 claims and 200 guesses inside 200 guesses.

**1. The belief is carried unnormalised.** Write U_n(m) = mass(m) · V_n(m ⁄ mass(m)). Then §2 is

    U_0(m)   = max over terminal t of  Σ_w m(w) u_t(w)
    Q_n(m,k) = −price(k)·mass(m)  +  Σ_o U_{n−1}(m|k,o)          (m|k,o)(w) = m(w) K_k(o|w)

with no division anywhere. `belief._split` is `push` and `condition` in one pass: P_b(o|k) is the
mass of a part and b|k,o is that part over its mass, and the lookahead multiplies that mass straight
back in, so the normalisation is written down and taken away again in the same line. Every rational
division — the costliest operation there is, being a gcd — leaves the lookahead. `mass` is then
needed only where a price is paid, so at n = 0 it is never computed at all.

A state of mass zero is dropped where the measure is built, and by `condition` too: it weighs
nothing in any sum above, and m(w)·K(o|w) = 0, so no conditioning revives it. The support only
shrinks. The belief a host or an episode holds is still normalised and still changes only by
`condition`, and S5 still fires there.

**2. One act per group of acts the belief cannot tell apart** (`same.py`). Same price, same `once`,
same ending outcomes with the same u_end, and the same kernel row at every state the belief still
carries. What they do at a state of mass zero cannot matter, because every support still in reach is
inside this one. Two such acts have the same Q here, so J3 already says which is played: the first
in menu order, which is the one evaluated. The continuation needs an argument of its own: Q_n
recurses with M \ {k}, so two copies k₁, k₂ leave *different* menus — but they differ by a
relabelling, since M \ {k₁} still holds k₂ and k₂ behaves on every reachable support exactly as k₁
does. A value is a max over acts and does not read their names, so the two are equal. **Multiplicity
is kept**: the menu still carries every copy, so two identical `once` acts are still two looks, and
`tests/test_fastpath.py` holds a World where the second look is worth exactly 1/48.

Deciding sameness has to be cheaper than the values it saves, so every cell, row, u_end table and
price of a World is read once into a small integer: a signature is then a tuple of integers, and two
rationals are compared once and never again. For the terminal acts one more fact halves it again —
restricting to a smaller support can only *merge* groups, never split one, so the representatives of
a superset are enough to start from. At the bottom of the 200-word tree there are four terminal
representatives to sift, not two hundred.

**3. A value already found is not found again**, keyed by the measure, the menu and n — at n = 0 the
menu is not in the key, because only terminal acts are in reach and T never leaves the menu. The
table belongs to the World, which does not change once declared, so it is shared by every episode
played in it: this is what makes 200 answers cost barely more than the first one.

**What they cost and what they bought.** At 200 words, `check` takes 1.8 s and `declare` 0.5 s. At
depth 1 the first episode takes 1.8 s and all 200 answers 2.2 s. At depth 2 the root decision takes
33 s — 8,928 distinct nodes one step down and 77,225 two steps down — and the other 199 answers cost
13 s between them. The reference's own specialised oracle, in machine integers over sets, takes 3.4 s
for the same root; a general kernel over `Fraction`s is ten times that and no more.

**The price of the floor, measured** (`packs/wordle200/SCOREBOARD.md`): mean attempts at depth 1
minus mean attempts at depth 2 is **0.000** over all 200 answers. The two depths are not playing the
same game — they part company on 8 answers — but the deeper agent gains an attempt on one and loses
one on another. Nothing was tuned to make that number larger.

## The think act (CHARTER v0.1)

The amendment adds one entry to the menu, and `decide` buys it or does not. Everything of v0 is
where it was: the argmax, the lookahead and the loop are still written once, the three fast paths
are still underneath them, and no act of any v0 World changed.

`decide.step` is the whole of §2's `think` block, in S7's order of precedence:

| the step reports | when | what it plays | what it pays |
|---|---|---|---|
| `floor` | the World declares no Depth⁺ | decide_min(d,n) | — |
| `struck_n` | n ≤ d, or M holds no observational act | decide_min(d,n) | — |
| `struck_cap` | ĝ = cap − V_d ≤ c: the bounds settle it and f is not read | decide_min(d,n) | — |
| `think` | V_d + f·ĝ − c > V_d, θ being last in M (J14) | decide_min(d⁺,n) (C17) | c = r·ops(s(b)) |
| `refused` | otherwise | decide_min(d,n) | — |

**The cap** (J12) is `max( V₀, Σ_ω b(ω)·best(ω) − the cheapest price in M )`, where best(ω) is the
most that state can still earn: its best terminal utility, or the best u_end of a menu act whose
kernel can emit that outcome *in that state*. One pass over the live states and the menu. It reads
V₀ — a max over terminal acts, no lookahead at all — and never evaluates Vₙ for n > 0, and never
reads d⁺ (S9, C19). The per-state form is the one that is a bound: valuing ending branches at the
root posterior instead gives 10 on `meta_check`'s `FIXED_CAP`, where V₅ is 40951/2000.

**The floor is the step's**, not the loop's, because the two depths are read against different n:
V_d is at min(d, n) and ĝ is 0 exactly when the raw n is at or below d. The deeper look is the
same `_value` with a different n — not a second lookahead and not a second World (E5, S8) — so the
memo of brief 004 answers most of a thought before it starts.

**The operation counter** (E6) lives where the arithmetic does: `belief._dot`, `belief._split` and
`belief._mass` tally what they multiply and add, in bulk, one integer add per call rather than one
per operation, so the Wordle packs pay nothing for being watched. `decide` zeroes the count as a
thought begins and never reads it; `episode.run` reads it when the thought is done and puts it in
`Result.operations`, and `report` prints it beside the `ops(s(b))` the pack predicted. Two
evaluators may count differently, and the page says so: the count is a measurement, never a value,
and never a clock. On the page's Appendix B a thought predicted at 200 operations takes 106 here.

**Five more refusals**, by name: `FRACTION`, `COST`, `DEPTH_PLUS`, `RATE`, `UNSCORED`, and
`TABLE_SOURCE` for a sixth thing — a Depth⁺ that is not the owner's. A Rate below zero is `RATE`:
§1 forbids the number and named no clause for it (QUESTIONS.md Q4), and the author has since
answered — ERRATA queues `RATE` for CHARTER v0.2 and SURFACE v0.1 K15 supplies it meanwhile,
under the name the Rate's own row already carries. A `fitted` Fraction or Cost carries **its own**
Score, named by the table it is of (K14), so `world.score` is a dict and the other table's score
will not do.

**A kit World dict is a probe, not a pack.** C19 hands the kernel a World whose d⁺ is N, which J11
refuses in a pack, to prove that the cap does not read d⁺. So `declare` is `build` — §1's
conversion, refused where it cannot be built — plus the rulings a pack must satisfy, and
`kit_adapter` stops at `build`, as it already did for the clock and the S5 stance.

## The surface of the think act (SURFACE v0.1)

Five declarations, one per table of CHARTER v0.1 §1, and each names its own source (K6):

| written | says | its source |
|---|---|---|
| `depth_plus(2, source="elicited")` | Depth⁺, written out although J11 fixes it — a pack has no defaults | `elicited` alone (K18) |
| `think(fraction=…, source=…)` | θ, and the Fraction f | `elicited` or `fitted` |
| `cost([…], source=…)` | ops(s) for s = 1 … \|Ω\|, **positional** | `elicited` or `fitted` |
| `rate(r, source="elicited")` | the Rate, utility per operation | `elicited` alone |
| `score(v, of=…, source="data")` | the held-out Score of one fitted table | `data` alone (K18) |

The first four come together or not at all (`MISSING`), each at most once (`DUPLICATE`); a pack
that writes none of them is a v0 pack and elaborates byte for byte as before. `score` is not one
of the four: there are two tables that can be fitted, so there can be two scores, one per table,
and no more (`DUPLICATE`). The Cost's keys are **positions**, not numerals (K12), so the list's
length is compared against the states the prior names — which is why `cost` before `prior` is
`MISSING` and a list of the wrong length is `COST`.

**K16, provenance.** v0's fence is absolute and stands untouched: a table that does not say
`fitted` may not read a `fitted` parameter. Over it, the five meta-tables ask a second, transitive
question. Every parameter carries the sources it descends from — its own, and those of every
parameter its cell reads — and a meta-table admits a parameter only if that whole set lies within
what the table could have declared for itself: `think` and `cost` admit `elicited` and `fitted`,
`rate` and `depth_plus` `elicited`, `score` `data`. Refused by the table's own name. The attack
this closes is a `data` number put in a `param` labelled `elicited` and read as the owner's Rate;
a second `param` in between changes nothing, because provenance is not laundered by a hop.

**K17, the census**, is the reading this kernel already had: a parameter counts once where it is
declared, under its own source; a cell counts once under its table's source, written in place or
read from a parameter. So `packs/ok/fitted_think_reads_elicited.py` is data 7, elicited 12,
fitted 1 — the `elicited` parameter once as `elicited`, and the `fitted` cell that reads it once
as `fitted`. The positions of a `cost` list count for nothing.

`check` still ends by calling `declare`: the World's own rules — f's range, a negative cell, a
negative Rate, (d, d⁺, N) — are written once, in `world.py`, and the surface does not repeat them
under its own names (K15).

## The packs

| pack | what it declares |
|---|---|
| `packs/wordle/pack.py` | Wordle on the charter's 40 words, depth 1 — the first pack, and the one the scoreboard was invented for |
| `packs/wordle200/d1.py`, `d2.py` | the same game on 200 words at the two depths: E3's price of the floor, measured |
| `packs/wordle200/adaptive.py` | depth 1 with a think act: `decide⁺` may buy the second look instead of declaring it, at a Rate the pack names |
| `packs/twins/adaptive.py` | the same, on 124 near-twins (-IGHT, -OUND, -ATCH) — a lexicon where one look ahead cannot separate the candidates and the horizon runs out |

All four Wordle packs are written by `tools/make_wordle_pack.py` and committed whole: every number
the World holds is in the file. Regenerate them; do not edit them. The two adaptive packs differ
from `d1.py` in five declarations at the end and in nothing else.

## What is learned between episodes (CHARTER v0.2)

A v0.2 state is the pair (l, g) and the v0 World is built over those pairs by `world.build`, so
`decide`, `step`, the fast paths and the episode loop are untouched: `episode.run` became
`_play(world, prior(world), door)`, and a plate calls `_play` with the prior its Counts give. A
World with no Global is wrapped as one Global value, (), and plays as v0.1 (C21).

**The prior from Counts** is P(Global | Counts) · P(local | Global). P(Global | Counts) is the
declared P(Global) conditioned by `belief._update` — the one update — once per distinct record,
under a likelihood that reads L(record | g)^count. L sums the local out over the draws and the
after-report together, because they share the episode's local. A multiset has no order, so C22
is not a property the code has to keep; it has no way to break it.

**E7's predictive** conditions each Global's local on the history with the same `_update` and
pushes the next kernel through it. That equals counts_check's ratio of sequence probabilities and
keeps the update in one place.

**How S15 scales.** A realisable design is a sequence of at most N acts, each `once` act at most
once: up to Σ_{n≤N} |O|ⁿ of them. Under each, every sequence of outcomes is enumerated at every
state of Ω, for every Global value, and for every end when an After-act is declared. That is
|G| · |T| · Σ_n (|O| · |B|)ⁿ · |Ω|/|G| rows, exponential in N. The kit's largest are the router
(16 states, 8 Global values, N = 1: 1.2 ms) and the cap (8 states, 10 designs at N = 2: 4.3 ms).
Nothing is pruned, sampled or bounded. A World too large for it is a stop, not an approximation.

**Two readings.** A dict that carries `d` is played by the adapter's `decide` as the episode
plays it, `step(...)[0]`: INTERFACE says so at kit v0.7 and kit v0.11's E2 asks it, and `step` is
still the only place `min(d, n)` is applied. And a probe may skip the floor (`build(spec,
floor=False)`): kit v0.11's levels World has N = 0 with d = 1. `declare` rules on the floor in its
old place, so no pack is refused by a different name than before.

## Declaring what is learned (SURFACE v0.2)

A pack that writes any of `globals`, `local_prior`, `after`, `counts`, `falsifiers` or `score(of="counts")` is
SURFACE v0.2's, and `load_pack` returns CHARTER v0.2's dict (`laws/model.py`'s World) instead of a v0.1 spec. It is
read in two steps, as the reference reads it. First the joint World over Omega's states *as SURFACE v0 spells them*
— the states being the pairs P(Global) and P(local | Global) give positive mass (V2.4) — goes through `surface.Pack.joint`,
the same code as every v0.1 pack, so every v0 and v0.1 rule speaks under its old name and |Ω|, `by(...)` and `cost`
all mean that support. Then each state is split into `(local, Global)` and the dict goes to `plated.declare` for
GLOBAL, AFTER, PLATE and UNSCORED. The After-act's price is taken out of `price` for the first step and put back for
the second: it is not in the menu.

**The dict carries no sources.** The kit v0.11 dict has no `table_sources`, and kit v0.12's R3 declares exactly
that dict, so `plated.build` asks for none when there are none (`world.build(..., sourced=False)`) and still rules
on everything else. The surface has judged every source already; a host that writes the dict by hand and wants its
sources ruled on passes `table_sources`, which are then checked as any spec's.

**The text is judged before the tree.** Python folds `ſcore` to `score` while parsing, and raises `ValueError`, not
`SyntaxError`, on a full-width `Ｎｏｎｅ`; so `text.py` finds identifiers in the text with a lexer that skips strings
and comments, and the tree is asked only about escaped surrogates — and only when the text has a `\u` or `\U`
escape at all, which no Wordle pack does (walking the 200-word pack's tree cost 0.4 s).

**The digest is the page's table.** `canonical.py` writes V2.13's rows as a tuple and encodes from them; the five
vectors of the page reproduce byte for byte, and 3,000 fuzzed record sets agree with `counts_check.counts_sha`.

**Where I parted from the reference**, by the page, in brief 008 — the After-act's kernel is a kernel and its price a
price (`QUESTIONS.md` Q10); a Global value the prior does not name is not in Omega (Q11); `score(of="counts")` needs
Counts in every pack (Q12); `falsifiers` may precede `counts` (Q13); an end is reached by its draws (Q14) — kit v0.13
adopted every one. `tests/test_surface_differential.py` runs the corpus's mutations against the reference and now
allows no divergence but SURFACE K7's: a variant that breaks two rules may be refused by either name.

## Shipping Counts, and numbers of any length (brief 009)

**Q15: a prefix may end at an ending outcome.** v0 §2's loop checks zero mass before it checks an ending outcome, so
a report that falsifies the World and is an ending outcome is the prefix's last draw and never becomes its end.
`counts.realisable` checks only that an ending outcome is a record's last draw; then a prefix needs no end, and a
record's end is its last draw's when that draw ends the episode, a terminal otherwise.

**Long literals.** A real Score has tens of thousands of digits (appendix A shipping 300 records: 68,811 characters,
a denominator of 34,486 digits); Python refuses to convert more than 4,300 by default, and the limit is the
interpreter's, so the kernel never sets it. `tokenize` is not on the import list, so `text.swap_long` finds literals
with the lexer V2.11 already needed: a maximal run of letters, digits, `_` and `.` outside strings and comments that
does not continue a name, all decimal digits, no leading zero, longer than 600 characters, is swapped for a fresh name
before `ast.parse`. `cells.py` reads that name as its integer in a cell and refuses it UNHOUSED_NUMERAL where no
number may stand, as the reference does; `counts` reads a multiplicity from its digits. A run Python could not read
anyway (`1_000…`, `0123…`) is left for the parser, which says SYNTAX. The pieces are 600 digits, not the reference's
4,000, because 640 is the least limit a host may set: under `-X int_max_str_digits=640` the kernel reads and writes
the same Score. Every number written for a reader goes through `digits.rational`: the Score, E7's lines, `report`,
the wire, a refusal's detail.

**`wald.digest` is a function from a fresh `import wald`.** Kit v0.13 found it the submodule `wald/digest.py`, which
Python sets on the package when the adapter imports it. The module is `canonical.py` now, so nothing can shadow it.

## Not here

No `host` form — withdrawn by SURFACE K4. No floats. No learning but Counts: no carried
posterior, no log, no forgetting, no fitted parameter within a plate (S13). No fast path that is not exact:
no pruning by a threshold, no sampling, and no special case for a uniform prior or a deterministic
kernel. The kernel does not know what game it is playing — there is no feedback rule and no word
list in `src/wald`. No clock: `time` is not imported anywhere here, and a thought costs the number
the pack declared, never a number measured. No second decider: θ is an entry of one menu, read by
the one `decide` (S8). Nothing in the surface lets a pack choose *when* to think: it supplies f,
ops and r, and the comparison of them is the kernel's (SURFACE v0.1 §3). No form keys a Fraction
or a Cost on anything but the count of live states, none updates either within an episode, and
there is no second think act.
