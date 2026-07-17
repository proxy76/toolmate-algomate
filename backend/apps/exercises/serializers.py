from rest_framework import serializers

from .generators.registry import PROFILES
from .models import ArchiveCompletion, ExerciseSession

PROFILE_CHOICES = PROFILES


class GenerateRequestSerializer(serializers.Serializer):
    profile = serializers.ChoiceField(choices=PROFILE_CHOICES)
    topics = serializers.ListField(
        child=serializers.CharField(max_length=40),
        min_length=1,
        max_length=12,
    )
    difficulty = serializers.IntegerField(min_value=1, max_value=3)
    count = serializers.IntegerField(min_value=1, max_value=50)
    seed = serializers.CharField(max_length=64, required=False, allow_blank=True)


class SimulateRequestSerializer(serializers.Serializer):
    profile = serializers.ChoiceField(choices=PROFILE_CHOICES)
    difficulty = serializers.IntegerField(min_value=1, max_value=3, default=2)
    seed = serializers.CharField(max_length=64, required=False, allow_blank=True)


class ExamPDFSerializer(serializers.Serializer):
    """Accepts a /simulate response (plus optional cover metadata) for PDF export."""

    profile = serializers.ChoiceField(choices=PROFILE_CHOICES)
    session = serializers.CharField(max_length=60, required=False, default="Simulare")
    year = serializers.IntegerField(min_value=2000, max_value=2100, required=False, default=2025)
    filiera = serializers.CharField(max_length=400, required=False)
    subiect_I = serializers.DictField(required=True)
    subiect_II = serializers.DictField(required=True)
    subiect_III = serializers.DictField(required=True)


class ExerciseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseSession
        fields = ("id", "profile", "topics", "difficulty", "seed", "items", "created_at")
        read_only_fields = ("id", "created_at")


class ArchiveProgressSerializer(serializers.Serializer):
    """One tick in the archive. `done=false` unticks it, so the client can send the
    state it wants rather than track which verb applies."""

    problem_id = serializers.CharField(
        max_length=ArchiveCompletion._meta.get_field("problem_id").max_length
    )
    done = serializers.BooleanField()
