"""Tracking models: Trips and append-only Location history.

A ``Trip`` groups the ``Location`` points recorded between a vehicle starting
and stopping movement for a session. Locations are append-only: they are never
edited after insertion, which keeps trip-history playback trustworthy.

Database-level constraints enforce the domain rules (valid coordinates,
non-negative speed/accuracy, one open trip per vehicle, unique client events)
so invalid data cannot be persisted even if application code has a bug.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.db.models import Q

from apps.accounts.models import DriverProfile
from apps.fleet.models import Vehicle


class TripStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    COMPLETED = "COMPLETED", "Completed"


class Trip(models.Model):
    """A single tracking session for a vehicle."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="trips")
    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="trips")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=TripStatus.choices, default=TripStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(status="OPEN"),
                name="uniq_open_trip_per_vehicle",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "-started_at"], name="idx_trip_vehicle_started"),
            models.Index(fields=["vehicle", "status"], name="idx_trip_vehicle_status"),
        ]

    def __str__(self) -> str:
        return f"Trip #{self.pk} {self.vehicle} ({self.status})"

    @property
    def is_open(self) -> bool:
        return self.status == TripStatus.OPEN


class Location(models.Model):
    """A single GPS fix. Append-only."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="locations")
    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="locations")
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="locations")

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    accuracy_m = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    captured_at = models.DateTimeField()  # device capture time
    received_at = models.DateTimeField(auto_now_add=True)  # server receipt time
    # Idempotency key so a retried submission does not create duplicate points.
    client_event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-captured_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__gte=-90) & Q(latitude__lte=90),
                name="chk_latitude_range",
            ),
            models.CheckConstraint(
                condition=Q(longitude__gte=-180) & Q(longitude__lte=180),
                name="chk_longitude_range",
            ),
            models.CheckConstraint(
                condition=Q(speed_kmh__isnull=True) | Q(speed_kmh__gte=0),
                name="chk_speed_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(accuracy_m__isnull=True) | Q(accuracy_m__gte=0),
                name="chk_accuracy_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "-captured_at"], name="idx_loc_vehicle_captured"),
            models.Index(fields=["trip", "captured_at"], name="idx_loc_trip_captured"),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle} @ ({self.latitude}, {self.longitude}) {self.captured_at:%H:%M:%S}"
