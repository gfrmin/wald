# Brief 013 — plan

## Context
Branch `b/013-integer-weights` from master `bc6fd60`. Baseline cage command at seed 1, 100 worlds:
`IMPLEMENTATION PASSES` in 2 m 18 s. The pack the brief names is on this machine
(`/srv/wald-measure/omniscience-p1-c0.py`, sha256 `7cc140d8…cf`, checked).

## The units
The lookahead already computes U_n(m) = mass(m)·V_n(m/mass(m)), which is homogeneous of degree one
in m. Make every number in it an int by fixing units once per World:

- **U**, the lcm of the denominators of every terminal utility, every u_end and every price. A
  utility, a u_end or a price times U is an int.
- **D_k**, per act, the lcm of the denominators of its kernel's rows. R_k = D_k·K_k is an int table.
  **D** is the lcm of the D_k (1 for a World with no act).
- A measure is an int vector **a** with a denominator **c**: the true measure is a/c.

`_value(a, c, n)` returns U·Dⁿ·U_n(a) — an int — and the act. Then
- a terminal: `_dot(a, U·u_t) · Dⁿ`;
- Q_n(k): over the parts a·R_k(o), which are D_k times the true parts, each non-ending part's
  value at n−1, each ending part's `_dot(part, U·u_end) · Dⁿ⁻¹`, less `U·price · mass(a) · D_k · Dⁿ⁻¹`;
  the sum is in units U·Dⁿ⁻¹·D_k, and `· (D / D_k)` brings it to U·Dⁿ.

Every entry compared at a node is the same positive constant times what is compared today, so every
`>` is the same comparison, ties included (J3). The scaling leaves where a value leaves: `value`,
`quantities` and `step` divide by U·Dⁿ·mass(a) into one `Fraction`, and `_cap` divides its sum by
U·mass(a) before it meets V_0 and the cheapest price, as today.

## The keys: exactly today's
Today's memo key is the true measure x, entry by entry. A child's ints are a·R_k(o) over c·D_k, so
the same x reached two ways — at two depths, through two acts, from two roots of one `run` — would
carry different ints. Keying on the ints would then miss a hit today makes, and a miss is work E6
counts. So each node reduces (a, c) by g = gcd(c, a…) and keys on the reduced pair: a canonical
representation of x, equal exactly when today's keys are equal. The memo holds the value of the
reduced a and returns it times g. The root is lcm of the belief's denominators, then the gcd
taken out (a no-op for a normalised belief): item 2's representative, and two equal beliefs reach
the same keys. Sameness reads only the states, which scaling does not touch. Nothing scaled is
kept past the call but the memo keys and values that already exist.

## E6
`_split`, `_dot` and `_mass` tally exactly what they tally today: `_split` counts a product where
K(o|w) ∉ {0, 1}, that is R ∉ {0, D_k}; a part at K = 1 is p·D_k, a change of units, not counted.
The unit conversions (·Dⁿ, ·D/D_k, the root's lcm, the reduction) are not push, condition or
expectation, and are not tallied. KERNEL.md says why, citing E6.

## posterior_global
One `_update` — still the one update — with a likelihood that is the product over every record of
L(record | g)^count, normalised once. Zero total mass raises `WorldFalsified` naming the first
token after which no Global value has mass, as the per-token form does today.

## Where it lives
`src/wald/scaled.py`, new: the World's tables in those units, built once per World (`World.scaled()`),
like `Sameness`. `belief.py`: `_integers(belief)`, and `_split` counting against D_k. `decide.py`:
the units above. `counts.py`: the product form. KERNEL.md: one line for `scaled.py` and a paragraph
for E6. API.md: nothing changes.

## Checks
- the cage command; `tests/` whole.
- `tests/test_integer_weights.py`: master's `Fraction` lookahead frozen in `tests/fraction_lookahead.py`,
  against the kernel, on random Worlds (with θ, ending outcomes, fresh and once acts, forced ties)
  and on a plate with Counts: every act, S7 bucket, thought paid, E6 count and `Plate.values()` text.
- `tools/integer_weights.py`: the brief's table at T = 0, 300, 600 on the arena pack, against a
  master worktree, with acts and final belief compared.
- the Wordle kits' times before and after.
