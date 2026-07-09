from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login accepts either the email (default) or the username as identifier —
    so the ``admin`` account can sign in with its username, not just its email."""

    def validate(self, attrs):
        identifier = attrs.get(self.username_field)
        if identifier and "@" not in identifier:
            match = User.objects.filter(username__iexact=identifier).first()
            if match:
                attrs[self.username_field] = match.email
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password", "profile")
        extra_kwargs = {
            "username": {"required": True, "min_length": 3, "max_length": 50},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
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
        )
        read_only_fields = fields
