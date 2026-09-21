"""The episode of section 2, in the page's order, and the Door the host implements. Its one act
of its own is the step: `decide+`, which under CHARTER v0.1 may buy a deeper look before it
returns an act, and which under a v0 World is the floor and nothing else (E3).

A think act is not an act: the door never sees it, it mints no Obs, it consumes no horizon, and
what it costs is not a price. It is charged here, beside the episode that bought it, and the
operations it took are written down here too -- as a measurement, in no value and by no clock."""
from fractions import Fraction

from .belief import _counted, condition, prior
from .decide import REFUSED, STRUCK_CAP, STRUCK_N, THINK, step
from .obs import mint
from .refusals import WorldFalsified

TERMINAL = "TERMINAL"
ENDED = "ENDED"
WORLD_FALSIFIED = "WORLD_FALSIFIED"


class Door:
    """The world's edge. The host says what an act reads and what firing one does; `observe`
    is the only mint, so every Obs in existence came of executing an observational act."""

    def outcome(self, act):
        raise NotImplementedError("a door says what an observational act reads")

    def fire(self, act):
        raise NotImplementedError("a door says what a terminal act does")

    def observe(self, act):
        return mint(act, self.outcome(act))


class Result:
    """What one episode did: the acts played (the terminal one last), the raw values observed,
    how it ended, what it paid in prices, and the belief it ended holding -- and then what it
    paid for thought, how its steps were settled (S7's four counts) and what each thought
    actually took to think (E6, one count per think act, in order)."""

    __slots__ = ("acts", "outcomes", "status", "paid", "final", "thought", "steps", "operations")

    def __init__(self, acts, outcomes, status, paid, final, thought, steps, operations):
        self.acts = tuple(acts)
        self.outcomes = tuple(outcomes)
        self.status = status
        self.paid = paid
        self.final = final
        self.thought = thought
        self.steps = dict(steps)
        self.operations = tuple(operations)

    def __repr__(self):
        return "Result(" + str(self.acts) + ", " + self.status + ", paid " + str(self.paid) + ")"


def run(world, door):
    """n <- N. Repeat: a <- decide+(b,M,n) -- which, if it took theta, has already paid for it
    and evaluated the act it bought, and did not touch n doing so. If a is terminal the door
    fires it and the episode ends. Otherwise the door executes a, the
    episode pays price(a), the door mints o, and then, in this order: if P_b(o|a) = 0 the episode
    ends as WORLD_FALSIFIED; else b <- b|a,o; then if o is an ending outcome the episode ends,
    earning u_end; else M <- M', n <- n-1.

    Under a v0 World decide+ is decide_min(d,n) and nothing below it ever fires."""
    belief = prior(world)
    n = world.N
    used = set()
    acts, outcomes, paid = [], [], Fraction(0)
    thought, operations = Fraction(0), []
    steps = {STRUCK_N: 0, STRUCK_CAP: 0, REFUSED: 0, THINK: 0}

    def ended(status):
        return Result(acts, outcomes, status, paid, belief, thought, steps, operations)

    while True:
        act, how, cost = step(belief, world, n, frozenset(used))
        if how in steps:                        # S7's four; a v0 World's step is in none of them
            steps[how] += 1
        if how == THINK:
            thought += cost
            operations.append(_counted())
        acts.append(act)
        if act in world.T:
            door.fire(act)
            return ended(TERMINAL)
        spec = world.O[act]
        paid += spec.price
        obs = door.observe(act)
        outcomes.append(obs.value)
        try:
            belief = condition(belief, world, obs)
        except WorldFalsified:
            return ended(WORLD_FALSIFIED)
        if obs.value in spec.ends:
            return ended(ENDED)
        if spec.once:
            used.add(act)
        n -= 1
