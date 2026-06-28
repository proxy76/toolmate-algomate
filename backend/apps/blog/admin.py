from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "published_at", "author")
    list_filter = ("is_published",)
    search_fields = ("title", "body_md")
    prepopulated_fields = {"slug": ("title",)}
