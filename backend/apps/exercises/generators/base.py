"""Abstract base classes for BAC generators.

This is the spec architecture from ``generator.md`` §8.1, extended with a
``ProblemGenerator`` for the linked a/b/c sub-items required by Subiectele II/III
(§2.3–2.4, §10). See ``GENERATOR_REWORK.md`` for the migration plan.

Inviolable rules (spec §8.1):
1. ``generate()`` is PURE w.r.t. ``(profile, difficulty, rng)`` — the same seed
   reproduces the same exercise.
2. The mathematical result is VERIFIED with sympy before returning.
3. Output is always valid LaTeX (delimited ``$...$``).
4. No hard-coded answer strings — everything is computed.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Optional

import sympy as sp


class ExerciseGenerator(ABC):
    """Base class for single-statement exercises (Subiectul I, /generate)."""

    TOPIC_CODE: str = ""            # e.g. "derivatives"
    SUPPORTED_PROFILES: list = []   # e.g. ["M1", "M2"]
    MAX_RETRIES: int = 50           # re-generation attempts if validation fails

    def __init__(self, profile: str, difficulty: int, rng: random.Random):
        if profile not in self.SUPPORTED_PROFILES:
            raise ValueError(f"{self.TOPIC_CODE} nu suportă profilul {profile}")
        if difficulty not in (1, 2, 3):
            raise ValueError("difficulty trebuie să fie 1, 2 sau 3")
        self.profile = profile
        self.difficulty = difficulty
        self.rng = rng

    # --- subclass contract ---------------------------------------------------
    @abstractmethod
    def _generate_params(self) -> dict:
        """Generate the random parameters of the exercise."""
        ...

    @abstractmethod
    def _compute_answer(self, params: dict):
        """Compute the answer with sympy. Returns a sympy object/dict."""
        ...

    @abstractmethod
    def _validate(self, params: dict, answer) -> bool:
        """Return True iff the generated exercise is correct and reasonable."""
        ...

    @abstractmethod
    def _build_question(self, params: dict) -> str:
        """Build the LaTeX question string (Romanian, per spec §12)."""
        ...

    def _build_hint(self, params: dict) -> str:
        """Methodic hint (never the answer). Override as needed."""
        return ""

    def _build_steps(self, params: dict) -> list[str]:
        """Optional worked steps."""
        return []

    def _build_answer_latex(self, params: dict, answer) -> str:
        """LaTeX of the answer. Override when the answer is a custom string."""
        return self._format_answer(answer)

    # --- engine entry point --------------------------------------------------
    def generate(self) -> dict:
        for _ in range(self.MAX_RETRIES):
            try:
                params = self._generate_params()
                answer = self._compute_answer(params)
                if not self._validate(params, answer):
                    continue
                item = {
                    "topic": self.TOPIC_CODE,
                    "difficulty": self.difficulty,
                    "question_latex": self._build_question(params),
                    "answer_latex": self._build_answer_latex(params, answer),
                }
                hint = self._build_hint(params)
                if hint:
                    item["hint_latex"] = hint
                steps = self._build_steps(params)
                if steps:
                    item["steps_latex"] = steps
                from .validation import is_sane_value, item_is_clean
                if not is_sane_value(answer) or not item_is_clean(item):
                    continue
                return item
            except Exception:
                continue
        raise RuntimeError(
            f"Generatorul {self.TOPIC_CODE} nu a putut produce un exercițiu valid "
            f"în {self.MAX_RETRIES} tentative "
            f"(profile={self.profile}, difficulty={self.difficulty})"
        )

    @staticmethod
    def _format_answer(answer) -> str:
        from .latexconv import sympy_to_bac_latex  # lazy: module added in P4.1

        try:
            return sympy_to_bac_latex(answer)
        except Exception:
            return f"${sp.latex(answer)}$"


class TieredExerciseGenerator(ExerciseGenerator):
    """Single-item generator driven by a ``{difficulty: [subtype_fn]}`` map.

    Each ``subtype_fn(rng)`` returns a complete item dict (topic / question /
    answer / hint? / steps?) — typically built with ``_utils.make`` and verified
    inside the function. The tier is chosen by the requested difficulty with
    graceful fallback (``_utils.choose_subtype``). Subclasses set ``TOPIC_CODE`` /
    ``SUPPORTED_PROFILES`` and implement :meth:`_tiers` (may depend on profile,
    e.g. M3 = a reduced tier map).
    """

    def _tiers(self) -> dict:
        raise NotImplementedError

    # The ABC hooks below are unused — ``generate`` is overridden — but must exist.
    def _generate_params(self) -> dict:
        return {}

    def _compute_answer(self, params):
        return None

    def _validate(self, params, answer) -> bool:
        return True

    def _build_question(self, params) -> str:
        return ""

    def generate(self) -> dict:
        from ._utils import choose_subtype
        from .validation import item_is_clean

        for _ in range(self.MAX_RETRIES):
            try:
                item = choose_subtype(self.difficulty, self.rng, self._tiers())
                item.setdefault("topic", self.TOPIC_CODE)
                item.setdefault("difficulty", self.difficulty)
                if not item_is_clean(item):
                    continue
                return item
            except Exception:
                continue
        raise RuntimeError(
            f"Generatorul {self.TOPIC_CODE} nu a putut produce un exercițiu valid "
            f"în {self.MAX_RETRIES} tentative "
            f"(profile={self.profile}, difficulty={self.difficulty})"
        )


class ProblemGenerator(ABC):
    """Base class for a multi-part *problem* (Subiectul II/III).

    A problem fixes a single shared object (a parametrized matrix ``A(x)``, a
    function ``f``, a law of composition ``∗`` …) introduced by
    ``_build_statement`` and then poses several linked cerinte that escalate in
    difficulty (§10.3). Most problems have 3 sub-items (a, b, c); the M3 special
    cases (§5.4) have 6.

    Output shape (consumed by the simulate engine):
        {
          "number": int,
          "topic_primary": str,
          "statement_latex": str,          # "Se consideră ..."
          "sub_items": [
            {"label": "a", "points": 5, "difficulty": 1,
             "question_latex": str, "hint_latex": str,
             "answer_latex": str, "steps_latex": [str, ...]},
            ...
          ],
        }
    """

    TOPIC_CODE: str = ""
    SUPPORTED_PROFILES: list = []
    SUB_LABELS: tuple = ("a", "b", "c")   # ("a".."f") for M3 6-item format
    SUB_DIFFICULTIES: tuple = (1, 2, 3)   # per-label tier, escalating (§10.3)
    POINTS_PER_SUB: int = 5
    MAX_RETRIES: int = 50

    def __init__(self, profile: str, rng: random.Random):
        if profile not in self.SUPPORTED_PROFILES:
            raise ValueError(f"{self.TOPIC_CODE} nu suportă profilul {profile}")
        self.profile = profile
        self.rng = rng

    @abstractmethod
    def _generate_context(self) -> dict:
        """Build the shared object + everything the sub-items need (with sympy)."""
        ...

    @abstractmethod
    def _build_statement(self, ctx: dict) -> str:
        """LaTeX intro shared by all sub-items ("Se consideră ...")."""
        ...

    @abstractmethod
    def _build_sub_item(self, ctx: dict, label: str, difficulty: int) -> dict:
        """Return {question_latex, answer_latex, hint_latex?, steps_latex?} for one cerință.

        Must compute & verify its answer with sympy. May reuse earlier results
        stored on ``ctx`` (link b→a, c→a,b per §10.3).
        """
        ...

    def _validate_context(self, ctx: dict) -> bool:
        """Optional gate on the shared object (e.g. det≠0 when needed)."""
        return True

    def generate(self, number: int) -> dict:
        for _ in range(self.MAX_RETRIES):
            try:
                ctx = self._generate_context()
                if not self._validate_context(ctx):
                    continue
                from .validation import is_clean_latex, item_is_clean
                sub_items = []
                for label, tier in zip(self.SUB_LABELS, self._sub_tiers()):
                    sub = self._build_sub_item(ctx, label, tier)
                    sub.setdefault("hint_latex", "")
                    sub.setdefault("steps_latex", [])
                    sub.update(label=label, points=self.POINTS_PER_SUB, difficulty=tier)
                    sub_items.append(sub)
                statement = self._build_statement(ctx)
                if not is_clean_latex(statement) or not all(item_is_clean(s) for s in sub_items):
                    continue
                return {
                    "number": number,
                    "topic_primary": self.TOPIC_CODE,
                    "statement_latex": statement,
                    "sub_items": sub_items,
                }
            except Exception:
                continue
        raise RuntimeError(
            f"Problema {self.TOPIC_CODE} nu a putut fi generată în {self.MAX_RETRIES} "
            f"tentative (profile={self.profile})"
        )

    def _sub_tiers(self) -> tuple:
        """Per-label difficulty; pad/truncate to match SUB_LABELS length."""
        tiers = self.SUB_DIFFICULTIES
        if len(tiers) == len(self.SUB_LABELS):
            return tiers
        # M3 6-item: ramp 1,1,2,2,3,3 by default.
        ramp = [1, 1, 2, 2, 3, 3]
        return tuple(ramp[i] if i < len(ramp) else 3 for i in range(len(self.SUB_LABELS)))
