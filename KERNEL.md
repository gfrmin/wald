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

## The three things that exist exactly once

- **The choice.** `decide.py`. The argmax, the lookahead and the episode loop's call to it. Packs and
  fast paths supply beliefs and values, never acts (E5, J10).
- **The belief update.** `belief._update`. The public verb `condition` is that plus the token; the
  adapter is that without one, because the kit hands it raw outcomes rather than minted Obs.
- **The floor.** `episode.run`, as `min(world.d, n)`. `decide` is always exactly decide_n: an
  evaluator is compared with the reference *at the same d* (E3), so the depth is never baked into it.

## Two notes on what is here that the page did not name

- `refusals.PRICE`. §1 declares `price : O → ℚ≥0` and `laws/INTERFACE.md` fixes seven refusal names,
  none of them for a negative price. A rule that forbids nothing says nothing (`violators.md`), so
  the clause is enforced under an eighth name rather than left unsaid. Nothing in the kit declares a
  negative price, so this neither passes nor fails anything there; brief 002 may rename it.
- S2's second clause is enforced: a `fresh` act that names a source not declared in `components` is
  `SHARED_SOURCE`, because its two executions read that source twice. The default — no `sources` key,
  a private source per act, a new one per execution of a `fresh` act — is never refused.

## Not here (brief 001's `Not in this brief`, and INTERFACE's deferrals)

Surface syntax and the pack checker, so: unhoused numerals and unread parameters (S3), and refusing a
pack that chooses (E5), are brief 002's. No fast path (E2), no domain packs, no floats, no learning.
