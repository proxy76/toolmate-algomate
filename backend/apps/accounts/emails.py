"""Email-verification tokens + the confirmation email.

Tokens are stateless: a signed, time-limited payload (Django's signing), so no
extra table or cleanup is needed. A token stays valid for ``MAX_AGE`` seconds and
simply carries the user id.
"""
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail

SALT = "accounts.email-verify"
MAX_AGE = 60 * 60 * 24  # 24 hours


def make_token(user) -> str:
    return signing.dumps({"uid": user.pk}, salt=SALT)


def read_token(token: str):
    """Return the user id encoded in a valid token, or ``None`` if it's invalid
    or older than ``MAX_AGE``."""
    try:
        data = signing.loads(token, salt=SALT, max_age=MAX_AGE)
    except signing.BadSignature:
        return None
    return data.get("uid")


def send_verification_email(user) -> None:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/verify?token={make_token(user)}"
    body = (
        f"Bună, {user.username}!\n\n"
        "Îți mulțumim că ți-ai creat un cont Algomate. Confirmă-ți adresa de "
        "email accesând linkul de mai jos:\n\n"
        f"{link}\n\n"
        "Linkul expiră în 24 de ore. Dacă nu tu ai creat acest cont, poți ignora "
        "acest mesaj.\n\n"
        "— Echipa Algomate"
    )
    send_mail(
        subject="Confirmă-ți adresa Algomate",
        message=body,
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
        fail_silently=False,
    )
