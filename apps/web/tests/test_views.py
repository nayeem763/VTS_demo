"""Web page view tests: rendering and role-based access control."""

from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Public map — open to everyone
# ---------------------------------------------------------------------------
def test_public_map_renders_for_anonymous(client):
    resp = client.get(reverse("web:public_map"))
    assert resp.status_code == 200
    assert "public/vehicle_map.html" in [t.name for t in resp.templates]


# ---------------------------------------------------------------------------
# Admin dashboard — admin only
# ---------------------------------------------------------------------------
def test_dashboard_redirects_anonymous_to_login(client):
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 302
    assert reverse("accounts:admin_login") in resp.url


def test_dashboard_forbidden_for_driver(client, driver_user):
    client.force_login(driver_user)
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 403


def test_dashboard_ok_for_admin(client, admin_user, vehicle):
    client.force_login(admin_user)
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 200
    assert list(resp.context["vehicles"]) == [vehicle]


# ---------------------------------------------------------------------------
# Tracker — driver only
# ---------------------------------------------------------------------------
def test_tracker_redirects_anonymous_to_driver_login(client):
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 302
    assert reverse("accounts:driver_login") in resp.url


def test_tracker_forbidden_for_admin(client, admin_user):
    client.force_login(admin_user)
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 403


def test_tracker_ok_for_driver_and_sets_csrf_cookie(client, assigned_driver, vehicle):
    client.force_login(assigned_driver)
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 200
    assert resp.context["assigned_vehicle"] == vehicle
    assert "csrftoken" in resp.cookies


# ---------------------------------------------------------------------------
# Trip history — admin only
# ---------------------------------------------------------------------------
def test_trip_history_ok_for_admin(client, admin_user):
    client.force_login(admin_user)
    resp = client.get(reverse("web:trip_history"))
    assert resp.status_code == 200


def test_trip_history_forbidden_for_driver(client, driver_user):
    client.force_login(driver_user)
    resp = client.get(reverse("web:trip_history"))
    assert resp.status_code == 403
