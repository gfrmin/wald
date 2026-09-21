# Brief 005c — plan: Wordle under a time price, two adaptive packs and the scoreboard

Read first: `briefs/005c-packs.md`, then the headers of `charter/laws/kit_wordle_think.py` (T0–T3)
and `charter/laws/wordle_meta_oracle.py` (the reduction, the five curves, the omniscient DP), then
`charter/laws/wordle_oracle.py` underneath them. Every number in this brief is the owner's or the
author's; I choose none.

## Where the work is, and where it is not

**Not in `src/wald`.** The think act was built in 005a and given a syntax in 005b. This brief
declares two Worlds that use it and writes down what happens. I generated the two packs and ran
the kit before planning anything, and it says so:

    wordle-think: 15/15 pass      (T0 8-word proof, T1 shape x2, T2 acts/buckets/cost x4, T3 curves)

T2 is the sharp one — every act the kernel plays is the oracle's, every step lands in the oracle's
bucket, and the thought charged is the oracle's — and it passes on the sampled answers at the
seed I can see. So the kernel is not what this brief changes. What it needs is the two packs
committed, the player taught to write down a think act, and two scoreboards with numbers in them
that I computed rather than copied.

## The six things to build

### 1. Two packs, generated and committed

    python3 tools/make_wordle_pack.py --words charter/laws/wordle/words200.txt --depth 1 \
        --out packs/wordle200/adaptive.py \
        --think="11930007676619916058/36661206089336597,-43860132154564000/1929537162596663,1/10000000,41/200"
    python3 tools/make_wordle_pack.py --words charter/laws/wordle/twins124.txt --depth 1 \
        --out packs/twins/adaptive.py \
        --think="99613375741023143/629231233233738,22716401291570095/314615616616869,1/10000000,149/500"

28011 and 11052 lines. Regenerated, never edited: the command that made each one goes at the top
of its scoreboard, so the file can be rebuilt and diffed. The generator is already in this branch
and I do not touch it.

### 2. `tools/play_wordle.py` learns the think act

`Result` has carried `thought`, `steps` and `operations` since 005a and the player has never read
them. It gains, for a pack that declares a think act and for no other:

- the four S7 counts, summed over every episode (`refused` and `struck_cap` and `struck_n` and
  `think`), and the thought paid, total and per episode;
- **predicted against realised operations**, one row per think act: `world.ops[s]` at the live
  count against what `Result.operations` recorded. These are not the same number and are not
  meant to be (E6). The first thought of a run is a cold depth-2 evaluation; every later thought
  at the same node finds brief 004's memo already answered and costs almost nothing. The
  scoreboard says that in words rather than leaving a reader to wonder which number is wrong.

A v0 pack's scoreboard must come out byte for byte as before: `packs/wordle/SCOREBOARD.md` and
`packs/wordle200/SCOREBOARD.md` are regenerated and diffed to prove it.

### 3. `tools/curves.py` — the five E3 curves, computed here

The kit prints the oracle's table and mine must match it, which is only a test if I compute mine.
So this tool computes the five policy values along the r grid `{0, 1/10⁸, 3/10⁸, 1/10⁷, 3/10⁷,
1/10⁶}` from **my kernel's own acts**:

| curve | how it is got |
|---|---|
| fixed d = 1 | the act `decide` gives at depth 1, at every node |
| fixed d = 2 paying c | the act at depth 2, charged `r·ops(\|C\|)` at every step with n > 1 and a guess left |
| best fixed | the larger of those two — hindsight, not a policy |
| adaptive | `decide.step`: the bucket and the charge are the kernel's |
| omniscient | the DP of `wordle_meta_oracle`'s docstring: at each node take whichever of the two continuations is worth more net of c, ties to the shallow one |

The arithmetic — the expectation over answers, the feedback classes, the DP — is the tool's, and
the game is the tool's; every *act* is `decide`'s and every *bucket and charge* is `step`'s. That
is the same division the kit makes: it is a measuring instrument standing where the kit stands,
which is why it may call `wald.decide` as `wald.kit_adapter` does. It chooses nothing, compares no
probability, and is outside `src/`.

This runs offline and writes into the scoreboards; nothing in the cage command runs it, so its
wall-clock is mine and not CI's.

### 4. Two scoreboards

`packs/wordle200/SCOREBOARD.md` and `packs/twins/SCOREBOARD.md`, each with, at the declared
r = 1/10⁷: the attempts distribution, the mean, the worst, the wrong claims, the thought paid, the
predicted-against-realised operations, the four S7 counts, the census with its `fitted` count, and
the wall-clock. Then the five curves along the grid, and one line of regret: the adaptive agent
against the omniscient meta-policy at the declared r, and against the best fixed depth.

`packs/wordle200/SCOREBOARD.md` already exists for `d1.py` and `d2.py`. The adaptive pack belongs
beside them in the same file — it is the same lexicon, and the price of the floor that file
already measures is exactly what the think act is buying.

### 5. Report what it says, and do not tune it

The author's oracle says, and the kit printed at my seed:

- **words200**: every curve but the adaptive one is −2.6450 at every r; the adaptive agent
  overpays below r ≈ 3/10⁷ (−3.8570 at 1/10⁷ against −2.6450).
- **twins124**: fixed d = 1 (−3.4194) beats free depth 2 (−3.4516), and the omniscient gains
  0.0162 at r = 0 (−3.4032) by thinking at one child of the root.

Both hold. Nothing gets tuned to change them; if my episodes and the oracle disagree on an act, a
bucket or a cost, that is a `QUESTIONS.md` entry with the answer and both traces, and I stop on
that point.

### 6. `KERNEL.md`

One line: the two adaptive packs and what they are for. `tools/curves.py` gets its one-line reason
to exist beside the other three tools.

## How I will know it is right

- `sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100`, green, and inside CI's 30 minutes.
- `kit_wordle_think` alone at several seeds and `--episodes` above the default: T2 on answers the default seed never draws.
- My curve table against the kit's printed one, digit for digit, on both lexicons and all six r.
- The two v0 scoreboards regenerated and diffed: no byte moves.
- The packs regenerated from the committed command and diffed: no byte moves.

## What this brief does not touch

`src/wald`, unless the kit says otherwise — and it does not. No Wordle in the kernel: the feedback
rule stays in `tools/` and in the charter's oracle. The generator is the author's this time and I
leave it alone. The E3 sweep's *owner-facing* question — which r to declare — is the author's
proposal and I report it, not choose it.
