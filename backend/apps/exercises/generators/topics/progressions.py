"""Arithmetic & geometric progressions — single-item class (spec §7.3). M1/M2/M3.

Serves Subiectul I position 1 for M1/M2/M3 (the real papers open with a
progression term-finding item roughly as often as with complex numbers). The
dominant corpus phrasing is "Determinați termenul $a_k$ al progresiei aritmetice
$(a_n)$, cu $a_i = \\ldots$ și $a_j = \\ldots$" and the geometric analogue; a
"consecutive terms" proof also appears.

D1: n-th term / sum from the direct formula.
D2: recover a term from two given terms; geometric sum; consecutive-terms proof.
"""
from __future__ import annotations

from ..base import TieredExerciseGenerator
from .._utils import make


def _sub(sym: str, idx) -> str:
    return rf"{sym}_{{{idx}}}"


# --- direct formula ----------------------------------------------------------
def _d1_arith_term(rng):
    a1, r, n = rng.randint(1, 9), rng.randint(2, 5), rng.randint(5, 12)
    an = a1 + (n - 1) * r
    return make("progressions",
                rf"Într-o progresie aritmetică $a_1 = {a1}$ și rația $r = {r}$. "
                rf"Calculați $a_{{{n}}}$.", rf"$a_{{{n}}} = {an}$",
                hint_latex=r"$a_n = a_1 + (n-1)\,r$.")


def _d1_arith_sum(rng):
    a1, r, n = rng.randint(1, 9), rng.randint(2, 5), rng.randint(5, 10)
    an = a1 + (n - 1) * r
    s = n * (a1 + an) // 2
    return make("progressions",
                rf"Calculați suma primilor ${n}$ termeni ai progresiei aritmetice cu "
                rf"$a_1 = {a1}$ și rația $r = {r}$.", rf"$S_{{{n}}} = {s}$",
                hint_latex=r"$S_n = \dfrac{n\,(a_1 + a_n)}{2}$.")


def _d1_geom_term(rng):
    b1, q, n = rng.randint(1, 5), rng.randint(2, 3), rng.randint(4, 7)
    bn = b1 * q ** (n - 1)
    return make("progressions",
                rf"Într-o progresie geometrică $b_1 = {b1}$ și rația $q = {q}$. "
                rf"Calculați $b_{{{n}}}$.", rf"$b_{{{n}}} = {bn}$",
                hint_latex=r"$b_n = b_1\cdot q^{\,n-1}$.")


# --- recover a term from two given terms (the dominant pos-1 form) ------------
def _term_from_two_arith(rng):
    a1 = rng.randint(-3, 6)
    r = rng.choice([-3, -2, 2, 3, 4, 5])
    i, j, k = sorted(rng.sample([1, 2, 3, 4, 5, 6], 3))
    # present two of the three indices, ask for the remaining one
    show = rng.sample([i, j, k], 2)
    ask = [t for t in (i, j, k) if t not in show][0]
    term = lambda t: a1 + (t - 1) * r
    (i1, i2), va = sorted(show), None
    v1, v2, vk = term(i1), term(i2), term(ask)
    return make("progressions",
                rf"Determinați termenul $a_{{{ask}}}$ al progresiei aritmetice $(a_n)_{{n\geq 1}}$, "
                rf"cu ${_sub('a', i1)} = {v1}$ și ${_sub('a', i2)} = {v2}$.",
                rf"$a_{{{ask}}} = {vk}$",
                hint_latex=rf"Din ${_sub('a', i1)}$ și ${_sub('a', i2)}$ aflați rația "
                           rf"$r = \dfrac{{a_{{{i2}}} - a_{{{i1}}}}}{{{i2} - {i1}}}$, apoi "
                           rf"$a_{{{ask}}} = a_1 + ({ask}-1)r$.",
                steps_latex=[rf"$r = \dfrac{{{v2} - {v1}}}{{{i2 - i1}}} = {r}$",
                             rf"$a_{{{ask}}} = {vk}$"])


def _term_from_two_geom(rng):
    b1 = rng.choice([1, 2, 3, 5, 10])
    q = rng.choice([2, 3])
    i, j = sorted(rng.sample([1, 2, 3, 4, 5], 2))
    ask = rng.choice([t for t in [1, 2, 3, 4, 5] if t not in (i, j)] or [1])
    term = lambda t: b1 * q ** (t - 1)
    vi, vj, vk = term(i), term(j), term(ask)
    return make("progressions",
                rf"Determinați termenul $b_{{{ask}}}$ al progresiei geometrice $(b_n)_{{n\geq 1}}$, "
                rf"cu ${_sub('b', i)} = {vi}$ și ${_sub('b', j)} = {vj}$.",
                rf"$b_{{{ask}}} = {vk}$",
                hint_latex=rf"Din ${_sub('b', i)}$ și ${_sub('b', j)}$ aflați rația "
                           rf"$q$, apoi $b_{{{ask}}} = b_1\cdot q^{{{ask}-1}}$.",
                steps_latex=[rf"$q = {q}$", rf"$b_{{{ask}}} = {vk}$"])


def _d2_find_ratio(rng):
    a1, r, k = rng.randint(1, 6), rng.randint(2, 5), rng.randint(3, 6)
    ak = a1 + (k - 1) * r
    return make("progressions",
                rf"Într-o progresie aritmetică $a_1 = {a1}$ și $a_{{{k}}} = {ak}$. "
                rf"Determinați rația $r$.", rf"$r = {r}$",
                hint_latex=rf"$a_{{{k}}} = a_1 + ({k}-1)\,r$, de unde scoateți $r$.",
                steps_latex=[rf"${ak} = {a1} + {k-1}\,r \Rightarrow r = {r}$"])


