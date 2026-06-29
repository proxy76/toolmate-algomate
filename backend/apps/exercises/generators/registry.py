"""Canonical registry data — profiles, topic restrictions, labels, exam rules.

Single source of truth derived from ``generator.md`` §3–5, §8.2, §10.2. The
``CLASS_REGISTRY`` fills up as topics are ported to classes (see
GENERATOR_REWORK.md §7). Until a topic is ported, the legacy function registry in
``generators/__init__.py`` still serves it.
"""
from __future__ import annotations

# topic_code -> human label (Romanian). Spec §12 terminology.
TOPIC_LABELS: dict[str, str] = {
    "powers": "Puteri și radicali",
    "logarithms": "Logaritmi",
    "complex": "Numere complexe",
    "polynomials": "Polinoame",
    "matrices": "Matrice și determinanți",
    "systems": "Sisteme de ecuații liniare",
    "algebraic_structures": "Structuri algebrice",
    "sequences": "Șiruri",
    "limits": "Limite de funcții",
    "derivatives": "Derivate",
    "integrals": "Primitive și integrale",
    "geometry": "Geometrie plană și analitică",
    "trigonometry": "Trigonometrie",
    "combinatorics": "Combinatorică și probabilități",
    "progressions": "Progresii",
    "statistics": "Statistică",
}

# Allowed topics per profile (spec §8.2 PROFILE_TOPICS, verbatim).
PROFILE_TOPICS: dict[str, list[str]] = {
    "M1": [
        "powers", "logarithms", "complex", "polynomials",
        "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics",
    ],
    "M2": [
        "powers", "logarithms", "complex",            # complex: algebraic only
        "polynomials", "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics", "progressions",
    ],
    "M3": [
        "powers", "logarithms",
        "matrices",                 # 2×2 only
        "algebraic_structures",     # basic
        "geometry", "trigonometry", "combinatorics",
        "progressions", "statistics",
        "derivatives",              # polynomials only
    ],
}

# Per-profile capability flags the generators must honor (spec §3–5, §13.1).
PROFILE_CAPS: dict[str, dict] = {
    "M1": {"matrix_size": (2, 3), "complex": "full", "derivatives": "full"},
    "M2": {"matrix_size": (2, 3), "complex": "algebraic_only", "derivatives": "full"},
    "M3": {"matrix_size": (2,), "complex": None, "derivatives": "poly_only"},
}

# Exam composition per profile (spec §10.2). Slot topics that offer a choice are
# given as tuples; the engine picks one per-seed. M3's II/III are single-topic
# 6-item formats (spec §5.4).
SIMULATION_RULES: dict[str, dict] = {
    "M1": {
        "subiect_I": [
            ("logarithms", "complex"),
            ("derivatives",),
            ("logarithms", "powers", "complex"),
            ("combinatorics",),
            ("geometry",),
            ("trigonometry",),
        ],
        "subiect_II": {"format": "two_problems",
                       "problems": [("matrices",), ("polynomials", "algebraic_structures")]},
        "subiect_III": {"format": "two_problems",
                        "problems": [("derivatives",), ("integrals",)]},
    },
    "M2": {
        "subiect_I": [
            ("progressions", "logarithms"),
            ("derivatives",),
            ("logarithms", "powers"),
            ("combinatorics",),
            ("geometry",),
            ("trigonometry",),
        ],
        "subiect_II": {"format": "two_problems",
                       "problems": [("matrices",), ("algebraic_structures",)]},
        "subiect_III": {"format": "two_problems",
                        "problems": [("derivatives",), ("integrals",)]},
    },
    "M3": {
        "subiect_I": [
            ("progressions",),
            ("derivatives",),
            ("logarithms",),
            ("combinatorics", "statistics"),
            ("geometry",),
            ("geometry",),
        ],
        "subiect_II": {"format": "single_topic_6_items", "topic": "algebraic_structures"},
        "subiect_III": {"format": "single_topic_6_items", "topic": "matrices"},
    },
}


# topic_code -> ExerciseGenerator subclass (single-item). Filled during porting.
CLASS_REGISTRY: dict[str, type] = {}

# topic_code -> ProblemGenerator subclass (multi sub-item). Filled during porting.
PROBLEM_REGISTRY: dict[str, type] = {}


def _register():
    """Import ported topic classes and populate the registries.

    Wrapped in try/except per topic so a not-yet-ported topic never breaks import
    (the legacy function registry covers it meanwhile).
    """
    from importlib import import_module

    single = {
        "derivatives": ("topics.derivatives", "DerivativesGenerator"),
        "geometry": ("topics.geometry", "GeometryGenerator"),
        "logarithms": ("topics.logarithms", "LogarithmsGenerator"),
        "sequences": ("topics.sequences", "SequencesGenerator"),
        "statistics": ("topics.statistics", "StatisticsGenerator"),
        "systems": ("topics.systems", "SystemsGenerator"),
        "powers": ("topics.powers", "PowersGenerator"),
        "complex": ("topics.complex", "ComplexNumbersGenerator"),
        "trigonometry": ("topics.trigonometry", "TrigonometryGenerator"),
        "combinatorics": ("topics.combinatorics", "CombinatoricsGenerator"),
        "progressions": ("topics.progressions", "ProgressionsGenerator"),
        "limits": ("topics.limits", "LimitsGenerator"),
    }
    problem = {
        "matrices": ("topics.matrices", "MatricesProblem"),
        "algebraic_structures": ("topics.algebraic_structures", "AlgebraicStructuresProblem"),
        "derivatives": ("topics.derivatives", "DerivativesStudyProblem"),
        "integrals": ("topics.integrals", "IntegralsProblem"),
        "polynomials": ("topics.polynomials", "PolynomialsProblem"),
    }
    for code, (mod, cls) in single.items():
        try:
            m = import_module(f"{__package__}.{mod}")
            CLASS_REGISTRY[code] = getattr(m, cls)
        except Exception:
            pass
    for code, (mod, cls) in problem.items():
        try:
            m = import_module(f"{__package__}.{mod}")
            PROBLEM_REGISTRY[code] = getattr(m, cls)
        except Exception:
            pass


_register()
