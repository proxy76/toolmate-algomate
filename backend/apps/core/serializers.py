from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "body")
        extra_kwargs = {
            "name": {"min_length": 2, "max_length": 120},
            "subject": {"min_length": 3, "max_length": 200},
            "body": {"min_length": 10, "max_length": 4000},
        }
