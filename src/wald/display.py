"""A display value: it renders, and it does nothing else. It has no comparison, no arithmetic,
no truth and no number, so it cannot reach control flow or a belief (S1)."""

_MINT = object()


def _inert(*args, **kwargs):
    raise TypeError("a display value has no operations: it renders, and flows nowhere (S1)")


class Display:
    """Minted by `report`. Every operation below is the one a gate would need."""

    __slots__ = ("_text",)

    def __init__(self, text, mint=None):
        if mint is not _MINT:
            raise TypeError("a Display is minted by `report`")
        object.__setattr__(self, "_text", text)

    def __setattr__(self, name, value):
        raise AttributeError("a display value is immutable")

    def __str__(self):
        return self._text

    def __repr__(self):
        return self._text

    __lt__ = __le__ = __gt__ = __ge__ = __eq__ = __ne__ = _inert
    __add__ = __sub__ = __mul__ = __truediv__ = __floordiv__ = __mod__ = __pow__ = _inert
    __radd__ = __rsub__ = __rmul__ = __rtruediv__ = __rfloordiv__ = __rmod__ = __rpow__ = _inert
    __neg__ = __pos__ = __abs__ = __round__ = _inert
    __float__ = __int__ = __index__ = __complex__ = __bool__ = _inert
    __iter__ = __len__ = __getitem__ = __contains__ = __next__ = _inert
    __hash__ = None


def render(text):
    """The only mint: `report` calls it, nothing else does."""
    return Display(text, _MINT)
