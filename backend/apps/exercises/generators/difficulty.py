"""Difficulty parameters and per-set difficulty distribution.

Encodes ``generator.md`` §7.2 (coefficient/technique envelope per level) and
§8.4 (``compute_item_difficulty`` — natural spread inside a set).

Philosophy (decision D4 in GENERATOR_REWORK.md): difficulty is **technique-first**.
We allow the *mild* coefficient/parameter growth the spec describes at d2/d3, but
answers must stay clean (int, simple fraction, √2/√3/√5) — never escalate by
arithmetic mess alone (§13.2).
"""
from __future__ import annotations

import random

# Per-level envelope. Generators read these instead of hard-coding ranges, so
# the difficulty contract is consistent across topics (§7.2).
DIFFICULTY: dict[int, dict] = {
    1: {  # Ușor / Subiectul I
        "coef_lo": -6, "coef_hi": 6,
        "max_exp": 3,
        "max_params": 1,
        "allow_negative": True,
        "allow_inequality": False,
        "allow_two_params": False,
        "radicals": [2, 3, 5],
        "log_bases": [2, 3, 10],
    },
    2: {  # Mediu / Subiectul II a,b
        "coef_lo": -10, "coef_hi": 10,
        "max_exp": 4,
        "max_params": 2,
        "allow_negative": True,
        "allow_inequality": True,
        "allow_two_params": True,
        "radicals": [2, 3, 5, 6, 7],
        "log_bases": [2, 3, 5, 6, 10],
    },
    3: {  # Greu / Subiectul II c, III b,c
        "coef_lo": -10, "coef_hi": 10,
        "max_exp": 4,
        "max_params": 2,
        "allow_negative": True,
        "allow_inequality": True,
        "allow_two_params": True,
        "radicals": [2, 3, 5, 6, 7, 10],
        "log_bases": [2, 3, 5, 6, 10],
        "natural_number_answers": True,  # c often asks for n ∈ ℕ
    },
}


# §8.4 — within a set requested at ``base_difficulty``, items vary so the set
# feels like a real paper. Deterministic, position-indexed.
_DISTRIBUTIONS: dict[int, list[int]] = {
    1: [1, 1, 1, 1, 2],   # 80% easy / 20% medium
    2: [1, 2, 2, 2, 3],   # 20 / 60 / 20
    3: [2, 3, 3, 3, 3],   # 10 / 90
}


def compute_item_difficulty(base_difficulty: int, position: int, total: int = 0) -> int:
    """Difficulty for item ``position`` in a set requested at ``base_difficulty``.

    Deterministic but position-dependent so the spread is reproducible (§8.4).
    """
    pool = _DISTRIBUTIONS.get(base_difficulty, [base_difficulty])
    return pool[position % len(pool)]


# --- rng-bound samplers (clean, small numbers at every level) ----------------
def coef(rng: random.Random, difficulty: int, *, nonzero: bool = False) -> int:
    """A clean coefficient within the level's envelope (kept small on purpose)."""
    p = DIFFICULTY[difficulty]
    # Keep magnitudes tidy regardless of level; the spec's larger ranges exist
    # for variety, not to create messy arithmetic.
    lo, hi = (-5, 5) if difficulty == 1 else (-6, 6)
    if not p["allow_negative"]:
        lo = 1
    v = rng.randint(lo, hi)
    if nonzero:
        while v == 0:
            v = rng.randint(lo, hi)
    return v


def positive(rng: random.Random, lo: int = 2, hi: int = 6) -> int:
    return rng.randint(lo, hi)
