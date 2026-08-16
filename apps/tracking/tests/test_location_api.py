"""Location ingestion API tests (``POST /api/v1/locations/``)."""

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.api.views import LocationCreateView
from apps.tracking.models import Location

pytestmark = pytest.mark.django_db

URL = reverse("api:location-create")


def _payload(**overrides):
    data = {
        "client_event_id": str(uuid.uuid4()),
        "latitude": "23.777100",
        "longitude": "90.399400",
        "speed_kmh": "31.50",
        "captured_at": timezone.now().isoformat(),
    }
    data.update(overrides)
    return data


def test_throttle_scope_is_declared():
    assert LocationCreateView.throttle_scope == "location_ingest"


def test_assigned_driver_can_post_location(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["duplicate"] is False
    assert body["trip_id"] is not None
    assert "received_at" in body
    assert Location.objects.count() == 1


def test_duplicate_client_event_id_returns_200(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    payload = _payload()
    first = api_client.post(URL, payload, format="json")
    second = api_client.post(URL, payload, format="json")
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["duplicate"] is True
    assert first.json()["id"] == second.json()["id"]
    assert Location.objects.count() == 1


def test_non_driver_is_forbidden(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_anonymous_is_forbidden(api_client):
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_driver_without_assignment_is_forbidden(api_client, driver_user):
    api_client.force_authenticate(user=driver_user)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_invalid_coordinates_rejected_by_serializer(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.post(URL, _payload(latitude="120.0"), format="json")
    assert resp.status_code == 400
    assert "latitude" in resp.json()


def test_future_timestamp_rejected_by_service(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    future = (timezone.now() + timedelta(minutes=10)).isoformat()
    resp = api_client.post(URL, _payload(captured_at=future), format="json")
    assert resp.status_code == 400
    assert Location.objects.count() == 0


def test_missing_required_field_rejected(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    payload = _payload()
    del payload["captured_at"]
    resp = api_client.post(URL, payload, format="json")
    assert resp.status_code == 400
