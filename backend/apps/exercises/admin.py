from django.contrib import admin

from .models import ExerciseSession


@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "profile", "difficulty", "seed", "created_at")
    list_filter = ("profile", "difficulty")
    search_fields = ("user__email", "seed")
    readonly_fields = ("items",)
