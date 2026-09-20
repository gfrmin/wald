# Plan — Brief 001, the v0 kernel

Read first: `charter/CHARTER.md` (at signed tag `charter-v0`), `charter/laws/INTERFACE.md`,
`charter/laws/violators.md`. The judge is
`python3 charter/laws/kit.py --impl src --seed <unseen> --worlds 100`.
Everything below is either a citation of the page or a decision forced by one; where a decision is
mine and not the page's, it is marked **[mine]** and confined to `kit_adapter.py` or to what the kit
cannot observe.

## 0. The lock (resolved)

Superseded. The author fixed `cage/charter.lock`; `sh cage/fetch_charter.sh` now prints
`charter ok: kit-v0.1 at 38285fcb430aaf8ab8698cf30c1ee092bbc79823, signed by author@wald, page unchanged since charter-v0`.
`kit-v0.1` adds `laws/kit_structural.py` and the INTERFACE section revised into this plan below;
`CHARTER.md` itself is byte-identical to `charter-v0`, so nothing in §4-§7 of this plan moves.

## 1. What the judge actually calls

Two judges now. `kit.py` reaches the kernel through `wald.kit_adapter.make_agent()`'s four methods;
`kit_structural.py` (kit v0.1) judges **the real API**, whose names and signatures INTERFACE.md fixes
under "The structural surface". So "everything else in `src/wald` is the builder's" is now false in
the places that section names, and my earlier guesses at those names are replaced by its list.

The four-method surface (`kit.py`):

| the kit calls | passes | must get back |
|---|---|---|
| `push(b, K)` | `b = {state: Fraction}`, `K = {state: {outcome: Fraction}}` | `{outcome: Fraction}`, summing to 1 (C1) |
| `condition(b, K, o)` | as above, `o` a raw outcome value | `{state: Fraction}`; raises a class **named** `WorldFalsified` when `P_b(o|k) = 0` |
| `expect(b, f)` | `f = {state: Fraction}` | `Fraction` |
| `decide(b, world, n, used)` | `world` a plain dict, `n` an int >= 0, `used` a frozenset | the act **key**, the same string the world dict is keyed by |

The real surface (`kit_structural.py`), which the adapter is a shim over:

- `wald.__all__` subset of `{declare, run, Door, report, Display, refusals}`. `push`, `condition`,
  `expect` and `decide` are **not** exported: a host or pack never holds a probability (S1, E5).
- `wald.world.declare(spec) -> World`, where `spec` is the kit's World dict **plus** `N`, `d`, either
  `closed: True` or `bottom: <state>`, `table_sources`, and optionally `sources` / `components`.
- `wald.belief`: `Belief` (unconstructible, no public attributes, immutable), `prior(world)`,
  `condition(belief, world, obs)`, `expect(belief, f)`, `report(belief) -> Display`.
- `wald.obs.Obs` unconstructible, single-use; `wald.display.Display` unconstructible and inert;
  `wald.episode.Door` with `observe` as the only mint; `wald.episode.run(world, door) -> result`
  carrying `acts`, `outcomes`, `status`, `paid`, `final`.

Four things this settles, three of which my first draft had to guess at:

- **Plain dicts still cross the four-method boundary in both directions** (`C2` compares `condition`
  results with `==`). So the seal is "nothing outside the package sees the weights", and ST2 tightens
  it: `dir(belief)` must be **empty of public names** — not one public method, not one attribute.
  Implementation: `__slots__`, a private construction seal, `__setattr__` that refuses, and a
  package-private `_weights` accessor that `push`/`expect`/`decide`/`report`/the adapter use.
- **The Obs discipline lives on the real `condition(belief, world, obs)`, not on the adapter's.** The
  kit conditions on the same raw outcome many times over (`same_acts`, `C1`, `C7`), so the adapter
  needs a lower-level path. One update, two entry points: the public verb spends a token, the
  package-private `_update(belief, kernel, value)` is the arithmetic of §2 and exists once.
  ST5 confirms the order: check-spent first (`ObsSpent`), compute, and mark spent **only on success** —
  the page says every Obs *that does not falsify the World* is consumed by exactly one `condition`, so
  a falsifying token is never consumed.
- **`decide` is `decide_n`, never the floor.** `min(d, n)` lives in `run`, which ST6 tests directly
  (the H world: `N=2, d=1`, two blank peeks then X). Confirmed, not guessed.
