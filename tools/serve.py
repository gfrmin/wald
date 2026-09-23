"""The wire: wald spoken to over stdin/stdout in JSON lines (laws/INTERFACE.md, kit v0.10; API.md).

    python3 tools/serve.py

One JSON object per line, each way. The client sends ops -- `hello`, `declare`, `load_pack`,
`run`, `bye` -- and during a `run` the server is the kernel's side of the Door and the client the
world's: the server asks `{"observe": act, "id": n}` and `{"fire": act, "id": n}`, the client
answers `{"outcome": o, "id": n}` and `{"fired": true, "id": n}`, and the episode ends with
`{"result": ...}` as `wald.to_json` writes it.

Outside src/, so it may import sys and json; it holds no semantics of its own and uses the ten
names of `wald` and nothing under them. The kernel does no I/O: this file is all of it. What a
client can send wrong is refused by name -- `UNKNOWN_OP`, `UNKNOWN_WORLD`, `WIRE`, and every name
of `wald.refusals` that `declare` or `load_pack` can speak -- and `bye` or end of input, at any
point, ends the session cleanly. A fault in the kernel itself is not caught: it is a traceback,
not a refusal under a made-up name.
"""
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

import wald                                            # noqa: E402
from wald.refusals import WIRE, Refused                # noqa: E402

UNKNOWN_OP = "UNKNOWN_OP"          # an op the protocol does not have
UNKNOWN_WORLD = "UNKNOWN_WORLD"    # a world id this session did not declare


class Hangup(Exception):
    """The client's end closed. Not an error: the session is over."""


class Wire:
    """One JSON object per line, each way."""

    def __init__(self, inp, out):
        self.inp, self.out = inp, out

    def send(self, obj):
        self.out.write(json.dumps(obj) + "\n")
        self.out.flush()

    def recv(self):
        """The next object, skipping blank lines. End of input is a Hangup; a line that is not a
        JSON object is refused as WIRE, and the line is gone."""
        while True:
            line = self.inp.readline()
            if not line:
                raise Hangup()
            if line.strip():
                break
        try:
            msg = json.loads(line)
        except ValueError as e:
            raise Refused(WIRE, "not JSON: " + str(e))
        if not isinstance(msg, dict):
            raise Refused(WIRE, "a message is a JSON object")
        return msg


class WireDoor(wald.Door):
    """The world's side of the Door is the client. Every question carries an id and the answer must
    carry the same one and the key the question asked for; anything else is out of order."""

    def __init__(self, wire, ids):
        self.wire, self.ids = wire, ids

    def ask(self, question, key):
        n = next(self.ids)
        self.wire.send(dict(question, id=n))
        reply = self.wire.recv()
        if key not in reply or type(reply.get("id")) is not int or reply["id"] != n:
            raise Refused(WIRE, "asked " + json.dumps(dict(question, id=n)) + ", got " + json.dumps(reply))
        return reply[key]

    def outcome(self, act):
        o = self.ask({"observe": act}, "outcome")
        if type(o) not in (str, int):
            raise Refused(WIRE, "an outcome is a string or an integer, not " + json.dumps(o))
        return o

    def fire(self, act):
        if self.ask({"fire": act}, "fired") is not True:
            raise Refused(WIRE, "a fire is answered with \"fired\": true")


class Session:
    def __init__(self, inp, out):
        self.wire = Wire(inp, out)
        self.worlds = {}
        self.ids = itertools.count(1)

    def declared(self, spec):
        wid = len(self.worlds) + 1
        self.worlds[wid] = wald.declare(spec)
        return {"ok": True, "world": wid}

    def op_hello(self, msg):
        return {"law": wald.law}

    def op_declare(self, msg):
        return self.declared(wald.from_json(json.dumps(msg.get("spec"))))

    def op_load_pack(self, msg):
        text, data_dir = msg.get("text"), msg.get("data_dir", ".")
        if not isinstance(text, str) or not isinstance(data_dir, str):
            raise Refused(WIRE, "load_pack takes \"text\" and \"data_dir\" as strings")
        return self.declared(wald.load_pack(text, data_dir))

    def op_run(self, msg):
        wid = msg.get("world")
        if type(wid) is not int or wid not in self.worlds:
            return {"refused": UNKNOWN_WORLD, "detail": "no world " + json.dumps(wid) + " in this session"}
        world = self.worlds[wid]
        result = wald.run(world, WireDoor(self.wire, self.ids))
        return {"result": json.loads(wald.to_json(result, world))}

    def serve(self):
        ops = {"hello": self.op_hello, "declare": self.op_declare,
               "load_pack": self.op_load_pack, "run": self.op_run}
        while True:
            try:
                msg = self.wire.recv()
                if "op" not in msg:
                    raise Refused(WIRE, "no op, and no question outstanding: " + json.dumps(msg))
                if msg["op"] == "bye":
                    return
                handler = ops.get(msg["op"]) if isinstance(msg["op"], str) else None
                if handler is None:
                    reply = {"refused": UNKNOWN_OP, "detail": "no op " + json.dumps(msg["op"])}
                else:
                    reply = handler(msg)
            except Hangup:
                return
            except Refused as e:
                reply = {"refused": e.name, "detail": str(e)}
            self.wire.send(reply)


def main():
    Session(sys.stdin, sys.stdout).serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
