# KERNEL.md — every module, and its one reason to exist

The kernel of CHARTER v0. Ten modules; if one of them cannot keep its line here, it should not
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
| `wald/belief.py` | the sealed `Belief` and the verbs allowed to touch it — `prior`, `push`, `condition`, `expect`, `report`; the belief update of §2 is written once, here |
| `wald/decide.py` | the one `decide`: V₀, Qₙ, Vₙ and the argmax exist here and nowhere else (E5) |
| `wald/episode.py` | `Door` and `run`: the episode of §2 in the page's order, and the only place the floor `min(d, n)` is applied (E3) |
| `wald/kit_adapter.py` | the `laws/INTERFACE.md` shim: plain dicts in, kernel types out, no logic of its own |
| `wald/cells.py` | SURFACE §3: what a number may be, where it is housed, the `fitted` fence, and the census of quantities by source |
| `wald/datafile.py` | SURFACE K5: a kernel's rows read from a JSON file beside the pack, pinned by the SHA-256 of its bytes — the only file the kernel ever reads |
| `wald/surface.py` | SURFACE §1, §2 and §4: the nine declarations and the seven kernel forms, parsed with `ast` and never executed, elaborated to a World spec |
| `tools/wald_check.py` | outside `src/`: `python3 tools/wald_check.py pack.py` — the write, check, repair loop for every pack author |

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

## Not here

Domain packs (brief 003 is Wordle). No `host` form — withdrawn by SURFACE K4. No fast path (E2), no
floats, no learning.