- **The adapter still supplies what the kit's four-method World dict does not declare** — `N = d = 1`
  (a pair satisfying `1 <= d <= N`; the horizon must *not* come from a call's `n`, since the kit calls
  `decide(..., n=0)`), `closed: True`, and no `sources` key, i.e. the default private source per act.
  **[mine]**, and unobservable to `kit.py`. The source default is load-bearing and is now confirmed by
  ST4: `twin` declares two acts with *identical kernels* and private sources and must be **accepted**.
  "Identical kernels are not a shared source" is INTERFACE's own sentence.

## 2. Modules (one line each, as they will read in `KERNEL.md`)

The fixed names land one per module, so the module list is unchanged from the first draft:

| module | why it exists |
|---|---|
| `wald/refusals.py` | `Refused` (with `name`), `WorldFalsified`, `ObsSpent`, and the seven refusal names; refusing by name is required and the class names are read by the kit |
| `wald/dist.py` | a finite distribution over Q that cannot exist unless its mass sums to one — the one place row sums are enforced (S4) |
| `wald/kernels.py` | `Kernel` plus the five combinators of S4 (point, table, mixture, product, composition), each preserving row sums by construction |
| `wald/world.py` | `declare(spec) -> World`: the declared tables with their `data`/`elicited`/`fitted` tags, and every validation that refuses by name |
| `wald/obs.py` | the `Obs` token: minted only by a door, consumed exactly once, a second use raises `ObsSpent` (§1, S2) |
| `wald/display.py` | `Display`: renders, and raises `TypeError` on every comparison, operator, `float`, `int`, `bool`, `hash`, `iter`, `len` and index (S1) |
| `wald/belief.py` | the sealed `Belief` and the verbs that may touch its weights: `prior`, `push`, `condition`, `expect` (§2), plus `report` (S1) |
| `wald/decide.py` | the one `decide` — V_0, Q_n, V_n, decide_n — existing exactly once (E5) |
| `wald/episode.py` | `Door` and `run`: the loop of §2 in the page's order, with `min(d, n)` (E3) |
| `wald/kit_adapter.py` | the INTERFACE.md shim: dicts in, kernel types out, no logic of its own |

## 3. Order of work

1. `refusals`, `dist`, `kernels` — S4 first, because every table in every later test needs it.
2. `world.declare` and its refusals, one per clause: `EMPTY_T`; `PRIOR` (not strictly positive, or not
   summing to 1); `KERNEL_ROW`; `DEPTH` (`d` outside `1..N`); `PRICE` (§1 says
   `price : O -> Q>=0`; INTERFACE's seven names have none for it, and a rule that forbids nothing
   says nothing, so it is enforced under an eighth name); `ZERO_EVIDENCE` (neither `closed` nor a
   `bottom` whose kernel rows are strictly positive everywhere); `TABLE_SOURCE` (a table that names no
   source, or a tag outside `data | elicited | fitted`); `SHARED_SOURCE` (two acts naming one source
   that is not in `components` — and, per S2's second clause, a `fresh` act naming one, since its two
   executions read it twice). **Unhoused numerals, unread parameters (S3) and refusing a pack that
   chooses (E5) are deferred to brief 002**, where the surface syntax exists to carry them.
3. `obs`, `display`, `belief`. The verbs are three lines each from §2; the work is the seal, the
   single-use token and the inert Display.
4. `decide` (E5), straight from the §2 box, then checked by hand against the appendix:
   `E[treat] = -8/5`, `P(+) = 17/50`, `Q_1(test) = -51/50 > -8/5`, `decide_1 = test`.
5. `episode.run` + `Door`, in the page's order (§4 below).
6. `kit_adapter`, then the whole command: fetch, lint, kit at seed 1 and at seeds of my own, and at
   `--worlds 300`, since CI's seed is unseen and 100 worlds at one seed is not evidence.
7. `KERNEL.md`, tests, PR.

## 4. The two places the page's exact wording decides the code

