# Brief 002 — the surface: packs, the checker, and a command to check them

**Done when** the `cage` check is green on a pull request from `b/002-surface`.

The law for this brief is a second signed page: `charter/SURFACE.md` (tag `surface-v0`), subordinate to `CHARTER.md`. Read it fully, then the new section of `charter/laws/INTERFACE.md` ("The surface"), then a few packs from `charter/laws/packs/ok` and `charter/laws/packs/poison`. `charter/laws/surface_check.py` is the reference checker: it is the definition, not a dependency. You may read it. You may not import it or copy it wholesale: build yours from the page, and use the reference to find where you differ.

1. **`wald/surface.py`**: `check(text, data_dir) -> spec` and `census(text, data_dir)`, exactly as INTERFACE.md says. A pack is parsed with `ast` and **never executed**: no `eval`, `exec`, `compile` or import of a pack, ever. Data files are read with `pathlib` (the lint still bans `open`).
2. **Refusals by name** (SURFACE §5). Add the surface's names to `wald/refusals.py`. One broken rule, that rule's name; several, any one of theirs.
3. **`declare` accepts the v0.3 spec**: `table_sources["kernels"][act]` is now a sorted list of tags (possibly empty); `sources` holds every act's `reads`; `components` lists the space's components. Kit v0.2's structural tests have been updated to the list form.
4. **`tools/wald_check.py`** (outside `src/`, so it may use `sys` and `argparse`): `python3 tools/wald_check.py pack.py` prints `ok`, the World's size and the census by source, or the refusal's name and message, and exits 0 or 1. This is the loop you and every later pack author will use: write, check, repair.
5. **`KERNEL.md`**: one line for each new module.

**Not in this brief:** writing domain packs (brief 003 is Wordle on a few hundred words), any `host` form (withdrawn: SURFACE K4), fast paths, floats, learning.

If the page and the reference checker disagree anywhere, the page wins and the disagreement goes in `QUESTIONS.md` with the pack that shows it. That would be a finding against the author's kit, not against you.
