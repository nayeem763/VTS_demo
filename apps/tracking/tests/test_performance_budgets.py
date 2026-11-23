"""Performance, SQL query-budget (anti-N+1), compression, and latency tests."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from datetime import timezone as dt_tz
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.fleet.services import assign_driver_to_vehicle
from apps.tracking.models import Trip, TripStatus
from apps.tracking.reports import (
    ReportType,
    _haversine_km,
    _sample_locations,
    build_fleet_record_pdf,
)

pytestmark = pytest.mark.django_db


def _seed_fleet(make_vehicle, make_driver, add_point, count: int):
    vehicles = []
    base = timezone.now() - timedelta(minutes=15)
    for i in range(count):
        v = make_vehicle(bus_number=f"PERF-{i:02d}", route_label=f"Route {i}")
        d = make_driver(username=f"perf_drv_{i:02d}", first_name="Driver", last_name=str(i))
        assign_driver_to_vehicle(driver=d, vehicle=v)
        trip = Trip.objects.create(vehicle=v, driver=d, started_at=base, status=TripStatus.OPEN)
        add_point(trip=trip, captured_at=base + timedelta(seconds=10), speed_kmh=Decimal("22.00"))
        add_point(trip=trip, captured_at=base + timedelta(seconds=30), speed_kmh=Decimal("31.00"))
        vehicles.append(v)
    return vehicles


# ---------------------------------------------------------------------------
# 1. SQL Query-Count Regression Guards (20 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("fleet_size", [1, 3, 6, 10, 15])
def test_perf_fleet_manage_page_constant_query_budget(
    client, admin_user, make_vehicle, make_driver, add_point, django_assert_max_num_queries, fleet_size
):
    _seed_fleet(make_vehicle, make_driver, add_point, fleet_size)
    client.force_login(admin_user)
    # Must stay O(1) queries regardless of fleet size (no N+1 per vehicle/driver)
    with django_assert_max_num_queries(16):
        resp = client.get(reverse("web:fleet_manage"))
    assert resp.status_code == 200


@pytest.mark.parametrize("fleet_size", [1, 3, 6, 10, 15])
def test_perf_admin_dashboard_constant_query_budget(
    client, admin_user, make_vehicle, make_driver, add_point, django_assert_max_num_queries, fleet_size
):
    _seed_fleet(make_vehicle, make_driver, add_point, fleet_size)
    client.force_login(admin_user)
    with django_assert_max_num_queries(10):
        resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 200


@pytest.mark.parametrize("fleet_size", [1, 3, 6, 10, 15])
def test_perf_public_live_api_bounded_queries(
    make_vehicle, make_driver, add_point, django_assert_max_num_queries, fleet_size
):
    _seed_fleet(make_vehicle, make_driver, add_point, fleet_size)
    api = APIClient()
    # Constant O(1) SQL queries regardless of fleet size (eliminates N+1)
    with django_assert_max_num_queries(5):
        resp = api.get(reverse("api:vehicle-latest-locations"))
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == fleet_size


@pytest.mark.parametrize("fleet_size", [1, 3, 5, 8, 12])
def test_perf_pdf_report_constant_query_budget(
    make_vehicle, make_driver, add_point, django_assert_max_num_queries, fleet_size
):
    vehicles = _seed_fleet(make_vehicle, make_driver, add_point, fleet_size)
    with django_assert_max_num_queries(10):
        pdf = build_fleet_record_pdf(
            vehicles=vehicles,
            generated_by="admin",
            report_type=ReportType.EXECUTIVE_SUMMARY,
        )
    assert pdf.startswith(b"%PDF-")


# ---------------------------------------------------------------------------
# 2. Smart Checkpoint Sampler Throughput & Compression (15 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("raw_count", [120, 240, 480, 720, 1200])
@pytest.mark.parametrize("interval_s", [60, 120, 300])
def test_perf_smart_sampler_compression_and_speed(raw_count, interval_s):
    base = datetime(2026, 11, 24, 8, 0, tzinfo=dt_tz.utc)
    # Realistic campus shuttle moving ~2 m every 5 seconds (~1.5 m/s slow campus traffic)
    stream = [
        SimpleNamespace(
            pk=i + 1,
            trip_id=1,
            vehicle_id=1,
            latitude=Decimal(f"{22.4716 + i * 0.000018:.6f}"),
            longitude=Decimal(f"{91.7876 + i * 0.000010:.6f}"),
            speed_kmh=Decimal("52.00" if i == raw_count // 2 else "14.00"),
            accuracy_m=Decimal("8.00"),
            captured_at=base + timedelta(seconds=i * 5),
        )
        for i in range(raw_count)
    ]
    t0 = time.perf_counter()
    sampled = _sample_locations(locations=stream, interval_seconds=interval_s)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    compression_ratio = 1.0 - (len(sampled) / raw_count)
    assert compression_ratio >= 0.75
    assert elapsed_ms < 250.0


# ---------------------------------------------------------------------------
# 3. Haversine Batch Calculation Throughput (5 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("segments", [100, 250, 500, 1000, 2000])
def test_perf_haversine_batch_latency(segments):
    t0 = time.perf_counter()
    total_km = 0.0
    for i in range(segments):
        total_km += _haversine_km(
            22.4716 + i * 0.0001,
            91.7876 + i * 0.0001,
            22.4717 + i * 0.0001,
            91.7877 + i * 0.0001,
        )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert total_km > 0.0
    assert elapsed_ms < 150.0


# ---------------------------------------------------------------------------
# 4. PDF Rendering Latency & Page Compactness under Dense 5s Data (10 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("report_type", ReportType.ALL)
@pytest.mark.parametrize("dense_points", [60, 180])
def test_perf_pdf_generation_latency_and_compact_pages(
    vehicle, open_trip, add_point, report_type, dense_points
):
    base = timezone.now() - timedelta(minutes=30)
    for i in range(dense_points):
        add_point(
            trip=open_trip,
            captured_at=base + timedelta(seconds=i * 5),
            latitude=Decimal("22.471600") + Decimal("0.000020") * i,
            longitude=Decimal("91.787600") + Decimal("0.000015") * i,
            speed_kmh=Decimal("49.00" if i == 30 else "21.00"),
            accuracy_m=Decimal("8.00"),
        )

    t0 = time.perf_counter()
    pdf = build_fleet_record_pdf(
        vehicles=[vehicle],
        generated_by="admin",
        report_type=report_type,
    )
    elapsed_s = time.perf_counter() - t0

    assert pdf.startswith(b"%PDF-")
    assert elapsed_s < 5.0
    page_count = pdf.count(b"/Type /Page") - 1
    if report_type in (ReportType.EXECUTIVE_SUMMARY, ReportType.SAFETY_AUDIT, ReportType.TRIP_SUMMARY):
        # Compact summaries never explode into dozens of pages even with 180 five-second fixes
        assert page_count <= 3


@pytest.mark.parametrize("fleet_size", [3, 6])
def test_perf_multi_vehicle_executive_pdf_stays_compact(
    make_vehicle, make_driver, add_point, fleet_size
):
    vehicles = _seed_fleet(make_vehicle, make_driver, add_point, fleet_size)
    t0 = time.perf_counter()
    pdf = build_fleet_record_pdf(
        vehicles=vehicles,
        generated_by="director",
        report_type=ReportType.EXECUTIVE_SUMMARY,
    )
    elapsed_s = time.perf_counter() - t0
    assert pdf.startswith(b"%PDF-")
    assert elapsed_s < 5.0
    assert (pdf.count(b"/Type /Page") - 1) == 2
