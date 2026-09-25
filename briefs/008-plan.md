# Brief 008 — plan: the kernel reads SURFACE v0.2

Read first: `charter/SURFACE-v0.2.md` whole (V2.0–V2.14), INTERFACE.md's kit v0.12 section,
`laws/model.py`, then the references `laws/surface_check.py` and `laws/counts_check.py`, and the
judges `kit_surface.py` and `kit_counts.py` (K7). The owner's numbers for this brief: `wald.law` is
`{"charter": "charter-v0.2", "surface": "surface-v0.2", "kit": "kit-v0.12"}` — Q7, answered.

## Where it stands

The first cage run on `b/008-surface-v02` (197 s), before any code:

    charter ok: kit-v0.12 at 9505ea6…, six pages unchanged
    structural 37/37, wordle 14/14, wordle200 16/16, think pass, wordle-think 27/27
    surface: 142/195 pass      the 14 lawful v0.2 packs refused NOT_A_DECLARATION, and 39 poisons
                               refused by that name instead of their own
    library: 14/15 pass        L1: wald.law names charter-v0.1, surface-v0.1, kit-v0.11
    counts: the adapter lacks ['digest']

Every failure is something this brief asks for; nothing of v0 or v0.1 moved.

## The shape

A v0.2 pack elaborates, exactly as the reference does, in two steps: first the joint World over
Omega's states as SURFACE v0 spells them, judged by v0's and v0.1's rules (`world.declare`, as
now); then the kit v0.11 dict — states as `(local, Global)` pairs — judged by CHARTER v0.2's rules
(`plated.declare`). `load_pack` returns that dict, which is what the kit's R3 compares and declares.

| module | change |
|---|---|
| `text.py` (new) | V2.11, before anything is parsed: a coding declaration naming another encoding, a CR, a surrogate code point in the text or in any string (escaped too, paired or not), a non-ASCII identifier character outside strings and comments. Its own small lexer finds strings and comments, because Python folds `ſcore` to `score` in the tree and raises `ValueError` — not `SyntaxError` — on a full-width `Ｎｏｎｅ`, so the tree cannot be asked afterwards |
| `learned.py` (new) | the v0.2 reader: `globals`, the prior as P(Global), `local_prior`, `after` with `reads`, `counts`, `falsifiers`, `score(of="counts")` — a mixin of `surface.Pack`, each refusal carrying its rule `[V2.k]`, and the projection to the kit v0.11 dict |
| `digest.py` (new) | V2.13: V2.13's escape table as a declared table, row for row, the first matching row deciding; the canonical bytes of `[counts, falsifiers]`, each array in byte order; their SHA-256. Not Python's `json` — DEL is escaped, `/` is not, and the page's table is what decides |
| `surface.py` | dispatch the six new declarations; V2.0 at most once; `states()` waits for `local_prior` when there are locals; `by(...)` over a Global in a utility is GLOBAL (V2.10); `spec` hands a v0.2 pack to `learned.py` |
| `counts.py` | the Score over the Counts **and** the falsifying records (V2.8); `realisable` for falsifiers: a prefix `(draws, None, None)`, or a full record with an after-report, never a full record without one (V2.7); `expressible` over both; the old digest removed |
| `plated.py` | `falsifiers` (a list, model.py's key) instead of kit v0.11's `falsifier`; tables over Omega's support (a pack's tables are keyed by the joint support, V2.4), a per-state ending utility (model.py) as well as kit v0.11's number; GLOBAL on ending utilities; `bottom` as a state; PLATE on the V2.13 digest whenever `counts` or `falsifiers` is present, the empty list included; a dict without `table_sources` — the kit v0.11 dict has none, and R3 declares it — is judged on everything but sources |
| `world.py` | `build(..., sourced=False)` for that dict: every rule but the sources |
| `plate.py` | the evidence is the Counts and every shipped falsifying record |
| `kit_adapter.py` | `digest(counts, falsifiers)`; `score(world, counts, falsifiers=())` |
| `law.py` | the owner's three tags |

`decide.py`, `belief.py`, `episode.py`'s loop: untouched.

## Readings, each checked against the reference before it is taken

Where the page and the reference differ I follow the page and write it in `QUESTIONS.md` with the
pack; where the page is silent I follow the reference and say so. I will find them by running my
checker against the reference on every mutation of the v0.2 corpus (`tests/test_surface_differential.py`,
extended), not by guessing.

## Tests

- `tests/test_learned.py`: appendix A's pack and its shipped twin through `load_pack` and `plate`
  (census 12/24 and 14/24; the first act `ask` at 1/4 and at 17/50; one right grade gives
  (3/5, 2/5)); the five digest vectors from their bytes; V2.11's text rules; the Score with a
  falsifier at 363/10000.
- the surface differential over the v0.2 corpus, packs read as bytes with no newline translation.

## Report

The cage's time; each suite's line; the five digests; appendix A's shipped pack through `plate`.
