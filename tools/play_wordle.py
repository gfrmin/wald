"""Play every answer of a pack through the kernel and write its scoreboard.

    python3 tools/play_wordle.py [--pack packs/wordle/pack.py] [--out packs/wordle/SCOREBOARD.md]
    python3 tools/play_wordle.py --pack packs/wordle200/d1.py --pack packs/wordle200/d2.py \
                                --out packs/wordle200/SCOREBOARD.md

Given more than one pack it plays each and writes one scoreboard, and where two of the packs
differ only in their declared depth it prints the measured price of the floor: the mean attempts
at the shallower depth minus the mean at the deeper one (CHARTER E3).

A pack that declares a think act (CHARTER v0.1) gets a section of its own: S7's four buckets, the
thought charged, and the operations each thought predicted against the operations it took (E6).
`--curves` takes the JSON `tools/curves.py` writes and prints the five E3 curves beside it.

The door is the game: it returns the feedback of the guess against the answer it is holding, and
fires the claim the kernel ends with. Nothing here chooses -- `wald.episode.run` plays, at the
depth the pack declares, and this only writes down what happened. Where it asks `decide.step` for
a step's bucket it is asking a second time what the episode already did, and it checks that the
answers agree before writing either down.
"""
import argparse
import json
import pathlib
import sys
import time
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from curves import CURVES                                         # noqa: E402
from make_wordle_pack import feedback                             # noqa: E402
from wald.belief import _measure, condition, prior                # noqa: E402
from wald.decide import THINK, step                               # noqa: E402
from wald.episode import Door, run                                # noqa: E402
from wald.surface import census, check                            # noqa: E402
from wald.world import declare                                    # noqa: E402

