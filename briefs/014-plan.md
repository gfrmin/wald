# Brief 014 — plan

## Context
Brief 010 gave each plate its own memo, so 100 fresh plates over one World each start empty and
redo what `run` (and v0.2.1's plates) found once: the arena measured 17.1 s → 153.9 s. A fresh
plate's episode prior is the World's prior, and `_value` reads only the World and the belief, so
the values under that prior are the World's memo's values. Brief 013 made the memo keys canonical
for the measure (lcm, then gcd out), so equal beliefs reach equal keys across `run` and plates.

Branch `b/014-fresh-plate-memo` from master `6c0df4d` (013 merged).

## Design — one line in `Plate._work`
`Plate._work(prior)` already compares the episode prior's measure with the last one (`_since`).
When it differs, the plate now picks the memo for the new prior:

- the prior's measure equals the World's prior's (`_measure(belief.prior(world))`, exact Fraction
  equality: equality of the beliefs) → `world.work()[1]`, `run`'s memo;
- otherwise → a new `{}`, as brief 010 built.

The World's prior is computed only when the prior moved, so a plate whose prior never moves pays
it once. Consequences:
- The World's memo is only ever handed to an episode that starts at the World's prior, so it is
  filled only from beliefs that prior reaches — the beliefs `run` would put there. A learning
  plate's later episodes get their own memo, and the World's stops growing.
- When the prior moves, the plate's reference to the old memo (its own, or the World's) is replaced
  before the episode starts: nothing of the previous episode survives except in the World's memo,
  where `run` would have left it.
- `wald.run`, `decide`, `step`, `_play` unchanged. `World.work`'s docstring: the memo is `run`'s,
  and a plate's while its prior is the World's.
- A v0 World on a plate (wrap: one Global, no records move) — its prior is the World's, so it plays
  on the World's memo for life, as before brief 010.

## Tests (`tests/test_plate_memo.py`)
- `test_the_world_memo_is_not_the_plates` → "a plate that has learned leaves the World's memo as a
  fresh plate would have": World A, one plate, one episode; World B, one plate, 30 episodes, same
  door seed. `A.work()[1] == B.work()[1]` (keys and values), and non-empty.
- New kept-vs-dropped case: 40 fresh plates on one World sharing its memo, against 40 fresh plates
  each forced onto an empty memo (a `Plate` subclass, brief 010's behaviour), each pair on the same
  door seed: `same()` on every Result, and `Plate.values()` text equal; operations only by length.
  Also assert the shared World's memo is the same object every fresh plate used.
- Existing tests: `test_no_global_keeps_the_memo` now asserts the memo is the World's;
  the learning test asserts the first episode used the World's memo and later ones did not.

## Measurement
- `tools/plate_memory.py` 200 episodes, master vs branch (git worktree in scratchpad).
- Arena shape: `/srv/wald-measure/omniscience-p1-c0.py` (hash checked) with its `counts(...)` line
  removed (1,152 Global values, no Counts), declared once, then 100 fresh `wald.plate(world)` each
  running one episode with a seeded random door; seconds for the 100 plates and peak RSS, on
  `v0.2.1`, master and this branch (worktrees, `PYTHONPATH`). Script in the scratchpad.
- Wordle kits not required by this brief; `run` is untouched.

## Verification
Own tests; the cage command timed with each suite's line; `KERNEL.md` brief 010 line amended;
`API.md` plate sentence checked. Commit signed, push `b/014-fresh-plate-memo`, hand over PR text.
