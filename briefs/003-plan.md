# Plan — Brief 003, Wordle on forty words

Law: `charter/CHARTER.md` and `charter/SURFACE.md`, both signed. Judge: the command in CLAUDE.md,
which at kit v0.5 also runs `laws/kit_wordle.py` — W1 (the pack is lawful and my checker elaborates
it to the reference's World), W2 (the pack **is** Wordle on `laws/wordle/words.txt`, checked table by
table against a feedback rule the kit computes itself), W3 (on answers from a seed I never see, every
act the kernel plays is the oracle's `decide_min(d, n)` at that belief, and every episode ends within
the horizon).

Nothing in `src/wald` changes for this brief. This is a pack, two tools, and a scoreboard — the first
time the kernel is asked to play a game rather than pass a test.

## 1. The World, and why it is this one

| | |
|---|---|
| Ω | the 40 words, in the file's order. Uniform prior, `data`. |
| O | every word, a `once` guess at price 1 (`data`), kernel the game's feedback row by row (`data`) |
| ending | `ggggg` ends the episode earning 0 (`elicited`, with the rest of the utility) |
| T | `claim <word>`: −1 if right, `loss` if wrong |
| clock | `horizon(5, data)` — five guesses and a claim are Wordle's six attempts; `depth(1, elicited)` |
| stance | `closed`: the answer is one of the forty, and the pack says so |

**Why claims, and why the loss is what it is.** The brief is right that a World whose only terminal
act is "give up" is degenerate at d = 1, and it is worth writing down *why*, because the arithmetic
also fixes the loss. Under CHARTER §2 a one-step lookahead values the frontier at V₀ — the value of
stopping there — so with m candidates left, a loss L < 0 for a wrong claim and −1 for a right one:

    V_0(b)   = L + (|L| − 1)/m                      claim the likeliest word
    Q_1(b,g) = (m−1)/m · L + (|L| − 1)·c/m − 1      guess g, c non-green feedback classes
    Q_1 − V_0 = [ |L| + (|L| − 1)(c − 1) − m ] / m

So guessing beats stopping exactly when `|L| + (|L|−1)(c−1) > m`. With "give up" alone the only
terminal value is a constant and the frontier is worth the same everywhere, so the difference is
−1 and the agent stops at once: nothing the code does can change that, and nothing in the code
should try. With claims, a first guess that cuts 40 words into ~20 classes needs only `|L| > ~2`.

The floor on `|L|` is not free, though: at m = 1 the agent must be indifferent or better between
claiming the known word (−1) and guessing it (0 − 1 = −1 — all-green, ending at 0, after paying 1).
That is an exact tie, and J3 hands it to the terminal act, so the episode ends on a claim. And the
kit requires one loss below −6. Both point the same way: **five guesses and a claim cost 6, so a
wrong claim must be worse than playing the game out honestly and claiming right.** `loss = −7`,
one worse, an `elicited` `param` — the only number here that is anybody's opinion.

## 2. Pieces

| piece | what it is |
|---|---|
| `tools/make_wordle_pack.py` | writes `packs/wordle/pack.py` from the word list: the feedback rule, greens then yellows while unmatched copies remain, and a writer that wraps every table so each number stays visible |
| `packs/wordle/pack.py` | committed, generated, SURFACE and nothing else |
| `tools/play_wordle.py` | plays all forty answers through `wald.episode.run` behind a door that is the game, and writes the scoreboard |
| `packs/wordle/SCOREBOARD.md` | attempts, mean, failures, the declared depth, and the census by source |

The feedback rule is the one place my code could silently differ from the kit's, so I check it the
only way that settles it: **all 1,600 (guess, answer) pairs against `kit_wordle.feedback`**, before
trusting the pack. A disagreement is a `QUESTIONS.md` entry with the pair.

## 3. Size and speed, measured

No fast paths (brief 003, and CHARTER E2 is brief 004's). Exact rationals, the kernel as written.
What that costs, measured on this machine:

- The pack is 1,270 lines and 4,883 quantities: `data` 1,681 (prior 40, prices 40, 1,600 kernel
  rows, the horizon), `elicited` 3,202 (1,600 claim cells, 1,600 ending cells, the depth, `loss`),
  `fitted` 0.
- `check` + `declare`: well under a tenth of a second. Elaboration is not the cost.
- **`decide` at the root: about 2 s.** At d = 1 it is V₀ over 40 claims (40 × 40 expectation terms)
  plus Q₁ for each of 40 guesses, each summing over that guess's feedback classes and valuing every
  one at V₀ again: ≈ 1.3 M exact-rational operations per call.
- An episode is 2–3 acts, so ≈ 2.2 s; all forty answers ≈ 90 s; the whole `cage` command ≈ 45 s.

That is the number brief 004 gets to attack. The shape of the cost is worth saying too: it is
`|T| × |Ω|` inside `|O| × (classes)`, and the belief keeps all forty states after conditioning
because the reference does — zeros included — so the work per decide barely falls as the game is won.

## 4. Order of work

1. `make_wordle_pack.py`; check the feedback rule against the kit's on all 1,600 pairs.
2. Generate, then `tools/wald_check.py packs/wordle/pack.py` — the loop brief 002 built for this.
3. `play_wordle.py`, all forty answers, and read the failures before the mean.
4. The kit, at seed 1 and at seeds of my own, with more episodes than the default 6.
5. `KERNEL.md`, tests, PR with the measurement.

## 5. What I expect to see

With one look ahead the agent should open with the same guess every time (the belief is the same),
split the forty words, and claim as soon as one candidate remains — so ~2–3 attempts, never the
six the game allows, and no failures. If any answer fails, the interesting question is whether the
horizon or the depth bound it, and the scoreboard says which.