**`decide` (§2).** `V_0 = max_t E_b[u(·,t)]` over T in declared order;
`Q_n(b,M,k) = Σ_o P_b(o|k)·W − price(k)`, the sum over outcomes of **positive mass only**;
`W = E_{b|k,o}[u_end(·,k,o)]` for an ending outcome — the belief is **conditioned first**, then u_end
is taken under the posterior (attack 2, finding 3.1; conditioning is not optional for ending
outcomes) — and `W = V_{n−1}(b|k,o, M′)` otherwise, `M′` dropping `k` only if `k` is `once`.
`V_n = max(V_0, max_k Q_n)`, and `decide_n` is **the first entry of M attaining V_n**, T before O,
in declared order (J3). "First attaining" is a strict improvement scan: a later entry replaces the
incumbent only on `>`, never `>=`. The kit forces exact ties on purpose (`tie_variants`, and the
`TieLast` poison it uses to prove its own tie worlds bite), so `>=` here is a guaranteed failure.

**The episode loop (§2), in this order and no other.** `n ← N`. Repeat: `a ← decide_min(d,n)(b, M)`.
If `a` is terminal the door fires it and the episode ends. Otherwise the door executes `a`, the
episode **pays `price(a)`**, the door **mints `o`**, and then, in this order: if `P_b(o|a) = 0` the
episode ends as `WORLD_FALSIFIED` (S5 — **before** anything else is done with the token, ending
outcome or not); else `b ← b|a,o`; then if `o` is an ending outcome the episode ends earning `u_end`;
else `M ← M′`, `n ← n−1`. The price is paid before the mint, and the falsification test precedes the
ending-outcome test: both orderings are stated on the page and both are cheap to get wrong.

## 5. Poisons I am most likely to write, and what kills each

From `spec_check.py`'s kill matrix, read as a list of my own likely mistakes:

| mistake | killed by |
|---|---|
| ties to the last entry (`>=` in the scan) | the kit's forced-tie variants (J3) |
| playing the first look that beats stopping | E2 only — hence E5, one `decide` |
| always `d = 1`, ignoring the `n` passed | E2 only |
| `max` over the nuisance latent where the page says sum | C1, C7, E2 |
| conditioning on one token twice | C2, C6, C7 |
| tempering or clipping the posterior | C6, C7 |
| a gate on a display value (`if confidence < 4/5`) | C3, C4, C9 — and S1 forbids it structurally |
| treating price as zero | C5, C9b, E2 |
| `z == 0 → return prior`, or `z = max(z, ε)` | S5 |
| a kernel row summing to < 1 | C1 |

The structural rules are what stop me writing these at all; the checks are only how I find out.
Note the page's own concession (§4, attack 2 finding 5.1): C1–C11 are **necessary, not sufficient**.
Passing them is not evidence of correctness; only E2's differential against the reference is, and only
on toy worlds. So I will not treat a green kit as a finished proof — I will treat a red kit as a
proof of failure.

## 6. My own tests (`tests/`, proving nothing — CLAUDE.md)

- The appendix vector worked by hand, every intermediate number from the page's last section.
- Every violator in `violators.md` that brief 001 owns, as a case that must raise the named refusal:
  S1's display gate (`Display` has no `__lt__`, no `__float__`), S2's shared source and its reused
  token, S4's short row, S5's two (`return prior`; an `epsilon` floor), E3's `depth: 0`. S3's two
  (unhoused numeral, unread parameter) and E5's pack that picks need the surface syntax and are
  brief 002's.
- The episode loop against a scripted door: the order of §2, including a falsifying draw in a
  `closed` world and an ending outcome, each landing on the right branch.
- `decide` against `spec_check.Ref` on worlds I generate myself, with seeds unrelated to 1 — the same
  differential the kit runs, in my own harness, so I find failures before CI does.

## 7. Open questions

None yet. The three gaps between INTERFACE.md's World dict and §1's World (no Horizon/Depth, no
`closed`/⊥, no declared sources) are not ambiguities in the page: INTERFACE.md is explicit that the
kit keeps the floor to itself, and each gap has exactly one reading that lets the adapter stay
logic-free (§1 above). If any of them turns out to change an **act**, that is a `QUESTIONS.md` entry
with the World that exposes it, and work on that point stops. The `charter.lock` placeholder (§0) is
for the author, not for `QUESTIONS.md`.

## 8. Done when

`sh cage/fetch_charter.sh && python3 cage/lint_imports.py src/wald && python3 charter/laws/kit.py --impl src --seed 1 --worlds 100`
is green on the pull request from `b/001-kernel` — which, per §0, needs the author's `charter.lock`
fix before step one can pass anywhere.
