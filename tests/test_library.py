"""Brief 006: wald as a library, and the wire. The ten names, `from_json` and `to_json` on the
page's Appendix A and B, and `tools/serve.py` driven over a pipe the way kit L4 drives it -- and
then the ways a client can get the wire wrong, each of which must come back as a refusal by name,
never a traceback. The kit judges; these are how I know before it does."""
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction as F

import _path
from world_fixtures import APPX_K, APPX_T, act, spec
import wald
from wald.refusals import FLOAT, WIRE, Refused

SERVE = os.path.join(_path.ROOT, "tools", "serve.py")
SCAN_K = {"sick": {"y": F(9, 10), "n": F(1, 10)}, "well": {"y": F(2, 5), "n": F(3, 5)}}
META = {"N": 2, "d": 1, "dplus": 2, "fraction": F(1, 2), "rate": F(1, 1000),
        "ops": {1: F(100), 2: F(200)}}
META_SRC = {"dplus": "elicited", "fraction": "elicited", "cost": "elicited", "rate": "elicited"}


def thinker(O):
    s = spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T, O, **META)
    s["table_sources"].update(META_SRC)
    return s


def vector_A():
    return thinker({"test": act(APPX_K, F(1, 2), once=False)})


def vector_B():
    return thinker({"test": act(APPX_K, F(1, 2)), "scan": act(SCAN_K, F(1, 5))})


def wire(s):
    """The wire's spelling of a spec: every Fraction a string, every key a string."""
    return json.dumps(s, default=str)


class Script(wald.Door):
    def __init__(self, outcomes):
        self.outcomes, self.fired = list(outcomes), []

    def outcome(self, act):
        return self.outcomes.pop(0)

    def fire(self, act):
        self.fired.append(act)


def refused(f, *args):
    try:
        f(*args)
    except Refused as e:
        return e.name
    return None


class TheElevenNames(unittest.TestCase):
    def test_all(self):
        """Eleven names on `wald`, and `__all__` lists them (ST1 as of kit v0.11; Q5 answered)."""
        for name in ("declare", "run", "Door", "report", "Display", "refusals",
                     "load_pack", "from_json", "to_json", "law", "plate"):
            self.assertTrue(hasattr(wald, name), name)
        self.assertEqual(set(wald.__all__), {"declare", "run", "Door", "report", "Display", "refusals",
                                             "load_pack", "from_json", "to_json", "law", "plate"})

    def test_plate_is_the_function_not_the_module(self):
        import wald.plate                                   # noqa: F401 -- the submodule, again
        self.assertTrue(callable(wald.plate))

    def test_law_is_the_dict_not_the_module(self):
        import wald.law                                     # noqa: F401 -- the submodule, again
        self.assertEqual(wald.law, {"charter": "charter-v0.1", "surface": "surface-v0.1",
                                    "kit": "kit-v0.11"})

    def test_law_kit_is_the_lock(self):
        with open(os.path.join(_path.ROOT, "cage", "charter.lock")) as f:
            tag = [line.split("=", 1)[1].strip() for line in f if line.startswith("TAG=")][0]
        self.assertEqual(wald.law["kit"], tag)

    def test_no_verb_of_section_2(self):
        """`wald.decide` exists as the submodule, which Python sets on its parent; the verb does not."""
        for verb in ("push", "condition", "expect", "decide", "step"):
            self.assertNotIn(verb, wald.__all__)
            self.assertFalse(callable(getattr(wald, verb, None)), verb)


