from django.conf import settings
from django.db import models


class ExerciseSession(models.Model):
    """A snapshot of a generated set so users can revisit it later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_sessions",
    )
    profile = models.CharField(max_length=32)
    topics = models.JSONField(default=list)
    difficulty = models.PositiveSmallIntegerField()
    seed = models.CharField(max_length=64)
    items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user_id} {self.profile} {self.topics} d{self.difficulty}"


class ArchiveCompletion(models.Model):
    """A past BAC problem the user has ticked off in /arhiva.

    The archive itself is static files served by nginx — the API never sees a problem,
    only the id printed in its manifest (`mate-info-1-1/2026-model-114`). So this table
    is the whole of what the server knows about a student's way through it: one row per
    problem solved, its absence meaning not-yet.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="archive_completions",
    )
    # Free text on purpose: validating against the manifests would put the API back in
    # the archive's business, and a stale id costs nothing but a row.
    problem_id = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        # The unique index this builds is also the one the lookups want: every query
        # here filters on user, or on user + problem_id.
        constraints = [
            models.UniqueConstraint(
                fields=("user", "problem_id"), name="unique_user_archive_problem"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.problem_id}"
