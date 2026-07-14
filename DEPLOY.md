# Deploy — Algomate (production)

This is the `production` branch: application code only. The exam corpus, download
scripts, and design/planning docs live on `main` and are intentionally absent here.

Target: a single VM (systemd + nginx). No Docker.

- **Backend:** Django + DRF + Gunicorn, served behind nginx, static via WhiteNoise.
- **Frontend:** Vite/React, built to static and served by nginx.
- **DB:** PostgreSQL (SQLite is only a local-dev fallback — never used in prod).

---

## 1. System packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip postgresql nginx git
# Node 20+ for the frontend build (nodesource or nvm)
```

## 2. PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE algomate WITH LOGIN PASSWORD 'CHANGE_ME_STRONG';
CREATE DATABASE algomate OWNER algomate;
ALTER ROLE algomate SET client_encoding TO 'utf8';
ALTER ROLE algomate SET timezone TO 'Europe/Bucharest';
SQL
```

The backend reads the DB from `DATABASE_URL` (via `dj-database-url`), so no code
change is needed — just point it at Postgres:

```
DATABASE_URL=postgres://algomate:CHANGE_ME_STRONG@localhost:5432/algomate
```

## 3. Backend

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example`, never commit it):

```
DJANGO_SETTINGS_MODULE=algomate.settings.production
DJANGO_SECRET_KEY=<50+ random chars>          # prod refuses to boot with a weak/default key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=algomate.ro,www.algomate.ro
DATABASE_URL=postgres://algomate:CHANGE_ME_STRONG@localhost:5432/algomate
CORS_ALLOWED_ORIGINS=https://algomate.ro
CSRF_TRUSTED_ORIGINS=https://algomate.ro,https://www.algomate.ro
JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7
ADMIN_PASSWORD=<strong password>              # see note below
```

Migrate + collect static:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

> **Bootstrap admin.** Migration `accounts.0002_create_admin` creates a superuser
> `admin` / `admin@algomate.ro`. It uses `ADMIN_PASSWORD` if set, otherwise a weak
> default. **Always set a strong `ADMIN_PASSWORD` before the first `migrate`** (or
> rotate the password immediately after), or the account will have a known password.

Run with Gunicorn (bind to a local port; nginx proxies to it):

```bash
gunicorn algomate.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

### systemd unit (`/etc/systemd/system/algomate.service`)

```ini
[Unit]
Description=Algomate Gunicorn
After=network.target postgresql.service

[Service]
User=algomate
WorkingDirectory=/srv/algomate/backend
EnvironmentFile=/srv/algomate/backend/.env
ExecStart=/srv/algomate/backend/.venv/bin/gunicorn algomate.wsgi:application \
          --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now algomate
```

## 4. Frontend

```bash
cd frontend
npm ci
# .env for the build — point at the API served under /api/v1 by nginx:
echo 'VITE_API_BASE=/api/v1' > .env
npm run build          # outputs frontend/dist/
```

## 5. nginx

```nginx
server {
    listen 80;
    server_name algomate.ro www.algomate.ro;

    root /srv/algomate/frontend/dist;
    index index.html;

    # Cap request bodies at the edge (defense-in-depth; Django also caps at 1 MB).
    client_max_body_size 2m;

    location /api/  { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; }

    # Django admin: restrict to trusted IPs so it isn't brute-forceable from the
    # open internet. Replace with your office/VPN address(es), or drop this block
    # entirely if you only administer via the React dashboard + API.
    location /admin/ {
        allow 203.0.113.0/24;   # <-- your admin network
        deny all;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ { proxy_pass http://127.0.0.1:8000; }

    # Content-hashed build assets: safe to cache forever. A genuinely missing
    # asset must 404 — never fall back to index.html, or the browser receives
    # HTML for a .js request and the app fails to boot after a redeploy.
    location /assets/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # SPA shell: always revalidate so a redeploy is picked up immediately and a
    # stale index.html never points at deleted asset hashes.
    location / {
        try_files $uri /index.html;
        add_header Cache-Control "no-cache";
    }
}
```

Then add TLS (e.g. `certbot --nginx`). Production settings force HTTPS redirect,
HSTS, and secure cookies, and honour `X-Forwarded-Proto` from nginx.

> **SPA caching matters.** The app shell (`index.html`) must be served with
> `Cache-Control: no-cache` so browsers always fetch the current build; the
> content-hashed `/assets/*` are immutable and cached hard. Without this, a
> browser holding a stale `index.html` requests asset hashes that a later deploy
> deleted, the fallback returns `index.html` (HTML) for those `.js`/`.css`
> requests, and the page hangs on load. If a CDN (e.g. Cloudflare) sits in front,
> purge its cache after a deploy, or set its Browser Cache TTL to "Respect
> Existing Headers".

## 6. Updating

```bash
git pull origin production
# backend: pip install -r requirements.txt && python manage.py migrate && collectstatic
# frontend: npm ci && npm run build
sudo systemctl restart algomate
```
