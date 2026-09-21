# Wordle — scoreboard

`packs/twins/adaptive.py`, played by `wald.episode.run` through a door that answers
with the game's feedback. Every act is the kernel's own: the depth below is what the pack
declares, and the kernel plays `decide_min(d, n)` (CHARTER E3).

This pack declares a **think act** (CHARTER v0.1): at a step with room left it
may buy one deeper look, at a price the pack itself declares, and play the act that look
found. Its column says `1 + θ` — the floor is still 1, and what it buys is not a depth it
declares but a computation the one `decide` chose to pay for.

|  | **depth 1 + θ** |
|---|---|
| words (states) | 124 |
| horizon | 5 |
| **declared depth** | **1** + θ |
| answers played | 124 |
| solved | 123 / 124 |
| **mean attempts** | **3.403** |
| worst | 6 |
| first episode | 7.1 s |
| all answers | 13.7 s |

## Quantities by source

`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,
mixture weight, price, the horizon and the depth once, however it is written.

| source | depth 1 + θ |
|---|---|
| data | 15626 |
| elicited | 30757 |
| fitted | 126 |
| **total** | **46509** |

The prior, the prices, the horizon and every kernel row are `data` — facts of the game
and of the word list. What is `elicited` is the owner's: the depth, the utilities,
including `loss`, and — where a think act is declared — Depth⁺, the Fraction and the
Rate. What is `fitted` is the Cost table: two parameters fitted by the author to the
kernel's own operation counts, read by 124 cells, each of which counts once under
its table's source (SURFACE v0.1 K17). A fitted table carries its held-out Score, and
this one does.

## Depth 1 + θ — `packs/twins/adaptive.py`

An attempt is an act the agent played: each guess, and the claim it ends on.

| attempts | answers |  |
|---|---|---|
| 1 | 1 | # |
| 2 | 21 | ################# |
| 3 | 49 | ######################################## |
| 4 | 36 | ############################# |
| 5 | 14 | ########### |
| 6 | 3 | ## |

Failures:
- **years**: watch → bound → right → fears → pears → claim sears (TERMINAL)

<details><summary>every answer</summary>

| answer | attempts | acts |
|---|---|---|
| light | 4 | watch → bears → found → light |
| might | 5 | watch → bears → found → light → might |
| night | 4 | watch → bears → found → claim night |
| right | 3 | watch → bears → claim right |
| sight | 3 | watch → bears → claim sight |
| tight | 6 | watch → bears → found → light → might → claim tight |
| fight | 4 | watch → bears → found → claim fight |
| eight | 3 | watch → bears → claim eight |
| bight | 3 | watch → bears → claim bight |
| wight | 2 | watch → claim wight |
| bound | 4 | watch → sinks → bumps → claim bound |
| found | 4 | watch → sinks → bumps → found |
| hound | 2 | watch → hound |
| mound | 4 | watch → sinks → bumps → claim mound |
| pound | 4 | watch → sinks → bumps → claim pound |
| round | 5 | watch → sinks → bumps → found → claim round |
| sound | 3 | watch → sinks → claim sound |
| wound | 3 | watch → winks → claim wound |
| batch | 3 | watch → bumps → claim batch |
| catch | 3 | watch → bumps → catch |
| hatch | 4 | watch → bumps → catch → hatch |
| latch | 5 | watch → bumps → catch → hatch → claim latch |
| match | 3 | watch → bumps → claim match |
| patch | 3 | watch → bumps → claim patch |
| watch | 1 | watch |
| bower | 3 | watch → bumps → claim bower |
| cower | 2 | watch → claim cower |
| lower | 3 | watch → bumps → claim lower |
| mower | 3 | watch → bumps → claim mower |
| power | 3 | watch → bumps → claim power |
| tower | 2 | watch → claim tower |
| bills | 4 | watch → sinks → bumps → claim bills |
| fills | 4 | watch → sinks → bumps → fills |
| gills | 5 | watch → sinks → bumps → fills → claim gills |
| hills | 3 | watch → hound → claim hills |
| kills | 3 | watch → sinks → claim kills |
| mills | 4 | watch → sinks → bumps → claim mills |
| pills | 4 | watch → sinks → bumps → claim pills |
| sills | 3 | watch → sinks → claim sills |
| tills | 2 | watch → claim tills |
| wills | 3 | watch → winks → claim wills |
| bears | 3 | watch → bound → claim bears |
| dears | 3 | watch → bound → claim dears |
| fears | 4 | watch → bound → right → fears |
| gears | 4 | watch → bound → right → claim gears |
| hears | 2 | watch → claim hears |
| nears | 3 | watch → bound → claim nears |
| pears | 5 | watch → bound → right → fears → pears |
| rears | 4 | watch → bound → right → claim rears |
| sears | 6 | watch → bound → right → fears → pears → claim sears |
| tears | 2 | watch → tears |
| wears | 2 | watch → claim wears |
| years | 6 | watch → bound → right → fears → pears → claim sears (**TERMINAL**) |
| baste | 2 | watch → baste |
| caste | 2 | watch → caste |
| haste | 2 | watch → claim haste |
| paste | 3 | watch → baste → paste |
| taste | 4 | watch → baste → paste → claim taste |
| waste | 2 | watch → claim waste |
| kinks | 4 | watch → sinks → lumps → kinks |
| links | 4 | watch → sinks → lumps → claim links |
| minks | 4 | watch → sinks → lumps → claim minks |
| pinks | 4 | watch → sinks → lumps → claim pinks |
| rinks | 5 | watch → sinks → lumps → kinks → claim rinks |
| sinks | 2 | watch → sinks |
| winks | 2 | watch → winks |
| balls | 3 | watch → might → balls |
| calls | 3 | watch → lower → claim calls |
| falls | 4 | watch → might → balls → claim falls |
| galls | 3 | watch → might → claim galls |
| halls | 2 | watch → claim halls |
| malls | 3 | watch → might → claim malls |
| walls | 2 | watch → claim walls |
| backs | 4 | watch → lower → bumps → claim backs |
| hacks | 2 | watch → claim hacks |
| jacks | 4 | watch → lower → bumps → jacks |
| lacks | 3 | watch → lower → claim lacks |
| packs | 4 | watch → lower → bumps → claim packs |
| racks | 3 | watch → lower → claim racks |
| sacks | 5 | watch → lower → bumps → jacks → claim sacks |
| tacks | 3 | watch → caste → claim tacks |
| docks | 3 | watch → could → claim docks |
| hocks | 2 | watch → claim hocks |
| locks | 3 | watch → could → claim locks |
| mocks | 4 | watch → could → mower → claim mocks |
| rocks | 4 | watch → could → mower → claim rocks |
| socks | 4 | watch → could → mower → claim socks |
| bumps | 4 | watch → sinks → bound → claim bumps |
| dumps | 4 | watch → sinks → bound → claim dumps |
| humps | 3 | watch → hound → claim humps |
| jumps | 5 | watch → sinks → bound → pills → claim jumps |
| lumps | 5 | watch → sinks → bound → pills → claim lumps |
| pumps | 5 | watch → sinks → bound → pills → claim pumps |
| dates | 4 | watch → might → found → claim dates |
| fates | 4 | watch → might → found → claim fates |
| gates | 3 | watch → might → claim gates |
| hates | 2 | watch → claim hates |
| mates | 3 | watch → might → claim mates |
| rates | 4 | watch → might → found → rates |
| sates | 5 | watch → might → found → rates → claim sates |
| deeds | 5 | watch → sinks → bound → dears → claim deeds |
| feeds | 5 | watch → sinks → bound → dears → claim feeds |
| heeds | 3 | watch → hound → claim heeds |
| needs | 3 | watch → sinks → claim needs |
| reeds | 5 | watch → sinks → bound → dears → claim reeds |
| seeds | 3 | watch → sinks → claim seeds |
| weeds | 3 | watch → winks → claim weeds |
| boast | 3 | watch → tears → claim boast |
| coast | 2 | watch → claim coast |
| roast | 3 | watch → tears → claim roast |
| toast | 3 | watch → tears → claim toast |
| could | 2 | watch → could |
| would | 3 | watch → winks → claim would |
| bunch | 3 | watch → bumps → claim bunch |
| hunch | 3 | watch → bumps → hunch |
| lunch | 4 | watch → bumps → hunch → claim lunch |
| munch | 3 | watch → bumps → claim munch |
| punch | 3 | watch → bumps → claim punch |
| kings | 3 | watch → sinks → claim kings |
| rings | 4 | watch → sinks → pound → claim rings |
| sings | 3 | watch → sinks → claim sings |
| wings | 3 | watch → winks → claim wings |
| dings | 4 | watch → sinks → pound → claim dings |
| pings | 4 | watch → sinks → pound → claim pings |

</details>

### The think act

The pack declares Depth⁺ 2, a Fraction f = 1/2, a fitted Cost table and a
Rate r = 1/10000000. At every step `decide⁺` settles into one of S7's four buckets, in
precedence order, and only the last of them costs anything.

| bucket | steps | share | what it means |
|---|---|---|---|
| `struck_n` | 20 | 4.7% | n ≤ d, or no guess left: there is nothing a deeper look could reach |
| `struck_cap` | 87 | 20.6% | the cap leaves less room than the thought costs; f is never read |
| `refused` | 0 | 0.0% | Q(θ) was formed and θ still lost |
| **`think`** | **315** | 74.6% | **θ bought: one deeper look, paid for, and the act it found is played** |
| **total steps** | **422** |  |  |

**Wrong claims**: 1 of 124 — `years`. A wrong claim is the horizon running out, not a mistake the
kernel made: `decide` plays the act of highest value at the depth it is allowed, and when
no guess left in the menu can separate the candidates in the steps remaining, claiming one
of them is the best act there is.

**Thought paid**, over all 124 episodes: 562873307006343789366593/12584624664674760000000 (≈ 44.7271) of utility,
which is 562873307006343789366593/1560493458419670240000000 (≈ 0.360702) an episode. It is not a price: no act was
executed for it, the door never saw it, and it consumed no horizon (C17).

### Predicted against realised operations (E6)

The Cost table says how many operations a thought at s live states will take. The kernel
counts what it actually took, and the two are printed side by side and never compared by
anything: the prediction is what the policy is charged for, the count is a measurement.

| s (live states) | thoughts | ops predicted | counted, least | counted, most | counted 0 |
|---|---|---|---|---|---|
| 2 | 20 | 637 | 0 | 586 | 10 |
| 3 | 21 | 1,440 | 0 | 1,136 | 14 |
| 4 | 28 | 2,570 | 0 | 2,064 | 21 |
| 5 | 25 | 4,030 | 0 | 3,576 | 20 |
| 6 | 30 | 5,824 | 0 | 6,206 | 25 |
| 7 | 7 | 7,956 | 0 | 8,627 | 6 |
| 8 | 8 | 10,429 | 0 | 8,416 | 7 |
| 9 | 18 | 13,247 | 0 | 25,416 | 16 |
| 34 | 34 | 205,892 | 0 | 206,166 | 33 |
| 124 | 124 | 3,544,372 | 0 | 3,544,368 | 123 |

Over all 315 thoughts the kernel counted 3,882,258 operations, against 447,270,635 predicted —
about 1% of the Cost table's number, and 275 of the thoughts counted nothing at all.

That is the memo of brief 004 and not a fault in the fit. A thought is one evaluation of
one belief at depth 2, and the World keeps what it has already worked out; the first
thought at a node pays for it and every later thought at **that same node** finds the
answer there. The rows above group by s, the count of live states the Cost is keyed on,
and two different nodes can have the same s — which is why the least and the most in a
row differ, and why the `counted 0` column is the memo and not the model. The page
expects this: two evaluators may count differently, and each prints its own count
beside the same prediction (E6). The policy is charged the prediction, always, and never
the count (J15) — so nothing the memo saves ever reaches a value.


### The five curves of E3

Computed by `tools/curves.py` over the declared model — exactly, in rationals, over every
answer — from this kernel's own acts: `decide` gives the act at a depth, `decide⁺` gives
the bucket and the charge, and the tool does the expectation and the backward induction.
`laws/kit_wordle_think.py` prints the same table from the author's oracle, and the two
agree to every digit printed here.

Utility per episode. **Larger is better**; a guess costs 1, a wrong claim -7.

| r | fixed d=1 | always d=2 | best fixed | **adaptive** | omniscient |
|---|---|---|---|---|---|
| `0` | -3.4194 | -3.4516 | -3.4194 | -3.4516 | -3.4032 |
| `1/100000000` | -3.4194 | -3.4877 | -3.4194 | -3.4877 | -3.4037 |
| `3/100000000` | -3.4194 | -3.5598 | -3.4194 | -3.5598 | -3.4046 |
| `1/10000000` **←** | -3.4194 | -3.8123 | -3.4194 | -3.8123 | -3.4079 |
| `3/10000000` | -3.4194 | -4.5338 | -3.4194 | -4.5337 | -3.4173 |
| `1/1000000` | -3.4194 | -7.0587 | -3.4194 | -3.4564 | -3.4194 |

**Regret at the declared rate** r = 1/10000000:

- against the omniscient meta-policy: **0.4044** of utility per episode.
- against the best fixed depth in hindsight: **0.3930**.
- against thinking never (fixed d = 1): **0.3930**,
  and the thought it paid for was 0.3607 an episode.

Those two differ by 0.0323: the thoughts did not only cost, they changed
acts, and on balance they changed them for the worse by that much. Look at the r = 0
row for why. With thinking free, the deep agent still scores 0.0323 below the
shallow one — **depth 2 is worse here than depth 1**, and no price is involved. The
deeper look is exact, V₂ and not an estimate, so what it costs is not error: it is the
step of the horizon spent reaching for it, on a lexicon of near-twins where one look
cannot separate the candidates and the clock is what binds. E3 is not the claim that
deeper is better; it is the question of what the floor costs, and on this World the
answer is negative.

