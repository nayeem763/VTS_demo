"""Reusable domain validators for tracking data.

These raise Django's ``ValidationError`` and are the authoritative server-side
checks, independent of any serializer. They mirror the database CheckConstraints
so bad data is rejected early with a clear message.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

LAT_MIN, LAT_MAX = Decimal("-90"), Decimal("90")
LON_MIN, LON_MAX = Decimal("-180"), Decimal("180")


def validate_coordinates(latitude: Decimal, longitude: Decimal) -> None:
    """Latitude in [-90, 90] and longitude in [-180, 180]."""
    if latitude is None or longitude is None:
        raise ValidationError("Latitude and longitude are required.")
    if not (LAT_MIN <= latitude <= LAT_MAX):
        raise ValidationError({"latitude": "Latitude must be between -90 and 90."})
    if not (LON_MIN <= longitude <= LON_MAX):
        raise ValidationError({"longitude": "Longitude must be between -180 and 180."})


def validate_speed(speed_kmh: Decimal | None) -> None:
    """Speed must be null or non-negative."""
    if speed_kmh is not None and speed_kmh < 0:
        raise ValidationError({"speed_kmh": "Speed must be zero or positive."})


def validate_accuracy(accuracy_m: Decimal | None) -> None:
    """Accuracy must be null or non-negative."""
    if accuracy_m is not None and accuracy_m < 0:
        raise ValidationError({"accuracy_m": "Accuracy must be zero or positive."})


def validate_capture_timestamp(captured_at: datetime, *, now: datetime | None = None) -> None:
    """Reject fixes from the far future (clock skew/spoofing) or the distant past."""
    if captured_at is None:
        raise ValidationError({"captured_at": "Capture time is required."})
    now = now or timezone.now()
    future_skew = timedelta(seconds=settings.LOCATION_MAX_FUTURE_SKEW_SECONDS)
    max_age = timedelta(seconds=settings.LOCATION_MAX_AGE_SECONDS)
    if captured_at > now + future_skew:
        raise ValidationError({"captured_at": "Capture time is too far in the future."})
    if captured_at < now - max_age:
        raise ValidationError({"captured_at": "Capture time is too old to accept."})
