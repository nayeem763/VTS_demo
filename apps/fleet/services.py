"""Fleet services: state-changing operations for vehicles and assignments."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile

from .models import DriverAssignment, Vehicle


def _close_open_trips(
    *,
    vehicle: Vehicle | None = None,
    driver: DriverProfile | None = None,
    now=None,
) -> int:
    """Close open tracking trips affected by a fleet assignment/status change."""
    from apps.tracking.models import Trip, TripStatus

    qs = Trip.objects.filter(status=TripStatus.OPEN)
    if vehicle is not None:
        qs = qs.filter(vehicle=vehicle)
    if driver is not None:
        qs = qs.filter(driver=driver)
    if vehicle is None and driver is None:
        return 0
    ts = now or timezone.now()
    return qs.update(status=TripStatus.COMPLETED, ended_at=ts, updated_at=ts)


@transaction.atomic
def create_vehicle(
    *,
    bus_number: str,
    registration_number: str = "",
    route_label: str = "",
    admin_description: str = "",
    is_active: bool = True,
) -> Vehicle:
    """Create a new fleet vehicle with normalized fields."""
    return Vehicle.objects.create(
        bus_number=bus_number.strip(),
        registration_number=registration_number.strip() or None,
        route_label=route_label.strip(),
        admin_description=admin_description.strip(),
        is_active=is_active,
    )


@transaction.atomic
def update_vehicle(
    vehicle: Vehicle,
    *,
    bus_number: str,
    registration_number: str = "",
    route_label: str = "",
    admin_description: str = "",
) -> Vehicle:
    """Rename or update a vehicle's operational metadata and admin-only note."""
    vehicle.bus_number = bus_number.strip()
    vehicle.registration_number = registration_number.strip() or None
    vehicle.route_label = route_label.strip()
    vehicle.admin_description = admin_description.strip()
    vehicle.save(
        update_fields=[
            "bus_number",
            "registration_number",
            "route_label",
            "admin_description",
            "updated_at",
        ]
    )
    return vehicle


@transaction.atomic
def delete_vehicle_if_unused(vehicle: Vehicle) -> tuple[bool, str]:
    """Delete a vehicle only when it has no historical trips, fixes, or assignments."""
    from apps.tracking.models import Location, Trip

    if (
        Trip.objects.filter(vehicle=vehicle).exists()
        or Location.objects.filter(vehicle=vehicle).exists()
        or DriverAssignment.objects.filter(vehicle=vehicle).exists()
    ):
        return (
            False,
            f"{vehicle.bus_number} has historical trips or assignments and cannot be "
            "deleted. Deactivate it instead to preserve audit records.",
        )
    name = vehicle.bus_number
    vehicle.delete()
    return True, f"Deleted vehicle {name}."


@transaction.atomic
def assign_driver_to_vehicle(
    *,
    driver: DriverProfile,
    vehicle: Vehicle,
    starts_at=None,
) -> DriverAssignment:
    """Assign ``driver`` to ``vehicle``, ending any conflicting active assignments.

    Because a driver and a vehicle may each have only one active assignment,
    any existing active assignment (and open live trip) for either side is
    closed first inside the same transaction.
    """
    if not vehicle.is_active:
        raise ValueError(f"Vehicle {vehicle.bus_number} is inactive and cannot be assigned.")
    if not driver.is_active:
        raise ValueError(f"Driver {driver.display_name} is inactive and cannot be assigned.")

    now = timezone.now()
    starts_at = starts_at or now

    # Close any open live trips held by the driver or the target vehicle.
    _close_open_trips(driver=driver, now=now)
    _close_open_trips(vehicle=vehicle, now=now)

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
    """End a single active assignment and close any open live trip for it."""
    if assignment.is_active:
        now = timezone.now()
        _close_open_trips(vehicle=assignment.vehicle, driver=assignment.driver, now=now)
        assignment.is_active = False
        assignment.ends_at = now
        assignment.save(update_fields=["is_active", "ends_at"])
    return assignment


@transaction.atomic
def deactivate_vehicle(vehicle: Vehicle) -> Vehicle:
    """Remove a vehicle from the live fleet, ending its active assignment and open trip."""
    now = timezone.now()
    _close_open_trips(vehicle=vehicle, now=now)
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
