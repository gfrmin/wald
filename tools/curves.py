"""The five E3 curves of a Wordle pack that declares a think act, along a grid of rates.

    python3 tools/curves.py --pack packs/wordle200/adaptive.py
    python3 tools/curves.py --pack packs/twins/adaptive.py --json packs/twins/curves.json

CHARTER E3 asks what the floor costs. With a think act there are five answers to compare, and
this computes all five under the declared model -- exactly, in rationals, over every answer:

    fixed d = 1            the shallow agent, thinking never
    fixed d = 2 paying c   the deep agent, charged r*ops(s) at every step with n > 1
    best fixed depth       the larger of those two: hindsight, not a policy
    adaptive               `decide+`: the kernel decides at each step whether to buy the look
    omniscient             the meta-policy that buys the look exactly where it raises the value
                           of its own continuation net of c -- a DP over (candidates, n)

**Every act here is the kernel's.** The tool asks `wald.decide.decide` for the act at a depth and
`wald.decide.step` for the bucket and the charge, and then does arithmetic on what they said: the
expectation over answers, the feedback classes, and the backward induction of the omniscient
policy. It stands where `wald.kit_adapter` stands -- an instrument outside `src/`, measuring the
kernel through its own verbs -- and it chooses nothing, holds no comparison on a display value,
and never puts a number into a World.

The candidate set is the whole state of a Wordle belief: the prior is uniform and every feedback
row is a point mass, so conditioning keeps the belief uniform over the surviving words. The tool
still conditions through the kernel, one Obs per class, rather than asserting that.
"""
import argparse
import json
import pathlib
import sys
import time
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from make_wordle_pack import feedback                             # noqa: E402
from wald.belief import condition, prior                          # noqa: E402
from wald.decide import decide, step                              # noqa: E402
from wald.episode import Door                                     # noqa: E402
from wald.surface import check                                    # noqa: E402
from wald.world import declare                                    # noqa: E402

GRID = [Fraction(0), Fraction(1, 10**8), Fraction(3, 10**8), Fraction(1, 10**7),
        Fraction(3, 10**7), Fraction(1, 10**6)]
ALL_GREEN = "ggggg"
CURVES = ("fixed d=1", "always d=2", "best fixed", "adaptive", "omniscient")


class Told(Door):
    """A door that says what it is told. It exists to mint one Obs: `condition` takes a token and
    only a door makes one, and a tool does not get to make beliefs another way."""

    def __init__(self):
        self.said = None

    def outcome(self, act):
        return self.said

    def fire(self, act):
        pass


class Node:
    """A node of the game tree: the candidates still alive, the belief over them, and which
    guesses are spent. `n` is not here -- it is the argument, because the same node is reached
    with different clocks."""

    __slots__ = ("words", "belief", "used")

    def __init__(self, words, belief, used):
        self.words = words
        self.belief = belief
        self.used = used

    def key(self):
        return (self.words, self.used)


