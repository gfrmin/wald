# Plan — Brief 002, the surface

Law for this brief: `charter/SURFACE.md` (signed `surface-v0`), subordinate to `CHARTER.md`, plus the
new "The surface" section of `charter/laws/INTERFACE.md`. `charter/laws/surface_check.py` is the
reference checker: I may read it, and I have, but I build mine from the page and use the reference
only to find where I differ. Judge:

    sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100

which now also runs `kit_surface.py`: R3 (every pack in `packs/ok` elaborates to *exactly* the
reference's World, with the same census, and `declare` accepts it), R2 (every pack in `packs/poison`
is refused by a name on its first line), R1 (random Worlds printed as packs and read back).

## 0. What the kit actually demands

- `wald.surface.check(text, data_dir) -> spec` and `wald.surface.census(text, data_dir) -> {source: n}`,
  called with `data_dir` as a keyword. `check` raises `wald.refusals.Refused` with SURFACE §5's names.
- R3 compares my spec with the reference's on `prior, T, O, N, d, closed, bottom, sources, components,
  table_sources`, **and on the order of `T` and `O`** — the menu (J3). Equality of Fractions, so every
  cell must be exact and every `by` must expand to the same per-state mapping.
- **`check` must raise the World-level names too** (`PRICE`, `DEPTH`, `ZERO_EVIDENCE`, `PRIOR`,
  `KERNEL_ROW`, `TABLE_SHAPE`, `EMPTY_T`, `SHARED_SOURCE`): `verdict()` in `kit_surface.py` calls only
  `check`, yet eleven poison packs expect those names. So `check` ends by calling `world.declare` on
  the spec it built and letting the refusal out. The World's rules stay written once (E5's habit), and
  `declare` is then called a second time by the kit on the accepted spec, harmlessly.
- `declare` must take the v0.3 spec: `table_sources["kernels"][act]` is now a **sorted list** of tags
  (empty for a kernel with no numbers, e.g. `point`), `sources` is every act's `reads`, `components`
  lists the space's components. Kit v0.2's structural tests moved to the list form, so this is not
  optional.

## 1. Modules

| module | why it exists |
|---|---|
| `wald/cells.py` | SURFACE §3: what a number may be — an integer, a ratio, a parameter, `+ − * /` over these — where each is housed, the `fitted` fence, and the census of quantities by source |
| `wald/datafile.py` | SURFACE §4 K5: rows read from a JSON file beside the pack, pinned by the SHA-256 of its bytes. The only file the kernel ever reads, kept to one module so R4 (inertness) is checkable by eye |
| `wald/surface.py` | SURFACE §1, §2 and §4: the nine declarations and the seven kernel forms, parsed with `ast` and never executed, elaborated to the World spec of INTERFACE.md |
| `tools/wald_check.py` | outside `src/`, so it may use `sys` and `argparse`: the write-check-repair loop for every pack author, including me in brief 003 |

`wald/refusals.py` gains SURFACE §5's twelve surface names; `wald/world.py` learns the list form of
`table_sources["kernels"]`. No other kernel module changes: the surface builds a spec, and everything
downstream of `declare` is already written.

## 2. The grammar, as I will implement it

A pack is `ast.parse`d (a `SyntaxError` is `SYNTAX`) and **never executed** — no `eval`, `exec`,
`compile`, no import of a pack; the lint bans `open`, so `datafile` reads through `pathlib`.
Every top-level statement must be `Expr(Call(Name in the nine))`, else `NOT_A_DECLARATION` — which is
the name for *anything the grammar gives no form*, wherever it stands (K7): a top-level `if`, an
assignment, a lambda, a comprehension, an attribute, a subscript, an f-string, a starred argument, a
call to any other name, a conditional expression inside a cell, `host(...)`.

Two vocabularies, and they are not the same:

- **plain** (a name in quotes, `True`/`False`, lists and tuples of them): a numeral here is
  `UNHOUSED_NUMERAL` — that is what refuses `space({"health": ["sick", "well", 3]})`.
- **cell** (`cells.number`): an integer, a parameter, unary minus, `+ − * /`. A decimal is `FLOAT`
  (§3 K3: `0.9` is refused, `9/10` is lawful), `x/0` is `DIVISION_BY_ZERO`, an unknown name is
  `UNKNOWN_NAME`, a boolean or anything else is `NOT_A_DECLARATION`.

Housing (§3): a number lives in a cell, a mixture weight, a `price`, the `horizon` or the `depth`, or
once as a `param` read by name. **The census counts quantities, not numerals**: one per cell however
it is written (`census_counts_cells.py` writes the appendix entirely in `u`s and still counts 14),
one per `param`, one per mixture weight, one for the horizon, one for the depth, and one per number in
a `data` file. A `by` row is counted where it is written, once, not once per state it covers.

The **`fitted` fence** is absorbing and has no promotion: a cell or a `param` whose own tag is not
`fitted` may not read a `fitted` parameter (`TABLE_SOURCE`). This is checked in `cells.number`, so it
catches the one-hop launder (`param("sens", sens_fit, source="data")`) as well as the direct read.

**`reads` (K9)** is two checks, both `UNDECLARED_READ`: every component the kernel *names* (in `point`
or `by`) is in `reads`; and the kernel *depends on* no component outside `reads` — states sharing a
projection onto the read components must have identical rows. Then `declare` has the last word on
sharing (`SHARED_SOURCE`): a source read by two acts must be a component, and a `fresh` act may name
nothing but components, because its executions read it twice.

## 3. Order of work

1. `refusals`, then `cells` (§3) — everything else consumes numbers.
2. `datafile` (K5), small and alone.
3. `surface`: the argument plumbing first (it decides `NOT_A_DECLARATION` vs `DUPLICATE` vs
   `TABLE_SOURCE` for a missing `source`), then the nine declarations, then the seven kernel forms,
   then `spec()`.
4. `world.declare`: the list form of `table_sources["kernels"]`.
5. `tools/wald_check.py`.
6. The kit, at seed 1 and at seeds of my own; then `KERNEL.md`, tests, PR.

## 4. Two places the page and the reference checker disagree

Both are recorded in `QUESTIONS.md` with the pack that shows them, as the brief directs. Neither
changes an act, and neither is exercised by the corpus, so implementing the page cannot fail the kit.

1. **A key written twice in `utility(...)` is accepted.** §2: "A key written twice in one dict, or a
   state listed twice in a `data` file, is refused." The reference enforces this in `table()` — a
   state written twice in the prior is `DUPLICATE` — but `d_utility` builds `T` and `ending` with dict
   comprehensions straight off the syntax tree, so a terminal act, an ending act or an ending outcome
   written twice is silently accepted and the last one wins. I refuse all three: `DUPLICATE`.
2. **A `param` may not be named after a declaration.** §2: "The name is an identifier that is not a
   Python keyword." The reference also refuses any name in the nine (`param("world", …)` is
   `BAD_NAME`). The page wins, so I accept it; nothing in a pack can confuse the two, since a
   declaration is a top-level call and a parameter is a name inside a cell.

## 5. My own tests

The corpus is the author's; mine go where it is thin. The round trip (R1) is the sharpest tool I have
and it is cheap to run on shapes the kit's generator does not draw, so: packs with `by` over a
two-component space, `product` and nested `mixture`/`compose`, ending outcomes, `fresh` acts, and a
`bottom` world. Plus a violator per surface rule, the census on a pack written two ways (in ratios and
in `param` arithmetic) giving the same count, and `check` refusing every pack in my own poison set by
the name the page gives. Inertness (R4) I test by checking that a pack whose text would delete a file
or import a module is refused as text, never run.

## 6. Done when

The command in CLAUDE.md is green, which now includes `surface: N/N pass` alongside the kit's
consequences and the structural tests.
