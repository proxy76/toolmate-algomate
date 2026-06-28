# Algomate — Local & VM setup

The project is split in two: a Django REST backend in `backend/` and a
React TS frontend in `frontend/`. There is **no Docker** by design — the
target is a single VM running Postgres + gunicorn + nginx.

---

## Local development

### Prerequisites
- Python 3.11+
- Node.js 20+
- A running PostgreSQL 15+ (any local install)

### 1. Database
Create the role and database (defaults match `.env.example`):

```sql
CREATE ROLE algomate WITH LOGIN PASSWORD 'algomate';
CREATE DATABASE algomate OWNER algomate;
```

### 2. Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate            # PowerShell
pip install -r requirements.txt
cp .env.example .env                 # then edit DJANGO_SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`, so the SPA at
`http://127.0.0.1:5173` talks to Django without CORS friction.

---

## Production on a single VM

High-level layout:

```
nginx  :443  --->  gunicorn (algomate.wsgi)  :8001
                     |
                     v
                Postgres (Unix socket)
```

### One-time provisioning

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv \
  postgresql nginx certbot python3-certbot-nginx

sudo -u postgres psql -c "CREATE USER algomate WITH PASSWORD '<strong>';"
sudo -u postgres psql -c "CREATE DATABASE algomate OWNER algomate;"

sudo adduser --disabled-password --gecos '' algomate
sudo -u algomate git clone <repo> /home/algomate/app
```

### Backend service

`/etc/systemd/system/algomate.service`:

```ini
[Unit]
Description=Algomate gunicorn
After=network.target postgresql.service

[Service]
User=algomate
WorkingDirectory=/home/algomate/app/backend
EnvironmentFile=/home/algomate/app/backend/.env.production
ExecStart=/home/algomate/app/backend/.venv/bin/gunicorn algomate.wsgi:application \
  --workers 3 --bind 127.0.0.1:8001 --access-logfile - --error-logfile -
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/algomate/app/backend
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

`backend/.env.production` (chmod 600, owned by `algomate`):

```
DJANGO_SETTINGS_MODULE=algomate.settings.production
DJANGO_SECRET_KEY=<openssl rand -hex 32>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=algomate.ro,www.algomate.ro
DATABASE_URL=postgres://algomate:<strong>@/algomate?host=/var/run/postgresql
CORS_ALLOWED_ORIGINS=https://algomate.ro
CSRF_TRUSTED_ORIGINS=https://algomate.ro,https://www.algomate.ro
JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7
```

### Frontend build

```bash
cd /home/algomate/app/frontend
npm ci
VITE_API_BASE=/api/v1 npm run build   # outputs to dist/
```

### nginx

```nginx
server {
  listen 443 ssl http2;
  server_name algomate.ro;

  ssl_certificate     /etc/letsencrypt/live/algomate.ro/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/algomate.ro/privkey.pem;

  # static SPA
  root /home/algomate/app/frontend/dist;
  index index.html;

  # SPA fallback
  location / {
    try_files $uri /index.html;
  }

  # API
  location /api/ {
    proxy_pass         http://127.0.0.1:8001;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
    limit_req zone=api burst=20 nodelay;
  }

  # Lock the admin to your office IP
  location /admin/ {
    allow <your_ip>;
    deny  all;
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "same-origin" always;
}

server {
  listen 80;
  server_name algomate.ro www.algomate.ro;
  return 301 https://algomate.ro$request_uri;
}
```

Add to `nginx.conf` (http block):

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
```

### Deploy cycle

```bash
sudo -u algomate -i
cd app && git pull
cd backend && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
cd ../frontend && npm ci && VITE_API_BASE=/api/v1 npm run build
exit
sudo systemctl restart algomate
sudo systemctl reload nginx
```
