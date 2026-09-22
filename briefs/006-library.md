# Brief 006 — wald as a library, and the wire

**Done when** the `cage` check is green on a pull request from `b/006-library`, and `python3 -m build` (or `uv build`) produces a wheel from the repository root that `pip install`s into a clean environment with no dependencies. Kit v0.10 adds `kit_library.py`: read its header and INTERFACE.md's last section first; they are the contract.

**The owner's numbers for this brief** (you choose none): the package version is `0.1.0`; `wald.law` is `{"charter": "charter-v0.1", "surface": "surface-v0.1", "kit": "kit-v0.10"}`. Nothing else in this brief is a number.

1. **`src/wald/law.py`**: the three strings above, and `law` as the dict. `wald.law` is what a consumer prints to say which law it was judged under; the kit compares its `kit` to `cage/charter.lock`.
2. **`src/wald/wire.py`**: `from_json(text)` and `to_json(result, world)` exactly as INTERFACE says — rationals as `"p/q"` strings both ways, `ops` keys back to ints, and `final` rendered through `report` as text. A Result's belief never leaves the kernel as values: `Belief` stays sealed and `to_json` must not read `_w`. Nothing in `wire.py` imports beyond the lint's list (`json` and `fractions` are on it).
3. **`src/wald/__init__.py`** exports `load_pack` (= `surface.check`), `from_json`, `to_json`, `law` beside the existing six names; `__all__` lists all ten. `KERNEL.md`'s header lists the ten and says what a host may and may not get from each.
4. **`tools/serve.py`**: the JSON-lines door, protocol as INTERFACE gives it, the server being the kernel's side of the Door and the client the world's. Outside `src/wald`, so it may `import sys, json`. Refusals cross by name; an unknown op or world id is a refusal, never a traceback; `bye` or EOF ends it cleanly. Kit L4 drives it as a subprocess and plays Appendix B against it.
5. **`pyproject.toml`** at the root: package `wald` from `src/`, version `0.1.0`, no dependencies, `requires-python >= 3.12`, license as `LICENSE` says (add MIT if there is none — owner's choice, ask if unsure). `tools/` is not part of the wheel; `wald` is.
6. **`API.md`** at the root, one page: the ten names with one line each; the wire protocol as a message-by-message example (hello, declare, run with two observes and a fire, result, bye); the versioning rule — the package's minor version follows the charter's minor, a release is a signed tag `vX.Y.Z` on this repository cut only when the cage is green, and `wald.law` names the law the release was judged under. Put the rule about the belief (values never cross; `report` is what a host sees) in its own paragraph.
7. **`tests/`**: a round trip `from_json(to_json_spec)` on Appendix A and B; `to_json` on a run; `serve.py` driven in-process the way the kit drives it.

Nothing about `decide`, `episode` or `world` changes. If a name INTERFACE asks for cannot be given without reading a sealed belief, that is a `QUESTIONS.md` entry with the reason, and stop on that point.

Report in the PR: the cage command's time; the wheel's file list; the exact `wald.law`; the example session from API.md, run.
