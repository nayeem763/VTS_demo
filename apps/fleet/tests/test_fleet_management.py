"""Fleet Management web workflow, service invariants, and privacy tests."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.models import DriverProfile
from apps.fleet.models import DriverAssignment, Vehicle
from apps.tracking.models import Trip, TripStatus

pytestmark = pytest.mark.django_db


def test_fleet_manage_access_control(client, admin_user, driver_user):
    url = reverse("web:fleet_manage")

    anon = client.get(url)
    assert anon.status_code == 302
    assert reverse("accounts:admin_login") in anon.url

    client.force_login(driver_user)
    assert client.get(url).status_code == 403
    assert client.post(reverse("web:fleet_vehicle_create"), {"bus_number": "CU-99"}).status_code == 403

    client.force_login(admin_user)
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"Fleet management" in resp.content


def test_admin_can_create_rename_edit_toggle_and_delete_vehicle(client, admin_user):
    client.force_login(admin_user)

    # Create vehicle with admin-only description
    resp = client.post(
        reverse("web:fleet_vehicle_create"),
        {
            "bus_number": "CU-10",
            "registration_number": "CTG-BA-1010",
            "route_label": "Campus Express",
            "admin_description": "AC 40-seater · Prefer senior driver",
            "is_active": "1",
        },
        follow=True,
    )
    assert resp.status_code == 200
    v = Vehicle.objects.get(bus_number="CU-10")
    assert v.registration_number == "CTG-BA-1010"
    assert v.route_label == "Campus Express"
    assert v.admin_description == "AC 40-seater · Prefer senior driver"
    assert v.is_active is True

    # Rename & update admin description
    resp = client.post(
        reverse("web:fleet_vehicle_edit", args=[v.pk]),
        {
            "bus_number": "CU-10A",
            "registration_number": "CTG-BA-1010",
            "route_label": "Science Express",
            "admin_description": "Renamed bus · Brake check complete",
        },
        follow=True,
    )
    assert resp.status_code == 200
    v.refresh_from_db()
    assert v.bus_number == "CU-10A"
    assert v.route_label == "Science Express"
    assert v.admin_description == "Renamed bus · Brake check complete"

    # Toggle inactive -> active
    client.post(reverse("web:fleet_vehicle_toggle", args=[v.pk]))
    v.refresh_from_db()
    assert v.is_active is False
    client.post(reverse("web:fleet_vehicle_toggle", args=[v.pk]))
    v.refresh_from_db()
    assert v.is_active is True

    # Delete unused vehicle succeeds
    client.post(reverse("web:fleet_vehicle_delete", args=[v.pk]))
    assert not Vehicle.objects.filter(pk=v.pk).exists()


def test_vehicle_with_trip_history_cannot_be_deleted(client, admin_user, vehicle, open_trip):
    client.force_login(admin_user)
    resp = client.post(reverse("web:fleet_vehicle_delete", args=[vehicle.pk]), follow=True)
    assert resp.status_code == 200
    assert Vehicle.objects.filter(pk=vehicle.pk).exists()


def test_admin_description_never_leaks_to_public_or_drivers(
    client, admin_user, assigned_driver, vehicle
):
    secret_note = "INTERNAL-ADMIN-ONLY-ENGINE-NOTE-774"
    vehicle.admin_description = secret_note
    vehicle.save(update_fields=["admin_description"])

    # Visible to admins in Fleet Management (table + assignment selector)
    client.force_login(admin_user)
    fleet_resp = client.get(reverse("web:fleet_manage"))
    assert fleet_resp.status_code == 200
    assert secret_note.encode() in fleet_resp.content

    # Hidden from public API & public map
    client.logout()
    api_resp = client.get(reverse("api:vehicle-latest-locations"))
    assert api_resp.status_code == 200
    assert secret_note.encode() not in api_resp.content
    assert b"admin_description" not in api_resp.content

    pub_resp = client.get(reverse("web:public_map"))
    assert pub_resp.status_code == 200
    assert secret_note.encode() not in pub_resp.content

    # Hidden from the assigned driver's own tracker page
    client.force_login(assigned_driver)
    tracker_resp = client.get(reverse("web:tracker"))
    assert tracker_resp.status_code == 200
    assert secret_note.encode() not in tracker_resp.content


def test_assign_reassign_and_deassign_close_open_trips(
    client, admin_user, make_vehicle, make_driver, assignment, open_trip, vehicle, driver_profile
):
    client.force_login(admin_user)
    bus_two = make_vehicle(bus_number="CU-22", route_label="Station Loop")
    driver_two = make_driver(username="driver_two", first_name="Rafiq", last_name="Islam")

    # Initial active assignment on vehicle + open_trip exists
    first_assignment = assignment

    # Reassigning vehicle to driver_two closes first_assignment AND closes open_trip
    resp = client.post(
        reverse("web:fleet_assign"),
        {"vehicle": str(vehicle.pk), "driver": str(driver_two.pk), "return_tab": "vehicles"},
        follow=True,
    )
    assert resp.status_code == 200
    first_assignment.refresh_from_db()
    open_trip.refresh_from_db()
    assert first_assignment.is_active is False
    assert first_assignment.ends_at is not None
    assert open_trip.status == TripStatus.COMPLETED
    assert open_trip.ended_at is not None

    new_assignment = DriverAssignment.objects.get(vehicle=vehicle, driver=driver_two, is_active=True)

    # Assign driver_two to bus_two switches them off vehicle cleanly
    client.post(
        reverse("web:fleet_assign"),
        {"vehicle": str(bus_two.pk), "driver": str(driver_two.pk), "return_tab": "assignments"},
    )
    new_assignment.refresh_from_db()
    assert new_assignment.is_active is False
    bus_two_assignment = DriverAssignment.objects.get(vehicle=bus_two, driver=driver_two, is_active=True)

    # Open a trip on bus_two, then deassign -> closes assignment AND open trip
    trip_two = Trip.objects.create(
        vehicle=bus_two,
        driver=driver_two,
        started_at=bus_two_assignment.starts_at,
        status=TripStatus.OPEN,
    )
    client.post(
        reverse("web:fleet_deassign", args=[bus_two_assignment.pk]),
        {"return_tab": "assignments"},
    )
    bus_two_assignment.refresh_from_db()
    trip_two.refresh_from_db()
    assert bus_two_assignment.is_active is False
    assert trip_two.status == TripStatus.COMPLETED


def test_admin_can_create_edit_and_toggle_driver(client, admin_user, vehicle):
    client.force_login(admin_user)

    resp = client.post(
        reverse("web:fleet_driver_create"),
        {
            "username": "newdriver99",
            "first_name": "Salim",
            "last_name": "Reza",
            "employee_id": "CU-DRV-99",
            "phone_number": "+8801711000099",
            "password": "StrongPass!992",
        },
        follow=True,
    )
    assert resp.status_code == 200
    profile = DriverProfile.objects.select_related("user").get(user__username="newdriver99")
    assert profile.display_name == "Salim Reza"
    assert profile.employee_id == "CU-DRV-99"
    assert profile.is_active is True

    # Edit driver details + assign to vehicle
    client.post(
        reverse("web:fleet_driver_edit", args=[profile.pk]),
        {
            "first_name": "Salim",
            "last_name": "Ahmed",
            "employee_id": "CU-DRV-99",
            "phone_number": "+8801811000099",
            "new_password": "",
        },
    )
    profile.refresh_from_db()
    assert profile.display_name == "Salim Ahmed"
    assert profile.phone_number == "+8801811000099"

    client.post(reverse("web:fleet_assign"), {"vehicle": str(vehicle.pk), "driver": str(profile.pk)})
    assert DriverAssignment.objects.filter(driver=profile, vehicle=vehicle, is_active=True).exists()

    # Deactivating driver ends their active assignment and disables login
    client.post(reverse("web:fleet_driver_toggle", args=[profile.pk]))
    profile.refresh_from_db()
    profile.user.refresh_from_db()
    assert profile.is_active is False
    assert profile.user.is_active is False
    assert not DriverAssignment.objects.filter(driver=profile, is_active=True).exists()

    # Reactivating restores login & profile
    client.post(reverse("web:fleet_driver_toggle", args=[profile.pk]))
    profile.refresh_from_db()
    profile.user.refresh_from_db()
    assert profile.is_active is True
    assert profile.user.is_active is True
