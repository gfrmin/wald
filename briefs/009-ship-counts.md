# Brief 009 — shipping Counts without the kit, and brief 008's questions answered

**Done when** the `cage` check is green on a pull request from `b/009-ship-counts`. The lock pins `kit-v0.13`. No page changes: kit v0.13 corrects the reference where your Q10–Q17 showed it wrong, pins each correction in the corpus, and adds three public functions. Read INTERFACE.md's kit v0.13 section first, then the answers below.

**The owner's numbers for this brief** (you choose none): `wald.law` is `{"charter": "charter-v0.2", "surface": "surface-v0.2", "kit": "kit-v0.13"}`.

**Your questions, answered.** In every one but Q15 your reading was right, and kit v0.13 moves the reference to it. Each is now a pack in the corpus or a check in the kit. Your differential's allowances for them in `tests/test_surface_differential.py` (`RECORDED`, and the Q13 and Q3/Q17 clauses) should no longer be needed. Your substitutions reach places my mutations do not, so any divergence that remains is a new question.

- **Q10a–e: your readings.** The reference refuses each by the name you gave it:
  - a row of the After-act's kernel that is not a distribution, KERNEL_ROW [V2.5];
  - an After-act row keyed by no state, TABLE_SHAPE [V2.4];
  - a negative After-act price, PRICE [V2.5];
  - a catch-all the After-act gives no mass, AFTER [C2.S12];
  - one end written twice, DUPLICATE [V2.5].

  A state of a one-component space respelt as a one-name tuple is no state, so it is TABLE_SHAPE [V2.4]. Poisons `v02_q10*.py` pin all six.
- **Q10f: the page is silent.** It is queued for SURFACE v0.3 (`ERRATA.md`). Keep accepting tuple after-outcomes, as the reference does. The kit pins nothing.
- **Q11: your reading.** It is pinned by `global_value_unnamed.py` and K8.
- **Q12: your reading.** It is pinned by `v02_q12_score_of_counts_in_v0_pack.py`.
- **Q13: your reading.** It is pinned by `falsifiers_before_counts.py`.
- **Q14: your reading.** It is pinned by `v02_q14_end_without_its_draw.py` and K8.
- **Q15: V2.7 decides, and your kernel must change.** A prefix falsifier is "draws … ending at the report that falsified". The loop checks zero mass before it checks an ending outcome, so a falsifying report that is an ending outcome never becomes an end: it is the prefix's last draw. C2.S13's "and then as the end" is about a record, and a prefix has no end. `realisable` must accept a prefix whose last draw is an ending outcome. Three things pin it:
  - `prefix_falsifier_ending.py` (R3), which ships such a prefix into a declaration where that outcome is possible;
  - K8;
  - K9, which ships your own plate's falsifier into a refit with the same mechanics.

  It cannot be shipped back into the declaration that wrote it: no Global value there holds a falsifier with the Counts it followed, and C2.S13 refuses Counts and falsifying records no Global value holds together.
- **Q16: the page is silent.** It is queued for SURFACE v0.3. The reference refuses a byte-order mark as NOT_A_DECLARATION, and you refuse it as SYNTAX. The kit pins neither name, and R10 accepts any refusal. Keep yours.
- **Q17: your readings.** They are pinned by `v02_q17b_after_before_space.py`, `v02_q17c_cost_before_local_prior.py`, `after_act_without_price_declaration.py`, and R9's raw surrogate.

**What to build:**

1. **Q15.** A prefix falsifier may end at an ending outcome (above). K8, K9 and R3 on `prefix_falsifier_ending.py` judge it.
2. **Long integer literals.** `wald.load_pack` reads an integer literal of any length. A real Score has tens of thousands of digits: the arena's 144 records gave about 35,700, and appendix A shipping 300 records gives 34,486. Python refuses more than 4,300 by default. Do not call `sys.set_int_max_str_digits`, not even for a moment: it is interpreter-wide, so it touches every thread and every other library in the host's process. The reference swaps each long literal for a fresh name before `ast.parse` and reads its digits 4,000 at a time; see `surface_check.parse`, `long_int` and `decimal`. Writing such a number back out needs the same care. R9 and L5 check that the limit is the same after your call as before it.
3. **`wald.digest(counts, falsifiers=())`**, **`wald.score(world, counts, falsifiers=())`** and **`wald.e7(world, counts)`**, in `wald.__all__`, which then has fourteen names (ST1). `world` is what `wald.declare` returns.
   - `score` returns the Score as a pack writes it: `"p/q"`, or the integer when q is 1, in decimal digits however many.
   - `e7` returns a `Display`: inert (S1), whose text holds every line of E7 as an exact rational.
   - `digest` is the adapter's `digest`, in public.

   With these, a host that plays a plate writes the pack that ships its Counts itself (INTERFACE.md, kit v0.13). Today `wald.digest` resolves to your `digest` submodule once the adapter has imported it, and a fresh `import wald` has no such name. The function must be the package's attribute; L1 asks for callables.
4. **`wald.law`** names `kit-v0.13`.
5. **`KERNEL.md`**, a line each for Q15's prefix, long literals, and the three functions. **`API.md`**, the three functions and a worked example: a plate played, then the pack that ships its Counts, written with `wald` alone. **`tests/`**, that example, and a Score of more than 4,300 digits through `load_pack`.

Nothing about `decide` changes. A performance problem is a stop, not an approximation. Where the page and the reference disagree, the page decides and the reference is the usual culprit: put it in `QUESTIONS.md`, with the pack, and stop on that point. Kit v0.13's gate has five new checks built from your questions; what you find beyond them goes to `QUESTIONS.md`, and the author will first ask which gate check should have found it.

**Report in the PR:**

- the cage command's time;
- each suite's line (`structural: …`, `surface: …`, `counts: …`, `library: …`); on brief 008's kernel, kit v0.13 gave structural 37/37, surface 212/215, counts 40/42, library 15/17, the last before L5 could run;
- `len(wald.score(...))` for appendix A shipping 300 records;
- appendix A's pack shipping three graded episodes, written by `wald.digest` and `wald.score` from a plate you played, printed.
