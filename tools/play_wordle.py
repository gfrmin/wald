"""Play every answer of a pack through the kernel and write its scoreboard.

    python3 tools/play_wordle.py [--pack packs/wordle/pack.py] [--out packs/wordle/SCOREBOARD.md]
    python3 tools/play_wordle.py --pack packs/wordle200/d1.py --pack packs/wordle200/d2.py \
                                --out packs/wordle200/SCOREBOARD.md

Given more than one pack it plays each and writes one scoreboard, and where the packs differ only
in their declared depth it prints the measured price of the floor: the mean attempts at the
shallower depth minus the mean at the deeper one (CHARTER E3).

The door is the game: it returns the feedback of the guess against the answer it is holding, and
fires the claim the kernel ends with. Nothing here chooses -- `wald.episode.run` plays, at the
depth the pack declares, and this only writes down what happened.
"""
import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from make_wordle_pack import feedback                             # noqa: E402
from wald.episode import Door, run                                # noqa: E402
from wald.surface import census, check                            # noqa: E402
from wald.world import declare                                    # noqa: E402


class Game(Door):
    """Wordle itself: it knows the answer and says only what the game says."""

    def __init__(self, answer):
        self.answer = answer
        self.fired = None

    def outcome(self, act):
        return feedback(act, self.answer)

    def fire(self, act):
        self.fired = act


def play(world, answer):
    door = Game(answer)
    started = time.time()
    result = run(world, door)
    solved = (result.status == "ENDED" and result.acts[-1] == answer) or \
             (result.status == "TERMINAL" and door.fired == "claim " + answer)
    return result, solved, time.time() - started


class Run:
    """One pack, played out."""

    def __init__(self, path, quiet=False):
        self.path = path
        text = path.read_text(encoding="utf-8")
        self.spec = check(text, data_dir=str(path.parent))
        self.quantities = census(text, data_dir=str(path.parent))
        world = declare(self.spec)
        self.counts, self.rows, self.seconds, self.first = {}, [], 0.0, 0.0
        for answer in self.spec["prior"]:
            result, solved, took = play(world, answer)
            self.seconds += took
            self.first = self.first or took
            n = len(result.acts)
            self.counts[n] = self.counts.get(n, 0) + 1
            self.rows.append((answer, " → ".join(result.acts), result.status, solved, n))
            if not quiet:
                print("%-6s %d attempts  %-16s %6.2fs  %s" % (answer, n, result.status, took,
                                                              "" if solved else "NOT SOLVED"))

    @property
    def played(self):
        return len(self.rows)

    @property
    def mean(self):
        return sum(k * n for k, n in self.counts.items()) / self.played

    @property
    def failures(self):
        return [r for r in self.rows if not r[3]]


def _table(head, lines):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + lines


