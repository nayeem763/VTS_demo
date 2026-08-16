"""Tracking services: the authoritative state-changing tracking operations.

The central service, :func:`record_vehicle_location`, resolves the vehicle from
the authenticated driver's active assignment (never from client input),
validates the fix, attaches it to the correct open trip (opening one when
needed), and is idempotent on ``client_event_id``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile
from apps.accounts.permissions import RequestUser
from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_assignment_for_user

from .models import Location, Trip, TripStatus
from .validators import (
    validate_accuracy,
    validate_capture_timestamp,
    validate_coordinates,
    validate_speed,
)

logger = logging.getLogger("apps.tracking")


class DomainError(Exception):
    """Base class for tracking domain errors that map to a 4xx response."""


class NoActiveAssignment(DomainError):
    """The user has no active driver assignment, so cannot submit locations."""


class VehicleInactive(DomainError):
    """The assigned vehicle is not part of the live fleet."""


# ---------------------------------------------------------------------------
# Trip lifecycle
# ---------------------------------------------------------------------------
def _is_trip_stale(trip: Trip, *, now: datetime, threshold: timedelta) -> bool:
    """True if the trip has had no fix within ``threshold``."""
    last_captured = (
        trip.locations.order_by("-captured_at").values_list("captured_at", flat=True).first()
    )
    reference = last_captured or trip.started_at
    return (now - reference) > threshold


def open_trip(*, vehicle: Vehicle, driver: DriverProfile, started_at: datetime) -> Trip:
    """Open a new trip for a vehicle, tolerating a concurrent opener."""
    try:
        return Trip.objects.create(
            vehicle=vehicle,
            driver=driver,
            started_at=started_at,
            status=TripStatus.OPEN,
        )
    except IntegrityError:
        # A concurrent request opened the trip first; reuse it.
        existing = Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).first()
        if existing is None:  # pragma: no cover - defensive
            raise
        return existing


def close_trip(trip: Trip, *, reason: str = "") -> Trip:
    """Mark a trip completed. Completed trips accept no further locations."""
    if trip.status != TripStatus.COMPLETED:
        trip.status = TripStatus.COMPLETED
        trip.ended_at = timezone.now()
        trip.save(update_fields=["status", "ended_at", "updated_at"])
        logger.info("Closed trip %s (reason=%s)", trip.pk, reason or "unspecified")
    return trip


def close_open_trip_for_user(user: RequestUser, *, reason: str = "") -> Trip | None:
    """Close the open trip belonging to a driver (used on logout)."""
    profile = getattr(user, "driver_profile", None)
    if profile is None:
        return None
    trip = Trip.objects.filter(driver=profile, status=TripStatus.OPEN).first()
    if trip is not None:
        close_trip(trip, reason=reason)
    return trip


def close_stale_trips(*, threshold_minutes: int | None = None) -> int:
    """Close every open trip with no fix within the inactivity threshold.

    Returns the number of trips closed. Intended to be run on a schedule.
    """
    minutes = threshold_minutes or settings.TRIP_INACTIVITY_MINUTES
    threshold = timedelta(minutes=minutes)
    now = timezone.now()
    closed = 0
    for trip in Trip.objects.filter(status=TripStatus.OPEN):
        if _is_trip_stale(trip, now=now, threshold=threshold):
            close_trip(trip, reason="stale_batch")
            closed += 1
    return closed


def _get_or_open_trip(*, vehicle: Vehicle, driver: DriverProfile, captured_at: datetime) -> Trip:
    """Return the vehicle's current open trip, starting a fresh one if needed.

    A stale open trip (idle past the inactivity threshold) is closed and a new
    trip is opened, so a resumed session after a long gap starts cleanly.
    """
    threshold = timedelta(minutes=settings.TRIP_INACTIVITY_MINUTES)
    now = timezone.now()
    open_trip_qs = Trip.objects.select_for_update().filter(vehicle=vehicle, status=TripStatus.OPEN)
    current = open_trip_qs.first()
    if current is not None:
        if _is_trip_stale(current, now=now, threshold=threshold):
            close_trip(current, reason="stale_on_ingest")
        else:
            return current
    return open_trip(vehicle=vehicle, driver=driver, started_at=captured_at)


# ---------------------------------------------------------------------------
# Location ingestion
# ---------------------------------------------------------------------------
@transaction.atomic
def record_vehicle_location(
    *,
    user: RequestUser,
    client_event_id,
    latitude: Decimal,
    longitude: Decimal,
    captured_at: datetime,
    speed_kmh: Decimal | None = None,
    accuracy_m: Decimal | None = None,
) -> tuple[Location, bool]:
    """Validate and persist a driver's GPS fix under the correct trip.

    Returns ``(location, created)``. ``created`` is False when the
    ``client_event_id`` was already recorded (idempotent retry).
    """
    # Idempotency: a retried submission returns the original record.
    existing = Location.objects.filter(client_event_id=client_event_id).first()
    if existing is not None:
        return existing, False

    # Authoritative vehicle resolution: from the assignment, never the client.
    assignment = get_active_assignment_for_user(user)
    if assignment is None:
        raise NoActiveAssignment("No active vehicle assignment for this driver.")
    if not assignment.vehicle.is_active:
        raise VehicleInactive("The assigned vehicle is not active.")

    # Authoritative domain validation (mirrors DB constraints).
    validate_coordinates(latitude, longitude)
    validate_speed(speed_kmh)
    validate_accuracy(accuracy_m)
    validate_capture_timestamp(captured_at)

    driver = assignment.driver
    vehicle = assignment.vehicle
    trip = _get_or_open_trip(vehicle=vehicle, driver=driver, captured_at=captured_at)

    try:
        location = Location.objects.create(
            vehicle=vehicle,
            driver=driver,
            trip=trip,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            accuracy_m=accuracy_m,
            captured_at=captured_at,
            client_event_id=client_event_id,
        )
    except IntegrityError:
        # Concurrent duplicate of the same client_event_id.
        duplicate = Location.objects.filter(client_event_id=client_event_id).first()
        if duplicate is not None:
            return duplicate, False
        raise

    return location, True
