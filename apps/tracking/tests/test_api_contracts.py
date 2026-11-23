"""REST API contract, schema, boundary, and anti-spoofing integration tests."""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.fleet.models import BusRoute, RouteStop
from apps.tracking.models import Location, Trip, TripStatus

pytestmark = pytest.mark.django_db

PUBLIC_VEHICLE_KEYS = {
    "vehicle_id",
    "bus_number",
    "route_label",
    "has_signal",
    "latitude",
    "longitude",
    "speed_kmh",
    "captured_at",
    "age_seconds",
    "is_stale",
    "trajectory",
}
ADMIN_VEHICLE_KEYS = PUBLIC_VEHICLE_KEYS | {"driver_name", "accuracy_m"}


# ---------------------------------------------------------------------------
# 1. Public & Admin Live Locations API Contract (35 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("age_seconds,expected_stale", [
    (0, False),
    (1, False),
    (5, False),
    (10, False),
    (15, False),
    (25, False),
    (29, False),
    (31, True),
    (45, True),
    (60, True),
    (120, True),
    (600, True),
])
def test_api_contract_stale_flag_boundary(vehicle, open_trip, add_point, age_seconds, expected_stale):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(seconds=age_seconds))
    client = APIClient()
    resp = client.get(reverse("api:vehicle-latest-locations"))
    assert resp.status_code == 200
    row = resp.json()["results"][0]
    assert set(row.keys()) == PUBLIC_VEHICLE_KEYS
    assert row["is_stale"] is expected_stale


@pytest.mark.parametrize("turn_count", [1, 2, 3, 5, 8, 12, 15, 20])
def test_api_contract_trajectory_preserves_exact_ordered_points(vehicle, open_trip, add_point, turn_count):
    base = timezone.now() - timedelta(minutes=10)
    expected = []
    for i in range(turn_count):
        lat = Decimal("22.471600") + Decimal("0.000100") * i
        lon = Decimal("91.787600") + Decimal("0.000150") * (i % 4)
        add_point(trip=open_trip, captured_at=base + timedelta(seconds=i * 10), latitude=lat, longitude=lon)
        expected.append((str(lat), str(lon)))

    client = APIClient()
    resp = client.get(reverse("api:vehicle-latest-locations"))
    assert resp.status_code == 200
    traj = resp.json()["results"][0]["trajectory"]
    assert len(traj) == turn_count
    assert [(p["latitude"], p["longitude"]) for p in traj] == expected
    for p in traj:
        assert set(p.keys()) == {"latitude", "longitude", "captured_at"}


@pytest.mark.parametrize("role", ["anon", "driver", "admin", "superuser"])
def test_api_contract_vehicle_schema_by_role(
    admin_user, superuser, driver_user, vehicle, open_trip, add_point, role
):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(seconds=5), accuracy_m=Decimal("7.50"))
    client = APIClient()
    if role == "admin":
        client.force_authenticate(user=admin_user)
    elif role == "superuser":
        client.force_authenticate(user=superuser)
    elif role == "driver":
        client.force_authenticate(user=driver_user)

    resp = client.get(reverse("api:vehicle-latest-locations"))
    assert resp.status_code == 200
    row = resp.json()["results"][0]
    expected_keys = ADMIN_VEHICLE_KEYS if role in ("admin", "superuser") else PUBLIC_VEHICLE_KEYS
    assert set(row.keys()) == expected_keys


@pytest.mark.parametrize("bad_id", [99991, 99992, 99993, 99994, 99995])
def test_api_contract_single_vehicle_missing_returns_404(bad_id):
    client = APIClient()
    resp = client.get(reverse("api:vehicle-latest-location", args=[bad_id]))
    assert resp.status_code == 404


@pytest.mark.parametrize("inactive_count", [1, 2, 3, 4, 5, 6])
def test_api_contract_inactive_vehicles_hidden_from_live_feed(make_vehicle, inactive_count):
    active_v = make_vehicle(bus_number="LIVE-1", is_active=True)
    for i in range(inactive_count):
        make_vehicle(bus_number=f"OFF-{i}", is_active=False)
    client = APIClient()
    resp = client.get(reverse("api:vehicle-latest-locations"))
    assert resp.status_code == 200
    ids = [v["vehicle_id"] for v in resp.json()["results"]]
    assert ids == [active_v.pk]


