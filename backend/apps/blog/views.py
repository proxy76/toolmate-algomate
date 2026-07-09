from django.utils import timezone
from rest_framework import generics, permissions

from .models import BlogPost
from .serializers import (
    BlogPostAdminSerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
)


class PostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class PostDetailView(generics.RetrieveAPIView):
    lookup_field = "slug"
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class AdminPostListCreateView(generics.ListCreateAPIView):
    """List every post (incl. drafts) and create new ones — admin only."""

    serializer_class = BlogPostAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = BlogPost.objects.all()

    def perform_create(self, serializer):
        published_at = timezone.now() if serializer.validated_data.get("is_published") else None
        serializer.save(author=self.request.user, published_at=published_at)