class FromJson(unittest.TestCase):
    def test_round_trip_appendix(self):
        for s in (vector_A(), vector_B()):
            back = wald.from_json(wire(s))
            self.assertEqual(back, s)
            self.assertEqual(set(back["ops"]), {1, 2})
            self.assertIsInstance(back["prior"]["sick"], F)

    def test_a_state_spelled_like_a_rational_stays_a_name(self):
        s = spec({"1/2": F(1, 3), "3": F(2, 3)}, {"t": {"1/2": F(0), "3": F(1)}},
                 {"k": act({"1/2": {"0.5": F(1)}, "3": {"0.5": F(1)}}, F(0))})
        back = wald.from_json(wire(s))
        self.assertEqual(list(back["prior"]), ["1/2", "3"])
        self.assertEqual(list(back["O"]["k"]["K"]["1/2"]), ["0.5"])
        wald.declare(back)

    def test_order_is_kept(self):
        s = vector_B()
        self.assertEqual(list(wald.from_json(wire(s))["O"]), ["test", "scan"])

    def test_float_by_name(self):
        s = json.loads(wire(vector_A()))
        s["prior"]["sick"] = 0.2
        self.assertEqual(refused(wald.from_json, json.dumps(s)), FLOAT)
        s["prior"]["sick"] = "0.2"
        self.assertEqual(refused(wald.from_json, json.dumps(s)), FLOAT)
        s = json.loads(wire(vector_A()))
        s["N"] = 2.0
        self.assertEqual(refused(wald.from_json, json.dumps(s)), FLOAT)

    def test_wire_by_name(self):
        good = json.loads(wire(vector_A()))
        bad = [
            "not json", "[]", json.dumps(dict(good, dplsu=2)), json.dumps({k: v for k, v in good.items() if k != "N"}),
            json.dumps(dict(good, rate=1)), json.dumps(dict(good, N="2")), json.dumps(dict(good, closed="yes")),
            json.dumps(dict(good, ops={"one": "100", "2": "200"})), json.dumps(dict(good, table_sources=[])),
            json.dumps(dict(good, O={"test": dict(good["O"]["test"], once="no")})),
            json.dumps(dict(good, O={"test": dict(good["O"]["test"], K=[])})),
            json.dumps(dict(good, components=3)), json.dumps(dict(good, bottom=["x"])),
            json.dumps(dict(good, fraction="1/0")),
        ]
        for text in bad:
            self.assertEqual(refused(wald.from_json, text), WIRE, text[:80])

    def test_the_world_refuses_under_its_own_names(self):
        s = vector_A()
        s["fraction"] = F(3, 2)
        self.assertEqual(refused(wald.declare, wald.from_json(wire(s))), "FRACTION")


class ToJson(unittest.TestCase):
    def test_appendix_B(self):
        world = wald.declare(wald.from_json(wire(vector_B())))
        r = wald.run(world, Script(["y", "+"]))
        out = json.loads(wald.to_json(r, world))
        self.assertEqual(out["acts"], ["scan", "test", "treat"])
        self.assertEqual(out["outcomes"], ["y", "+"])
        self.assertEqual(out["status"], "TERMINAL")
        self.assertEqual(out["paid"], "7/10")
        self.assertEqual(out["thought"], "1/5")
        self.assertEqual(out["steps"]["think"], 1)
        self.assertEqual(out["operations"], list(r.operations))
        self.assertEqual(out["final"], str(wald.report(r.final, world)))
        self.assertEqual(set(out), {"acts", "outcomes", "status", "paid", "thought", "steps",
                                    "operations", "final"})

    def test_appendix_A(self):
        world = wald.declare(wald.from_json(wire(vector_A())))
        r = wald.run(world, Script(["+"]))
        out = json.loads(wald.to_json(r, world))
        self.assertEqual((out["acts"], out["paid"], out["thought"]), (["test", "treat"], "1/2", "1/5"))

    def test_wire_never_reads_a_belief(self):
        """The brief's rule, checked where it lives: nothing in wire.py names the sealed weights,
        the package-private reader of them, or the Belief class. The belief leaves as `report`."""
        import ast
        with open(os.path.join(_path.ROOT, "src", "wald", "wire.py")) as f:
            tree = ast.parse(f.read())
        names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
        self.assertFalse(names & {"_w", "_weights", "_measure", "Belief", "_sealed"}, names)


class Client:
    """The world's end of the wire, as kit L4 is."""

    def __init__(self):
        env = dict(os.environ, PYTHONPATH=os.path.join(_path.ROOT, "src"))
        self.p = subprocess.Popen([sys.executable, SERVE], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  env=env, cwd=_path.ROOT)

    def send(self, obj):
        self.p.stdin.write((obj if isinstance(obj, str) else json.dumps(obj)) + "\n")
        self.p.stdin.flush()

    def recv(self):
        line = self.p.stdout.readline()
        if not line:
            raise RuntimeError("server closed: " + self.p.stderr.read()[-600:])
        return json.loads(line)

    def ask(self, obj):
        self.send(obj)
        return self.recv()

    def play(self, wid, script):
        """Run a world, answering the door from a script; the fired acts and the result."""
        script, fired = list(script), []
        msg = self.ask({"op": "run", "world": wid})
        while "observe" in msg or "fire" in msg:
            if "observe" in msg:
                msg = self.ask({"outcome": script.pop(0), "id": msg["id"]})
            else:
                fired.append(msg["fire"])
                msg = self.ask({"fired": True, "id": msg["id"]})
        return fired, msg

    def close(self):
        self.p.stdin.close()
        code = self.p.wait(timeout=10)
        err = self.p.stderr.read()
        self.p.stdout.close()
        self.p.stderr.close()
        return code, err


