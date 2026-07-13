"""Local development settings — never use in production."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Print emails to the console instead of sending them locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
FRONTEND_BASE_URL = "http://localhost:5173"
