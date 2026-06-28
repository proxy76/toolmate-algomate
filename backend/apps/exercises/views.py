from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import engine
from .models import ExerciseSession
from .serializers import (
    ExerciseSessionSerializer,
    GenerateRequestSerializer,
    SimulateRequestSerializer,
)


class TopicsView(APIView):
    """List the (profile, topic) catalogue so the frontend can render menus."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "labels": engine.all_topic_labels(),
                "by_profile": {
                    p: engine.supported_topics(p) for p in ("M1", "M2", "M3")
                },
            }
        )


class GenerateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        ser = GenerateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            result = engine.generate_set(**ser.validated_data)
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class SimulateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        ser = SimulateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            result = engine.simulate_bac(**ser.validated_data)
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class SessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ExerciseSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
