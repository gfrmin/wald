"""Check a pack: print what it declares, or why it is refused.

    python3 tools/wald_check.py PACK.py

Outside src/, so it may use sys and argparse; it holds no semantics of its own. Exit code 0 if
the pack is lawful, 1 if it is refused -- the loop every pack author works in: write, check,
repair. Data files are looked for beside the pack.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from wald.plated import Plated                         # noqa: E402
from wald.refusals import Refused                      # noqa: E402
from wald.surface import Pack                          # noqa: E402
from wald.world import declare                         # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="check a wald pack against the signed pages")
    parser.add_argument("pack", help="the pack to check")
    args = parser.parse_args()
    path = pathlib.Path(args.pack)
    try:
        # The bytes as written (SURFACE v0.2 V2.11): no newline translation, or a CR is lost
        # before the checker can refuse it.
        text = path.read_bytes().decode("utf-8")
    except OSError as e:
        print("cannot read " + str(path) + ": " + str(e))
        return 1
    except UnicodeDecodeError as e:
        print("refused: NOT_A_DECLARATION")
        print("  [V2.11] a pack is UTF-8 text: " + str(e))
        return 1
    try:
        pack = Pack(text, str(path.resolve().parent))
        spec = pack.spec()
        declared = declare(spec)
    except Refused as e:
        print("refused: " + e.name)
        print("  " + str(e))
        return 1
    plated = declared if isinstance(declared, Plated) else None
    world = plated.world if plated else declared
    census = pack.cells.census
    terminal, observational = list(world.T), list(world.O)
    print("ok")
    closed, bottom = (spec.get("closed", False), spec.get("bottom")) if plated else (world.closed, world.bottom)
    print("  world       " + str(pack.name) + ("  (closed)" if closed else "  (bottom: " + repr(bottom) + ")"))
    print("  space       " + ", ".join(str(c) + " [" + str(len(v)) + "]"
                                       for c, v in pack.space.items())
          + "  ->  " + str(len(world.omega())) + " states")
    print("  menu        " + str(len(terminal)) + " terminal: " + ", ".join(map(str, terminal)))
    print("              " + str(len(observational)) + " observational: "
          + ", ".join(str(k) + ("" if world.O[k].once else " (fresh)") for k in observational))
    print("  clock       horizon " + str(world.N) + ", depth " + str(world.d))
    if plated is not None:
        print("  learned     " + (", ".join(c for c, _ in spec["globals"]) or "no Global") + "; "
              + (repr(plated.after.name) + " after every episode" if plated.after else "no After-act")
              + "; " + str(sum(plated.counts.values())) + " records shipped, "
              + str(len(plated.falsifiers)) + " falsifying")
    print("  quantities  " + ", ".join(str(tag) + " " + str(n) for tag, n in sorted(census.items()))
          + "  (total " + str(sum(census.values())) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
