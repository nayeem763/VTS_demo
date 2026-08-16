"""Signals that keep role groups present on any freshly migrated database."""

from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_role_groups(sender, **kwargs) -> None:
    """Create the Admin and Driver groups if they do not yet exist.

    Runs after this app's migrations so the auth tables are available.
    """
    if getattr(sender, "label", None) != "accounts":
        return

    from django.contrib.auth.models import Group

    for group_name in (settings.ADMIN_GROUP, settings.DRIVER_GROUP):
        Group.objects.get_or_create(name=group_name)
