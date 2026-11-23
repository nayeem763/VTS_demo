"""Database constraint, transactional service, selector, and management-command integration tests."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile
from apps.accounts.services import activate_driver, create_driver, deactivate_driver, update_driver
from apps.fleet.models import BusRoute, DriverAssignment, RouteStop, Vehicle
from apps.fleet.selectors import (
    get_active_assignment_for_driver,
    get_active_assignment_for_user,
    get_active_assignment_for_vehicle,
    get_active_vehicles,
)
from apps.fleet.services import (
    activate_vehicle,
    assign_driver_to_vehicle,
    create_vehicle,
    deactivate_vehicle,
    delete_vehicle_if_unused,
    end_assignment,
    update_vehicle,
)
from apps.tracking.models import Location, Trip, TripStatus
from apps.tracking.selectors import (
    get_latest_vehicle_location,
    get_location_trajectory,
    get_open_trip_for_vehicle,
    get_trip_points,
    get_vehicle_trips,
)
from apps.tracking.services import (
    NoActiveAssignment,
    VehicleInactive,
    close_open_trip_for_user,
    close_stale_trips,
    close_trip,
    record_vehicle_location,
)

pytestmark = pytest.mark.django_db

# ---------------------------------------------------------------------------
# 1. Database CheckConstraints & UniqueConstraints (30 tests)
# ---------------------------------------------------------------------------
INVALID_DB_LOCATIONS = [
    {"latitude": Decimal("90.1"), "longitude": Decimal("91.78")},
    {"latitude": Decimal("-90.1"), "longitude": Decimal("91.78")},
    {"latitude": Decimal("99.9"), "longitude": Decimal("91.78")},
    {"latitude": Decimal("-99.9"), "longitude": Decimal("91.78")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("180.1")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("-180.1")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("250.0")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("-250.0")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("91.78"), "speed_kmh": Decimal("-0.01")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("91.78"), "speed_kmh": Decimal("-10.00")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("91.78"), "accuracy_m": Decimal("-0.01")},
    {"latitude": Decimal("22.47"), "longitude": Decimal("91.78"), "accuracy_m": Decimal("-25.00")},
]


@pytest.mark.parametrize("fields", INVALID_DB_LOCATIONS)
def test_db_location_check_constraints_reject_invalid_rows(vehicle, driver_profile, open_trip, fields):
    with pytest.raises(IntegrityError), transaction.atomic():
        Location.objects.create(
            vehicle=vehicle,
            driver=driver_profile,
            trip=open_trip,
            captured_at=timezone.now(),
            **fields,
        )


@pytest.mark.parametrize("idx", range(6))
def test_db_only_one_open_trip_per_vehicle(make_vehicle, driver_profile, idx):
    v = make_vehicle(bus_number=f"OT-{idx}")
    Trip.objects.create(vehicle=v, driver=driver_profile, started_at=timezone.now(), status=TripStatus.OPEN)
    with pytest.raises(IntegrityError), transaction.atomic():
        Trip.objects.create(vehicle=v, driver=driver_profile, started_at=timezone.now(), status=TripStatus.OPEN)


@pytest.mark.parametrize("completed_count", [1, 2, 3, 4])
def test_db_multiple_completed_trips_allowed_per_vehicle(make_vehicle, driver_profile, completed_count):
    v = make_vehicle(bus_number=f"CT-{completed_count}")
    for i in range(completed_count):
        Trip.objects.create(
            vehicle=v,
            driver=driver_profile,
            started_at=timezone.now() - timedelta(hours=i + 1),
            ended_at=timezone.now() - timedelta(hours=i),
            status=TripStatus.COMPLETED,
        )
    assert Trip.objects.filter(vehicle=v, status=TripStatus.COMPLETED).count() == completed_count


@pytest.mark.parametrize("seq", [1, 2, 3, 4])
def test_db_route_stop_unique_sequence_per_route(seq):
    route = BusRoute.objects.create(
        name=f"SeqRoute-{seq}",
        start_latitude=Decimal("22.47"),
        start_longitude=Decimal("91.78"),
        end_latitude=Decimal("22.35"),
        end_longitude=Decimal("91.82"),
    )
    RouteStop.objects.create(route=route, sequence=seq, name="Stop A", latitude=Decimal("22.41"), longitude=Decimal("91.80"))
    with pytest.raises(IntegrityError), transaction.atomic():
        RouteStop.objects.create(route=route, sequence=seq, name="Stop B", latitude=Decimal("22.42"), longitude=Decimal("91.81"))


@pytest.mark.parametrize("idx", range(4))
def test_db_vehicle_unique_registration_number(idx):
    Vehicle.objects.create(bus_number=f"UR-A-{idx}", registration_number=f"CTG-{idx:04d}")
    with pytest.raises(IntegrityError), transaction.atomic():
        Vehicle.objects.create(bus_number=f"UR-B-{idx}", registration_number=f"CTG-{idx:04d}")


# ---------------------------------------------------------------------------
# 2. Multi-Step Service State Transitions & Commands (40 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("chain_len", [2, 3, 4, 5, 6])
def test_service_chained_driver_reassignments_preserve_single_active(make_vehicle, driver_profile, chain_len):
    vehicles = [make_vehicle(bus_number=f"CH-{chain_len}-{i}") for i in range(chain_len)]
    for v in vehicles:
        assign_driver_to_vehicle(driver=driver_profile, vehicle=v)
        assert DriverAssignment.objects.filter(driver=driver_profile, is_active=True).count() == 1
    assert DriverAssignment.objects.filter(driver=driver_profile, is_active=False).count() == chain_len - 1
    active = get_active_assignment_for_driver(driver_profile)
    assert active is not None and active.vehicle == vehicles[-1]


@pytest.mark.parametrize("cycles", [1, 2, 3, 4, 5])
def test_service_vehicle_activate_deactivate_cycles(make_vehicle, driver_profile, cycles):
    v = make_vehicle(bus_number=f"CYC-{cycles}")
    for _ in range(cycles):
        assign_driver_to_vehicle(driver=driver_profile, vehicle=v)
        Trip.objects.create(vehicle=v, driver=driver_profile, started_at=timezone.now(), status=TripStatus.OPEN)
        deactivate_vehicle(v)
        assert not v.is_active
        assert get_active_assignment_for_vehicle(v) is None
        assert get_open_trip_for_vehicle(v) is None
        activate_vehicle(v)
        assert v.is_active


@pytest.mark.parametrize("cycles", [1, 2, 3, 4, 5])
def test_service_driver_deactivate_reactivate_cycles(make_vehicle, make_driver, cycles):
    v = make_vehicle(bus_number=f"DCYC-{cycles}")
    d = make_driver(username=f"dcyc_{cycles}")
    for _ in range(cycles):
        assign_driver_to_vehicle(driver=d, vehicle=v)
        Trip.objects.create(vehicle=v, driver=d, started_at=timezone.now(), status=TripStatus.OPEN)
        deactivate_driver(d)
        assert not d.is_active and not d.user.is_active
        assert get_active_assignment_for_driver(d) is None
        assert get_open_trip_for_vehicle(v) is None
        activate_driver(d)
        assert d.is_active and d.user.is_active


@pytest.mark.parametrize("inactive_side", ["vehicle", "driver"])
def test_service_assign_rejects_inactive_entity(make_vehicle, make_driver, inactive_side):
    v = make_vehicle(bus_number=f"IN-{inactive_side}", is_active=(inactive_side != "vehicle"))
    d = make_driver(username=f"in_{inactive_side}")
    if inactive_side == "driver":
        d.is_active = False
        d.save(update_fields=["is_active"])
    with pytest.raises(ValueError):
        assign_driver_to_vehicle(driver=d, vehicle=v)


@pytest.mark.parametrize("age_mins,threshold,should_close", [
    (5, 15, False),
    (10, 15, False),
    (14, 15, False),
    (16, 15, True),
    (30, 15, True),
    (60, 30, True),
    (20, 30, False),
    (120, 60, True),
])
def test_service_close_stale_trips_threshold_matrix(
    make_vehicle, driver_profile, age_mins, threshold, should_close
):
    v = make_vehicle(bus_number=f"ST-{age_mins}-{threshold}")
    trip = Trip.objects.create(
        vehicle=v,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=age_mins),
        status=TripStatus.OPEN,
    )
    closed = close_stale_trips(threshold_minutes=threshold)
    trip.refresh_from_db()
    assert closed == (1 if should_close else 0)
    assert trip.status == (TripStatus.COMPLETED if should_close else TripStatus.OPEN)


@pytest.mark.parametrize("idx", range(5))
def test_service_vehicle_create_update_delete_lifecycle(idx):
    v = create_vehicle(
        bus_number=f"LC-{idx}",
        registration_number=f"REG-LC-{idx}",
        route_label="Old Route",
        admin_description="Initial admin note",
    )
    update_vehicle(
        v,
        bus_number=f"LC-{idx}-REN",
        registration_number=f"REG-LC-{idx}",
        route_label="New Route",
        admin_description="Updated admin note",
    )
    v.refresh_from_db()
    assert v.bus_number == f"LC-{idx}-REN"
    assert v.admin_description == "Updated admin note"
    ok, _msg = delete_vehicle_if_unused(v)
    assert ok is True
    assert not Vehicle.objects.filter(pk=v.pk).exists()


@pytest.mark.parametrize("idx", range(5))
def test_service_driver_create_update_password_and_login(idx):
    d = create_driver(
        username=f"srv_drv_{idx}",
        password=f"InitPass!{idx:03d}",
        first_name="First",
        last_name=f"Last{idx}",
        employee_id=f"SEMP-{idx}",
        phone_number=f"01700000{idx}",
    )
    update_driver(
        d,
        first_name="Updated",
        last_name=f"Name{idx}",
        employee_id=f"SEMP-{idx}",
        phone_number=f"01800000{idx}",
        new_password=f"NewPass!{idx:03d}",
    )
    d.refresh_from_db()
    assert d.display_name == f"Updated Name{idx}"
    assert d.user.check_password(f"NewPass!{idx:03d}")


def test_management_command_seed_roles_is_idempotent():
    call_command("seed_roles")
    call_command("seed_roles")
    assert Group.objects.filter(name="Admin").exists()
    assert Group.objects.filter(name="Driver").exists()


def test_management_command_close_stale_trips_runs_cleanly(vehicle, driver_profile):
    Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(hours=3),
        status=TripStatus.OPEN,
    )
    call_command("close_stale_trips")
    assert Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).count() == 0


def test_management_command_create_demo_data_is_idempotent():
    call_command("create_demo_data")
    v_count = Vehicle.objects.count()
    d_count = DriverProfile.objects.count()
    call_command("create_demo_data")
    assert Vehicle.objects.count() == v_count
    assert DriverProfile.objects.count() == d_count
    assert v_count >= 1 and d_count >= 1


@pytest.mark.parametrize("idx", range(2))
def test_service_record_location_guards(driver_user, vehicle, make_driver, idx):
    if idx == 0:
        # Unassigned driver raises NoActiveAssignment
        with pytest.raises(NoActiveAssignment):
            record_vehicle_location(
                user=driver_user,
                client_event_id=f"00000000-0000-4000-8000-00000000000{idx}",
                latitude=Decimal("22.47"),
                longitude=Decimal("91.78"),
                captured_at=timezone.now(),
            )
    else:
        # Inactive vehicle raises VehicleInactive
        d = make_driver(username="guard_drv")
        assign_driver_to_vehicle(driver=d, vehicle=vehicle)
        Vehicle.objects.filter(pk=vehicle.pk).update(is_active=False)
        with pytest.raises(VehicleInactive):
            record_vehicle_location(
                user=d.user,
                client_event_id=f"00000000-0000-4000-8000-00000000000{idx}",
                latitude=Decimal("22.47"),
                longitude=Decimal("91.78"),
                captured_at=timezone.now(),
            )


# ---------------------------------------------------------------------------
# 3. Selectors & Query Correctness Integration Tests (30 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("n_active,n_inactive", [(0, 2), (1, 0), (3, 2), (5, 4), (7, 1)])
def test_selector_get_active_vehicles_counts_and_ordering(make_vehicle, n_active, n_inactive):
    for i in range(n_active):
        make_vehicle(bus_number=f"AV-{n_active - i:02d}", is_active=True)
    for i in range(n_inactive):
        make_vehicle(bus_number=f"IV-{i:02d}", is_active=False)
    active = list(get_active_vehicles())
    assert len(active) == n_active
    assert [v.bus_number for v in active] == sorted(v.bus_number for v in active)


@pytest.mark.parametrize("point_count", [0, 1, 2, 5, 10])
def test_selector_latest_location_and_trajectory_isolated_per_trip(
    vehicle, driver_profile, add_point, point_count
):
    old_trip = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(hours=2),
        ended_at=timezone.now() - timedelta(hours=1),
        status=TripStatus.COMPLETED,
    )
    add_point(trip=old_trip, captured_at=timezone.now() - timedelta(hours=1, minutes=30))

    new_trip = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=20),
        status=TripStatus.OPEN,
    )
    last_loc = None
    for i in range(point_count):
        last_loc = add_point(trip=new_trip, captured_at=timezone.now() - timedelta(minutes=15 - i))

    latest = get_latest_vehicle_location(vehicle)
    if point_count > 0:
        assert latest.pk == last_loc.pk
        traj = get_location_trajectory(latest)
        assert len(traj) == point_count
        assert all(p.trip_id == new_trip.pk for p in traj)
    else:
        assert latest.trip_id == old_trip.pk
        assert len(get_location_trajectory(latest)) == 1


@pytest.mark.parametrize("days_ago", [0, 1, 2, 3, 5])
def test_selector_get_vehicle_trips_date_filtering(vehicle, driver_profile, days_ago):
    target_dt = timezone.now() - timedelta(days=days_ago)
    Trip.objects.create(vehicle=vehicle, driver=driver_profile, started_at=target_dt, status=TripStatus.COMPLETED)
    Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=target_dt - timedelta(days=10),
        status=TripStatus.COMPLETED,
    )
    matching = list(get_vehicle_trips(vehicle=vehicle, on_date=timezone.localdate(target_dt)))
    assert len(matching) == 1


@pytest.mark.parametrize("slice_start,slice_end,expected_len", [
    (0, 9, 10),
    (2, 8, 7),
    (5, 9, 5),
    (0, 0, 1),
    (9, 9, 1),
])
def test_selector_get_trip_points_time_bounds(open_trip, add_point, slice_start, slice_end, expected_len):
    base = timezone.now() - timedelta(minutes=20)
    times = [base + timedelta(minutes=i) for i in range(10)]
    for t in times:
        add_point(trip=open_trip, captured_at=t)
    pts = list(get_trip_points(trip=open_trip, start=times[slice_start], end=times[slice_end]))
    assert len(pts) == expected_len


@pytest.mark.parametrize("scenario", ["assigned", "unassigned", "inactive_profile", "admin_no_profile", "ended_assignment"])
def test_selector_get_active_assignment_for_user_variants(
    admin_user, make_driver, vehicle, scenario
):
    if scenario == "admin_no_profile":
        assert get_active_assignment_for_user(admin_user) is None
        return
    d = make_driver(username=f"sel_{scenario}")
    if scenario == "inactive_profile":
        d.is_active = False
        d.save(update_fields=["is_active"])
    if scenario in ("assigned", "ended_assignment"):
        a = assign_driver_to_vehicle(driver=d, vehicle=vehicle)
        if scenario == "ended_assignment":
            end_assignment(a)
    res = get_active_assignment_for_user(d.user)
    if scenario == "assigned":
        assert res is not None and res.vehicle == vehicle
    else:
        assert res is None


@pytest.mark.parametrize("idx", range(5))
def test_selector_close_trip_and_open_trip_for_user_edge_cases(make_vehicle, make_driver, idx):
    v = make_vehicle(bus_number=f"CO-{idx}")
    d = make_driver(username=f"co_drv_{idx}")
    t = Trip.objects.create(vehicle=v, driver=d, started_at=timezone.now(), status=TripStatus.OPEN)
    assert get_open_trip_for_vehicle(v).pk == t.pk
    if idx % 2 == 0:
        close_open_trip_for_user(d.user, reason="logout")
    else:
        close_trip(t, reason="manual")
    assert get_open_trip_for_vehicle(v) is None
