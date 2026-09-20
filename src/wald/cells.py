"""SURFACE section 3: numbers. What a cell may hold, where a number is allowed to live, the
`fitted` fence, and the census of quantities by source.

Two vocabularies meet here and they are not the same. A *plain* position -- a name in quotes,
True or False, lists and tuples of them -- holds no number at all: a numeral there is unhoused.
A *cell* holds an integer, a parameter, unary minus, and + - * / over these, exactly."""
import ast
import keyword
from fractions import Fraction

from .refusals import (BAD_NAME, DIVISION_BY_ZERO, DUPLICATE, FLOAT, NOT_A_DECLARATION,
                       TABLE_SOURCE, UNHOUSED_NUMERAL, UNKNOWN_NAME, UNREAD_PARAMETER, Refused)

TAGS = ("data", "elicited", "fitted")
FITTED = "fitted"



def where(node):
    return "line " + str(getattr(node, "lineno", "?"))


class Cells:
    """The pack's numbers: its parameters, which of them have been read, and the count of
    quantities by source. One of these per pack."""

    def __init__(self):
        self.params = {}
        self.source_of = {}
        self.read = set()
        self.census = {tag: 0 for tag in TAGS}

    def count(self, tag, n=1):
        """A quantity, counted once however it is written: a cell, a parameter, a mixture
        weight, a price, the horizon, the depth."""
        self.census[tag] += n

    def plain(self, node):
        """A literal with no number in it. This is where a stray numeral is unhoused."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, bool)):
                return node.value
            if isinstance(node.value, (int, float, complex)):
                raise Refused(UNHOUSED_NUMERAL, where(node) + ": " + repr(node.value)
                              + " is not in a table")
        if isinstance(node, ast.List):
            return [self.plain(e) for e in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self.plain(e) for e in node.elts)
        raise Refused(NOT_A_DECLARATION, where(node) + ": a name in quotes, True or False, or a"
                      + " list or tuple of them")

    def tag(self, node):
        """A source: data, elicited or fitted, and nothing else."""
        t = self.plain(node)
        if t not in TAGS:
            raise Refused(TABLE_SOURCE, where(node) + ": " + repr(t) + " is not "
                          + ", ".join(TAGS))
        return t

    def number(self, node, tag):
        """A cell, read exactly. `tag` is the source of the table holding it: a table that does
        not say `fitted` may not read a fitted parameter, and there is no way to promote one."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise Refused(NOT_A_DECLARATION, where(node) + ": a boolean is not a number")
            if isinstance(node.value, float) or isinstance(node.value, complex):
                raise Refused(FLOAT, where(node) + ": " + repr(node.value)
                              + " is not exact; write a ratio of integers")
            if isinstance(node.value, int):
                return Fraction(node.value)
        if isinstance(node, ast.Name):
            if node.id not in self.params:
                raise Refused(UNKNOWN_NAME, where(node) + ": " + node.id
                              + " is not a parameter this pack declared")
            if tag != FITTED and self.source_of[node.id] == FITTED:
                raise Refused(TABLE_SOURCE, where(node) + ": a " + repr(tag) + " table reads the"
                              + " fitted parameter " + repr(node.id) + "; fitted does not promote")
            self.read.add(node.id)
            return self.params[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self.number(node.operand, tag)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            left = self.number(node.left, tag)
            right = self.number(node.right, tag)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if right == 0:
                raise Refused(DIVISION_BY_ZERO, where(node))
            return left / right
        raise Refused(NOT_A_DECLARATION, where(node) + ": not a number a table can hold")

    def declare_param(self, name_node, value_node, tag):
        """A table cell written once and read by name (SURFACE K11). It keeps its own source
        wherever it is read."""
        name = self.plain(name_node)
        if name in self.params:
            raise Refused(DUPLICATE, "the parameter " + repr(name) + " is declared twice")
        if not isinstance(name, str) or not name.isidentifier() or keyword.iskeyword(name):
            raise Refused(BAD_NAME, repr(name) + " cannot be read from a cell")
        self.params[name] = self.number(value_node, tag)
        self.source_of[name] = tag
        self.count(tag)

    def refuse_unread(self):
        """CHARTER S3: every declared parameter is read."""
        unread = sorted(name for name in self.params if name not in self.read)
        if unread:
            raise Refused(UNREAD_PARAMETER, ", ".join(unread) + ": declared and read by nothing")
