from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Email is the canonical identifier; username is kept for admin compatibility."""

    email = models.EmailField(unique=True)
    profile = models.CharField(
        max_length=32,
        choices=[
            ("mate-info", "Matematică–Informatică"),
            ("stiintele-naturii", "Științele Naturii"),
            ("tehnologic", "Tehnologic"),
            ("pedagogic", "Pedagogic"),
        ],
        default="mate-info",
    )

    # --- usage stats (incremented server-side; see apps.exercises.views) -------
    generated_tests = models.PositiveIntegerField(default=0)      # full simulations
    generated_problems = models.PositiveIntegerField(default=0)   # individual exercises
    downloaded_pdfs = models.PositiveIntegerField(default=0)

    # Single active session: each login rotates this id and stamps it into the
    # JWTs; a token whose "sid" no longer matches is rejected (newest login wins).
    active_session_id = models.CharField(max_length=32, blank=True, default="")

    # Email confirmation: new signups must click a link before they can log in.
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email
