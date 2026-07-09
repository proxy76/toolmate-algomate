"""Combinatorics & probability — single-item class (spec §7.3). M1/M2/M3.

This serves Subiectul I position 4 (``info-on-sub1.md`` §4), whose dominant
flavour is *probability over the two-digit numbers*, *counting subsets*, and (M3)
*practical percentage* — alongside the classic direct evaluations of
``n!``, ``C(n,k)``, ``A(n,k)``.

D1: direct evaluation + the position-4 probability/subset/percentage items.
D2: a small combinatorial equation, classical urn probability.
D3: probability built from combinations. M3 = D1 only (§5.2).
"""
from __future__ import annotations

from math import comb, factorial, gcd, lcm, perm

from ..base import TieredExerciseGenerator
from .._utils import make


def _d1_arrangements(rng):
    n, k = rng.randint(4, 8), rng.randint(2, 3)
    return make("combinatorics", rf"Calculează $A_{{{n}}}^{{{k}}}$.", rf"${perm(n, k)}$",
                hint_latex=r"$A_n^k = \dfrac{n!}{(n-k)!}$.")


def _d1_combinations(rng):
    n, k = rng.randint(4, 8), rng.randint(2, 3)
    return make("combinatorics", rf"Calculează $C_{{{n}}}^{{{k}}}$.", rf"${comb(n, k)}$",
                hint_latex=r"$C_n^k = \dfrac{n!}{k!\,(n-k)!}$.")


def _d1_factorial(rng):
    n = rng.randint(3, 6)
    return make("combinatorics", rf"Calculează ${n}!$.", rf"${factorial(n)}$",
                hint_latex=r"$n! = 1\cdot 2\cdot\ldots\cdot n$.")


def _d2_equation(rng):
    n = rng.randint(4, 8)
    val = comb(n, 2)
    return make("combinatorics", rf"Rezolvați în $\mathbb{{N}}$, $n \geq 2$: $C_n^2 = {val}$.",
                rf"$n = {n}$",
                hint_latex=r"$C_n^2 = \dfrac{n(n-1)}{2}$; rezolvați ecuația de gradul al II-lea.",
                steps_latex=[rf"$\dfrac{{n(n-1)}}{{2}} = {val} \Rightarrow "
                             rf"n(n-1) = {2*val} \Rightarrow n = {n}$"])


def _d2_arrangement_eq(rng):
    n = rng.randint(4, 9)
    val = perm(n, 2)                         # n(n-1)
    return make("combinatorics", rf"Rezolvați în $\mathbb{{N}}$, $n \geq 2$: $A_n^2 = {val}$.",
                rf"$n = {n}$",
                hint_latex=r"$A_n^2 = n(n-1)$; rezolvați ecuația de gradul al II-lea.",
                steps_latex=[rf"$n(n-1) = {val} \Rightarrow n^2 - n - {val} = 0 "
                             rf"\Rightarrow n = {n}$"])


def _d2_comb_eq3(rng):
    n = rng.randint(5, 9)
    val = comb(n, 3)
    return make("combinatorics", rf"Rezolvați în $\mathbb{{N}}$, $n \geq 3$: $C_n^3 = {val}$.",
                rf"$n = {n}$",
                hint_latex=r"$C_n^3 = \dfrac{n(n-1)(n-2)}{6}$.",
                steps_latex=[rf"$\dfrac{{n(n-1)(n-2)}}{{6}} = {val} \Rightarrow n = {n}$"])


def _d2_probability(rng):
    total = rng.randint(8, 16)
    favorable = rng.randint(2, total - 2)
    g = gcd(favorable, total)
    return make("combinatorics",
                rf"O urnă conține ${total}$ bile, dintre care ${favorable}$ roșii. Calculează "
                r"probabilitatea ca, extrăgând o bilă, aceasta să fie roșie.",
                rf"$P = \dfrac{{{favorable // g}}}{{{total // g}}}$",
                hint_latex=r"$P = \dfrac{\text{cazuri favorabile}}{\text{cazuri posibile}}$.")


