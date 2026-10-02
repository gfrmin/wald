# Brief 010 — plan

## Context
The arena's stage 2 ran out of memory: the lookahead's memo (`World.work()`, `src/wald/world.py:56`)
lives for the World's life, and on a learning plate every episode's prior is new, so the memo only
grows (~0.25 GB/episode). The arena now pokes `world._work = None` from the host. The brief: the
plate owns the memo, keeps it only while the episode prior recurs, drops it before an episode whose
prior moved; `wald.run` on a v0 World keeps today's life-long memo; no act or value changes; no new
public name; lock stays `kit-v0.13`. Not in scope: `posterior_global`'s per-episode cost (S13 —
recompute from Counts as today).

Branch `b/010-plate-memo` from master `3a0b104` (already checked out, clean).

## Design — the memo on the `Plate`, tagged by the prior it was found under
The commit title on master says it: the plate owns it. Putting it on the Plate (not the World) also
means two plates over one World, or `run` beside a plate, never share beliefs.

1. **`src/wald/plate.py`**: `Plate.__slots__` gains `_since` (the measure of the prior the memo was
   found under) and `_memo` (a dict). In `run`, after `prior = C.episode_prior(...)`:
   `m = _measure(prior)`; if `m != self._since`: `self._since, self._memo = m, {}` — the old memo and
   old prior are gone before `_play` starts. Then `_play(plated.world, prior, door, self._memo)`.
   Exact comparison of the measure (dict of Fractions), so: no Global (wrap's one value `()`) or a
   record that cannot move P(Global | Counts) → equal → memo kept, as today. The tag is the memo's
   own root key in another form and is read by nothing but this comparison. Update the module and
   class docstrings (S13 wording: Counts, falsifier, and a memo with no meaning, which holds nothing
   of a past episode once the next begins).
2. **`src/wald/episode.py`**: `_play(world, belief, door, memo=None)` passes `memo` to `step`; `run`
   unchanged (passes none → World's memo for life).
3. **`src/wald/decide.py`**: `step(belief, world, n, used=frozenset(), memo=None)`:
   `same, kept = world.work(); memo = kept if memo is None else memo`. Nothing else in `decide`,
   `value`, `_solve`, `_value`, `_q` changes. `Sameness` stays the World's (a fact of the World,
   bounded, holds no belief). `world.work()` docstring: the memo it returns is `run`'s; a plate
   brings its own.
4. **`KERNEL.md`**: one line for this brief (fast path 3's paragraph + the `plate.py` row + "Not
   here"): the plate owns its memo; dropped before an episode whose prior moved, so the kernel holds
   no belief of a past episode once the next begins — S13's "no cache with a meaning", tightened;
   `run` on a v0 World keeps its memo for the World's life. **`API.md`**: "A plate keeps its Counts
   and nothing else" still true for a host; check, likely no change.

## Tests and measurement
- **`tests/test_plate_memo.py`** (new): an appendix-A-shaped v0.2 dict (answer local × `rel` Global on
  the grid k/200, k=101..200 — 100 values, uniform; right 1, wrong 0, abstain 0; `ask` free and
  `once`; After-act `grade` revealing the answer), so `ask` is always worth E[rel] > 1/2 and every
  record moves the prior. A seeded random door. Two plates, same seed: the plate as built, and a
  `Plate` subclass whose memo is one dict for its life. Assert every Result identical — acts,
  outcomes, status, paid, `report(final)`, thought, steps, record — and the Counts. (E6's
  `operations` is a measurement of work done, and the memo changes it by design; asserted only
  that it is a tuple of the same length.) Also assert: the plate's `_since` changed every episode,
  and on a v0 World (no Global) and appendix A with a non-moving record the memo is the same object
  across episodes. ~60 episodes to stay fast.
- **`tools/plate_memory.py`** (new, outside `src/`, a KERNEL.md line): the same World, 200 episodes,
  public API only (`wald.declare`, `wald.plate`, `wald.Door`), prints `ru_maxrss` after 50/100/200
  episodes and seconds an episode. Run against this branch and against master via a `git worktree`
  of `3a0b104` in the scratchpad (`PYTHONPATH=<tree>/src`), for the PR's before/after table.

## Verification
1. `python3 -m unittest discover tests` (own tests).
2. The cage, timed: `time (sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100)` — record each suite's line.
3. Wordle kits timed, before (master worktree) and after: `charter/laws/kit_wordle.py`,
   `kit_wordle_big.py`, `kit_wordle_think.py` (check their CLI flags first).
4. `tools/plate_memory.py` before/after.
5. Write `briefs/010-plan.md` (this plan) first, commit plan + code + KERNEL.md (signed, with the
   Co-Authored-By line), push `b/010-plate-memo`, open the PR with the report the brief asks for;
   watch the `cage` check until green.
6. Anything the page leaves open → `QUESTIONS.md` with its World, and stop on that point (none
   expected: the brief itself allows the memo to be held between episodes and dropped "before the
   episode starts").
