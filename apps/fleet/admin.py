from __future__ import annotations

from django.contrib import admin
from django.utils import timezone

from .models import DriverAssignment, Vehicle
from .services import deactivate_vehicle, end_assignment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("bus_number", "registration_number", "route_label", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("bus_number", "registration_number", "route_label")
    readonly_fields = ("created_at", "updated_at")
    actions = ("action_deactivate",)

    @admin.action(description="Deactivate selected vehicles (ends active assignment)")
    def action_deactivate(self, request, queryset) -> None:
        for vehicle in queryset:
            deactivate_vehicle(vehicle)
        self.message_user(request, f"Deactivated {queryset.count()} vehicle(s).")


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("driver", "vehicle", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active",)
    search_fields = (
        "driver__user__username",
        "driver__user__first_name",
        "driver__user__last_name",
        "vehicle__bus_number",
    )
    autocomplete_fields = ("driver", "vehicle")
    readonly_fields = ("created_at",)
    actions = ("action_end",)

    def get_changeform_initial_data(self, request) -> dict:
        return {"starts_at": timezone.now()}

    @admin.action(description="End selected assignments")
    def action_end(self, request, queryset) -> None:
        for assignment in queryset:
            end_assignment(assignment)
        self.message_user(request, f"Ended {queryset.count()} assignment(s).")
