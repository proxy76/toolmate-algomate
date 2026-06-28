"""New generation engine (spec §8.3, §10).

Bridges the migration: a topic is served by its ported class
(``CLASS_REGISTRY`` / ``PROBLEM_REGISTRY``) when available, otherwise by the
legacy function registry. Reproducibility uses per-item derived seeds
``f"{seed}_{i}_{topic}"`` (§8.3, §13.2); a set's items vary in difficulty via
``compute_item_difficulty`` (§8.4).

Transitional notes (see GENERATOR_REWORK.md):
- Subiect II/III problems use a real ``ProblemGenerator`` where ported
  (matrices, algebraic_structures — so **M3 II/III are fully linked 6-item
  problems**); other problem slots use an adapter that assembles a/b/c from
  single-item generators until those topics get problem-ported (Phase 2).
- Slots whose topic has no generator yet (geometry, statistics, …) fall back to
  another profile-appropriate topic so the paper is always complete.
"""
from __future__ import annotations

import hashlib
import random
import secrets

from . import REGISTRY as LEGACY_REGISTRY  # (topic, profile) -> callable
from .difficulty import compute_item_difficulty
from .registry import (
    CLASS_REGISTRY,
    PROBLEM_REGISTRY,
    PROFILE_TOPICS,
    SIMULATION_RULES,
    TOPIC_LABELS,
)


class GenerationError(ValueError):
    pass


# --- topic catalogue (for the menus) -----------------------------------------
def all_topic_labels() -> dict[str, str]:
    return dict(TOPIC_LABELS)


def supported_topics(profile: str) -> list[dict]:
    """Topics a user can actually pick (have a working generator) for ``profile``."""
    return [{"code": t, "label": TOPIC_LABELS.get(t, t)} for t in _available_topics(profile)]


# --- seeding -----------------------------------------------------------------
def _seed_to_int(seed: str) -> int:
    return int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big")


def _rng(seed: str, *parts) -> random.Random:
    return random.Random(_seed_to_int(seed + "_" + "_".join(str(p) for p in parts)))


# --- generator availability + single-item production -------------------------
def _has_generator(topic: str, profile: str) -> bool:
    cls = CLASS_REGISTRY.get(topic)
    if cls and profile in cls.SUPPORTED_PROFILES:
        return True
    return (topic, profile) in LEGACY_REGISTRY


def _make_single(topic: str, profile: str, difficulty: int, rng: random.Random) -> dict:
    cls = CLASS_REGISTRY.get(topic)
    if cls and profile in cls.SUPPORTED_PROFILES:
        return cls(profile, difficulty, rng).generate()
    fn = LEGACY_REGISTRY.get((topic, profile))
    if fn is None:
        raise GenerationError(f"Niciun generator pentru {topic}/{profile}.")
    item = fn(difficulty, rng)
    item.setdefault("difficulty", difficulty)
    item.setdefault("topic", topic)
    return item


def _available_topics(profile: str) -> list[str]:
    return [t for t in PROFILE_TOPICS.get(profile, []) if _has_generator(t, profile)]


# --- /generate ---------------------------------------------------------------
def generate_exercises(
    *, profile: str, topics, difficulty: int, count: int, seed: str | None = None
) -> dict:
    if profile not in PROFILE_TOPICS:
        raise GenerationError("Profil invalid. Folosește M1, M2 sau M3.")
    if difficulty not in (1, 2, 3):
        raise GenerationError("Dificultatea trebuie să fie 1, 2 sau 3.")
    if not (1 <= count <= 50):
        raise GenerationError("Numărul de exerciții trebuie să fie între 1 și 50.")

    allowed = set(PROFILE_TOPICS[profile])
    valid = [t for t in (topics or []) if t in allowed and _has_generator(t, profile)]
    if not valid:
        valid = _available_topics(profile)
    if not valid:
        raise GenerationError(
            f"Niciun generator disponibil pentru capitolele alese la profilul {profile}."
        )

    seed = seed or secrets.token_hex(8)
    order = list(valid)
    _rng(seed, "order").shuffle(order)

    items: list[dict] = []
    seen: set[str] = set()
    for i in range(count):
        topic = order[i % len(order)]
        item_diff = compute_item_difficulty(difficulty, i)
        item = None
        for salt in range(6):  # variety guard (§13.2): avoid duplicate questions
            cand = _make_single(topic, profile, item_diff, _rng(seed, i, topic, salt))
            if cand["question_latex"] not in seen:
                item = cand
                break
            item = cand
        seen.add(item["question_latex"])
        item["difficulty"] = item_diff
        item["id"] = f"{topic[:3]}_{seed}_{i:02d}"
        item["index"] = i + 1
        items.append(item)

    return {"seed": seed, "items": items}


