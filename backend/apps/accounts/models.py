from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Email is the canonical identifier; username is kept for admin compatibility."""

    email = models.EmailField(unique=True)
    profile = models.CharField(
        max_length=4,
        choices=[("M1", "Mate-Info"), ("M2", "Științele Naturii"), ("M3", "Pedagogic / Tehnologic")],
        default="M1",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email
