"""wald: the kernel of a language for Bayesian decision-theoretic agents.

A host gets ten names. `declare` a World -- from a spec, from a pack with `load_pack`, or from
the wire with `from_json` -- `run` an episode against a `Door`, and `report` a belief as an inert
`Display`; `to_json` gives the Result back as text, `refusals` names every clause that can refuse,
and `law` says which signed pages this package was judged under. The verbs of section 2 -- push,
condition, expect and decide -- are not here: a host never holds a probability, and only the
kernel chooses (S1, E5)."""
from . import refusals
from .belief import report
from .display import Display
from .episode import Door, run
from .law import law
from .surface import check as load_pack
from .wire import from_json, to_json
from .world import declare

# The four names of brief 006 are bound above but not listed here: kit_structural's ST1 still holds
# __all__ to the six of INTERFACE's first section, and brief 006 asks for all ten. QUESTIONS.md Q5.
__all__ = ["declare", "run", "Door", "report", "Display", "refusals"]
