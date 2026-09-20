"""The episode of section 2, in the page's order, and the Door the host implements. The floor
lives here and only here: play is decide_min(d,n) (E3)."""
from fractions import Fraction

from .belief import condition, prior
from .decide import decide
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
    how it ended, what it paid, and the belief it ended holding."""

    __slots__ = ("acts", "outcomes", "status", "paid", "final")

    def __init__(self, acts, outcomes, status, paid, final):
        self.acts = tuple(acts)
        self.outcomes = tuple(outcomes)
        self.status = status
        self.paid = paid
        self.final = final

    def __repr__(self):
        return "Result(" + str(self.acts) + ", " + self.status + ", paid " + str(self.paid) + ")"


def run(world, door):
    """n <- N. Repeat: a <- decide_min(d,n)(b,M). If a is terminal the door fires it and the
    episode ends. Otherwise the door executes a, the episode pays price(a), the door mints o,
    and then, in this order: if P_b(o|a) = 0 the episode ends as WORLD_FALSIFIED; else
    b <- b|a,o; then if o is an ending outcome the episode ends, earning u_end; else M <- M',
    n <- n-1."""
    belief = prior(world)
    n = world.N
    used = set()
    acts, outcomes, paid = [], [], Fraction(0)
    while True:
        act = decide(belief, world, min(world.d, n), frozenset(used))
        acts.append(act)
        if act in world.T:
            door.fire(act)
            return Result(acts, outcomes, TERMINAL, paid, belief)
        spec = world.O[act]
        paid += spec.price
        obs = door.observe(act)
        outcomes.append(obs.value)
        try:
            belief = condition(belief, world, obs)
        except WorldFalsified:
            return Result(acts, outcomes, WORLD_FALSIFIED, paid, belief)
        if obs.value in spec.ends:
            return Result(acts, outcomes, ENDED, paid, belief)
        if spec.once:
            used.add(act)
        n -= 1
