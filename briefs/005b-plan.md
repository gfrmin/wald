# Brief 005b — plan: the surface of the think act (SURFACE v0.1), and two names

Read first: `charter/SURFACE-v0.1.md` whole, `charter/ERRATA.md`, `charter/laws/INTERFACE.md`'s
kit v0.7 and v0.8 sections, and `charter/laws/surface_check.py`'s `owned` and its five `d_*`
handlers. The page decides; where it is silent the reference checker is the definition.

Nothing here is a new decision. Five declarations are added to a parser that already has nine,
one rule (K16) is added to the fence that already stands, and two refusals move from one name to
another because the author has now named them. The kernel's `decide⁺` is untouched.

## What is already in place, and what it costs

Brief 005a built the World side: `world.build` carries `dplus`, `fraction`, `rate`, `ops` and
`score`, `world._rulings` refuses by name, `decide.step` buys the thought, `episode.run` records
it. The surface has never said any of it: `src/wald/surface.py` knows nine declarations, and a
pack that writes `think(...)` is refused `NOT_A_DECLARATION` today. That is the whole gap.

Two things 005a got the name of wrong, and the author has now ruled:

- a **Rate below zero** was `COST` (QUESTIONS.md Q4, taking `meta_check.refuse_meta`'s one line);
  ERRATA now queues `RATE` for CHARTER v0.2 and SURFACE v0.1 K15 supplies it. `meta_check` moved
  at kit v0.8 and `kit_think.refusal_cases` now tests it. Q4 is answered, not withdrawn.
- a **Depth⁺ whose source is not `elicited`** had no name; K18 makes it `TABLE_SOURCE`, and
  `kit_think` tests that too. The surface is deliberately stricter than CHARTER v0.1 S3 here,
  as K3 was stricter about numerals; the Worlds outside it are unsayable by design.

And one shape changed under it: `score` was a single number and is now a dict keyed by
`"fraction"` and `"cost"`, one entry per fitted meta-table (K14, INTERFACE kit v0.8).

## The six things to build

### 1. Five declarations in `src/wald/surface.py` (§1)

| written | held | refused |
| --- | --- | --- |
| `depth_plus(d⁺, source="elicited")` | `self.dplus`, `dplus_source` | source not `elicited`: `TABLE_SOURCE` (K18) |
| `think(fraction=…, source=…)` | `self.fraction`, `fraction_source` | source not `elicited`/`fitted`: `FRACTION` |
| `cost([…], source=…)` | `self.ops` as `{s: cell}` for s = 1…\|Ω\| | not a list: `NOT_A_DECLARATION`; wrong length: `COST`; source not owned: `COST`; before the prior: `MISSING` |
| `rate(r, source="elicited")` | `self.rate`, `rate_source` | source not `elicited`: `RATE` |
| `score(v, of=…, source="data")` | `self.scores[of]` | source not `data`: `TABLE_SOURCE`; `of` not `fraction`/`cost`: `NOT_A_DECLARATION`; twice for one table: `DUPLICATE` |

`depth_plus`, `think`, `cost`, `rate` join `ONCE`'s duplicate rule as their own group `META`
(each at most once, `DUPLICATE`); `score` is not in it, because there are two fitted tables.
The `cost` list is positional and its positions are keys, not numerals (K12): the count of cells
is compared against `len(self.prior)` — \|Ω\| as the prior names it (K10) — so `cost` before
`prior` is `MISSING`, which is what `self.states()` already says.

In `spec()`: if any of the four is declared, or any `score` is, then all four must be
(`MISSING`); a `depth_plus` that is not a whole number is `DEPTH_PLUS`; the spec gains `dplus`,
`fraction`, `rate`, `ops` and the four `table_sources` entries; a `fitted` fraction or cost
without its `score` entry is `UNSCORED`, and a `score` of a table that is not fitted is
`MISSING`; `score` goes in as a dict only when there is one. `declare(spec)` still has the last
word and is still the only place the World's own rules are written.

### 2. K16, provenance, in `src/wald/cells.py`

v0's fence is `Cells.number`'s and does not move: a table that does not say `fitted` cannot read
a `fitted` parameter, wherever it is. K16 adds a second fence **for the five meta-tables only**:

- every `param` carries a **provenance** — its own source, and transitively the provenance of
  every `param` its own cell reads. Computed once at `declare_param` by walking the value node.
- a meta-table cell may read a `param` only if that provenance lies within the sources the table
  could itself declare: `think` and `cost` admit `{elicited, fitted}`, `rate` and `depth_plus`
  `{elicited}`, `score` `{data}`. Otherwise: the table's own name (`FRACTION`, `COST`, `RATE`;
  `TABLE_SOURCE` for `depth_plus` and `score`).

