# Subiectul I — Task Phrasing Bank (Positions 1–6)
## Instructions for the generation agent

> **What this file is**: A bank of *task expressions* (phrasings) for each of the six items of SUBIECTUL I, extracted from 10 years of official BAC papers (2015–2025) across M1, M2, M3. Each position has a fixed **topic role** and a set of **interchangeable phrasings**. Phrasings contain **placeholders** (`{a}`, `{n}`, `{P}`, …) and **never literal numbers**. The agent fills placeholders with randomly chosen numbers.

---

## 0. How the agent must use this bank

For each item position `i` (1..6) and a given `profile`:

1. **Pick the topic** assigned to `(profile, i)` — it is fixed (see each section).
2. **Randomly select one phrasing template** from that position's list (`rng.choice(templates)`).
3. **Randomly choose the numbers** for every placeholder, within the per-template parameter ranges.
4. **Compute the answer with `sympy`** — never hardcode it. If the random numbers produce an ugly answer (non-integer where an integer is expected, empty solution set, undefined expression), **reject and re-roll** (loop up to `MAX_RETRIES`).
5. **Emit the LaTeX** for `question_latex`, plus `hint_latex` and `answer_latex`.

```python
def generate_subiect_I_item(profile, position, rng):
    topic = POSITION_TOPIC[profile][position]
    for _ in range(MAX_RETRIES):
        template = rng.choice(PHRASINGS[profile][position])
        params   = roll_params(template, rng)          # random numbers in range
        answer   = compute_answer_sympy(template, params)
        if not is_clean(template, params, answer):
            continue                                    # re-roll
        return render(template, params, answer)
    raise GenerationError(profile, position)
```

**Cleanliness rules (apply to every position):**
- The "din oficiu" calculator-free constraint means answers must be computable by hand. Reject any roll whose answer is not a small integer, a simple fraction, or a short radical/`ln` expression.
- Reject rolls that make a denominator zero, a log argument ≤ 0, or a radicand < 0.
- Reject rolls where the "show that" target value would be non-integer unless the template explicitly allows a radical/fraction target.

**Placeholder convention used throughout:**
`{a} {b} {c} {m} {n} {k} {p} {q} {r}` = integer parameters · `{base}` = log/exp base · `{xv} {yv}` = point coordinates · `{val}` = the show-that target (computed, not rolled) · `{P} {Q}` = point names · `{set}` = an explicit finite set.

---

## 1. POSITION 1

| Profile | Topic role |
|---|---|
| M1 | Complex numbers (algebraic form) — occasionally powers/radicals or logarithms |
| M2 | Progressions (arithmetic/geometric) — occasionally powers |
| M3 | Progressions OR powers/radicals |

### 1.1 M1 — phrasings

```
T1.M1.a  "Arătați că numărul $z = ({a} - {b}i)({a} + {b}i)$ este natural, unde $i^2 = -1$."
           → answer: a²+b²  (always natural). pick a,b ∈ [1,6].

T1.M1.b  "Se consideră numărul complex $z = {a} + {b}i$. Arătați că $z\\big(\\bar{z} - {c}i\\big) = {val}$."
           → compute z·(conj(z) - c·i) with sympy; require Im result == 0 → choose c = b (then result = a²+b² + 0i... verify). Re-roll if not clean.

T1.M1.c  "Se consideră numerele complexe $z_1 = {a} - {b}i$ și $z_2 = {c} + {d}i$. Arătați că $z_1 + i z_2 = {val}$."
           → val = sympy(z1 + I*z2); require val purely real & integer; else re-roll.

T1.M1.d  "Determinați numărul complex $z$, știind că ${p} z - \\bar{z} = {a} {sign} {b}i$, unde $\\bar{z}$ este conjugatul lui $z$."
           → solve for z = x+iy with sympy linear system. require integer x,y.

T1.M1.e  "Arătați că ${k}\\lg{100} + \\lg{{a}} + \\lg{{b}} = {val}$, unde ${a}\\cdot{b} = 10$."
           → pick (a,b) ∈ {(2,5),(5,2)}; val = 2k+1.

T1.M1.f  "Arătați că $\\sqrt{{a}} \\cdot \\big(\\sqrt{{a}} - \\sqrt{{b}}\\big) + \\sqrt{{a}\\cdot{b}} = {val}$."
           → val = sympy.simplify(...); require integer.
```

### 1.2 M2 / M3 — phrasings (progressions + powers)

