# Brief 009 — plan

Branch `b/009-ship-counts` from master at `087b7e4`. The lock pins `kit-v0.13`; no page changes.
Read first, as the brief asks: INTERFACE.md's kit v0.13 section, SURFACE v0.2 V2.7,
`counts_check.realisable` and `_walk`, `surface_check.parse`, `long_int` and `decimal`.

## 1. Q15 — a prefix falsifier may end at an ending outcome

`counts.realisable` today refuses any draw of an ending outcome unless it is the last *and* the end
names it. A prefix `(draws, None, None)` has no end, so a prefix whose falsifying report is an
ending outcome was never realisable. V2.7: a prefix is the draws "ending at the report that
falsified", and v0 §2's loop checks zero mass before it checks an ending outcome, so such a report
is the prefix's last draw and never becomes an end.

The change: the walk over the draws checks only that an ending outcome is the *last* draw. Then a
prefix returns (non-empty, no after-report); a record's end must be the ending outcome's when the
last draw ends, a terminal otherwise. This is the reference's order of checks. Everything else in
`realisable` stays. Judged by K8, K9 and R3 on `prefix_falsifier_ending.py`.

Outcomes the kernels do not name: the reference refuses them in `realisable`; the kernel refuses
them in `expressible`, since such a draw has likelihood 0 under every Global value. Same verdict,
same name (PLATE), so I leave it where it is.

## 2. Long integer literals, read and written without lifting the limit

Never `sys.set_int_max_str_digits` (and `sys` is not on the import list anyway). `tokenize` and
`io` are not on the list either, so the kernel cannot do what `surface_check.parse` does with them.
Instead:

- **`digits.py`** (new): `long_int(digits)` and `decimal(n)`, 4,000 digits at a time, and
  `rational(q)` — `"p"` or `"p/q"` in decimal digits however many. Every place the kernel writes
  a rational for a reader goes through it: the Score, E7's lines, `report`, the wire, and the
  refusal messages that print a number.
- **Pieces of 600 digits**, not the reference's 4,000: 640 is the least limit Python lets a host
  set, so the kernel reads and writes under any limit, not only the default.
- **Reading.** `text.py` already has a lexer that walks a pack outside its strings and comments
  (V2.11). A maximal run of `[0-9A-Za-z_.]` that starts a token, is all digits, has no leading
  zero, and is longer than 600 characters is a decimal literal Python could not read: it is
  swapped for a fresh name not in the text, and its digits kept. Anything else is left to
  `ast.parse`, which refuses it SYNTAX as today (a long literal with `_`, or a leading zero).
  The tree's positions are the swapped text's, so the pack keeps that text as its own.
- **`Cells`** reads such a name as the integer (`number`), refuses it UNHOUSED_NUMERAL where a
  literal with no number is asked (`plain`), as the reference does; `counts` reads a multiplicity
  from its digits.

## 3. `wald.digest`, `wald.score`, `wald.e7`

- `digest.py` is renamed **`canonical.py`**, so no submodule of `wald` is named like a function of
  it: `wald.digest` is the function from a fresh `import wald`, whatever the adapter imports later.
- **`ship.py`** (new): the three functions a host needs to write the pack that ships its Counts.
  `digest(counts, falsifiers=())` is `canonical.digest`; `score(world, counts, falsifiers=())` is
  `counts.score` written by `digits.rational`; `e7(world, counts)` is `counts.e7`'s lines as a
  `Display`, one per line, each an exact rational. `world` is what `wald.declare` returns: a v0.2
  declaration, or a v0 World, wrapped as `plate` wraps one (C21).
- `__init__` exports them: fourteen names (ST1).

## 4. `wald.law` names `kit-v0.13`.

## 5. The differential

Remove `RECORDED`, the Q13 clause and the Q3/Q17 clause from `tests/test_surface_differential.py`.
The Q1 clause is from brief 002 and closed; I try without it too. (The kernel's refusal details
still cite `QUESTIONS.md` Q10 and Q12: that is where each reading came from, and the reference's
details cite the same entries.) Any divergence
that remains is a new question for `QUESTIONS.md`, with the pack and the gate check I think should
have caught it, and I stop on it.

## 6. Documents and tests

- `KERNEL.md`: a line for `digits.py`, `ship.py`, `canonical.py`; Q15's prefix under `counts.py`;
  the fourteen names.
- `API.md`: the three functions and a worked example — a plate played, then the pack that ships
  its Counts, written with `wald` alone, loaded and declared.
- `tests/`: that example; a Score of more than 4,300 digits through `load_pack`; Q15's prefix;
  the limit unchanged.

## As done

The differential without those clauses showed 138 divergences, every one two refusal names for a
variant that breaks two rules (SURFACE K7): a poison mutated to break a second rule (one side names
the poison's own rule), the After-act row substitution, which by itself makes a row that is not a
distribution and a kernel that reads `rel`, and `v02_q17c` without `globals`. The test now allows
exactly those, mechanically where it can; no acceptance differs and the reference never raises.

## Order

1 → 4 → 2 → 3 → 5 → 6, running the cage after each.