def _d3_probability_comb(rng):
    n = rng.randint(5, 8)
    red = rng.randint(2, n - 2)
    total_ways, fav_ways = comb(n, 2), comb(red, 2)
    g = gcd(fav_ways, total_ways)
    return make("combinatorics",
                rf"Dintr-o urnă cu ${n}$ bile, dintre care ${red}$ roșii, se extrag simultan "
                r"$2$ bile. Calculează probabilitatea ca ambele să fie roșii.",
                rf"$P = \dfrac{{{fav_ways // g}}}{{{total_ways // g}}}$",
                hint_latex=r"$P = \dfrac{C_{red}^2}{C_n^2}$ — alegeri favorabile/posibile, "
                           r"fără ordine.",
                steps_latex=[rf"cazuri posibile $C_{{{n}}}^2 = {total_ways}$, "
                             rf"favorabile $C_{{{red}}}^2 = {fav_ways}$",
                             rf"$P = \dfrac{{{fav_ways}}}{{{total_ways}}} = "
                             rf"\dfrac{{{fav_ways // g}}}{{{total_ways // g}}}$"])


# --- Subiectul I position 4 (info-on-sub1 §4) --------------------------------
# Sample space for two-digit naturals is 90 (10..99); three-digit is 900 (100..999).
_TWO_DIGIT = range(10, 100)
_THREE_DIGIT = range(100, 1000)


def _digits(n):
    return [int(c) for c in str(n)]


def _prob_item(question, fav, total, hint):
    """Assemble a probability item with the reduced fraction (fav/total)."""
    g = gcd(fav, total)
    return make("combinatorics", question, rf"$P = \dfrac{{{fav // g}}}{{{total // g}}}$",
                hint_latex=hint)


# The corpus pos-4 flavour: probability over the 2-/3-digit numbers with a
# divisibility / digit / parity / product-of-digits condition. Exact counts.
def _p4_3digit_not_mult(rng):
    d = rng.choice([3, 5])
    fav = sum(1 for n in _THREE_DIGIT if n % d != 0)
    return _prob_item(
        rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        rf"de trei cifre, acesta să nu fie multiplu de ${d}$.",
        fav, 900,
        rf"Numerele de trei cifre sunt $900$; scădeți multiplii lui ${d}$ din $[100, 999]$.")


def _p4_3digit_prime_digits(rng):
    primes = {2, 3, 5, 7}
    fav = sum(1 for n in _THREE_DIGIT
              if set(_digits(n)) <= primes and len(set(_digits(n))) == 3)
    return _prob_item(
        r"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        r"de trei cifre, acesta să aibă cifrele numere prime distincte.",
        fav, 900,
        r"Cifrele prime sunt $\{2,3,5,7\}$; numărați aranjamentele de $3$ cifre distincte.")


def _p4_3digit_prod_digits(rng):
    P = rng.choice([6, 8, 12])
    def prod(n):
        p = 1
        for d in _digits(n):
            p *= d
        return p
    fav = sum(1 for n in _THREE_DIGIT if prod(n) == P)
    return _prob_item(
        rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        rf"de trei cifre, acesta să aibă produsul cifrelor egal cu ${P}$.",
        fav, 900,
        rf"Numărați numerele de trei cifre cu produsul cifrelor egal cu ${P}$.")


def _p4_2digit_sum_div3(rng):
    fav = sum(1 for n in _TWO_DIGIT if sum(_digits(n)) % 3 == 0)
    return _prob_item(
        r"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        r"de două cifre, acesta să aibă suma cifrelor divizibilă cu $3$.",
        fav, 90,
        r"Numărați numerele de două cifre a căror sumă a cifrelor este multiplu de $3$.")


