"""Throttles for the exercise endpoints."""
from rest_framework.throttling import AnonRateThrottle


class AnonGenerateThrottle(AnonRateThrottle):
    """The 'try once' gate for problem generation.

    Only throttles *anonymous* callers (AnonRateThrottle returns no cache key for
    authenticated users, so email-verified accounts bypass it entirely). Behind
    the Cloudflare tunnel every request reaches the origin from 127.0.0.1, so key
    off the real visitor IP in ``CF-Connecting-IP`` when present.
    """

    scope = "anon_generate"

    def get_ident(self, request):
        return request.META.get("HTTP_CF_CONNECTING_IP") or super().get_ident(request)
