from django.conf import settings
from django.db import models


class ExerciseSession(models.Model):
    """A snapshot of a generated set so users can revisit it later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_sessions",
    )
    profile = models.CharField(max_length=4)
    topics = models.JSONField(default=list)
    difficulty = models.PositiveSmallIntegerField()
    seed = models.CharField(max_length=64)
    items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user_id} {self.profile} {self.topics} d{self.difficulty}"
