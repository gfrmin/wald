# Brief 005a — plan: the think act

CHARTER v0.1 adds one entry to the menu and one page of arithmetic around it. Nothing in v0 moves:
the lookahead, the argmax and the episode loop stay written once (E5), and the three fast paths of
brief 004 stay underneath them. What is new is a step that decides, at the floor, whether to pay
for a deeper one — and that decision is made by `decide`, not beside it (S8).

## What the page asks for, in the order I will build it

| # | the page | where it goes |
|---|---|---|
| 1 | the Depth⁺, Fraction, Cost, Rate and Score tables (§1) | `world.py`: five more fields, five more refusals |
| 2 | `cap(b,M)`, one pass over the live states and the menu (J12) | `decide.py`, beside `_value`, reading no lookahead |
| 3 | ĝ, c, the strike, Q(θ) and the buy (§2) | `decide.step`, the one place θ is on the menu |
| 4 | the operation counter (E6) | `belief.py`, where the arithmetic on ℚ actually happens |
| 5 | the loop's one changed line, and three more fields on `Result` | `episode.py` |
| 6 | `step` for the kit | `kit_adapter.py` |

## 1. The tables (§1, S3, S6, S10)

`declare` gains five refusals, by name, with INTERFACE's exact conditions:

- `FRACTION` — f outside [0,1], or a Fraction whose source is not `elicited`/`fitted`.
- `COST` — an ops cell missing (the table is total over s = 1 … |Ω|) or negative, or a Cost whose
  source is not `elicited`/`fitted`.
- `DEPTH_PLUS` — a World with θ whose (d, d⁺, N) is not (1, 2, ≥ 2). **[J11]**
- `RATE` — a Rate whose source is not `elicited`.
- `UNSCORED` — a `fitted` Fraction or Cost with no Score. **[J18]**

A negative Rate the page does not name: §1 says r ∈ ℚ≥0, so it must be refused, and
`meta_check.refuse_meta` — which INTERFACE calls the reference and the definition — refuses it by
`COST`, in the line that also refuses the ops table. I adopt the reference's name and record it,
as this kernel did for `PRICE` and the `fresh` half of `SHARED_SOURCE` under kit v0.1.

A spec without `dplus` is a v0 World: none of the five is read, nothing is refused by the new
names, and every v0 suite must stay green. That is the first thing I will check after the change.

**The probe.** C19 hands the kernel `dplus = N` — a dict J11 refuses as a pack — to prove the cap
does not read d⁺. So the kit's shim converts rather than declares: `declare` becomes
`build` (the conversion of §1, refused where it cannot be built) plus the pack's rulings, and
`kit_adapter` calls `build`. That is what the shim already does for the clock and the S5 stance,
and it is why INTERFACE says the kit never declares a pack.

## 2. The cap (J12), and why it is not deliberation

    best(ω)   = max( max_t u(ω,t), max u_end(ω,k,o) over k in M∩O with K_k(o|ω) > 0 )
    cap(b,M)  = max( V_0(b,M), Σ_ω b(ω) best(ω) − min_{k in M∩O} price(k) ),  V_0 if M∩O = ∅

One pass over the live states and the menu. It reads V_0 — which is `_value` at n = 0, the max over
terminal acts and no lookahead at all — the utilities, the ending outcomes a kernel can emit, and
the prices. It never calls `_value` at n > 0, and it never reads d⁺ (C19). On `FIXED_CAP` it must
be ≥ V₅ = 40951/2000; the per-state form gives 50 there, and the root-posterior form gives 10,
which is why the page took the per-state one.

## 3. The step (§2, S7, S9)

    v, a   = V_d(b,M), decide_d(b,M)            d = min(world.d, n), the floor, as always
    v0 World (no θ)        -> (a, "floor",      0)
    n ≤ d or M∩O = ∅       -> (a, "struck_n",   0)          ĝ = 0 exactly
    ĝ = cap − V_d ≤ c      -> (a, "struck_cap", 0)          bounds settle it; f is not read (S7)
    V_d + f·ĝ − c > V_d    -> (decide_{d⁺}, "think", c)     θ is last in M, so strictly (J14, C17)
    otherwise              -> (a, "refused",    0)

Five lines, in that order, which is S7's order of precedence. The deeper evaluation is my existing
`_value` with a different n — not a second lookahead (E5) — over the same World, so the memo of
brief 004 answers most of it. `decide` keeps its signature and its meaning (decide_n at the n it is
given); `step` is the one that applies the floor, because the page's ĝ reads the raw n.

## 4. The counter (E6)

One tally per arithmetic operation on ℚ in `belief._dot`, `belief._split` and `belief._mass` —
the three places the fast path multiplies or adds measures, and therefore the whole of `push`,
`condition` and expectation as this evaluator performs them. The count is added in bulk, so
counting costs one integer add per call and not one per operation; the Wordle packs must not
get slower.

`decide` resets the counter as θ begins and never reads it. `episode.run` reads it when the step
comes back `"think"` and appends it to `Result.operations`. `report` prints it beside the predicted
`ops(s(b))` when it is given the World. Two evaluators may count differently (E6 says so); mine
counts what it does.

## 5. The loop, and the Result

One line changes: `decide(belief, world, min(world.d, n), used)` becomes
`step(belief, world, n, used)`. θ is not an act: the door never sees it, `n` is not decremented for
it, and its cost goes to `Result.thought`, not to `paid`. `Result` gains `thought`, `steps` (the
four S7 counts) and `operations`. Everything after the door mints `o` is untouched.

## 6. How I will know it is right

- `python3 charter/laws/kit_think.py` through the cage command: 60 random Worlds + 11 pinned,
  C12–C20, E2, the five buckets, the thirteen refusals.
- Appendix A and B worked from the page's own numbers as tests: V₁, V₂, cap, ĝ, c, the bucket at
  three rates, and the act bought. Plus `FIXED_CAP`'s cap ≥ 40951/2000, and the S1-2B/S1-2C Worlds.
- Every v0 suite green and unchanged: structural, surface, wordle, wordle200, and C1–C11 on 300
  worlds at three unseen seeds.
- The Wordle packs timed again: the counter must not have cost anything visible.

## What this brief does not touch

No pack — 005b brings the surface syntax and the two packs, after SURFACE v0.1 is signed. No
scoreboard sweep over r. No Wordle. No float, no threshold, no clock: `time` stays out of
`src/wald`, and the cost of a thought is the number the pack declares, never a number measured.
