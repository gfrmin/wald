"""The Obs token: (act, value), minted only by the door when an observational act is executed,
and consumed by exactly one `condition` (section 1, S2)."""
from .refusals import ObsSpent

_MINT = object()


class Obs:
    """A token. It is not a record to be read twice: the second reading is the bug S2 forbids."""

    __slots__ = ("_act", "_value", "_spent")

    def __init__(self, act, value, mint=None):
        if mint is not _MINT:
            raise TypeError("an Obs is minted by the door, by executing an observational act")
        object.__setattr__(self, "_act", act)
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_spent", False)

    def __setattr__(self, name, value):
        raise AttributeError("an Obs is spent through `condition`, not set")

    @property
    def act(self):
        return self._act

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return "Obs(" + repr(self._act) + ", " + repr(self._value) + ")"


def mint(act, value):
    """Called by the door and by nothing else: Door.observe is the only mint."""
    return Obs(act, value, _MINT)


def check_unspent(obs):
    if obs._spent:
        raise ObsSpent(repr(obs) + " was already consumed by a condition")


def spend(obs):
    object.__setattr__(obs, "_spent", True)
