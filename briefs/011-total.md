Builder brief — wald Q18: `_total` is quadratic in |Ω|

Scope: src/wald only; the cage judges. Kit-neutral: no act, value, or
refusal name may change.

1. Reproduce: on the Renavon pack (world/packs/renavon.py at
   renavon-monorepo world/turn-three, 20,736 states), profile `declare`.
   Confirm `_total` at ~86% of ~248 s and that its cost grows as |Ω|² across
   the arena's 13,824-state pack and a 2-rung scratch pack of the same shape.
2. Read `_total` and state in the PR why it is quadratic — a nested scan over
   tuples where one pass with a dict keyed on the tuple suffices, or
   otherwise. Do not guess; show the loop.
3. Rewrite it linear in |Ω|, exact rationals unchanged, same return value.
   No cache that survives the call; no float; no early exit that skips a
   check the law names.
4. Measure again on the three packs; print before/after seconds and the
   fraction of `declare` remaining in `_total`.
5. Done when the kit passes at the pinned charter, the three packs declare
   to the same census digests as before, and the Renavon pack's `declare`
   is under 60 s. If it is not under 60 s after `_total` is linear, name
   the next hot check and stop; one fix per PR.
