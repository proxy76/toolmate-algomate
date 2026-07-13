import logging

from django.contrib.auth import get_user_model
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .emails import read_token, send_verification_email
from .serializers import (
    AdminUserSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)

_CHECK_INBOX = (
    "Contul a fost creat. Ți-am trimis un email de confirmare — "
    "accesează linkul din el pentru a-ți activa contul."
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            send_verification_email(user)
        except Exception:  # don't fail signup if the mail server hiccups
            logger.exception("Failed to send verification email to %s", user.email)
        return Response({"detail": _CHECK_INBOX}, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """Confirm an account from the emailed link's token."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        ser = VerifyEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        uid = read_token(ser.validated_data["token"])
        if uid is None:
            return Response(
                {"detail": "Link invalid sau expirat. Cere un email nou de confirmare."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(pk=uid).first()
        if user is None:
            return Response(
                {"detail": "Cont inexistent."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
        return Response({"detail": "Adresa a fost confirmată. Te poți conecta acum."})


class ResendVerificationView(APIView):
    """Re-send the confirmation email. Always returns a generic message so it
    can't be used to probe which emails are registered."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        ser = ResendVerificationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=ser.validated_data["email"]).first()
        if user and not user.is_email_verified:
            try:
                send_verification_email(user)
            except Exception:
                logger.exception("Failed to resend verification email to %s", user.email)
        return Response(
            {"detail": "Dacă adresa există și nu e confirmată, am retrimis emailul."}
        )


class LoginView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer
    throttle_scope = "auth"


class RefreshView(TokenRefreshView):
    throttle_scope = "auth"


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminUserListView(generics.ListAPIView):
    """All registered accounts with usage stats — admin only (staff).

    Supports ``?search=`` to find a student by username or email.
    """

    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("-date_joined")
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email"]
