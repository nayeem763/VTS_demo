"""Tracking selectors: read-only queries for live and historical views."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from django.db.models import OuterRef, QuerySet, Subquery

from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_vehicles

from .models import Location, Trip, TripStatus


def get_latest_vehicle_location(vehicle: Vehicle) -> Location | None:
    """The most recently captured location for a vehicle, or None."""
    return (
        Location.objects.filter(vehicle=vehicle)
        .select_related("driver__user", "vehicle")
        .order_by("-captured_at", "-id")
        .first()
    )


def get_latest_active_vehicle_locations() -> list[tuple[Vehicle, Location | None]]:
    """Return (vehicle, latest_location_or_None) for every active vehicle in O(1) queries.

    Including vehicles without a location lets dashboards mark them as
    unavailable while avoiding per-vehicle N+1 queries on the public live feed.
    """
    latest_loc_pk = (
        Location.objects.filter(vehicle_id=OuterRef("pk"))
        .order_by("-captured_at", "-id")
        .values("pk")[:1]
    )
    vehicles = list(get_active_vehicles().annotate(_latest_loc_id=Subquery(latest_loc_pk)))
    loc_ids = [v._latest_loc_id for v in vehicles if v._latest_loc_id is not None]
    locations_by_id = {
        loc.pk: loc
        for loc in Location.objects.filter(pk__in=loc_ids).select_related("driver__user", "vehicle")
    }
    return [(v, locations_by_id.get(v._latest_loc_id)) for v in vehicles]


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
    # ``id`` makes the order stable even if two fixes have the same device
    # timestamp.  A stable chronological sequence is essential for drawing a
    # route through every reported coordinate.
    return qs.order_by("captured_at", "id")


def get_location_trajectory(location: Location | None) -> list[Location]:
    """Return the complete, ordered trace for a location's trip.

    A location is the current end of a driver's session.  Its trip contains
    the exact sequence of GPS fixes needed by the live map to preserve turns
    and detours between the first and latest fixes.
    """
    if location is None:
        return []
    return list(
        Location.objects.filter(trip_id=location.trip_id)
        .order_by("captured_at", "id")
        .only("latitude", "longitude", "captured_at")
    )


def get_trajectories_for_locations(locations: list[Location]) -> dict[int, list[Location]]:
    """Batch-fetch ordered trip traces for a set of latest locations in one SQL query."""
    trip_ids = {loc.trip_id for loc in locations if loc is not None}
    if not trip_ids:
        return {}
    by_trip: dict[int, list[Location]] = defaultdict(list)
    points = (
        Location.objects.filter(trip_id__in=trip_ids)
        .order_by("captured_at", "id")
        .only("trip_id", "latitude", "longitude", "captured_at")
    )
    for point in points:
        by_trip[point.trip_id].append(point)
    return dict(by_trip)


def get_open_trip_for_vehicle(vehicle: Vehicle) -> Trip | None:
    """The vehicle's current open trip, or None."""
    return Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).first()
