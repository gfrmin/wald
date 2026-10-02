# Brief 012 — plan

Judge: L1 and L6 of `kit_library.py` at kit-v0.14, every other suite unchanged. Definition:
`laws/counts_check.py` (`Plate.prior`, `Plate.values`, `marginal`, `render_marginal`, `values`,
`render_values`); contract: INTERFACE, "What a host may ask of a plate (kit v0.14)".

Neither brief 010 (the plate's memo) nor 011 (`_total`) is on master, so `values` builds a memo of
its own and drops it when it returns, as the brief says.

1. **`law.KIT = "kit-v0.14"`.** L1.
2. **The declared World keeps its dimensions.** `Plated` gains `dims`: the declared `locals` and
   `globals`, each a tuple of `(name, values)`. `wrap` (a v0 World) gives none. `components()` maps a
   name to (part, index, values), part 0 the local tuple of a state `(l, g)`, 1 the Global tuple.
3. **`Plate.prior()`.** `run`'s own prior, `counts.episode_prior(plated, Counts + shipped
   falsifiers)`, through one private method that `run` calls too, so they are the same belief.
   It raises `WorldFalsified` once the plate is falsified, as `run` does.
4. **`report(belief, world, over=None)`.** Given a `Plated`, `report` reads its v0 World (the
   `AttributeError` L6 found: a `Plated` has no `dplus`). With `over`, it gives the marginal.
   `over` must be a non-empty list of distinct component names, or the call raises
   `Refused(UNKNOWN_NAME)`, and a v0 World has no components. The output is one line per value of
   positive mass, in the order of the product of the declared values: compact JSON of the values
   with `ensure_ascii` (V2.13's escapes), then the mass as `digits.rational` writes it.
5. **`Plate.values()`.** At `prior()`, with the full menu, n = min(d, N). Three line types:
   - `V_0` and one `T` line per terminal: E_b[u], from `_dot`.
   - One `O` line per act of `world.menu(())`, in declared order: Q_n from `decide._q` called
     directly. No `same.acts` skipping, so every act gets its own line, a copy included.
   - `V_n decide_n`: from `decide._value`, which is the lookahead `run`'s first step at the floor
     uses. It is the kernel's one lookahead, not a second argmax.
   
   The memo is `(Sameness(world), {})`, made for this call. θ is not run. The output is a
   `Display`, and the call raises `WorldFalsified` once the plate is falsified.
6. **One refusal convention.** API.md's `declare` row says it returns `Refused`; correct it to
   "raises", and state once that every verb refuses by raising `Refused`.
7. **API.md**: the three additions, with appendix A of CHARTER v0.2 (`appendix_a.py`) as the
   example answering the issue's four questions. **KERNEL.md**: one line.

Tests (`tests/test_host_reports.py`): the appendix's values (V_0 −8/5, Q_1 −51/50, 29/50, test);
`prior()` is `run`'s prior; `over` refusals; marginal order; a copied act keeps its own `O` line;
a falsified plate refuses both.

Not measurable here: the arena's p1-c0 pack, Renavon and `world/analyse.py` are not in this
checkout. The PR says so.