def scoreboard(runs, root):
    """One file: a column per pack in the summary, then a section each."""
    names = [str(r.path.relative_to(root)) for r in runs]
    one = runs[0]
    out = ["# Wordle — scoreboard",
           "",
           "`" + "`, `".join(names) + "`, played by `wald.episode.run` through a door that answers",
           "with the game's feedback. Every act is the kernel's own: the depth below is what the pack",
           "declares, and the kernel plays `decide_min(d, n)` (CHARTER E3).",
           ""]
    out += _table([""] + ["**depth " + str(r.spec["d"]) + "**" for r in runs], [
        "| words (states) | " + " | ".join(str(len(r.spec["prior"])) for r in runs) + " |",
        "| horizon | " + " | ".join(str(r.spec["N"]) for r in runs) + " |",
        "| **declared depth** | " + " | ".join("**" + str(r.spec["d"]) + "**" for r in runs) + " |",
        "| answers played | " + " | ".join(str(r.played) for r in runs) + " |",
        "| solved | " + " | ".join(str(r.played - len(r.failures)) + " / " + str(r.played) for r in runs) + " |",
        "| **mean attempts** | " + " | ".join("**%.3f**" % r.mean for r in runs) + " |",
        "| worst | " + " | ".join(str(max(r.counts)) for r in runs) + " |",
        "| first episode | " + " | ".join("%.1f s" % r.first for r in runs) + " |",
        "| all answers | " + " | ".join("%.1f s" % r.seconds for r in runs) + " |",
    ])
    if len(runs) > 1:
        shallow, deep = runs[0], runs[-1]
        a, b = {r[0]: r for r in shallow.rows}, {r[0]: r for r in deep.rows}
        differ = [w for w in a if a[w][1] != b[w][1]]
        better = [w for w in differ if b[w][4] < a[w][4]]
        worse = [w for w in differ if b[w][4] > a[w][4]]
        out += ["",
                "**The price of the floor, measured.** Mean attempts at depth " + str(shallow.spec["d"])
                + " minus mean attempts at depth " + str(deep.spec["d"]) + ", over all "
                + str(one.played) + " answers, is **" + ("%+.3f" % (shallow.mean - deep.mean)).replace("+0.000", "0.000")
                + "**. Nothing here is tuned to make it larger: the two packs differ in one line.",
                "",
                "The two depths are not playing the same game, though. They play " + str(len(differ))
                + " of the " + str(one.played) + " answers differently"
                + (": " + ", ".join("`" + w + "`" for w in differ) if differ else "") + ". Of those, the",
                "deeper agent needs fewer attempts on " + str(len(better)) + " and more on "
                + str(len(worse)) + "."]
    out += ["",
            "## Quantities by source",
            "",
            "`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,",
            "mixture weight, price, the horizon and the depth once, however it is written.",
            ""]
    tags = sorted(one.quantities)
    out += _table(["source"] + ["depth " + str(r.spec["d"]) for r in runs],
                  ["| " + tag + " | " + " | ".join(str(r.quantities[tag]) for r in runs) + " |"
                   for tag in tags]
                  + ["| **total** | " + " | ".join("**" + str(sum(r.quantities.values())) + "**"
                                                   for r in runs) + " |"])
    out += ["",
            "`fitted` is 0: nothing in this World is a point estimate. The prior, the prices, the",
            "horizon and every kernel row are `data` — facts of the game and of the word list. What is",
            "`elicited` is the owner's: the depth, and the utilities, including `loss`."]
    for r in runs:
        out += ["",
                "## Depth " + str(r.spec["d"]) + " — `" + str(r.path.relative_to(root)) + "`",
                "",
                "An attempt is an act the agent played: each guess, and the claim it ends on.",
                ""]
        width = max(r.counts.values())
        out += _table(["attempts", "answers", ""],
                      ["| " + str(k) + " | " + str(r.counts[k]) + " | "
                       + "#" * max(1, round(r.counts[k] * 40 / width)) + " |" for k in sorted(r.counts)])
        out += ["",
                ("Failures: none — every answer was claimed right, or guessed all-green, within the horizon."
                 if not r.failures else
                 "Failures:\n" + "\n".join("- **" + f[0] + "**: " + f[1] + " (" + f[2] + ")" for f in r.failures)),
                "",
                "<details><summary>every answer</summary>",
                ""]
        out += _table(["answer", "attempts", "acts"],
                      ["| " + a + " | " + str(n) + " | " + acts + (" |" if solved else " (**" + status + "**) |")
                       for a, acts, status, solved, n in r.rows])
        out += ["", "</details>"]
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = pathlib.Path(__file__).resolve().parent.parent
    parser.add_argument("--pack", action="append", default=None)
    parser.add_argument("--out", default=str(root / "packs" / "wordle" / "SCOREBOARD.md"))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    packs = [pathlib.Path(p).resolve() for p in (args.pack or [str(root / "packs" / "wordle" / "pack.py")])]
    runs = [Run(p, args.quiet) for p in packs]
    pathlib.Path(args.out).write_text(scoreboard(runs, root), encoding="utf-8")
    for r in runs:
        print("depth %d: %d answers, mean %.3f attempts, %d failures, %.1f s"
              % (r.spec["d"], r.played, r.mean, len(r.failures), r.seconds))
    print("wrote " + args.out)
    return 1 if any(r.failures for r in runs) else 0


if __name__ == "__main__":
    sys.exit(main())
