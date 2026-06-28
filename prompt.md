# Algomate — Romanian Baccalaureate Math Exercise Generator

> A high-fidelity, customizable practice platform that procedurally generates math
> exercises calibrated to the official Romanian Baccalaureate (BAC) syllabus across
> all profiles (mate-info / M1, științele naturii / M2, pedagogic & tehnologic / M3).

---

## 1. Vision

Romanian high-school students preparing for the BAC need **massive amounts of varied
practice** at the exact difficulty and topic distribution of the real exam. Existing
options — printed problem books, scanned PDFs, ad-hoc generators — give them either
finite, repetitive material or low-fidelity randomization that doesn't match the
official subject structure (MEN / variante oficiale Edu.ro).

**Algomate** solves this by combining:

1. A **deterministic, parametric exercise engine** built on top of `sympy` that
   guarantees mathematically valid problems with correct hints and worked
   solutions — not just numeric answers.
2. A **profile-aware curriculum model** that mirrors the official MEN programs
   for M_mate-info, M_șt-nat, M_pedagogic, M_tehnologic, so each generated set
   stays inside what the student is actually examined on.
3. A **session-oriented practice UI** that supports targeted drilling
   (single topic, single difficulty) and full **simulated subiecte** —
   3-part exam papers matching the real BAC structure (SUBIECTUL I, II, III).
4. **Persistent accounts** so users can save practice sessions, track which
   topics they've mastered, and resume where they left off.

The platform is in **Romanian** (UI, exercise text, hints). It MUST render
math correctly (KaTeX) on every page, on mobile and desktop.

---

## 2. Romanian BAC Math — Curriculum Research

