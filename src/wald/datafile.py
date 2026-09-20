"""SURFACE section 4, K5: a kernel's rows read from a JSON file beside the pack and pinned by the
SHA-256 of its bytes. This is the only file the kernel ever reads, and it is read as bytes and
parsed as JSON -- never imported, never executed. An `elicited` number is written in the pack,
where its owner can see it; only `data` and `fitted` tables come from a file."""
import hashlib
import json
import pathlib
from fractions import Fraction

from .refusals import DATA_HASH, DUPLICATE, FLOAT, NOT_A_DECLARATION, Refused


def rows(data_dir, name, sha256):
    """The pinned file as {state: {outcome: Fraction}}, and the count of numbers in it.
    A tuple state is written as a JSON list."""
    path = pathlib.Path(data_dir) / name
    if not path.is_file():
        raise Refused(DATA_HASH, "the file " + repr(name) + " the pack pinned is not beside it")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise Refused(DATA_HASH, repr(name) + " is not the file the pack pinned")
    try:
        pairs = json.loads(raw)
    except ValueError as e:
        raise Refused(NOT_A_DECLARATION, repr(name) + " is not JSON: " + str(e))
    if not isinstance(pairs, list):
        raise Refused(NOT_A_DECLARATION, repr(name) + " is a list of [state, {outcome: \"a/b\"}] pairs")
    K, count = {}, 0
    for pair in pairs:
        if not (isinstance(pair, list) and len(pair) == 2 and isinstance(pair[1], dict)):
            raise Refused(NOT_A_DECLARATION,
                          repr(name) + " is a list of [state, {outcome: \"a/b\"}] pairs")
        state = tuple(pair[0]) if isinstance(pair[0], list) else pair[0]
        if state in K:
            raise Refused(DUPLICATE, "the state " + repr(state) + " is listed twice in " + repr(name))
        row = {}
        for outcome, q in pair[1].items():
            if isinstance(q, float):
                raise Refused(FLOAT, repr(name) + ": " + repr(q) + " is not exact; write \"a/b\"")
            try:
                row[outcome] = Fraction(q)
            except (ValueError, TypeError):
                raise Refused(NOT_A_DECLARATION, repr(name) + ": " + repr(q) + " is not a number")
        K[state] = row
        count += len(row)
    return K, count
