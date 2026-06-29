"""LaTeX output conventions (spec §12).

Reference constants for Romanian BAC notation plus ``sympy_to_bac_latex``, the
default sympy → ``$...$`` converter used by the base generator.

NOTE: the spec's illustrative ``sympy_to_bac_latex`` (§12.3) includes a blanket
``\\log → \\ln`` replacement — that is incorrect (it would corrupt ``\\log_2`` and
change the meaning of base-b logarithms), so we do **not** apply it. Correctness
wins over the literal snippet (cf. §11, §13.3).
"""
from __future__ import annotations

import sympy as sp

# Number sets (spec §12.1).
LATEX_SETS = {
    "R": r"\mathbb{R}",
    "N": r"\mathbb{N}",
    "Z": r"\mathbb{Z}",
    "Q": r"\mathbb{Q}",
    "C": r"\mathbb{C}",
    "R+": r"(0, +\infty)",
    "R*": r"\mathbb{R}^*",
}

# Romanian terminology with correct article agreement (spec §12.1).
RO_TERMS = {
    "domain": "domeniu",
    "function": "funcție",
    "sequence": "șir",
    "polynomial": "polinom",
    "matrix": "matrice",
    "derivative": "derivată",
    "integral": "integrală",
    "limit": "limită",
    "probability": "probabilitate",
}


def sympy_to_bac_latex(expr, simplify: bool = False) -> str:
    """Convert a sympy object to BAC-style LaTeX wrapped in ``$...$``.

    Uses ``mul_symbol="dot"`` for an explicit ``·`` and avoids the
    ``\\left/\\right`` blow-up where possible. ``simplify`` is opt-in so that an
    already-clean computed answer is not re-shaped unexpectedly.
    """
    if simplify:
        expr = sp.simplify(expr)
    return f"${sp.latex(expr, mul_symbol='dot')}$"
