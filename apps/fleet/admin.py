from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import path
from django.utils import timezone

from apps.tracking.reports import (
    REPORT_CATALOG,
    ReportType,
    build_fleet_record_pdf,
    fleet_record_filename,
)

from .models import BusRoute, DriverAssignment, RouteStop, Vehicle
from .services import deactivate_vehicle, end_assignment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "bus_number",
        "registration_number",
        "route_label",
        "admin_description",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("bus_number", "registration_number", "route_label", "admin_description")
    readonly_fields = ("created_at", "updated_at")
    actions = (
        "action_generate_fleet_record",
        "action_generate_trip_ledger",
        "action_generate_safety_audit",
        "action_generate_telemetry_trace",
        "action_deactivate",
    )
    change_list_template = "admin/fleet/vehicle/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-fleet-record/",
                self.admin_site.admin_view(self.generate_fleet_record_view),
                name="fleet_vehicle_generate_fleet_report",
            )
        ]
        return custom_urls + urls

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not self._can_export_location_data(request):
            for key in (
                "action_generate_fleet_record",
                "action_generate_trip_ledger",
                "action_generate_safety_audit",
                "action_generate_telemetry_trace",
            ):
                actions.pop(key, None)
        return actions

    def generate_fleet_record_view(self, request: HttpRequest) -> HttpResponse:
        """Download a fleet PDF directly from the Vehicle changelist."""
        allowed = self.has_view_or_change_permission(request)
        if not allowed or not self._can_export_location_data(request):
            raise PermissionDenied
        report_type = request.GET.get("report_type", "").strip() or ReportType.EXECUTIVE_SUMMARY
        if report_type not in REPORT_CATALOG:
            return HttpResponseBadRequest(
                "Unsupported report_type.", content_type="text/plain; charset=utf-8"
            )
        queryset = self.get_queryset(request)
        return self._pdf_response(
            queryset=queryset,
            generated_by=request.user.get_username(),
            report_type=report_type,
        )

    @admin.action(description="PDF: Executive Fleet Overview for selected vehicles")
    def action_generate_fleet_record(self, request, queryset) -> HttpResponse:
        """Download an executive fleet overview scoped to selected vehicles."""
        if not self._can_export_location_data(request):
            raise PermissionDenied
        return self._pdf_response(
            queryset=queryset,
            generated_by=request.user.get_username(),
            report_type=ReportType.EXECUTIVE_SUMMARY,
        )

    @admin.action(description="PDF: Trip Operations Ledger for selected vehicles")
    def action_generate_trip_ledger(self, request, queryset) -> HttpResponse:
        if not self._can_export_location_data(request):
            raise PermissionDenied
        return self._pdf_response(
            queryset=queryset,
            generated_by=request.user.get_username(),
            report_type=ReportType.TRIP_SUMMARY,
        )

    @admin.action(description="PDF: Speed & Safety Audit for selected vehicles")
    def action_generate_safety_audit(self, request, queryset) -> HttpResponse:
        if not self._can_export_location_data(request):
            raise PermissionDenied
        return self._pdf_response(
            queryset=queryset,
            generated_by=request.user.get_username(),
            report_type=ReportType.SAFETY_AUDIT,
        )

    @admin.action(description="PDF: Route Telemetry Trace (smart sampled) for selected vehicles")
    def action_generate_telemetry_trace(self, request, queryset) -> HttpResponse:
        if not self._can_export_location_data(request):
            raise PermissionDenied
        return self._pdf_response(
            queryset=queryset,
            generated_by=request.user.get_username(),
            report_type=ReportType.TELEMETRY_AUDIT,
        )

    def _pdf_response(
        self,
        *,
        queryset,
        generated_by: str,
        report_type: str = ReportType.EXECUTIVE_SUMMARY,
    ) -> HttpResponse:
        pdf = build_fleet_record_pdf(
            vehicles=queryset,
            generated_by=generated_by,
            report_type=report_type,
        )
        filename = fleet_record_filename(report_type=report_type)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = str(len(pdf))
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response

    @staticmethod
    def _can_export_location_data(request: HttpRequest) -> bool:
        # The report exposes private driver identities and precise coordinates.
        # Require the same model-level viewing capability as LocationAdmin.
        return bool(request.user and request.user.has_perm("tracking.view_location"))

    @admin.action(description="Deactivate selected vehicles (ends active assignment)")
    def action_deactivate(self, request, queryset) -> None:
        for vehicle in queryset:
            deactivate_vehicle(vehicle)
        self.message_user(request, f"Deactivated {queryset.count()} vehicle(s).")


class RouteStopInline(admin.TabularInline):
    """Maintain a route's ordered stops alongside its endpoints."""

    model = RouteStop
    extra = 1
    fields = ("sequence", "name", "longitude", "latitude")
    ordering = ("sequence",)


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ("name", "start_coordinates", "stop_count", "end_coordinates", "updated_at")
    search_fields = ("name", "stops__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = (RouteStopInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_stop_count=Count("stops"))

    @admin.display(description="Start")
    def start_coordinates(self, route: BusRoute) -> str:
        return f"{route.start_longitude}, {route.start_latitude}"

    @admin.display(description="Stops", ordering="_stop_count")
    def stop_count(self, route: BusRoute) -> int:
        return route._stop_count

    @admin.display(description="End")
    def end_coordinates(self, route: BusRoute) -> str:
        return f"{route.end_longitude}, {route.end_latitude}"


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
