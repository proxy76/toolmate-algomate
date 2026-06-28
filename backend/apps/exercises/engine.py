"""Top-level orchestration over the registry of generators."""
from __future__ import annotations

import hashlib
import random
import secrets
from typing import Iterable

from .generators import REGISTRY, SUPPORTED_TOPICS_PER_PROFILE, TOPIC_LABELS


class GenerationError(ValueError):
    pass


def supported_topics(profile: str) -> list[dict]:
    topics = SUPPORTED_TOPICS_PER_PROFILE.get(profile, [])
    return [{"code": t, "label": TOPIC_LABELS.get(t, t)} for t in topics]


def all_topic_labels() -> dict[str, str]:
    return dict(TOPIC_LABELS)


def _seed_to_int(seed: str) -> int:
    return int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big")


def generate_set(
    *,
    profile: str,
    topics: Iterable[str],
    difficulty: int,
    count: int,
    seed: str | None = None,
) -> dict:
    if profile not in {"M1", "M2", "M3"}:
        raise GenerationError("Profil invalid. Folosește M1, M2 sau M3.")
    if difficulty not in (1, 2, 3):
        raise GenerationError("Dificultatea trebuie să fie 1, 2 sau 3.")
    if not (1 <= count <= 50):
        raise GenerationError("Numărul de exerciții trebuie să fie între 1 și 50.")

    topics = [t.strip() for t in topics if t and t.strip()]
    if not topics:
        raise GenerationError("Selectează cel puțin un capitol.")

    pairs = [(t, profile) for t in topics if (t, profile) in REGISTRY]
    if not pairs:
        raise GenerationError(
            f"Niciun generator disponibil pentru capitolele alese la profilul {profile}."
        )

    seed = seed or secrets.token_hex(8)
    rng = random.Random(_seed_to_int(seed))

    items: list[dict] = []
    for i in range(count):
        topic, _ = pairs[i % len(pairs)]
        gen = REGISTRY[(topic, profile)]
        item = gen(difficulty, rng)
        item.setdefault("difficulty", difficulty)
        item["id"] = f"{topic[:3]}_{i + 1:03d}_{seed[:6]}"
        item["index"] = i + 1
        items.append(item)

    rng.shuffle(items)
    for i, it in enumerate(items, 1):
        it["index"] = i
    return {"seed": seed, "items": items}


def simulate_bac(*, profile: str, difficulty: int = 2, seed: str | None = None) -> dict:
    """Generate a BAC-shaped paper: SUBIECTUL I (6), II (2), III (2).

    The exam's difficulty is *structural*, so each subiect is generated at its
    own fixed tier — I is one-step recall, II direct method application, III
    multi-step analysis — regardless of the request's ``difficulty`` field
    (kept only for backwards compatibility).
    """
    seed = seed or secrets.token_hex(8)
    base_rng = random.Random(_seed_to_int(seed))

    topic_pool = [t for t in SUPPORTED_TOPICS_PER_PROFILE.get(profile, [])]
    if not topic_pool:
        raise GenerationError(f"Profilul {profile} nu este încă suportat pentru simulare.")

    def pick_n(n: int, tier: int, prefer: list[str]) -> list[dict]:
        result = []
        for i in range(n):
            wanted = [t for t in prefer if t in topic_pool] or topic_pool
            topic = wanted[base_rng.randrange(len(wanted))]
            item = REGISTRY[(topic, profile)](tier, base_rng)
            item.setdefault("difficulty", tier)
            item["index"] = i + 1
            item["id"] = f"sim_{topic[:3]}_{i + 1}_{seed[:6]}"
            result.append(item)
        return result

    return {
        "seed": seed,
        "subiectul_I": pick_n(
            6, 1, ["powers", "logarithms", "trigonometry", "complex", "progressions", "combinatorics"]
        ),
        "subiectul_II": pick_n(2, 2, ["matrices", "polynomials"]),
        "subiectul_III": pick_n(2, 3, ["derivatives", "integrals", "limits"]),
    }