```
T1.PG.a  "Determinați termenul ${idx}$ al progresiei aritmetice $(a_n)_{n\\ge 1}$, în care $a_{i} = {av}$ și $a_{j} = {bv}$."
           → r = (bv-av)/(j-i); a_idx = av + (idx-i)*r; require r integer & a_idx integer.

T1.PG.b  "Determinați al treilea termen al progresiei geometrice $(b_n)_{n\\ge 1}$, știind că $b_1 = {a}$ și $b_2 = {b}$."
           → q = b/a; b3 = a*q²; require q rational-clean & b3 integer.

T1.PG.c  "Se consideră progresia geometrică $(b_n)_{n\\ge 1}$ cu $b_1 = {a}$ și $b_2 = {b}$. Calculați $b_{idx}$."
           → as above for arbitrary idx ∈ [3,5].

T1.PW.a  "Arătați că ${a}\\sqrt{{r}} + \\sqrt{{b}} - \\sqrt{{c}} = {val}$."
           → val = sympy.simplify; require integer. (M3 frequent.)

T1.PW.b  "Arătați că $\\sqrt[{k}]{{a}} + \\sqrt{{b}} - {c} = {val}$."
           → pick a a perfect k-th power, b a perfect square; val integer.
```

---

## 2. POSITION 2

**Topic role (all profiles): Functions** — point on graph, composition, functional identity, parabola vertex.

```
T2.a  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$. Determinați numărul real ${par}$ pentru care $f({par}) = {val}$."
        → solve a·par+b = val. (M3/M2 most common; a,b small.)

T2.b  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$, unde ${b}$ este număr real.
        Determinați numărul real ${b}$, știind că punctul $M({xv}, {yv})$ aparține graficului funcției $f$."
        → solve a·xv + b = yv for b. require b integer.

T2.c  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$.
        Determinați numărul real $a$ pentru care $(f\\circ f)({xv}) = {val}$."
        → (f∘f)(xv) = a(a·xv+b)+b; solve for a; require integer/clean.

T2.d  "Se consideră funcțiile $f,g:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$ și $g(x) = {c}x + {d}$.
        Calculați $(f\\circ g)({xv})$."
        → compute; any integer result acceptable.

T2.e  "Se consideră funcțiile $f,g:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$ și $g(x) = {c}x + {d}$.
        Determinați numărul real ${par}$ pentru care $f({par}) = g({par})$."
        → solve a·par+b = c·par+d; require a≠c and integer solution.

T2.f  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$.
        Arătați că $f({k}x) - {k}f(x) = {val}$, pentru orice număr real $x$."
        → val = a·k·x + b - k(a·x+b) = b(1-k); require integer; identity holds ∀x.

T2.g  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = x^2 + {a}x + {b}$.
        Determinați numerele reale $a$, știind că vârful parabolei asociate funcției $f$ se află pe axa $Ox$."
        → condition: discriminant = 0 → a² - 4b = 0. (M1/M2 only.)

T2.h  "Se consideră funcția $f:\\mathbb{R}\\to\\mathbb{R}$, $f(x) = {a}x + {b}$.
        Determinați numărul real ${par}$ pentru care $f({par}) + f({k}{par}) = {val}$."
        → solve linear; require integer.
```

> **M3 restriction**: use only `T2.a, T2.b, T2.d, T2.e` (linear/affine functions). Never the parabola-vertex form `T2.g`.

---

## 3. POSITION 3

**Topic role (all profiles): Equation in ℝ.** The wrapper is invariant; only the equation type rotates.

**Invariant wrapper:**
```
"Rezolvați în mulțimea numerelor reale ecuația $<EQ>$."
```

**Equation bodies `<EQ>` (pick one, fill numbers, solve with `sympy.solve`, require clean roots):**

```
E3.exp1   "{base}^{{x}} + {base}^{{-x}} = {val}"          → substitution t={base}^x; require t roots positive & x clean.
E3.exp2   "{base}^{{2x}} - {a}\\cdot{base}^{{x}} + {b} = 0" → quadratic in t; require integer logs.
E3.exp3   "{a}^{{x}} \\cdot {b}^{{x}} = {c}^{{x+ {k}}}"     → solve exponent equation.
E3.exp4   "{a}^{{2x}} \\cdot {b}^{{x}} = {val}"             → linear in x after log.
E3.log1   "\\log_{{{base}}}(x^2 + {a}x) = \\log_{{{base}}}({val})"   → x²+ax-val=0; require integer roots & domain ok.
E3.log2   "\\log_{{{base}}}({a}x + {b}) = {k}"             → a·x+b = base^k; require domain ok.
E3.log3   "\\log_{{{base}}}(x + {a}) + \\log_{{{base}}}(x + {b}) = \\log_{{{base}}}({val})"  → require both args >0 at solution.
E3.irr1   "\\sqrt{{{a}x + {b}}} = x - {c}"                 → square; check extraneous; keep real roots in domain.
E3.irr2   "\\sqrt{{{a} + {b}x}} = {c}"                     → linear after squaring.
E3.abs1   "|{a}x - {b}| = {c}"                             → two branches; require integer roots.
```

