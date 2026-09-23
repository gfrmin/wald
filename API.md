# wald — the library and the wire

The wheel built from this repository (`uv build`, or `python3 -m build`) installs one package,
`wald`: standard library only, no dependencies, Python ≥ 3.12. It is judged by the kit of
[gfrmin/wald-charter](https://github.com/gfrmin/wald-charter) and by nothing else.

## The ten names

`import wald` exposes these ten. Everything else under `wald.` is the kernel's own and is not a
host's to call. (`wald.__all__` lists the first six for now — `QUESTIONS.md` Q5; `from wald
import *` therefore gives six, and `wald.<name>` gives all ten.)

| name | what a host gets |
|---|---|
| `declare(spec)` | a World from INTERFACE's World dict, or `Refused` with the name of the clause it breaks |
| `run(world, door)` | one episode against your `Door`: a Result with `acts`, `outcomes`, `status`, `paid`, `thought`, `steps`, `operations`, `final` |
| `Door` | the base class you subclass: say what `outcome(act)` reads and what `fire(act)` does |
| `report(belief, world=None)` | a belief as a `Display` — text, and nothing else |
| `Display` | renders with `str()`; every comparison, arithmetic, `bool`, `float`, `len` and index raises `TypeError` |
| `refusals` | `Refused` (with `.name`), `WorldFalsified`, `ObsSpent`, and every refusal name as a constant |
| `load_pack(text, data_dir)` | a pack's text elaborated to a World spec, ready for `declare`; the pack is parsed, never run |
| `from_json(text)` | the wire's World spec to INTERFACE's dict: `"p/q"` strings to rationals, `ops` keys to ints |
| `to_json(result, world)` | a Result as JSON: rationals as `"p/q"`, and the final belief as `report`'s text |
| `law` | `{"charter", "surface", "kit"}`: the signed pages and the kit this package was judged under |

There is no `push`, `condition`, `expect` or `decide` among them. A host never holds a
probability, and only the kernel chooses (CHARTER S1, E5).

## The belief

**A belief never leaves the kernel as values.** A Result's `final` is a sealed `Belief`; what a
host can have of it is `report(final, world)`, a `Display` whose text it may print, log or send,
and on which it can do nothing else. `to_json` puts that text on the wire and not the weights. There
is no way back from the text to a belief, and nothing a host does with the text reaches a choice.

## The wire

`python3 tools/serve.py` speaks JSON lines on stdin and stdout: one object per line, each way.
Every rational is a string `"p"` or `"p/q"`; a JSON float or a decimal string is refused as
`FLOAT`, and no float ever crosses. The client sends ops; during a `run` the server is the
kernel's side of the Door and the client the world's — the server asks `observe` and `fire`, each
with an `id`, and the client answers with the same `id`.

A session on CHARTER v0.1's Appendix B, run, not typed (`>` the client, `<` the server):

```
> {"op": "hello"}
< {"law": {"charter": "charter-v0.1", "surface": "surface-v0.1", "kit": "kit-v0.10"}}
> {"op": "declare", "spec": {"prior": {"sick": "1/5", "well": "4/5"}, "T": {"treat": {"sick": "0", "well": "-2"}, "leave": {"sick": "-10", "well": "0"}}, "O": {"test": {"K": {"sick": {"+": "9/10", "-": "1/10"}, "well": {"+": "1/5", "-": "4/5"}}, "price": "1/2", "once": true, "ends": {}}, "scan": {"K": {"sick": {"y": "9/10", "n": "1/10"}, "well": {"y": "2/5", "n": "3/5"}}, "price": "1/5", "once": true, "ends": {}}}, "N": 2, "d": 1, "dplus": 2, "fraction": "1/2", "rate": "1/1000", "ops": {"1": "100", "2": "200"}, "closed": true, "table_sources": {"prior": "data", "utility": "elicited", "price": "elicited", "horizon": "elicited", "depth": "elicited", "kernels": {"test": ["data"], "scan": ["data"]}, "dplus": "elicited", "fraction": "elicited", "cost": "elicited", "rate": "elicited"}}}
< {"ok": true, "world": 1}
> {"op": "run", "world": 1}
< {"observe": "scan", "id": 1}
> {"outcome": "y", "id": 1}
< {"observe": "test", "id": 2}
> {"outcome": "+", "id": 2}
< {"fire": "treat", "id": 3}
> {"fired": true, "id": 3}
< {"result": {"acts": ["scan", "test", "treat"], "outcomes": ["y", "+"], "status": "TERMINAL", "paid": "7/10", "thought": "1/5", "steps": {"struck_n": 2, "struck_cap": 0, "refused": 0, "think": 1}, "operations": [106], "final": "sick 81/113, well 32/113 | 2 live: 200 operations predicted, 144 counted since the last thought began"}}
> {"op": "bye"}
```

`{"op": "load_pack", "text": …, "data_dir": …}` answers as `declare` does. A refusal is
`{"refused": NAME, "detail": …}` and the session goes on: the World's own names from `declare`
and `load_pack`; `UNKNOWN_OP`; `UNKNOWN_WORLD`; and `WIRE` for anything that is not the protocol —
a line that is not a JSON object, a reply with the wrong `id` or key (which abandons the run), a
spec key INTERFACE does not give. An outcome the World gives no mass is not a wire error: the run
ends `WORLD_FALSIFIED` (S5). `bye`, or the end of input at any point, ends the session with exit
status 0. States, acts and outcomes cross as JSON strings (or integers).

## Versions

The package's minor version follows the charter's minor: `0.1.x` is CHARTER v0.1. A release is a
signed tag `vX.Y.Z` on this repository, cut only when the `cage` check is green, and `wald.law` in
that release names the law it was judged under — the signed charter and surface tags and the kit
tag of `cage/charter.lock`.
