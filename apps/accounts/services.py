"""Account services: state-changing operations for users and driver profiles."""

from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.db import transaction
from django.utils import timezone

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
        username=username.strip(),
        password=password,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )
    driver_group, _ = Group.objects.get_or_create(name=settings.DRIVER_GROUP)
    user.groups.add(driver_group)
    return DriverProfile.objects.create(
        user=user,
        employee_id=(employee_id or "").strip() or None,
        phone_number=phone_number.strip(),
    )


@transaction.atomic
def update_driver(
    profile: DriverProfile,
    *,
    first_name: str = "",
    last_name: str = "",
    employee_id: str | None = None,
    phone_number: str = "",
    new_password: str = "",
) -> DriverProfile:
    """Update a driver's user identity, profile metadata, and optional password."""
    user = profile.user
    user.first_name = first_name.strip()
    user.last_name = last_name.strip()
    update_user_fields = ["first_name", "last_name"]
    if new_password:
        user.set_password(new_password)
        update_user_fields.append("password")
    user.save(update_fields=update_user_fields)

    profile.employee_id = (employee_id or "").strip() or None
    profile.phone_number = phone_number.strip()
    profile.save(update_fields=["employee_id", "phone_number", "updated_at"])
    return profile


@transaction.atomic
def deactivate_driver(profile: DriverProfile) -> DriverProfile:
    """Soft-deactivate a driver, end any active assignment/trip, and disable login."""
    from apps.fleet.models import DriverAssignment
    from apps.tracking.models import Trip, TripStatus

    now = timezone.now()
    Trip.objects.filter(driver=profile, status=TripStatus.OPEN).update(
        status=TripStatus.COMPLETED, ended_at=now, updated_at=now
    )
    DriverAssignment.objects.filter(driver=profile, is_active=True).update(
        is_active=False, ends_at=now
    )
    profile.is_active = False
    profile.save(update_fields=["is_active", "updated_at"])
    user = profile.user
    user.is_active = False
    user.save(update_fields=["is_active"])
    return profile


@transaction.atomic
def activate_driver(profile: DriverProfile) -> DriverProfile:
    """Re-enable a deactivated driver account and ensure Driver group membership."""
    from django.conf import settings

    profile.is_active = True
    profile.save(update_fields=["is_active", "updated_at"])
    user = profile.user
    user.is_active = True
    user.save(update_fields=["is_active"])
    driver_group, _ = Group.objects.get_or_create(name=settings.DRIVER_GROUP)
    user.groups.add(driver_group)
    return profile
