from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "profile", "is_staff", "date_joined")
    list_filter = ("profile", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (("Algomate", {"fields": ("profile",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Algomate", {"fields": ("email", "profile")}),)
