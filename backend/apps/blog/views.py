from rest_framework import generics, permissions

from .models import BlogPost
from .serializers import BlogPostDetailSerializer, BlogPostListSerializer


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
