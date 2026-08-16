"""Authentication flow tests: role-aware login, logout, trip closing."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.views import role_landing_url
from apps.tracking.models import Trip, TripStatus

pytestmark = pytest.mark.django_db


def test_role_landing_url_by_role(admin_user, driver_user):
    from django.contrib.auth.models import AnonymousUser

    assert str(role_landing_url(admin_user)) == reverse("web:admin_dashboard")
    assert str(role_landing_url(driver_user)) == reverse("web:tracker")
    assert str(role_landing_url(AnonymousUser())) == reverse("web:public_map")


def test_admin_login_page_renders(client):
    resp = client.get(reverse("accounts:admin_login"))
    assert resp.status_code == 200
    assert "accounts/admin_login.html" in [t.name for t in resp.templates]


def test_admin_login_redirects_to_dashboard(client, admin_user, password):
    resp = client.post(
        reverse("accounts:admin_login"),
        {"username": admin_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("web:admin_dashboard")


def test_driver_login_redirects_to_tracker(client, driver_user, password):
    resp = client.post(
        reverse("accounts:driver_login"),
        {"username": driver_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("web:tracker")


def test_login_respects_safe_next(client, admin_user, password):
    target = reverse("web:trip_history")
    resp = client.post(
        reverse("accounts:admin_login") + f"?next={target}",
        {"username": admin_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == target


def test_logout_requires_post(client, driver_user):
    client.force_login(driver_user)
    assert client.get(reverse("accounts:logout")).status_code == 405


def test_logout_closes_open_trip_and_redirects(client, driver_user, open_trip):
    client.force_login(driver_user)
    resp = client.post(reverse("accounts:logout"))
    assert resp.status_code == 302
    assert resp.url == reverse("web:public_map")

    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED
    assert open_trip.ended_at is not None


def test_logout_without_open_trip_is_safe(client, driver_user):
    client.force_login(driver_user)
    resp = client.post(reverse("accounts:logout"))
    assert resp.status_code == 302
    assert not Trip.objects.filter(status=TripStatus.OPEN).exists()
