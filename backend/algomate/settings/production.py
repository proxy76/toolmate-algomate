"""Production settings — refuses to boot with a default secret key."""
from decouple import config

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY

if not SECRET_KEY or SECRET_KEY.startswith("replace-me") or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "DJANGO_SECRET_KEY must be set to a strong (>=32 char) value in production."
    )

DEBUG = False

# --- HTTPS / cookies ----------------------------------------------------

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# --- HSTS ---------------------------------------------------------------

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- Misc headers -------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# --- CSRF trusted origins (must include scheme) -------------------------

CSRF_TRUSTED_ORIGINS = [
    o for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",") if o.strip()
]
