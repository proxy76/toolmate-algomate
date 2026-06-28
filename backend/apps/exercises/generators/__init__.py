"""Exercise generator engine.

Each generator is a callable that accepts (difficulty, rng) and returns a
dict with `topic`, `question_latex`, `hint_latex`, `answer_latex`, plus
optional `steps_latex`. Answers are verified with sympy when possible.

The `REGISTRY` maps (topic_code, profile) -> generator. A topic can be
registered for multiple profiles with different generators (e.g. simpler
M3 versions of the same topic).
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

from . import (
    combinatorics,
    complex_numbers,
    derivatives,
    integrals,
    limits,
    logarithms,
    matrices,
    polynomials,
    powers,
    progressions,
    trigonometry,
)

Generator = Callable[[int, "random.Random"], dict]

# (topic_code, profile) -> generator
REGISTRY: Dict[Tuple[str, str], Generator] = {
    # powers / radicals — all profiles
    ("powers", "M1"): powers.generate,
    ("powers", "M2"): powers.generate,
    ("powers", "M3"): powers.generate_basic,
    # logarithms — M1/M2
    ("logarithms", "M1"): logarithms.generate,
    ("logarithms", "M2"): logarithms.generate,
    # complex — M1 (full) and M2 (algebraic only)
    ("complex", "M1"): complex_numbers.generate,
    ("complex", "M2"): complex_numbers.generate_algebraic,
    # polynomials
    ("polynomials", "M1"): polynomials.generate,
    ("polynomials", "M2"): polynomials.generate,
    # matrices
    ("matrices", "M1"): matrices.generate,
    ("matrices", "M2"): matrices.generate,
    # limits
    ("limits", "M1"): limits.generate,
    ("limits", "M2"): limits.generate,
    # derivatives
    ("derivatives", "M1"): derivatives.generate,
    ("derivatives", "M2"): derivatives.generate,
    ("derivatives", "M3"): derivatives.generate_basic,
    # integrals — M1/M2
    ("integrals", "M1"): integrals.generate,
    ("integrals", "M2"): integrals.generate,
    # trigonometry — all
    ("trigonometry", "M1"): trigonometry.generate,
    ("trigonometry", "M2"): trigonometry.generate,
    ("trigonometry", "M3"): trigonometry.generate_basic,
    # combinatorics — all
    ("combinatorics", "M1"): combinatorics.generate,
    ("combinatorics", "M2"): combinatorics.generate,
    ("combinatorics", "M3"): combinatorics.generate_basic,
    # progressions — M2/M3
    ("progressions", "M2"): progressions.generate,
    ("progressions", "M3"): progressions.generate,
}


SUPPORTED_TOPICS_PER_PROFILE: Dict[str, list] = {}
for (code, profile) in REGISTRY:
    SUPPORTED_TOPICS_PER_PROFILE.setdefault(profile, []).append(code)
for v in SUPPORTED_TOPICS_PER_PROFILE.values():
    v.sort()


TOPIC_LABELS = {
    "powers": "Puteri și radicali",
    "logarithms": "Logaritmi",
    "complex": "Numere complexe",
    "polynomials": "Polinoame",
    "matrices": "Matrice și determinanți",
    "limits": "Limite de funcții",
    "derivatives": "Derivate",
    "integrals": "Primitive și integrale",
    "trigonometry": "Trigonometrie",
    "combinatorics": "Combinatorică și probabilități",
    "progressions": "Progresii",
}
