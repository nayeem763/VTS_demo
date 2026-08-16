"""Tracking selector tests: live and historical read queries."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus
from apps.tracking.selectors import (
    get_latest_active_vehicle_locations,
    get_latest_vehicle_location,
    get_open_trip_for_vehicle,
    get_trip_points,
    get_vehicle_trips,
)

pytestmark = pytest.mark.django_db


def test_get_latest_vehicle_location_returns_most_recent(open_trip, vehicle, add_point):
    now = timezone.now()
    add_point(trip=open_trip, captured_at=now - timedelta(minutes=5))
    newest = add_point(trip=open_trip, captured_at=now - timedelta(seconds=5))
    assert get_latest_vehicle_location(vehicle) == newest


def test_get_latest_vehicle_location_none_when_empty(vehicle):
    assert get_latest_vehicle_location(vehicle) is None


def test_latest_active_locations_include_vehicles_without_fix(
    open_trip, vehicle, make_vehicle, add_point
):
    silent = make_vehicle(bus_number="SILENT")
    add_point(trip=open_trip)

    results = {veh.id: loc for veh, loc in get_latest_active_vehicle_locations()}
    assert results[vehicle.id] is not None
    assert results[silent.id] is None


def test_get_vehicle_trips_filters_by_date(vehicle, driver_profile):
    today = timezone.localtime(timezone.now())
    Trip.objects.create(
        vehicle=vehicle, driver=driver_profile, started_at=today, status=TripStatus.OPEN
    )
    Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=today - timedelta(days=3),
        status=TripStatus.COMPLETED,
    )

    all_trips = get_vehicle_trips(vehicle=vehicle)
    todays = get_vehicle_trips(vehicle=vehicle, on_date=today.date())
    assert all_trips.count() == 2
    assert todays.count() == 1


def test_get_trip_points_orders_ascending_and_bounds(open_trip, add_point):
    now = timezone.now()
    p1 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=3))
    p2 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=2))
    p3 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=1))

    ordered = list(get_trip_points(trip=open_trip))
    assert ordered == [p1, p2, p3]

    bounded = list(
        get_trip_points(
            trip=open_trip,
            start=now - timedelta(minutes=2, seconds=30),
            end=now - timedelta(seconds=90),
        )
    )
    assert bounded == [p2]


def test_get_open_trip_for_vehicle(open_trip, vehicle):
    assert get_open_trip_for_vehicle(vehicle) == open_trip


def test_get_open_trip_for_vehicle_none_when_completed(open_trip, vehicle):
    open_trip.status = TripStatus.COMPLETED
    open_trip.save(update_fields=["status"])
    assert get_open_trip_for_vehicle(vehicle) is None
