"""wald: the kernel of a language for Bayesian decision-theoretic agents.

A host gets four names: `declare` a World, `run` an episode against a `Door`, and `report` a
belief as an inert `Display`. The verbs of section 2 -- push, condition, expect and decide --
are not here: a host never holds a probability, and only the kernel chooses (S1, E5)."""
from . import refusals
from .belief import report
from .display import Display
from .episode import Door, run
from .world import declare

__all__ = ["declare", "run", "Door", "report", "Display", "refusals"]
