"""Functional and end-to-end multi-step user journey tests across web pages and PDF exports."""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import DriverProfile
from apps.fleet.models import DriverAssignment, Vehicle
from apps.tracking.models import Location, Trip, TripStatus
from apps.tracking.reports import ReportType

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# 1. End-to-End Multi-Actor Tracking & Fleet Journeys (15 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("fix_count", [1, 3, 5, 8, 12])
def test_e2e_driver_broadcast_to_public_and_admin_to_logout(
    client, admin_user, assigned_driver, vehicle, fix_count
):
    # 1. Driver loads tracker page & posts GPS fixes
    client.force_login(assigned_driver)
    assert client.get(reverse("web:tracker")).status_code == 200

    api = APIClient()
    api.force_authenticate(user=assigned_driver)
    base = timezone.now() - timedelta(seconds=fix_count * 5)
    for i in range(fix_count):
        r = api.post(
            reverse("api:location-create"),
            {
                "client_event_id": str(uuid.uuid4()),
                "latitude": f"{22.4716 + i * 0.0002:.6f}",
                "longitude": f"{91.7876 + i * 0.0002:.6f}",
                "speed_kmh": "24.50",
                "accuracy_m": "8.00",
                "captured_at": (base + timedelta(seconds=i * 5)).isoformat(),
            },
            format="json",
        )
        assert r.status_code == 201

    # 2. Public map API sees vehicle & trajectory without driver PII
    pub = APIClient().get(reverse("api:vehicle-latest-locations")).json()["results"][0]
    assert pub["has_signal"] is True
    assert len(pub["trajectory"]) == fix_count
    assert "driver_name" not in pub

    # 3. Admin API sees driver name & accuracy
    admin_api = APIClient()
    admin_api.force_authenticate(user=admin_user)
    adm = admin_api.get(reverse("api:vehicle-latest-locations")).json()["results"][0]
    assert adm["driver_name"] == assigned_driver.driver_profile.display_name
    assert adm["accuracy_m"] == "8.00"

    # 4. Driver logs out -> open trip closes automatically
    assert Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).count() == 1
    assert client.post(reverse("accounts:logout")).status_code == 302
    assert Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).count() == 0


@pytest.mark.parametrize("idx", range(5))
def test_e2e_fleet_lifecycle_create_rename_assign_gps_reassign_deassign_pdf(
    client, admin_user, make_driver, idx
):
    client.force_login(admin_user)
    d1 = make_driver(username=f"e2e_d1_{idx}", first_name="Kamal", last_name=f"One{idx}")
    d2 = make_driver(username=f"e2e_d2_{idx}", first_name="Jamal", last_name=f"Two{idx}")

    # Create bus with admin-only note
    client.post(
        reverse("web:fleet_vehicle_create"),
        {
            "bus_number": f"E2E-{idx}",
            "registration_number": f"CTG-E2E-{idx}",
            "route_label": "Campus Loop",
            "admin_description": f"Admin internal note #{idx}",
            "is_active": "1",
        },
    )
    bus = Vehicle.objects.get(bus_number=f"E2E-{idx}")

    # Rename bus
    client.post(
        reverse("web:fleet_vehicle_edit", args=[bus.pk]),
        {
            "bus_number": f"E2E-{idx}X",
            "registration_number": f"CTG-E2E-{idx}",
            "route_label": "Science Shuttle",
            "admin_description": f"Renamed note #{idx}",
        },
    )
    bus.refresh_from_db()
    assert bus.bus_number == f"E2E-{idx}X"

    # Assign d1 & post GPS fix (opens trip)
    client.post(reverse("web:fleet_assign"), {"vehicle": str(bus.pk), "driver": str(d1.pk)})
    drv_api = APIClient()
    drv_api.force_authenticate(user=d1.user)
    assert drv_api.post(
        reverse("api:location-create"),
        {
            "client_event_id": str(uuid.uuid4()),
            "latitude": "22.471600",
            "longitude": "91.787600",
            "speed_kmh": "31.00",
            "captured_at": timezone.now().isoformat(),
        },
        format="json",
    ).status_code == 201
    assert Trip.objects.filter(vehicle=bus, status=TripStatus.OPEN).count() == 1

    # Reassign to d2 -> closes d1 assignment & closes open trip
    client.post(reverse("web:fleet_assign"), {"vehicle": str(bus.pk), "driver": str(d2.pk)})
    assert Trip.objects.filter(vehicle=bus, status=TripStatus.OPEN).count() == 0
    a2 = DriverAssignment.objects.get(vehicle=bus, driver=d2, is_active=True)

    # Deassign d2
    client.post(reverse("web:fleet_deassign", args=[a2.pk]))
    assert not DriverAssignment.objects.filter(vehicle=bus, is_active=True).exists()

    # Export Executive PDF for this bus
    pdf_resp = client.get(
        reverse("web:fleet_record_pdf"),
        {"report_type": ReportType.EXECUTIVE_SUMMARY, "vehicle_scope": "single", "vehicle": str(bus.pk)},
    )
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF-")