def _d2_geom_sum(rng):
    b1, q, n = rng.randint(1, 4), rng.randint(2, 3), rng.randint(4, 6)
    s = b1 * (q**n - 1) // (q - 1)
    return make("progressions",
                rf"Calculați suma primilor ${n}$ termeni ai progresiei geometrice cu "
                rf"$b_1 = {b1}$ și rația $q = {q}$.", rf"$S_{{{n}}} = {s}$",
                hint_latex=r"$S_n = b_1\,\dfrac{q^n - 1}{q - 1}$.")


def _d2_consecutive(rng):
    # Show three numbers form consecutive terms of an AP or a GP (2b = a+c / b²=ac).
    if rng.random() < 0.5:
        a1, r = rng.randint(1, 6), rng.choice([2, 3, 4])
        t0 = rng.randint(1, 4)
        a, b, c = a1 + t0 * r, a1 + (t0 + 1) * r, a1 + (t0 + 2) * r
        assert 2 * b == a + c
        return make("progressions",
                    rf"Arătați că numerele ${a}$, ${b}$ și ${c}$ sunt termeni consecutivi ai "
                    rf"unei progresii aritmetice.",
                    rf"$2\cdot{b} = {a} + {c}$",
                    hint_latex=r"Trei numere sunt în progresie aritmetică dacă termenul din "
                               r"mijloc este media aritmetică a celorlalte: $2b = a + c$.")
    b1, q = rng.choice([1, 2, 3]), rng.choice([2, 3])
    t0 = rng.randint(1, 3)
    a, b, c = b1 * q ** t0, b1 * q ** (t0 + 1), b1 * q ** (t0 + 2)
    assert b * b == a * c
    return make("progressions",
                rf"Arătați că numerele ${a}$, ${b}$ și ${c}$ sunt termeni consecutivi ai unei "
                rf"progresii geometrice.",
                rf"${b}^2 = {a}\cdot{c}$",
                hint_latex=r"Trei numere sunt în progresie geometrică dacă $b^2 = a\cdot c$.")


def _d1_geom_sum(rng):
    b1, q, n = rng.choice([1, 2, 3]), rng.randint(2, 3), rng.randint(3, 5)
    S = b1 * (q ** n - 1) // (q - 1)
    return make("progressions",
                rf"Calculați suma primilor ${n}$ termeni ai progresiei geometrice cu "
                rf"$b_1 = {b1}$ și rația $q = {q}$.", rf"$S_{{{n}}} = {S}$",
                hint_latex=r"$S_n = b_1\dfrac{q^{\,n} - 1}{q - 1}$.")


def _d2_arith_find_n(rng):
    a1, r = rng.randint(1, 6), rng.randint(2, 5)
    n = rng.randint(6, 15)
    an = a1 + (n - 1) * r
    return make("progressions",
                rf"În progresia aritmetică cu $a_1 = {a1}$ și rația $r = {r}$, determinați "
                rf"rangul $n$ pentru care $a_n = {an}$.", rf"$n = {n}$",
                hint_latex=r"$a_n = a_1 + (n-1)r \Rightarrow n$.")


def _d2_three_consec_ap(rng):
    x, d = rng.randint(2, 9), rng.randint(1, 4)
    total = 3 * x
    return make("progressions",
                rf"Numerele $a - {d}$, $a$, $a + {d}$ sunt termeni consecutivi ai unei "
                rf"progresii aritmetice și au suma egală cu ${total}$. Determinați $a$.",
                rf"$a = {x}$",
                hint_latex=r"Suma a trei termeni consecutivi ai unei progresii "
                           r"aritmetice este $3a$.")


def _d3_arith_a1_from_sum(rng):
    r, n, a1 = rng.randint(2, 5), rng.randint(5, 10), rng.randint(1, 8)
    an = a1 + (n - 1) * r
    S = n * (a1 + an) // 2
    return make("progressions",
                rf"Suma primilor ${n}$ termeni ai unei progresii aritmetice cu rația "
                rf"$r = {r}$ este $S_{{{n}}} = {S}$. Determinați primul termen $a_1$.",
                rf"$a_1 = {a1}$",
                hint_latex=r"$S_n = \dfrac{n\,(2a_1 + (n-1)r)}{2}$.")


def _d3_geom_ratio_from_two(rng):
    b1, q = rng.choice([1, 2, 3]), rng.randint(2, 3)
    i, j = sorted(rng.sample([1, 2, 3, 4, 5], 2))
    bi, bj = b1 * q ** (i - 1), b1 * q ** (j - 1)
    return make("progressions",
                rf"Într-o progresie geometrică cu termeni pozitivi, $b_{{{i}}} = {bi}$ și "
                rf"$b_{{{j}}} = {bj}$. Determinați rația $q$.", rf"$q = {q}$",
                hint_latex=rf"$\dfrac{{b_{{{j}}}}}{{b_{{{i}}}}} = q^{{{j - i}}}$.")


_TIERS = {
    1: [_d1_arith_term, _d1_arith_sum, _d1_geom_term, _d1_geom_sum,
        _term_from_two_arith, _term_from_two_geom],
    2: [_term_from_two_arith, _term_from_two_geom, _d2_find_ratio,
        _d2_geom_sum, _d2_consecutive, _d2_arith_find_n, _d2_three_consec_ap],
    3: [_d2_find_ratio, _d2_consecutive, _d2_arith_find_n, _d2_three_consec_ap,
        _d3_arith_a1_from_sum, _d3_geom_ratio_from_two],
}


class ProgressionsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "progressions"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _tiers(self):
        return _TIERS
