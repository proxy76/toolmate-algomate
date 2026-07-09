from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .generators import engine
from .generators.registry import PROFILES
from .models import ExerciseSession
from .serializers import (
    ExamPDFSerializer,
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
                    p: engine.supported_topics(p) for p in PROFILES
                },
            }
        )


class GenerateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        ser = GenerateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = dict(ser.validated_data)
        data["seed"] = data.get("seed") or None
        try:
            result = engine.generate_exercises(**data)
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class SimulateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        ser = SimulateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            result = engine.generate_full_simulation(
                profile=data["profile"], seed=data.get("seed") or None
            )
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class ExportPDFView(APIView):
    """Render a generated mock exam to a BAC-faithful, downloadable PDF."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        ser = ExamPDFSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = dict(ser.validated_data)
        try:
            from .pdf_renderer import render_exam_pdf  # lazy: heavy deps only when used

            pdf_bytes = render_exam_pdf(data)
        except Exception:
            return Response(
                {"detail": "Nu am putut genera PDF-ul. Încearcă din nou."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        session = str(data.get("session", "subiect")).replace(" ", "_")
        response["Content-Disposition"] = (
            f'attachment; filename="algomate_{data["profile"]}_{session}.pdf"'
        )
        return response


class SessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ExerciseSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
