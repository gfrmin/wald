"""Brief 012's measurement: `Plate.values()` beside one episode, after 0, 300 and 600 records.

    python3 tools/host_reports_timing.py PACK [DATA_DIR] [SEED]

The plate writes its own records: a door draws a state from the declared prior and every report
from that state's rows, as the kit's L6 door does, so no record falsifies the plate."""
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import wald  # noqa: E402
from wald.episode import ending  # noqa: E402


def door(plated, rng):
    states = list(plated.world.prior.items())
    state = rng.choices([s for s, _ in states], [p for _, p in states])[0]

    def pick(row):
        row = dict(row.items())
        os_ = [o for o, p in row.items() if p > 0]
        return rng.choices(os_, [row[o] for o in os_])[0]

    class Drawn(wald.Door):
        end = None

        def outcome(self, act):
            if plated.after is not None and act == plated.after.name:
                return pick(plated.after.kernels[self.end].row(state))
            o = pick(plated.world.O[act].kernel.row(state))
            if o in plated.world.O[act].ends:
                self.end = ending(act, o)
            return o

        def fire(self, act):
            self.end = act
    return Drawn()


def main(path, data_dir, seed):
    with open(path, encoding="utf-8", newline="") as f:
        world = wald.declare(wald.load_pack(f.read(), data_dir))
    p, rng, written = wald.plate(world), random.Random(seed), 0
    print(os.path.basename(path) + ": " + str(len(world.world.prior.carrier())) + " states")
    for target in (0, 300, 600):
        while written < target:
            p.run(door(world, rng))
            written += 1
        t = time.perf_counter()
        p.values()
        tv = time.perf_counter() - t
        t = time.perf_counter()
        p.run(door(world, rng))
        te = time.perf_counter() - t
        written += 1
        print(f"  {target:4d} records: values() {tv:.4f} s, one episode {te:.4f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(sys.argv[1]),
         int(sys.argv[3]) if len(sys.argv) > 3 else 1)