def _p4_2digit_div9(rng):
    fav = sum(1 for n in _TWO_DIGIT if n % 9 == 0)
    return _prob_item(
        r"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        r"de două cifre, acesta să fie divizibil cu $9$.",
        fav, 90,
        r"Multiplii de două cifre ai lui $9$ sunt $18, 27, \ldots, 99$.")


def _p4_2digit_digits_bound(rng):
    if rng.random() < 0.5:
        k = rng.choice([2, 3, 4])
        fav = sum(1 for n in _TWO_DIGIT if all(d <= k for d in _digits(n)))
        return _prob_item(
            rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
            rf"de două cifre, acesta să aibă ambele cifre mai mici sau egale cu ${k}$.",
            fav, 90,
            rf"Cifra zecilor $\in\{{1,\ldots,{k}\}}$, cifra unităților $\in\{{0,\ldots,{k}\}}$.")
    k = rng.choice([6, 7, 8])
    fav = sum(1 for n in _TWO_DIGIT if all(d >= k for d in _digits(n)))
    return _prob_item(
        rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        rf"de două cifre, acesta să aibă ambele cifre mai mari sau egale cu ${k}$.",
        fav, 90,
        rf"Ambele cifre $\in\{{{k},\ldots,9\}}$.")


def _p4_2digit_distinct_odd(rng):
    fav = sum(1 for n in _TWO_DIGIT
              if all(d % 2 == 1 for d in _digits(n)) and len(set(_digits(n))) == 2)
    return _prob_item(
        r"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
        r"de două cifre, acesta să aibă cifrele impare și distincte.",
        fav, 90,
        r"Cifrele impare sunt $\{1,3,5,7,9\}$; alegeți două distincte, cu ordine.")


def _p4_count_from_set(rng):
    """Câte numere de două cifre distincte (eventual impare) se formează dintr-o mulțime."""
    setvals = sorted(rng.sample([1, 2, 3, 4, 5, 7, 9], 5))
    odd = rng.random() < 0.5
    units_pool = [d for d in setvals if (d % 2 == 1)] if odd else setvals
    fav = sum(1 for t in setvals for u in units_pool if u != t)
    setstr = ",\\ ".join(str(v) for v in setvals)
    cond = "impare, " if odd else ""
    return make("combinatorics",
                rf"Determinați câte numere naturale {cond}de două cifre distincte se pot forma "
                rf"cu elementele mulțimii $A = \{{{setstr}\}}$.",
                rf"${fav}$",
                hint_latex=r"Alegeți cifra unităților (cu paritatea cerută), apoi cifra "
                           r"zecilor distinctă de ea.")


def _p4_subsets_at_most(rng):
    """Numărul submulțimilor cu cel mult 2 elemente ale unei mulțimi cu n elemente."""
    n = rng.choice([10, 12, 5, 6])
    nonempty = rng.random() < 0.5
    val = comb(n, 1) + comb(n, 2) + (0 if nonempty else 1)
    which = "nevide " if nonempty else ""
    return make("combinatorics",
                rf"Determinați numărul submulțimilor {which}cu cel mult $2$ elemente ale unei "
                rf"mulțimi cu ${n}$ elemente.",
                rf"${val}$",
                hint_latex=(rf"Adunați submulțimile cu $1$ și cu $2$ elemente"
                            + ("" if nonempty else r" și mulțimea vidă") + r"."))


def _p4_two_digit_div(rng):
    """Probability that a two-digit number is divisible by a and by b (§4.1 C4.a)."""
    a, b = rng.sample([2, 3, 4, 5, 6], 2)
    m = lcm(a, b)
    fav = sum(1 for n in _TWO_DIGIT if n % m == 0)
    g = gcd(fav, 90)
    return make("combinatorics",
                rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
                rf"de două cifre, acesta să fie divizibil cu ${a}$ și cu ${b}$.",
                rf"$P = \dfrac{{{fav // g}}}{{{90 // g}}}$",
                hint_latex=rf"Numerele cerute sunt multiplii lui ${m}$ din intervalul $[10, 99]$ "
                           rf"(${fav}$ numere), din cele $90$ posibile.")


