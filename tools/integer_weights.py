"""Brief 013's measurement: wald-charter's measurements/2026-10-01-counts-likelihood, the episode
at T = 0, 300 and 600 records on the arena's omniscience-p1-c0 pack. T = 300 is the Counts the pack
ships; T = 600 doubles every multiplicity; T = 0 has none. Door scripted as the README's: `b1`, `all`,
`same`, `right`. Prints `episode_prior` and `_play` seconds, the acts, and a digest of the final
belief's exact weights, so two kernels' runs can be compared line for line.

    PYTHONPATH=<kernel>/src python3 tools/integer_weights.py <pack.py> [0,1,2]

The pack is read from its own directory, as the README ran it. The memo is cleared between runs."""
import hashlib
import os
import sys
import time
from collections import Counter

import wald
from wald import counts as C
from wald.belief import _weights
from wald.episode import _play
from wald.plate import plate

PACK = os.path.abspath(sys.argv[1])
MULTS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0, 1, 2]


class ScriptedDoor(wald.Door):
    def outcome(self, act):
        return {"confidence": "b1", "agreement": "all", "second_opinion": "same"}.get(act, "right")

    def fire(self, act):
        pass


os.chdir(os.path.dirname(PACK))
print("kernel", os.path.dirname(wald.__file__), flush=True)
t = time.time()
with open(PACK, encoding="utf-8", newline="") as f:
    world = wald.declare(wald.load_pack(f.read(), "."))
print(f"load {time.time() - t:.0f} s", flush=True)
plated = plate(world)._plated
base = Counter(plated.counts)
for m in MULTS:
    counts = Counter({r: n * m for r, n in base.items()}) if m else Counter()
    t = time.time()
    prior = C.episode_prior(plated, counts)
    t_ep = time.time() - t
    t = time.time()
    r = _play(plated.world, prior, ScriptedDoor())
    t_play = time.time() - t
    plated.world._work = None
    final = hashlib.sha256(repr(list(_weights(r.final).items())).encode()).hexdigest()[:16]
    print(f"T={sum(counts.values()):4d}  episode_prior {t_ep:6.2f} s  _play {t_play:6.2f} s  "
          f"acts {r.acts}  final {final}  operations {r.operations}", flush=True)
