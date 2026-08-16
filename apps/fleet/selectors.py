"""Fleet selectors: read-only queries. No side effects."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import DriverProfile
from apps.accounts.permissions import RequestUser

from .models import DriverAssignment, Vehicle


def get_active_vehicles() -> QuerySet[Vehicle]:
    """All vehicles currently included in the live fleet."""
    return Vehicle.objects.filter(is_active=True).order_by("bus_number")


def get_active_assignment_for_driver(
    driver: DriverProfile,
) -> DriverAssignment | None:
    """The driver's single active assignment, or None."""
    return (
        DriverAssignment.objects.select_related("vehicle", "driver__user")
        .filter(driver=driver, is_active=True)
        .first()
    )


def get_active_assignment_for_user(
    user: RequestUser,
) -> DriverAssignment | None:
    """Resolve an authenticated user to their active assignment.

    Returns None if the user has no driver profile or no active assignment.
    This is the authoritative driver -> vehicle resolution path.
    """
    profile = getattr(user, "driver_profile", None)
    if profile is None or not profile.is_active:
        return None
    return get_active_assignment_for_driver(profile)


def get_active_assignment_for_vehicle(vehicle: Vehicle) -> DriverAssignment | None:
    """The vehicle's single active assignment, or None."""
    return (
        DriverAssignment.objects.select_related("driver__user")
        .filter(vehicle=vehicle, is_active=True)
        .first()
    )
