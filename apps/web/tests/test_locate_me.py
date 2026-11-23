"""Tests for the all-persona right-panel 'Locate Me / My Location' live map feature."""

from __future__ import annotations

import pathlib

import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db

BASE_DIR = pathlib.Path(settings.BASE_DIR)

REQUIRED_LOCATE_MARKERS = (
    b'id="locate-me-btn"',
    b"data-locate-me",
    b"vts-rail-btn--locate",
    b'id="my-location-card"',
    b'id="my-location-status"',
    b'id="my-location-coords"',
    b'id="my-location-meta"',
    b'id="my-location-nearest"',
    b'id="my-location-copy"',
    b'id="my-location-route-start"',
    b'id="my-location-close"',
)


# ---------------------------------------------------------------------------
# 1. Live Map ('/') — accessible to EVERY persona (Public, Driver, Admin, Superuser)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("persona", ["public", "driver", "assigned_driver", "admin", "superuser"])
def test_live_map_locate_controls_available_to_every_persona(
    client,
    persona,
    driver_user,
    assigned_driver,
    admin_user,
    superuser,
):
    if persona == "driver":
        client.force_login(driver_user)
    elif persona == "assigned_driver":
        client.force_login(assigned_driver)
    elif persona == "admin":
        client.force_login(admin_user)
    elif persona == "superuser":
        client.force_login(superuser)

    resp = client.get(reverse("web:public_map"))
    assert resp.status_code == 200
    assert "_my_location_card.html" in [t.name for t in resp.templates]
    for marker in REQUIRED_LOCATE_MARKERS:
        assert marker in resp.content, f"Missing {marker!r} for persona={persona}"

    # Both the expanded right-panel header button and the collapsed rail button exist.
    assert resp.content.count(b"data-locate-me") == 2

    # Geolocation permission policy and strict CSP must both be present.
    assert "geolocation=(self)" in resp["Permissions-Policy"]
    assert "script-src 'self'" in resp["Content-Security-Policy"]


# ---------------------------------------------------------------------------
# 2. Admin Live Dashboard ('/dashboard/') — Admin & Superuser also have right-panel Locate
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("persona", ["admin", "superuser"])
def test_admin_dashboard_has_locate_controls_for_admins(
    client,
    persona,
    admin_user,
    superuser,
    vehicle,
):
    client.force_login(admin_user if persona == "admin" else superuser)
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 200
    assert "_my_location_card.html" in [t.name for t in resp.templates]
    for marker in REQUIRED_LOCATE_MARKERS:
        assert marker in resp.content, f"Missing {marker!r} on dashboard for {persona}"

    assert resp.content.count(b"data-locate-me") == 2
    assert "geolocation=(self)" in resp["Permissions-Policy"]
    assert "script-src 'self'" in resp["Content-Security-Policy"]


def test_admin_dashboard_remains_protected_while_live_map_stays_open(
    client,
    driver_user,
):
    # Anonymous user gets Live Map with locate controls, but is redirected from Dashboard.
    assert client.get(reverse("web:public_map")).status_code == 200
    assert client.get(reverse("web:admin_dashboard")).status_code == 302

    # Driver gets Live Map with locate controls, but gets 403 on Dashboard.
    client.force_login(driver_user)
    assert client.get(reverse("web:public_map")).status_code == 200
    assert client.get(reverse("web:admin_dashboard")).status_code == 403


# ---------------------------------------------------------------------------
# 3. Privacy invariant — adding My Location never exposes admin_description or driver PII
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("persona", ["public", "driver"])
def test_live_map_with_locate_feature_preserves_privacy(
    client,
    persona,
    driver_user,
    make_vehicle,
):
    secret_note = "CONFIDENTIAL-GARAGE-PIN-9988"
    make_vehicle(bus_number="CU-PRIV", route_label="Gate 1", admin_description=secret_note)
    if persona == "driver":
        client.force_login(driver_user)

    resp = client.get(reverse("web:public_map"))
    assert resp.status_code == 200
    assert secret_note.encode() not in resp.content


# ---------------------------------------------------------------------------
# 4. Client-side JS engine & wiring contract checks
# ---------------------------------------------------------------------------
def test_vts_common_exposes_user_locator_engine_and_error_handling():
    src = (BASE_DIR / "static/js/vts-common.js").read_text(encoding="utf-8")
    for token in (
        "function haversineMeters(",
        "function fmtDistance(",
        "function userLocationIcon(",
        "function nearestCampusLandmark(",
        "function findNearestActiveVehicle(",
        "function locateUser(",
        "function clearUserLocation(",
        "navigator.geolocation.getCurrentPosition",
        "window.isSecureContext === false",
        "err.code === 1",
        "err.code === 3",
        "vts-user-marker",
        "data-focus-nearest-vehicle",
    ):
        assert token in src, f"Missing expected locator implementation token: {token}"


@pytest.mark.parametrize("script_rel", ["static/js/public-map.js", "static/js/admin-map.js"])
def test_map_entry_scripts_wire_user_locator_hooks(script_rel):
    src = (BASE_DIR / script_rel).read_text(encoding="utf-8")
    for hook in (
        "userLocator:",
        "[data-locate-me]",
        "my-location-card",
        "my-location-status",
        "my-location-coords",
        "my-location-meta",
        "my-location-nearest",
        "my-location-copy",
        "my-location-route-start",
        "my-location-close",
    ):
        assert hook in src, f"{script_rel} missing userLocator wiring for {hook}"
