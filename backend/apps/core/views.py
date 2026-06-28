from rest_framework import generics, permissions

from .models import ContactMessage
from .serializers import ContactMessageSerializer


def _client_ip(request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ContactView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ContactMessage.objects.all()
    throttle_scope = "contact"

    def perform_create(self, serializer):
        serializer.save(ip_address=_client_ip(self.request))