@pytest.mark.parametrize("tab", ["vehicles", "assignments", "drivers", "invalid_falls_back"])
def test_e2e_fleet_manage_tab_selection(client, admin_user, tab):
    client.force_login(admin_user)
    resp = client.get(reverse("web:fleet_manage"), {"tab": tab})
    assert resp.status_code == 200
    expected = tab if tab in ("vehicles", "assignments", "drivers") else "vehicles"
    assert resp.context["active_tab"] == expected


def test_e2e_healthz_liveness_probe(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.content.strip() == b"ok"


# ---------------------------------------------------------------------------
# 2. Fleet PDF Report Builder Parameter Matrix (48 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("report_type", ReportType.ALL)
@pytest.mark.parametrize("preset", ["all", "today", "7d", "30d"])
@pytest.mark.parametrize("scope", ["all", "active"])
def test_functional_fleet_pdf_matrix_presets_and_scopes(
    client, admin_user, vehicle, open_trip, add_point, report_type, preset, scope
):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(minutes=2), speed_kmh=Decimal("28.00"))
    client.force_login(admin_user)
    resp = client.get(
        reverse("web:fleet_record_pdf"),
        {"report_type": report_type, "preset": preset, "vehicle_scope": scope},
    )
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF-")


@pytest.mark.parametrize("interval", ["0", "60", "120", "300"])
@pytest.mark.parametrize("report_type", ReportType.ALL)
def test_functional_fleet_pdf_sampling_intervals(
    client, admin_user, vehicle, open_trip, add_point, interval, report_type
):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(minutes=3), speed_kmh=Decimal("47.50"))
    client.force_login(admin_user)
    resp = client.get(
        reverse("web:fleet_record_pdf"),
        {"report_type": report_type, "interval": interval, "vehicle": str(vehicle.pk)},
    )
    assert resp.status_code == 200
    assert resp.content.startswith(b"%PDF-")


# ---------------------------------------------------------------------------
# 3. Fleet & Trip PDF Invalid Input Handling (22 tests)
# ---------------------------------------------------------------------------
INVALID_FLEET_PDF_PARAMS = [
    {"report_type": "nope"},
    {"preset": "yearly"},
    {"preset": "custom", "date_from": "bad-date"},
    {"preset": "custom", "date_to": "bad-date"},
    {"preset": "custom", "date_from": "2026-11-25", "date_to": "2026-11-20"},
    {"vehicle_scope": "invalid_scope"},
    {"vehicle": "not-an-int"},
    {"vehicle": "999999"},
    {"interval": "abc"},
    {"interval": "15"},
    {"interval": "-10"},
]


@pytest.mark.parametrize("params", INVALID_FLEET_PDF_PARAMS)
def test_functional_fleet_pdf_invalid_params_return_400(client, admin_user, params):
    client.force_login(admin_user)
    resp = client.get(reverse("web:fleet_record_pdf"), params)
    assert resp.status_code == 400


INVALID_TRIP_PDF_PARAMS = [
    {"date": "not-a-date"},
    {"start": "08:00"},
    {"end": "10:00"},
    {"date": "2026-11-24", "start": "25:99"},
    {"date": "2026-11-24", "end": "99:99"},
    {"date": "2026-11-24", "start": "16:00", "end": "09:00"},
    {"report_type": "invalid_profile"},
    {"interval": "not-int"},
    {"interval": "42"},
    {"vehicle": "abc"},
    {"vehicle": "999999"},
]


@pytest.mark.parametrize("params", INVALID_TRIP_PDF_PARAMS)
def test_functional_trip_pdf_invalid_params_return_400(client, admin_user, params):
    client.force_login(admin_user)
    resp = client.get(reverse("web:trip_history_pdf"), params)
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 4. Trip History PDF & Django Admin Export Matrix (15 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("report_type", [ReportType.TRIP_SUMMARY, ReportType.TELEMETRY_AUDIT, ReportType.SAFETY_AUDIT])
@pytest.mark.parametrize("with_vehicle", [False, True])
@pytest.mark.parametrize("with_times", [False, True])
def test_functional_trip_history_pdf_matrix(
    client, admin_user, vehicle, open_trip, add_point, report_type, with_vehicle, with_times
):
    now = timezone.now() - timedelta(minutes=5)
    add_point(trip=open_trip, captured_at=now, speed_kmh=Decimal("33.00"))
    client.force_login(admin_user)
    params = {"report_type": report_type, "date": timezone.localdate(now).isoformat()}
    if with_vehicle:
        params["vehicle"] = str(vehicle.pk)
    if with_times:
        params["start"] = "00:00"
        params["end"] = "23:59"
    resp = client.get(reverse("web:trip_history_pdf"), params)
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF-")


@pytest.mark.parametrize("report_type", [ReportType.EXECUTIVE_SUMMARY, ReportType.TRIP_SUMMARY, ReportType.TELEMETRY_AUDIT])
def test_functional_django_admin_vehicle_pdf_downloads(client, superuser, vehicle, report_type):
    client.force_login(superuser)
    resp = client.get(
        reverse("admin:fleet_vehicle_generate_fleet_report"),
        {"report_type": report_type},
    )
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF-")
