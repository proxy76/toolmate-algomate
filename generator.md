# Algomate — Ghid Complet pentru Motorul de Generare BAC
## Documentație pentru agentul de implementare (Claude Code)

> **Scop**: Acest document este referința canonică pentru implementarea unui motor de generare de exerciții de matematică pentru bacalaureatul românesc. Acoperă toate cele trei profile (M1, M2, M3), structura oficială a subiectelor, tipurile de cerințe, parametrii de dificultate, logica de aleatorism și arhitectura internă a proiectului Algomate.

---

## Cuprins

1. [Contextul proiectului și arhitectura existentă](#1-contextul-proiectului-și-arhitectura-existentă)
2. [Structura oficială a examenului BAC](#2-structura-oficială-a-examenului-bac)
3. [Profilul M1 — M_mate-info](#3-profilul-m1--m_mate-info)
4. [Profilul M2 — M_șt-nat](#4-profilul-m2--m_șt-nat)
5. [Profilul M3 — M_pedagogic și M_tehnologic](#5-profilul-m3--m_pedagogic-și-m_tehnologic)
6. [Taxonomia completă a cerințelor](#6-taxonomia-completă-a-cerințelor)
7. [Sistemul de dificultate și aleatorism](#7-sistemul-de-dificultate-și-aleatorism)
8. [Arhitectura motorului de generare](#8-arhitectura-motorului-de-generare)
9. [Specificații per topic și per subtip](#9-specificații-per-topic-și-per-subtip)
10. [Modul Simulare BAC complet](#10-modul-simulare-bac-complet)
11. [Validare sympy și corectitudine matematică](#11-validare-sympy-și-corectitudine-matematică)
12. [Formatare LaTeX și convenții de output](#12-formatare-latex-și-convenții-de-output)
13. [Anti-patternuri și greșeli de evitat](#13-anti-patternuri-și-greșeli-de-evitat)
14. [Checklist de implementare](#14-checklist-de-implementare)

---

## 1. Contextul proiectului și arhitectura existentă

### 1.1 Stack-ul existent

Proiectul folosește:
- **Backend**: Django 5 + Django REST Framework + PostgreSQL + `sympy` pentru verificare simbolică
- **Frontend**: React 18 + TypeScript + Vite + Tailwind + KaTeX
- **Auth**: JWT cu simplejwt (access token 15 min, refresh 7 zile)

### 1.2 Layout-ul aplicației backend

```
backend/
  algomate/
    settings/
      base.py
      development.py
      production.py
  apps/
    accounts/         # user, JWT, register/login/me
    exercises/        # MOTORUL — generatoare, sesiuni, API
    blog/             # postări publice
    core/             # contact, health check
```

### 1.3 Endpoint-ul central de generare

```
POST /api/v1/exercises/generate/

{
  "profile":     "M1" | "M2" | "M3",
  "topics":      ["derivatives", "matrices", ...],
  "difficulty":  1 | 2 | 3,
  "count":       1..50,
  "seed":        "string-optional"   // reproducibilitate
}
```

Răspuns:
```json
{
  "items": [
    {
      "id":              "der_a1b2",
      "topic":           "derivatives",
      "difficulty":      2,
      "question_latex":  "...",
      "hint_latex":      "...",
      "answer_latex":    "...",
      "steps_latex":     ["...", "..."]
    }
  ],
  "seed": "abc123"
}
```

### 1.4 Endpoint Simulare BAC

```
POST /api/v1/exercises/simulate/

{
  "profile":  "M1" | "M2" | "M3",
  "seed":     "string-optional"
}
```

Răspuns: o structură cu `subiect_I`, `subiect_II`, `subiect_III`, fiecare cu itemii corespunzători, replicând exact formatul oficial al examenului.

### 1.5 Locul generatoarelor în cod

Toate generatoarele trăiesc în `apps/exercises/`. Structura recomandată:

```
apps/exercises/
  generators/
    __init__.py
    registry.py           # mapa topic_code -> generator class
    base.py               # clasa abstractă ExerciseGenerator
    difficulty.py         # parametri per difficulty level
    topics/
      powers.py
      logarithms.py
      complex_numbers.py
      polynomials.py
      matrices.py
      systems.py
      algebraic_structures.py
      sequences.py
      limits.py
      derivatives.py
      integrals.py
      geometry.py
      trigonometry.py
      combinatorics.py
      statistics.py
      progressions.py
  views.py                # GenerateView, SimulateView
  serializers.py
  models.py               # Session, SavedExercise
```

---

## 2. Structura oficială a examenului BAC

### 2.1 Regulile de bază (comune tuturor profilelor)

- Toate subiectele sunt obligatorii.
- Se acordă **10 puncte din oficiu**.
- Timp de lucru: **3 ore** (calculatorul este interzis).
- Punctajul: SUBIECTUL I (30p) + SUBIECTUL II (30p) + SUBIECTUL III (30p) + 10p oficiu = 100p.
- Nota = punctaj total / 10.

### 2.2 SUBIECTUL I — Structura invariantă (toate profilele)

SUBIECTUL I conține **6 itemi**, fiecare valorând **5 puncte**.

Caracteristici observate consistent în examenele 2015–2025:

- Fiecare item este **independent** — nu depinde de rezolvarea altui item.
- Itemii sunt de tip **demonstrație simplă** ("Arătați că...") sau **determinare directă** ("Determinați...").
- Cerințele sunt în general **one-step sau two-step** — nu necesită mai mult de 2-3 pași de calcul.
- Acoperă topic-uri diverse: algebră, analiză, geometrie, probabilități — nu există un topic unic per subiect.
- Dificultatea itemilor din Subiectul I este mereu **medium-low** (echivalent difficulty=1 sau 2 în sistemul platformei).

**Distribuția tipică a topic-urilor în Subiectul I** (observată în 100+ variante):

| Poziție (1–6) | Topic frecvent M1           | Topic frecvent M2              | Topic frecvent M3             |
|---------------|-----------------------------|-------------------------------|-------------------------------|
| 1             | logaritmi / complexe        | progresii / logaritmi          | progresii / funcții simple    |
| 2             | funcții simple (compoziție) | funcții simple                 | funcții simple                |
| 3             | ecuații exp/log/iraționale  | ecuații exp/log                | ecuații log/simple            |
| 4             | combinatorică/probabilități | combinatorică/probabilități    | probleme practice (procente)  |
| 5             | geometrie analitică (dreapta/punct) | geometrie analitică   | geometrie plană               |
| 6             | trigonometrie/geometrie trg | trigonometrie                  | geometrie triunghi Pitagora   |

### 2.3 SUBIECTUL II — Structura invariantă

SUBIECTUL II conține **2 probleme** (numerotate 1 și 2), fiecare cu **3 sub-puncte (a, b, c)**, fiecare sub-punct valorând **5 puncte**.

Caracteristici:

- Problemele au o structură **progresivă de dificultate**: (a) este ușor/mediu, (b) mediu, (c) greu.
- Sub-punctele sunt adesea legate — (b) poate folosi rezultatul din (a), (c) extinde (b).
- **Problema 1** din Subiectul II: în general **matrice/sisteme** (M1/M2) sau **lege de compoziție** (M3).
- **Problema 2** din Subiectul II: variabil — **polinoame** (M1), **lege de compoziție/structuri algebrice** (M1/M2), **matrice** (M3).

### 2.4 SUBIECTUL III — Structura invariantă

SUBIECTUL III conține **2 probleme** (numerotate 1 și 2), fiecare cu **3 sub-puncte (a, b, c)**, fiecare valorând **5 puncte**.

Caracteristici:

- Aproape exclusiv **analiză matematică** (funcții, derivate, integrale).
- **Problema 1**: studiu de funcție (derivabilitate, monotonie, extrema, asimptote, bijectivitate sau inegalități).
- **Problema 2**: integrale definite, calcul de arie, inegalități integrale.
- Sub-punctele sunt puternic legate — (b) și (c) depind frecvent de (a).
- Dificultatea crește semnificativ de la (a) la (c).

---

## 3. Profilul M1 — M_mate-info

### 3.1 Identitate și context

- **Filiera**: Teoretică, profilul real, specializarea matematică-informatică; vocațională, profilul militar, specializarea matematică-informatică.
- **Nivel de dificultate intrinsecă**: Cel mai ridicat dintre cele 3 profile.
- **Ore de matematică**: 4+ ore/săptămână pe parcursul liceului.
- **Publicul elevilor**: Pregătiți pentru facultăți tehnice, informatică, matematică.

### 3.2 Curriculum complet M1

#### Algebră (clasa IX–X)
- Mulțimi, relații, operații cu mulțimi, principiul includerii-excluderii
- Numere reale: proprietăți, modul, parte întreagă `⌊x⌋`
- Puteri și radicali: simplificare, raționalizare
- Logaritmi: proprietăți, schimbare de bază, ecuații și inecuații logaritmice
- Funcții exponențiale și logaritmice: grafice, ecuații, inecuații
- **Numere complexe**: forma algebrică `z = a + bi`, modulul `|z|`, conjugatul `z̄`, forma trigonometrică `r(cosθ + i·sinθ)`, rădăcini ale unității
- Polinoame: operații, teorema lui Bézout, schema lui Horner, teorema fundamentală a algebrei, rădăcini raționale, divizibilitate, descompunere în factori

#### Algebră (clasa XI–XII)
- Matrice: operații (+, ×, scalar), determinant (2×2, 3×3), rangul matricei, matricea inversă (metoda adjunctelor / algoritmul Gauss–Jordan)
- Sisteme de ecuații liniare: metoda Cramer, eliminare Gauss
- Structuri algebrice: monoid, grup, inel, corp — proprietăți (`(Zn, +)`, `(Zn*, ·)`, `Mn(R)`, inelul polinoamelor)
- Legi de compoziție definite pe mulțimi: asociativitate, comutativitate, element neutru, element simetric/invers

#### Geometrie și trigonometrie
- Trigonometrie: funcțiile sin, cos, tan, cot; formule de adunare, dublă măsură, produse în sumă
- Teorema sinusurilor, teorema cosinusului, formule pentru aria triunghiului
- Vectori în plan: operații, produs scalar, coliniaritate
- Geometrie analitică: dreapta (ecuații, distanțe, unghiuri, unghi, dreapta mediană/bisectoare), cercul (ecuație, tangente)

#### Analiză matematică (clasa XI)
- Șiruri: convergență, mărginire, monotonie, teorema lui Weierstrass, criteriul Cesàro-Stolz
- Limite de funcții: calcul direct, forme nedeterminate, asimptote (orizontale, verticale, oblice)
- Continuitate: definiție, proprietăți, teorema lui Cauchy, teorema Bolzano
- Derivabilitate: definiție, reguli de calcul (produs, câț, compusă), derivatele funcțiilor elementare
- Aplicații ale derivatei: teorema lui Fermat, Rolle, Lagrange, Cauchy; monotonie, extrema, convexitate, coarda, tangenta; regula L'Hôpital

#### Analiză matematică (clasa XII)
- Primitive: metode (tabel, integrare prin părți, substituție), primitive ale funcțiilor uzuale
- Integrala Riemann: definiție, proprietăți, formula Leibniz–Newton
- Aplicații: aria suprafeței plane, volumul solidului de revoluție, lungimea arcului

### 3.3 Structura tipică a unui subiect M1

**SUBIECTUL I** (6 itemi × 5p):
1. Calcul cu logaritmi sau numere complexe (ex: demonstrație algebrică simplă)
2. Funcție elementară — compoziție sau inversă (determinare valori)
3. Ecuație în R — exponențială, logaritmică sau irațională
4. Combinatorică sau probabilități discrete
5. Geometrie analitică — dreapta sau punct (determinare coordonate, paralelism)
6. Triunghi dreptunghic sau triunghi isoscel — demonstrație cu teorema sinusurilor sau a cosinusului

**SUBIECTUL II**:
- Problema 1: Matrice parametrizată `A(x)` — determinant, produs matriceal, sisteme
- Problema 2: Polinom `f(X)` parametrizat — rădăcini, împărțire polinomială (Horner/Bézout), relațiile lui Viète

**SUBIECTUL III**:
- Problema 1: Funcție `f: R → R` sau `f: (a,b) → R` — derivata, monotonie, bijectivitate, inegalitate
- Problema 2: Integrală definită — calcul, inegalitate integrală, arie

### 3.4 Tipare de cerințe specifice M1 (observate în examenele 2015–2025)

#### Cerințe standard M1 — SUBIECTUL I:
- `"Arătați că [expresie_logaritmică] = [valoare]."` — simplificare directă
- `"Determinați numărul real a pentru care f(a) = f(3a)."` — rezolvare ecuație simplă
- `"Rezolvați în R ecuația [exp sau log sau irațională]."` — soluție unică sau două soluții
- `"Calculați probabilitatea că..."` — spațiu finit, eveniment simplu
- `"Determinați coordonatele punctului C pentru care [condiție geometrică]."` — condiție de paralelism sau mijloc
- `"Arătați că BC = [valoare]."` sau `"Arătați că aria = [valoare]."` — triunghi cu date trigonometrice

#### Cerințe standard M1 — SUBIECTUL II (Matrice):
- `(a) Arătați că det(A(x₀)) = [valoare]."` — calcul determinant 3×3 cu parametru fixat
- `(b) Arătați că A(x)·A(y) = A(x+y)."` sau `"Determinați x pentru care A(x)·M = M·A(x)."` — proprietăți de matrice
- `(c) Determinați numerele naturale n pentru care [inegalitate cu det]."` — condiție mai complexă

#### Cerințe standard M1 — SUBIECTUL II (Polinoame):
- `(a) Arătați că f(x₀) = [valoare], pentru orice a."` — evaluare cu parametru
- `(b) Arătați că f este divizibil cu g."` sau `"Determinați câtul și restul împărțirii f la g."` — Horner / Bézout
- `(c) Determinați a ∈ (0, +∞) pentru care x₁+x₂+x₃ = k."` sau produse de rădăcini — relațiile lui Viète

#### Cerințe standard M1 — SUBIECTUL II (Structuri algebrice):
- `(a) Arătați că x₀ ∗ y₀ = valoare."` — calcul direct
- `(b) Arătați că e este elementul neutru al legii ∗."` — demonstrație cu definiție
- `(c) Demonstrați că x ∗ (−x) ≤ k, pentru orice x."` — inegalitate cu lege de compoziție

#### Cerințe standard M1 — SUBIECTUL III (Studiu de funcție):
- `(a) Arătați că f'(x) = [expresie], x ∈ R."` — demonstrație prin calcul derivatei
- `(b) Determinați ecuația asimptotei oblice/orizontale spre +∞."` — calcul limită
- `(c) Arătați că ecuația f(x) = 0 are exact k soluții."` sau `"Demonstrați că f(x) ≥ g(x)."` — argument cu monotonie/IVT

#### Cerințe standard M1 — SUBIECTUL III (Integrale):
- `(a) Arătați că ∫[a,b] f(x) dx = valoare."` — calcul direct
- `(b) Arătați că ∫[c,d] f(x) dx = ln(k)."` — substituție sau integrare prin părți
- `(c) Arătați că aria = [expresie]."` — calculul ariei cu funcție compusă sau funcție auxiliară

---

## 4. Profilul M2 — M_șt-nat

### 4.1 Identitate și context

- **Filiera**: Teoretică, profilul real, specializarea științe ale naturii.
- **Nivel**: Mediu — sub M1, dar semnificativ peste M3.
- **Ore**: ~3 ore/săptămână.
- **Publicul elevilor**: Pregătiți pentru biologie, chimie, medicină, sciences.

### 4.2 Diferențe față de M1 — ce LIPSEȘTE sau este REDUS în M2

Acestea sunt **restricțiile critice** pe care generatorul trebuie să le respecte:

| Topic | M1 | M2 |
|-------|----|----|
| Numere complexe — forma trigonometrică + rădăcini ale unității | ✅ Prezent | ❌ Absent sau foarte rar |
| Polinoame — Horner, Bézout, descompunere completă | ✅ Aprofundat | ⚠️ Redus (rădăcini raționale, împărțire simplă) |
| Structuri algebrice (grup, inel, corp) | ✅ Prezent | ⚠️ Prezent în formă redusă (lege de compoziție simplă) |
| Matrice 3×3 | ✅ Frecvent | ⚠️ Prezent, dar mai simplu |
| Sisteme Cramer/Gauss complete | ✅ Aprofundat | ⚠️ Prezent, mai direct |
| Șiruri (Cesàro-Stolz, șiruri recursiv definite) | ✅ Complex | ⚠️ Limitat la convergență simplă |
| Derivate — teoreme (Rolle, Lagrange, l'Hôpital complex) | ✅ Aprofundat | ⚠️ Aplicat, rar teoreme pure |
| Integrale — calcule complexe (volume revoluție, L arc) | ✅ | ⚠️ Arie plană și integrale standard |

### 4.3 Ce este PREZENT și frecvent în M2

- **Progresii aritmetice și geometrice**: calculul termenilor, suma, recunoașterea tipului — mai frecvente decât la M1.
- **Funcții** (lin, quadr, exp, log): valori, monotonie, grafice.
- **Ecuații logaritmice/exponențiale**: similare M1 dar cu coeficienți mai simpli.
- **Geometrie analitică**: aceleași tipuri de probleme (dreapta, triunghi, condiții de paralelism/perpendicularitate).
- **Probabilități**: spații finite, evenimente simple.
- **Matrice 2×2 și 3×3**: det, invers, produs.
- **Lege de compoziție**: element neutru, element simetric, verificări simple.
- **Derivate și integrale**: calcul aplicat, studiu de funcție cu derivata, arii plane.

### 4.4 Structura tipică a unui subiect M2

**SUBIECTUL I** (6 itemi × 5p):
1. Progresie aritmetică sau geometrică (determina termenul sau suma)
2. Funcție liniară sau afină (determina parametru dintr-o condiție)
3. Ecuație logaritmică sau exponențială
4. Probabilitate pe mulțime finită
5. Geometrie analitică — triangle dreptunghic sau dreapta
6. Trigonometrie — expresie care se simplifică la o valoare

**SUBIECTUL II**:
- Problema 1: Matrice (2×2 sau 3×3) cu parametru — det, produs, inversabilitate
- Problema 2: Lege de compoziție definită pe R sau pe un subset — verificări, ecuații

**SUBIECTUL III**:
- Problema 1: Studiu de funcție (derivata, monotonie, asimptote, inegalitate)
- Problema 2: Integrală definită (calcul, arie, inegalitate)

### 4.5 Tipare de cerințe specifice M2

Structurile de cerință sunt **foarte similare** cu M1, dar cu:
- Expresii mai simple (mai puțini parametri, coeficienți mai mici)
- Funcții mai directe (fără compoziții de 3+ funcții)
- Calculul derivatei mai rar necesită regula lanțului în formă complexă

Exemple din examenele reale:
- `"Determinați termenul a₁ al progresiei aritmetice (aₙ)ₙ≥₁, în care a₂=8 și a₃=12."` — direct
- `"Se consideră funcția f(x)=3x-2. Determinați m pentru care f(m)=m."` — ecuație simplă
- `"Arătați că B(2)·B(0) = B(1)·B(4)."` — matrice cu parametru întreg
- `"Determinați a ∈ R pentru care matricea C(a)=B(a)-aA nu este inversabilă."` — condiție det=0
- `"Arătați că f(x)·(4-f(x)) ≤ 1, pentru orice x ∈ [4,+∞)."` — inegalitate din studiu de funcție

---

## 5. Profilul M3 — M_pedagogic și M_tehnologic

### 5.1 Identitate și context

- **Filierele**: Vocațională (profilul pedagogic — specializarea învățător-educatoare) și Vocațională (profilul tehnologic).
- **Nivel**: Cel mai accesibil dintre cele 3 profile — accentul pe aplicabilitate.
- **Ore**: ~2 ore/săptămână.
- **Publicul elevilor**: Nu se pregătesc pentru cariere STEM intensive; au nevoie de alfabetizare matematică aplicată.

### 5.2 Ce este PREZENT în M3

| Topic | Detalii |
|-------|---------|
| Progresii aritmetice și geometrice | Termeni, sume, recunoaștere tip — **foarte frecvente** |
| Funcții liniare, cuadratice | Grafice, valori, parametri |
| Funcții exponențiale și logaritmice | Numai aplicații de bază |
| Ecuații logaritmice simple | Cu baza 2, 3, 10 |
| Probleme practice (procente, creșteri, prețuri) | Aritmetică aplicată |
| Geometrie plană | Triunghi dreptunghic, Pitagora, perimetru, arie |
| Geometrie analitică elementară | Distanțe, mijloace, coordonate |
| Probabilități simple | Evenimente cu enumerare |
| Matrice 2×2 | Det, operații, sisteme 2×2 — **nu 3×3** |
| Lege de compoziție simplă | Verificări, element neutru, comutativitate — **subiectul II integral** |
| Derivate simple | Numai polinoame și funcții simple — **nu** funcții compuse complexe |

### 5.3 Ce LIPSEȘTE în M3

- Numere complexe (complet absent)
- Polinoame cu Horner/Bézout (absent)
- Structuri algebrice abstracte (absent)
- Matrice 3×3 (absent — doar 2×2)
- Sisteme 3×3 (absent)
- Șiruri cu limite (absent)
- Limite de funcții (absent)
- Integrale (complet absent)
- Derivate complexe (compuse, logaritmice, exponențiale) — limitat

### 5.4 Structura tipică SUBIECTUL II și III în M3

**SUBIECTUL II — complet dedicat legii de compoziție** (6 sub-puncte × 5p):

Structura observată constant în examenele 2015–2025:
1. `"Arătați că x₀ ∗ y₀ = valoare."` — calcul direct cu definiția
2. `"Determinați x ∈ M pentru care x ∗ x = valoare."` — ecuație simplă
3. `"Arătați că legea ∗ este comutativă."` sau `"Arătați că e este element neutru."` — demonstrație cu definiție
4. `"Determinați x pentru care x ∗ y₀ = valoare."` — ecuație cu legea
5. `"Determinați n ∈ N pentru care [expresie cu lege] este număr natural."` — condiție de tip
6. `"Determinați x ∈ subset pentru care [condiție complexă]."` — ecuație sau inegalitate

**SUBIECTUL III — complet dedicat matricelor 2×2** (6 sub-puncte × 5p):

Structura observată constant:
1. `"Arătați că det(A(a)) = [valoare fixă]."` — det care nu depinde de parametru
2. `"Arătați că A(x)·A(y) = [expresie]."` sau `"Arătați că A(2)·A(1) = [matrice]."` — produs
3. `"Demonstrați că A(a+[val]) - A(a) = A(0), pentru orice a."` — proprietate structurală
4. `"Determinați a ∈ R pentru care det(A(a)) = [valoare]."` — ecuație în parametru
5. `"Determinați a ∈ R pentru care [condiție matriceală]."` — condiție mai complexă
6. `"Determinați x și y pentru care A(a)·[x,y]ᵀ = [v]ᵀ."` — sistem matriceal 2×2

### 5.5 Tipare de cerințe specifice M3 — SUBIECTUL I

- `"Se consideră progresia geometrică (bₙ)ₙ≥₁ cu b₁=4 și b₂=8. Calculați b₃."` — one-step
- `"Se consideră funcția f(x) = 7x+2. Determinați a pentru care f(a) = 9."` — ecuație liniară
- `"Rezolvați în R ecuația log₂(3x+1) = log₂(3)·(1+x)."` — log simplă
- `"După o scumpire cu k%, prețul a crescut cu n lei. Determinați prețul inițial."` — procente
- `"Demonstrați că BM=CM, unde M este mijlocul lui AB."` — geometrie cu coordonate
- `"Se consideră triunghiul ABC dreptunghic în A cu AB=k₁ și BC=k₂. Arătați că perimetrul este p."` — Pitagora

---

## 6. Taxonomia completă a cerințelor

### 6.1 Tipuri de cerințe după acțiunea verbală

Aceste pattern-uri verbale au FRECVENȚĂ RIDICATĂ în examenele oficiale și trebuie reproduse **exact** în limbajul generatoarelor.

#### Grupul A — Demonstrație (Arătați că / Demonstrați că)
Sunt **cele mai frecvente** cerințe, apărând în ~60% din toate sub-punctele.

```
"Arătați că [expresie/egalitate/inegalitate]."
"Demonstrați că [afirmație]."
"Arătați că [identitate matematică]."
"Demonstrați că [inegalitate] pentru orice x ∈ [domeniu]."
"Arătați că [funcția/ecuația] are proprietatea că..."
"Demonstrați că legea ∗ este comutativă / asociativă / are element neutru."
```

#### Grupul B — Determinare (Determinați)
Sunt cele mai frecvente în Subiectul I.

```
"Determinați [numărul real / numerele reale / naturale] [simbol] pentru care [condiție]."
"Determinați coordonatele punctului [P] pentru care [condiție geometrică]."
"Determinați ecuația [dreptei/asimptotei] [descriere]."
"Determinați [mulțimea soluțiilor] ecuației."
"Determinați [intervalele de monotonie / extremele] funcției."
"Determinați câtul și restul împărțirii lui f la g."
"Determinați probabilitatea ca [eveniment]."
```

#### Grupul C — Calcul (Calculați)
Mai rar în ultimii ani față de "Arătați că" și "Determinați".

```
"Calculați [expresia / suma / produsul / determinantul]."
"Calculați probabilitatea că..."
"Calculați [bₙ] / [Sₙ]."
```

#### Grupul D — Rezolvare (Rezolvați)
Aproape exclusiv pentru ecuații.

```
"Rezolvați în mulțimea numerelor reale ecuația [expresie]."
"Rezolvați în R ecuația [expresie]."
"Rezolvați sistemul de ecuații."
```

### 6.2 Structuri de condiționare frecvente

```
"...unde [parametru] este număr real."
"...pentru orice număr real x."
"...pentru orice x ∈ [domeniu]."
"...pentru orice numere reale x și y."
"...unde a este număr real nenul."
"...în mulțimea [M] = [definire]."
"...pe mulțimea [M] se definește legea de compoziție..."
```

### 6.3 Formule de introducere a contextului

```
"Se consideră funcția f: R → R, f(x) = [expresie]."
"Se consideră matricea A(x) = [matrice cu parametru x]."
"Se consideră polinomul f(X) = [polinom cu parametru a]."
"Pe mulțimea M = [subset] se definește legea de compoziție x ∗ y = [formulă]."
"Se consideră șirul (aₙ)ₙ≥₁ cu [condiții inițiale]."
"Se consideră triunghiul ABC [descriere condiții]."
"În reperul cartezian xOy se consideră punctele A([x₁,y₁]) și B([x₂,y₂])."
"Se consideră numerele complexe z₁ = [expr] și z₂ = [expr]."
```

---

## 7. Sistemul de dificultate și aleatorism

### 7.1 Principiul de bază al aleatorismului

**Regula de aur**: Aleatorismul în BAC nu provine din exerciții complet diferite, ci din **varierea parametrilor în cadrul acelorași tipare structurale**. Un generator bun menține tiparul recunoscut al examenului (formularea, structura logică, topicul) și variază:
- Coeficienții și constantele
- Baza funcțiilor (log, exp)
- Tipul de condiție (egalitate, inegalitate, domeniu)
- Nivelul de compunere al expresiilor

### 7.2 Parametrii de dificultate (difficulty=1,2,3) per topic

#### difficulty=1 (Ușor / Subiectul I tipic)

Caracteristici generale:
- Coeficienți întregi mici: `a ∈ {1,2,3,4,5,6}`, `b ∈ {-6,...,6}`
- Puteri mici: exponent ≤ 3
- Radicali simpli: √2, √3, √5
- Logaritmi cu baze uzuale: log₂, log₃, log₁₀, ln
- Funcții simple: polinoame de grad ≤ 2, afine simple
- Rezultate "curate": întregi sau fracții simple
- Fără compuneri de 3+ funcții
- Fără parametri multipli simultani

#### difficulty=2 (Mediu / Subiectul II a,b tipic)

- Coeficienți: `a ∈ {1,...,10}`, negativi posibili
- Puteri: exponent ≤ 4, radicali compuși
- Expresii cu doi parametri (ex: matrice A(x,y))
- Polinoame de grad 3, împărțire polinomială
- Funcții compuse (ex: f ∘ g cu funcții elementare)
- Rezultate ce necesită simplificare (fracții, expresii cu √)
- Condiții cu inegalitate (nu doar egalitate)

#### difficulty=3 (Greu / Subiectul II c, Subiectul III b,c tipic)

- Expresii complexe: produse de funcții elementare diferite
- Funcții combinate (e^x + ln(x), raționale complicate)
- Demonstrații cu argumente indirecte (imposibilitate, unicitate)
- Integrale cu substituție neobvioasă
- Inegalități din studiu de funcție (nu direct din calcul)
- Limite de tip ∞/∞ cu L'Hôpital sau echivalenți
- Condiții care necesită mai mulți pași logici concatenați
- Numere naturale ca soluții (condiție de integrabilitate)

### 7.3 Tabla de aleatorism per topic

#### `powers` — Puteri și radicali

```python
# difficulty=1
base = rng.choice([2, 3, 5, 6, 10])
exp_num = rng.randint(1, 3)
exp_den = rng.randint(2, 4)
# Exemple generate:
# "Arătați că ∛8 + √25 - 4 = 3."
# "Simplificați (√6 - 1)·(√6 + 1)."

# difficulty=2
bases = rng.sample([2, 3, 5, 6, 7], 2)
# Exemple generate:
# "Rezolvați în R ecuația 2^(x²-1) = 4^x."
# "Rezolvați 3^(x+1) + 3^x = 12."

# difficulty=3
# Sisteme de ecuații cu exponențiale, substituții
# "Rezolvați sistemul: 2^x + 3^y = 5, 2^(x+1) - 3^y = 1."
```

#### `logarithms` — Logaritmi

```python
# difficulty=1 — una sau două proprietăți
base = rng.choice([2, 3, 10])
target_int = rng.randint(1, 4)  # log_b(b^k) = k
# Exemple:
# "Arătați că 2·log₁₀(100) + log₁₀(2) + log₁₀(5) = 5."
# "Rezolvați în R ecuația log₂(x²+3x) = log₂(10)."

# difficulty=2 — schimbare de bază, ecuație cu doi termeni
# "Rezolvați în R ecuația log₆(x) - log₆(5) = log₆(x-1) + 1."
# "Determinați x ∈ R pentru care log₃(x²+1) ≤ log₃(5)."

# difficulty=3 — inecuație cu parametru sau sistem
# "Determinați a ∈ R pentru care ecuația log_a(x²-1)=log_a(k)..."
```

#### `complex_numbers` — Numere complexe (M1 complet, M2 algebric only)

```python
# difficulty=1 — operații algebrice simple
re1, im1 = rng.randint(-4, 4), rng.randint(-4, 4)
re2, im2 = rng.randint(-4, 4), rng.randint(-4, 4)
# Exemple M1:
# "Se consideră z=3+i. Arătați că z·(z̄-2i) = 10."  [M1+M2]
# "Determinați forma algebrică a lui z=[(1+i)/(1-i)]^4."  [M1]
# "Arătați că z₁ + i·z₂ = [valoare]."  [M1+M2]

# difficulty=2 — modul, interpretare geometrică, argumnet
# "Determinați z ∈ C cu |z|=2 și arg(z)=π/3."  [M1 only]
# "Arătați că |z₁|² + |z₂|² = 10."  [M1+M2]

# difficulty=3 — rădăcini ale unității, forma trigonometrică
# "Determinați rădăcinile de ordin 3 ale lui -8."  [M1 only]
# "Arătați că ω^k + ω̄^k ∈ R, unde ω = e^(2πi/n)."  [M1 only]
```

**RESTRICȚIE**: Pentru M2, generatorul de numere complexe generează NUMAI itemuri în forma algebrică. Niciodată forma trigonometrică, rădăcini ale unității sau argumnet.

#### `polynomials` — Polinoame

```python
# difficulty=1 — evaluare sau rădăcini raționale simple
degree = 2
a_coeff = rng.randint(1, 3)
# Exemple:
# "Arătați că f(2) = 0, pentru orice a ∈ R."  (f are pe 2 ca rădăcină indiferent de a)
# "Determinați a pentru care f(1) = 0."

# difficulty=2 — împărțire (Horner), relațiile lui Viète
# "Determinați câtul și restul împărțirii lui f la g=X²+X-3."
# "Arătați că f este divizibil cu g=X+1."

# difficulty=3 — combinație: parametru + rădăcini + relații Viète
# "Determinați a > 0 pentru care x₁² + x₂² + x₃² = k."
# "Determinați a pentru care (x₁+1)(x₂+1)(x₃+1) = val."
```

#### `matrices` — Matrice și determinanți

```python
# difficulty=1 — determinant 2×2 sau 3×3 simplu cu valoare fixă
size = rng.choice([2, 3])  # M3: mereu 2
# Exemple:
# "Arătați că det(A(1)) = 7."
# "Arătați că det(A(a)) = k, pentru orice a ∈ R."  ← det independent de parametru

# difficulty=2 — produs matriceal A(x)·A(y)=A(f(x,y)), inversabilitate
# "Arătați că A(x)·A(y) = A(x+y)."
# "Determinați a pentru care matricea C(a) nu este inversabilă."
# "Determinați x pentru care A(2x)·A(1) = A(x)·A(2)."

# difficulty=3 — sisteme, inegalități cu det, puteri de matrice
# "Determinați n ∈ N pentru care 2·det(A(n)) ≤ det(A(2n))."
# "Arătați că A(a+2) - A(a) = A(0), pentru orice a."
# "Demonstrați că (A(a))ⁿ = A(n·a)."
```

#### `algebraic_structures` — Structuri algebrice

```python
# Template general pentru legea x ∗ y = f(x, y)
# Tipuri de legi frecvente în examenele BAC:

law_templates = [
    # Pe R sau subset
    "x * y = x*y - x - y + 2",           # element neutru e=1
    "x * y = 2*x*y - x - y",              # structuri neliniare
    "x * y = x + y - x*y",                # frecvent
    "x * y = x*y*(x**2 + y**2) / ...",    # mai rar
    # Pe (0,+∞)
    "x * y = 1/x + 1/y",                  # M3 frecvent
    "x * y = x*y + sqrt(x) + sqrt(y)",    # M1/M2
]

# difficulty=1 — calcul direct + comutativitate
# "Arătați că 1 ∗ 1 = 3."
# "Arătați că legea ∗ este comutativă."

# difficulty=2 — element neutru, ecuație
# "Demonstrați că e=k este element neutru."
# "Determinați x ∈ M pentru care x ∗ x = val."

# difficulty=3 — element simetric/invers, inegalitate cu lege
# "Determinați, pentru fiecare x ∈ M nenul, elementul simetric al lui x față de legea ∗."
# "Demonstrați că x ∗ (-x) ≤ 1, pentru orice x ∈ R."
```

#### `sequences` — Șiruri (M1/M2 only)

```python
# difficulty=1 — șiruri aritmetice/geometrice simple, calcul de termen
# "Determinați a₁ dacă a₂=8 și a₃=12."

# difficulty=2 — convergență, recurențe simple
# "Demonstrați că șirul (aₙ) este convergent și calculați limita."
# "Demonstrați că (aₙ) este monoton crescător și mărginit."

# difficulty=3 — Cesàro-Stolz, subsiruri, recurențe complexe (M1 only)
# "Utilizând criteriul Cesàro-Stolz, calculați lim(aₙ/n)."
```

#### `limits` — Limite de funcții

```python
# difficulty=1 — calcul direct, forme nedeterminate simple
# "Calculați lim_{x→2} (x²-4)/(x-2)."  → substituție simplifcată

# difficulty=2 — asimptote oblice, forme nedeterminate complexe
# "Determinați ecuația asimptotei oblice spre +∞."  → m=lim(f/x), n=lim(f-mx)

# difficulty=3 — L'Hôpital, limite cu parametru, convergență
# "Arătați că lim_{x→0} [∫₀ˣ f(t)dt] / x² = val."  → L'Hôpital sau echivalent
```

#### `derivatives` — Derivate

```python
# REGULĂ FUNDAMENTALĂ: derivata se verifică cu sympy.diff()

# difficulty=1 — derivate de polinoame, exp, log simple
func_types_d1 = [
    "a*x**n + b*x**m + c",              # polinom
    "a*exp(x) + b*x",                   # exp+liniar
    "a*log(x, base) + b*x",             # log+liniar
]
# Cerință tipică: "Arătați că f'(x) = [expr], x ∈ R."

# difficulty=2 — regula produsului, câtului, funcție compusă
func_types_d2 = [
    "x**n * exp(a*x)",                  # produs
    "(a*x + b)/(c*x + d)",              # cât
    "exp(a*x**2 + b*x)",                # compusă
    "log(a*x**2 + b*x + c)",            # compusă logaritmică
]
# Cerință tipică: "Determinați intervalele de monotonie." sau
# "Demonstrați că pentru orice m ∈ (k₁,k₂], ecuația f(x)=m are soluție unică."

# difficulty=3 — studiu complet + demonstrații cu monotonie
func_types_d3 = [
    "x*exp(x) - a*exp(x)",              # studiu cu extrema
    "x**2 * log(x)",                    # compusă cu radical sau log
    "(a*x**2+b)/(x**2+c)",              # rațională
    "x**(1/2) - log(x)",                # irațională-logaritmică
]
# Cerință tipică: "Demonstrați că ecuația f(x)=0 are exact k soluții."
# "Demonstrați că f(x) ≥ g(x), pentru orice x ∈ domeniu."
```

#### `integrals` — Primitive și integrale definite

```python
# REGULĂ FUNDAMENTALĂ: integrala se verifică cu sympy.integrate()

# difficulty=1 — integrale directe din tabel
integral_types_d1 = [
    "x**n",                             # putere → x^(n+1)/(n+1)
    "1/(a*x+b)",                        # log
    "exp(a*x)",                         # exp
    "sin(a*x)", "cos(a*x)",             # trig
]
# Cerință tipică: "Arătați că ∫[a,b] f(x) dx = valoare."

# difficulty=2 — integrare prin părți, substituție
integral_types_d2 = [
    "x * exp(x)",                       # prin părți
    "x * sin(x)", "x * cos(x)",         # prin părți
    "log(x)",                           # prin părți cu 1·log(x)
    "x/(x**2+a)**n",                    # substituție
]
# Cerință tipică: "Arătați că ∫[0,1] f(x) dx = ln(k)."

# difficulty=3 — combinații, arii, inegalități integrale
integral_types_d3 = [
    "funcție rațională cu descompunere",
    "f(x)*g(x) unde g provine dintr-o altă problemă",
    "aria suprafeței delimitate de grafice compuse",
]
# Cerință tipică: "Arătați că aria suprafeței plane ... este egală cu [expr]."
# "Demonstrați că lim_{x→0} [∫₀ˣ f(t) dt] / x² = val."
```

#### `geometry` — Geometrie plană și analitică

```python
# difficulty=1 — condiții simple pe punct/dreaptă
# M: punct pe dreaptă, dreaptă prin două puncte, distanță
# Exemple:
# "Determinați a ∈ R știind că A(a,a) aparține dreptei y=3x-2."
# "Determinați coordonatele lui C pentru care AC = OB (ca vectori)."

# difficulty=2 — condiții compuse (paralelism+perpendicularitate+mijloc)
# "Determinați a,b astfel că segmentele AC și BD au același mijloc."

# difficulty=3 — cerc, tangente, condiții combinate
# "Determinați ecuația cercului circumscris triunghiului ABC."
```

#### `trigonometry` — Trigonometrie

```python
# difficulty=1 — calcul direct cu formule
angle_multiples = [sp.pi/6, sp.pi/4, sp.pi/3, sp.pi/2]
# "Se consideră E = sin²x·cos²(π/4) + ... Arătați că E(π/3) = val."

# difficulty=2 — ecuații trigonometrice
# "Rezolvați în R ecuația 2sin²x - sinx - 1 = 0."

# difficulty=3 — demonstrații cu formule multiple
# "Demonstrați că sin(3x) = 3sinx - 4sin³x."
```

#### `combinatorics` — Combinatorică și probabilități

```python
# difficulty=1 — spațiu finit explicit, probabilitate simplă
space_size = rng.randint(10, 99)  # ex: numerele naturale de 2 cifre
# "Determinați probabilitatea ca, alegând n ∈ A, numărul n+5 să fie multiplu de 10."
# "Determinați câte submulțimi cu 2 elemente are A={...}."

# difficulty=2 — combinații, aranjamente, permutări
n = rng.randint(4, 8)
k = rng.randint(2, n-1)
# "Arătați că C(n,k) + C(n,k-1) = C(n+1,k)."

# difficulty=3 — probabilitate condiționată, distribuții simple
# "Determinați probabilitatea ca evenimentul A să aibă loc, știind că B s-a produs."
```

#### `progressions` — Progresii (frecvente M2, M3)

```python
# difficulty=1 — termen, sumă directă
r_arith = rng.choice([-3,-2,-1,1,2,3,4,5])
a1 = rng.randint(1, 10)
# "Se consideră progresia aritmetică cu a₁=k și r=m. Calculați S₁₀."

# difficulty=2 — progresie geometrică cu condiție
q = rng.choice([2, 3, 1/2, -2])
# "Determinați n pentru care aₙ = 48, dacă a₁=3 și q=2."

# difficulty=3 — șir mixt sau condiție combinată
# "Demonstrați că șirul (aₙ·bₙ) este și el geometric."
```

#### `statistics` — Statistică (M3 exclusiv)

```python
# difficulty=1 — medie aritmetică, mediană din date date
data = [rng.randint(1,10) for _ in range(rng.randint(5,8))]
# "Calculați media aritmetică a valorilor {d₁, d₂, ..., dₙ}."

# difficulty=2 — medie ponderată, dispersie
# "Determinați a ∈ R pentru care media aritmetică a lui a, a+2, a+5 este 6."

# difficulty=3 — combinare cu probabilități
# "Datele unui sondaj arată că... Determinați probabilitatea că..."
```

---

## 8. Arhitectura motorului de generare

### 8.1 Clasa de bază abstractă

```python
# apps/exercises/generators/base.py

import sympy as sp
import hashlib
import random
from abc import ABC, abstractmethod
from typing import Optional

class ExerciseGenerator(ABC):
    """
    Clasa de bază pentru toți generatorii de exerciții BAC.
    
    REGULILE NESTRICATE:
    1. generate() este o funcție PURĂ față de (profile, difficulty, rng) —
       aceeași sămânță reproduce ACELAȘI exercițiu.
    2. Rezultatul matematic este VERIFICAT cu sympy înainte de returnare.
    3. Output-ul este întotdeauna LaTeX valid (delimitat $...$).
    4. Nu există string-uri hard-codate pentru răspuns — se calculează.
    """

    TOPIC_CODE: str = ""  # ex: "derivatives"
    SUPPORTED_PROFILES: list = []  # ex: ["M1", "M2"]
    MAX_RETRIES: int = 50  # tentative de re-generare dacă validarea eșuează

    def __init__(self, profile: str, difficulty: int, rng: random.Random):
        if profile not in self.SUPPORTED_PROFILES:
            raise ValueError(f"{self.TOPIC_CODE} nu suportă profilul {profile}")
        if difficulty not in (1, 2, 3):
            raise ValueError("difficulty trebuie să fie 1, 2 sau 3")
        self.profile = profile
        self.difficulty = difficulty
        self.rng = rng

    @abstractmethod
    def _generate_params(self) -> dict:
        """Generează parametrii aleatori ai exercițiului."""
        ...

    @abstractmethod
    def _build_question(self, params: dict) -> str:
        """Construiește string-ul LaTeX al întrebării."""
        ...

    @abstractmethod
    def _compute_answer(self, params: dict):
        """Calculează răspunsul cu sympy. Returnează obiect sympy."""
        ...

    @abstractmethod
    def _validate(self, params: dict, answer) -> bool:
        """Verifică că exercițiul generat este corect și rezonabil."""
        ...

    def _build_hint(self, params: dict) -> str:
        """Hint implicit — poate fi suprasscris."""
        return ""

    def _build_steps(self, params: dict) -> list[str]:
        """Pași de rezolvare opționali."""
        return []

    def generate(self) -> dict:
        """Generează și returnează exercițiul complet."""
        for attempt in range(self.MAX_RETRIES):
            try:
                params = self._generate_params()
                answer_sympy = self._compute_answer(params)
                if not self._validate(params, answer_sympy):
                    continue
                return {
                    "topic": self.TOPIC_CODE,
                    "difficulty": self.difficulty,
                    "question_latex": self._build_question(params),
                    "hint_latex": self._build_hint(params),
                    "answer_latex": self._format_answer(answer_sympy),
                    "steps_latex": self._build_steps(params),
                }
            except Exception:
                continue
        raise RuntimeError(
            f"Generatorul {self.TOPIC_CODE} nu a putut produce un exercițiu valid "
            f"în {self.MAX_RETRIES} tentative (profile={self.profile}, difficulty={self.difficulty})"
        )

    def _format_answer(self, answer_sympy) -> str:
        """Convertește răspunsul sympy în LaTeX."""
        return f"${sp.latex(answer_sympy)}$"
```

### 8.2 Registrul generatoarelor

```python
# apps/exercises/generators/registry.py

from .topics.powers import PowersGenerator
from .topics.logarithms import LogarithmsGenerator
# ... import toate generatoarele

REGISTRY: dict[str, type] = {
    "powers":                PowersGenerator,
    "logarithms":            LogarithmsGenerator,
    "complex":               ComplexNumbersGenerator,
    "polynomials":           PolynomialsGenerator,
    "matrices":              MatricesGenerator,
    "systems":               SystemsGenerator,
    "algebraic_structures":  AlgebraicStructuresGenerator,
    "sequences":             SequencesGenerator,
    "limits":                LimitsGenerator,
    "derivatives":           DerivativesGenerator,
    "integrals":             IntegralsGenerator,
    "geometry":              GeometryGenerator,
    "trigonometry":          TrigonometryGenerator,
    "combinatorics":         CombinatoricsGenerator,
    "statistics":            StatisticsGenerator,
    "progressions":          ProgressionsGenerator,
}

PROFILE_TOPICS = {
    "M1": [
        "powers", "logarithms", "complex", "polynomials",
        "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics"
    ],
    "M2": [
        "powers", "logarithms", "complex",  # complex: algebric only
        "polynomials", "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics", "progressions"
    ],
    "M3": [
        "powers", "logarithms",
        "matrices",              # matrices: 2×2 only
        "algebraic_structures",  # structuri: nivel basic
        "geometry", "trigonometry", "combinatorics",
        "progressions", "statistics",
        "derivatives"            # derivate: polinoame only
    ],
}
```

### 8.3 Funcția de generare a unui set de exerciții

```python
# apps/exercises/generators/engine.py

import random
import hashlib
from .registry import REGISTRY, PROFILE_TOPICS

def generate_exercises(
    profile: str,
    topics: list[str],
    difficulty: int,
    count: int,
    seed: Optional[str] = None
) -> dict:
    """
    Funcția centrală de generare.
    
    LOGICA DE ALEATORISM:
    - Dacă seed este None, se generează unul aleator.
    - Sămânța controlează COMPLET aleatorismul: același seed = aceleași exerciții.
    - Topics-urile sunt alese ciclic dar cu shuffling per-seed pentru varietate.
    """
    if seed is None:
        seed = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
    
    rng = random.Random(seed)
    
    # Validare topics față de profil
    allowed = set(PROFILE_TOPICS.get(profile, []))
    valid_topics = [t for t in topics if t in allowed]
    if not valid_topics:
        valid_topics = list(allowed)
    
    # Distribuție ciclică cu shuffling
    rng.shuffle(valid_topics)
    topic_cycle = (valid_topics * (count // len(valid_topics) + 1))[:count]
    
    items = []
    for i, topic in enumerate(topic_cycle):
        # Fiecare exercițiu are propria sa sămânță derivată
        item_seed = f"{seed}_{i}_{topic}"
        item_rng = random.Random(item_seed)
        
        generator_class = REGISTRY[topic]
        generator = generator_class(profile, difficulty, item_rng)
        item = generator.generate()
        item["id"] = f"{topic[:3]}_{seed}_{i:02d}"
        items.append(item)
    
    return {"items": items, "seed": seed}
```

### 8.4 Logica de distribuție a dificultății în setul generat

Când difficulty este specificat de utilizator, se aplică variația internă:

```python
def compute_item_difficulty(base_difficulty: int, position: int, total: int) -> int:
    """
    În cadrul unui set cu difficulty=2, exercițiile vor varia între 1 și 3
    pentru a oferi o distribuție naturală — similar cu examenul real.
    
    Distribuție recomandată per difficulty level:
    - difficulty=1: 80% easy (1), 20% medium (2)
    - difficulty=2: 20% easy (1), 60% medium (2), 20% hard (3)
    - difficulty=3: 10% medium (2), 90% hard (3)
    """
    distributions = {
        1: [1, 1, 1, 1, 2],          # 80/20
        2: [1, 2, 2, 2, 3],          # 20/60/20
        3: [2, 3, 3, 3, 3],          # 10/90
    }
    pool = distributions[base_difficulty]
    # Deterministic dar dependent de poziție
    return pool[position % len(pool)]
```

---

## 9. Specificații per topic și per subtip

### 9.1 Generator `derivatives` — Exemplu complet de implementare

Acesta este cel mai complex generator și servește drept **model de referință**.

```python
# apps/exercises/generators/topics/derivatives.py
import sympy as sp
import random
from ..base import ExerciseGenerator

class DerivativesGenerator(ExerciseGenerator):
    TOPIC_CODE = "derivatives"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    # Tipuri de funcții per difficulty și profil
    FUNC_TEMPLATES = {
        "M1": {
            1: [
                # (template_func, description, sympy_expr_builder)
                ("poly",    "polinom grad 3-4",
                 lambda p, x: p["a"]*x**p["n"] + p["b"]*x**p["m"] + p["c"]),
                ("exp_lin", "exp×liniar",
                 lambda p, x: sp.exp(p["a"]*x) + p["b"]*x),
                ("log_lin", "logaritm+liniar",
                 lambda p, x: p["a"]*sp.log(x) + p["b"]*x**2),
            ],
            2: [
                ("prod",    "produs",
                 lambda p, x: x**p["n"] * sp.exp(p["a"]*x)),
                ("quot",    "cât rational",
                 lambda p, x: (p["a"]*x + p["b"])/(p["c"]*x**2 + p["d"])),
                ("comp",    "compusă exp",
                 lambda p, x: sp.exp(p["a"]*x**2 + p["b"]*x)),
                ("comp_log","compusă log",
                 lambda p, x: sp.log(p["a"]*x**2 + p["b"]*x + p["c"])),
            ],
            3: [
                ("mixed1",  "exp×polinom+log",
                 lambda p, x: (p["a"]*x**2 + p["b"]*x)*sp.exp(p["c"]*x) - p["d"]*x),
                ("rational","rațională complexă",
                 lambda p, x: (p["a"]*x**2 + p["b"])/(x**2 + p["c"])),
                ("sqrt_log","radical+log",
                 lambda p, x: sp.sqrt(p["a"]*x + p["b"]) - sp.log(x)),
            ],
        },
        "M2": {
            # M2 = subset din M1, fără funcțiile cele mai complexe
            1: [("poly","polinom", lambda p,x: p["a"]*x**p["n"]+p["b"]*x+p["c"]),
                ("exp_lin","exp", lambda p,x: sp.exp(p["a"]*x)+p["b"]*x)],
            2: [("prod","produs", lambda p,x: x**p["n"]*sp.exp(p["a"]*x)),
                ("quot","cât", lambda p,x: (p["a"]*x+p["b"])/(x**2+p["c"]))],
            3: [("comp","compusă", lambda p,x: sp.exp(p["a"]*x**2+p["b"]*x)),
                ("rational","rațională", lambda p,x: x**2/(x**2+p["a"]*x+p["b"]))],
        },
        "M3": {
            # M3: NUMAI polinoame și funcții simple — fără exp, log complexe
            1: [("poly2","polinom grad 2", lambda p,x: p["a"]*x**2+p["b"]*x+p["c"]),
                ("lin","liniară", lambda p,x: p["a"]*x+p["b"])],
            2: [("poly3","polinom grad 3", lambda p,x: p["a"]*x**3+p["b"]*x**2+p["c"]*x+p["d"])],
            3: [("poly4","polinom grad 4", lambda p,x: p["a"]*x**4+p["b"]*x**2+p["c"])],
        },
    }

    def _generate_params(self) -> dict:
        d = self.difficulty
        rng = self.rng
        
        # Selectează template-ul
        templates = self.FUNC_TEMPLATES[self.profile][d]
        tmpl = rng.choice(templates)
        
        # Generează coeficienți conform difficulty
        if d == 1:
            coeffs = {
                "a": rng.choice([-3,-2,-1,1,2,3]),
                "b": rng.choice([-4,-3,-2,-1,1,2,3,4]),
                "c": rng.choice([-5,-3,-1,0,1,3,5]),
                "n": rng.randint(2, 3),
                "m": rng.randint(1, 2),
                "d": rng.choice([1,2,3,4]),
            }
        elif d == 2:
            coeffs = {
                "a": rng.choice([-3,-2,-1,1,2,3]),
                "b": rng.choice([-5,-3,-1,0,1,3,5]),
                "c": rng.randint(1, 5),
                "d": rng.randint(1, 4),
                "n": rng.randint(2, 4),
                "m": rng.randint(1, 3),
            }
        else:  # d == 3
            coeffs = {
                "a": rng.choice([-2,-1,1,2]),
                "b": rng.choice([-3,-2,-1,0,1,2,3]),
                "c": rng.randint(1, 4),
                "d": rng.choice([-2,-1,1,2]),
                "n": rng.randint(2, 4),
            }
        
        return {"template": tmpl, "coeffs": coeffs}

    def _compute_answer(self, params: dict):
        x = sp.Symbol("x")
        tmpl = params["template"]
        coeffs = params["coeffs"]
        
        # Construiește expresia
        f_expr = tmpl[2](coeffs, x)
        
        # Calculează derivata cu sympy
        f_prime = sp.diff(f_expr, x)
        f_prime_simplified = sp.simplify(f_prime)
        
        return {
            "f_expr": f_expr,
            "f_prime": f_prime_simplified,
            "x": x,
        }

    def _validate(self, params: dict, answer) -> bool:
        # Verifică că derivata nu este trivial zero sau constant
        if answer["f_prime"] == 0:
            return False
        # Verifică că expresia nu are puncte de nedefinire problematice
        # Verifică că LaTeX-ul nu este prea lung (>200 caractere)
        latex_len = len(sp.latex(answer["f_prime"]))
        return latex_len < 200

    def _build_question(self, params: dict) -> str:
        x = sp.Symbol("x")
        tmpl = params["template"]
        coeffs = params["coeffs"]
        f_expr = tmpl[2](coeffs, x)
        
        # Selecție cerință în funcție de difficulty
        d = self.difficulty
        rng = self.rng
        
        if d == 1:
            return (
                f"Se consideră funcția $f : \\mathbb{{R}} \\to \\mathbb{{R}}$, "
                f"$f(x) = {sp.latex(f_expr)}$. "
                f"Arătați că $f'(x) = {sp.latex(sp.diff(f_expr, x))}$, $x \\in \\mathbb{{R}}$."
            )
        elif d == 2:
            req = rng.choice([
                "Determinați intervalele de monotonie ale funcției $f$.",
                "Determinați punctele de extrem ale funcției $f$.",
            ])
            return (
                f"Se consideră funcția $f : \\mathbb{{R}} \\to \\mathbb{{R}}$, "
                f"$f(x) = {sp.latex(f_expr)}$. {req}"
            )
        else:
            req = rng.choice([
                f"Arătați că ecuația $f(x) = 0$ are exact două soluții reale.",
                f"Demonstrați că $f(x) \\geq f(0)$, pentru orice $x \\in \\mathbb{{R}}$.",
                f"Demonstrați că funcția $f$ este bijectivă.",
            ])
            return (
                f"Se consideră funcția $f : \\mathbb{{R}} \\to \\mathbb{{R}}$, "
                f"$f(x) = {sp.latex(f_expr)}$. {req}"
            )
    
    def _build_hint(self, params: dict) -> str:
        x = sp.Symbol("x")
        tmpl = params["template"]
        coeffs = params["coeffs"]
        f_expr = tmpl[2](coeffs, x)
        f_prime = sp.diff(f_expr, x)
        return f"Calculați $f'(x) = {sp.latex(f_prime)}$."
```

### 9.2 Generator `matrices` — Specificații critice

```python
# Matricele parametrizate trebuie să aibă determinanți cu proprietăți speciale:

# Tipul 1: det(A(x)) = constantă (nu depinde de x)
# → Exerciții de tipul "Arătați că det(A(1)) = 7" sau "det(A(a)) = k pentru orice a"
# → Se generează prin construcție: se pornește de la det dorit și se construiesc elementele

# Tipul 2: A(x)·A(y) = A(f(x,y))  — matrice cu proprietate de homomorfism
# → Classic: A(x)·A(y) = A(x+y) — se testează câteva familii de matrice
# → Familie frecventă: A(x) = I + x·N unde N este nilpotentă

# Tipul 3: det depinde de a, condiție det=0 → inversabilitate
# → det(C(a)) = polinomul în a, se caută rădăcinile

# RESTRICȚII per profil:
# M3: numai matrice 2×2, parametru simplu, det cu formulă directă
# M2: matrice 2×2 și 3×3, parametru simplu sau dublu
# M1: matrice 3×3, parametri multipli, sisteme asociate

def generate_matrix_type1(rng, size, profile):
    """Generează matrice A(x) cu det constant."""
    target_det = rng.choice([1, -1, 2, -2, 3, 4, 6, 7, 8])
    # ... construcție backwards din determinant dorit
    
def generate_matrix_type2(rng, profile):
    """Generează matrice A(x) cu A(x)·A(y)=A(x+y)."""
    # Familie: [[1, x], [0, 1]] — matrice superioară unitriangulară
    # → det = 1, A(x)·A(y) = A(x+y) — verificat
    # Familie pentru 3×3: extend similar
```

### 9.3 Generator `algebraic_structures` — Tipologia legilor

```python
# Legile de compoziție frecvente în examene (verificate pe baza datelor din 2015-2025)

LAW_TEMPLATES_M1_M2 = [
    # (formulă lambda, element_neutru, tip_domeniu)
    (lambda x,y: x*y - x - y + 2,  1, "R"),        # neutru e=1
    (lambda x,y: 2*x*y - x - y,    None, "R"),       # fără neutru în R
    (lambda x,y: x+y - x*y,        0, "R"),           # neutru e=0
    (lambda x,y: (x+y)/(1+x*y),    0, "(-1,1)"),     # grup tanh
]

LAW_TEMPLATES_M3 = [
    # Legi mai simple, definite pe (0,+∞)
    (lambda x,y: 1/x + 1/y,         None, "(0,+inf)"),
    (lambda x,y: x*y + x + y + 1,   -1+sp.sqrt(2), "(0,+inf)"),
    (lambda x,y: sp.sqrt(x**2+y**2), 0, "[0,+inf)"),
]

# REGULI de generare:
# 1. Legea trebuie să fie SIMPLU de calculat manual — fără derivate sau limite.
# 2. Sub-punctul (a) trebuie să fie un calcul direct cu numere concrete.
# 3. Sub-punctul de comutativitate/neutru trebuie să fie demonstrabil în 3-5 rânduri.
# 4. Sub-punctul (c/6) trebuie să implice o inegalitate sau o condiție netrivială.
```

---

## 10. Modul Simulare BAC complet

### 10.1 Reguli stricte de structurare

Simularea BAC trebuie să reproducă **exact** structura oficială, inclusiv:

```python
def generate_full_simulation(profile: str, seed: Optional[str] = None) -> dict:
    """
    Generează un subiect complet de BAC cu structura oficială.
    
    Structura returnată:
    {
      "profile": "M1",
      "seed": "abc123",
      "total_points": 100,
      "officiu_points": 10,
      "subiect_I": {
        "points": 30,
        "items": [  # exact 6 itemi, fiecare 5p
          {
            "number": 1,
            "points": 5,
            "topic": "logarithms",
            "difficulty": 1,
            "question_latex": "...",
            "hint_latex": "...",
            "answer_latex": "...",
          },
          # ... itemi 2-6
        ]
      },
      "subiect_II": {
        "points": 30,
        "problems": [
          {
            "number": 1,
            "topic_primary": "matrices",
            "sub_items": [  # exact 3 sub-itemi: a, b, c
              {"label": "a", "points": 5, "difficulty": 1, ...},
              {"label": "b", "points": 5, "difficulty": 2, ...},
              {"label": "c", "points": 5, "difficulty": 3, ...},
            ]
          },
          {
            "number": 2,
            "topic_primary": "polynomials",  # sau algebraic_structures
            "sub_items": [...],
          }
        ]
      },
      "subiect_III": {
        "points": 30,
        "problems": [
          {
            "number": 1,
            "topic_primary": "derivatives",  # studiu de funcție
            "sub_items": [...]
          },
          {
            "number": 2,
            "topic_primary": "integrals",    # integrale și arie
            "sub_items": [...]
          }
        ]
      }
    }
    """
```

### 10.2 Reguli de alocare topic-uri per subiect în simulare

```python
SIMULATION_RULES = {
    "M1": {
        "subiect_I": {
            # Distribuție bazată pe analiza examenelor 2015-2025
            "slot_1": rng.choice(["logarithms", "complex"]),
            "slot_2": "derivatives",        # funcție simplă, compoziție
            "slot_3": rng.choice(["logarithms", "powers", "complex"]),  # ecuație
            "slot_4": "combinatorics",
            "slot_5": "geometry",
            "slot_6": "trigonometry",
        },
        "subiect_II": {
            "problem_1": "matrices",        # sau systems
            "problem_2": rng.choice(["polynomials", "algebraic_structures"]),
        },
        "subiect_III": {
            "problem_1": "derivatives",     # studiu de funcție
            "problem_2": "integrals",
        },
    },
    "M2": {
        "subiect_I": {
            "slot_1": rng.choice(["progressions", "logarithms"]),
            "slot_2": "derivatives",        # funcție simplă
            "slot_3": rng.choice(["logarithms", "powers"]),
            "slot_4": "combinatorics",
            "slot_5": "geometry",
            "slot_6": "trigonometry",
        },
        "subiect_II": {
            "problem_1": "matrices",
            "problem_2": "algebraic_structures",
        },
        "subiect_III": {
            "problem_1": "derivatives",
            "problem_2": "integrals",
        },
    },
    "M3": {
        "subiect_I": {
            "slot_1": "progressions",
            "slot_2": "derivatives",        # funcție liniară/afină
            "slot_3": "logarithms",         # ecuație log simplă
            "slot_4": rng.choice(["combinatorics", "statistics"]),
            "slot_5": "geometry",
            "slot_6": "geometry",           # triunghi, Pitagora
        },
        "subiect_II": {
            # M3: INTEGRAL subiect pentru lege de compoziție (6 sub-puncte)
            "format": "single_topic_6_items",
            "topic": "algebraic_structures",
        },
        "subiect_III": {
            # M3: INTEGRAL subiect pentru matrice 2×2 (6 sub-puncte)
            "format": "single_topic_6_items",
            "topic": "matrices",
        },
    },
}
```

### 10.3 Progresivitatea dificultății în sub-itemii a/b/c

Acesta este un principiu critic observat în TOATE examenele analizate:

```
Sub-item (a): difficulty=1 sau 2
  → Demonstrație directă prin calcul simplu
  → "Arătați că [rezultat concret]."
  → Necesită 2-4 rânduri de rezolvare

Sub-item (b): difficulty=2
  → Demonstrație algebrică sau determinare cu condiție
  → Poate folosi rezultatul din (a)
  → Necesită 4-8 rânduri

Sub-item (c): difficulty=3
  → Demonstrație cu argument din analiză/algebră
  → Adesea necesită rezultatele din (a) și (b)
  → Necesită 8-15 rânduri
  → Include condiții de tipul "pentru orice...", "există unic...", "numărul de soluții..."
```

### 10.4 Structura matriceală a unui subiect M1 simulat — exemplu concret

```
SUBIECTUL I (6 × 5p = 30p):
  [1] complex:      "Se consideră z₁=a+bi, z₂=c+di. Arătați că z₁·z̄₂ + z̄₁·z₂ = val."
  [2] functions:    "Se consideră f(x)=k√x+m. Determinați a pentru care f(a)=f(3a)."
  [3] equations:    "Rezolvați în R ecuația 3^(2x)·5^x = 5^(x+2)."
  [4] combinatorics: "Câte submulțimi cu 2 elemente pare are A={...}?"
  [5] geometry:     "Determinați coordonatele lui C pentru care AC⃗=OB⃗."
  [6] trigonometry: "Arătați că în triunghiul ABC dreptunghic în A cu [date], BC=val."

SUBIECTUL II (2 × 3 sub-puncte × 5p = 30p):
  Problema 1 — Matrice A(x) parametrizată 3×3:
    (a) Arătați că det(A(1)) = val.          [difficulty=1]
    (b) Arătați că A(x)·A(y) = A(x+y).      [difficulty=2]
    (c) Determinați n∈N pentru care 2·det(A(n)) ≤ det(A(2n)). [difficulty=3]
  
  Problema 2 — Polinom f(X) = X³ + aX² - aX + 2:
    (a) Arătați că f(x₀) = val, pentru orice a.    [difficulty=1]
    (b) Determinați câtul/restul împărțirii f la g=X+1. [difficulty=2]
    (c) Determinați a>0 pentru care x₁+x₂+x₃=k.   [difficulty=3]

SUBIECTUL III (2 × 3 sub-puncte × 5p = 30p):
  Problema 1 — Funcție f: studiu de funcție:
    (a) Arătați că f'(x) = [expresie].             [difficulty=1]
    (b) Determinați ecuația asimptotei oblice.      [difficulty=2]
    (c) Demonstrați că f(x)=0 are exact 2 soluții. [difficulty=3]
  
  Problema 2 — Integrală definită:
    (a) Arătați că ∫[a,b] f(x)dx = val.            [difficulty=1]
    (b) Arătați că ∫[c,d] f(x)dx = ln(k).          [difficulty=2]
    (c) Arătați că aria = [expresie].               [difficulty=3]
```

---

## 11. Validare sympy și corectitudine matematică

### 11.1 Principii fundamentale de validare

**NICIO VALOARE DE RĂSPUNS nu este hard-codată sau generată prin string manipulation.**
Toate răspunsurile sunt calculate cu sympy și comparate simbolic.

```python
# BINE — calculat cu sympy
import sympy as sp
x = sp.Symbol("x")
f = x**3 - 2*x + 1
f_prime = sp.diff(f, x)  # → 3x² - 2
# f_prime este verificat, nu inventat

# RĂU — nu face asta niciodată
answer = "3x^2 - 2"  # string inventat fără verificare
```

### 11.2 Strategii de validare per topic

```python
# derivatives: sp.diff(expr, x) == expected_derivative (simplify first)
# integrals:   sp.integrate(expr, x) == primitive sau sp.integrate(expr, (x,a,b)) == value
# polynomials: sp.rem(f, g, x) == 0 pentru divizibilitate
# matrices:    sp.det(M) == expected_det
# complex:     sp.Abs(z), sp.re(z), sp.im(z), sp.conjugate(z)
# algebraic:   verificare element neutru: law(x, e) == x și law(e, x) == x (sympy.simplify)
# limits:      sp.limit(expr, x, point) == expected_value
```

### 11.3 Garduri de siguranță

```python
def is_valid_exercise(params: dict, answer) -> bool:
    """Verificări comune tuturor generatoarelor."""
    
    # 1. Răspunsul nu trebuie să fie indefinit sau NaN
    if answer is None or answer == sp.nan or answer == sp.zoo:
        return False
    
    # 2. Expresia finală nu trebuie să fie prea simplă (trivial)
    # (ex: derivata unui constant → 0)
    if answer == 0 and params.get("type") == "derivative":
        return False
    
    # 3. LaTeX generat nu trebuie să fie prea lung (>300 char = prea complex pentru exam)
    try:
        latex_str = sp.latex(answer)
        if len(latex_str) > 300:
            return False
    except Exception:
        return False
    
    # 4. Coeficienții din răspuns trebuie să fie rezonabili (|coeff| ≤ 1000)
    # (evite răspunsuri cu numere uriașe)
    
    # 5. Domeniul funcției trebuie să fie non-trivial (mai mult de un punct)
    
    return True
```

### 11.4 Cazuri edge de evitat

```python
# LOGARITMI: evitați log(0) sau log(negativ) în domeniu
# → Generați coeficienți care asigură discriminant > 0 în argumentul log

# RADICALI: evitați √(negativ)
# → Verificați că expresia de sub radical este ≥ 0 pe domeniu

# MATRICE: evitați matrice cu det=0 când se cere inversabilitate
# → Generați matricea și verificați det ≠ 0

# INTEGRALE: evitați singularități pe intervalul de integrare
# → Verificați că f este continuă pe [a,b]

# POLINOAME: evitați polinoame fără rădăcini reale când problema le cere
# → Verificați discriminant ≥ 0 sau factorizabilitate

# FUNCȚII COMPUSE: asigurați domeniu non-vid pentru compoziție
# → Verificați că Im(g) ⊆ Dom(f) pe intervalul relevant
```

---

## 12. Formatare LaTeX și convenții de output

### 12.1 Convenții generale

Toate string-urile de output trebuie să respecte:

```python
# Mulțimi de numere
LATEX_SETS = {
    "R":    "\\mathbb{R}",
    "N":    "\\mathbb{N}",
    "Z":    "\\mathbb{Z}",
    "Q":    "\\mathbb{Q}",
    "C":    "\\mathbb{C}",
    "R+":   "(0, +\\infty)",
    "R*":   "\\mathbb{R}^*",
}

# Terminologie română corectă
RO_TERMS = {
    "domain":      "domeniu",
    "function":    "funcție",
    "sequence":    "șir",
    "polynomial":  "polinom",
    "matrix":      "matrice",
    "derivative":  "derivată",
    "integral":    "integrală",
    "limit":       "limită",
    "probability": "probabilitate",
}

# Articole și acorduri gramaticale
# "numărul real a" (corect), nu "număr real a" (greșit)
# "funcția f" (corect), nu "funcție f" (greșit)
# "matricea A" (corect), nu "matrice A" (greșit)
# "polinomul f" (corect), nu "polinom f" (greșit)
```

### 12.2 Template-uri de formulare complete

Acestea sunt formulările **exacte** care trebuie reproduse în limbajul exercițiilor, bazate pe analiza examenelor BAC 2015–2025:

```
[FUNCȚIE]
"Se consideră funcția f : ℝ → ℝ, f(x) = [expr]."
"Se consideră funcția f : [dom] → ℝ, f(x) = [expr]."
"Pe mulțimea [M] se definește legea de compoziție x ∗ y = [expr]."
"Se consideră matricea A(x) = [matrice], unde x este număr real."
"Se consideră polinomul f(X) = [expr], unde a este număr real."
"Se consideră șirul (aₙ)ₙ≥₁, definit prin [condiție]."
"Se consideră numerele complexe z₁ = [expr₁] și z₂ = [expr₂]."
"Se consideră progresia aritmetică (aₙ)ₙ≥₁, în care a₂ = [val] și a₃ = [val]."
"Se consideră progresia geometrică (bₙ)ₙ≥₁ cu b₁ = [val] și q = [val]."
"În reperul cartezian xOy se consideră punctele A([x₁],[y₁]) și B([x₂],[y₂])."
"Se consideră triunghiul ABC, dreptunghic în A, cu AB = [val] și BC = [val]."
```

### 12.3 Formatare LaTeX pentru sympy output

```python
def sympy_to_bac_latex(expr, simplify=True) -> str:
    """Convertește o expresie sympy în LaTeX conform convențiilor BAC."""
    import sympy as sp
    
    if simplify:
        expr = sp.simplify(expr)
    
    latex_str = sp.latex(expr)
    
    # Înlocuiri de convenție pentru aspectul BAC
    replacements = {
        r"\log":         r"\ln",                    # sympy folosește \log, BAC-ul folosește \ln sau log_b
        r"e^{":         r"e^{",                    # OK
        r"\left(":      r"(",                      # simplificare paranteze mari inutile
        r"\right)":     r")",
        r"\cdot":       r"\cdot",                  # OK
        r"\mathbb{R}":  r"\mathbb{R}",             # OK
    }
    
    for old, new in replacements.items():
        latex_str = latex_str.replace(old, new)
    
    return f"${latex_str}$"
```

---

## 13. Anti-patternuri și greșeli de evitat

### 13.1 Greșeli de structură

```
❌ GREȘIT: Exerciții cu mai mult de 3 sub-puncte în modul de exerciții individuale
✅ CORECT: Exerciții individuale au un singur enunț + răspuns

❌ GREȘIT: Subiectul I cu itemi de dificultate 3 (prea grei pentru acest subiect)
✅ CORECT: Subiectul I: numai difficulty=1 sau maximum difficulty=2

❌ GREȘIT: Subiectul III cu matrice sau structuri algebrice
✅ CORECT: Subiectul III: NUMAI analiză (derivate, integrale, studiu de funcție)

❌ GREȘIT: M3 cu integrale, numere complexe sau polinoame cu Horner
✅ CORECT: M3: numai topic-urile din PROFILE_TOPICS["M3"]

❌ GREȘIT: M2 cu rădăcini ale unității sau forma trigonometrică a complexelor
✅ CORECT: M2 cu numere complexe: numai forma algebrică, calcul cu Re/Im/modul

❌ GREȘIT: M3 cu matrice 3×3
✅ CORECT: M3: numai matrice 2×2
```

### 13.2 Greșeli de aleatorism

```
❌ GREȘIT: Aceeași formulare cu parametri diferiți în același set de exerciții
  (ex: 3 exerciții consecutive de forma "Rezolvați 2^x · k^x = val")
✅ CORECT: Rotire prin subtip-uri diferite chiar în cadrul aceluiași topic

❌ GREȘIT: Coeficienți mari care fac calculul imposibil fără calculator
  (ex: 2^(1543) sau log(732849))
✅ CORECT: Coeficienți care duc la răspunsuri "curate" (întregi, fracții simple, √2, √3)

❌ GREȘIT: Combinarea a 2+ topics diferite într-un singur item (ex: logaritm+matrice)
✅ CORECT: Fiecare item are un singur topic_code clar

❌ GREȘIT: Semințe consecutive generează seturi identice (bug de aleatorism)
✅ CORECT: Sămânța derivată per item: seed_{i}_{topic} garantează unicitate
```

### 13.3 Greșeli de validare matematică

```
❌ GREȘIT: Returnarea unui răspuns calculat cu float (floating point errors)
  ex: 0.9999999999 în loc de 1
✅ CORECT: Utilizare exclusivă sympy (calcul simbolic exact)

❌ GREȘIT: Verificarea cu == în loc de sp.simplify(expr1-expr2)==0
✅ CORECT: sp.simplify(computed - expected) == 0

❌ GREȘIT: Exerciții cu domeniu gol (ex: log(x²+1)=log(-5) fără soluții)
✅ CORECT: Verificați că exercițiul are cel puțin o soluție înainte de a-l returna

❌ GREȘIT: Derivata calculată manual (string manipulation)
✅ CORECT: sp.diff(expr, x), niciodată manual

❌ GREȘIT: Parametri generați aleator care produc singularități în domeniu
✅ CORECT: Validare că pe intervalul problemei nu există puncte de discontinuitate
```

### 13.4 Greșeli de limbaj și formulare

```
❌ GREȘIT: Formulări în engleză ("Calculate the derivative")
✅ CORECT: Formulări în română ("Calculați derivata")

❌ GREȘIT: "Fie funcția f..." (incorect conform stilului BAC)
✅ CORECT: "Se consideră funcția f..."

❌ GREȘIT: "Aflați x pentru care..."
✅ CORECT: "Determinați numărul real x pentru care..."

❌ GREȘIT: "Demonstrați/Arătați că 2+2=4" (trivial, fără calcul)
✅ CORECT: Ceva care necesită minim 2-3 pași non-triviali

❌ GREȘIT: Hint care dă răspunsul direct
✅ CORECT: Hint care indică metoda: "Folosiți regula produsului pentru derivată."
```

---

## 14. Checklist de implementare

### 14.1 Prioritatea de implementare

Aceasta este ordinea recomandată de implementare a generatoarelor:

**Faza 1 — Fundație** (cel mai impactant pentru simulare):
1. `derivatives` — prezent în Subiectul I și III (toate profilele)
2. `integrals` — Subiectul III (M1, M2)
3. `matrices` — Subiectul II și III/M3 (toate profilele)
4. `algebraic_structures` — Subiectul II (M1/M2) și II+III/M3

**Faza 2 — Subiectul I și completare M1**:
5. `logarithms` — Subiectul I item 1 sau 3
6. `complex` — Subiectul I item 1 (M1)
7. `polynomials` — Subiectul II problema 2 (M1/M2)
8. `geometry` — Subiectul I item 5 (toate)
9. `trigonometry` — Subiectul I item 6 (toate)
10. `combinatorics` — Subiectul I item 4 (toate)

**Faza 3 — Completare M2, M3, și topic-uri suplimentare**:
11. `progressions` — Subiectul I item 1 (M2, M3)
12. `sequences` — M1/M2
13. `limits` — M1/M2
14. `powers` — Subiectul I item 3 (M1/M2)
15. `statistics` — M3
16. `systems` — M1/M2 Subiectul II

### 14.2 Checklist per generator

Pentru fiecare generator implementat, verificați:

- [ ] `TOPIC_CODE` unic și corect
- [ ] `SUPPORTED_PROFILES` corect (M3 exclus de la complex, integrale etc.)
- [ ] `_generate_params()` returnează dict valid pentru toate difficulty=1,2,3
- [ ] `_compute_answer()` folosește EXCLUSIV sympy
- [ ] `_validate()` returnează False pentru exerciții triviale sau cu probleme
- [ ] `_build_question()` returnează LaTeX în română, conform template-urilor
- [ ] `_build_hint()` oferă indiciu metodic (nu răspunsul)
- [ ] `generate()` nu aruncă excepție în >95% din apeluri
- [ ] Sămânța produce rezultate reproductibile
- [ ] LaTeX-ul se randează corect în KaTeX

### 14.3 Checklist pentru SimulateView

- [ ] Structura returnată include subiect_I, subiect_II, subiect_III
- [ ] Subiectul I are exact 6 itemi, fiecare 5p
- [ ] Subiectul II are 2 probleme × 3 sub-itemi (a,b,c) × 5p fiecare
- [ ] Subiectul III are 2 probleme × 3 sub-itemi (a,b,c) × 5p fiecare
- [ ] Total: 90p + 10p oficiu = 100p
- [ ] M3: Subiectul II are 6 itemi pe același topic (lege de compoziție)
- [ ] M3: Subiectul III are 6 itemi pe același topic (matrice 2×2)
- [ ] Dificultatea crește progresiv în cadrul fiecărei probleme din Subiectele II și III
- [ ] Seed-ul reproduce complet același subiect

### 14.4 Checklist de testare finală

```python
# Test de reproducibilitate
result1 = generate_exercises("M1", ["derivatives"], 2, 10, seed="test123")
result2 = generate_exercises("M1", ["derivatives"], 2, 10, seed="test123")
assert result1 == result2, "Seed trebuie să reproducă același set"

# Test de varietate
results = [generate_exercises("M1", ["derivatives"], 2, 5, seed=str(i)) for i in range(20)]
questions = [item["question_latex"] for r in results for item in r["items"]]
assert len(set(questions)) > 50, "Varietate insuficientă"

# Test de corectitudine matematică (sample)
for profile in ["M1", "M2", "M3"]:
    sim = generate_full_simulation(profile)
    assert sim["subiect_I"]["points"] == 30
    assert len(sim["subiect_I"]["items"]) == 6
    assert all(item["points"] == 5 for item in sim["subiect_I"]["items"])

# Test de profile restriction
m3_sim = generate_full_simulation("M3")
topics_used = [item["topic"] for item in m3_sim["subiect_I"]["items"]]
assert "complex" not in topics_used, "M3 nu trebuie să aibă numere complexe"
assert "integrals" not in topics_used, "M3 nu trebuie să aibă integrale"
```

---

## Referințe — Surse examene analizate

Analiza de mai sus se bazează pe examinarea sistematică a variantelor oficiale de bacalaureat disponibile la `pro-matematica.ro`, pentru sesiunile:

- **BAC 2015–2025**, sesiunile I (vară), II (toamnă), speciale și simulări
- Profile: M_mate-info (M1), M_șt-nat (M2), M_pedagogic (M3), M_tehnologic (M3)
- Total ~60+ subiecte analizate structural

**Observații cheie cross-year**:
1. Structura (6 itemi × 5p în Subiectul I, 2×3 sub-puncte în II și III) este **invariantă** din 2015 încoace.
2. Topic-ul "matrice cu proprietate A(x)·A(y)=A(x+y)" apare cu frecvență ridicată în Subiectul II.
3. "Demonstrați că ecuația f(x)=0 are exact k soluții" este cerința canonical de dificultate 3 în Subiectul III.
4. M3 a menținut constant formatul: Subiectul II = lege de compoziție (6 itemi), Subiectul III = matrice 2×2 (6 itemi).
5. M2 include din ce în ce mai frecvent legi de compoziție (importate de la M1) față de perioadele anterioare.

---

*Document generat pentru Algomate — platforma de generare procedurală a exercițiilor de matematică pentru bacalaureatul românesc. Versiune: 1.0. Ultima actualizare bazată pe examenele BAC 2025.*