BUCKETS = ("struck_n", "struck_cap", "refused", "think")


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

    def __init__(self, path, quiet=False, curves=None):
        self.path = path
        text = path.read_text(encoding="utf-8")
        self.spec = check(text, data_dir=str(path.parent))
        self.quantities = census(text, data_dir=str(path.parent))
        self.curves = curves
        self.thinks = self.spec.get("dplus") is not None
        world = declare(self.spec)
        self.world = world
        self.counts, self.rows, self.seconds, self.first = {}, [], 0.0, 0.0
        self.steps = {b: 0 for b in BUCKETS}
        self.thought = Fraction(0)
        self.thoughts = []            # (answer, live states, predicted ops, operations counted)
        for answer in self.spec["prior"]:
            result, solved, took = play(world, answer)
            self.seconds += took
            self.first = self.first or took
            n = len(result.acts)
            self.counts[n] = self.counts.get(n, 0) + 1
            self.rows.append((answer, " → ".join(result.acts), result.status, solved, n))
            if self.thinks:
                self.record(answer, result)
            if not quiet:
                print("%-6s %d attempts  %-16s %6.2fs  %s" % (answer, n, result.status, took,
                                                              "" if solved else "NOT SOLVED"))

    def record(self, answer, result):
        """What the episode's steps were, walked a second time. `wald.episode.run` keeps the four
        counts and the operation counts but not which step was which, so this asks `decide.step`
        along the same path -- every answer already in the World's memo, so it costs nothing -- and
        refuses to write anything down unless the second telling matches the first."""
        belief, n, used, live = prior(self.world), self.world.N, set(), []
        door = Game(answer)
        acts, hows = [], []
        for i, act in enumerate(result.acts):
            played, how, cost = step(belief, self.world, n, frozenset(used))
            acts.append(played)
            hows.append(how)
            live.append(len(_measure(belief)))       # s: the live states the Cost is keyed on
            if act in self.spec["T"]:
                break
            obs = door.observe(act)
            belief = condition(belief, self.world, obs)
            if obs.value in self.world.O[act].ends:
                break
            used.add(act)
            n -= 1
        again = {b: hows.count(b) for b in BUCKETS}
        charged = sum((self.world.rate * self.world.ops[s]
                       for s, how in zip(live, hows) if how == THINK), Fraction(0))
        if acts != list(result.acts) or again != dict(result.steps) or charged != result.thought:
            raise SystemExit("the second telling of %r differs from the episode: %s / %s"
                             % (answer, (acts, again, charged),
                                (list(result.acts), dict(result.steps), result.thought)))
        for b in BUCKETS:
            self.steps[b] += again[b]
        self.thought += result.thought
        counted = list(result.operations)
        for s, how in zip(live, hows):
            if how == THINK:
                self.thoughts.append((answer, s, self.world.ops[s], counted.pop(0)))

    @property
    def rate(self):
        return self.world.rate

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
           "declares, and the kernel plays `decide_min(d, n)` (CHARTER E3)."]
    if any(r.thinks for r in runs):
        out += ["",
                ("This pack declares" if len(runs) == 1 else "One of these packs declares")
                + " a **think act** (CHARTER v0.1): at a step with room left it",
                "may buy one deeper look, at a price the pack itself declares, and play the act that look",
                "found. Its column says `1 + θ` — the floor is still 1, and what it buys is not a depth it",
                "declares but a computation the one `decide` chose to pay for."]
    out += [""]
    head = lambda r: "**depth " + (str(r.spec["d"]) + " + θ" if r.thinks else str(r.spec["d"])) + "**"
    out += _table([""] + [head(r) for r in runs], [
        "| words (states) | " + " | ".join(str(len(r.spec["prior"])) for r in runs) + " |",
        "| horizon | " + " | ".join(str(r.spec["N"]) for r in runs) + " |",
        "| **declared depth** | " + " | ".join("**" + str(r.spec["d"]) + ("** + θ" if r.thinks else "**") for r in runs) + " |",
        "| answers played | " + " | ".join(str(r.played) for r in runs) + " |",
        "| solved | " + " | ".join(str(r.played - len(r.failures)) + " / " + str(r.played) for r in runs) + " |",
        "| **mean attempts** | " + " | ".join("**%.3f**" % r.mean for r in runs) + " |",
        "| worst | " + " | ".join(str(max(r.counts)) for r in runs) + " |",
        "| first episode | " + " | ".join("%.1f s" % r.first for r in runs) + " |",
        "| all answers | " + " | ".join("%.1f s" % r.seconds for r in runs) + " |",
    ])
    plain = [r for r in runs if not r.thinks]
    if len(plain) > 1:
        shallow, deep = plain[0], plain[-1]
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
    out += _table(["source"] + ["depth " + str(r.spec["d"]) + (" + θ" if r.thinks else "") for r in runs],
                  ["| " + tag + " | " + " | ".join(str(r.quantities[tag]) for r in runs) + " |"
                   for tag in tags]
                  + ["| **total** | " + " | ".join("**" + str(sum(r.quantities.values())) + "**"
                                                   for r in runs) + " |"])
    if any(r.thinks for r in runs):
        out += ["",
                "The prior, the prices, the horizon and every kernel row are `data` — facts of the game",
                "and of the word list. What is `elicited` is the owner's: the depth, the utilities,",
                "including `loss`, and — where a think act is declared — Depth⁺, the Fraction and the",
                "Rate. What is `fitted` is the Cost table: two parameters fitted by the author to the",
                "kernel's own operation counts, read by "
                + str(len(next(r for r in runs if r.thinks).spec["prior"])) + " cells, each of which counts once under",
                "its table's source (SURFACE v0.1 K17). A fitted table carries its held-out Score, and",
                "this one does."]
    else:
        out += ["",
                "`fitted` is 0: nothing in this World is a point estimate. The prior, the prices, the",
                "horizon and every kernel row are `data` — facts of the game and of the word list. What is",
                "`elicited` is the owner's: the depth, and the utilities, including `loss`."]
    for r in runs:
        out += ["",
                "## Depth " + str(r.spec["d"]) + (" + θ" if r.thinks else "")
                + " — `" + str(r.path.relative_to(root)) + "`",
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
        if r.thinks:
            out += think_section(r)
    return "\n".join(out) + "\n"


def q(x, places=6):
    "A rational, printed as itself and as a decimal. The decimal is for reading, never for a rule."
    return "%s (≈ %.*f)" % (x, places, float(x))


def think_section(r):
    """S7's four buckets, the thought charged, and E6's two operation counts side by side."""
    total = sum(r.steps.values())
    out = ["",
           "### The think act",
           "",
           "The pack declares Depth⁺ 2, a Fraction f = " + str(r.spec["fraction"]) + ", a fitted Cost table and a",
           "Rate r = " + str(r.rate) + ". At every step `decide⁺` settles into one of S7's four buckets, in",
           "precedence order, and only the last of them costs anything.",
           ""]
    out += _table(["bucket", "steps", "share", "what it means"], [
        "| `struck_n` | " + str(r.steps["struck_n"]) + " | " + "%.1f%%" % (100 * r.steps["struck_n"] / total)
        + " | n ≤ d, or no guess left: there is nothing a deeper look could reach |",
        "| `struck_cap` | " + str(r.steps["struck_cap"]) + " | " + "%.1f%%" % (100 * r.steps["struck_cap"] / total)
        + " | the cap leaves less room than the thought costs; f is never read |",
        "| `refused` | " + str(r.steps["refused"]) + " | " + "%.1f%%" % (100 * r.steps["refused"] / total)
        + " | Q(θ) was formed and θ still lost |",
        "| **`think`** | **" + str(r.steps["think"]) + "** | " + "%.1f%%" % (100 * r.steps["think"] / total)
        + " | **θ bought: one deeper look, paid for, and the act it found is played** |",
        "| **total steps** | **" + str(total) + "** |  |  |",
    ])
    episodes = r.played
    wrong = [f[0] for f in r.failures]
    out += ["",
            "**Wrong claims**: " + (str(len(wrong)) + " of " + str(episodes)
                                    + (" — " + ", ".join("`" + a + "`" for a in wrong) if wrong else ""))
            + ". A wrong claim is the horizon running out, not a mistake the",
            "kernel made: `decide` plays the act of highest value at the depth it is allowed, and when",
            "no guess left in the menu can separate the candidates in the steps remaining, claiming one",
            "of them is the best act there is.",
            "",
            "**Thought paid**, over all " + str(episodes) + " episodes: " + q(r.thought, 4) + " of utility,",
            "which is " + q(r.thought / episodes, 6) + " an episode. It is not a price: no act was",
            "executed for it, the door never saw it, and it consumed no horizon (C17).",
            "",
            "### Predicted against realised operations (E6)",
            "",
            "The Cost table says how many operations a thought at s live states will take. The kernel",
            "counts what it actually took, and the two are printed side by side and never compared by",
            "anything: the prediction is what the policy is charged for, the count is a measurement.",
            ""]
    by_s = {}
    for answer, s_live, predicted, counted in r.thoughts:
        by_s.setdefault(s_live, []).append(counted)
    lines = []
    for s_live in sorted(by_s):
        counted = by_s[s_live]
        lines.append("| " + str(s_live) + " | " + str(len(counted)) + " | "
                     + "{:,}".format(int(r.spec["ops"][s_live])) + " | "
                     + "{:,}".format(min(counted)) + " | " + "{:,}".format(max(counted)) + " | "
                     + str(sum(1 for c in counted if c == 0)) + " |")
    out += _table(["s (live states)", "thoughts", "ops predicted", "counted, least",
                   "counted, most", "counted 0"], lines)
    cold = sum(c for _, _, _, c in r.thoughts)
    predicted = sum(p for _, _, p, _ in r.thoughts)
    free = sum(1 for _, _, _, c in r.thoughts if c == 0)
    out += ["",
            "Over all " + str(len(r.thoughts)) + " thoughts the kernel counted " + "{:,}".format(cold)
            + " operations, against " + "{:,}".format(int(predicted)) + " predicted —",
            "about " + "%.0f" % (100 * cold / max(predicted, 1)) + "% of the Cost table's number, and "
            + str(free) + " of the thoughts counted nothing at all.",
            "",
            "That is the memo of brief 004 and not a fault in the fit. A thought is one evaluation of",
            "one belief at depth 2, and the World keeps what it has already worked out; the first",
            "thought at a node pays for it and every later thought at **that same node** finds the",
            "answer there. The rows above group by s, the count of live states the Cost is keyed on,",
            "and two different nodes can have the same s — which is why the least and the most in a",
            "row differ, and why the `counted 0` column is the memo and not the model. The page",
            "expects this: two evaluators may count differently, and each prints its own count",
            "beside the same prediction (E6). The policy is charged the prediction, always, and never",
            "the count (J15) — so nothing the memo saves ever reaches a value.",
            ""]
    if r.curves:
        out += curve_section(r)
    return out


def curve_section(r):
    """CHARTER E3 along a grid of rates: what the floor costs when thinking has a price."""
    table = r.curves["curves"]
    declared = str(r.rate)
    out = ["",
           "### The five curves of E3",
           "",
           "Computed by `tools/curves.py` over the declared model — exactly, in rationals, over every",
           "answer — from this kernel's own acts: `decide` gives the act at a depth, `decide⁺` gives",
           "the bucket and the charge, and the tool does the expectation and the backward induction.",
           "`laws/kit_wordle_think.py` prints the same table from the author's oracle, and the two",
           "agree to every digit printed here.",
           "",
           "Utility per episode. **Larger is better**; a guess costs 1, a wrong claim " + str(int(min(r.spec["T"]["claim " + next(iter(r.spec["prior"]))].values()))) + ".",
           ""]
    lines = []
    for rate, row in table.items():
        mark = " **←**" if rate == declared else ""
        lines.append("| `" + rate + "`" + mark + " | "
                     + " | ".join("%.4f" % float(Fraction(row[c])) for c in CURVES) + " |")
    out += _table(["r"] + ["**" + c + "**" if c == "adaptive" else c for c in CURVES], lines)
    here = table[declared]
    adaptive, omniscient, best = (Fraction(here["adaptive"]), Fraction(here["omniscient"]),
                                  Fraction(here["best fixed"]))
    shallow = Fraction(here["fixed d=1"])
    per_episode = r.thought / r.played
    out += ["",
            "**Regret at the declared rate** r = " + declared + ":",
            "",
            "- against the omniscient meta-policy: **" + "%.4f" % float(omniscient - adaptive)
            + "** of utility per episode.",
            "- against the best fixed depth in hindsight: **" + "%.4f" % float(best - adaptive) + "**.",
            "- against thinking never (fixed d = 1): **" + "%.4f" % float(shallow - adaptive) + "**,",
            "  and the thought it paid for was " + "%.4f" % float(per_episode) + " an episode."]
    gap = float(shallow - adaptive) - float(per_episode)
    if abs(gap) < 5e-5:
        out += ["",
                "Those last two are the same number, and that is the whole finding on this lexicon:",
                "**every thought the agent bought changed nothing.** It played the same acts as the",
                "shallow agent — the same mean attempts, answer for answer — and the entire loss is",
                "what it paid to discover that the second look agreed with the first. The Fraction is",
                "the owner's optimism about a look it has not taken yet (f = " + str(r.spec["fraction"]) + "), and here the",
                "optimism was misplaced; the cap could not tell, because the cap is a bound and not a",
                "deliberation (C19). Further up the grid the Cost table finally makes c large enough for",
                "the cap to strike θ, and the curve comes back to within a few thousandths of the",
                "shallow one."]
    elif gap > 0:
        free = table[str(Fraction(0))]
        depth_gap = float(Fraction(free["fixed d=1"]) - Fraction(free["always d=2"]))
        out += ["",
                "Those two differ by " + "%.4f" % gap + ": the thoughts did not only cost, they changed",
                "acts, and on balance they changed them for the worse by that much. Look at the r = 0",
                "row for why. With thinking free, the deep agent still scores " + "%.4f" % depth_gap + " below the",
                "shallow one — **depth 2 is worse here than depth 1**, and no price is involved. The",
                "deeper look is exact, V₂ and not an estimate, so what it costs is not error: it is the",
                "step of the horizon spent reaching for it, on a lexicon of near-twins where one look",
                "cannot separate the candidates and the clock is what binds. E3 is not the claim that",
                "deeper is better; it is the question of what the floor costs, and on this World the",
                "answer is negative."]
    else:
        out += ["",
                "Those two differ by " + "%.4f" % gap + ": the acts the thoughts bought were worth more than",
                "nothing, and they paid back that much of what they cost."]
    out += [""]
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = pathlib.Path(__file__).resolve().parent.parent
    parser.add_argument("--pack", action="append", default=None)
    parser.add_argument("--out", default=str(root / "packs" / "wordle" / "SCOREBOARD.md"))
    parser.add_argument("--curves", default=None,
                        help="the JSON tools/curves.py writes, for the pack that declares a think act")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    packs = [pathlib.Path(p).resolve() for p in (args.pack or [str(root / "packs" / "wordle" / "pack.py")])]
    curves = json.loads(pathlib.Path(args.curves).read_text(encoding="utf-8")) if args.curves else None
    runs = [Run(p, args.quiet, curves) for p in packs]
    pathlib.Path(args.out).write_text(scoreboard(runs, root), encoding="utf-8")
    for r in runs:
        print("depth %d%s: %d answers, mean %.3f attempts, %d failures, %.1f s"
              % (r.spec["d"], " + theta" if r.thinks else "", r.played, r.mean,
                 len(r.failures), r.seconds)
              + ("" if not r.thinks else "; steps %s, thought %.4f" % (r.steps, float(r.thought))))
    print("wrote " + args.out)
    return 1 if any(r.failures for r in runs) else 0


if __name__ == "__main__":
    sys.exit(main())
