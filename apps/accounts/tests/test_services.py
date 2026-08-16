"""Account service tests: driver creation and deactivation."""

from __future__ import annotations

import pytest
from django.conf import settings

from apps.accounts.models import DriverProfile
from apps.accounts.services import create_driver, deactivate_driver

pytestmark = pytest.mark.django_db


def test_create_driver_creates_user_group_and_profile():
    profile = create_driver(
        username="newdriver",
        password="pw-1234-strong",
        first_name="Sam",
        last_name="Road",
        employee_id="E-42",
        phone_number="+8801000000",
    )
    assert isinstance(profile, DriverProfile)
    assert profile.user.username == "newdriver"
    assert profile.user.groups.filter(name=settings.DRIVER_GROUP).exists()
    assert profile.employee_id == "E-42"
    assert profile.is_active is True
    assert profile.display_name == "Sam Road"


def test_create_driver_blank_employee_id_stored_as_null():
    profile = create_driver(username="noid", password="pw-1234-strong")
    assert profile.employee_id is None


def test_display_name_falls_back_to_username():
    profile = create_driver(username="justusername", password="pw-1234-strong")
    assert profile.display_name == "justusername"


def test_deactivate_driver_disables_profile_and_login():
    profile = create_driver(username="leaving", password="pw-1234-strong")
    deactivate_driver(profile)
    profile.refresh_from_db()
    profile.user.refresh_from_db()
    assert profile.is_active is False
    assert profile.user.is_active is False