# --- /simulate ---------------------------------------------------------------
def _make_problem(topic, profile, rng, *, six: bool, number: int) -> dict:
    cls = PROBLEM_REGISTRY.get(topic)
    if cls and profile in cls.SUPPORTED_PROFILES:
        kwargs = {"six_items": True} if six else {}
        return cls(profile, rng, **kwargs).generate(number)
    return _adapter_problem(topic, profile, rng, six=six, number=number)


def _adapter_problem(topic, profile, rng, *, six: bool, number: int) -> dict:
    """Transitional: assemble a/b/c (or six) from single-item generators."""
    labels = ("a", "b", "c", "d", "e", "f")[: (6 if six else 3)]
    tiers = (1, 1, 2, 2, 3, 3)[: len(labels)] if six else (1, 2, 3)
    use_topic = topic if _has_generator(topic, profile) else (
        _available_topics(profile)[0] if _available_topics(profile) else topic
    )
    subs = []
    for j, (label, tier) in enumerate(zip(labels, tiers)):
        it = _make_single(use_topic, profile, tier, random.Random(rng.random()))
        subs.append({
            "label": label,
            "points": 5,
            "difficulty": tier,
            "question_latex": it["question_latex"],
            "answer_latex": it["answer_latex"],
            "hint_latex": it.get("hint_latex", ""),
            "steps_latex": it.get("steps_latex", []),
        })
    return {
        "number": number,
        "topic_primary": use_topic,
        "statement_latex": "",
        "sub_items": subs,
    }


def _pick_topic(choices, profile, rng) -> str:
    """Choose a slot topic, falling back to an available one if unbuilt."""
    pool = [c for c in choices if _has_generator(c, profile)]
    if pool:
        return pool[rng.randrange(len(pool))]
    avail = _available_topics(profile)
    return avail[rng.randrange(len(avail))] if avail else choices[0]


def _build_subiect_problems(spec, profile, seed, tag) -> dict:
    if spec["format"] == "single_topic_6_items":
        topic = spec["topic"]
        prob = _make_problem(topic, profile, _rng(seed, tag, topic), six=True, number=1)
        return {"points": 6 * 5, "problems": [prob]}

    problems = []
    for pnum, choices in enumerate(spec["problems"], start=1):
        rng = _rng(seed, tag, pnum)
        topic = _pick_topic(choices, profile, rng)
        problems.append(_make_problem(topic, profile, rng, six=False, number=pnum))
    return {"points": len(problems) * 3 * 5, "problems": problems}


def generate_full_simulation(*, profile: str, seed: str | None = None) -> dict:
    if profile not in SIMULATION_RULES:
        raise GenerationError(f"Profilul {profile} nu este suportat pentru simulare.")
    seed = seed or secrets.token_hex(8)
    rules = SIMULATION_RULES[profile]

    # Subiectul I — 6 independent items, exam-easy (tier 1).
    si_items = []
    for idx, choices in enumerate(rules["subiect_I"]):
        rng = _rng(seed, "I", idx)
        topic = _pick_topic(choices, profile, rng)
        item = _make_single(topic, profile, 1, rng)
        item.update(number=idx + 1, points=5)
        item["id"] = f"sim_{topic[:3]}_{idx + 1}_{seed[:6]}"
        si_items.append(item)

    subiect_I = {"points": 30, "items": si_items}
    subiect_II = _build_subiect_problems(rules["subiect_II"], profile, seed, "II")
    subiect_III = _build_subiect_problems(rules["subiect_III"], profile, seed, "III")

    return {
        "profile": profile,
        "seed": seed,
        "total_points": 100,
        "officiu_points": 10,
        "subiect_I": subiect_I,
        "subiect_II": subiect_II,
        "subiect_III": subiect_III,
    }