> **M3 restriction**: use only `E3.exp4, E3.log1, E3.log2, E3.irr2, E3.abs1` (single-step, base ∈ {2,3,10}).

---

## 4. POSITION 4

**Topic role:**
- M1/M2: probability on a finite numeric set, or counting subsets.
- M3: probability on a small set, OR a practical percentage problem.

### 4.1 Probability over 2-digit numbers (M1/M2 main pattern)

**Wrapper:**
```
"Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale de două cifre, acesta să <COND>."
```
Sample space = 90 (numbers 10..99). Compute favourable count with a predicate, probability = count/90, reduce fraction.

**Conditions `<COND>` (pick one, fill numbers):**
```
C4.a  "fie divizibil cu ${a}$ și cu ${b}$"                → multiples of lcm(a,b) in [10,99].
C4.b  "aibă cifra unităților {parity}"                   → parity ∈ {pară, impară}.
C4.c  "aibă cifra zecilor divizor al numărului ${a}$"    → tens digit | a.
C4.d  "fie divizor al numărului ${a}$"                   → divisors of a within [10,99]; pick a with several.
C4.e  "verifice $n + {a}$ este multiplu de ${b}$"        → (n+a) mod b == 0.
C4.f  "aibă cifrele distincte și {parity}"               → both digits parity & distinct.
```

### 4.2 Counting subsets (M1/M2 alternative)

```
T4.sub1  "Determinați numărul submulțimilor cu ${k}$ elemente ale mulțimii $A = {set}$, care îl conțin pe ${e}$."
           → C(|A|-1, k-1). set explicit small (5–7 elements).
T4.sub2  "Determinați câte submulțimi cu ${k}$ elemente, {restrict}, are mulțimea $A = {set}$."
           → restrict e.g. "ambele numere pare" → C(#even, k).
```

### 4.3 Probability over 1-digit set (M2/M3)

```
T4.dig1  "Determinați probabilitatea ca, alegând un număr $n$ din mulțimea numerelor naturale de o cifră, numărul $n$ să fie divizor al numărului ${a}$."
T4.dig2  "Determinați probabilitatea ca, alegând un număr $n$ din mulțimea $A = \\{0,1,\\dots,9\\}$, numărul ${a}n + {b}$ să aparțină mulțimii $A$."
```

### 4.4 Practical percentage (M3 main pattern)

```
T4.pct1  "După o scumpire cu ${p}\\%$, prețul unui obiect a crescut cu ${d}$ de lei. Determinați prețul obiectului înainte de scumpire."
           → initial = d / (p/100). require integer; pick p ∈ {10,20,25,50}, choose d as multiple.
T4.pct2  "După o ieftinire cu ${p}\\%$, un produs costă ${c}$ lei. Determinați prețul produsului înainte de ieftinire."
           → initial = c / (1 - p/100). require integer.
```

---

## 5. POSITION 5

**Topic role: Analytic geometry in the $xOy$ plane** — line through point (parallel/perpendicular), point on a line, midpoint/collinearity, vectors.

**Wrapper preamble (always):**
```
"În reperul cartezian $xOy$ se consideră <POINTS>."
```
where `<POINTS>` declares 1–4 named points with **rolled integer coordinates** in `[-6, 6]`.

