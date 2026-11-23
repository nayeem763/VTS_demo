"""Unit and Boundary-Value Analysis (BVA) tests for tracking validators and report helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from datetime import timezone as dt_tz
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.tracking.reports import (
    ReportType,
    _format_accuracy,
    _format_chart_value,
    _format_date_window,
    _format_distance,
    _format_duration,
    _format_origin_dest,
    _format_speed,
    _format_speed_pair,
    _haversine_km,
    _nice_maximum_float,
    _safe_text,
    _sampling_description,
    _truncate,
    fleet_record_filename,
    trip_history_filename,
)
from apps.tracking.validators import (
    validate_accuracy,
    validate_capture_timestamp,
    validate_coordinates,
    validate_speed,
)

# ---------------------------------------------------------------------------
# 1. Coordinate Boundary-Value Analysis (60 tests: 36 valid + 24 invalid)
# ---------------------------------------------------------------------------
VALID_COORDS = [
    # Exact globe boundaries & cardinal zeros
    (Decimal("-90.000000"), Decimal("-180.000000")),
    (Decimal("-90.000000"), Decimal("0.000000")),
    (Decimal("-90.000000"), Decimal("180.000000")),
    (Decimal("0.000000"), Decimal("-180.000000")),
    (Decimal("0.000000"), Decimal("0.000000")),
    (Decimal("0.000000"), Decimal("180.000000")),
    (Decimal("90.000000"), Decimal("-180.000000")),
    (Decimal("90.000000"), Decimal("0.000000")),
    (Decimal("90.000000"), Decimal("180.000000")),
    # Micro-interior near limits
    (Decimal("-89.999999"), Decimal("-179.999999")),
    (Decimal("89.999999"), Decimal("179.999999")),
    (Decimal("-89.999999"), Decimal("179.999999")),
    (Decimal("89.999999"), Decimal("-179.999999")),
    # Chittagong University & Chattogram landmarks
    (Decimal("22.471600"), Decimal("91.787600")),
    (Decimal("22.478700"), Decimal("91.785800")),
    (Decimal("22.467200"), Decimal("91.782300")),
    (Decimal("22.476700"), Decimal("91.791200")),
    (Decimal("22.368300"), Decimal("91.826300")),
    (Decimal("22.356900"), Decimal("91.783200")),
    (Decimal("22.347500"), Decimal("91.812300")),
    (Decimal("22.375200"), Decimal("91.842100")),
    # Float & integer coercions across all hemispheres
    (22.4716, 91.7876),
    (-33.8688, 151.2093),
    (51.5074, -0.1278),
    (40.7128, -74.0060),
    (-23.5505, -46.6333),
    (35.6762, 139.6503),
    (1.3521, 103.8198),
    (23.8103, 90.4125),
    (0, 0),
    (90, 180),
    (-90, -180),
    (Decimal("45.123456"), Decimal("-122.654321")),
    (Decimal("-12.046374"), Decimal("-77.042793")),
    (Decimal("64.146582"), Decimal("-21.942635")),
    (Decimal("-41.286460"), Decimal("174.776236")),
]


@pytest.mark.parametrize(("lat", "lon"), VALID_COORDS)
def test_bva_valid_coordinates_accepted(lat, lon):
    validate_coordinates(lat, lon)


INVALID_COORDS = [
    (Decimal("90.000001"), Decimal("0")),
    (Decimal("-90.000001"), Decimal("0")),
    (Decimal("0"), Decimal("180.000001")),
    (Decimal("0"), Decimal("-180.000001")),
    (Decimal("91"), Decimal("91.78")),
    (Decimal("-91"), Decimal("91.78")),
    (Decimal("22.47"), Decimal("181")),
    (Decimal("22.47"), Decimal("-181")),
    (Decimal("180"), Decimal("90")),
    (Decimal("-180"), Decimal("-90")),
    (Decimal("999"), Decimal("999")),
    (Decimal("-999"), Decimal("-999")),
    (None, Decimal("91.7876")),
    (Decimal("22.4716"), None),
    (None, None),
    (90.5, 0.0),
    (-90.5, 0.0),
    (0.0, 180.5),
    (0.0, -180.5),
    (100, 100),
    (-100, 100),
    (22.47, 200),
    (22.47, -200),
    (Decimal("90.1"), Decimal("180.1")),
]


@pytest.mark.parametrize(("lat", "lon"), INVALID_COORDS)
def test_bva_invalid_coordinates_rejected(lat, lon):
    with pytest.raises(ValidationError):
        validate_coordinates(lat, lon)


# ---------------------------------------------------------------------------
# 2. Speed & Accuracy BVA (50 tests: 25 speed + 25 accuracy)
# ---------------------------------------------------------------------------
SPEED_CASES = [
    (None, True),
    (Decimal("0"), True),
    (Decimal("0.00"), True),
    (Decimal("0.01"), True),
    (Decimal("4.99"), True),
    (Decimal("5.00"), True),
    (Decimal("15.50"), True),
    (Decimal("24.99"), True),
    (Decimal("25.00"), True),
    (Decimal("44.99"), True),
    (Decimal("45.00"), True),
    (Decimal("60.00"), True),
    (Decimal("120.00"), True),
    (Decimal("299.99"), True),
    (Decimal("300.00"), True),
    (0, True),
    (38.5, True),
    (Decimal("-0.01"), False),
    (Decimal("-0.50"), False),
    (Decimal("-1"), False),
    (Decimal("-12.34"), False),
    (Decimal("-50.5"), False),
    (Decimal("-999"), False),
    (-0.001, False),
    (-10, False),
]


@pytest.mark.parametrize(("speed", "is_valid"), SPEED_CASES)
def test_bva_speed_validation(speed, is_valid):
    if is_valid:
        validate_speed(speed)
    else:
        with pytest.raises(ValidationError):
            validate_speed(speed)


ACCURACY_CASES = [
    (None, True),
    (Decimal("0"), True),
    (Decimal("0.01"), True),
    (Decimal("1.50"), True),
    (Decimal("5.00"), True),
    (Decimal("8.00"), True),
    (Decimal("12.34"), True),
    (Decimal("25.00"), True),
    (Decimal("50.00"), True),
    (Decimal("100.00"), True),
    (Decimal("250.00"), True),
    (Decimal("1000.00"), True),
    (Decimal("9999.99"), True),
    (Decimal("50000.00"), True),
    (0, True),
    (14.2, True),
    (Decimal("-0.01"), False),
    (Decimal("-0.50"), False),
    (Decimal("-1.00"), False),
    (Decimal("-10.00"), False),
    (Decimal("-100.00"), False),
    (-0.1, False),
    (-5, False),
]


@pytest.mark.parametrize(("accuracy", "is_valid"), ACCURACY_CASES)
def test_bva_accuracy_validation(accuracy, is_valid):
    if is_valid:
        validate_accuracy(accuracy)
    else:
        with pytest.raises(ValidationError):
            validate_accuracy(accuracy)


# ---------------------------------------------------------------------------
# 3. Timestamp Skew & Age BVA (40 tests)
# ---------------------------------------------------------------------------
TIMESTAMP_OFFSET_CASES = [
    # Valid offsets in seconds relative to now (positive = future, negative = past)
    (0, True),
    (-1, True),
    (-5, True),
    (-30, True),
    (-60, True),
    (-120, True),
    (-300, True),
    (-600, True),
    (-1200, True),
    (-1800, True),
    (-2400, True),
    (-3000, True),
    (-3500, True),
    (-3590, True),
    (1, True),
    (10, True),
    (30, True),
    (60, True),
    (90, True),
    (115, True),
    # Invalid future skew (> LOCATION_MAX_FUTURE_SKEW_SECONDS = 120)
    (125, False),
    (130, False),
    (180, False),
    (300, False),
    (600, False),
    (3600, False),
    (86400, False),
    (86400 * 30, False),
    # Invalid stale past (> LOCATION_MAX_AGE_SECONDS = 3600)
    (-3605, False),
    (-3660, False),
    (-4000, False),
    (-7200, False),
    (-14400, False),
    (-43200, False),
    (-86400, False),
    (-86400 * 7, False),
    (-86400 * 30, False),
    (-86400 * 365, False),
]


@pytest.mark.parametrize(("offset_seconds", "is_valid"), TIMESTAMP_OFFSET_CASES)
def test_bva_capture_timestamp_offsets(offset_seconds, is_valid):
    now = timezone.now()
    ts = now + timedelta(seconds=offset_seconds)
    if is_valid:
        validate_capture_timestamp(ts, now=now)
    else:
        with pytest.raises(ValidationError):
            validate_capture_timestamp(ts, now=now)


def test_bva_capture_timestamp_none_rejected():
    with pytest.raises(ValidationError):
        validate_capture_timestamp(None)


def test_bva_capture_timestamp_naive_rejected():
    naive = datetime(2026, 11, 24, 10, 0, 0)
    with pytest.raises(ValidationError):
        validate_capture_timestamp(naive)


# ---------------------------------------------------------------------------
# 4. Report Formatting, Geometry & Utility Unit Tests (90 tests)
# ---------------------------------------------------------------------------
DURATION_CASES = [
    (None, "—"),
    (0.0, "<1m"),
    (0.4, "<1m"),
    (0.6, "1m"),
    (1.0, "1m"),
    (14.4, "14m"),
    (59.4, "59m"),
    (60.0, "1h 00m"),
    (61.0, "1h 01m"),
    (90.0, "1h 30m"),
    (125.0, "2h 05m"),
    (600.0, "10h 00m"),
]


@pytest.mark.parametrize(("minutes", "expected"), DURATION_CASES)
def test_unit_format_duration(minutes, expected):
    assert _format_duration(minutes) == expected


SPEED_FORMAT_CASES = [
    (None, "—"),
    (0.0, "0.0 km/h"),
    (4.94, "4.9 km/h"),
    (25.95, "25.9 km/h"),
    (45.0, "45.0 km/h"),
    (102.34, "102.3 km/h"),
]


@pytest.mark.parametrize(("val", "expected"), SPEED_FORMAT_CASES)
def test_unit_format_speed(val, expected):
    assert _format_speed(val) == expected


ACCURACY_FORMAT_CASES = [
    (None, "—"),
    (0.0, "0 m"),
    (7.4, "7 m"),
    (7.6, "8 m"),
    (59.0, "59 m"),
    (141.2, "141 m"),
]


@pytest.mark.parametrize(("val", "expected"), ACCURACY_FORMAT_CASES)
def test_unit_format_accuracy(val, expected):
    assert _format_accuracy(val) == expected


DISTANCE_FORMAT_CASES = [
    (0.0, "0.00 km"),
    (0.034, "0.03 km"),
    (1.5, "1.50 km"),
    (16.194, "16.19 km"),
    (123.456, "123.46 km"),
]


@pytest.mark.parametrize(("val", "expected"), DISTANCE_FORMAT_CASES)
def test_unit_format_distance(val, expected):
    assert _format_distance(val) == expected


NICE_MAX_CASES = [
    (0.0, 1.0),
    (0.5, 1.0),
    (1.0, 2.0),
    (2.1, 3.0),
    (4.0, 6.0),
    (6.68, 8.0),
    (8.5, 10.0),
    (10.0, 15.0),
    (18.0, 25.0),
    (35.0, 40.0),
    (77.0, 90.0),
    (225.0, 300.0),
]


@pytest.mark.parametrize(("raw", "expected"), NICE_MAX_CASES)
def test_unit_nice_maximum_float(raw, expected):
    ceiling = _nice_maximum_float(raw)
    assert ceiling == expected
    assert ceiling >= raw


CHART_VAL_CASES = [
    (0.0, 0, "0"),
    (7.0, 0, "7"),
    (225.0, 0, "225"),
    (1000.0, 0, "1.0k"),
    (2540.0, 0, "2.5k"),
    (6.7, 1, "6.7"),
    (0.0, 1, "0.0"),
]


@pytest.mark.parametrize(("val", "decimals", "expected"), CHART_VAL_CASES)
def test_unit_format_chart_value(val, decimals, expected):
    assert _format_chart_value(val, decimals=decimals) == expected


SAFE_TEXT_CASES = [
    ("CU-01", "CU-01"),
    ("A & B", "A &amp; B"),
    ("<script>x</script>", "&lt;script&gt;x&lt;/script&gt;"),
    ("line1\nline2", "line1<br/>line2"),
    ('"quoted"', "&quot;quoted&quot;"),
    ("10 < 20 & 30 > 5", "10 &lt; 20 &amp; 30 &gt; 5"),
]


@pytest.mark.parametrize(("raw", "expected"), SAFE_TEXT_CASES)
def test_unit_safe_text_escapes_xml(raw, expected):
    assert _safe_text(raw) == expected


TRUNCATE_CASES = [
    ("CU-01", 10, "CU-01"),
    ("Exact10Chr", 10, "Exact10Chr"),
    ("VeryLongBusRouteName", 10, "VeryLongB…"),
    ("ABCDEFGH", 5, "ABCD…"),
    ("", 8, ""),
]


@pytest.mark.parametrize(("text", "limit", "expected"), TRUNCATE_CASES)
def test_unit_truncate(text, limit, expected):
    assert _truncate(text, limit) == expected


SPEED_PAIR_CASES = [
    (None, None, "Peak", "—"),
    (20.0, 40.0, "Peak", "20.0 km/h<br/><font color='#64748B'>Peak 40.0 km/h</font>"),
    (15.5, 32.0, "Max", "15.5 km/h<br/><font color='#64748B'>Max 32.0 km/h</font>"),
    (None, 30.0, "Max", "—<br/><font color='#64748B'>Max 30.0 km/h</font>"),
]


@pytest.mark.parametrize(("avg", "peak", "prefix", "expected"), SPEED_PAIR_CASES)
def test_unit_format_speed_pair(avg, peak, prefix, expected):
    assert _format_speed_pair(avg, peak, prefix=prefix) == expected


ORIGIN_DEST_CASES = [
    (None, None, "—"),
    ((22.4716, 91.7876), None, "22.4716, 91.7876"),
    ((22.4716, 91.7876), (22.4716, 91.7876), "22.4716, 91.7876"),
    (
        (22.4716, 91.7876),
        (22.3683, 91.8263),
        "22.4716, 91.7876<br/><font color='#64748B'>to 22.3683, 91.8263</font>",
    ),
]


@pytest.mark.parametrize(("start_c", "end_c", "expected"), ORIGIN_DEST_CASES)
def test_unit_format_origin_dest(start_c, end_c, expected):
    assert _format_origin_dest(start_c, end_c) == expected


DATE_WINDOW_CASES = [
    (None, None, "All recorded dates"),
    (date(2026, 11, 24), date(2026, 11, 24), "24 Nov 2026"),
    (date(2026, 11, 1), date(2026, 11, 24), "01 Nov 2026 — 24 Nov 2026"),
    (date(2026, 11, 1), None, "From 01 Nov 2026"),
    (None, date(2026, 11, 24), "Up to 24 Nov 2026"),
]


@pytest.mark.parametrize(("d_from", "d_to", "expected"), DATE_WINDOW_CASES)
def test_unit_format_date_window(d_from, d_to, expected):
    assert _format_date_window(date_from=d_from, date_to=d_to) == expected


SAMPLING_DESC_CASES = [
    (100, 100, 0, "Forensic raw mode"),
    (100, 12, 60, "1 min"),
    (260, 59, 120, "2 min"),
    (500, 20, 300, "5 min"),
    (50, 10, 45, "45s"),
]


@pytest.mark.parametrize(("raw", "sampled", "interval", "needle"), SAMPLING_DESC_CASES)
def test_unit_sampling_description(raw, sampled, interval, needle):
    desc = _sampling_description(raw_count=raw, sampled_count=sampled, interval_seconds=interval)
    assert needle in desc


FILENAME_CASES = [
    (ReportType.EXECUTIVE_SUMMARY, "fleet-record-20261124-"),
    (ReportType.TRIP_SUMMARY, "fleet-record-trips-20261124-"),
    (ReportType.SAFETY_AUDIT, "fleet-record-safety-audit-20261124-"),
    (ReportType.TELEMETRY_AUDIT, "fleet-record-telemetry-trace-20261124-"),
]


@pytest.mark.parametrize(("rtype", "prefix"), FILENAME_CASES)
def test_unit_fleet_record_filename(rtype, prefix):
    ts = datetime(2026, 11, 24, 6, 0, tzinfo=dt_tz.utc)
    name = fleet_record_filename(generated_at=ts, report_type=rtype)
    assert name.startswith(prefix)
    assert name.endswith(".pdf")
    assert name.isascii()


TRIP_FILENAME_CASES = [
    (ReportType.TRIP_SUMMARY, "trip-history-20261124-"),
    (ReportType.SAFETY_AUDIT, "trip-history-safety-audit-20261124-"),
    (ReportType.TELEMETRY_AUDIT, "trip-history-telemetry-trace-20261124-"),
]


@pytest.mark.parametrize(("rtype", "prefix"), TRIP_FILENAME_CASES)
def test_unit_trip_history_filename(rtype, prefix):
    ts = datetime(2026, 11, 24, 6, 0, tzinfo=dt_tz.utc)
    name = trip_history_filename(generated_at=ts, report_type=rtype)
    assert name.startswith(prefix)
    assert name.endswith(".pdf")
    assert name.isascii()


HAVERSINE_KNOWN_CASES = [
    # Identical points = 0
    (22.4716, 91.7876, 22.4716, 91.7876, 0.0, 0.001),
    # 1 degree latitude ~= 111.19 km
    (0.0, 0.0, 1.0, 0.0, 111.19, 0.2),
    # 1 degree longitude at equator ~= 111.19 km
    (0.0, 0.0, 0.0, 1.0, 111.19, 0.2),
    # CU Main Gate to Chattogram GEC (~12.1 km straight line)
    (22.4716, 91.7876, 22.3591, 91.8215, 13.0, 1.2),
    # Dhaka to Chattogram (~215 km straight line)
    (23.8103, 90.4125, 22.3569, 91.7832, 214.0, 10.0),
    # Antipodal poles (~20,015 km)
    (90.0, 0.0, -90.0, 0.0, 20015.0, 5.0),
    # Small campus hop (~150 m)
    (22.4716, 91.7876, 22.4729, 91.7876, 0.145, 0.02),
    # Negative hemisphere symmetry
    (-22.4716, -91.7876, -22.3591, -91.8215, 13.0, 1.2),
]


@pytest.mark.parametrize(("lat1", "lon1", "lat2", "lon2", "expected_km", "tol"), HAVERSINE_KNOWN_CASES)
def test_unit_haversine_known_distances(lat1, lon1, lat2, lon2, expected_km, tol):
    dist = _haversine_km(lat1, lon1, lat2, lon2)
    assert abs(dist - expected_km) <= tol