# ---------------------------------------------------------------------------
# 2. GPS Location Ingestion API Contract & Anti-Spoofing (35 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("lat", "lon", "speed", "accuracy"),
    [
        ("22.471600", "91.787600", "0.00", "5.00"),
        ("22.472100", "91.788100", "12.50", "8.25"),
        ("22.473200", "91.789200", "28.75", "11.00"),
        ("22.474300", "91.790300", "44.99", "14.50"),
        ("22.475400", "91.791400", "55.00", "20.00"),
        ("22.476500", "91.792500", None, "9.00"),
        ("22.477600", "91.793600", "19.20", None),
        ("22.478700", "91.794700", None, None),
        ("-22.471600", "-91.787600", "30.00", "6.00"),
        ("0.000000", "0.000000", "1.00", "1.00"),
    ],
)
def test_api_contract_location_ingest_valid_payloads(assigned_driver, vehicle, lat, lon, speed, accuracy):
    client = APIClient()
    client.force_authenticate(user=assigned_driver)
    body = {
        "client_event_id": str(uuid.uuid4()),
        "latitude": lat,
        "longitude": lon,
        "captured_at": timezone.now().isoformat(),
    }
    if speed is not None:
        body["speed_kmh"] = speed
    if accuracy is not None:
        body["accuracy_m"] = accuracy

    resp = client.post(reverse("api:location-create"), body, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert set(data.keys()) == {"id", "trip_id", "captured_at", "received_at", "duplicate"}
    assert data["duplicate"] is False
    assert Location.objects.get(pk=data["id"]).vehicle_id == vehicle.pk


@pytest.mark.parametrize("replay_count", [2, 3, 4, 5, 6])
def test_api_contract_location_ingest_idempotent_replays(assigned_driver, replay_count):
    client = APIClient()
    client.force_authenticate(user=assigned_driver)
    event_id = str(uuid.uuid4())
    payload = {
        "client_event_id": event_id,
        "latitude": "22.471600",
        "longitude": "91.787600",
        "captured_at": timezone.now().isoformat(),
    }
    statuses = [client.post(reverse("api:location-create"), payload, format="json").status_code for _ in range(replay_count)]
    assert statuses[0] == 201
    assert all(s == 200 for s in statuses[1:])
    assert Location.objects.filter(client_event_id=event_id).count() == 1


@pytest.mark.parametrize("forged_field,forged_val", [
    ("vehicle_id", 99999),
    ("vehicle", 99999),
    ("driver_id", 99999),
    ("driver", 99999),
    ("trip_id", 99999),
])
def test_api_contract_location_ingest_ignores_forged_identity_fields(
    assigned_driver, vehicle, driver_profile, forged_field, forged_val
):
    client = APIClient()
    client.force_authenticate(user=assigned_driver)
    payload = {
        "client_event_id": str(uuid.uuid4()),
        "latitude": "22.471600",
        "longitude": "91.787600",
        "captured_at": timezone.now().isoformat(),
        forged_field: forged_val,
    }
    resp = client.post(reverse("api:location-create"), payload, format="json")
    assert resp.status_code == 201
    loc = Location.objects.get(pk=resp.json()["id"])
    assert loc.vehicle_id == vehicle.pk
    assert loc.driver_id == driver_profile.pk


BAD_INGEST_PAYLOADS = [
    {"latitude": "22.47", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": "bad", "latitude": "22.47", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "95.0", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "-95.0", "longitude": "91.78", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "185.0", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "-185.0", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "speed_kmh": "-5.00", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "accuracy_m": "-1.00", "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "captured_at": "not-a-timestamp"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78"},
    {"client_event_id": str(uuid.uuid4()), "captured_at": "2026-11-24T04:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "captured_at": "2020-01-01T00:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "captured_at": "2099-01-01T00:00:00Z"},
    {"client_event_id": str(uuid.uuid4()), "latitude": "22.47", "longitude": "91.78", "speed_kmh": "500.00", "captured_at": "2026-11-24T04:00:00Z"},
    {},
]


@pytest.mark.parametrize("payload", BAD_INGEST_PAYLOADS)
def test_api_contract_location_ingest_rejects_bad_payloads(assigned_driver, payload):
    client = APIClient()
    client.force_authenticate(user=assigned_driver)
    resp = client.post(reverse("api:location-create"), payload, format="json")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 3. Fixed BusRoute CRUD API Contract (30 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("stop_count", [0, 1, 2, 3, 4, 5, 6, 8, 10, 12])
def test_api_contract_bus_route_create_and_stop_ordering(admin_user, stop_count):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    stops = [
        {"name": f"Stop {i}", "latitude": f"{22.46 - i * 0.005:.6f}", "longitude": f"{91.79 + i * 0.003:.6f}"}
        for i in range(1, stop_count + 1)
    ]
    resp = client.post(
        reverse("api:bus-route-list"),
        {
            "name": f"Route-{stop_count}-Stops",
            "start_latitude": "22.471600",
            "start_longitude": "91.787600",
            "end_latitude": "22.356900",
            "end_longitude": "91.830000",
            "stops": stops,
        },
        format="json",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["stops"]) == stop_count
    assert [s["sequence"] for s in data["stops"]] == list(range(1, stop_count + 1))
    assert RouteStop.objects.filter(route_id=data["id"]).count() == stop_count


@pytest.mark.parametrize("bad_route_id", [88801, 88802, 88803, 88804, 88805])
def test_api_contract_bus_route_delete_missing_returns_404(admin_user, bad_route_id):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.delete(reverse("api:bus-route-detail", args=[bad_route_id]))
    assert resp.status_code == 404


@pytest.mark.parametrize("variant", ["CU-GEC", "cu-gec", "Cu-Gec", "  CU-GEC  ", "cU-gEc"])
def test_api_contract_bus_route_duplicate_name_rejected(admin_user, variant):
    BusRoute.objects.create(
        name="CU-GEC",
        start_latitude=Decimal("22.471600"),
        start_longitude=Decimal("91.787600"),
        end_latitude=Decimal("22.356900"),
        end_longitude=Decimal("91.821500"),
    )
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.post(
        reverse("api:bus-route-list"),
        {
            "name": variant,
            "start_latitude": "22.471600",
            "start_longitude": "91.787600",
            "end_latitude": "22.356900",
            "end_longitude": "91.821500",
            "stops": [],
        },
        format="json",
    )
    assert resp.status_code == 400


@pytest.mark.parametrize("method", ["get", "post", "delete"])
@pytest.mark.parametrize("role", ["anon", "driver"])
def test_api_contract_bus_route_non_admin_forbidden(driver_user, method, role):
    route = BusRoute.objects.create(
        name="Protected Route",
        start_latitude=Decimal("22.471600"),
        start_longitude=Decimal("91.787600"),
        end_latitude=Decimal("22.356900"),
        end_longitude=Decimal("91.821500"),
    )
    client = APIClient()
    if role == "driver":
        client.force_authenticate(user=driver_user)
    url = reverse("api:bus-route-detail", args=[route.pk]) if method == "delete" else reverse("api:bus-route-list")
    resp = getattr(client, method)(url, {}, format="json")
    assert resp.status_code == 403


@pytest.mark.parametrize("idx", range(4))
def test_api_contract_bus_route_delete_cascades_stops(admin_user, idx):
    route = BusRoute.objects.create(
        name=f"Cascade-{idx}",
        start_latitude=Decimal("22.471600"),
        start_longitude=Decimal("91.787600"),
        end_latitude=Decimal("22.356900"),
        end_longitude=Decimal("91.821500"),
    )
    RouteStop.objects.create(route=route, sequence=1, name="Mid", latitude=Decimal("22.41"), longitude=Decimal("91.80"))
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.delete(reverse("api:bus-route-detail", args=[route.pk]))
    assert resp.status_code == 204
    assert not BusRoute.objects.filter(pk=route.pk).exists()
    assert not RouteStop.objects.filter(route_id=route.pk).exists()


# ---------------------------------------------------------------------------
# 4. Trip History & Points API Contract (30 tests)
# ---------------------------------------------------------------------------
BAD_TRIP_DATES = [
    "2026-13-01",
    "2026-00-10",
    "2026-02-30",
    "24-11-2026",
    "not-a-date",
    "2026/11/24",
    "12345",
    "2026-11",
    "yesterday",
    "9999-99-99",
]


@pytest.mark.parametrize("bad_date", BAD_TRIP_DATES)
def test_api_contract_trip_list_rejects_bad_dates(admin_user, vehicle, bad_date):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.get(reverse("api:trip-list"), {"vehicle_id": str(vehicle.pk), "date": bad_date})
    assert resp.status_code == 400


BAD_TIME_PARAMS = [
    {"start": "25:00"},
    {"start": "12:60"},
    {"start": "noon"},
    {"start": "99:99"},
    {"end": "25:00"},
    {"end": "invalid"},
    {"end": "14:75"},
    {"start": "14:00", "end": "bad"},
    {"start": "bad", "end": "14:00"},
    {"start": "abc", "end": "xyz"},
]


@pytest.mark.parametrize("params", BAD_TIME_PARAMS)
def test_api_contract_trip_points_rejects_bad_times(admin_user, open_trip, params):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.get(reverse("api:trip-points", args=[open_trip.pk]), params)
    assert resp.status_code == 400


@pytest.mark.parametrize("bad_trip_id", [77701, 77702, 77703, 77704, 77705])
def test_api_contract_trip_points_missing_trip_returns_404(admin_user, bad_trip_id):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.get(reverse("api:trip-points", args=[bad_trip_id]))
    assert resp.status_code == 404


@pytest.mark.parametrize("point_count", [1, 3, 6, 10, 15])
def test_api_contract_trip_points_stable_order_with_tied_timestamps(admin_user, open_trip, add_point, point_count):
    ts = timezone.now() - timedelta(minutes=5)
    created_ids = []
    for i in range(point_count):
        loc = add_point(
            trip=open_trip,
            captured_at=ts,
            latitude=Decimal("22.470000") + Decimal("0.000100") * i,
            longitude=Decimal("91.787600"),
        )
        created_ids.append(loc.pk)

    client = APIClient()
    client.force_authenticate(user=admin_user)
    resp = client.get(reverse("api:trip-points", args=[open_trip.pk]))
    assert resp.status_code == 200
    pts = resp.json()["points"]
    assert len(pts) == point_count
    lats = [Decimal(p["latitude"]) for p in pts]
    assert lats == sorted(lats)
