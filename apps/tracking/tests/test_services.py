"""Tracking service tests: location ingestion and trip lifecycle."""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.tracking.models import Location, Trip, TripStatus
from apps.tracking.services import (
    NoActiveAssignment,
    VehicleInactive,
    close_open_trip_for_user,
    close_stale_trips,
    close_trip,
    record_vehicle_location,
)

pytestmark = pytest.mark.django_db


def _record(user, **overrides):
    payload = {
        "user": user,
        "client_event_id": overrides.pop("client_event_id", uuid.uuid4()),
        "latitude": Decimal("23.777100"),
        "longitude": Decimal("90.399400"),
        "captured_at": overrides.pop("captured_at", timezone.now()),
    }
    payload.update(overrides)
    return record_vehicle_location(**payload)


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
def test_record_creates_trip_and_location(assigned_driver, vehicle, driver_profile):
    location, created = _record(assigned_driver, speed_kmh=Decimal("30.00"))
    assert created is True
    assert location.vehicle == vehicle
    assert location.driver == driver_profile
    assert location.trip.status == TripStatus.OPEN
    assert Trip.objects.count() == 1
    assert Location.objects.count() == 1


def test_record_is_idempotent_on_client_event_id(assigned_driver):
    eid = uuid.uuid4()
    first, created1 = _record(assigned_driver, client_event_id=eid)
    second, created2 = _record(assigned_driver, client_event_id=eid)
    assert created1 is True
    assert created2 is False
    assert first.id == second.id
    assert Location.objects.count() == 1


def test_record_without_assignment_raises(driver_user):
    with pytest.raises(NoActiveAssignment):
        _record(driver_user)


def test_record_with_inactive_vehicle_raises(assigned_driver, vehicle):
    # Force the vehicle inactive WITHOUT ending the assignment.
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active"])
    with pytest.raises(VehicleInactive):
        _record(assigned_driver)


def test_record_rejects_future_timestamp(assigned_driver):
    with pytest.raises(ValidationError):
        _record(assigned_driver, captured_at=timezone.now() + timedelta(minutes=10))


def test_consecutive_fixes_share_open_trip(assigned_driver):
    _record(assigned_driver)
    _record(assigned_driver)
    assert Trip.objects.count() == 1
    assert Location.objects.count() == 2


def test_stale_open_trip_is_closed_and_new_one_opened(assigned_driver, vehicle, driver_profile):
    stale = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=30),
        status=TripStatus.OPEN,
    )
    location, _ = _record(assigned_driver)

    stale.refresh_from_db()
    assert stale.status == TripStatus.COMPLETED
    assert location.trip.id != stale.id
    assert location.trip.status == TripStatus.OPEN
    assert Trip.objects.count() == 2


# ---------------------------------------------------------------------------
# Trip closing
# ---------------------------------------------------------------------------
def test_close_trip_sets_completed(open_trip):
    close_trip(open_trip, reason="test")
    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED
    assert open_trip.ended_at is not None


def test_close_trip_is_idempotent(open_trip):
    close_trip(open_trip)
    ended = Trip.objects.get(pk=open_trip.pk).ended_at
    close_trip(open_trip)
    assert Trip.objects.get(pk=open_trip.pk).ended_at == ended


def test_close_open_trip_for_user(driver_user, open_trip):
    result = close_open_trip_for_user(driver_user, reason="logout")
    assert result is not None
    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED


def test_close_open_trip_for_non_driver_returns_none(admin_user):
    assert close_open_trip_for_user(admin_user) is None


def test_close_stale_trips_closes_only_stale(vehicle, make_vehicle, driver_profile, make_driver):
    now = timezone.now()
    stale = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=now - timedelta(minutes=30),
        status=TripStatus.OPEN,
    )
    v2 = make_vehicle()
    d2 = make_driver(username="d2")
    fresh = Trip.objects.create(
        vehicle=v2,
        driver=d2,
        started_at=now - timedelta(minutes=1),
        status=TripStatus.OPEN,
    )

    closed = close_stale_trips()
    assert closed == 1
    stale.refresh_from_db()
    fresh.refresh_from_db()
    assert stale.status == TripStatus.COMPLETED
    assert fresh.status == TripStatus.OPEN
