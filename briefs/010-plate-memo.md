# Brief 010 — the plate owns the lookahead's memo

**Done when** the `cage` check is green on a pull request from `b/010-plate-memo`. The lock stays at `kit-v0.13`; no page changes, no kit changes, no new public name (`wald.__all__` keeps its fourteen, ST1). This is a performance item under v0.2 as signed, forced by one measurement from `gfrmin/wald-arena`.

**The owner's numbers for this brief:** none.

**The measurement.** The arena's stage 2 played 21 plates of 300 episodes each over one declaration with 1,152 Global values (its `QUESTIONS.md`, Findings, 2026-09-30). The lookahead's memo — `World.work()`, the values `_value` has found, keyed by `(measure, n, used)` and kept for the World's life — grew about 0.25 GB an episode, past 250 GB for the 21 plates, and the run was killed for memory. On a plate that learns, no episode's prior recurs: the Counts grow, P(Global | Counts) moves, and every belief the lookahead reaches is new. Within an episode the memo still pays, since the lookahead revisits beliefs; across episodes of a learning plate it only grows. The arena's harness now sets `world._work = None` after each episode (`board.py`, `forget_lookahead`), which is a host reaching into the kernel's slots — not an API, and not something a host should know exists.

**What to build:**

1. **A plate keeps the memo only while the episode prior recurs.** `Plate.run` plays each episode with a memo that holds what was found under the same prior as the last episode's; when the next episode's prior differs — the Counts changed and moved P(Global | Counts) — what was found before is dropped before the episode starts. Where the prior does not move (no Global declared, or a Global the records cannot move), the memo is kept, as it is today. The values found again are the same values: `_value` reads only the World and the belief, never the Counts, so no act and no value changes (the arena's `tests/test_omniscience_world.py` checks this from outside; write the same check inside).

   Where the memo lives is yours to choose — on the `Plate`, or on the World with the plate clearing it — under three constraints: `wald.run(world, door)` on a v0 World keeps today's behaviour, its memo for the World's life; `decide` is untouched save for where it reads the memo from, if at all; and the host never touches it (nothing in `World.__slots__` is for a host).
2. **Memory is bounded over a learning plate.** Over a plate whose prior moves every episode, the kernel's resident memory after episode k is bounded by the memo's size within one episode plus the Counts — not by k. Show it (below).
3. **Nothing from a past episode's belief survives it.** With the memo dropped when the prior moves, the kernel holds no belief of the previous episode once the next begins — a tightening of what S13's last clause asks structurally ("no cache with a meaning": the memo's keys are beliefs, and a belief on a learning plate encodes P(Global | Counts)). Say so in `KERNEL.md`'s one line for this brief.
4. **`KERNEL.md`**, the line above. **`API.md`**, nothing new, unless you find a sentence on plates that this changes.

**What this brief is not.** The arena's other finding — an episode's cost grows with the Counts (5.3 s at 50–100 records, 22–30 s at 300, at 1,152 Global values), because `posterior_global` recomputes the product of every record's likelihood, raised to its multiplicity, each episode — is **not** this brief's, and you must not fix it by keeping the per-Global weights between episodes. S13 as signed reads a kernel that "persists the posterior they determine" as a structural violation, seen only by the structural kit and the author's reading; whether S13 admits an exact sufficient form of the Counts' likelihood is the author's question, reference first, and is queued. Recompute from the Counts each episode, as today.

Nothing about `decide`'s choices changes. A performance problem elsewhere is a stop, not an approximation. Where the page and this brief disagree, the page decides: put it in `QUESTIONS.md`, with the World, and stop on that point.

**Report in the PR:**

- the cage command's time;
- each suite's line (`structural: …`, `surface: …`, `counts: …`, `library: …`); kit v0.13 on brief 009's kernel is green on every suite;
- a plate of 200 episodes over a declaration with at least 100 Global values whose prior moves every episode (CHARTER v0.2 appendix A's shape with its Global on a grid of at least 100 values, or appendix F's, with a door that answers at random): peak resident memory after 50, 100 and 200 episodes, before and after this brief; and seconds an episode, which should not rise;
- the same plate with the memo kept and dropped: every act and every value identical, as a test under `tests/`;
- the Wordle kits' times (`kit_wordle*.py`), which play v0 Worlds through `wald.run` and should not move.
