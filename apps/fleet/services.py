"""Fleet services: state-changing operations for vehicles and assignments."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile

from .models import DriverAssignment, Vehicle


@transaction.atomic
def assign_driver_to_vehicle(
    *,
    driver: DriverProfile,
    vehicle: Vehicle,
    starts_at=None,
) -> DriverAssignment:
    """Assign ``driver`` to ``vehicle``, ending any conflicting active assignments.

    Because a driver and a vehicle may each have only one active assignment,
    any existing active assignment for either side is closed first, inside the
    same transaction.
    """
    now = timezone.now()
    starts_at = starts_at or now

    # Close the driver's current active assignment, if any.
    DriverAssignment.objects.filter(driver=driver, is_active=True).update(
        is_active=False, ends_at=now
    )
    # Close whatever driver currently holds this vehicle, if any.
    DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).update(
        is_active=False, ends_at=now
    )

    return DriverAssignment.objects.create(
        driver=driver,
        vehicle=vehicle,
        starts_at=starts_at,
        is_active=True,
    )


@transaction.atomic
def end_assignment(assignment: DriverAssignment) -> DriverAssignment:
    """End a single active assignment."""
    if assignment.is_active:
        assignment.is_active = False
        assignment.ends_at = timezone.now()
        assignment.save(update_fields=["is_active", "ends_at"])
    return assignment


@transaction.atomic
def deactivate_vehicle(vehicle: Vehicle) -> Vehicle:
    """Remove a vehicle from the live fleet and end its active assignment."""
    now = timezone.now()
    DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).update(
        is_active=False, ends_at=now
    )
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active", "updated_at"])
    return vehicle


@transaction.atomic
def activate_vehicle(vehicle: Vehicle) -> Vehicle:
    """Return a vehicle to the live fleet."""
    vehicle.is_active = True
    vehicle.save(update_fields=["is_active", "updated_at"])
    return vehicle
