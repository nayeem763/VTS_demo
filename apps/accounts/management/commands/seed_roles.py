"""Create the Admin and Driver role groups. Idempotent."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the Admin and Driver role groups if they do not exist."

    def handle(self, *args, **options) -> None:
        for name in (settings.ADMIN_GROUP, settings.DRIVER_GROUP):
            _, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "exists"
            self.stdout.write(f"Group {name!r}: {status}")
        self.stdout.write(self.style.SUCCESS("Role groups are ready."))
