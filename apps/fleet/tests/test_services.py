"""Fleet service tests: assignment lifecycle and vehicle activation."""

from __future__ import annotations

import pytest

from apps.fleet.models import DriverAssignment
from apps.fleet.services import (
    activate_vehicle,
    assign_driver_to_vehicle,
    deactivate_vehicle,
    end_assignment,
)

pytestmark = pytest.mark.django_db


def test_assign_creates_active_assignment(driver_profile, vehicle):
    assignment = assign_driver_to_vehicle(driver=driver_profile, vehicle=vehicle)
    assert assignment.is_active is True
    assert assignment.ends_at is None


def test_reassigning_driver_closes_previous(driver_profile, make_vehicle):
    v1 = make_vehicle()
    v2 = make_vehicle()
    first = assign_driver_to_vehicle(driver=driver_profile, vehicle=v1)
    second = assign_driver_to_vehicle(driver=driver_profile, vehicle=v2)

    first.refresh_from_db()
    assert first.is_active is False
    assert first.ends_at is not None
    assert second.is_active is True
    assert DriverAssignment.objects.filter(driver=driver_profile, is_active=True).count() == 1


def test_assigning_new_driver_frees_occupied_vehicle(make_driver, vehicle):
    d1 = make_driver(username="d1")
    d2 = make_driver(username="d2")
    a1 = assign_driver_to_vehicle(driver=d1, vehicle=vehicle)
    a2 = assign_driver_to_vehicle(driver=d2, vehicle=vehicle)

    a1.refresh_from_db()
    assert a1.is_active is False
    assert a2.is_active is True
    assert DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).count() == 1


def test_end_assignment(assignment):
    ended = end_assignment(assignment)
    assert ended.is_active is False
    assert ended.ends_at is not None


def test_end_assignment_is_idempotent(assignment):
    end_assignment(assignment)
    first_ends_at = assignment.ends_at
    end_assignment(assignment)
    assert assignment.ends_at == first_ends_at


def test_deactivate_vehicle_ends_active_assignment(assignment, vehicle):
    deactivate_vehicle(vehicle)
    vehicle.refresh_from_db()
    assignment.refresh_from_db()
    assert vehicle.is_active is False
    assert assignment.is_active is False


def test_activate_vehicle(vehicle):
    deactivate_vehicle(vehicle)
    activate_vehicle(vehicle)
    vehicle.refresh_from_db()
    assert vehicle.is_active is True
