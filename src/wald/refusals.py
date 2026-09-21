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
TABLE_SHAPE = "TABLE_SHAPE"        # section 1: a table is total over Omega, and B_k holds the endings

# Of CHARTER v0.1, the think act. A World that declares no Depth+ is a v0 World and reads none of
# these tables, so none of these names can speak to it.
FRACTION = "FRACTION"              # section 1: 0 <= f <= 1, source `elicited` or `fitted` (S6)
COST = "COST"                      # section 1: ops total over s = 1..|Omega| and >= 0; r >= 0 (S6)
DEPTH_PLUS = "DEPTH_PLUS"          # J11: a World with theta declares d = 1, d+ = 2, N >= 2
RATE = "RATE"                      # section 1: the Rate's source is `elicited`
UNSCORED = "UNSCORED"              # S10: a `fitted` meta-table carries its Score (J18)

# Of the surface (SURFACE section 5). A pack that breaks one rule is refused by that rule's name;
# one that breaks several, by any one of theirs -- no order is promised (SURFACE K7).
SYNTAX = "SYNTAX"                        # not Python's syntax at all
NOT_A_DECLARATION = "NOT_A_DECLARATION"  # a form the grammar of SURFACE section 1 does not have
DUPLICATE = "DUPLICATE"                  # said twice: a declaration, a key, a name, a state
BAD_NAME = "BAD_NAME"                    # a parameter name a cell cannot read
UNKNOWN_NAME = "UNKNOWN_NAME"            # a name no declaration gave a meaning
FLOAT = "FLOAT"                          # a decimal, where only exact rationals are meant
DIVISION_BY_ZERO = "DIVISION_BY_ZERO"    # in a cell
UNHOUSED_NUMERAL = "UNHOUSED_NUMERAL"    # a numeral outside the six tables (S3, SURFACE K3)
DATA_HASH = "DATA_HASH"                  # the data file is not the one the pack pinned
UNDECLARED_READ = "UNDECLARED_READ"      # a kernel names or depends on what its act does not read
MISSING = "MISSING"                      # a declaration a pack must make and did not
UNREAD_PARAMETER = "UNREAD_PARAMETER"    # a declared parameter nobody reads (S3)
