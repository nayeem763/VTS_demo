"""Fleet models: vehicles and the driver-to-vehicle assignment history.

A separate ``DriverAssignment`` entity preserves assignment history, supports
reassignment, and keeps driver and vehicle lifecycles independent. Partial
unique constraints guarantee at most one *active* assignment per driver and
per vehicle at the database level.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.accounts.models import DriverProfile


class Vehicle(models.Model):
    """A university vehicle (bus) that can be tracked."""

    bus_number = models.CharField(max_length=32, unique=True)
    registration_number = models.CharField(max_length=64, unique=True, null=True, blank=True)
    # Descriptive metadata shown to riders and admins on the live map.
    route_label = models.CharField(max_length=120, blank=True)
    # Internal short note visible ONLY to admins (e.g., when assigning drivers).
    # Never exposed in public API responses, public maps, or driver views.
    admin_description = models.CharField(max_length=280, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bus_number"]

    def __str__(self) -> str:
        return self.bus_number


class BusRoute(models.Model):
    """A fixed bus route, from its first stop to its final stop.

    The route's road geometry is calculated by the map's routing provider from
    these fixed waypoints.  Keeping the endpoints and intermediate stops in
    our database makes the bus service configuration durable and auditable,
    while avoiding a dependency on a provider-specific geometry format.
    """

    name = models.CharField(max_length=120, unique=True)
    start_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
    )
    start_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
    )
    end_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
    )
    end_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RouteStop(models.Model):
    """One ordered intermediate stop on a :class:`BusRoute`."""

    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name="stops")
    sequence = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=120)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
    )

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["route", "sequence"],
                name="uniq_route_stop_sequence",
            )
        ]

    def __str__(self) -> str:
        return f"{self.route}: {self.sequence}. {self.name}"


class DriverAssignment(models.Model):
    """Links a driver to a vehicle for a period of time."""

    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="assignments")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="assignments")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["driver"],
                condition=Q(is_active=True),
                name="uniq_active_assignment_per_driver",
            ),
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(is_active=True),
                name="uniq_active_assignment_per_vehicle",
            ),
        ]
        indexes = [
            models.Index(fields=["driver", "is_active"], name="idx_assign_driver_active"),
            models.Index(fields=["vehicle", "is_active"], name="idx_assign_vehicle_active"),
        ]

    def __str__(self) -> str:
        state = "active" if self.is_active else "ended"
        return f"{self.driver} -> {self.vehicle} ({state})"
