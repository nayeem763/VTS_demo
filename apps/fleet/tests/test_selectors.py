"""Fleet selector tests: read-only assignment/vehicle resolution."""

from __future__ import annotations

import pytest

from apps.fleet.selectors import (
    get_active_assignment_for_driver,
    get_active_assignment_for_user,
    get_active_assignment_for_vehicle,
    get_active_vehicles,
)

pytestmark = pytest.mark.django_db


def test_get_active_vehicles_excludes_inactive_and_orders(make_vehicle):
    b = make_vehicle(bus_number="B-2")
    a = make_vehicle(bus_number="A-1")
    inactive = make_vehicle(bus_number="Z-9", is_active=False)

    result = list(get_active_vehicles())
    assert result == [a, b]
    assert inactive not in result


def test_active_assignment_for_user_resolves(assigned_driver, vehicle):
    assignment = get_active_assignment_for_user(assigned_driver)
    assert assignment is not None
    assert assignment.vehicle == vehicle


def test_active_assignment_for_user_none_without_assignment(driver_user):
    assert get_active_assignment_for_user(driver_user) is None


def test_active_assignment_for_user_none_for_non_driver(admin_user):
    assert get_active_assignment_for_user(admin_user) is None


def test_active_assignment_for_driver_and_vehicle(assignment, driver_profile, vehicle):
    assert get_active_assignment_for_driver(driver_profile) == assignment
    assert get_active_assignment_for_vehicle(vehicle) == assignment
