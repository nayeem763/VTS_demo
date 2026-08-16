"""Role-predicate and mixin authorisation tests."""

from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Group, User

from apps.accounts.permissions import is_admin, is_driver

pytestmark = pytest.mark.django_db


def test_anonymous_is_neither_admin_nor_driver():
    anon = AnonymousUser()
    assert is_admin(anon) is False
    assert is_driver(anon) is False


def test_admin_group_member_is_admin(admin_user):
    assert is_admin(admin_user) is True
    assert is_driver(admin_user) is False


def test_superuser_is_admin(superuser):
    assert is_admin(superuser) is True


def test_active_driver_is_driver(driver_user):
    assert is_driver(driver_user) is True
    assert is_admin(driver_user) is False


def test_inactive_driver_profile_is_not_driver(driver_profile):
    from apps.accounts.services import deactivate_driver

    deactivate_driver(driver_profile)
    driver_profile.user.refresh_from_db()
    assert is_driver(driver_profile.user) is False


def test_user_in_driver_group_without_profile_is_not_driver(driver_group):
    user = User.objects.create_user(username="ghost", password="x")
    user.groups.add(driver_group)
    assert is_driver(user) is False


def test_group_names_match_settings():
    assert Group.objects.filter(name=settings.ADMIN_GROUP).exists()
    assert Group.objects.filter(name=settings.DRIVER_GROUP).exists()
