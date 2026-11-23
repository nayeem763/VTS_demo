"""Unit and validation tests for Fleet Management Django forms."""

from __future__ import annotations

import pytest

from apps.fleet.forms import (
    AssignDriverForm,
    DriverCreateForm,
    DriverEditForm,
    VehicleForm,
)

pytestmark = pytest.mark.django_db

# ---------------------------------------------------------------------------
# 1. VehicleForm validation (40 tests)
# ---------------------------------------------------------------------------
VALID_VEHICLE_PAYLOADS = [
    {"bus_number": "CU-01", "registration_number": "", "route_label": "", "admin_description": ""},
    {"bus_number": "  CU-02  ", "registration_number": " CTG-102 ", "route_label": " Main ", "admin_description": " Note "},
    {"bus_number": "BUS-99", "registration_number": "DHA-KA-11-9999", "route_label": "Station - Campus", "admin_description": "AC minibus"},
    {"bus_number": "A" * 32, "registration_number": "R" * 64, "route_label": "L" * 120, "admin_description": "D" * 280},
    {"bus_number": "Faculty-1", "registration_number": "", "route_label": "Zero Point", "admin_description": "Senior driver only"},
    {"bus_number": "Shuttle_01", "registration_number": "REG-01", "route_label": "Hall Loop", "admin_description": "42 seats · new tyres"},
    {"bus_number": "CU-03A", "registration_number": "REG-03A", "route_label": "Science", "admin_description": "Inspect brakes Friday"},
    {"bus_number": "CU-04B", "registration_number": "", "route_label": "Arts", "admin_description": "VIP reserve"},
    {"bus_number": "EV-01", "registration_number": "EV-2026", "route_label": "Green Campus", "admin_description": "Electric shuttle"},
    {"bus_number": "MINIBUS-7", "registration_number": "MB-07", "route_label": "Medical", "admin_description": "Wheelchair ramp"},
    {"bus_number": "CU-100", "registration_number": "", "route_label": "", "admin_description": "100% tested <tag> & quote"},
    {"bus_number": "CU-101", "registration_number": "REG-101", "route_label": "Gate 2 -> Wasa", "admin_description": "Peak hour only"},
    {"bus_number": "CU-102", "registration_number": "REG-102", "route_label": "Muradpur", "admin_description": ""},
    {"bus_number": "CU-103", "registration_number": "REG-103", "route_label": "GEC", "admin_description": "AC compressor repaired"},
    {"bus_number": "CU-104", "registration_number": "REG-104", "route_label": "New Market", "admin_description": "52-seater Hino"},
    {"bus_number": "CU-105", "registration_number": "", "route_label": "Oxygen", "admin_description": "Morning shift"},
    {"bus_number": "CU-106", "registration_number": "", "route_label": "Agrabad", "admin_description": "Afternoon shift"},
    {"bus_number": "CU-107", "registration_number": "REG-107", "route_label": "Chawkbazar", "admin_description": "GPS box mounted front"},
    {"bus_number": "CU-108", "registration_number": "REG-108", "route_label": "Bahaddarhat", "admin_description": "Backup bus"},
    {"bus_number": "CU-109", "registration_number": "REG-109", "route_label": "Hathazari", "admin_description": "Long route"},
]


@pytest.mark.parametrize("payload", VALID_VEHICLE_PAYLOADS)
def test_vehicle_form_valid_payloads(payload):
    form = VehicleForm(payload)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["bus_number"] == payload["bus_number"].strip()
    assert len(form.cleaned_data["admin_description"]) <= 280


INVALID_VEHICLE_PAYLOADS = [
    {"bus_number": ""},
    {"bus_number": "    "},
    {"bus_number": "\t\n"},
    {"bus_number": "A" * 33},
    {"bus_number": "A" * 50},
    {"bus_number": "CU-1", "registration_number": "R" * 65},
    {"bus_number": "CU-1", "route_label": "L" * 121},
    {"bus_number": "CU-1", "admin_description": "D" * 281},
    {"bus_number": "CU-1", "admin_description": "D" * 400},
    {"bus_number": "CU-1", "registration_number": "R" * 100, "admin_description": "D" * 300},
    {},
    {"route_label": "No bus number"},
]


@pytest.mark.parametrize("payload", INVALID_VEHICLE_PAYLOADS)
def test_vehicle_form_invalid_payloads(payload):
    form = VehicleForm(payload)
    assert not form.is_valid()


