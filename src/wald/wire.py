"""The wire: a World spec in, and a Result out, as JSON text (laws/INTERFACE.md, kit v0.10).

Every rational crosses as a string "p/q", both ways, so no float is ever on the wire. The spec is
read by position -- the wire knows which cells of INTERFACE's World dict are rationals -- so a
state or an outcome that happens to be spelled "1/2" stays a name. `from_json` refuses only what
the wire itself can get wrong -- a key the dict does not have, a JSON type it does not give, a
rational not written "p/q". The World's own rules are `declare`'s, and the spec goes there next.

A Result's belief never crosses as values (S1). `to_json` hands the host what `report` renders
and nothing else: it does not open the Belief, and there is no way back from the text."""
import json
from fractions import Fraction

from .belief import report
from .digits import long_int, rational
from .refusals import FLOAT, WIRE, Refused

_DIGITS = "0123456789"

# INTERFACE's World dict, whole: a key outside these is refused, so a misspelt `dplus` cannot
# quietly declare a v0 World.
_SPEC_KEYS = ("prior", "T", "O", "N", "d", "closed", "bottom", "table_sources", "sources",
              "components", "dplus", "fraction", "rate", "ops", "score")
_ACT_KEYS = ("K", "price", "once", "ends")


def _natural(text):
    return text != "" and all(c in _DIGITS for c in text)


def _decimal(text):
    """A number with a point or an exponent: what a float prints, and what the wire refuses."""
    try:
        Fraction(text)
    except (ValueError, ZeroDivisionError):
        return False
    return any(c in text for c in ".eE") and text == text.strip()


def _rational(x, where):
    """A rational as `str(Fraction)` prints it, "p" or "p/q", and never a JSON number: a float or
    a decimal string ("0.5", "1e-3") is FLOAT, as it is in a pack; anything else not so spelled is WIRE."""
    if type(x) is float:
        raise Refused(FLOAT, where + ": " + json.dumps(x) + " is not exact; write it \"p/q\"")
    if type(x) is not str:
        raise Refused(WIRE, where + ": a rational is a string \"p/q\", not " + json.dumps(x))
    body = x[1:] if x.startswith("-") else x
    p, slash, q = body.partition("/")
    if not _natural(p) or (slash and not _natural(q)):
        if _decimal(x):
            raise Refused(FLOAT, where + ": " + json.dumps(x) + " is a decimal; write it \"p/q\"")
        raise Refused(WIRE, where + ": " + json.dumps(x) + " is not a rational")
    den = long_int(q) if slash else 1
    if not den:
        raise Refused(WIRE, where + ": " + json.dumps(x) + " divides by zero")
    return Fraction(-long_int(p) if x.startswith("-") else long_int(p), den)


def _table(x, where):
    if not isinstance(x, dict):
        raise Refused(WIRE, where + ": a table is a JSON object")
    return x


def _row(x, where):
    """{name: rational}, the names left as they are."""
    return {k: _rational(v, where + "[" + json.dumps(k) + "]") for k, v in _table(x, where).items()}


def _rows(x, where):
    """{name: {name: rational}}, in the order the wire gave it."""
    return {k: _row(v, where + "[" + json.dumps(k) + "]") for k, v in _table(x, where).items()}


def _count(x, where):
    """N, d and Depth+ are integers, and a JSON float is not one even when it is whole."""
    if type(x) is float:
        raise Refused(FLOAT, where + ": " + json.dumps(x) + " is a JSON number with a point; write an integer")
    if type(x) is not int:
        raise Refused(WIRE, where + ": an integer, not " + json.dumps(x))
    return x


def _flag(x, where):
    if type(x) is not bool:
        raise Refused(WIRE, where + ": true or false, not " + json.dumps(x))
    return x


def _name(x, where):
    """A state, an act, an outcome or a source, where it is a value and not a key."""
    if type(x) not in (str, int):
        raise Refused(WIRE, where + ": a name is a string or an integer, not " + json.dumps(x))
    return x


def _names(x, where):
    if not isinstance(x, list):
        raise Refused(WIRE, where + ": a list of names, not " + json.dumps(x))
    return [_name(v, where) for v in x]


def _tags(x, where):
    """table_sources: a tag per table, and per act the sorted list of its kernel's tags (kit v0.3)."""
    out = {}
    for k, v in _table(x, where).items():
        if k == "kernels":
            out[k] = {a: _names(t, where + ".kernels") for a, t in _table(v, where + ".kernels").items()}
        else:
            out[k] = _name(v, where + "." + k)
    return out


def _known(spec, keys, where):
    for key in spec:
        if key not in keys:
            raise Refused(WIRE, where + ": " + json.dumps(key) + " is not a key INTERFACE gives")


def _need(spec, key, where):
    if key not in spec:
        raise Refused(WIRE, where + ": no " + json.dumps(key))
    return spec[key]


def _act(spec, where):
    _known(_table(spec, where), _ACT_KEYS, where)
    out = dict(spec)
    out["K"] = _rows(_need(spec, "K", where), where + ".K")
    out["price"] = _rational(_need(spec, "price", where), where + ".price")
    out["once"] = _flag(_need(spec, "once", where), where + ".once")
    out["ends"] = _rows(spec.get("ends", {}), where + ".ends")
    return out


def from_json(text):
    """INTERFACE's World dict, from the wire: rationals back to Fractions and `ops` keys back to
    the ints they count. Every other field INTERFACE names is checked for its JSON type and passed
    through. A key it does not name is refused rather than ignored."""
    try:
        spec = json.loads(text)
    except ValueError as e:
        raise Refused(WIRE, "not JSON: " + str(e))
    _known(_table(spec, "spec"), _SPEC_KEYS, "spec")
    for key in ("prior", "T", "O", "N", "d"):
        _need(spec, key, "spec")
    out = dict(spec)
    out["prior"] = _row(spec["prior"], "prior")
    out["T"] = _rows(spec["T"], "T")
    out["O"] = {k: _act(v, "O[" + json.dumps(k) + "]") for k, v in _table(spec["O"], "O").items()}
    for key in ("N", "d", "dplus"):
        if key in spec:
            out[key] = _count(spec[key], key)
    if "closed" in spec:
        out["closed"] = _flag(spec["closed"], "closed")
    if "bottom" in spec:
        out["bottom"] = _name(spec["bottom"], "bottom")
    if "table_sources" in spec:
        out["table_sources"] = _tags(spec["table_sources"], "table_sources")
    if "sources" in spec:
        out["sources"] = {a: _names(v, "sources") for a, v in _table(spec["sources"], "sources").items()}
    if "components" in spec:
        out["components"] = _names(spec["components"], "components")
    for key in ("fraction", "rate"):
        if key in spec:
            out[key] = _rational(spec[key], key)
    if "ops" in spec:
        ops = {}
        for s, v in _table(spec["ops"], "ops").items():
            if not _natural(s):
                raise Refused(WIRE, "ops: " + json.dumps(s) + " is not a count of live states")
            ops[int(s)] = _rational(v, "ops[" + s + "]")
        out["ops"] = ops
    if "score" in spec:
        out["score"] = _row(spec["score"], "score")
    return out


def to_json(result, world):
    """A Result as JSON text: the acts and outcomes as played, the status, what was paid in prices
    and in thought as "p/q", S7's counts and E6's, and the final belief as the text of `report`."""
    return json.dumps({
        "acts": list(result.acts),
        "outcomes": list(result.outcomes),
        "status": result.status,
        "paid": rational(result.paid),
        "thought": rational(result.thought),
        "steps": dict(result.steps),
        "operations": list(result.operations),
        "final": str(report(result.final, world)),
    })
