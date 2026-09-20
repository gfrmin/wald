# Brief 001 — the v0 kernel

**Done when** the `cage` check is green on a pull request from `b/001-kernel`.

Build `src/wald/` so that the signed page is true of it. Python 3.12, standard library only.

1. **Types (CHARTER §1).** `World` with its declared tables (Prior, Kernels, Utility incl. u_end, Price, Horizon, Depth), each table carrying its source (`data` / `elicited` / `fitted`). `Belief` sealed: constructible only from a World's Prior, changed only by `condition`; no public access to its weights except through `push`, `expect` and `report`. `Obs` tokens minted only by the door and consumed exactly once (a second use raises). `Display` values returned by `report` support rendering only: no comparison, no arithmetic, no `float()`.
2. **Validation at declaration.** Refuse by name: empty T; a prior that is not strictly positive or does not sum to 1; a kernel row that does not sum to 1; d outside 1..N; a World that is neither `closed` nor has a ⊥ with full support (S5); a source read by two acts that is not a component of Ω (S2); an undeclared or unread parameter (S3).
3. **Kernel combinators (S4):** point, table, mixture, product, composition; each preserves row sums by construction.
4. **Verbs (§2):** `push`, `condition`, `decide`, exactly as defined, sums over outcomes of positive mass, ties to menu order with terminal acts first.
5. **The episode loop (§2),** in the page's order: decide_min(d,n); terminal → the door fires it; else pay the price, mint o; zero mass → WORLD_FALSIFIED; condition; ending outcome → end with u_end; else continue. The door is an interface the host implements; ship a simulated door that draws outcomes from a given true state, for tests.
6. **One `decide` (E5).** The argmax, the lookahead and the loop exist once.
7. **`wald/kit_adapter.py`** per `charter/laws/INTERFACE.md`: a shim that converts plain dicts to your types and calls the kernel. No logic of its own.
8. **`KERNEL.md`:** one line per module saying why it exists.

**Not in this brief:** any surface syntax or checker (that is brief 002), fast paths, domain packs, floats, learning.
