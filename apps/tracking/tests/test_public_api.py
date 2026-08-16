"""Public live-location API tests and the public/admin privacy boundary."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.api.views import (
    LatestActiveVehicleLocationsView,
    VehicleLatestLocationView,
)

pytestmark = pytest.mark.django_db

LIST_URL = reverse("api:vehicle-latest-locations")


def test_public_read_throttle_scopes_declared():
    assert LatestActiveVehicleLocationsView.throttle_scope == "public_read"
    assert VehicleLatestLocationView.throttle_scope == "public_read"


def test_latest_locations_public_shape(api_client, open_trip, vehicle, add_point):
    add_point(trip=open_trip, speed_kmh=Decimal("20.00"), accuracy_m=Decimal("5.00"))
    resp = api_client.get(LIST_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    row = body["results"][0]
    assert row["vehicle_id"] == vehicle.id
    assert row["bus_number"] == vehicle.bus_number
    assert row["has_signal"] is True
    assert isinstance(row["latitude"], str)
    assert isinstance(row["age_seconds"], int)
    # Privacy boundary: no driver identity or accuracy on the public view.
    assert "driver_name" not in row
    assert "accuracy_m" not in row


def test_latest_locations_admin_adds_driver_and_accuracy(
    api_client, admin_user, open_trip, add_point
):
    add_point(trip=open_trip, accuracy_m=Decimal("7.50"))
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(LIST_URL)
    row = resp.json()["results"][0]
    assert row["driver_name"] == open_trip.driver.display_name
    assert row["accuracy_m"] == "7.50"


def test_vehicle_without_fix_reports_no_signal(api_client, vehicle):
    resp = api_client.get(LIST_URL)
    row = resp.json()["results"][0]
    assert row["has_signal"] is False
    assert row["latitude"] is None
    assert row["is_stale"] is True


def test_fresh_fix_is_not_stale(api_client, open_trip, add_point):
    add_point(trip=open_trip, captured_at=timezone.now())
    resp = api_client.get(LIST_URL)
    assert resp.json()["results"][0]["is_stale"] is False


def test_old_fix_is_stale(api_client, open_trip, add_point):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(seconds=90))
    resp = api_client.get(LIST_URL)
    assert resp.json()["results"][0]["is_stale"] is True


def test_single_vehicle_latest_location(api_client, vehicle, open_trip, add_point):
    add_point(trip=open_trip)
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[vehicle.id]))
    assert resp.status_code == 200
    assert resp.json()["vehicle_id"] == vehicle.id


def test_single_vehicle_latest_location_404_when_inactive(api_client, vehicle):
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active"])
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[vehicle.id]))
    assert resp.status_code == 404


def test_single_vehicle_latest_location_404_when_missing(api_client):
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[999999]))
    assert resp.status_code == 404
