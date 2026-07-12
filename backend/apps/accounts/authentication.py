"""JWT authentication that enforces a single active session per account.

Each login rotates the user's ``active_session_id`` and stamps it into the token
as the ``sid`` claim (see the login serializer). Here we reject any token whose
``sid`` no longer matches — so when a new login happens, every previously issued
token stops working on its next request. Newest login wins.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class SingleSessionJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        sid = validated_token.get("sid")
        if not sid or sid != (user.active_session_id or ""):
            raise AuthenticationFailed(
                detail="Sesiune încheiată: contul a fost accesat pe alt dispozitiv.",
                code="session_superseded",
            )
        return user
