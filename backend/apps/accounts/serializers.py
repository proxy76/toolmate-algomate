from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login accepts either the email (default) or the username as identifier —
    so the ``admin`` account can sign in with its username, not just its email.

    Also enforces one active session per account: each login rotates the user's
    ``active_session_id`` and embeds it in the tokens as the ``sid`` claim, so any
    previously issued token is invalidated on the next request (newest login wins;
    see :class:`apps.accounts.authentication.SingleSessionJWTAuthentication`)."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        sid = uuid4().hex
        user.active_session_id = sid
        user.save(update_fields=["active_session_id"])
        token["sid"] = sid  # copied onto the derived access token by SimpleJWT
        return token

    def validate(self, attrs):
        identifier = attrs.get(self.username_field)
        if identifier and "@" not in identifier:
            match = User.objects.filter(username__iexact=identifier).first()
            if match:
                attrs[self.username_field] = match.email
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise AuthenticationFailed(
                detail="Confirmă-ți adresa de email înainte de a te conecta.",
                code="email_not_verified",
            )
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # Consent to the Terms & Privacy Policy. Required and must be True — the
    # timestamp is what we store as proof of consent (GDPR accountability).
    terms_accepted = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password", "profile", "terms_accepted")
        extra_kwargs = {
            "username": {"required": True, "min_length": 3, "max_length": 50},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                "Trebuie să accepți Termenii și Condițiile pentru a crea un cont."
            )
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        validated_data.pop("terms_accepted", None)
        user = User(**validated_data, terms_accepted_at=timezone.now())
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "profile", "date_joined", "is_staff")
        read_only_fields = fields


class AdminUserSerializer(serializers.ModelSerializer):
    """Fuller view of an account, for the admin dashboard's user list."""

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "profile",
            "date_joined", "last_login", "is_active", "is_staff",
            "generated_tests", "generated_problems", "downloaded_pdfs",
            "terms_accepted_at",
        )
        read_only_fields = fields


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
