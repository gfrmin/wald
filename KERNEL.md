# KERNEL.md — every module, and its one reason to exist

The kernel of CHARTER v0. Fifteen modules; if one of them cannot keep its line here, it should not
exist. Standard library only, exact rationals only, and the list in `cage/lint_imports.py` is the
whole of what `src/wald` may import.

| module | why it exists |
|---|---|
| `wald/__init__.py` | the host's whole surface: `declare`, `run`, `Door`, `report`, `Display`, `refusals` — and not the verbs, so a host never holds a probability and never chooses (S1, E5) |
| `wald/refusals.py` | `Refused` carries the **name** of the clause that refused a pack, so a refusal says which rule spoke; `WorldFalsified` and `ObsSpent` are the two things the kernel refuses at run time (S5, S2) |
| `wald/dist.py` | the one place mass is checked to sum to one, so a row that does not (S4) cannot come into existence anywhere else |
| `wald/kernels.py` | `Kernel`, and the only five ways to build one — point, table, mixture, product, composition — each preserving row sums by construction (S4) |
| `wald/world.py` | `declare`: the World of §1 with its tables and their `data`/`elicited`/`fitted` tags, and every validation that refuses a pack by name before anything runs |
| `wald/obs.py` | the Obs token, minted only by a door and consumed by exactly one `condition`; a token is not a record to be read twice (§1, S2) |
| `wald/display.py` | `Display`: it renders and does nothing else, so a display value cannot reach control flow or a belief (S1) |
| `wald/belief.py` | the sealed `Belief` and the verbs allowed to touch it — `prior`, `push`, `condition`, `expect`, `report`; the belief update of §2 is written once, here, and so is E2's unnormalised stand-in for the three of them |
| `wald/decide.py` | the one `decide`: V₀, Qₙ, Vₙ and the argmax exist here and nowhere else (E5), with E2's fast paths underneath them |
| `wald/same.py` | which acts a belief cannot tell apart, so the lookahead evaluates one of each group and J3 takes the first (E2) — it decides sameness and never a value |
| `wald/episode.py` | `Door` and `run`: the episode of §2 in the page's order, and the only place the floor `min(d, n)` is applied (E3) |
| `wald/kit_adapter.py` | the `laws/INTERFACE.md` shim: plain dicts in, kernel types out, no logic of its own |
| `wald/cells.py` | SURFACE §3: what a number may be, where it is housed, the `fitted` fence, and the census of quantities by source |
| `wald/datafile.py` | SURFACE K5: a kernel's rows read from a JSON file beside the pack, pinned by the SHA-256 of its bytes — the only file the kernel ever reads |
| `wald/surface.py` | SURFACE §1, §2 and §4: the nine declarations and the seven kernel forms, parsed with `ast` and never executed, elaborated to a World spec |
| `tools/wald_check.py` | outside `src/`: `python3 tools/wald_check.py pack.py` — the write, check, repair loop for every pack author |
| `tools/make_wordle_pack.py` | outside `src/`: writes a Wordle pack from one of the charter's word lists at a given depth, the game's feedback rule included |
| `tools/play_wordle.py` | outside `src/`: plays every answer of one or more packs through `wald.episode.run` behind a door that is the game, and writes the scoreboard |

## The three things that exist exactly once

- **The choice.** `decide.py`. The argmax, the lookahead and the episode loop's call to it. Packs and
  fast paths supply beliefs and values, never acts (E5, J10).
- **The belief update.** `belief._update`. The public verb `condition` is that plus the token; the
  adapter is that without one, because the kit hands it raw outcomes rather than minted Obs.
- **The floor.** `episode.run`, as `min(world.d, n)`. `decide` is always exactly decide_n: an
  evaluator is compared with the reference *at the same d* (E3), so the depth is never baked into it.

## The refusals, and one reading that had to be chosen

`declare` refuses a pack by the name of the clause it breaks: `EMPTY_T`, `PRIOR`, `KERNEL_ROW`,
`PRICE`, `DEPTH`, `ZERO_EVIDENCE`, `TABLE_SOURCE`, `TABLE_SHAPE`, `SHARED_SOURCE`. (`PRICE` and the
`fresh` half of `SHARED_SOURCE` were this kernel's readings under kit v0.1; kit v0.2 adopted both.)

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

## Not here

No `host` form — withdrawn by SURFACE K4. No floats, no learning. No fast path that is not exact:
no pruning by a threshold, no sampling, and no special case for a uniform prior or a deterministic
kernel. The kernel does not know what game it is playing — there is no feedback rule and no word
list in `src/wald`.