class Tree:
    """One pack, and the acts the kernel plays in it."""

    def __init__(self, path):
        text = path.read_text(encoding="utf-8")
        self.spec = check(text, data_dir=str(path.parent))
        self.world = declare(self.spec)
        self.words = tuple(self.spec["prior"])
        self.loss = min(self.spec["T"]["claim " + self.words[0]].values())
        self.N = self.spec["N"]
        self.ops = self.spec["ops"]
        self.fraction = self.spec["fraction"]
        self.declared_rate = self.spec["rate"]
        self.door = Told()
        self.acts, self.children = {}, {}

    # ---- the kernel, asked
    def root(self):
        return Node(self.words, prior(self.world), frozenset())

    def act(self, node, depth, n):
        """decide_min(depth, n) at this node, remembered: the same question is asked once per
        curve and six times over the grid, and the answer does not depend on r."""
        key = (node.key(), min(depth, n))
        if key not in self.acts:
            self.acts[key] = decide(node.belief, self.world, min(depth, n), node.used)
        return self.acts[key]

    def thought(self, node, n, rate):
        """decide+ at this node under a rate: the act, the bucket, and what it charged. The
        World declares one rate, so a grid point that is not it is asked of a World declared
        with that rate instead -- the kernel is asked, never told."""
        return step(node.belief, self.at(rate), n, node.used)

    def at(self, rate):
        """The same pack with one number changed. `declare` is what accepts it, so the World the
        kernel decides in is a declared World and not a dict I assembled."""
        if not hasattr(self, "_rated"):
            self._rated = {}
        if rate not in self._rated:
            self._rated[rate] = declare(dict(self.spec, rate=rate))
        return self._rated[rate]

    # ---- the game, partitioned
    def split(self, node, guess):
        """The feedback classes of a guess, each with the belief the kernel conditions to.
        All-green is the ending outcome and has no child."""
        if (node.key(), guess) in self.children:
            return self.children[(node.key(), guess)]
        classes = {}
        for answer in node.words:
            classes.setdefault(feedback(guess, answer), []).append(answer)
        out = []
        for mark, alive in classes.items():
            if mark == ALL_GREEN:
                out.append((mark, len(alive), None))
                continue
            self.door.said = mark
            child = Node(tuple(alive), condition(node.belief, self.world, self.door.observe(guess)),
                         node.used | {guess})
            out.append((mark, len(alive), child))
        self.children[(node.key(), guess)] = out
        return out

    # ---- the value of a policy, exactly
    def value(self, policy, node=None, n=None, memo=None):
        """The expected utility of one episode from this node, conditional on being here: the
        answer uniform over the candidates, the game deterministic, no approximation anywhere."""
        node = self.root() if node is None else node
        n = self.N if n is None else n
        memo = {} if memo is None else memo
        key = (node.key(), n)
        if key in memo:
            return memo[key]
        m = len(node.words)
        act, paid = policy(node, n)
        if act in self.spec["T"]:
            claimed = act[len("claim "):]
            right = Fraction(1, m) if claimed in node.words else Fraction(0)
            total = right * -1 + (1 - right) * self.loss - paid
        else:
            total = Fraction(-1) - paid              # the price of a guess
            for mark, size, child in self.split(node, act):
                if child is not None:
                    total += Fraction(size, m) * self.value(policy, child, n - 1, memo)
        memo[key] = total
        return total

    # ---- the five policies
    def fixed(self, depth):
        return lambda node, n: (self.act(node, depth, n), Fraction(0))

    def always_deep(self, rate):
        def policy(node, n):
            if n <= 1:
                return self.act(node, 1, n), Fraction(0)
            return self.act(node, 2, n), rate * self.ops[len(node.words)]
        return policy

    def adaptive(self, rate):
        def policy(node, n):
            act, how, paid = self.thought(node, n, rate)
            return act, paid
        return policy

    def omniscient(self, rate, node=None, n=None, memo=None):
        """The best a meta-policy could do knowing everything the model knows: at each node take
        whichever continuation is worth more net of c, ties to the shallow one. It is not a
        policy any agent could follow -- it is the ceiling the adaptive agent is measured against.
        """
        node = self.root() if node is None else node
        n = self.N if n is None else n
        memo = {} if memo is None else memo
        key = (node.key(), n)
        if key in memo:
            return memo[key]
        m = len(node.words)

        def after(act, paid):
            if act in self.spec["T"]:
                claimed = act[len("claim "):]
                right = Fraction(1, m) if claimed in node.words else Fraction(0)
                return right * -1 + (1 - right) * self.loss - paid
            total = Fraction(-1) - paid
            for mark, size, child in self.split(node, act):
                if child is not None:
                    total += Fraction(size, m) * self.omniscient(rate, child, n - 1, memo)
            return total

        best = after(self.act(node, 1, n), Fraction(0))
        if n > 1 and m > 1:
            deep = after(self.act(node, 2, n), rate * self.ops[m])
            if deep > best:
                best = deep
        memo[key] = best
        return best

    def curves(self, rate):
        one = self.value(self.fixed(1))
        two = self.value(self.always_deep(rate))
        return {"fixed d=1": one, "always d=2": two, "best fixed": max(one, two),
                "adaptive": self.value(self.adaptive(rate)),
                "omniscient": self.omniscient(rate)}


def sweep(path, grid=GRID):
    tree = Tree(path)
    table = {}
    for rate in grid:
        started = time.time()
        table[str(rate)] = {k: str(v) for k, v in tree.curves(rate).items()}
        print("  r = %-12s %s   (%.1f s)"
              % (str(rate), "  ".join("%s %9.4f" % (k, float(Fraction(v)))
                                      for k, v in table[str(rate)].items()), time.time() - started))
    return tree, table


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = pathlib.Path(__file__).resolve().parent.parent
    parser.add_argument("--pack", default=str(root / "packs" / "wordle200" / "adaptive.py"))
    parser.add_argument("--json", default=None)
    args = parser.parse_args()
    path = pathlib.Path(args.pack).resolve()
    print(str(path.relative_to(root)) + ": the five E3 curves, exact, over the declared model")
    tree, table = sweep(path)
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(
            {"pack": str(path.relative_to(root)), "rate": str(tree.declared_rate),
             "fraction": str(tree.fraction), "curves": table}, indent=1), encoding="utf-8")
        print("wrote " + args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
