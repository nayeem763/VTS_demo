"""Fleet-record PDF reporting tests."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus
from apps.tracking.reports import (
    _summarise_locations,
    build_fleet_record_pdf,
    build_trip_history_pdf,
)

pytestmark = pytest.mark.django_db


def test_pdf_report_contains_log_and_analytics_for_populated_fleet(vehicle, open_trip, add_point):
    first = timezone.now() - timedelta(days=1, minutes=15)
    add_point(
        trip=open_trip,
        captured_at=first,
        latitude=Decimal("23.777100"),
        longitude=Decimal("90.399400"),
        speed_kmh=Decimal("12.00"),
        accuracy_m=Decimal("7.00"),
    )
    add_point(
        trip=open_trip,
        captured_at=first + timedelta(minutes=10),
        latitude=Decimal("23.778100"),
        longitude=Decimal("90.400400"),
        speed_kmh=Decimal("34.00"),
        accuracy_m=Decimal("9.00"),
    )

    pdf = build_fleet_record_pdf(vehicles=[vehicle], generated_by="admin1")

    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 4_000
    # One detailed-log page and a dedicated analytics page are created.
    assert pdf.count(b"/Type /Page") >= 3


def test_report_metrics_keep_trip_points_separate_and_calculate_distance(
    vehicle, open_trip, add_point
):
    captured_at = timezone.now() - timedelta(minutes=30)
    first = add_point(
        trip=open_trip,
        captured_at=captured_at,
        latitude=Decimal("23.777100"),
        longitude=Decimal("90.399400"),
        speed_kmh=Decimal("3.00"),
    )
    second = add_point(
        trip=open_trip,
        captured_at=captured_at + timedelta(minutes=2),
        latitude=Decimal("23.778100"),
        longitude=Decimal("90.400400"),
        speed_kmh=Decimal("31.00"),
    )

    metrics = _summarise_locations(
        locations=[first, second],
        vehicle_count=1,
        trip_count=1,
    )

    assert metrics.record_count == 2
    assert metrics.average_speed_kmh == 17
    assert metrics.peak_speed_kmh == 31
    assert metrics.estimated_distance_km > 0
    assert dict(metrics.speed_buckets)["Idle <5"] == 1
    assert dict(metrics.speed_buckets)["25-44"] == 1


def test_pdf_report_handles_an_empty_fleet_selection(vehicle):
    pdf = build_fleet_record_pdf(vehicles=[vehicle])

    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 3_000


def test_trip_history_pdf_has_vehicle_sections_and_a_separate_combined_timeline(
    vehicle, open_trip, make_vehicle, driver_profile, add_point
):
    captured_at = timezone.now() - timedelta(minutes=15)
    second_vehicle = make_vehicle(bus_number="BUS-002", route_label="Science Shuttle")
    second_trip = Trip.objects.create(
        vehicle=second_vehicle,
        driver=driver_profile,
        started_at=captured_at,
        status=TripStatus.OPEN,
    )
    add_point(trip=open_trip, captured_at=captured_at)
    add_point(trip=second_trip, captured_at=captured_at + timedelta(minutes=5))

    pdf = build_trip_history_pdf(
        vehicles=[vehicle, second_vehicle],
        on_date=timezone.localdate(captured_at),
        generated_by="admin1",
    )

    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 3_000
    # The per-vehicle sections are followed by a forced page break for the
    # combined chronology. ReportLab also emits a page-tree object.
    assert pdf.count(b"/Type /Page") >= 3


def test_superuser_can_download_full_fleet_report_from_vehicle_admin(client, superuser, vehicle):
    client.force_login(superuser)

    response = client.get(reverse("admin:fleet_vehicle_generate_fleet_report"))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"].startswith('attachment; filename="fleet-record-')
    assert response.content.startswith(b"%PDF-")


def test_group_admin_can_download_full_fleet_report_from_dashboard(client, admin_user, vehicle):
    client.force_login(admin_user)

    response = client.get(reverse("web:fleet_record_pdf"))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Cache-Control"] == "private, no-store"
    assert response.content.startswith(b"%PDF-")


def test_group_admin_can_download_trip_history_pdf(client, admin_user, vehicle, open_trip, add_point):
    captured_at = timezone.now() - timedelta(minutes=5)
    add_point(trip=open_trip, captured_at=captured_at)
    client.force_login(admin_user)

    response = client.get(
        reverse("web:trip_history_pdf"),
        {"date": timezone.localdate(captured_at).isoformat()},
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"].startswith('attachment; filename="trip-history-')
    assert response["Cache-Control"] == "private, no-store"
    assert response.content.startswith(b"%PDF-")


def test_trip_history_pdf_rejects_invalid_time_range(client, admin_user):
    client.force_login(admin_user)

    response = client.get(
        reverse("web:trip_history_pdf"),
        {"date": "2026-11-15", "start": "18:00", "end": "09:00"},
    )

    assert response.status_code == 400


def test_admin_export_rejects_staff_without_location_view_permission(client):
    restricted_staff = User.objects.create_user(
        username="limited-staff",
        password="test-pass-9f2xQ",
        is_staff=True,
    )
    client.force_login(restricted_staff)

    response = client.get(reverse("admin:fleet_vehicle_generate_fleet_report"))

    assert response.status_code == 403