def _p4_two_digit_units(rng):
    """Probability that the units digit has a given parity (§4.1 C4.b)."""
    parity = rng.choice(["pară", "impară"])
    return make("combinatorics",
                rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
                rf"de două cifre, acesta să aibă cifra unităților {parity}.",
                r"$P = \dfrac{1}{2}$",
                hint_latex=r"Din cele $90$ de numere, exact jumătate au cifra unităților de "
                           r"paritatea cerută.")


def _p4_two_digit_divisor(rng):
    """Probability that a two-digit number is a divisor of A (§4.1 C4.d)."""
    A = rng.choice([24, 36, 48, 60, 72, 90])
    favs = [n for n in _TWO_DIGIT if A % n == 0]
    fav = len(favs)
    g = gcd(fav, 90)
    return make("combinatorics",
                rf"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale "
                rf"de două cifre, acesta să fie divizor al numărului ${A}$.",
                rf"$P = \dfrac{{{fav // g}}}{{{90 // g}}}$",
                hint_latex=rf"Divizorii de două cifre ai lui ${A}$ sunt $\{{{', '.join(map(str, favs))}\}}$ "
                           rf"(${fav}$ numere), din cele $90$ posibile.")


def _p4_subset_contains(rng):
    """Number of k-subsets of A that contain a fixed element (§4.2 T4.sub1)."""
    size = rng.choice([5, 6])
    setvals = sorted(rng.sample(range(1, 10), size))
    k = rng.randint(2, 3)
    e = rng.choice(setvals)
    val = comb(size - 1, k - 1)
    setstr = ",\\ ".join(str(v) for v in setvals)
    return make("combinatorics",
                rf"Determinați numărul submulțimilor cu ${k}$ elemente ale mulțimii "
                rf"$A = \{{{setstr}\}}$ care îl conțin pe ${e}$.",
                rf"${val}$",
                hint_latex=rf"Fixați elementul ${e}$ și alegeți restul de ${k - 1}$ elemente "
                           rf"dintre cele ${size - 1}$ rămase: $C_{{{size - 1}}}^{{{k - 1}}} = {val}$.")


def _p4_percentage(rng):
    """Practical percentage — recover the price before a change (§4.4, M3 main)."""
    p = rng.choice([10, 20, 25, 50])
    base = rng.randint(2, 9) * 100
    if rng.random() < 0.5:
        d = base * p // 100
        return make("combinatorics",
                    rf"După o scumpire cu ${p}\%$, prețul unui obiect a crescut cu ${d}$ de lei. "
                    rf"Determinați prețul obiectului înainte de scumpire.",
                    rf"$x = {base}$ lei",
                    hint_latex=rf"Creșterea reprezintă ${p}\%$ din prețul inițial: "
                               rf"$\dfrac{{{p}}}{{100}}\cdot x = {d}$.")
    c = base - base * p // 100
    return make("combinatorics",
                rf"După o ieftinire cu ${p}\%$, un produs costă ${c}$ lei. Determinați prețul "
                rf"produsului înainte de ieftinire.",
                rf"$x = {base}$ lei",
                hint_latex=rf"Prețul redus reprezintă ${100 - p}\%$ din cel inițial: "
                           rf"$\dfrac{{{100 - p}}}{{100}}\cdot x = {c}$.")


# The authentic Subiectul I pos-4 pool — probability over 2-/3-digit numbers,
# subset & number counting. This is the real content at every difficulty (the
# corpus has no "urn with balls" problems), so it fills tiers 1–3. Combinatorial
# equations (Aₙ²/Cₙ²/Cₙ³) appear rarely in the real papers → a light d2 presence.
_POS4 = [
    _p4_two_digit_div, _p4_two_digit_units, _p4_two_digit_divisor,
    _p4_2digit_sum_div3, _p4_2digit_div9, _p4_2digit_digits_bound,
    _p4_2digit_distinct_odd,
    _p4_3digit_not_mult, _p4_3digit_prime_digits, _p4_3digit_prod_digits,
    _p4_subset_contains, _p4_subsets_at_most, _p4_count_from_set, _p4_percentage,
]


