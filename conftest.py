"""Project-wide pytest fixtures.

Fixtures build the common object graph (admin, driver, vehicle, assignment)
through the real service layer, so the fixtures themselves exercise the code
they set up. Every fixture that touches the ORM depends on ``db`` so tests that
use them are granted database access transitively.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.utils import timezone

PASSWORD = "test-pass-9f2xQ"


@pytest.fixture
def password() -> str:
    """The plaintext password shared by all fixture users."""
    return PASSWORD


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset the cache around every test (isolates throttle/axes state)."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def admin_group(db) -> Group:
    return Group.objects.get_or_create(name=settings.ADMIN_GROUP)[0]


@pytest.fixture
def driver_group(db) -> Group:
    return Group.objects.get_or_create(name=settings.DRIVER_GROUP)[0]


@pytest.fixture
def admin_user(db, admin_group) -> User:
    """An authenticated Admin (group member, not a superuser)."""
    user = User.objects.create_user(username="admin1", password=PASSWORD)
    user.groups.add(admin_group)
    return user


@pytest.fixture
def superuser(db) -> User:
    return User.objects.create_superuser(username="root", password=PASSWORD)


@pytest.fixture
def make_driver(db, driver_group):
    """Factory: create a Driver user + active DriverProfile via the service."""
    from apps.accounts.services import create_driver

    def _make(username: str = "driver1", **kwargs):
        return create_driver(username=username, password=PASSWORD, **kwargs)

    return _make


@pytest.fixture
def driver_profile(make_driver):
    """A single active driver profile."""
    return make_driver(username="driver1", first_name="Dana", last_name="Rider")


@pytest.fixture
def driver_user(driver_profile) -> User:
    return driver_profile.user


@pytest.fixture
def make_vehicle(db):
    """Factory: create a Vehicle."""
    from apps.fleet.models import Vehicle

    counter = {"n": 0}

    def _make(bus_number: str | None = None, **kwargs):
        counter["n"] += 1
        if bus_number is None:
            bus_number = f"BUS-{counter['n']:03d}"
        return Vehicle.objects.create(bus_number=bus_number, **kwargs)

    return _make


@pytest.fixture
def vehicle(make_vehicle):
    return make_vehicle(bus_number="BUS-001", route_label="Campus Loop")


@pytest.fixture
def assignment(db, driver_profile, vehicle):
    """Active assignment linking the fixture driver to the fixture vehicle."""
    from apps.fleet.services import assign_driver_to_vehicle

    return assign_driver_to_vehicle(driver=driver_profile, vehicle=vehicle)


@pytest.fixture
def assigned_driver(driver_user, assignment) -> User:
    """A driver user who already holds an active vehicle assignment."""
    return driver_user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def add_point(db):
    """Factory: append a Location to a trip with full control over capture time.

    Bypasses the ingestion service so tests can create fixes at arbitrary
    (including stale/backdated) timestamps.
    """
    from apps.tracking.models import Location

    def _add(
        *,
        trip,
        captured_at=None,
        latitude=Decimal("23.777100"),
        longitude=Decimal("90.399400"),
        speed_kmh=None,
        accuracy_m=None,
    ) -> Location:
        return Location.objects.create(
            vehicle=trip.vehicle,
            driver=trip.driver,
            trip=trip,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            accuracy_m=accuracy_m,
            captured_at=captured_at or timezone.now(),
        )

    return _add


@pytest.fixture
def open_trip(db, vehicle, driver_profile):
    """An open trip for the fixture vehicle/driver."""
    from apps.tracking.models import Trip, TripStatus

    return Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=1),
        status=TripStatus.OPEN,
    )
