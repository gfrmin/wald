# Brief 004 — exact fast paths (CHARTER E2): Wordle on two hundred words

**Done when** the `cage` check is green on a pull request from `b/004-fast-paths`. Kit v0.6 adds `kit_wordle_big.py` and a second oracle, `wordle_oracle.py`: read both headers first.

**The owner's numbers for this brief** (you choose none): `loss = -7`; `depth(1)` in one pack and `depth(2)` in the other.

1. **Two packs**, `packs/wordle200/d1.py` and `packs/wordle200/d2.py`, from `charter/laws/wordle/words200.txt` (200 words, in that order; its first forty are brief 003's). The same World as brief 003 in every respect but the words, and the two differ only in `depth`. Extend your generator; commit both packs.
2. **Make the kernel fast enough to play them, without changing one act.** Your own measurement says where the time goes: |T|×|Ω| inside |O|×classes, and it does not fall as the game is won. CHARTER E2 allows an exact fast path to replace `push`, `condition` and expectation, and nothing else: `decide`, the lookahead and the loop stay written once (E5). Things that are exact, and general to every World, not to Wordle:
   - a belief need not carry, or visit, its zero-mass states;
   - acts that are identical on the support of the belief are one act, and J3 says which: the first in menu order. (Two hundred claims are at most m+1 different acts on a support of m states; guesses collapse the same way.)
   - a value already computed for a belief, a menu and an n need not be computed again.
   Nothing approximate: no pruning by a threshold, no sampling, no floats. If you want a fast path that is not on this list, it must be exact for every World, and the maths kit (300 random Worlds, forced ties, zero entries) will hold you to it.
3. **No Wordle in `src/wald`.** The kernel must not know what game it is playing: no feedback function, no word list, no special case for uniform priors or deterministic kernels beyond what the three items above already give you. The second oracle is allowed to be specialised; you are not.
4. **`packs/wordle200/SCOREBOARD.md`**: for each depth, all 200 answers: the distribution of attempts, the mean, the worst, failures, wall-clock time, and the census. Then one line: the measured price of the floor on this World, mean attempts at d=1 minus mean at d=2. Report whatever it is. (The author's oracle says it is small here; do not tune anything to make it larger.)
5. **Timing.** The whole cage command must finish inside CI's 30-minute limit. Say in the PR how long each part takes.

If your kernel and the second oracle ever disagree on an act, that is a `QUESTIONS.md` entry with the answer, the depth and the two act sequences: one of us is wrong, and it may be the oracle.
