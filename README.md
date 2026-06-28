# Algomate

Procedurally generates Romanian Baccalaureate (BAC) math exercises across all
profiles — **M1** (Mate-Info), **M2** (Științele Naturii), **M3** (Pedagogic /
Tehnologic). Every exercise ships with a hint and a `sympy`-verified answer, plus
a "Simulare BAC" mode that follows the official subiect structure (I/II/III).

## Stack

- **Backend** (`backend/`) — Django 5 + DRF + PostgreSQL, JWT auth (simplejwt),
  `sympy`-backed generators. No Docker by design; the target is a single VM with
  Postgres + gunicorn + nginx.
- **Frontend** (`frontend/`) — React 18 + TypeScript + Vite + Tailwind + KaTeX.

## Quick start

```bash
# Backend
cd backend
cp .env.example .env          # then edit the values
python -m venv .venv && . .venv/Scripts/activate   # (.venv/bin/activate on *nix)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
cp .env.example .env          # optional; defaults to the dev proxy
npm install
npm run dev
```

See [`SETUP.md`](SETUP.md) for full local + VM setup, [`PRODUCT.md`](PRODUCT.md)
for product context, and [`DESIGN.md`](DESIGN.md) for the design system.

## Environment

Secrets live in `.env` files, which are **git-ignored**. Copy the tracked
`*.env.example` templates and fill in real values locally — never commit a real
`.env`.
