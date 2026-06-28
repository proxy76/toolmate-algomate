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