# --- M2 (tehnologic) pos-4: probability over a small EXPLICIT set + percentage --
def _p4_set_multiples(rng):
    """A = {k, 2k, …, 9k}; probability that an element is divisible by d."""
    k = rng.choice([10, 5, 3, 4])
    elems = [k * i for i in range(1, 10)]
    d = rng.choice([2, 3, 20, 15, k * 2])
    fav = [e for e in elems if e % d == 0]
    if not fav or len(fav) == len(elems):
        raise ValueError("degenerate")
    setstr = ",".join(str(e) for e in elems)
    return _prob_item(
        rf"Determinați probabilitatea ca, alegând un număr din mulțimea "
        rf"$A = \{{{setstr}\}}$, acesta să fie divizibil cu ${d}$.",
        len(fav), len(elems),
        rf"Numărați elementele lui $A$ divizibile cu ${d}$ (${len(fav)}$), din cele "
        rf"${len(elems)}$ posibile.")


def _p4_set_range_ineq(rng):
    """A = {a, a+1, …, b}; probability that n satisfies a linear inequality."""
    a, b = rng.choice([(1, 23), (0, 9), (1, 20), (10, 30), (0, 9)])
    total = b - a + 1
    c = rng.choice([1, 2, 3])
    v = rng.randint(a * c, b * c)
    op = rng.choice([">", "\\geq", "<", "\\leq"])
    def ok(n):
        cn = c * n
        return {">": cn > v, "\\geq": cn >= v, "<": cn < v, "\\leq": cn <= v}[op]
    fav = [n for n in range(a, b + 1) if ok(n)]
    if not fav or len(fav) == total:
        raise ValueError("degenerate")
    setrepr = (rf"\{{{a}, {a+1}, {a+2}, \ldots, {b}\}}" if b - a > 4
               else r"\{" + ",".join(str(i) for i in range(a, b + 1)) + r"\}")
    cc = "" if c == 1 else f"{c}"
    return _prob_item(
        rf"Determinați probabilitatea ca, alegând un număr $n$ din mulțimea "
        rf"$A = {setrepr}$, acesta să verifice inegalitatea ${cc}n {op} {v}$.",
        len(fav), total,
        rf"Rezolvați inegalitatea în mulțimea $A$ (${len(fav)}$ soluții din ${total}$).")


# M_tehnologic / M_șt-nat pos-4: probability over a small explicit set, a practical
# percentage, and the 2-digit-number probability family (all difficulty-1 clean).
_POS4_M2 = [_p4_set_multiples, _p4_set_range_ineq, _p4_percentage,
            _p4_two_digit_div, _p4_two_digit_units, _p4_two_digit_divisor,
            _p4_2digit_sum_div3, _p4_2digit_div9]

_TIERS = {
    1: [_d1_arrangements, _d1_combinations, _d1_factorial] + _POS4,
    2: _POS4 + [_d2_equation, _d2_arrangement_eq, _d2_comb_eq3],
    3: _POS4 + [_d2_comb_eq3],
}


class CombinatoricsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "combinatorics"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _tiers(self):
        if self.profile == "pedagogic":
            return {1: _TIERS[1]}
        if self.profile == "tehnologic":
            # M_tehnologic pos-4: probability over a small explicit set + percentage.
            return {1: _POS4_M2, 2: _POS4_M2}
        if self.profile == "stiintele-naturii":
            # M_șt-nat pos-4 blends the digit-condition probability/counting family
            # with the explicit-small-set / percentage forms.
            return {1: _POS4_M2 + _TIERS[1], 2: _TIERS[2], 3: _TIERS[3]}
        return _TIERS
