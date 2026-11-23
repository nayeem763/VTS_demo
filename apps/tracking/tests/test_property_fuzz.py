"""Property-based invariant tests and deterministic fuzzing for CU-VTS core logic."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from datetime import timezone as dt_tz
from decimal import Decimal
from types import SimpleNamespace

import pytest

from apps.tracking.api.serializers import (
    BusRouteCreateSerializer,
    LocationIngestSerializer,
    RouteStopInputSerializer,
)
from apps.tracking.reports import _haversine_km, _sample_locations


def _gen_coord_triples(count: int, seed: int = 20261124) -> list[tuple[float, float, float, float, float, float]]:
    rng = random.Random(seed)
    triples = []
    for _ in range(count):
        triples.append(
            (
                round(rng.uniform(-89.9, 89.9), 6),
                round(rng.uniform(-179.9, 179.9), 6),
                round(rng.uniform(-89.9, 89.9), 6),
                round(rng.uniform(-179.9, 179.9), 6),
                round(rng.uniform(-89.9, 89.9), 6),
                round(rng.uniform(-179.9, 179.9), 6),
            )
        )
    return triples


# ---------------------------------------------------------------------------
# 1. Haversine Metric-Space Mathematical Properties (50 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("triple", _gen_coord_triples(50))
def test_property_haversine_metric_space_axioms(triple):
    lat1, lon1, lat2, lon2, lat3, lon3 = triple
    d11 = _haversine_km(lat1, lon1, lat1, lon1)
    d12 = _haversine_km(lat1, lon1, lat2, lon2)
    d21 = _haversine_km(lat2, lon2, lat1, lon1)
    d23 = _haversine_km(lat2, lon2, lat3, lon3)
    d13 = _haversine_km(lat1, lon1, lat3, lon3)

    # Identity, non-negativity, symmetry, triangle inequality, Earth circumference bound
    assert d11 == pytest.approx(0.0, abs=1e-9)
    assert d12 >= 0.0
    assert d12 == pytest.approx(d21, rel=1e-9, abs=1e-9)
    assert d13 <= d12 + d23 + 1e-6
    assert d12 <= 20015.2


# ---------------------------------------------------------------------------
# 2. Smart Checkpoint Sampler Mathematical Invariants (30 tests)
# ---------------------------------------------------------------------------
def _make_fake_stream(length: int, interval_step_s: int, peak_idx: int, peak_spd: float, seed: int):
    rng = random.Random(seed)
    base = datetime(2026, 11, 24, 8, 0, tzinfo=dt_tz.utc)
    lat = 22.4716
    lon = 91.7876
    locs = []
    bg_max = max(5.0, min(22.0, peak_spd - 1.0))
    for idx in range(length):
        lat += rng.uniform(0.00001, 0.00006)
        lon += rng.uniform(0.00001, 0.00006)
        spd = peak_spd if idx == peak_idx else round(rng.uniform(4.0, bg_max), 2)
        locs.append(
            SimpleNamespace(
                pk=idx + 1,
                trip_id=1,
                vehicle_id=1,
                latitude=Decimal(f"{lat:.6f}"),
                longitude=Decimal(f"{lon:.6f}"),
                speed_kmh=Decimal(f"{spd:.2f}"),
                accuracy_m=Decimal("8.00"),
                captured_at=base + timedelta(seconds=idx * interval_step_s),
            )
        )
    return locs


SAMPLER_SCENARIOS = [
    # (length, step_s, sample_interval_s, peak_idx, peak_speed, seed)
    (1, 5, 120, 0, 20.0, 101),
    (2, 5, 120, 1, 25.0, 102),
    (5, 5, 120, 2, 30.0, 103),
    (12, 5, 60, 6, 48.0, 104),
    (24, 5, 120, 11, 52.0, 105),
    (36, 5, 120, 17, 55.0, 106),
    (60, 5, 60, 29, 61.0, 107),
    (60, 5, 120, 33, 50.0, 108),
    (60, 5, 300, 25, 47.0, 109),
    (60, 5, 0, 20, 49.0, 110),
    (90, 5, 120, 44, 58.0, 111),
    (120, 5, 120, 65, 63.0, 112),
    (120, 5, 300, 77, 46.0, 113),
    (120, 5, 60, 12, 45.0, 114),
    (120, 5, 0, 50, 38.0, 115),
    (150, 5, 120, 99, 54.0, 116),
    (180, 5, 120, 88, 70.0, 117),
    (180, 5, 300, 90, 45.5, 118),
    (200, 5, 120, 101, 59.0, 119),
    (240, 5, 120, 120, 51.0, 120),
    (30, 10, 60, 14, 49.0, 121),
    (40, 10, 120, 22, 35.0, 122),
    (50, 10, 300, 25, 48.0, 123),
    (15, 30, 120, 7, 46.0, 124),
    (25, 15, 120, 12, 42.0, 125),
    (100, 5, 120, 50, 25.0, 126),
    (80, 5, 60, 40, 28.0, 127),
    (45, 5, 120, 1, 66.0, 128),
    (45, 5, 120, 43, 64.0, 129),
    (300, 5, 300, 150, 53.0, 130),
]


@pytest.mark.parametrize(
    ("length", "step_s", "interval_s", "peak_idx", "peak_spd", "seed"), SAMPLER_SCENARIOS
)
def test_property_smart_checkpoint_sampler_invariants(
    length, step_s, interval_s, peak_idx, peak_spd, seed
):
    stream = _make_fake_stream(length, step_s, peak_idx, peak_spd, seed)
    sampled = _sample_locations(locations=stream, interval_seconds=interval_s)

    kept_pks = [cp.location.pk for cp in sampled]
    # 1. Non-empty & strictly ordered chronologically
    assert len(sampled) >= 1
    assert kept_pks == sorted(kept_pks)
    assert len(kept_pks) == len(set(kept_pks))
    # 2. Trip Start and End always retained
    assert stream[0].pk in kept_pks
    assert stream[-1].pk in kept_pks
    assert sampled[0].tag == "Start"
    if length > 1:
        assert sampled[-1].tag == "End"
    # 3. Raw mode lossless; sampled mode never exceeds raw count & preserves peak
    if interval_s == 0:
        assert len(sampled) == length
    else:
        assert len(sampled) <= length
        assert stream[peak_idx].pk in kept_pks


# ---------------------------------------------------------------------------
# 3. Serializer Fuzzing (60 tests)
# ---------------------------------------------------------------------------
LOCATION_SERIALIZER_FUZZ = [
    # Valid payloads (15)
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.471600", "longitude": "91.787600", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "0", "longitude": "0", "speed_kmh": "0", "accuracy_m": "0", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "-90", "longitude": "-180", "speed_kmh": None, "accuracy_m": None, "captured_at": "2026-11-24T04:00:00+06:00"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "90", "longitude": "180", "speed_kmh": "99.99", "accuracy_m": "12.50", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "speed_kmh": "45.00", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.123456", "longitude": "91.654321", "accuracy_m": "5.25", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "-22.4716", "longitude": "-91.7876", "speed_kmh": "18.5", "accuracy_m": "10", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "23.8103", "longitude": "90.4125", "speed_kmh": "0.01", "accuracy_m": "0.01", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "45.5", "longitude": "120.25", "speed_kmh": "120.00", "accuracy_m": "500.00", "captured_at": "2026-11-24T04:00:00Z"}, True),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "89.999999", "longitude": "179.999999", "captured_at": "2026-11-24T04:00:00Z"}, True),
    # Malformed / fuzz payloads (20)
    ({}, False),
    ({"client_event_id": "not-a-uuid", "latitude": "22.47", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": "", "latitude": "22.47", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "90.000001", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "-90.000001", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "180.000001", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "-180.000001", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "NaN", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "Infinity", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "abc", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "speed_kmh": "-1", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "accuracy_m": "-0.1", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "speed_kmh": "10000.00", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "accuracy_m": "100000.00", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "captured_at": "not-a-date"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.1234567", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.1234567", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz", "latitude": "22.47", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"}, False),
    ({"client_event_id": str(uuid.uuid4()), "latitude": None, "longitude": None, "captured_at": "2026-11-24T04:00:00Z"}, False),
]


@pytest.mark.parametrize(("payload", "is_valid"), LOCATION_SERIALIZER_FUZZ)
def test_fuzz_location_ingest_serializer(payload, is_valid):
    s = LocationIngestSerializer(data=payload)
    assert s.is_valid() is is_valid


ROUTE_STOP_FUZZ = [
    ({"name": "Zero Point", "latitude": "22.471600", "longitude": "91.787600"}, True),
    ({"name": "A" * 120, "latitude": "22.47", "longitude": "91.78"}, True),
    ({"name": "Gate 2", "latitude": "-90", "longitude": "-180"}, True),
    ({"name": "GEC", "latitude": "90", "longitude": "180"}, True),
    ({"name": "", "latitude": "22.47", "longitude": "91.78"}, False),
    ({"name": "   ", "latitude": "22.47", "longitude": "91.78"}, False),
    ({"name": "A" * 121, "latitude": "22.47", "longitude": "91.78"}, False),
    ({"name": "Bad Lat", "latitude": "91", "longitude": "91.78"}, False),
    ({"name": "Bad Lon", "latitude": "22.47", "longitude": "181"}, False),
    ({"name": "Missing", "latitude": "22.47"}, False),
    ({"name": "Prec", "latitude": "22.1234567", "longitude": "91.78"}, False),
    ({}, False),
]


@pytest.mark.parametrize(("payload", "is_valid"), ROUTE_STOP_FUZZ)
def test_fuzz_route_stop_input_serializer(payload, is_valid):
    s = RouteStopInputSerializer(data=payload)
    assert s.is_valid() is is_valid


BUS_ROUTE_FUZZ = [
    # Valid (6)
    ({"name": "Route A", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": []}, True),
    ({"name": "Route B", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": [{"name": "Mid", "latitude": "22.41", "longitude": "91.80"}]}, True),
    ({"name": "Loop OK", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.47", "end_longitude": "91.78", "stops": [{"name": "Turnaround", "latitude": "22.36", "longitude": "91.82"}]}, True),
    ({"name": "X" * 120, "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.48", "end_longitude": "91.79", "stops": []}, True),
    ({"name": "3-Stop", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.35", "end_longitude": "91.83", "stops": [{"name": "S1", "latitude": "22.44", "longitude": "91.79"}, {"name": "S2", "latitude": "22.40", "longitude": "91.81"}, {"name": "S3", "latitude": "22.38", "longitude": "91.82"}]}, True),
    ({"name": "Trimmed ", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82"}, True),
    # Invalid (12)
    ({"name": "", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82"}, False),
    ({"name": "   ", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82"}, False),
    ({"name": "Same Start End", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.47", "end_longitude": "91.78", "stops": []}, False),
    ({"name": "Dup Stop Start", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": [{"name": "S1", "latitude": "22.47", "longitude": "91.78"}]}, False),
    ({"name": "Dup Stop End", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": [{"name": "S1", "latitude": "22.36", "longitude": "91.82"}]}, False),
    ({"name": "Dup Adjacent Stops", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": [{"name": "S1", "latitude": "22.40", "longitude": "91.80"}, {"name": "S2", "latitude": "22.40", "longitude": "91.80"}]}, False),
    ({"name": "Too Long " + "Z" * 120, "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82"}, False),
    ({"name": "Bad Start Lat", "start_latitude": "95", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82"}, False),
    ({"name": "Bad End Lon", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "200"}, False),
    ({"name": "Too Many Stops", "start_latitude": "22.47", "start_longitude": "91.78", "end_latitude": "22.36", "end_longitude": "91.82", "stops": [{"name": f"S{i}", "latitude": f"22.{400000 + i}", "longitude": "91.80"} for i in range(51)]}, False),
    ({"name": "Missing End", "start_latitude": "22.47", "start_longitude": "91.78"}, False),
    ({}, False),
]


@pytest.mark.django_db
@pytest.mark.parametrize(("payload", "is_valid"), BUS_ROUTE_FUZZ)
def test_fuzz_bus_route_create_serializer(payload, is_valid):
    s = BusRouteCreateSerializer(data=payload)
    assert s.is_valid() is is_valid
