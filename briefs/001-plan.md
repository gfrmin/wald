# Plan — Brief 001, the v0 kernel

Read first: `charter/CHARTER.md` (at signed tag `charter-v0`), `charter/laws/INTERFACE.md`,
`charter/laws/violators.md`. The judge is
`python3 charter/laws/kit.py --impl src --seed <unseen> --worlds 100`.
Everything below is either a citation of the page or a decision forced by one; where a decision is
mine and not the page's, it is marked **[mine]** and confined to `kit_adapter.py` or to what the kit
cannot observe.

## 0. Blocker for the author (not an ambiguity in the page)

`sh cage/fetch_charter.sh` fails as committed:

    tag kit-v0 does not point at the locked commit

because `cage/charter.lock` reads `SHA=PASTE_SHA_HERE`. `cage/` is mine not to touch (CLAUDE.md), so
I cannot fix it and CI will fail this branch at step one until the author does. Observed, for the
author's convenience: the tag `kit-v0` **is** signed by `author@wald`
(`Good "git" signature for author@wald`, ED25519 `SHA256:/hX9kxdf+khb2AenKoaXi0FWxvG9M748etPA8D/1WeQ`)
and points at `458e6e8656f8ed02429c5d21800b522e9a36f0de`; at that commit
`git diff --quiet charter-v0 -- CHARTER.md` is clean, so the page is unchanged since `charter-v0`.
The clone the failed script leaves behind sits on exactly that commit, so I have read and will build
against the signed page. `python3 charter/laws/spec_check.py` prints **PAGE PASSES** here.

This is not a `QUESTIONS.md` entry: it is a broken lock file, not an ambiguity in the page. I have no
`QUESTIONS.md` entry to file from this reading — see §7.

## 1. What the judge actually calls

`kit.py` reaches the kernel through one door only: `wald.kit_adapter.make_agent()`, returning an
object with four methods (INTERFACE.md). Everything else in `src/wald` is unobserved by the kit and
exists because the page and the brief require it.

| the kit calls | passes | must get back |
|---|---|---|
| `push(b, K)` | `b = {state: Fraction}`, `K = {state: {outcome: Fraction}}` | `{outcome: Fraction}`, summing to 1 (C1) |
| `condition(b, K, o)` | as above, `o` a raw outcome value | `{state: Fraction}`; raises a class **named** `WorldFalsified` when `P_b(o|k) = 0` |
| `expect(b, f)` | `f = {state: Fraction}` | `Fraction` |
| `decide(b, world, n, used)` | `world` a plain dict, `n` an int ≥ 0, `used` a frozenset | the act **key**, i.e. the same string the world dict is keyed by |

Consequences I must design around, each read off `kit.py` / `spec_check.py`:

- **Plain dicts cross the boundary in both directions.** `C2` compares two `condition` results with
  `==`; `C1` sums `push(...).values()`; `C6` feeds a `condition` result straight back into `expect`.
  So the adapter converts `Belief → {state: Fraction}` on the way out. The seal (brief 1) therefore
  cannot be "no code can see the weights"; it is "no code **outside the kernel package** can, and the
  only way in is `condition`". Implementation: `Belief` is frozen with `__slots__`, constructible
  only with a module-private token, and the weights are reachable only through a package-private
  accessor that `push`/`expect`/`decide`/`report`/the adapter use. Any other module importing it is a
  bug I can see in review; `wald.__init__` does not export it.