@pytest.mark.parametrize("dup_name", ["BUS-001", "bus-001", "Bus-001", "  BUS-001  "])
def test_vehicle_form_rejects_duplicate_bus_number_case_insensitive(vehicle, dup_name):
    form = VehicleForm({"bus_number": dup_name})
    assert not form.is_valid()
    assert "bus_number" in form.errors


def test_vehicle_form_allows_keeping_own_bus_number_on_edit(vehicle):
    form = VehicleForm(
        {"bus_number": vehicle.bus_number, "admin_description": "Updated note"},
        instance=vehicle,
    )
    assert form.is_valid(), form.errors


def test_vehicle_form_rejects_duplicate_registration_on_create(make_vehicle):
    make_vehicle(bus_number="CU-50", registration_number="CTG-5050")
    form = VehicleForm({"bus_number": "CU-51", "registration_number": "ctg-5050"})
    assert not form.is_valid()
    assert "registration_number" in form.errors


def test_vehicle_form_allows_own_registration_on_edit(make_vehicle):
    v = make_vehicle(bus_number="CU-52", registration_number="CTG-5252")
    form = VehicleForm(
        {"bus_number": "CU-52X", "registration_number": "CTG-5252"},
        instance=v,
    )
    assert form.is_valid(), form.errors


def test_vehicle_form_multiple_blank_registrations_allowed(make_vehicle):
    make_vehicle(bus_number="CU-53", registration_number=None)
    form = VehicleForm({"bus_number": "CU-54", "registration_number": "   "})
    assert form.is_valid(), form.errors
    assert form.cleaned_data["registration_number"] == ""


# ---------------------------------------------------------------------------
# 2. DriverCreateForm & DriverEditForm validation (45 tests)
# ---------------------------------------------------------------------------
VALID_DRIVER_CREATES = [
    ("drv_a1", "Karim", "Uddin", "EMP-101", "+8801711000101", "SecurePass!101"),
    ("drv_a2", "Rafiq", "", "EMP-102", "", "SecurePass!102"),
    ("drv_a3", "", "Islam", "", "01811000103", "SecurePass!103"),
    ("drv_a4", "", "", "", "", "SecurePass!104"),
    ("  drv_a5  ", "  Salim  ", "  Reza  ", "  EMP-105  ", "  +88019  ", "SecurePass!105"),
    ("drv.six", "Tariq", "Hasan", "CU-DRV-06", "+8801511000006", "ValidLongPass#6"),
    ("drv-seven", "Kamal", "Hossain", "CU-DRV-07", "+8801611000007", "ValidLongPass#7"),
    ("drv_08", "Jamal", "Mia", "CU-DRV-08", "+8801711000008", "ValidLongPass#8"),
    ("drv_09", "Nizam", "Uddin", "", "", "ValidLongPass#9"),
    ("drv_10", "Belal", "Ahmed", "CU-DRV-10", "01712345678", "ValidLongPass#10"),
    ("drv_11", "Harun", "Rashid", "CU-DRV-11", "01712345679", "ValidLongPass#11"),
    ("drv_12", "Mizan", "Rahman", "CU-DRV-12", "01712345680", "ValidLongPass#12"),
    ("drv_13", "Shafiq", "Alam", "CU-DRV-13", "01712345681", "ValidLongPass#13"),
    ("drv_14", "Anwar", "Ali", "CU-DRV-14", "01712345682", "ValidLongPass#14"),
    ("drv_15", "Faruk", "Khan", "CU-DRV-15", "01712345683", "ValidLongPass#15"),
]


@pytest.mark.parametrize(
    ("username", "first", "last", "emp_id", "phone", "password"), VALID_DRIVER_CREATES
)
def test_driver_create_form_valid(username, first, last, emp_id, phone, password):
    form = DriverCreateForm(
        {
            "username": username,
            "first_name": first,
            "last_name": last,
            "employee_id": emp_id,
            "phone_number": phone,
            "password": password,
        }
    )
    assert form.is_valid(), form.errors


INVALID_DRIVER_CREATES = [
    {"username": "", "password": "SecurePass!201"},
    {"username": "   ", "password": "SecurePass!202"},
    {"username": "drv_bad1", "password": ""},
    {"username": "drv_bad2", "password": "short"},
    {"username": "drv_bad3", "password": "1234567"},
    {"username": "drv_bad4", "password": "12345678"},
    {"username": "drv_bad5", "password": "password"},
    {"username": "drv_bad6", "password": "password123"},
    {"username": "drv_bad7", "password": "qwertyui"},
    {"username": "drv_bad8", "password": "11111111"},
    {"username": "u" * 151, "password": "SecurePass!211"},
    {"username": "drv_bad9", "employee_id": "E" * 51, "password": "SecurePass!212"},
    {"username": "drv_bad10", "phone_number": "9" * 33, "password": "SecurePass!213"},
    {"username": "drv_bad11", "first_name": "F" * 151, "password": "SecurePass!214"},
    {"username": "drv_bad12", "last_name": "L" * 151, "password": "SecurePass!215"},
]


