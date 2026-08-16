"""Tracking selectors: read-only queries for live and historical views."""

from __future__ import annotations

from datetime import date, datetime

from django.db.models import QuerySet

from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_vehicles

from .models import Location, Trip, TripStatus


def get_latest_vehicle_location(vehicle: Vehicle) -> Location | None:
    """The most recently captured location for a vehicle, or None."""
    return (
        Location.objects.filter(vehicle=vehicle)
        .select_related("driver__user", "vehicle")
        .order_by("-captured_at")
        .first()
    )


def get_latest_active_vehicle_locations() -> list[tuple[Vehicle, Location | None]]:
    """Return (vehicle, latest_location_or_None) for every active vehicle.

    Including vehicles without a location lets dashboards mark them as
    unavailable. The fleet is small (5-10 vehicles), so a per-vehicle lookup is
    clear and inexpensive.
    """
    results: list[tuple[Vehicle, Location | None]] = []
    for vehicle in get_active_vehicles():
        results.append((vehicle, get_latest_vehicle_location(vehicle)))
    return results


def get_vehicle_trips(*, vehicle: Vehicle, on_date: date | None = None) -> QuerySet[Trip]:
    """Trips for a vehicle, optionally limited to a single local calendar date."""
    qs = Trip.objects.filter(vehicle=vehicle).select_related("vehicle", "driver__user")
    if on_date is not None:
        # __date compares in the active timezone when USE_TZ is True.
        qs = qs.filter(started_at__date=on_date)
    return qs.order_by("-started_at")


def get_trip_points(
    *,
    trip: Trip,
    start: datetime | None = None,
    end: datetime | None = None,
) -> QuerySet[Location]:
    """Points for a trip in ascending capture order, optionally time-bounded."""
    qs = Location.objects.filter(trip=trip)
    if start is not None:
        qs = qs.filter(captured_at__gte=start)
    if end is not None:
        qs = qs.filter(captured_at__lte=end)
    return qs.order_by("captured_at")


def get_open_trip_for_vehicle(vehicle: Vehicle) -> Trip | None:
    """The vehicle's current open trip, or None."""
    return Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).first()