**Tasks (pick one):**
```
T5.a  "Determinați ecuația dreptei $d$ care trece prin punctul ${P}$ și este paralelă cu dreapta ${Q}{R}$."
        → slope = slope(QR); line through P. require defined slope (xQ≠xR).

T5.b  "Determinați ecuația dreptei $d$ care trece prin punctul ${P}$ și este perpendiculară pe dreapta ${Q}{R}$."
        → slope = -1/slope(QR); require slope(QR) ≠ 0 and defined.

T5.c  "Determinați numărul real ${a}$, știind că punctul ${P}({a},{a})$ aparține dreptei $d$ de ecuație $y = {m}x + {n}$."
        → solve a = m·a + n.

T5.d  "Determinați numerele reale ${a}$ și ${b}$, știind că segmentele ${P}{Q}$ și ${R}{S}$ au același mijloc,
        unde ${S}({a},{b})$."
        → midpoint(P,Q)=midpoint(R,S) → solve a,b.

T5.e  "Determinați coordonatele punctului ${P}$ pentru care $\\vec{{A}{P}} = \\vec{O{B}}$."
        → P = A + (B - O).

T5.f  "Demonstrați că punctele ${P}$, ${Q}$ și mijlocul segmentului ${R}{S}$ sunt coliniare."
        → require det collinearity = 0; construct coords so it holds, else re-roll.

T5.g  "Arătați că triunghiul ${P}{Q}{R}$ este dreptunghic în ${P}$."
        → require vec(PQ)·vec(PR)=0 by construction; else re-roll.

T5.h  "Demonstrați că ${A}{M} = {B}{M}$, unde punctul $M$ este mijlocul segmentului ${P}{Q}$."  (M3 frequent)
        → midpoint M; require |AM|=|BM| by construction.
```

> **M3 restriction**: prefer `T5.c, T5.e, T5.h` and simple midpoint/distance tasks; avoid perpendicular-slope algebra unless coordinates keep it clean.

---

## 6. POSITION 6

**Topic role: Trigonometry / triangle geometry.**
- M1/M2: right-triangle with trig data, OR a trig identity to prove.
- M3: right triangle with Pythagoras / basic trig ratio.

### 6.1 Right-triangle tasks (all profiles)

**Wrapper:**
```
"Se consideră triunghiul ${ABC}$, dreptunghic în ${vertex}$, <DATA>. <ASK>"
```

```
T6.a  DATA "cu aria egală cu ${S}$ și $\\widehat{{B}} = \\dfrac{\\pi}{{k}}$"   ASK "Arătați că ${AB} = {val}$."
        → use area + angle to derive side; require {val} clean (integer or simple radical).

T6.b  DATA "cu ${AB} = {a}$ și $\\operatorname{tg}{B} = {t}$"   ASK "Arătați că ${BC} = {val}$."
        → AC = AB·tgB; BC = √(AB²+AC²); require {val} = integer or k√m.

T6.c  DATA "cu ${AB} = {a}$ și ${AC} = {b}$"   ASK "Arătați că $\\sin{C} = {val}$."   (M3 frequent)
        → BC = √(a²+b²); sinC = AB/BC; require {val} a clean fraction.

T6.d  DATA "cu ${AB} = {a}$ și ${BC} = {c}$"   ASK "Arătați că perimetrul triunghiului ${ABC}$ este egal cu ${val}$."  (M3)
        → AC = √(c²-a²) (require Pythagorean triple); perimeter = a + AC + c.

T6.e  DATA "cu ${BC} = {a}$ și măsura unghiului ${C}$ de două ori mai mare decât măsura unghiului ${B}$"
        ASK "Determinați lungimea laturii ${AC}$ a triunghiului ${ABC}$."   (M3)
        → angles 30/60; AC = BC·sin(B). require clean.

T6.f  DATA "isoscel, cu ${AB} = {a}$ și $\\cos{A} = {cv}$"   ASK "Arătați că aria triunghiului ${ABC}$ este egală cu ${val}$."  (M1/M2)
        → area from two sides & included angle; pick cosA ∈ {0, 1/2, -1/2}.

T6.g  DATA "dreptunghic în ${vertex}$ și $\\sin{B} = \\cos{B}$"   ASK "Arătați că triunghiul ${ABC}$ este isoscel."  (M1/M2)
        → no numbers; pure proof template.

T6.h  DATA "dreptunghic în ${vertex}$"   ASK "Arătați că $\\operatorname{tg}{B} = \\dfrac{1}{\\operatorname{tg}{A}}$."  (M1/M2)
        → identity template; no numbers.
```

### 6.2 Trig-identity tasks (M1/M2)

```
T6.id1  "Arătați că $\\sin\\!\\left(x + \\dfrac{\\pi}{{k}}\\right) - \\cos\\!\\left(x - \\dfrac{\\pi}{{k}}\\right) = {val}$, pentru orice număr real $x$."
          → expand with sum formulas; require identity (val=0 typically).
T6.id2  "Arătați că $\\sin(a-b)\\sin(a+b) = \\sin^2 a - \\sin^2 b$, pentru orice numere reale $a$ și $b$."
          → fixed identity; no numbers.
T6.id3  "Se consideră expresia $E(x) = {expr}$. Arătați că $E\\!\\left(\\dfrac{\\pi}{{k}}\\right) = {val}$."
          → evaluate E at the angle with sympy; require clean val.
```

