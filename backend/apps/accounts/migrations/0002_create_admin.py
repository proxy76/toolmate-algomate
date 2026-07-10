"""Create the bootstrap admin account.

Idempotent: only creates ``admin`` if it does not already exist. The password
defaults to the value requested for local/early-access use but can be overridden
per-environment with the ``ADMIN_PASSWORD`` env var (set a strong one in prod).
"""
import os

from django.contrib.auth.hashers import make_password
from django.db import migrations

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@algomate.ro"
DEFAULT_PASSWORD = "admin#hjfbdk2k&g%fbl#fhly@fvcjy676teggjju97h-4gf"


def create_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    if User.objects.filter(username__iexact=ADMIN_USERNAME).exists():
        return
    if User.objects.filter(email__iexact=ADMIN_EMAIL).exists():
        return
    User.objects.create(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=make_password(os.environ.get("ADMIN_PASSWORD", DEFAULT_PASSWORD)),
        is_staff=True,
        is_superuser=True,
        is_active=True,
        profile="M1",
    )


def remove_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username__iexact=ADMIN_USERNAME, email__iexact=ADMIN_EMAIL).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.RunPython(create_admin, remove_admin)]
