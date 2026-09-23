# KERNEL.md — every module, and its one reason to exist

The kernel of CHARTER v0 and SURFACE v0, and of their amendments v0.1. Seventeen modules; if one
of them cannot keep its line here, it should not exist. Standard library only, exact rationals
only, and the list in `cage/lint_imports.py` is the whole of what `src/wald` may import.

## The ten names a host gets

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

`__all__` lists the first six and not the four of brief 006, because kit v0.10's ST1 still allows
only the six; all ten are bound on `wald`, which is what L1 asks (`QUESTIONS.md` Q5, open).

Not among them: `push`, `condition`, `expect`, `decide`, `step`, `Belief`. A host never holds a
probability and never chooses (S1, E5). The submodules are reachable, as anything in Python is;
they are the kernel's, and nothing in `API.md` names them.

| module | why it exists |
|---|---|
| `wald/__init__.py` | the host's whole surface, the ten names above — and not the verbs, so a host never holds a probability and never chooses (S1, E5) |
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
| `wald/cells.py` | SURFACE §3: what a number may be, where it is housed, the `fitted` fence, the census of quantities by source, and v0.1's K16 provenance — what sources a cell descends from, so a meta-table cannot be handed one it could not have declared |
| `wald/datafile.py` | SURFACE K5: a kernel's rows read from a JSON file beside the pack, pinned by the SHA-256 of its bytes — the only file the kernel ever reads |
| `wald/law.py` | the three tags this package was judged under, in one place, so a consumer can print which law its wald obeys and the kit can hold it to the lock |
| `wald/wire.py` | `from_json` and `to_json`: the World spec and the Result as JSON text, every rational `"p/q"` both ways, read by position so a name spelled like a number stays a name — and the belief out only as `report`'s text (S1) |
| `wald/surface.py` | SURFACE §1, §2 and §4: the nine declarations and the seven kernel forms, parsed with `ast` and never executed, elaborated to a World spec — and SURFACE v0.1's five more, `depth_plus`, `think`, `cost`, `rate` and `score`, which come together or not at all |
| `tools/wald_check.py` | outside `src/`: `python3 tools/wald_check.py pack.py` — the write, check, repair loop for every pack author |
| `tools/make_wordle_pack.py` | outside `src/`: writes a Wordle pack from one of the charter's word lists at a given depth, the game's feedback rule included — and, with `--think`, the five declarations of SURFACE v0.1 |
| `tools/play_wordle.py` | outside `src/`: plays every answer of one or more packs through `wald.episode.run` behind a door that is the game, and writes the scoreboard — S7's four buckets, the thought charged and E6's two operation counts included |
| `tools/serve.py` | outside `src/`: the wire as a process — JSON lines on stdin/stdout, the server the kernel's side of the Door and the client the world's; every client error refused by name, and all of the kernel's I/O is here |
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

## Not here

No `host` form — withdrawn by SURFACE K4. No floats, no learning. No fast path that is not exact:
no pruning by a threshold, no sampling, and no special case for a uniform prior or a deterministic
kernel. The kernel does not know what game it is playing — there is no feedback rule and no word
list in `src/wald`. No clock: `time` is not imported anywhere here, and a thought costs the number
the pack declared, never a number measured. No second decider: θ is an entry of one menu, read by
the one `decide` (S8). Nothing in the surface lets a pack choose *when* to think: it supplies f,
ops and r, and the comparison of them is the kernel's (SURFACE v0.1 §3). No form keys a Fraction
or a Cost on anything but the count of live states, none updates either within an episode, and
there is no second think act.
