"""Trip-history API tests (admin-only ``/trips/`` and ``/trips/<id>/points/``)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def a_trip(vehicle, driver_profile):
    return Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=5),
        status=TripStatus.OPEN,
    )


# ---------------------------------------------------------------------------
# /trips/
# ---------------------------------------------------------------------------
def test_trip_list_requires_vehicle_id(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"))
    assert resp.status_code == 400


def test_trip_list_returns_trips_for_vehicle(api_client, admin_user, a_trip, vehicle):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    row = body["results"][0]
    assert row["id"] == a_trip.id
    assert row["bus_number"] == vehicle.bus_number
    assert row["driver_name"] == a_trip.driver.display_name
    assert row["status"] == TripStatus.OPEN


def test_trip_list_bad_date_returns_400(api_client, admin_user, vehicle):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(
        reverse("api:trip-list"), {"vehicle_id": vehicle.id, "date": "not-a-date"}
    )
    assert resp.status_code == 400


def test_trip_list_unknown_vehicle_returns_404(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": 999999})
    assert resp.status_code == 404


def test_trip_list_forbidden_for_driver(api_client, assigned_driver, vehicle):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 403


def test_trip_list_forbidden_for_anonymous(api_client, vehicle):
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# /trips/<id>/points/
# ---------------------------------------------------------------------------
def test_trip_points_returns_ascending_points(api_client, admin_user, a_trip, add_point):
    now = timezone.now()
    add_point(trip=a_trip, captured_at=now - timedelta(minutes=2))
    add_point(trip=a_trip, captured_at=now - timedelta(minutes=1))
    api_client.force_authenticate(user=admin_user)

    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]))
    assert resp.status_code == 200
    body = resp.json()
    assert body["trip_id"] == a_trip.id
    assert body["count"] == 2
    times = [p["captured_at"] for p in body["points"]]
    assert times == sorted(times)
    assert set(body["points"][0]) == {"latitude", "longitude", "speed_kmh", "captured_at"}


def test_trip_points_bad_start_returns_400(api_client, admin_user, a_trip):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]), {"start": "99:99"})
    assert resp.status_code == 400


def test_trip_points_forbidden_for_driver(api_client, assigned_driver, a_trip):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]))
    assert resp.status_code == 403
