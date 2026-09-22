# Brief 006 — plan: wald as a library, and the wire

Read first: `briefs/006-library.md`, the header of `charter/laws/kit_library.py` (L1–L4) and the
last section of `charter/laws/INTERFACE.md`. The owner's numbers are the package version `0.1.0`
and the three tags of `wald.law`; I choose none.

## Where it stands

The first cage run on this branch, before any code, is what the author said it would be:

    charter ok: kit-v0.10 at 3d8fd46…
    structural 37/37, surface 123/123, wordle 14/14, wordle200 16/16, think pass, wordle-think 27/27
    FAIL L1 wald exposes … load_pack, from_json, to_json, law   missing ['load_pack', 'from_json', 'to_json', 'law']
    library: 0/1 pass

So nothing of `decide`, `episode` or `world` is in question, and nothing of them changes. The
brief adds names and a door; the kernel underneath is the one the other six kits already judge.

## The seven things to build

### 1. `src/wald/law.py`

Three strings — `CHARTER = "charter-v0.1"`, `SURFACE = "surface-v0.1"`, `KIT = "kit-v0.10"` — and
`law`, the dict of them. `wald/__init__.py` binds `wald.law` to the dict after the submodule is
imported, so the attribute is the dict and not the module; a test holds that.

### 2. `src/wald/wire.py`

**`from_json(text)`** reads INTERFACE's World dict with rationals written as strings. It knows
the dict's shape, so it converts by *position*, never by trying every string: a state named
`"1/2"` stays a state. The rational positions are prior values, utility cells, kernel cells,
prices, u_end cells, `fraction`, `rate`, `ops` cells and `score` values; `ops` keys go back to
ints. Everything else — `N`, `d`, `dplus`, `once`, `closed`, `bottom`, `table_sources`,
`sources`, `components` — passes through as JSON gave it. Then the spec goes to `declare` like
any other; `from_json` validates only what the wire itself can get wrong.

What the wire can get wrong, and what it is called:
- a rational written as a JSON number, or as a decimal string such as `"0.5"`: **`FLOAT`**,
  SURFACE §5's name for "a decimal, where only exact rationals are meant". A rational is
  `-?\d+` or `-?\d+/\d+` — what `str(Fraction)` prints — and nothing else.
- a text that is not JSON, not an object, a missing key the dict must have, a key it does not
  have (a misspelt `dplus` must not quietly declare a v0 World), a JSON type it does not give, or
  a table that is not an object: **`WIRE`**. INTERFACE gives `WIRE` for "a reply out of order"; I read it as the
  wire's refusal generally. That is a reading, so it goes in `QUESTIONS.md` (Q6) with the World
  that exposes it. The kit does not test it, so the kit is green under either reading.

**`to_json(result, world)`**: `acts`, `outcomes`, `status`, `paid` and `thought` as `"p/q"`,
`steps`, `operations`, and `final` as `str(report(result.final, world))`. It imports `report`
and never touches `Belief` or `_w`: the belief crosses only as the text a host could already
print. `json` and `fractions` are on the lint's list, and nothing else is needed.

`report(final, world)` prints E6's counter, which is module state. `to_json` reads it through
`report` exactly once and changes nothing, so the kit's `str(report(r.final, world))` beside it
prints the same text.

### 3. `src/wald/__init__.py` and `KERNEL.md`

Ten names: the six, plus `load_pack = surface.check`, `from_json`, `to_json`, `law`.

*Found while building:* the brief puts all ten in `__all__`, and kit v0.10's `kit_structural.py`
ST1 still holds `__all__` to the six — the cage goes red on it. `QUESTIONS.md` Q5; work stopped on
that point, and the branch stands where both kits are green: ten names bound, `__all__` the six.

The header of
`KERNEL.md` lists the ten with what a host gets from each and what it may not get: no
probability, no belief values, no choice. Two new rows in the module table (`law.py`,
`wire.py`) and one for `tools/serve.py`.

### 4. `tools/serve.py`

JSON lines on stdin/stdout, one object per line, as INTERFACE gives it. The server holds a table
of declared Worlds by integer id. `run` builds a `Door` whose `outcome` writes
`{"observe": act, "id": n}` and reads one line, and whose `fire` writes `{"fire": act, "id": n}`
and reads one line; `run` itself is `wald.run`, unchanged. Then `{"result": to_json(…)}`.

- `Refused` crosses as `{"refused": name, "detail": …}`; `UNKNOWN_OP`, `UNKNOWN_WORLD` as INTERFACE names them.
- A reply with the wrong id, the wrong key, a non-object, non-JSON, or an outcome that is not a
  JSON scalar: `WIRE`. The run is abandoned, the server answers `{"refused": "WIRE", …}` and
  goes back to reading ops. An outcome the World cannot emit is not a wire error: it is S5, and
  the result says `WORLD_FALSIFIED`.
- `bye` or EOF, at any point including mid-run, ends it with exit status 0.
- No `try: … except Exception` around the kernel: a bug in the kernel should be a traceback, not
  a refusal with a made-up name. Everything a client can send wrong is caught by name.

### 5. `pyproject.toml` and `LICENSE`

setuptools, `src/` layout, `packages = ["wald"]`, version `0.1.0`, `dependencies = []`,
`requires-python = ">=3.12"`. There is no `LICENSE`, so MIT, as the brief allows. `tools/`,
`tests/`, `packs/` are not packages and are not in the wheel. `kit_adapter.py` is inside `wald`
and ships; it is no more of a door than `wald.belief` already is to anyone who types an
underscore — `__all__` is the surface, and API.md says so.

Checked with `uv build` (`build` is not installed here), then a plain `pip install` of the wheel into a
fresh venv — no `--no-deps`, so a dependency would show — and `import wald; wald.law` from outside the repo.

### 6. `API.md`

One page: the ten names, one line each; the wire as a transcript — hello, declare, run with two
observes and a fire, result, bye — produced by running `tools/serve.py` on Appendix B, not typed;
the versioning rule; and the belief rule in a paragraph of its own.

### 7. `tests/test_library.py`

`from_json(json.dumps(wire))` equals the Fraction spec on Appendix A and B; states that look like
rationals stay states; `FLOAT` and `WIRE` by name; `to_json` on a run; `wald.law`; and
`tools/serve.py` driven as a subprocess the way the kit drives it, plus a reply out of order, an
unknown world, and EOF mid-run.

## Not here

No change to `decide`, `episode`, `world`, `belief` or `surface`. No new verb on the surface. No
float anywhere on the wire. No release tag: a release is the owner's to cut when the cage is green.
