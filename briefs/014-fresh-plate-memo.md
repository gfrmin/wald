# Brief 014 — a fresh plate starts from the World's memo

**Done when** the `cage` check is green on a pull request from `b/014-fresh-plate-memo`, under `kit-v0.14`. No page changes, no kit changes, no new public name: `wald.__all__` keeps its fourteen (ST1). This is a performance item under v0.2 as signed. **Work it after brief 013 has merged**, since it relies on 013's item 2.

**The owner's numbers for this brief:** none. The owner gave the go on 2026-10-02.

**The measurement.** The arena measured brief 010 against its PR (gfrmin/wald#13). The record is `gfrmin/wald-arena` `QUESTIONS.md` open item 2, on branch `close-002`, and issue gfrmin/wald-arena#6.

- **The setup:** stage 2's p = 1, c = 1 pack with its Counts removed. It played 100 fresh episodes, each on a new `wald.plate(world)`, on steel.
- **The result:** on `v0.2.1`, where every plate shared `World.work()`'s memo, the run took 17.1 s. On brief 010 it took 153.9 s, about 9× slower, because each new plate starts with an empty memo. The acts were identical, and peak memory was 1.25 GB in both.

A fresh plate's first episode starts from the World's prior. The values `run` has found under that prior are the same values: `_value` reads only the World and the belief, as brief 010 says. So a plate whose episode prior is the World's prior can use the World's memo. Once its prior moves, it holds its own memo, which brief 010 bounds.

**What to build:**

1. **While a plate's episode prior equals the World's prior, it plays with `World.work()`'s memo.** That covers a plate with no Counts, and a plate whose records move no Global value. Equality is equality of the beliefs. Once the prior differs, the plate does what brief 010 built: its own memo, dropped whenever the prior moves.
   - The World's memo is still never filled from a belief that the World's prior cannot reach. A learning plate's later episodes must not grow it.
   - `wald.run` is unchanged.
2. **Brief 010's guarantees hold.**
   - A learning plate's memory stays bounded by one episode's memo plus the Counts. Rerun `tools/plate_memory.py` at 200 episodes.
   - Once the next episode begins, no belief from the previous one survives anywhere except where `run` would have left it.
   - Change `tests/test_plate_memo.py`'s `test_the_world_memo_is_not_the_plates` to say what is now true. A plate that has learned leaves the World's memo as a fresh plate would have left it.
3. **Every act and every value is unchanged.** Extend brief 010's kept-vs-dropped test to cover this case: fresh plates sharing the World's memo against fresh plates with empty memos, identical in everything but E6's operation count.
4. **`KERNEL.md`:** brief 010's line, amended. **`API.md`:** the plate sentence, only if it changes.

Where the page and this brief disagree, the page decides: write it in `QUESTIONS.md`, with the World, and stop on that point.

**Report in the PR:**

- the cage command's time, and each suite's line;
- the arena's measurement of 100 fresh plates on a World of its shape, at least 100 Global values and no Counts, with each plate on a new `wald.plate(world)`. Give seconds and peak RSS on `v0.2.1`, on master, and on this brief. The aim is `v0.2.1`'s time or close to it;
- `tools/plate_memory.py` at 200 episodes, before and after: memory flat, seconds per episode not rising.
