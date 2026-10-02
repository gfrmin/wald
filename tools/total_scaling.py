"""Brief 011's measurement: `declare` and the share of it spent in `_total`, on v0 Worlds whose
states are tuples, as a plated World's (l, g) pairs are -- 3 terminal acts, 4 observational acts
with 2 ending outcomes each, every table over all of Omega.

    python3 tools/total_scaling.py SRC N [N ...]

times the kernel under SRC (a `src` directory, so a checkout of master can be set beside this one)
at each |Omega| = N."""
import sys
import time
from fractions import Fraction as F
sys.path.insert(0, sys.argv[1])
import wald.world as W

calls = {"t": 0.0}
orig = W._total
def timed(*a):
    t = time.perf_counter(); orig(*a); calls["t"] += time.perf_counter() - t
W._total = timed

def spec(n):
    states = [(("l%d" % (i % 24),), ("g%d" % (i // 24),)) for i in range(n)]
    p = F(1, n)
    prior = {s: p for s in states}
    T = {"t%d" % k: {s: F(k) for s in states} for k in range(3)}
    O = {}
    for k in range(4):
        K = {s: {"a": F(1, 2), "b": F(1, 2)} for s in states}
        O["o%d" % k] = {"K": K, "price": F(0), "once": True,
                        "ends": {"a": {s: F(1) for s in states}, "b": {s: F(0) for s in states}}}
    src = {"prior": "data", "utility": "elicited", "price": "elicited", "horizon": "elicited", "depth": "elicited"}
    return {"prior": prior, "T": T, "O": O, "N": 1, "d": 1, "closed": True,
            "table_sources": dict(src, kernels={k: ["data"] for k in O})}

for n in map(int, sys.argv[2:]):
    s = spec(n); calls["t"] = 0.0
    t = time.perf_counter(); W.declare(s); total = time.perf_counter() - t
    print("|Ω| = %6d  declare %8.3f s  _total %8.3f s  (%.0f%%)" % (n, total, calls["t"], 100 * calls["t"] / total))
