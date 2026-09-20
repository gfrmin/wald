# Brief 004 — plan: exact fast paths (CHARTER E2), Wordle at two hundred words

## What the measurement from brief 003 said

`decide` at the root of the forty-word World, depth 1, cost about two seconds: `|T| x |Omega|`
inside `|O| x classes`, and it did not fall as the game was won. Two hundred words at depth 2 is
that shape twice over. The reference's own specialised oracle (`laws/wordle_oracle.py`), written
in machine integers over sets, takes **7.8 s** for one depth-2 root and 0.3 s for the twenty
episodes after it. That is the budget: a general kernel over `Fraction`s may be a small multiple
of it, not a large one.

Where the time goes, counted rather than guessed:

| level | nodes | work at each |
|---|---|---|
| 2 (the root) | 1 | 200 guesses, each split over 200 states |
| 1 | ~12,000 | 200 guesses x ~3 states, then the terminal acts |
| 0 | ~70,000 | 200 claims x ~1 state |

Three things are wrong with the kernel as written, and the brief names all three.

1. A belief carries every state of Omega for ever, so level 0 costs `|Omega|` where it should
   cost `|support|`. `condition` never revives a zero, so the states are dead weight.
2. Every one of the 200 claims is evaluated at every node, though on a support of three words
   there are four different claims in the World: the three that name a candidate, and the 197
   that are wrong whatever happens. Likewise the guesses.
3. The same subset is reached by many paths and solved again each time.

## The three fast paths, and why each is exact

CHARTER E2 allows an exact fast path to replace `push`, `condition` and expectation, and nothing
else. `decide`, the lookahead and the loop stay written once (E5). Nothing below is approximate:
no threshold, no sampling, no float, no bound.

### 1. An unnormalised measure — one pass for `push` and `condition`, and no division at all

Write `U_n(m)` for `mass(m) x V_n(m/mass(m))`, the value of a normalised belief scaled by the mass
of the measure it came from. Then section 2 reads, with no division anywhere:

    U_0(m)        = max over terminal t of   sum_w m(w) u_t(w)
    U_n(m)        = max( U_0(m), max over k in M of Q_n(m,k) )
    Q_n(m,k)      = -price(k) x mass(m)  +  sum over outcomes o of  U_{n-1}(m|k,o)      [ending o: sum_w (m|k,o)(w) u_end(w)]
    (m|k,o)(w)    = m(w) K_k(o|w)                                  -- unnormalised, no z

This is exact and it is arithmetic, not a heuristic: `P_b(o|k) = mass(m|k,o) / mass(m)`, and
`b|k,o = (m|k,o) / mass(m|k,o)`, so `P_b(o|k) x V_{n-1}(b|k,o) x mass(m)` is exactly
`U_{n-1}(m|k,o)`. The normalisation the page writes is done and undone in the same line, so it is
not done. `push`, `condition` and expectation are the three verbs replaced, and only those.

It removes every `Fraction` division from the lookahead (a division costs a gcd, the most
expensive rational operation), and it makes `mass` needed only where a price is paid — at `n = 0`
there is no price, so the 70,000 level-0 nodes never compute one.

Zero-mass states are dropped where the measure is built: `m(w) = 0` contributes nothing to any
sum above, and `m(w) K(o|w) = 0`, so no conditioning can revive it. The support only shrinks.

`condition`, `push` and `expect` themselves keep their signatures and their meaning: the episode
and the adapter still hold a normalised belief, and `WorldFalsified` still fires there (S5).

### 2. One act per group of acts the belief cannot tell apart

Two acts a belief cannot tell apart have the same `Q` at that node, so J3 already says which is
played: the first in menu order. Evaluating the rest is evaluating a copy.

Sameness on a support `S` is: same price, same `once`, same ending outcomes with the same u_end,
and the same kernel row at every state of `S` (for terminal acts: the same utility at every state
of `S`). Off `S` nothing can matter, because every future support is contained in `S`.

