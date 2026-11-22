"""Fleet-record PDF reporting tests."""

from __future__ import annotations

import base64
import re
import zlib
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus
from apps.tracking.reports import (
    ReportType,
    _sample_locations,
    _summarise_locations,
    _summarise_trips,
    build_fleet_record_pdf,
    build_trip_history_pdf,
)

pytestmark = pytest.mark.django_db


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Decode ReportLab ASCII85 + FlateDecode PDF streams to inspect copy."""
    chunks: list[str] = []
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, flags=re.S):
        data = match.group(1).strip()
        if data.endswith(b"~>"):
            try:
                data = base64.a85decode(data, adobe=True)
            except ValueError:
                pass
        try:
            data = zlib.decompress(data)
        except zlib.error:
            pass
        chunks.append(data.decode("latin1", errors="ignore"))
    return "\n".join(chunks)


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


@pytest.mark.parametrize("report_type", ReportType.ALL)
def test_every_report_type_answers_five_specification_questions(
    report_type, vehicle, open_trip, add_point
):
    first = timezone.now() - timedelta(minutes=25)
    add_point(
        trip=open_trip,
        captured_at=first,
        latitude=Decimal("22.471600"),
        longitude=Decimal("91.787600"),
        speed_kmh=Decimal("22.00"),
        accuracy_m=Decimal("8.00"),
    )
    add_point(
        trip=open_trip,
        captured_at=first + timedelta(minutes=8),
        latitude=Decimal("22.475000"),
        longitude=Decimal("91.790500"),
        speed_kmh=Decimal("52.00"),
        accuracy_m=Decimal("10.00"),
    )

    pdf = build_fleet_record_pdf(
        vehicles=[vehicle],
        generated_by="director",
        report_type=report_type,
    )
    text = _extract_pdf_text(pdf)

    assert pdf.startswith(b"%PDF-")
    assert pdf.count(b"/Type /Page") >= 3
    for heading in (
        "i. Purpose",
        "ii. Intended Audience",
        "iii. Inputs & Scope",
        "iv. Outputs Delivered",
        "v. Platform & Environment",
    ):
        assert heading in text


def test_smart_sampling_condenses_five_second_pings_and_keeps_key_events(
    vehicle, open_trip, add_point
):
    start = timezone.now() - timedelta(minutes=10)
    points = []
    for idx in range(60):  # 5 minutes of 5-second fixes
        speed = Decimal("54.00") if idx == 27 else Decimal("18.00")
        points.append(
            add_point(
                trip=open_trip,
                captured_at=start + timedelta(seconds=idx * 5),
                latitude=Decimal("22.471600") + Decimal("0.000030") * idx,
                longitude=Decimal("91.787600") + Decimal("0.000020") * idx,
                speed_kmh=speed,
                accuracy_m=Decimal("9.00"),
            )
        )

    sampled = _sample_locations(locations=points, interval_seconds=120)
    tags = [cp.tag for cp in sampled]
    kept_pks = {cp.location.pk for cp in sampled}

    assert len(sampled) <= 8  # drastic compression from 60 raw fixes
    assert tags[0] == "Start"
    assert tags[-1] == "End"
    assert points[0].pk in kept_pks
    assert points[-1].pk in kept_pks
    assert points[27].pk in kept_pks  # overspeed peak preserved

    # Raw forensic mode keeps all fixes transparently.
    raw_sampled = _sample_locations(locations=points, interval_seconds=0)
    assert len(raw_sampled) == 60

    # Trip ledger summarises all 60 fixes into a single operational trip row.
    trip_rows = _summarise_trips(trips=[open_trip], locations=points)
    assert len(trip_rows) == 1
    assert trip_rows[0].fix_count == 60
    assert trip_rows[0].peak_speed_kmh == 54.0
    assert trip_rows[0].distance_km > 0


def test_dashboard_report_builder_filters_and_validation(client, admin_user, vehicle, open_trip, add_point):
    captured = timezone.now() - timedelta(minutes=10)
    add_point(trip=open_trip, captured_at=captured, speed_kmh=Decimal("49.00"))
    client.force_login(admin_user)

    for report_type in ReportType.ALL:
        resp = client.get(
            reverse("web:fleet_record_pdf"),
            {
                "report_type": report_type,
                "preset": "7d",
                "vehicle_scope": "single",
                "vehicle": str(vehicle.pk),
                "interval": "120",
            },
        )
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF-")

    bad_type = client.get(reverse("web:fleet_record_pdf"), {"report_type": "invalid"})
    assert bad_type.status_code == 400

    bad_dates = client.get(
        reverse("web:fleet_record_pdf"),
        {"preset": "custom", "date_from": "2026-11-20", "date_to": "2026-11-10"},
    )
    assert bad_dates.status_code == 400

    bad_interval = client.get(reverse("web:fleet_record_pdf"), {"interval": "13"})
    assert bad_interval.status_code == 400


def test_trip_history_pdf_supports_report_types_and_vehicle_filter(
    client, admin_user, vehicle, open_trip, add_point
):
    captured = timezone.now() - timedelta(minutes=5)
    add_point(trip=open_trip, captured_at=captured, speed_kmh=Decimal("32.00"))
    client.force_login(admin_user)

    for report_type in (ReportType.TRIP_SUMMARY, ReportType.TELEMETRY_AUDIT, ReportType.SAFETY_AUDIT):
        resp = client.get(
            reverse("web:trip_history_pdf"),
            {
                "report_type": report_type,
                "vehicle": str(vehicle.pk),
                "date": timezone.localdate(captured).isoformat(),
                "interval": "60",
            },
        )
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF-")

    bad = client.get(reverse("web:trip_history_pdf"), {"report_type": "unknown"})
    assert bad.status_code == 400


def test_vehicle_admin_supports_report_type_query_param(client, superuser, vehicle):
    client.force_login(superuser)

    resp = client.get(
        reverse("admin:fleet_vehicle_generate_fleet_report"),
        {"report_type": ReportType.SAFETY_AUDIT},
    )
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert "safety-audit" in resp["Content-Disposition"]

    bad = client.get(
        reverse("admin:fleet_vehicle_generate_fleet_report"),
        {"report_type": "bogus"},
    )
    assert bad.status_code == 400
