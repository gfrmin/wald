# Brief 003 — the first pack: Wordle on forty words

**Done when** the `cage` check is green on a pull request from `b/003-wordle`. Kit v0.5 adds `kit_wordle.py`: read its header first, it says exactly what is judged.

1. **`tools/make_wordle_pack.py`** writes `packs/wordle/pack.py` from `charter/laws/wordle/words.txt` (40 words, in that order). Commit the generated pack: every number in it must be visible in the repository. The generator is ordinary Python outside `src/`; the pack is SURFACE and nothing else.
2. **The World.** States: the words, uniform prior (`data`). Every word is a `once` guess, price 1 (`data`), whose kernel is the game's feedback written out row by row (`data`), duplicate letters handled as the game does: greens first, then yellows while unmatched copies remain. All-green (`ggggg`) ends the episode at 0. The terminal acts are the claims `claim <word>`: −1 if right, a loss if wrong, the loss an `elicited` `param`. Five guesses and a claim are Wordle's six attempts, so `horizon(5)`. `depth(1)`, `elicited`. Closed.
3. **Why claims.** A World whose only terminal act is "give up" is degenerate at depth 1: one look ahead sees a 1-in-40 hit and then the loss, so the agent gives up at once. Your kernel and the oracle agree on that; it is what CHARTER E3 says, since lookahead values the frontier at V_0, the value of stopping now. Stopping has to be worth something. Do not work around this in code: it is a fact about the declared World, and it is said in the World.
4. **`tools/play_wordle.py`** plays all forty answers through `wald.episode.run` with a door that returns the game's feedback, and writes `packs/wordle/SCOREBOARD.md`: the distribution of attempts, the mean, any failures, the declared depth, and the census by source from `wald.surface.census`.
5. **No fast paths.** Exact arithmetic, the kernel as it is. If something is too slow, measure it and say so in the PR: that measurement is the input to brief 004, where fast paths arrive under CHARTER E2.

If the kit's feedback rule and yours disagree on any (guess, answer), that is a `QUESTIONS.md` entry with the pair.
