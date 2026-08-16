"""Fleet models: vehicles and the driver-to-vehicle assignment history.

A separate ``DriverAssignment`` entity preserves assignment history, supports
reassignment, and keeps driver and vehicle lifecycles independent. Partial
unique constraints guarantee at most one *active* assignment per driver and
per vehicle at the database level.
"""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from apps.accounts.models import DriverProfile


class Vehicle(models.Model):
    """A university vehicle (bus) that can be tracked."""

    bus_number = models.CharField(max_length=32, unique=True)
    registration_number = models.CharField(max_length=64, unique=True, null=True, blank=True)
    # Descriptive metadata only. Dynamic route management is out of MVP scope.
    route_label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bus_number"]

    def __str__(self) -> str:
        return self.bus_number


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
