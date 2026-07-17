from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .generators import engine
from .generators.registry import PROFILES
from .models import ArchiveCompletion, ExerciseSession
from .serializers import (
    ArchiveProgressSerializer,
    ExamPDFSerializer,
    ExerciseSessionSerializer,
    GenerateRequestSerializer,
    SimulateRequestSerializer,
)
from .throttles import AnonGenerateThrottle

# Shown when a visitor hits a members-only action. Verified accounts bypass these.
_VISITOR_GENERATE_LIMIT = (
    "Ca vizitator poți genera un singur set de exerciții. Creează un cont și "
    "confirmă-ți adresa de email pentru acces nelimitat."
)
_MEMBERS_ONLY_SIMULATION = (
    "Simulările BAC sunt disponibile doar pentru conturi cu emailul confirmat. "
    "Creează un cont și confirmă-ți adresa pentru a genera simulări."
)

User = get_user_model()


def _bump(request, **increments):
    """Atomically increment usage counters for the signed-in user (no-op for
    anonymous callers, so anonymous generations simply aren't attributed)."""
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        User.objects.filter(pk=user.pk).update(
            **{field: F(field) + amount for field, amount in increments.items()}
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
    # Anonymous callers get one set per day (AnonGenerateThrottle); everyone is
    # also bounded by the shared "generate" scope. Verified users skip the former.
    throttle_classes = [AnonGenerateThrottle, ScopedRateThrottle]

    def throttled(self, request, wait):
        if request.user and request.user.is_authenticated:
            raise Throttled(wait=wait, detail="Prea multe cereri. Încearcă din nou în puțin timp.")
        raise Throttled(wait=wait, detail=_VISITOR_GENERATE_LIMIT)

    def post(self, request):
        ser = GenerateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = dict(ser.validated_data)
        data["seed"] = data.get("seed") or None
        try:
            result = engine.generate_exercises(**data)
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        _bump(request, generated_problems=len(result.get("items", [])))
        return Response(result)


class SimulateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "generate"

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": _MEMBERS_ONLY_SIMULATION}, status=status.HTTP_403_FORBIDDEN
            )
        ser = SimulateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            result = engine.generate_full_simulation(
                profile=data["profile"], seed=data.get("seed") or None
            )
        except engine.GenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        _bump(request, generated_tests=1)
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
        _bump(request, downloaded_pdfs=1)
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


class ArchiveProgressView(APIView):
    """Which past BAC problems this user has ticked off, and the ticking itself.

    GET returns the whole set (~2,350 problems is the ceiling, and a realistic user is
    far below it), because /arhiva paginates by exam slot and would otherwise ask again
    on every slider move.
    """

    permission_classes = [permissions.IsAuthenticated]

    def _ids(self, request):
        return list(
            ArchiveCompletion.objects.filter(user=request.user).values_list(
                "problem_id", flat=True
            )
        )

    def get(self, request):
        done = self._ids(request)
        return Response({"count": len(done), "done": done})

    def post(self, request):
        ser = ArchiveProgressSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        problem_id = ser.validated_data["problem_id"]

        if ser.validated_data["done"]:
            # Idempotent: re-ticking is a no-op, not a 400. The client may retry.
            ArchiveCompletion.objects.get_or_create(
                user=request.user, problem_id=problem_id
            )
        else:
            ArchiveCompletion.objects.filter(
                user=request.user, problem_id=problem_id
            ).delete()

        done = self._ids(request)
        return Response({"count": len(done), "done": done})
