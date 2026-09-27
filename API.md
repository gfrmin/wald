# wald — the library and the wire

The wheel built from this repository (`uv build`, or `python3 -m build`) installs one package,
`wald`: standard library only, no dependencies, Python ≥ 3.12. It is judged by the kit of
[gfrmin/wald-charter](https://github.com/gfrmin/wald-charter) and by nothing else.

## The fourteen names

`import wald` exposes these fourteen, and `wald.__all__` lists them. Everything else under `wald.`
is the kernel's own and is not a host's to call.

| name | what a host gets |
|---|---|
| `declare(spec)` | a World from INTERFACE's World dict, or `Refused` with the name of the clause it breaks |
| `run(world, door)` | one episode against your `Door`: a Result with `acts`, `outcomes`, `status`, `paid`, `thought`, `steps`, `operations`, `final`, `record` |
| `Door` | the base class you subclass: say what `outcome(act)` reads and what `fire(act)` does |
| `report(belief, world=None)` | a belief as a `Display` — text, and nothing else |
| `Display` | renders with `str()`; every comparison, arithmetic, `bool`, `float`, `len` and index raises `TypeError` |
| `refusals` | `Refused` (with `.name`), `WorldFalsified`, `ObsSpent`, and every refusal name as a constant |
| `load_pack(text, data_dir)` | a pack's text elaborated to a World spec, ready for `declare` — CHARTER v0.2's dict for a pack that declares what is learned; the pack is parsed, never run |
| `from_json(text)` | the wire's World spec to INTERFACE's dict: `"p/q"` strings to rationals, `ops` keys to ints |
| `to_json(result, world)` | a Result as JSON: rationals as `"p/q"`, and the final belief as `report`'s text |
| `law` | `{"charter", "surface", "kit"}`: the signed pages and the kit this package was judged under |
| `plate(world)` | a Plate: `run(door)` plays one episode from the prior its Counts give, `counts()`, `falsifier()`, and `disclosure()` as a `Display` |
| `digest(counts, falsifiers=())` | SURFACE v0.2 V2.13's digest of Counts and falsifying records: lowercase hex, the `sha256` a pack writes |
| `score(world, counts, falsifiers=())` | V2.8's Score of them under `world`, as `declare` returned it, written as a pack writes the cell: `"p/q"`, or `"p"` when q is 1, in decimal digits however many |
| `e7(world, counts)` | CHARTER v0.2 E7's lines as a `Display`: for every draw, by the history that led to it, the total variation between what Counts saw and the posterior predictive, each an exact rational |

There is no `push`, `condition`, `expect` or `decide` among them. The Score comes back as text:
it is a measurement a pack writes and the kernel checks, not a number a host acts on. A host never holds a
probability, and only the kernel chooses (CHARTER S1, E5).

## The belief

**A belief never leaves the kernel as values.** A Result's `final` is a sealed `Belief`; what a
host can have of it is `report(final, world)`, a `Display` whose text it may print, log or send,
and on which it can do nothing else. `to_json` puts that text on the wire and not the weights. There
is no way back from the text to a belief, and nothing a host does with the text reaches a choice.

## The plate

CHARTER v0.2: what is learned between episodes. A World declares some dimensions of Ω as
**Globals** (an instrument's reliability, a model's quality) and the rest as **locals**, drawn
afresh each episode from P(local | Global); it may declare one **After-act**, a report taken once
the episode has ended (a grade). Such a World comes from a pack (below), or from INTERFACE's v0.2
dict (`locals`, `globals`, `prior_global`, `prior_local`, `after`, with states the pairs `(l, g)`) —
the dict `load_pack` returns, which carries no sources; give it `table_sources` and they are
checked as any spec's.

```python
p = wald.plate(wald.declare(wald.load_pack(text, data_dir)))
r = p.run(door)          # the prior from p's Counts; v0's episode; the terminal fired; then, if an
                         # After-act is declared, door.outcome("grade") -- asked by name, after the fire
r.record                 # ((("ask", "a1"),), "say a1", "a1"): the draws, the end, the after-report
p.counts()               # a Counter of records: facts, which a host may hold (S1)
print(p.disclosure())    # what no plate of this World can ever learn (S15), as text
```

A plate keeps its Counts and nothing else. A report of probability zero, in the episode or in the
after-report, ends the plate: `r.status` is `WORLD_FALSIFIED`, the Counts stay as they were,
`p.falsifier()` holds the record that did it, and a further `run` raises `WorldFalsified`. A World
with no Global plays on a plate exactly as under `run`. `run` itself takes a v0 World; a World
that declares what is learned is played on a plate.

## Declaring what is learned, in a pack (SURFACE v0.2)

Six declarations and one more kind of Score, each with the rule of `charter/SURFACE-v0.2.md` that
states it. Every refusal names its rule, as `[V2.k]` in its detail.

| written | says | rule |
|---|---|---|
| `globals(["rel"])` | which components of the space are Global; after `space`, before `prior`; every component may be (a monitor) | V2.1 |
| `prior({"9/10": 1/2, "3/5": 1/2}, source=…)` | with Globals, P(Global), keyed by Global value — a name for one Global component, a tuple for several; without, v0's prior | V2.2 |
| `local_prior({"9/10": {"a1": 1/2, "a2": 1/2}, …}, source=…)` | P(local \| Global): a row for each Global value the prior names; after `prior`; required when some component is local | V2.3 |
| — | the states are the pairs the two give positive mass; every other table over states is keyed by them, as in SURFACE v0 | V2.4 |
| `after("grade", kernel=table({end: {state: {outcome: p}}}, source=…), reads=[…])` | the After-act: a row for exactly the ends — each terminal, and `("act", "outcome")` for each ending outcome — its `reads`, and its price a cell of `price` | V2.5 |
| `counts([[draws, end, after, n], …], sha256="…", source="data")` | shipped Counts: each record once, `n` written as decimal digits (no `True`, `0x1`, `1_0`), every outcome a name; no terminal's name begins `end:` | V2.6 |
| `falsifiers([[draws, end, after], …])` | the falsifying records the Counts travel with: a prefix `[draws, None, None]`, or a full record whose after-report falsified | V2.7 |
| `score(value, of="counts", source="data")` | the Score: for every copy of every record and every falsifying record, its likelihood under the prior conditioned on all the others, multiplied; the kernel recomputes it (`UNSCORED`) | V2.8 |

A World that declares an After-act or Counts and no Global has one Global value, `()` (V2.9). No
utility is written `by(...)` over a Global (`GLOBAL`, V2.10). A pack is UTF-8 with LF line endings:
**read it as its bytes are written** — `path.read_bytes().decode("utf-8")`, never a text mode that
translates newlines — for a CR anywhere, a coding declaration naming another encoding, a surrogate
in any string, or an identifier outside ASCII is refused `NOT_A_DECLARATION` (V2.11).
`python3 tools/wald_check.py pack.py` does that, and prints what the pack declares and learns.

**Numbers of any length.** A cell, a multiplicity and a Score may have any number of digits: a
Score of 300 graded records has tens of thousands. Python refuses to convert more than 4,300
digits by default, and that limit is the whole interpreter's, so `wald` never lifts it:
`load_pack` reads a long literal a piece at a time, and every number `wald` writes — a Score, an E7
line, a belief in `report`, a rational on the wire — is written the same way. Your host's limit is
the same after any call as before it.

**The digest** (V2.13) is the SHA-256, lowercase hex, of the bytes of the compact JSON array
`[counts, falsifiers]`: the records `[draws,end,after,n]` and the falsifying records
`[draws,end,after]`, each array in ascending order of its elements' bytes, no whitespace, `null`
for an absent end or after-report, and every character written as the page's escape table says —
`\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, other controls and everything from U+007F up as
`\u` and four lowercase hex digits (an astral character as its surrogate pair), and U+0020–U+007E
as themselves. DEL is escaped; `/` is not. Appendix A's one right grade:

```
$ printf '%s' '[[[[["ask","a1"]],"say a1","a1",1]],[]]' | sha256sum
c0cd11a6dbce579fb5a0ccc1e157fd2316358b4d31bcb47889e8072c50b53dba  -
```

## Shipping a plate's Counts, with `wald` alone

A host that played a plate can write the pack that ships its Counts to a refit or a sibling: the
bare pack, then `counts(...)` from `Plate.counts()`, `falsifiers(...)` from `Plate.falsifier()`,
the `sha256` from `wald.digest`, and `score(...)` from `wald.score`. Appendix A (SURFACE v0.2's
appendix pack, `appendix_a.py` beside the script), three graded episodes, run, not typed
(`tests/test_ship.py` runs this block as it stands here):

```python
import wald

with open("appendix_a.py", encoding="utf-8", newline="") as f:     # read as written (V2.11)
    bare = f.read()
world = wald.declare(wald.load_pack(bare, "."))


class Question(wald.Door):
    """One episode: the true answer, and what `ask` reports of it. The grade reveals the answer."""

    def __init__(self, answer, report):
        self.answer, self.report = answer, report

    def outcome(self, act):
        return self.report if act == "ask" else self.answer

    def fire(self, act):
        pass


p = wald.plate(world)
for answer, report in [("a1", "a1"), ("a2", "a2"), ("a1", "a2")]:
    p.run(Question(answer, report))

counts = p.counts()
falsifiers = [p.falsifier()] if p.falsifier() is not None else []


def record(draws, end, after):
    return "[" + repr([list(d) for d in draws]) + ", " + repr(end) + ", " + repr(after)


lines = ["counts([" + ", ".join(record(*r) + ", " + str(n) + "]" for r, n in counts.items()) + "], "
         + "sha256=" + repr(wald.digest(counts, falsifiers)) + ', source="data")']
if falsifiers:
    lines.append("falsifiers([" + ", ".join(record(*f) + "]" for f in falsifiers) + "])")
lines.append("score(" + wald.score(world, counts, falsifiers) + ', of="counts", source="data")')
shipped = bare + "\n".join(lines) + "\n"

refit = wald.declare(wald.load_pack(shipped, "."))   # the digest and the Score are checked here
print(shipped)
print(wald.e7(world, counts))
```

It prints the bare pack, then these three lines — two right grades and one wrong, whose Score is
CHARTER v0.2 appendix I's 1125/100672 — and E7:

```
counts([[[['ask', 'a1']], 'say a1', 'a1', 1], [[['ask', 'a2']], 'say a2', 'a2', 1], [[['ask', 'a2']], 'say a2', 'a1', 1]], sha256='2f4a30a562cd94f39e49a198a36f480ef5df7383aedec2a4e32500deee633976', source="data")
score(1125/100672, of="counts", source="data")

E7: total variation between each draw's outcomes in Counts and its posterior predictive, by the history that led to it
after the start: ask 1/6
after ask=a1, then say a1: grade 73/250
after ask=a2, then say a2: grade 26/125
```

`repr` writes each name as a Python string literal the pack reads back as the same name, and
`None` for an absent end or after-report. A plate that was falsified ships its falsifying record in
`falsifiers(...)`, and its Score scores it too. The refit declares only if it could have written
every record itself and all of them together have positive probability under some Global value
(CHARTER v0.2 S13); otherwise it is refused `PLATE`.

## The wire

`python3 tools/serve.py` speaks JSON lines on stdin and stdout: one object per line, each way.
Every rational is a string `"p"` or `"p/q"`; a JSON float or a decimal string is refused as
`FLOAT`, and no float ever crosses. The client sends ops; during a `run` the server is the
kernel's side of the Door and the client the world's — the server asks `observe` and `fire`, each
with an `id`, and the client answers with the same `id`.

A session on CHARTER v0.1's Appendix B, run, not typed (`>` the client, `<` the server):

```
> {"op": "hello"}
< {"law": {"charter": "charter-v0.2", "surface": "surface-v0.2", "kit": "kit-v0.13"}}
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
