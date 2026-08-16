"""Seed a fresh database with demo users, vehicles, assignments and live trips.

Idempotent and safe to re-run: existing objects are reused, never duplicated.
Intended for first-run demos and local development — not for production data.

Examples::

    python manage.py create_demo_data
    python manage.py create_demo_data --drivers 4 --vehicles 6 --admin-password 's3cret...'

If ``--admin-password`` is omitted a strong random password is generated and
printed once. The command never prints an existing admin's password.
"""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.accounts.models import DriverProfile
from apps.accounts.services import create_driver
from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_assignment_for_vehicle
from apps.fleet.services import assign_driver_to_vehicle
from apps.tracking.models import Location, Trip, TripStatus

# Approximate campus centre (Chittagong University). Demo points scatter nearby.
BASE_LAT = Decimal("22.469500")
BASE_LON = Decimal("91.788400")

ROUTE_LABELS = [
    "Main Gate - Faculty",
    "Station - Campus",
    "Hostel Loop",
    "City Shuttle",
    "Medical - Science",
    "Library Express",
]


class Command(BaseCommand):
    help = "Create demo users, vehicles, assignments and sample live trips (idempotent)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--drivers", type=int, default=3, help="Number of driver accounts.")
        parser.add_argument("--vehicles", type=int, default=5, help="Number of vehicles.")
        parser.add_argument("--admin-username", default="admin", help="Admin username.")
        parser.add_argument(
            "--admin-password",
            default=None,
            help="Admin password. If omitted, a strong one is generated and printed.",
        )
        parser.add_argument(
            "--points",
            type=int,
            default=6,
            help="Recent location points to generate per assigned vehicle (0 to skip).",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        admin_group, _ = Group.objects.get_or_create(name=settings.ADMIN_GROUP)
        Group.objects.get_or_create(name=settings.DRIVER_GROUP)

        self._ensure_admin(options["admin_username"], options["admin_password"], admin_group)
        drivers = self._ensure_drivers(options["drivers"])
        vehicles = self._ensure_vehicles(options["vehicles"])
        self._ensure_assignments(drivers, vehicles)
        if options["points"] > 0:
            self._ensure_live_trips(options["points"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {len(drivers)} driver(s), {len(vehicles)} vehicle(s)."
            )
        )

    # -- admin ---------------------------------------------------------------
    def _ensure_admin(self, username: str, password: str | None, admin_group: Group) -> None:
        user = User.objects.filter(username=username).first()
        if user is not None:
            user.groups.add(admin_group)
            self.stdout.write(f"Admin {username!r}: already exists (password unchanged).")
            return

        password = password or get_random_string(16)
        user = User.objects.create_user(username=username, password=password, is_staff=True)
        user.groups.add(admin_group)
        self.stdout.write(self.style.WARNING(f"Admin created — username: {username}"))
        self.stdout.write(self.style.WARNING(f"Admin password (shown once): {password}"))

    # -- drivers -------------------------------------------------------------
    def _ensure_drivers(self, count: int) -> list[DriverProfile]:
        drivers: list[DriverProfile] = []
        for i in range(1, count + 1):
            username = f"driver{i}"
            existing = User.objects.filter(username=username).first()
            if existing is not None:
                profile = getattr(existing, "driver_profile", None)
                if profile is not None:
                    drivers.append(profile)
                continue
            profile = create_driver(
                username=username,
                password=get_random_string(12),
                first_name="Driver",
                last_name=str(i),
                employee_id=f"EMP-{i:03d}",
            )
            drivers.append(profile)
            self.stdout.write(f"Driver {username!r}: created.")
        return drivers

    # -- vehicles ------------------------------------------------------------
    def _ensure_vehicles(self, count: int) -> list[Vehicle]:
        vehicles: list[Vehicle] = []
        for i in range(1, count + 1):
            bus_number = f"CU-{i:02d}"
            vehicle, created = Vehicle.objects.get_or_create(
                bus_number=bus_number,
                defaults={"route_label": ROUTE_LABELS[(i - 1) % len(ROUTE_LABELS)]},
            )
            vehicles.append(vehicle)
            if created:
                self.stdout.write(f"Vehicle {bus_number!r}: created.")
        return vehicles

    # -- assignments ---------------------------------------------------------
    def _ensure_assignments(self, drivers: list[DriverProfile], vehicles: list[Vehicle]) -> None:
        for driver, vehicle in zip(drivers, vehicles, strict=False):
            if get_active_assignment_for_vehicle(vehicle) is not None:
                continue
            assign_driver_to_vehicle(driver=driver, vehicle=vehicle)
            self.stdout.write(f"Assigned {driver} -> {vehicle}.")

    # -- live trips ----------------------------------------------------------
    def _ensure_live_trips(self, points: int) -> None:
        now = timezone.now()
        for vehicle in Vehicle.objects.filter(is_active=True):
            assignment = get_active_assignment_for_vehicle(vehicle)
            if assignment is None:
                continue
            if Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).exists():
                continue

            started_at = now - timedelta(seconds=points * 20)
            trip = Trip.objects.create(
                vehicle=vehicle,
                driver=assignment.driver,
                started_at=started_at,
                status=TripStatus.OPEN,
            )
            for step in range(points):
                jitter_lat = Decimal(str(round(random.uniform(-0.01, 0.01), 6)))
                jitter_lon = Decimal(str(round(random.uniform(-0.01, 0.01), 6)))
                Location.objects.create(
                    vehicle=vehicle,
                    driver=assignment.driver,
                    trip=trip,
                    latitude=BASE_LAT + jitter_lat,
                    longitude=BASE_LON + jitter_lon,
                    speed_kmh=Decimal(str(round(random.uniform(0, 45), 2))),
                    accuracy_m=Decimal("8.00"),
                    captured_at=now - timedelta(seconds=(points - step - 1) * 20),
                )
            self.stdout.write(f"Live trip for {vehicle}: {points} point(s).")
