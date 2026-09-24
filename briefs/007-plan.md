# Brief 007 — plan: what is learned between episodes

Read first: `charter/CHARTER-v0.2.md` whole, INTERFACE.md's kit v0.11 section, `kit_counts.py`,
`counts_check.py`. The owner's numbers for this brief: none.

## Where it stands

The first cage run on `b/007-counts` (3 min 03 s), before any code:

    charter ok: kit-v0.11 at a67d561…
    structural 37/37, surface 123/123, wordle 14/14, wordle200 16/16, think pass, wordle-think 27/27
    FAIL L1 wald.law names charter-v0.1, surface-v0.1 and the kit tag of the lock   got kit-v0.10, lock kit-v0.11
    library: 14/15 pass
    counts kit integrity: reference clean, 10 poisons killed, the pinned Worlds of six sessions hold
    FAIL counts: the adapter lacks ['prior', 'persist', 'declare', 'disclose', 'e7', 'score', 'world']

L1 is `law.KIT`, which follows the lock. L1 still asks `law["charter"] == "charter-v0.1"` although
v0.2 is now signed; I keep it and ask (Q7).

## The shape

A state of a v0.2 World is the pair `(l, g)`. Everything v0 already does — `build`, `Kernel`,
`Belief`, `decide`, `step`, the episode loop — takes such a state as it takes any hashable, so the
amendment is a layer *around* a v0 World and changes nothing inside one (C21).

| module | holds |
|---|---|
| `plated.py` | `Plated`: the v0 World over Ω = {(l, g) : P(g) P(l\|g) > 0}, each state's Global, P(Global), P(state \| Global), the After-act (name, price, a Kernel per end), the shipped Counts and falsifier. `build` converts; `declare` adds GLOBAL, AFTER, PLATE, UNSCORED and v0.1's rulings. `world.declare` hands it any dict with a `globals` key |
| `counts.py` | L(record \| g); P(Global \| Counts) as `belief._update` applied once per distinct record with likelihood L^count — the one update, not a second; the episode's prior; `counts_sha`; realisable/expressible (S13); the leave-one-out Score (S14); E7's lines |
| `disclose.py` | S15: realisable designs, classes of inseparable Global values, the classes whose members disagree on what an act can feel; its text |
| `plate.py` | `Plate` and `plate(world)`: `run(door)` = the prior from Counts, `episode._play` unchanged, the After-act asked by name after the fire, the record into Counts; J26 |

`episode.run` becomes `_play(world, prior(world), door)`, so the plate's episode is literally v0's.
`Result` gains `record`.

The E7 predictive conditions each Global's local on the history by `_update` and pushes the next
kernel through it, which equals counts_check's ratio of sequence probabilities and keeps the belief
update in one place.

## Readings I take, each checked against the reference

- An ending outcome is an outcome in `ends` or a key of `u_end`; its end is `"end:k=o"`.
- The After-act declares a kernel for every **end** — each terminal *and* each `end:k=o` (page S12,
  "declared for every end"). `counts_check.refuse` asks exactly the terminals; that is the reference
  disagreeing with the page on a World with an ending outcome and an After-act: Q8. No kit World has
  both.
- A falsifier from within an episode is `(draws up to and with the falsifying one, None, None)`, the
  stand-in's; `realisable` then refuses it if shipped. Q9.

## Tests

Appendix A through `wald.plate` (3/5, 2/5; 39/50 and 17/50; 3/11, 8/11 either order), appendix K's
falsified plate, and the kit's disclosure/E7/Score Worlds against `counts_check`.
