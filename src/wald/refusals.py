"""The refusals, by name. A pack is refused at declaration and told which clause refused it;
the kernel raises WorldFalsified for zero evidence (S5) and ObsSpent for a token used twice (S2)."""


class Refused(Exception):
    """A pack refused at declaration. `name` is the clause of the page that refused it."""

    def __init__(self, name, detail=""):
        self.name = name
        Exception.__init__(self, name if not detail else name + ": " + detail)


class WorldFalsified(Exception):
    """An observation of zero mass under the belief. The episode ends here, and nothing is
    silently handled: the World said this could not happen and it did (S5)."""


class ObsSpent(Exception):
    """An Obs consumed a second time. Every Obs that does not falsify the World is consumed
    by exactly one condition (S2)."""


EMPTY_T = "EMPTY_T"                # section 1: T is non-empty
PRIOR = "PRIOR"                    # section 1: P0 is strictly positive and sums to 1
KERNEL_ROW = "KERNEL_ROW"          # S4: every row of every kernel sums to 1
PRICE = "PRICE"                    # section 1: price : O -> Q>=0
DEPTH = "DEPTH"                    # E3: 1 <= d <= N
ZERO_EVIDENCE = "ZERO_EVIDENCE"    # S5: `closed`, or a bottom state with full support
SHARED_SOURCE = "SHARED_SOURCE"    # S2: a source read twice is a declared component of Omega
TABLE_SOURCE = "TABLE_SOURCE"      # S3: every table names its source
