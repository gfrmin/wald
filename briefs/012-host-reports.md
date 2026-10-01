# Brief 012 — what a host may ask of a plate

**Done when** the `cage` check is green on a pull request from `b/012-host-reports`, under `kit-v0.14`. No page changes, and no new public name: `wald.__all__` keeps its fourteen (ST1). Everything below is on names a host already holds, `Plate` and `report`.

**The owner's numbers for this brief:** none.

**The measurement.** Issue #14: a real host built against `v0.2.1` (the Renavon World: 81 Global values, 20,736 states, 70 monthly records) needed four things for an ordinary report, and could get each only by reaching past `__all__`:

- the posterior over its Globals, which it took from `counts.posterior_global`;
- a component's marginal, which it could get only by parsing `report`'s text;
- an act's value, V_0 and Q_n − V_0, which it took from `decide._q`, `decide._value` and `belief._measure`;
- the act the kernel would take next, for which it subclassed `Door` and raised out of `outcome` to abort a `Plate.run`.

The arena imports `posterior_global` too (`showcases/omniscience/run.py:486`). Each of the four is a report, and S1 already lets `report` render "beliefs and values for display". `laws/INTERFACE.md`, the section "What a host may ask of a plate (kit v0.14)", is the contract. `laws/counts_check.py` is the definition (`Plate.prior`, `Plate.values`, `marginal`, `render_marginal`, `values`, `render_values`). L6 in `laws/kit_library.py` is the judge.

**What to build:**

1. **`Plate.prior() -> Belief`**: the belief `run` would start the next episode from, sealed. It is the same object `run` builds today from `counts.episode_prior` over the Counts and the shipped falsifying records. Once the plate is falsified it raises `WorldFalsified`.
2. **`report(belief, world, over=[...])`**: the marginal on the named components, written as INTERFACE says, line for line. To do this, the declared World must keep the names of its `locals` and `globals`. A v0 World declares none, and `over` is then `UNKNOWN_NAME`. Also fix `report(belief, world)` for the World `declare` returns from a v0.2 dict: on `v0.2.1` it raises `AttributeError` (a `Plated` has no `dplus`). L6 found this.
3. **`Plate.values() -> Display`**: n = min(d, N); V_0; E_b[u] per terminal; Q_n and Q_n − V_0 per observational act on the full menu; V_n and decide_n. The format is INTERFACE's, line for line. Compute Q_n with the same `_q` and `_value` the episode uses, so the act on the last line is the one `run` would take first, at the floor. Do not route around the `same.acts` skipping: an act identical to an earlier one still gets its own `O` line, with its own Q_n.
4. **One refusal convention.** `declare` already raises `Refused`, as `load_pack` does. API.md's table says it returns `Refused`. Correct the sentence, and state the convention once for every verb.
5. **`wald.law["kit"]` is `"kit-v0.14"`** (`src/wald/law.py`). L1 compares it with the lock's tag, so until this changes the cage is red on L1, whatever else passes.
6. **`API.md`**: the three additions, with an example that answers the issue's four questions on appendix A of CHARTER v0.2. **`KERNEL.md`**: one line.

**What this brief is not.** No act's value is ever exported as a number: `values` is a `Display`, and nothing here hands a host a probability or a rational it can compute with (S1). There is no `next_act` returning a name for the host to act on outside the door. The kernel's next act is the last line of `values`, and only `run` fires it. Do not make `posterior_global` public either: `Plate.prior()` with `over` the Globals is the same quantity. If brief 010 or 011 has landed first, `prior` and `values` read the memo as `run` does. Otherwise they build a memo of their own and drop it.

A performance problem is a stop, not an approximation. Where the page and this brief disagree, the page decides: put it in `QUESTIONS.md`, with the World, and stop on that point.

**Report in the PR:**

- the cage command's time;
- each suite's line; `library:` on kit v0.14 should be green (on `v0.2.1` it fails L6 and, until item 5, L1's kit tag);
- `Plate.values()`'s time on the arena's p1-c0 pack at 0, 300 and 600 records, beside one episode's time there;
- the issue's `world/analyse.py` questions, answered with public names only (or say which one you could not answer).
