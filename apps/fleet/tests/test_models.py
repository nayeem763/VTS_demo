"""Fleet model constraint tests."""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.fleet.models import DriverAssignment, Vehicle

pytestmark = pytest.mark.django_db


def test_vehicle_str_is_bus_number(vehicle):
    assert str(vehicle) == "BUS-001"


def test_assignment_str_reflects_state(assignment):
    assert "active" in str(assignment)


def test_bus_number_is_unique(vehicle):
    with pytest.raises(IntegrityError), transaction.atomic():
        Vehicle.objects.create(bus_number="BUS-001")


def test_only_one_active_assignment_per_driver(driver_profile, make_vehicle):
    v1 = make_vehicle()
    v2 = make_vehicle()
    now = timezone.now()
    DriverAssignment.objects.create(driver=driver_profile, vehicle=v1, starts_at=now)
    with pytest.raises(IntegrityError), transaction.atomic():
        DriverAssignment.objects.create(driver=driver_profile, vehicle=v2, starts_at=now)


def test_only_one_active_assignment_per_vehicle(make_driver, vehicle):
    d1 = make_driver(username="d1")
    d2 = make_driver(username="d2")
    now = timezone.now()
    DriverAssignment.objects.create(driver=d1, vehicle=vehicle, starts_at=now)
    with pytest.raises(IntegrityError), transaction.atomic():
        DriverAssignment.objects.create(driver=d2, vehicle=vehicle, starts_at=now)


def test_ended_assignments_do_not_conflict(driver_profile, vehicle):
    now = timezone.now()
    DriverAssignment.objects.create(
        driver=driver_profile, vehicle=vehicle, starts_at=now, is_active=False, ends_at=now
    )
    # A second, also-ended assignment is allowed (partial constraint only guards active).
    DriverAssignment.objects.create(
        driver=driver_profile, vehicle=vehicle, starts_at=now, is_active=False, ends_at=now
    )
    assert DriverAssignment.objects.filter(is_active=False).count() == 2
