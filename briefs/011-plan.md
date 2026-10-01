# Brief 011 — plan

## Context
`declare` on the Renavon pack (20,736 states) takes ~248 s, ~86% of it in `_total`
(`src/wald/world.py`). Branch `b/011-total` from `origin/master` (`3a0b104`), apart from
brief 010's branch, which is not merged: one fix per PR.

## Why it is quadratic — the loop
```python
missing = [state for state in omega if state not in table]
strangers = [state for state in table if state not in omega]
```
`omega` is `prior.carrier()`, which is `tuple(self._mass)`. A kernel's `table` is
`kernel.states()`, which is `tuple(self._rows)`. `in` on a tuple is a scan, comparing tuple
states element by element. So `strangers` is |table|·|Ω| for every table, and `missing` is
too for every kernel: 2·|Ω|² per kernel, |Ω|² per utility and u_end table. Not a nested
scan written out, but two hidden ones.

## The fix
Build `set(omega)` and `set(table)` once per call, locals, gone at return; test membership
in those; walk the same two sequences in the same order. Linear in |Ω|. The lists are the
same lists, so the refusal (TABLE_SHAPE, its text, gaps before strangers) is the same. No
number is touched; no cache; no early exit. States are already dict keys (the prior's), so
they are hashable and set membership agrees with tuple membership.

## Checks
- the cage command at seed 1, 100 worlds; `tests/` whole; `tests/test_total.py` pins the
  refusal text and order.
- the repo's packs (twins, wordle, wordle200 ×3): census and declare outcome the same before
  and after.
- `tools/total_scaling.py` at master and here: before/after seconds and `_total`'s share.

## Not reachable from this checkout
The Renavon pack (renavon-monorepo) and the arena's 13,824-state pack are not here. The
synthetic Worlds of `tools/total_scaling.py` at 13,824 and 20,736 states stand in for them;
the brief's own numbers on the real packs are for whoever holds them.