---

## 7. Position → Topic resolver (for the agent)

```python
POSITION_TOPIC = {
    "M1": {1: "complex|powers|log", 2: "functions", 3: "equation",
           4: "probability|subsets", 5: "analytic_geometry", 6: "trig|triangle"},
    "M2": {1: "progressions|powers", 2: "functions", 3: "equation",
           4: "probability", 5: "analytic_geometry", 6: "trig|triangle"},
    "M3": {1: "progressions|powers", 2: "functions_linear", 3: "equation_simple",
           4: "probability|percentage", 5: "geometry_simple", 6: "triangle_pythagoras"},
}
```

For positions where a profile maps to several candidate topics (e.g. M1 position 1 = complex/powers/log), the agent rolls the topic too:
```python
topic_pool = POSITION_TOPIC[profile][position].split("|")
topic = rng.choice(topic_pool)   # then pick a phrasing whose topic matches
```

**Weighting** (optional, to match real-exam frequency): in M1 position 1, weight `complex` at ~0.7, `powers` 0.2, `log` 0.1 — complex numbers dominate position 1 historically.

---

## 8. Number-rolling rules per placeholder

```python
PARAM_RANGES = {
    # integers
    "a": (1, 6), "b": (1, 6), "c": (1, 6), "m": (-5, 5), "n": (-5, 5),
    "k": (2, 4), "p": (10, 50), "d": (10, 90),
    # coordinates
    "xv": (-6, 6), "yv": (-6, 6),
    # bases
    "base": [2, 3, 10],
    # angle denominators
    "angle_k": [3, 4, 6],
    # cos special values
    "cos_special": [0, "1/2", "-1/2"],
    # parity word
    "parity": ["pară", "impară"],
}
```

**Hard constraints enforced after rolling, before accepting:**
1. Position 1 (complex): require the show-that target to be a real integer.
2. Position 2: require linear solutions to be integers; for `T2.g` require `a² = 4b` solvable in integers.
3. Position 3: run `sympy.solve`; require ≥1 real root, all roots rational or simple radicals, domain valid.
4. Position 4: require probability fraction to reduce to small denominator; percentage answers integer lei.
5. Position 5: coordinates that keep slopes defined and answers integer-valued; for "prove" tasks construct coords so the property holds, then re-roll if degenerate (collinear triangle, coincident points).
6. Position 6: require the show-that length/area/ratio to be an integer, a simple fraction, or `k√m` with small `k,m`; for Pythagoras tasks roll from known triples `(3,4,5),(6,8,10),(5,12,13),(8,15,17),(7,24,25)`.

---

## 9. Worked example (M1, position 3, template E3.exp2)

```
template = E3.exp2:  "{base}^{2x} - {a}·{base}^{x} + {b} = 0"
roll:     base=2, a=5, b=4
build EQ: 2^{2x} - 5·2^{x} + 4 = 0
sympy:    t=2^x → t²-5t+4=0 → t∈{1,4} → x∈{0,2}      (both clean → accept)
question_latex: "Rezolvați în mulțimea numerelor reale ecuația $2^{2x} - 5\\cdot 2^{x} + 4 = 0$."
hint_latex:     "Notați $t = 2^{x}$, $t>0$, și rezolvați ecuația de gradul al II-lea."
answer_latex:   "$x \\in \\{0, 2\\}$"
```

If instead the roll were `base=2, a=3, b=5`: `t²-3t+5=0` has no real roots → **reject, re-roll**.

---

## 10. Summary table — what each position generates

| Pos | M1 | M2 | M3 | Invariant wrapper present? |
|----|----|----|----|----|
| 1 | complex (alg.) | progressions | progressions/powers | no |
| 2 | functions (any) | functions | functions (linear only) | no |
| 3 | equation (exp/log/irr) | equation (exp/log/irr) | equation (simple) | **yes** ("Rezolvați în mulțimea numerelor reale ecuația…") |
| 4 | probability/subsets | probability | probability/percentage | partial ("Calculați probabilitatea ca, alegând…") |
| 5 | analytic geometry | analytic geometry | geometry (simple) | **yes** ("În reperul cartezian xOy se consideră…") |
| 6 | trig/right triangle | trig/right triangle | right triangle (Pythagoras) | partial ("Se consideră triunghiul ABC, dreptunghic în…") |

The agent should treat the **wrapper as fixed text** and only vary the inner mathematical content, exactly as the official papers do — this is what produces 1:1 stylistic similarity while keeping every item unique through randomized numbers.