"""Helpers shared by every generator.

Difficulty philosophy — calibrated to the Romanian BAC
------------------------------------------------------
Difficulty is **structural, not arithmetic**. The official exam keeps numbers
clean and escalates difficulty by *technique* and *number of steps*, mirroring
its own three-part paper:

    1  ->  Subiectul I   : one step, direct recall/computation (clasa IX-X).
    2  ->  Subiectul II  : direct application of a single method/formula.
    3  ->  Subiectul III : multi-step reasoning — function study, tangent,
                           monotonicity, integral applications.

So a generator must NOT make an exercise "harder" by enlarging coefficients
(``3x^4`` and ``12x^8`` are the same task — the power rule — just messier
arithmetic). Instead it selects a harder *technique* and chains more *steps*,
while keeping the final answer a clean integer or simple fraction.

Each topic registers its sub-types under the tier they belong to and calls
``choose_subtype`` so the requested difficulty controls *which kind* of problem
is produced, with graceful fallback when a topic has no variant at that tier.
"""
from __future__ import annotations

import random
from typing import Callable, Dict, Iterable, List

import sympy as sp

# Shared symbols.
x = sp.Symbol("x", real=True)
n = sp.Symbol("n", positive=True, integer=True)

# Human label for where this difficulty sits on a real BAC paper.
BAC_CONTEXT: Dict[int, str] = {
    1: "Subiectul I",
    2: "Subiectul II",
    3: "Subiectul III",
}


def latex(expr) -> str:
    """sympy -> compact LaTeX. Juxtaposition for products (``6x^2``, ``2xe^{2x}``)
    as in the real BAC papers — no ``\\cdot`` between coefficients and variables
    (it is non-standard here and widens expressions ~15%, risking PDF overflow)."""
    return sp.latex(expr)


def pick(rng: random.Random, items: Iterable):
    items = list(items)
    return items[rng.randrange(len(items))]


def nonzero(rng: random.Random, lo: int, hi: int) -> int:
    """Random int in [lo, hi], never zero (useful for coefficients)."""
    v = rng.randint(lo, hi)
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def small_coef(rng: random.Random, allow_negative: bool = True) -> int:
    """A clean, small coefficient.

    Magnitude is *deliberately independent of difficulty*: the BAC keeps
    arithmetic tidy at every level. Difficulty lives in the technique, not the
    size of the numbers.
    """
    lo = -5 if allow_negative else 1
    return nonzero(rng, lo, 5)


def small_pos(rng: random.Random, lo: int = 2, hi: int = 6) -> int:
    return rng.randint(lo, hi)


# A sub-type is a callable that takes the rng and returns a partial item dict
# (topic / question_latex / answer_latex / hint_latex / steps_latex). The tier
# and bac_context are stamped on by ``choose_subtype``.
Subtype = Callable[[random.Random], dict]
Tiers = Dict[int, List[Subtype]]


def make(
    topic: str,
    question_latex: str,
    answer_latex: str,
    hint_latex: str | None = None,
    steps_latex: List[str] | None = None,
) -> dict:
    """Assemble the per-item payload shared by every generator."""
    out: dict = {
        "topic": topic,
        "question_latex": question_latex,
        "answer_latex": answer_latex,
    }
    if hint_latex:
        out["hint_latex"] = hint_latex
    if steps_latex:
        out["steps_latex"] = steps_latex
    return out


def choose_subtype(difficulty: int, rng: random.Random, tiers: Tiers) -> dict:
    """Pick a sub-type whose *technique* matches the requested difficulty.

    Falls back to the nearest available tier (preferring an easier one) so a
    topic that has no variant at the requested level still returns its closest
    authentic item. The delivered item's ``difficulty`` reflects the tier that
    actually produced it, so the label never lies.
    """
    # Try the exact tier, then descend (easier), then ascend (harder).
    order = [difficulty]
    order += [difficulty - k for k in range(1, 3) if difficulty - k >= 1]
    order += [difficulty + k for k in range(1, 3) if difficulty + k <= 3]
    for tier in order:
        pool = tiers.get(tier)
        if pool:
            item = pick(rng, pool)(rng)
            item.setdefault("difficulty", tier)
            item.setdefault("bac_context", BAC_CONTEXT[tier])
            return item
    raise ValueError("no sub-types registered for any difficulty tier")