The Romanian BAC math exam is split by liceu profile. The exam structure is
the same for all profiles (3 subiecte × ~30 points each, plus 10 points "din
oficiu"), but the **topics and difficulty differ significantly**.

### 2.1 M_mate-info ("M1") — Real, Matematică-Informatică

Hardest profile. 4h+/week of math throughout high school. Topics include:

- **Algebra IX–X**: sets, real-number properties, intervals, modul, partea
  întreagă, powers & radicals, logarithms, exponential & logarithmic
  equations & inequalities, complex numbers (algebraic & trigonometric form,
  roots of unity), polynomials (Bézout, Horner, divisibility, fundamental
  theorem of algebra).
- **Algebra XI–XII**: matrices (operations, determinants up to 3×3, rank,
  inverse), systems of linear equations (Cramer, Gauss), algebraic structures
  (monoizi, groups, rings, fields — `(Z_n, +, ·)`, `M_n(R)`, polynomial rings).
- **Geometry & trig**: triangle geometry (sine/cosine theorem, area
  formulas), vectors in plane, analytic geometry of line and circle.
- **Analysis XI**: sequences (monotonicity, boundedness, Weierstrass,
  Cesàro–Stolz), limits of functions, continuity, **derivatives** (rules,
  Fermat, Rolle, Lagrange, applications: monotonicity, extrema, convexity,
  l'Hôpital).
- **Analysis XII**: primitives (table, integration by parts, substitution),
  Riemann integral, applications (area under curve, volume of revolution).

### 2.2 M_șt-nat ("M2") — Real, Științele Naturii

Mid-tier. ~3h/week. Same big areas as M1 but **reduced scope**:

- Complex numbers usually only in algebraic form (no roots of unity, no
  trig form).
- Matrices typically only up to 2×2 / 3×3 with simpler determinant problems.
- Algebraic structures dropped or very limited.
- Polynomials covered but Horner/Bézout less emphasized.
- Analysis: limits, continuity, derivatives, primitives, integrals — mostly
  **applied** problems (compute, find extrema), fewer theorem-heavy problems.

### 2.3 M_pedagogic and M_tehnologic ("M3")

Basic tier. ~2h/week. Focus is on **applications**, not proofs:

- Functions: linear, quadratic, exponential, logarithmic (basic).
- Sequences (arithmetic & geometric progressions — recognition, sum formulas).
- Combinatorics and basic probability.
- Statistics (mean, median, mode, variance).
- Trigonometry basics, planar geometry.
- Some calculus (derivatives of simple polynomials, basic applications).
- No abstract algebra, no complex analysis-style proofs.

### 2.4 Exam paper structure (all profiles)

- **SUBIECTUL I** (30p): 6 short items — usually computation, identities,
  one-step problems.
- **SUBIECTUL II** (30p): 2 longer problems — typically matrices/systems
  + algebraic structures (M1), or matrices + a second algebra block.
- **SUBIECTUL III** (30p): 2 longer problems — analysis (function study
  using derivatives + integration / area).
- 10p **din oficiu**.
- Duration: 3h. Calculator forbidden.

### 2.5 Topic taxonomy used by the platform

Each generator is keyed by `(profile, topic_code, difficulty)`. The seed
taxonomy (extensible later):

| code            | label                                  | profiles      |
|-----------------|----------------------------------------|---------------|
| `powers`        | Puteri și radicali                     | M1, M2, M3    |
| `logarithms`    | Logaritmi (ecuații, inecuații)         | M1, M2        |
| `complex`       | Numere complexe (algebrică & trig)     | M1, M2 (alg.) |
| `polynomials`   | Polinoame (Horner, Bézout, rădăcini)   | M1, M2        |
| `matrices`      | Matrice & determinanți                 | M1, M2        |
| `systems`       | Sisteme liniare (Cramer, Gauss)        | M1, M2        |
| `groups`        | Structuri algebrice (grup, inel)       | M1            |
| `sequences`     | Șiruri (limită, monotonie)             | M1, M2        |
| `limits`        | Limite de funcții                      | M1, M2        |
| `derivatives`   | Derivate (reguli + studiu de funcție)  | M1, M2, M3*   |
| `integrals`     | Primitive & integrale                  | M1, M2        |
| `geometry`      | Geometrie plană & analitică            | M1, M2, M3    |
| `trigonometry`  | Trigonometrie                          | M1, M2, M3    |
| `combinatorics` | Combinatorică & probabilități          | M1, M2, M3    |
| `statistics`    | Statistică                             | M3            |
| `progressions`  | Progresii aritm. & geom.               | M3, M2        |

*M3 derivatives are restricted to polynomials and simple compositions.

---

## 3. Tech Stack

### 3.1 Backend — Python 3.11 + Django 5 + DRF + Postgres

- `Django 5` + `djangorestframework` for the JSON API.
- `djangorestframework-simplejwt` for stateless auth (access + refresh tokens).
- `sympy` for symbolic math — guarantees algebraic correctness in generators
  (we never trust hand-rolled string substitution for the answer).
- `psycopg[binary]` driver, `dj-database-url` for env-driven DB config.
- `django-cors-headers` (allowlist only).
- `python-decouple` / `os.environ` for all secrets.
- `gunicorn` + `whitenoise` for prod static; reverse-proxied behind nginx.

#### App layout

```
backend/
  algomate/           # project (settings, urls, wsgi, asgi)
    settings/
      base.py
      development.py
      production.py
  apps/
    accounts/         # custom user, JWT views, register/login/me
    exercises/        # generator engine, sessions, /api/exercises/generate
    blog/             # public blog posts
    core/             # contact form, health check
```

#### API surface (versioned `/api/v1/`)

| Method | Path                              | Description                                |
|--------|-----------------------------------|--------------------------------------------|
| GET    | `/api/v1/health/`                 | liveness probe                             |
| POST   | `/api/v1/auth/register/`          | create account                             |
| POST   | `/api/v1/auth/login/`             | JWT pair                                   |
| POST   | `/api/v1/auth/refresh/`           | refresh access token                       |
| GET    | `/api/v1/auth/me/`                | current user                               |
| GET    | `/api/v1/exercises/topics/`       | list supported (profile, topic) pairs      |
| POST   | `/api/v1/exercises/generate/`     | core generation endpoint                   |
| POST   | `/api/v1/exercises/simulate/`     | full BAC-style simulated paper (I+II+III)  |
| GET    | `/api/v1/exercises/sessions/`     | list user's saved sessions (auth)          |
| POST   | `/api/v1/exercises/sessions/`     | save a session (auth)                      |
| GET    | `/api/v1/blog/posts/`             | paginated blog posts                       |
| GET    | `/api/v1/blog/posts/<slug>/`      | single post                                |
| POST   | `/api/v1/contact/`                | contact form (throttled, no auth)          |

### 3.2 Frontend — React 18 + TypeScript + Vite + Tailwind

- `vite` for fast dev.
- `react-router-dom` for routing.
- `axios` for HTTP with a typed API client + JWT refresh interceptor.
- `katex` + thin `<TeX/>` wrapper for math rendering (same approach as
  the example, but as a real npm dependency, not a CDN injection).
- `tailwindcss` for styling — same visual language as the prototype.
- `lucide-react` icons.

#### Routes

| Path         | Page                                             | Auth |
|--------------|--------------------------------------------------|------|
| `/`          | landing — pitch + try-it-now demo                | no   |
| `/practice`  | core feature — customize & generate exercises    | no   |
| `/simulate`  | full BAC simulation paper                        | no   |
| `/blog`      | blog index                                       | no   |
| `/blog/:slug`| blog post                                        | no   |
| `/contact`   | contact form                                     | no   |
| `/login`     | login                                            | no   |
| `/register`  | register                                         | no   |
| `/dashboard` | user dashboard (saved sessions, progress)        | yes  |

---

## 4. Core Feature — Customizable Exercise Generation

The endpoint `POST /api/v1/exercises/generate/` accepts:

```json
{
  "profile": "M1" | "M2" | "M3",
  "topics": ["derivatives", "powers", ...],
  "difficulty": 1 | 2 | 3,            // 1=easy, 2=medium, 3=hard
  "count": 20,                         // 1..50, hard cap
  "seed": "optional-string"            // reproducible sets
}
```

Response:

```json
{
  "items": [
    {
      "id": "der_a1b2",
      "topic": "derivatives",
      "difficulty": 2,
      "question_latex": "Calculează derivata: $f(x) = 3x^4 - 2x^2$",
      "hint_latex":     "Folosește regula puterii pentru fiecare termen.",
      "answer_latex":   "$f'(x) = 12x^3 - 4x$",
      "steps_latex":    ["...", "..."]   // optional worked steps
    }
  ],
  "seed": "abc123"
}
```

Generation rules:

1. Each generator validates its own output with `sympy` (e.g. the
   derivative answer is `sympy.diff(question_expr)` — we never produce an
   answer that doesn't match).
2. Difficulty controls coefficient ranges, exponent ranges, expression
   depth, and which sub-types of a topic are eligible.
3. Generators are **pure functions** of `(profile, difficulty, rng)` so a
   seed reproduces the exact same set.
4. Output is LaTeX (delimited with `$…$`) so the frontend renders with
   KaTeX. Server never emits raw HTML.

---

## 5. Security (Production Hosting Considerations)

The platform will be deployed publicly, so the baseline ships with:

- **Secrets via env vars only** — `.env` is gitignored; `.env.example`
  ships placeholders. `DJANGO_SECRET_KEY`, `DATABASE_URL`,
  `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` all read from env. Production
  settings refuse to boot if `DJANGO_SECRET_KEY` is unset or default.
- **Strict prod settings**: `DEBUG=False`, `SECURE_SSL_REDIRECT=True`,
  `SECURE_HSTS_SECONDS=31536000`, `SESSION_COOKIE_SECURE=True`,
  `CSRF_COOKIE_SECURE=True`, `SECURE_BROWSER_XSS_FILTER=True`,
  `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF=True`,
  `SECURE_REFERRER_POLICY="same-origin"`.
- **CORS allowlist** (no `*`). Origins set in env.
- **JWT** with short access (15 min) + longer refresh (7 days), rotation
  on refresh, blacklist on logout.
- **DRF throttling** on anonymous endpoints — login, register, contact
  form, exercise generation (anon gets a lower quota).
- **Password validators** — Django's default + min length 10.
- **All SQL through the ORM** — no raw queries in app code.
- **React** auto-escapes; we only call `dangerouslySetInnerHTML` against
  KaTeX output that we ourselves produced from server-supplied LaTeX, and
  we configure KaTeX with `throwOnError: false` and `trust: false` so it
  can't inject arbitrary HTML.
- **Postgres** runs on the same VM, listening only on the Unix socket
  (no TCP port exposed). The Django role is non-superuser with a strong
  env-supplied password.
- **Logging** — structured logs to stdout for the container runtime to
  collect. No PII in logs.
- **Rate limiting at the proxy** (nginx) layer is documented as the
  recommended deployment posture, in addition to DRF throttling.
- **Static admin** — `/admin/` is enabled but should be IP-restricted at
  the proxy in production.
- **CSP** — content security policy header set in production middleware:
  `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
   (for KaTeX); img-src 'self' data:;` — adjust as KaTeX rendering needs.

---

## 6. Non-Goals (for the baseline)

- AI/LLM-generated problems — we want **deterministic, audit-able**
  output. Symbolic generators only.
- Mobile app — responsive web only.
- Payment / subscription tier — not in the baseline.
- Teacher dashboards & classroom management — deferred.

---

## 7. Roadmap after baseline

1. Expand the generator catalog to cover every taxonomy code in §2.5.
2. Per-user progress tracking (which topics, which difficulties solved).
3. PDF export of a generated set / simulated subiect.
4. Spaced-repetition scheduler over saved problems.
5. Public problem library curated from past official BAC papers (text +
   reference, no copyright violation — links to Edu.ro PDFs).
