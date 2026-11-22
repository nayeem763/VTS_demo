"""DRF serializers for the tracking API.

The privacy boundary lives here: :class:`PublicVehicleLocationSerializer`
never exposes driver contact details, usernames, emails, or internal
assignment identifiers. The admin serializer adds only a display name and
accuracy on top of the public fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from itertools import pairwise

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from apps.fleet.models import BusRoute, RouteStop, Vehicle

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
# Fixed bus routes (admin only)
# ---------------------------------------------------------------------------
class RouteStopSerializer(serializers.ModelSerializer):
    """An ordered intermediate point on a saved bus route."""

    class Meta:
        model = RouteStop
        fields = ["id", "sequence", "name", "longitude", "latitude"]
        read_only_fields = fields


class BusRouteSerializer(serializers.ModelSerializer):
    """A saved bus route and all of its intermediate stops."""

    stops = RouteStopSerializer(many=True, read_only=True)

    class Meta:
        model = BusRoute
        fields = [
            "id",
            "name",
            "start_longitude",
            "start_latitude",
            "stops",
            "end_longitude",
            "end_latitude",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RouteStopInputSerializer(serializers.Serializer):
    """Validate a stop supplied while creating a fixed route."""

    name = serializers.CharField(max_length=120, trim_whitespace=True)
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
    )
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
    )


class BusRouteCreateSerializer(serializers.Serializer):
    """Create a fixed route from an ordered source, stops, and destination."""

    name = serializers.CharField(max_length=120, trim_whitespace=True)
    start_longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
    )
    start_latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
    )
    stops = RouteStopInputSerializer(many=True, required=False, default=list, max_length=50)
    end_longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
    )
    end_latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
    )

    def validate_name(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("Route name is required.")
        if BusRoute.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A route with this name already exists.")
        return value

    def validate(self, attrs: dict) -> dict:
        """Reject duplicate adjacent waypoints before requesting road routing."""
        points = [
            (attrs["start_longitude"], attrs["start_latitude"]),
            *[(stop["longitude"], stop["latitude"]) for stop in attrs["stops"]],
            (attrs["end_longitude"], attrs["end_latitude"]),
        ]
        for previous, current in pairwise(points):
            if previous == current:
                raise serializers.ValidationError(
                    "Each stop must have different coordinates from the point before it."
                )
        return attrs

    def create(self, validated_data: dict) -> BusRoute:
        stops = validated_data.pop("stops", [])
        with transaction.atomic():
            route = BusRoute.objects.create(**validated_data)
            RouteStop.objects.bulk_create(
                [
                    RouteStop(route=route, sequence=index, **stop)
                    for index, stop in enumerate(stops, start=1)
                ]
            )
        return route


# ---------------------------------------------------------------------------
# Live locations (output)
# ---------------------------------------------------------------------------
@dataclass
class VehicleSnapshot:
    """A vehicle, its latest location, and that location's trip trace."""

    vehicle: Vehicle
    location: Location | None
    now: datetime
    # The view obtains this through the selector layer.  It is intentionally a
    # separate field instead of being read by the serializer, so serializers
    # remain pure representations of data that has already been selected.
    trajectory: list[Location] = field(default_factory=list)


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
            # Points are in capture order, from the first GPS fix in this
            # trip to the current one.  This lets the live map draw the real
            # recorded trace rather than a direct start-to-end line.
            "trajectory": [],
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
            data["trajectory"] = [
                {
                    "latitude": str(point.latitude),
                    "longitude": str(point.longitude),
                    "captured_at": point.captured_at.isoformat(),
                }
                for point in snapshot.trajectory
            ]
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
