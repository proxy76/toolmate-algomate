from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "ip_address")
    search_fields = ("email", "subject", "body")
    readonly_fields = ("name", "email", "subject", "body", "created_at", "ip_address")
