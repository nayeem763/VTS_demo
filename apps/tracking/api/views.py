"""Versioned tracking API views under ``/api/v1/``.

- ``POST /locations/`` — a driver submits a GPS fix (idempotent).
- ``GET  /vehicles/latest-locations/`` — latest fix per active vehicle.
- ``GET  /vehicles/<id>/latest-location/`` — latest fix for one vehicle.
- ``GET  /trips/`` — trips for a vehicle/date (admin).
- ``GET  /trips/<id>/points/`` — trip points for polyline playback (admin).
"""

from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import is_admin
from apps.fleet.models import Vehicle

from ..selectors import (
    get_latest_active_vehicle_locations,
    get_latest_vehicle_location,
    get_trip_points,
    get_vehicle_trips,
)
from ..services import (
    NoActiveAssignment,
    VehicleInactive,
    record_vehicle_location,
)
from .permissions import IsAdminRole, IsDriverWithActiveAssignment
from .serializers import (
    AdminVehicleLocationSerializer,
    LocationCreatedSerializer,
    LocationIngestSerializer,
    PublicVehicleLocationSerializer,
    TripPointSerializer,
    TripSerializer,
    VehicleSnapshot,
)


def _location_serializer_for(request: Request):
    """Admins get the richer serializer; everyone else gets the public one."""
    return (
        AdminVehicleLocationSerializer
        if is_admin(request.user)
        else PublicVehicleLocationSerializer
    )


class LocationCreateView(APIView):
    """Accept a driver's GPS fix. Vehicle/driver/trip are derived server-side."""

    permission_classes = [IsDriverWithActiveAssignment]
    throttle_scope = "location_ingest"

    def post(self, request: Request) -> Response:
        serializer = LocationIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            location, created = record_vehicle_location(
                user=request.user,
                client_event_id=data["client_event_id"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                captured_at=data["captured_at"],
                speed_kmh=data.get("speed_kmh"),
                accuracy_m=data.get("accuracy_m"),
            )
        except NoActiveAssignment as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except VehicleInactive as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message_dict if hasattr(exc, "message_dict") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        body = LocationCreatedSerializer(location).data
        body["duplicate"] = not created
        return Response(
            body,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class LatestActiveVehicleLocationsView(APIView):
    """Latest location for every active vehicle. Public, role-aware output."""

    permission_classes = [AllowAny]
    throttle_scope = "public_read"

    def get(self, request: Request) -> Response:
        now = timezone.now()
        snapshots = [
            VehicleSnapshot(vehicle=vehicle, location=location, now=now)
            for vehicle, location in get_latest_active_vehicle_locations()
        ]
        serializer_cls = _location_serializer_for(request)
        data = serializer_cls(snapshots, many=True).data
        return Response({"count": len(data), "results": data})


class VehicleLatestLocationView(APIView):
    """Latest location for a single active vehicle. Public, role-aware output."""

    permission_classes = [AllowAny]
    throttle_scope = "public_read"

    def get(self, request: Request, vehicle_id: int) -> Response:
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id, is_active=True)
        snapshot = VehicleSnapshot(
            vehicle=vehicle,
            location=get_latest_vehicle_location(vehicle),
            now=timezone.now(),
        )
        serializer_cls = _location_serializer_for(request)
        return Response(serializer_cls(snapshot).data)


class TripListView(APIView):
    """List trips for a vehicle, optionally on a date. Admin only."""

    permission_classes = [IsAdminRole]

    def get(self, request: Request) -> Response:
        vehicle_id = request.query_params.get("vehicle_id")
        if not vehicle_id:
            return Response(
                {"detail": "vehicle_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

        on_date = None
        date_param = request.query_params.get("date")
        if date_param:
            on_date = parse_date(date_param)
            if on_date is None:
                return Response(
                    {"detail": "date must be YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        trips = get_vehicle_trips(vehicle=vehicle, on_date=on_date)
        data = TripSerializer(trips, many=True).data
        return Response({"count": len(data), "results": data})


class TripPointsView(APIView):
    """Return a trip's points (ascending) for polyline playback. Admin only."""

    permission_classes = [IsAdminRole]

    def get(self, request: Request, trip_id: int) -> Response:
        from ..models import Trip

        trip = get_object_or_404(Trip, pk=trip_id)

        # start/end are HH:MM times interpreted on the trip's local date.
        trip_local_date = timezone.localtime(trip.started_at).date()
        start_dt = self._time_on_date(request.query_params.get("start"), trip_local_date)
        end_dt = self._time_on_date(request.query_params.get("end"), trip_local_date)
        if request.query_params.get("start") and start_dt is None:
            return Response({"detail": "start must be HH:MM."}, status=400)
        if request.query_params.get("end") and end_dt is None:
            return Response({"detail": "end must be HH:MM."}, status=400)

        points = get_trip_points(trip=trip, start=start_dt, end=end_dt)
        data = TripPointSerializer(points, many=True).data
        return Response(
            {
                "trip_id": trip.id,
                "vehicle_id": trip.vehicle_id,
                "status": trip.status,
                "count": len(data),
                "points": data,
            }
        )

    @staticmethod
    def _time_on_date(raw: str | None, on_date):
        """Combine an HH:MM string with a date into an aware datetime, or None.

        Returns None for both missing and malformed input. ``parse_time`` may
        *raise* ValueError on a well-formed but out-of-range value (e.g.
        ``"99:99"``), so that is caught and treated as invalid rather than
        surfacing as a 500.
        """
        if not raw:
            return None
        try:
            parsed = parse_time(raw)
        except ValueError:
            return None
        if parsed is None:
            return None
        from datetime import datetime

        naive = datetime.combine(on_date, parsed)
        return timezone.make_aware(naive, timezone.get_current_timezone())
