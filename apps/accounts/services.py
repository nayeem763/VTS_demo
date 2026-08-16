"""Account services: state-changing operations for users and driver profiles."""

from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.db import transaction

from .models import DriverProfile


@transaction.atomic
def create_driver(
    *,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    employee_id: str | None = None,
    phone_number: str = "",
) -> DriverProfile:
    """Create a User in the Driver group with an attached DriverProfile."""
    from django.conf import settings

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    driver_group, _ = Group.objects.get_or_create(name=settings.DRIVER_GROUP)
    user.groups.add(driver_group)
    return DriverProfile.objects.create(
        user=user,
        employee_id=employee_id or None,
        phone_number=phone_number,
    )


@transaction.atomic
def deactivate_driver(profile: DriverProfile) -> DriverProfile:
    """Soft-deactivate a driver and disable login without deleting history."""
    profile.is_active = False
    profile.save(update_fields=["is_active", "updated_at"])
    user = profile.user
    user.is_active = False
    user.save(update_fields=["is_active"])
    return profile
