"""Accounts models.

The MVP uses Django's built-in ``User`` for authentication and attaches a
one-to-one ``DriverProfile`` for driver-specific attributes. There is no custom
user model, keeping authentication conventional and low-risk.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class DriverProfile(models.Model):
    """Driver-specific data attached to a Django ``User``."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Driver profile"
        verbose_name_plural = "Driver profiles"
        ordering = ["user__username"]

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        """Human-friendly name for dashboards (never exposes username/email)."""
        full = self.user.get_full_name().strip()
        return full or self.user.get_username()
