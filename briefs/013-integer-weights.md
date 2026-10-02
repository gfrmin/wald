# Brief 013 — the lookahead over integer weights

**Done when** the `cage` check is green on a pull request from `b/013-integer-weights`, under `kit-v0.14`. No page changes, no kit changes, no new public name: `wald.__all__` keeps its fourteen (ST1). This is a performance item under v0.2 as signed. Every act, every value, every refusal and every E6 operation count stays as it is.

**The owner's numbers for this brief:** none. The owner gave the go on 2026-10-02.

**The measurement.** On the arena's `omniscience-p1-c0` pack, an episode's cost grows with the Counts: 1.3 s at no records, 20.0 s at 300 and 57.2 s at 600. The pack has 1,152 Global values × 12 locals = 13,824 states, with N = d = 3, from `gfrmin/wald-arena` stage 2, master `51f5adc`. Packs are not committed there, so a copy is at `/srv/wald-measure/omniscience-p1-c0.py` on steel, sha256 `7cc140d806042635dfbbc4d496ee99cbf36946dc1475c48d2bdad0f0ea21d2cf`. Check the hash before you measure. The author measured it on 2026-10-01; the record is wald-charter's `measurements/2026-10-01-counts-likelihood/` (in your `charter/` checkout at the lock), whose README and both scripts are the reference for this brief.

- **The Counts are not the cost.** They are already the sufficient statistic (CHARTER v0.2 §4), and P(Global | Counts) is about a tenth of an episode.
- **The cost is `Fraction` arithmetic in the lookahead.** The lookahead carries the posterior's exact masses, about 16 bits a record and so about 9,700 bits each at 600 records. It sums them over the states as `Fraction`s, and each mass has its own reduced denominator. At 600 records, 53.5 of 65.6 s are `math.gcd`, all of it in `Fraction._add` under `_dot` and `_mass`. Only 71 `_value` nodes are visited.
- **Scaling to integers removes most of it.** The same measure, scaled by one common denominator so that every weight is an `int`, plays the same episode in 6.3 s instead of 19.6 s at 300 records, and 14.6 s instead of 55.1 s at 600. The acts are the same and the final belief is the same.
- **`posterior_global` does more work than it needs.** It normalises after every token (`belief._update`). The reference's `post_global` multiplies every token in and normalises once. That gives the same rationals at 2.3–2.8× less cost.

**What to build:**

1. **The lookahead runs on integer weights.** Before an episode's lookahead, bring the measure to integers by one common denominator. Do the same per act for its kernel rows and `u_end`, and for the terminal utilities, so that `_split`, `_dot` and `_mass` add and multiply `int`s. The lookahead is already written unnormalised ("mass(m) E_{m/mass(m)}[f]"), so a measure scaled by a constant gives values scaled by the same constant. Undo the scaling where a value leaves the lookahead: in `decide`'s and `step`'s returns, in `quantities`, and in the price comparisons that `_cap` and the floor make against a per-act price.
   - The arithmetic stays exact: no float, no bound, no approximation.
   - What is compared stays exactly what is compared today. J3's ties are the same ties.
2. **The scaling is a function of the belief alone.** Two equal beliefs must reach the same memo keys and the same `Sameness` classes. This holds in `run`, on a plate, and across plates, since brief 014 relies on it. A representative that is canonical for the projective class does this: lcm of the denominators, then the gcd of the numerators taken out. Neither the scaled measure nor its denominator is kept past the call, except as memo keys that already exist today.
3. **`posterior_global` normalises once.** Multiply every record's likelihood, raised to its multiplicity, into P(Global), then normalise. A multiset no Global value can have written still raises `WorldFalsified` (zero total mass), with the same message.
   - S13 stands as signed: the posterior is recomputed from the Counts at every episode, and nothing about it is kept between episodes.
4. **E6 counts the same operations.** `_tally` counts products and sums, not their cost. If the scaling itself is arithmetic the page's operations do not name, it is not tallied. Say in `KERNEL.md` why that is right, citing E6.
5. **`KERNEL.md`:** one line for this brief. **`API.md`:** nothing, unless a sentence there changes.

**What this brief is not.** Filtered arithmetic (float bounds with an exact fallback on a near-tie) performs different operations. It is E6's and the think kit's question before it is the kernel's, so it is out of scope. A performance problem elsewhere is a stop, not an approximation. Where the page and this brief disagree, the page decides: write it in `QUESTIONS.md`, with the World, and stop on that point.

**Report in the PR:**

- the cage command's time, and each suite's line;
- the measurement's table again, before and after this brief, at T = 0, 300 and 600 records on the arena's `omniscience-p1-c0` pack (the README says how to build each T). Report `episode_prior` and `_play` seconds, and show that the acts and the final belief are identical;
- a test under `tests/` showing that the integer-weight lookahead and the `Fraction` one, on random Worlds and on a plate with Counts, give every act, every value (`Plate.values()`'s text) and every E6 count the same;
- the Wordle kits' times (`kit_wordle*.py`). They should fall or stay level.
