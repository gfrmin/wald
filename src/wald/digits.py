"""Whole numbers of any length, read from decimal digits and written back to them, without lifting
Python's limit on integer conversion (4,300 digits by default). That limit is interpreter-wide:
lifting it, even for a moment, touches every thread and every other library in the host's
process, so the kernel never does. A real Score runs to tens of thousands of digits (brief 009):
it is read and written here CHUNK digits at a time, and every number the kernel writes for a
reader -- a Score, an E7 line, a belief in `report`, a rational on the wire -- is written by
`rational`."""
from fractions import Fraction

CHUNK = 600      # the least limit Python lets a host set is 640, so each piece converts under any


def long_int(digits):
    """A string of decimal digits, however long, as an int."""
    n = 0
    for i in range(0, len(digits), CHUNK):
        piece = digits[i:i + CHUNK]
        n = n * 10 ** len(piece) + int(piece)
    return n


def decimal(n):
    """An int, however large, as decimal digits, with a minus sign when it is negative."""
    if n < 0:
        return "-" + decimal(-n)
    if n < 10 ** CHUNK:
        return str(n)
    high, low = divmod(n, 10 ** CHUNK)
    return decimal(high) + str(low).rjust(CHUNK, "0")


def rational(q):
    """A rational as a pack writes a cell: "p/q", or "p" when q is 1."""
    q = Fraction(q)
    if q.denominator == 1:
        return decimal(q.numerator)
    return decimal(q.numerator) + "/" + decimal(q.denominator)