@pytest.mark.parametrize("payload", INVALID_DRIVER_CREATES)
def test_driver_create_form_invalid(payload):
    form = DriverCreateForm(payload)
    assert not form.is_valid()


@pytest.mark.parametrize("dup_user", ["driver1", "DRIVER1", "Driver1", "  driver1 "])
def test_driver_create_form_rejects_duplicate_username(driver_profile, dup_user):
    form = DriverCreateForm({"username": dup_user, "password": "StrongPass!901"})
    assert not form.is_valid()
    assert "username" in form.errors


@pytest.mark.parametrize("dup_emp", ["EMP-001", "emp-001", "  EMP-001  "])
def test_driver_create_form_rejects_duplicate_employee_id(driver_profile, dup_emp):
    driver_profile.employee_id = "EMP-001"
    driver_profile.save(update_fields=["employee_id"])
    form = DriverCreateForm(
        {"username": "unique_drv", "employee_id": dup_emp, "password": "StrongPass!902"}
    )
    assert not form.is_valid()
    assert "employee_id" in form.errors


DRIVER_EDIT_CASES = [
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "EMP-1", "phone_number": "01700", "new_password": ""}, True),
    ({"first_name": "Dana", "last_name": "Updated", "employee_id": "", "phone_number": "", "new_password": ""}, True),
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "EMP-2", "phone_number": "+8801711", "new_password": "BrandNewPass!88"}, True),
    ({"first_name": "", "last_name": "", "employee_id": "", "phone_number": "", "new_password": ""}, True),
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "EMP-1", "phone_number": "", "new_password": "123"}, False),
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "EMP-1", "phone_number": "", "new_password": "password"}, False),
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "E" * 51, "phone_number": "", "new_password": ""}, False),
    ({"first_name": "Dana", "last_name": "Rider", "employee_id": "EMP-1", "phone_number": "P" * 33, "new_password": ""}, False),
]


@pytest.mark.parametrize(("payload", "is_valid"), DRIVER_EDIT_CASES)
def test_driver_edit_form_cases(driver_profile, payload, is_valid):
    form = DriverEditForm(payload, instance=driver_profile)
    assert form.is_valid() is is_valid


# ---------------------------------------------------------------------------
# 3. AssignDriverForm validation (35 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("idx", range(15))
def test_assign_driver_form_accepts_active_pairs(make_vehicle, make_driver, idx):
    v = make_vehicle(bus_number=f"AF-{idx:02d}")
    d = make_driver(username=f"af_drv_{idx:02d}")
    form = AssignDriverForm({"vehicle": str(v.pk), "driver": str(d.pk)})
    assert form.is_valid(), form.errors
    assert form.cleaned_data["vehicle"] == v
    assert form.cleaned_data["driver"] == d


@pytest.mark.parametrize("idx", range(10))
def test_assign_driver_form_rejects_inactive_vehicle(make_vehicle, driver_profile, idx):
    v = make_vehicle(bus_number=f"INACT-V-{idx}", is_active=False)
    form = AssignDriverForm({"vehicle": str(v.pk), "driver": str(driver_profile.pk)})
    assert not form.is_valid()
    assert "vehicle" in form.errors


@pytest.mark.parametrize("idx", range(5))
def test_assign_driver_form_rejects_inactive_driver(vehicle, make_driver, idx):
    d = make_driver(username=f"inact_d_{idx}")
    d.is_active = False
    d.save(update_fields=["is_active"])
    form = AssignDriverForm({"vehicle": str(vehicle.pk), "driver": str(d.pk)})
    assert not form.is_valid()
    assert "driver" in form.errors


INVALID_ASSIGN_RAW = [
    {},
    {"vehicle": "", "driver": ""},
    {"vehicle": "999999", "driver": "999999"},
    {"vehicle": "abc", "driver": "def"},
    {"vehicle": "-1", "driver": "0"},
]


@pytest.mark.parametrize("payload", INVALID_ASSIGN_RAW)
def test_assign_driver_form_rejects_malformed_ids(payload):
    form = AssignDriverForm(payload)
    assert not form.is_valid()