One new method, `Cells.owned(node, tag, admits, name)`: walk the node, refuse a `param` whose
provenance is not within `admits`, then `number(node, tag)` as before. The six v0 tables do not
call it and are unchanged. The attack this closes is `rate_laundered.py`: a `data` number put
into a `param` that says `elicited`, then read by `rate` — the fence lets it through because
nothing is `fitted`, and provenance does not.

### 3. K17, the census — nothing to change, and one line to check

Our `Cells.count` already implements the reading K17 fixes: a `param` counts once at declaration
under its own source, a cell counts once under its table's source. So each meta-table counts its
own cells: `depth_plus`, `think` and `rate` one each, `cost` \|Ω\|, each `score` one. The
positions of the `cost` list count for nothing. The proof is
`packs/ok/fitted_think_reads_elicited.py`: data 7, elicited 12, fitted 1 — the `elicited` `param`
once as `elicited`, the `fitted` fraction cell that reads it once as `fitted`.

### 4. Two names in `src/wald/world.py`

`_rulings` moves two lines and grows one:

- `world.rate < 0` → `RATE`, not `COST` (K15, ERRATA). The Cost block keeps the table's own two
  refusals (a missing cell, a negative cell) and the source; the Rate block takes both of the
  Rate's.
- `table_sources["dplus"]` other than `elicited` → `TABLE_SOURCE` (K18). It goes before the
  `DEPTH_PLUS` ruling: a source is read before the number it labels.
- `UNSCORED` reads the dict: `{t for t in ("fraction", "cost") if source is "fitted"} - set(score)`
  must be empty. `build` keeps `score` as a dict, `{}` when there is none.

`kit_think.refusal_cases()` is fifteen cases now and is the check.

### 5. `report`'s label

`belief.report(belief, world)` prints `"<s> live: <ops> operations predicted, <n> counted"`. The
counter is reset when a thought begins, so what it prints is the operations since then and the
label says so: `"… counted since the last thought began"`. No number moves.

### 6. `KERNEL.md` and `QUESTIONS.md`

`KERNEL.md`: the `surface.py` row names the five declarations, and the think section gains K16's
sentence and the two moved names. `QUESTIONS.md`: Q4 is marked **answered — RATE**, with the
ERRATA entry and K15 quoted, and the note that the kernel moved in this brief.

## How I will know it is right

- `sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100`. The corpus is now 20 lawful and 103 poison packs; R3 asks for the same World *and the same census* as `surface_check.py` for each lawful one, and `declare` must accept it.
- The v0 corpus is unchanged: I will diff `check`'s spec and `census` over `packs/ok` before and after the change, and the only differences must be the five packs that declare a think act.
- `python3 charter/laws/kit_think.py --impl src` for the fifteen refusals alone, and the local tests under `tests/`.
- `--worlds 300` on seeds the brief does not name, for the seed CI keeps.

## What this brief does not touch

`decide.step`, the cap, the operation counter's arithmetic, `episode.run`, the fast paths of 004.
No pack chooses when to think (§3): the surface supplies f, ops and r, and the comparison stays
in the kernel's one `decide`. The scoreboard's S7 counts and the E3 sweep over r are still not
asked for.
