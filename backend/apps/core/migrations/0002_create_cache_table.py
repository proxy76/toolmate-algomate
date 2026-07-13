"""Create the database cache table used by the default cache backend.

Runs Django's ``createcachetable`` (idempotent) so the throttle-backing table
exists after a plain ``migrate`` — no separate manual step on deploy.
"""
from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    call_command("createcachetable", database=schema_editor.connection.alias)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_cache_table, migrations.RunPython.noop),
    ]
