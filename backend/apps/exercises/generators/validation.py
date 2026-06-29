"""Central validation gardens (spec §11.3–11.4).

Shared sanity checks applied uniformly by the base generators on top of each
topic's own ``_validate``. They reject the universal failure modes — undefined
results, runaway expressions, empty or malformed LaTeX — so no individual
generator has to re-implement them.
"""
from __future__ import annotations

import sympy as sp

_BAD_SUBSTRINGS = ("nan", "zoo", r"\text{nan}", "i*oo", "oo*i")


def is_sane_value(expr, max_latex: int = 300) -> bool:
    """A computed sympy answer is undefined-free, finite-ish and not gigantic.

    ``None`` is allowed: some generators return a custom answer string and carry
    no sympy object (they are validated via :func:`is_clean_latex`).
    """
    if expr is None:
        return True
    try:
        if expr in (sp.nan, sp.zoo):
            return False
        fin = getattr(expr, "is_finite", None)
        if fin is False:          # explicitly infinite (None = unknown is allowed)
            return False
        if len(sp.latex(expr)) > max_latex:
            return False
    except Exception:
        return False
    return True


def is_clean_latex(s: str, max_len: int = 320) -> bool:
    """A LaTeX fragment is non-empty, bounded, and free of undefined markers."""
    if not s or not s.strip():
        return False
    if len(s) > max_len:
        return False
    low = s.lower()
    return not any(bad in low for bad in _BAD_SUBSTRINGS)


def item_is_clean(item: dict) -> bool:
    """Final gate for a single-item payload before it leaves a generator."""
    if not is_clean_latex(item.get("question_latex", "")):
        return False
    if not is_clean_latex(item.get("answer_latex", "")):
        return False
    return True
