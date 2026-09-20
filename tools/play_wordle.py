"""Play every answer through the kernel and write packs/wordle/SCOREBOARD.md.

    python3 tools/play_wordle.py [--pack packs/wordle/pack.py] [--out packs/wordle/SCOREBOARD.md]

The door is the game: it returns the feedback of the guess against the answer it is holding, and
fires the claim the kernel ends with. Nothing here chooses -- `wald.episode.run` plays, at the
depth the pack declares (CHARTER E3), and this only writes down what happened.
"""
import argparse
import pathlib
import sys
import time
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from make_wordle_pack import ALL_GREEN, feedback                  # noqa: E402
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
    return result, door, solved, time.time() - started


def scoreboard(world, spec, counts, quantities, rows, seconds):
    played = sum(counts.values())
    attempts = sum(k * n for k, n in counts.items())
    failures = [r for r in rows if not r[3]]
    out = ["# Wordle — scoreboard",
           "",
           "`packs/wordle/pack.py`, played by `wald.episode.run` through a door that answers with the",
           "game's feedback. Every act is the kernel's own: the depth below is what the pack declares,",
           "and the kernel plays `decide_min(d, n)` (CHARTER E3).",
           "",
           "| | |",
           "|---|---|",
           "| words (states) | " + str(len(spec["prior"])) + " |",
           "| horizon | " + str(spec["N"]) + " (five guesses and a claim: Wordle's six attempts) |",
           "| **declared depth** | **" + str(spec["d"]) + "** |",
           "| answers played | " + str(played) + " |",
           "| solved | " + str(played - len(failures)) + " / " + str(played) + " |",
           "| mean attempts | " + ("%.3f" % (attempts / played)) + " |",
           "| worst | " + str(max(counts)) + " |",
           "| time | " + ("%.1f s for %d episodes (%.2f s each)" % (seconds, played, seconds / played)) + " |",
           "",
           "## Attempts",
           "",
           "An attempt is an act the agent played: each guess, and the claim it ends on.",
           "",
           "| attempts | answers | |",
           "|---|---|---|"]
    for k in sorted(counts):
        out.append("| " + str(k) + " | " + str(counts[k]) + " | " + "#" * counts[k] + " |")
    out += ["",
            "## Failures",
            "",
            ("None: every answer was claimed right, or guessed all-green, within the horizon."
             if not failures else
             "\n".join("- **" + r[0] + "**: " + r[2] + " (" + r[1] + ")" for r in failures)),
            "",
            "## Quantities by source",
            "",
            "`wald.surface.census`, which counts quantities, not numerals: each cell, parameter,",
            "mixture weight, price, the horizon and the depth once, however it is written.",
            "",
            "| source | quantities |",
            "|---|---|"]
    for tag in sorted(quantities):
        out.append("| " + tag + " | " + str(quantities[tag]) + " |")
    out += ["| **total** | **" + str(sum(quantities.values())) + "** |",
            "",
            "`fitted` is 0: nothing in this World is a point estimate. The prior, the prices, the",
            "horizon and every kernel row are `data` — facts of the game and of the word list. What is",
            "`elicited` is the owner's: the depth, and the utilities, including `loss`.",
            "",
            "## Every answer",
            "",
            "| answer | attempts | acts |",
            "|---|---|---|"]
    for answer, acts, status, solved, n in rows:
        out.append("| " + answer + " | " + str(n) + " | " + acts + (" |" if solved else " (**" + status + "**) |"))
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = pathlib.Path(__file__).resolve().parent.parent
    parser.add_argument("--pack", default=str(root / "packs" / "wordle" / "pack.py"))
    parser.add_argument("--out", default=str(root / "packs" / "wordle" / "SCOREBOARD.md"))
    args = parser.parse_args()
    pack = pathlib.Path(args.pack)
    text = pack.read_text(encoding="utf-8")
    spec = check(text, data_dir=str(pack.parent))
    quantities = census(text, data_dir=str(pack.parent))
    world = declare(spec)
    answers = list(spec["prior"])
    counts, rows, seconds = {}, [], 0.0
    for answer in answers:
        result, door, solved, took = play(world, answer)
        seconds += took
        n = len(result.acts)
        counts[n] = counts.get(n, 0) + 1
        rows.append((answer, " → ".join(result.acts), result.status, solved, n))
        print("%-6s %d attempts  %-16s %6.2fs  %s" % (answer, n, result.status, took,
                                                      "" if solved else "NOT SOLVED"))
    pathlib.Path(args.out).write_text(
        scoreboard(world, spec, counts, quantities, rows, seconds), encoding="utf-8")
    failures = sum(1 for r in rows if not r[3])
    print("wrote " + args.out + ": " + str(len(answers)) + " answers, mean "
          + ("%.3f" % (sum(k * n for k, n in counts.items()) / len(answers))) + " attempts, "
          + str(failures) + " failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