- **The kit's outcome values are not minted tokens.** `same_acts`, `policy_value`, `C1` and `C7` call
  `condition` with the same raw outcome many times over. So the Obs discipline of §1 ("minted only by
  the door", consumed exactly once) lives in the door and the episode loop, **not** in `condition`'s
  signature at the adapter boundary. `condition` takes an `Obs`; the adapter mints one per call from a
  test door and spends it immediately. **[mine]**, and it is conversion, not choice: the adapter still
  computes nothing.
- **`decide` is `decide_n`, never the floor.** `E2`/`same_acts` compares against
  `REF.decide(b, world, n, used)`, the exact §2 recursion; INTERFACE.md says the kit passes
  `n = min(d, n)` itself when it tests a floor. So `min(d, n)` belongs in the episode loop (brief 5),
  and `decide` must not apply it. Getting this backwards is the poison
  `Rolling(1, "ignores the declared depth")`.
- **The kit's World dict declares no Horizon, no Depth, no `closed`/⊥, no sources.** The adapter must
  supply them to build a `World` that validates. **[mine]**, all three unobservable to the kit:
  `closed = True` (forced in substance: the `S5` check requires `condition` on a zero-mass outcome to
  raise, which is closed-world behaviour); `N = d = 1`, a pair that satisfies `1 ≤ d ≤ N` — the
  horizon must **not** be derived from the `n` of a call, since the kit calls `decide(..., n=0)`
  (`C5`, `C8`) and `N = 0` would refuse a world the kit expects an answer for; each observational act
  reads its own private source, so no source is shared and S2 has nothing to refuse. That last one is
  load-bearing: `tie_variants` hands me `k0_copy`, a duplicate of `k0` with an identical kernel, and a
  validator that read "identical kernel ⇒ shared source" would refuse a world the kit requires me to
  answer. Identical kernels are not a shared source; a shared *declared* source is (S2).

## 2. Modules (one line each, as they will read in `KERNEL.md`)

| module | why it exists |
|---|---|
| `wald/refusals.py` | the named refusals of §1/S4/S5/E3 and `WorldFalsified`; refusing by name is required by brief 2 and the class name is read by the kit |
| `wald/dist.py` | a finite distribution over ℚ that cannot exist unless its mass sums to 1 — the one place row sums are enforced (S4) |
| `wald/kernels.py` | `Kernel` plus the five combinators of S4 (point, table, mixture, product, composition), each preserving row sums by construction |
| `wald/world.py` | the World and its declared tables with their `data`/`elicited`/`fitted` source tag (§1, S3), and all declaration-time validation (brief 2) |
| `wald/obs.py` | the `Obs` token: minted only by a door, consumed exactly once, a second use raises (§1, S2) |
| `wald/display.py` | `Display`: a rendered value with no comparison, no arithmetic, no `float()` (S1) |
| `wald/belief.py` | the sealed `Belief` and the three verbs that may touch its weights: `push`, `condition`, `expect` (§2), plus `report` (S1) |
| `wald/decide.py` | the one `decide` — V₀, Qₙ, Vₙ, `decide_n` — existing exactly once (E5) |
| `wald/episode.py` | the episode loop of §2 in the page's order, the `Door` interface the host implements, and a simulated door for tests |
| `wald/kit_adapter.py` | the INTERFACE.md shim: dicts in, kernel types out, no logic of its own |

Ten modules. If any one of them ends the brief without a sentence of its own in `KERNEL.md`, it
should not exist.

## 3. Order of work

1. `refusals`, `dist`, `kernels` — S4 first, because every table in every later test needs it.
2. `world` + validation (brief 2). Refuse by name, one named refusal per clause: empty T; prior not
   strictly positive or not summing to 1; kernel row ≠ 1; `d` outside `1..N`; neither `closed` nor a
   ⊥ with full support over every act's every outcome (S5); a source read by two acts that is not a
   declared component of Ω (S2); an undeclared parameter, and a declared parameter read by nothing
   (S3, both halves — `violators.md` S3 expects *two* refusals).
3. `obs`, `display`, `belief`. `push`/`condition`/`expect` are three lines each from §2; the work is
   the seal and the single-use token.
4. `decide` (E5). Written straight from the §2 box, then checked against the appendix by hand:
   `E[treat] = −8/5`, `P(+) = 17/50`, `Q₁(test) = −51/50 > −8/5`, `decide₁ = test`.
5. `kit_adapter`, then the kit. Run `--seed 1 --worlds 100`, then other seeds of my own choosing, plus
   `--worlds 300`, since CI's seed is unseen and 100 worlds at one seed is not evidence.
6. `episode` + the simulated door, in the page's order (§4 below).
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
- Every violator in `violators.md` as a case that must raise the named refusal: S1's display gate
  (`Display` has no `__lt__`, no `__float__`), S2's three (token reused; two acts one source; five
  copies of one attestation), S3's two (unhoused numeral; parameter read by nothing), S4's short row,
  S5's two (`return prior`; `ε`-floor), E3's `depth: 0`, E5's pack that picks.
- The episode loop against the simulated door: the order of §2, including a falsifying draw in a
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
