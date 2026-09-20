"""The page's appendix vector and the shapes the tests declare against."""
from fractions import Fraction as F

SRC = {"prior": "data", "utility": "elicited", "price": "elicited", "horizon": "elicited", "depth": "elicited"}
APPX_T = {"treat": {"sick": F(0), "well": F(-2)}, "leave": {"sick": F(-10), "well": F(0)}}
APPX_K = {"sick": {"+": F(9, 10), "-": F(1, 10)}, "well": {"+": F(1, 5), "-": F(4, 5)}}


def act(K, price, once=True, ends=None):
    return {"K": K, "price": price, "once": once, "ends": ends or {}}


def spec(prior, T, O, N=1, d=1, **kw):
    s = {"prior": prior, "T": T, "O": O, "N": N, "d": d, "closed": True,
         "table_sources": dict(SRC, kernels={k: ["data"] for k in O})}
    s.update(kw)
    return s


def appendix(price=F(1, 2), once=True, N=1, d=1):
    return spec({"sick": F(1, 5), "well": F(4, 5)}, APPX_T, {"test": act(APPX_K, price, once)}, N, d)