class Serve(unittest.TestCase):
    def setUp(self):
        self.c = Client()

    def tearDown(self):
        if self.c.p.poll() is None:
            self.c.p.kill()
            self.c.p.wait()
        for f in (self.c.p.stdin, self.c.p.stdout, self.c.p.stderr):
            if not f.closed:
                f.close()

    def test_appendix_B_over_the_wire_equals_in_process(self):
        self.assertEqual(self.c.ask({"op": "hello"}), {"law": wald.law})
        d = self.c.ask({"op": "declare", "spec": json.loads(wire(vector_B()))})
        self.assertEqual(d, {"ok": True, "world": 1})
        fired, msg = self.c.play(1, ["y", "+"])
        self.assertEqual(fired, ["treat"])
        world = wald.declare(vector_B())
        here = json.loads(wald.to_json(wald.run(world, Script(["y", "+"])), world))
        self.assertEqual(msg, {"result": here})
        self.c.send({"op": "bye"})
        self.assertEqual(self.c.close(), (0, ""))

    def test_refusals_by_name_and_the_session_goes_on(self):
        bad = json.loads(wire(vector_A()))
        bad["fraction"] = "3/2"
        self.assertEqual(self.c.ask({"op": "declare", "spec": bad})["refused"], "FRACTION")
        bad["fraction"] = 0.5
        self.assertEqual(self.c.ask({"op": "declare", "spec": bad})["refused"], FLOAT)
        self.assertEqual(self.c.ask({"op": "nonsense"})["refused"], "UNKNOWN_OP")
        self.assertEqual(self.c.ask({"op": 7})["refused"], "UNKNOWN_OP")
        self.assertEqual(self.c.ask({"op": "run", "world": 9})["refused"], "UNKNOWN_WORLD")
        self.assertEqual(self.c.ask({"op": "run", "world": [1]})["refused"], "UNKNOWN_WORLD")
        self.assertEqual(self.c.ask("not json")["refused"], WIRE)
        self.assertEqual(self.c.ask("[1, 2]")["refused"], WIRE)
        self.assertEqual(self.c.ask({"outcome": "+", "id": 1})["refused"], WIRE)
        self.assertEqual(self.c.ask({"op": "load_pack", "text": 3})["refused"], WIRE)
        self.assertEqual(self.c.ask({"op": "load_pack", "text": "prior(", "data_dir": "."})["refused"], "SYNTAX")
        self.assertEqual(self.c.ask({"op": "hello"}), {"law": wald.law})
        self.c.send({"op": "bye"})
        self.assertEqual(self.c.close(), (0, ""))

    def test_a_reply_out_of_order_is_WIRE_and_abandons_the_run(self):
        self.c.ask({"op": "declare", "spec": json.loads(wire(vector_B()))})
        msg = self.c.ask({"op": "run", "world": 1})
        self.assertEqual(msg, {"observe": "scan", "id": 1})
        self.assertEqual(self.c.ask({"outcome": "y", "id": 99})["refused"], WIRE)
        msg = self.c.ask({"op": "run", "world": 1})
        self.assertEqual(self.c.ask({"fired": True, "id": msg["id"]})["refused"], WIRE)
        msg = self.c.ask({"op": "run", "world": 1})
        self.assertEqual(self.c.ask({"outcome": ["y"], "id": msg["id"]})["refused"], WIRE)
        fired, msg = self.c.play(1, ["y", "+"])            # and the World is as it was
        self.assertEqual(msg["result"]["acts"], ["scan", "test", "treat"])

    def test_an_outcome_the_world_cannot_emit_is_S5_not_the_wire(self):
        self.c.ask({"op": "declare", "spec": json.loads(wire(vector_B()))})
        fired, msg = self.c.play(1, ["nothing"])
        self.assertEqual((fired, msg["result"]["status"]), ([], "WORLD_FALSIFIED"))

    def test_eof_mid_run_ends_cleanly(self):
        self.c.ask({"op": "declare", "spec": json.loads(wire(vector_B()))})
        self.assertIn("observe", self.c.ask({"op": "run", "world": 1}))
        self.assertEqual(self.c.close(), (0, ""))

    def test_load_pack(self):
        okd = os.path.join(_path.CHARTER, "packs", "ok")
        if not os.path.isdir(okd):
            self.skipTest("the charter is not fetched")
        with open(os.path.join(okd, "appendix_think.py")) as f:
            text = f.read()
        self.assertEqual(self.c.ask({"op": "load_pack", "text": text, "data_dir": okd}),
                         {"ok": True, "world": 1})
        fired, msg = self.c.play(1, ["+", "+"])
        self.assertEqual(msg["result"]["status"], "TERMINAL")


if __name__ == "__main__":
    unittest.main()
