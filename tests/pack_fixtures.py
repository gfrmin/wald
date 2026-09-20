"""Packs the tests write. The corpus in charter/laws/packs is the author's; these go where it is
thin, and every one of them is text -- a pack is parsed, never executed."""

APPENDIX = '''
world("p", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
space({"health": ["sick", "well"]})
prior({"sick": 1/5, "well": 4/5}, source="data")
utility({"treat": {"sick": 0, "well": -2}, "leave": {"sick": -10, "well": 0}}, source="elicited")
price({"test": 1/2}, source="elicited")
act("test", once=True, kernel=table({"sick": {"+": 9/10, "-": 1/10}, "well": {"+": 1/5, "-": 4/5}}, source="data"), reads=["health"])
'''

TWO_COMPONENTS = '''
world("two", closed=True)
horizon(2, source="elicited")
depth(1, source="elicited")
space({"side": ["x", "y"], "draw": ["p", "m"]})
prior({("x", "p"): 3/8, ("x", "m"): 1/8, ("y", "p"): 1/8, ("y", "m"): 3/8}, source="data")
utility({"go": by("side", {"x": 1, "y": -4}), "hold": by("side", {"x": 0, "y": 0})}, source="elicited")
price({"peek": 1/20, "again": 1/20}, source="elicited")
act("peek", once=True, kernel=point("draw"), reads=["draw"])
act("again", once=False, kernel=by("side", {"x": {"L": 3/4, "R": 1/4}, "y": {"L": 1/4, "R": 3/4}}, source="elicited"), reads=["side"])
'''

PRODUCT_AND_MIXTURE = '''
world("built", closed=True)
horizon(1, source="elicited")
depth(1, source="elicited")
space({"health": ["sick", "well"]})
param("lie", 1/10, source="elicited")
prior({"sick": 1/5, "well": 4/5}, source="data")
utility({"treat": {"sick": 0, "well": -2}, "leave": {"sick": -10, "well": 0}}, source="elicited")
price({"both": 1/2}, source="elicited")
act("both", once=True, kernel=product(
        point("health"),
        mixture([(1 - lie, table({"sick": {"+": 1, "-": 0}, "well": {"+": 0, "-": 1}}, source="data")),
                 (lie, compose(table({"sick": {"+": 1/2, "-": 1/2}, "well": {"+": 1/2, "-": 1/2}}, source="data"),
                               {"+": {"+": 1 - lie, "-": lie}, "-": {"+": lie, "-": 1 - lie}}, source="elicited"))],
                source="elicited")),
    reads=["health"])
'''

ENDING_AND_BOTTOM = '''
world("guess", bottom="rest")
horizon(2, source="elicited")
depth(2, source="elicited")
space({"answer": ["a", "b", "rest"]})
prior({"a": 2/5, "b": 2/5, "rest": 1/5}, source="data")
utility({"give up": {"a": -8, "b": -8, "rest": -8}}, ending={"say a": {"hit": {"a": 0, "b": 0, "rest": 0}}}, source="elicited")
price({"say a": 1}, source="elicited")
act("say a", once=True, kernel=table({"a": {"hit": 3/4, "miss": 1/4}, "b": {"hit": 1/4, "miss": 3/4}, "rest": {"hit": 1/2, "miss": 1/2}}, source="data"), reads=["answer"])
'''


def without(pack, line):
    return "\n".join(l for l in pack.splitlines() if not l.startswith(line)) + "\n"


def instead(pack, line, replacement):
    return "\n".join(replacement if l.startswith(line) else l for l in pack.splitlines()) + "\n"
