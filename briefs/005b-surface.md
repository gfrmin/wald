# Brief 005b — the surface of the think act (SURFACE v0.1), and two names

**Done when** the `cage` check is green on a pull request from `b/005b-surface`. Kit v0.8 grows the corpus by 5 lawful and 39 poison packs under SURFACE v0.1 (signed, tag `surface-v0.1`): read that page fully, then `INTERFACE.md`'s kit v0.8 sections, then `laws/surface_check.py`'s five `d_*` handlers for the new declarations and its `owned` — the reference is the definition; you may read it.

**The owner's numbers for this brief** (you choose none): none. This brief declares no pack.

1. **Five declarations in `src/wald/surface.py`**: `depth_plus(d⁺, source=…)`, `think(fraction=…, source=…)`, `cost([…], source=…)`, `rate(r, source=…)`, `score(v, of=…, source=…)`, exactly as SURFACE v0.1 §1 gives them — positional `cost` of length |Ω| after `prior`; `depth_plus` `elicited` only; `score` one per fitted table, named by `of`. Together or not at all (`MISSING`). Everything else in a pack is v0 and must parse exactly as before: the v0 corpus stays 75/75 through your `check`.
2. **K16, provenance.** Every `param` carries the set of sources it descends from (its own, and transitively those of every `param` its cell reads). A meta-table admits a `param` only if that set lies within the sources the table could declare; refuse by the table's own name (`FRACTION`, `COST`, `RATE`; `TABLE_SOURCE` for `depth_plus` and `score`). v0's `fitted` fence is unchanged and still covers every cell. The poison packs `rate_laundered.py`, `fraction_laundered.py`, `score_laundered.py` are the shape of the attack this closes.
3. **K17, the census.** A `param` counts once at declaration under its own source; a cell counts once under its table's source whether written in place or read from a `param`. `census` on `packs/ok/fitted_think_reads_elicited.py` is data 7, elicited 12, fitted 1.
4. **The spec `check` returns** gains `dplus`, `fraction`, `rate`, `ops`, `table_sources.{dplus, fraction, cost, rate}` and `score` as a dict keyed by `"fraction"`/`"cost"` (INTERFACE kit v0.8). `check` still ends by calling `declare`: the World's rules are not written twice.
5. **Two names in `world.declare`.** A Rate below zero is `RATE`, not `COST` (ERRATA on CHARTER v0.1; SURFACE v0.1 K15) — your Q4, answered. A Depth⁺ whose source is not `elicited` is `TABLE_SOURCE` (K18). `UNSCORED` now reads the `score` dict: a fitted fraction needs `score["fraction"]`, a fitted cost `score["cost"]`.
6. **`report`'s label.** The counted operations it prints are those since the last thought began; say so in the label ("counted since the last thought began"), not "counted". No number changes.
7. **`KERNEL.md`**: the surface line names the five declarations and K16. `QUESTIONS.md`: mark Q4 answered (RATE) with the ERRATA reference.

Where SURFACE v0.1 and `surface_check.py` disagree, the page decides and the checker is the usual culprit: `QUESTIONS.md`, with the pack. Where the page admits two readings, the same, and stop on that point.

Report in the PR: the cage command's time; `census` on the four appendix packs of the corpus; and one line confirming no v0 pack's spec or census changed (diff `check` before and after on `packs/ok`).
