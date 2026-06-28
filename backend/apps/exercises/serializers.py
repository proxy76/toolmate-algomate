from rest_framework import serializers

from .models import ExerciseSession

PROFILE_CHOICES = ("M1", "M2", "M3")


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


class ExerciseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseSession
        fields = ("id", "profile", "topics", "difficulty", "seed", "items", "created_at")
        read_only_fields = ("id", "created_at")
