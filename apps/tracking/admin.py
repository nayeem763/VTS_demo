from __future__ import annotations

from django.contrib import admin

from .models import Location, Trip
from .services import close_trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "driver", "status", "started_at", "ended_at")
    list_filter = ("status", "vehicle")
    search_fields = ("vehicle__bus_number", "driver__user__username")
    date_hierarchy = "started_at"
    readonly_fields = ("created_at", "updated_at")
    actions = ("action_close",)

    @admin.action(description="Close selected open trips")
    def action_close(self, request, queryset) -> None:
        count = 0
        for trip in queryset:
            if trip.is_open:
                close_trip(trip, reason="admin_close")
                count += 1
        self.message_user(request, f"Closed {count} open trip(s).")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Locations are append-only; the admin is read-only to preserve integrity."""

    list_display = ("id", "vehicle", "trip", "latitude", "longitude", "speed_kmh", "captured_at")
    list_filter = ("vehicle",)
    search_fields = ("vehicle__bus_number",)
    date_hierarchy = "captured_at"
    readonly_fields = (
        "vehicle",
        "driver",
        "trip",
        "latitude",
        "longitude",
        "speed_kmh",
        "accuracy_m",
        "captured_at",
        "received_at",
        "client_event_id",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        # Only superusers may prune raw data; normal admins cannot.
        return bool(request.user and request.user.is_superuser)
