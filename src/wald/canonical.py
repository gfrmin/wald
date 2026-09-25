"""SURFACE v0.2 V2.13: the digest of shipped Counts and their falsifying records.

The digest is defined by its bytes: the compact JSON array `[counts, falsifiers]`, each array's
elements in ascending order of their bytes, every character of a string written as V2.13's
escape table says, the first row whose range holds it deciding. The table is below as the page
prints it, row for row, so what this module writes is the page's and not a JSON library's
reading of it: Python's `json` would agree today, but DEL (U+007F) is escaped and `/` is not
only because the table says so. The digest is a name, not a numeral (V2.12)."""
import hashlib

from .digits import decimal

ITSELF = "itself"
CODE = "\\uXXXX"                  # \u and four lowercase hex digits of the code point
PAIR = "\\uXXXX\\uXXXX"           # the same, for each half of its UTF-16 surrogate pair

# V2.13's table: (from, to, written as). The first row whose range holds a character decides.
ESCAPES = (
    (0x0022, 0x0022, '\\"'),
    (0x005C, 0x005C, "\\\\"),
    (0x0008, 0x0008, "\\b"),
    (0x000C, 0x000C, "\\f"),
    (0x000A, 0x000A, "\\n"),
    (0x000D, 0x000D, "\\r"),
    (0x0009, 0x0009, "\\t"),
    (0x0000, 0x001F, CODE),
    (0x0020, 0x007E, ITSELF),
    (0x007F, 0xFFFF, CODE),
    (0x10000, 0x10FFFF, PAIR),
)


def _char(ch):
    point = ord(ch)
    for low, high, written in ESCAPES:
        if low <= point <= high:
            if written == ITSELF:
                return ch
            if written == CODE:
                return "\\u%04x" % point
            if written == PAIR:
                v = point - 0x10000
                return "\\u%04x\\u%04x" % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF))
            return written
    raise ValueError("V2.13's table has no row for U+%04X" % point)


def _string(value):
    """A name as V2.13 writes it, or `null` for an absent end or after-report."""
    if value is None:
        return "null"
    if not isinstance(value, str):
        raise TypeError("a record holds names (V2.6), not " + repr(value))
    return '"' + "".join(_char(ch) for ch in value) + '"'


def _record(record, n=None):
    draws, end, report = record
    parts = ["[" + ",".join("[" + _string(act) + "," + _string(outcome) + "]"
                            for act, outcome in draws) + "]", _string(end), _string(report)]
    if n is not None:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError("a multiplicity is a whole number at least 1, not " + repr(n))
        parts.append(decimal(n))   # decimal digits: no sign, no exponent, no leading zero
    return "[" + ",".join(parts) + "]"


def canonical(counts, falsifiers=()):
    """The bytes V2.13 hashes. Every escape is ASCII, so byte order is the order of the text."""
    rows = sorted(_record(record, n) for record, n in counts.items())
    fal = sorted(_record(record) for record in falsifiers)
    return ("[[" + ",".join(rows) + "],[" + ",".join(fal) + "]]").encode("ascii")


def digest(counts, falsifiers=()):
    """SHA-256, lowercase hex, of the canonical bytes of `[counts, falsifiers]`."""
    return hashlib.sha256(canonical(counts, falsifiers)).hexdigest()
