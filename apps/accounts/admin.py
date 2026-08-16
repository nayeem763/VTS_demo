from __future__ import annotations

from django.contrib import admin

from .models import DriverProfile


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "employee_id", "phone_number", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "employee_id")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Driver")
    def display_name(self, obj: DriverProfile) -> str:
        return obj.display_name
