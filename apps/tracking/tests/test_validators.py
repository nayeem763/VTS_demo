"""Tracking validator tests (authoritative server-side domain checks)."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.tracking.validators import (
    validate_accuracy,
    validate_capture_timestamp,
    validate_coordinates,
    validate_speed,
)


def test_valid_coordinates_pass():
    validate_coordinates(Decimal("23.7771"), Decimal("90.3994"))


@pytest.mark.parametrize(
    "lat,lon",
    [
        (Decimal("91"), Decimal("0")),
        (Decimal("-91"), Decimal("0")),
        (Decimal("0"), Decimal("181")),
        (Decimal("0"), Decimal("-181")),
    ],
)
def test_out_of_range_coordinates_raise(lat, lon):
    with pytest.raises(ValidationError):
        validate_coordinates(lat, lon)


def test_missing_coordinates_raise():
    with pytest.raises(ValidationError):
        validate_coordinates(None, None)


def test_speed_validation():
    validate_speed(None)
    validate_speed(Decimal("0"))
    validate_speed(Decimal("42.5"))
    with pytest.raises(ValidationError):
        validate_speed(Decimal("-1"))


def test_accuracy_validation():
    validate_accuracy(None)
    validate_accuracy(Decimal("0"))
    with pytest.raises(ValidationError):
        validate_accuracy(Decimal("-0.5"))


def test_capture_timestamp_accepts_recent():
    now = timezone.now()
    validate_capture_timestamp(now, now=now)
    validate_capture_timestamp(now - timedelta(seconds=30), now=now)


def test_capture_timestamp_rejects_future_skew():
    now = timezone.now()
    with pytest.raises(ValidationError):
        validate_capture_timestamp(now + timedelta(minutes=10), now=now)


def test_capture_timestamp_rejects_too_old():
    now = timezone.now()
    with pytest.raises(ValidationError):
        validate_capture_timestamp(now - timedelta(hours=2), now=now)


def test_capture_timestamp_required():
    with pytest.raises(ValidationError):
        validate_capture_timestamp(None)
