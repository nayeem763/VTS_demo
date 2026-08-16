"""DRF serializers for the tracking API.

The privacy boundary lives here: :class:`PublicVehicleLocationSerializer`
never exposes driver contact details, usernames, emails, or internal
assignment identifiers. The admin serializer adds only a display name and
accuracy on top of the public fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from apps.fleet.models import Vehicle

from ..models import Location, Trip


# ---------------------------------------------------------------------------
# Ingestion (input)
# ---------------------------------------------------------------------------
class LocationIngestSerializer(serializers.Serializer):
    """Validates a single GPS submission. Driver/vehicle/trip are server-derived."""

    client_event_id = serializers.UUIDField()
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, min_value=Decimal("-90"), max_value=Decimal("90")
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, min_value=Decimal("-180"), max_value=Decimal("180")
    )
    speed_kmh = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, allow_null=True, min_value=Decimal("0")
    )
    accuracy_m = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False, allow_null=True, min_value=Decimal("0")
    )
    captured_at = serializers.DateTimeField()


class LocationCreatedSerializer(serializers.ModelSerializer):
    """Confirmation returned after a fix is accepted."""

    trip_id = serializers.IntegerField(source="trip.id", read_only=True)

    class Meta:
        model = Location
        fields = ["id", "trip_id", "captured_at", "received_at"]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Live locations (output)
# ---------------------------------------------------------------------------
@dataclass
class VehicleSnapshot:
    """A vehicle plus its latest location (which may be missing)."""

    vehicle: Vehicle
    location: Location | None
    now: datetime


class PublicVehicleLocationSerializer(serializers.Serializer):
    """Public-safe view of a vehicle's latest position. No driver identity."""

    def to_representation(self, snapshot: VehicleSnapshot) -> dict:
        vehicle = snapshot.vehicle
        loc = snapshot.location
        data: dict = {
            "vehicle_id": vehicle.id,
            "bus_number": vehicle.bus_number,
            "route_label": vehicle.route_label,
            "has_signal": loc is not None,
            "latitude": None,
            "longitude": None,
            "speed_kmh": None,
            "captured_at": None,
            "age_seconds": None,
            "is_stale": True,
        }
        if loc is not None:
            age = (snapshot.now - loc.captured_at).total_seconds()
            data.update(
                {
                    "latitude": str(loc.latitude),
                    "longitude": str(loc.longitude),
                    "speed_kmh": str(loc.speed_kmh) if loc.speed_kmh is not None else None,
                    "captured_at": loc.captured_at.isoformat(),
                    "age_seconds": int(age),
                    "is_stale": age > settings.LOCATION_STALE_SECONDS,
                }
            )
        return data


class AdminVehicleLocationSerializer(PublicVehicleLocationSerializer):
    """Admin view: adds driver display name and accuracy to the public fields."""

    def to_representation(self, snapshot: VehicleSnapshot) -> dict:
        data = super().to_representation(snapshot)
        loc = snapshot.location
        data["driver_name"] = loc.driver.display_name if loc is not None else None
        data["accuracy_m"] = (
            str(loc.accuracy_m) if loc is not None and loc.accuracy_m is not None else None
        )
        return data


# ---------------------------------------------------------------------------
# Trip history (output, admin only)
# ---------------------------------------------------------------------------
class TripSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source="vehicle.bus_number", read_only=True)
    driver_name = serializers.CharField(source="driver.display_name", read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "vehicle_id",
            "bus_number",
            "driver_name",
            "started_at",
            "ended_at",
            "status",
        ]
        read_only_fields = fields


class TripPointSerializer(serializers.ModelSerializer):
    """A single point for polyline playback."""

    class Meta:
        model = Location
        fields = ["latitude", "longitude", "speed_kmh", "captured_at"]
        read_only_fields = fields
