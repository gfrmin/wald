"""Brief 010's measurement: a plate whose prior moves every episode, and the resident memory it
leaves behind. CHARTER v0.2 appendix A's shape -- the answer local, `ask` reporting it with the
reliability, the After-act revealing it -- with the reliability a Global on the 100 values k/200,
k = 101..200, uniform; a right answer 1, a wrong one 0, `ask` free. Every value of the grid is
better than a coin, so `ask` is worth E[rel] > 1/2 at every prior and is always taken, and every
record it writes moves P(Global | Counts). The door answers both acts at random, from a seed.

    python3 tools/plate_memory.py [--episodes 200] [--seed 1] [--at 50,100,200]

prints, at each mark, the process's peak resident memory (ru_maxrss) and the seconds an episode
took over the stretch before it. Public names only, so it measures any kernel on PYTHONPATH."""
import argparse
import os
import random
import resource
import sys
import time
from fractions import Fraction as F

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))  # after PYTHONPATH
import wald  # noqa: E402

GRID = [F(k, 200) for k in range(101, 201)]


def world(grid=GRID):
    """Appendix A's World as INTERFACE's v0.2 dict, every table sourced, on `grid`."""
    ls, gs = [("a1",), ("a2",)], [(str(r),) for r in grid]
    other = {"a1": "a2", "a2": "a1"}
    K = {(l, g): {l[0]: F(g[0]), other[l[0]]: 1 - F(g[0])} for l in ls for g in gs}
    T = {"say a1": {(l, g): F(int(l == ("a1",))) for l in ls for g in gs},
         "say a2": {(l, g): F(int(l == ("a2",))) for l in ls for g in gs},
         "abstain": {(l, g): F(0) for l in ls for g in gs}}
    W = {"locals": [("answer", ["a1", "a2"])], "globals": [("rel", [g[0] for g in gs])],
         "prior_global": {g: F(1, len(gs)) for g in gs},
         "prior_local": {g: {l: F(1, 2) for l in ls} for g in gs}, "T": T,
         "O": {"ask": {"K": K, "price": F(0), "once": True}}, "N": 1, "d": 1,
         "after": {"K": {t: {(l, g): {l[0]: F(1)} for l in ls for g in gs} for t in T}, "price": F(0)}}
    sources = {"prior": "elicited", "utility": "elicited", "price": "elicited", "horizon": "elicited",
               "depth": "elicited", "kernels": {"ask": ["elicited"]}}
    return dict(W, closed=True, table_sources=sources)


class Coin(wald.Door):
    """Answers every act, the After-act included, a1 or a2 at random."""

    def __init__(self, seed):
        self.rng = random.Random(seed)

    def outcome(self, act):
        return self.rng.choice(["a1", "a2"])

    def fire(self, act):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--at", default="50,100,200")
    a = ap.parse_args()
    marks = set(int(m) for m in a.at.split(","))
    plate, door = wald.plate(wald.declare(world())), Coin(a.seed)
    print("kernel:", os.path.dirname(wald.__file__), "| Global values:", len(GRID))
    start = last = time.perf_counter()
    since = 0
    for k in range(1, a.episodes + 1):
        r = plate.run(door)
        assert r.status != "WORLD_FALSIFIED" and r.acts[0] == "ask", r
        if k in marks:
            now = time.perf_counter()
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            print(f"episode {k:4d}: peak RSS {peak:8.1f} MB, {(now - last) / (k - since):.4f} s an episode"
                  f" since episode {since}")
            last, since = now, k
    print(f"total {time.perf_counter() - start:.1f} s, {(time.perf_counter() - start) / a.episodes:.4f} s an episode")


if __name__ == "__main__":
    main()
