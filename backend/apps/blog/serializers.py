from rest_framework import serializers

from .models import BlogPost


class BlogPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ("id", "title", "slug", "excerpt", "published_at")


class BlogPostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ("id", "title", "slug", "excerpt", "body_md", "published_at")


class BlogPostAdminSerializer(serializers.ModelSerializer):
    """Full read/write view for the admin dashboard (includes drafts)."""

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlogPost
        fields = (
            "id", "title", "slug", "excerpt", "body_md",
            "is_published", "author", "created_at", "published_at",
        )
        read_only_fields = ("id", "slug", "author", "created_at", "published_at")