The continuation is where this has to be argued. `Q_n(m,k)` recurses with the menu `M \ {k}`, so
for two same acts `k1, k2` the child menus differ. They differ by a relabelling: `M \ {k1}` holds
`k2`, which behaves on every reachable support exactly as `k1` does, and `M \ {k2}` holds `k1`.
A value is a max over acts and does not read their names, so the two are equal. The *act* returned
differs, but only at the node, and there J3 chooses the earlier one, which is the representative.
Multiplicity is kept, not collapsed: the menu still carries both, so two identical `once` acts
are still two looks.

**Cost.** Sameness must be decided more cheaply than the values it saves. Every cell, row, u_end
table and price of a World is interned once, on that World's first decision, into a small integer,
so a signature is a tuple of integers and two rationals are compared once and never again.
For the terminal acts one more fact halves it again: restricting to a smaller support can only
*merge* groups, so the representatives of a superset are enough to start from — at level 0 there
are four terminal representatives to sift, not two hundred.

### 3. A value already computed is not computed again

Keyed by `(the measure, n, the menu)`, as the brief says. The menu enters as the set of `once`
acts already used; at `n = 0` it does not enter at all, because only terminal acts are in reach
and `T` never leaves the menu. The table lives on the World, which is immutable once declared, so
it is shared by every episode played in that World — this is what makes 200 answers cost barely
more than the first.

Nothing else. No pruning by a threshold, no bound carried for unevaluated mass, no special case
for a uniform prior or a deterministic kernel. The maths kit's 300 random Worlds, its forced ties
and its zero entries hold this to the reference act for act.

## What changes, file by file

| file | change |
|---|---|
| `src/wald/same.py` | **new.** The interning and the two grouping functions. It never compares a value and never picks an act. |
| `src/wald/belief.py` | `_measure`, `_split`, `_dot`, `_mass`: the unnormalised fast path. `_update` drops zero-mass states. |
| `src/wald/decide.py` | `_value` and `_q` over measures, with the memo and the representatives. The argmax loop is unchanged in shape and still the only one. |
| `src/wald/world.py` | one slot for the sameness tables and the memo, built on first use. |
| `tools/make_wordle_pack.py` | a word list and a depth as arguments; writes `packs/wordle200/d1.py` and `d2.py`. |
| `tools/play_wordle.py` | takes a pack and writes `packs/wordle200/SCOREBOARD.md`. |
| `KERNEL.md` | one line for `same.py`; the fast-path section. |

## The two packs

`packs/wordle200/d1.py` and `d2.py` are brief 003's World on `laws/wordle/words200.txt`, in that
order, differing only in `depth`. The owner's numbers are given: `loss = -7`, `horizon 5`,
`closed`, price 1, uniform prior, nothing `fitted`. Brief 003's arithmetic carries over: with
`|L| = 7` a wrong claim (-7) is one worse than five guesses and a claim (-6), and at one candidate
left the claim and the guess tie exactly, so J3 ends the episode on the claim.

## How I will know it is right

- `kit_wordle_big` B2: every act the kernel plays is the specialised oracle's, at both depths, on
  answers from a seed I never see. A fast path that changes one act fails there.
- The maths kit at `--worlds 300` on several seeds, and the forced-tie worlds: E2 act for act
  against the general reference, where the fast paths get no special structure to lean on.
- A differential of my own: the old kernel and the new one on the same random Worlds, same acts
  and same values.
- If my kernel and the second oracle ever disagree, that is a `QUESTIONS.md` entry with the
  answer, the depth and the two act sequences. One of us would be wrong, and it may be the oracle.

## Measurements to report

Each part of the cage command, timed; the depth-2 root; one episode; all 200 answers at each
depth; and the line the brief asks for in the scoreboard: mean attempts at `d=1` minus mean at
`d=2`, whatever it is.
