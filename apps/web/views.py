"""Presentation views and authenticated PDF report downloads.

Dashboard pages expose the minimum context they need and defer live-map data
to the REST API. Report downloads validate query parameters cleanly and
delegate PDF construction to tracking's read-only reporting module.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.accounts.permissions import AdminRequiredMixin, DriverRequiredMixin
from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_assignment_for_user, get_active_vehicles
from apps.tracking.reports import (
    DEFAULT_SAMPLE_INTERVAL_SECONDS,
    REPORT_CATALOG,
    REPORT_CHOICES,
    SAMPLING_INTERVAL_CHOICES,
    TRIP_REPORT_CHOICES,
    VALID_SAMPLE_INTERVALS,
    ReportType,
    build_fleet_record_pdf,
    build_trip_history_pdf,
    fleet_record_filename,
    trip_history_filename,
)


class PublicMapView(TemplateView):
    """Public, read-only live map of active vehicles."""

    template_name = "public/vehicle_map.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["routing_service_url"] = settings.ROUTING_SERVICE_URL
        return context


@method_decorator(ensure_csrf_cookie, name="dispatch")
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin live dashboard with a vehicle selector and PDF report builder."""

    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        context["all_vehicles"] = Vehicle.objects.all()
        context["routing_service_url"] = settings.ROUTING_SERVICE_URL
        context["report_choices"] = REPORT_CHOICES
        context["sampling_choices"] = SAMPLING_INTERVAL_CHOICES
        return context


class FleetRecordReportView(AdminRequiredMixin, View):
    """Create and download a tailored CU Transport Authority PDF report."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        params, error = self._parse_params(request)
        if error:
            return HttpResponseBadRequest(error, content_type="text/plain; charset=utf-8")

        pdf = build_fleet_record_pdf(
            vehicles=params["vehicles"],
            generated_by=request.user.get_username(),
            report_type=params["report_type"],
            date_from=params["date_from"],
            date_to=params["date_to"],
            sample_interval_seconds=params["interval"],
            vehicle_scope_label=params["vehicle_scope_label"],
        )
        filename = fleet_record_filename(report_type=params["report_type"])
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = str(len(pdf))
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response

    @staticmethod
    def _parse_params(request: HttpRequest) -> tuple[dict, str | None]:
        report_type = request.GET.get("report_type", "").strip() or ReportType.EXECUTIVE_SUMMARY
        if report_type not in REPORT_CATALOG:
            return {}, "Unsupported report_type."

        preset = request.GET.get("preset", "").strip() or "all"
        date_from_raw = request.GET.get("date_from", "").strip()
        date_to_raw = request.GET.get("date_to", "").strip()
        today = timezone.localdate()

        if preset == "today":
            date_from: date | None = today
            date_to: date | None = today
        elif preset == "7d":
            date_from = today - timedelta(days=6)
            date_to = today
        elif preset == "30d":
            date_from = today - timedelta(days=29)
            date_to = today
        elif preset in ("all", "custom"):
            date_from = parse_date(date_from_raw) if date_from_raw else None
            date_to = parse_date(date_to_raw) if date_to_raw else None
            if date_from_raw and date_from is None:
                return {}, "date_from must be YYYY-MM-DD."
            if date_to_raw and date_to is None:
                return {}, "date_to must be YYYY-MM-DD."
            if date_from is not None and date_to is not None and date_from > date_to:
                return {}, "date_from must not be later than date_to."
        else:
            return {}, "Unsupported date preset."

        vehicle_scope = request.GET.get("vehicle_scope", "").strip() or "all"
        vehicle_raw = request.GET.get("vehicle", "").strip()
        if vehicle_raw:
            try:
                vehicle_pk = int(vehicle_raw)
            except ValueError:
                return {}, "vehicle must be an integer ID."
            vehicles = list(Vehicle.objects.filter(pk=vehicle_pk))
            if not vehicles:
                return {}, "Selected vehicle was not found."
            vehicle_scope_label = f"Single vehicle ({vehicles[0].bus_number})"
        elif vehicle_scope == "active":
            vehicles = list(Vehicle.objects.filter(is_active=True))
            vehicle_scope_label = "Active fleet only"
        elif vehicle_scope in ("all", "single"):
            vehicles = list(Vehicle.objects.all())
            vehicle_scope_label = "Entire fleet (active & historic vehicles)"
        else:
            return {}, "Unsupported vehicle_scope."

        interval_raw = request.GET.get("interval", "").strip()
        if interval_raw:
            try:
                interval = int(interval_raw)
            except ValueError:
                return {}, "interval must be an integer."
            if interval not in VALID_SAMPLE_INTERVALS:
                return {}, "Unsupported sampling interval."
        else:
            interval = DEFAULT_SAMPLE_INTERVAL_SECONDS

        return (
            {
                "report_type": report_type,
                "date_from": date_from,
                "date_to": date_to,
                "vehicles": vehicles,
                "vehicle_scope_label": vehicle_scope_label,
                "interval": interval,
            },
            None,
        )


class TripHistoryReportView(AdminRequiredMixin, View):
    """Download structured trip ledgers or sampled traces for a date/time window."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        on_date, start, end, error = self._filters(request)
        if error:
            return HttpResponseBadRequest(error, content_type="text/plain; charset=utf-8")

        report_type = request.GET.get("report_type", "").strip() or ReportType.TRIP_SUMMARY
        if report_type not in REPORT_CATALOG:
            return HttpResponseBadRequest(
                "Unsupported report_type.", content_type="text/plain; charset=utf-8"
            )

        interval_raw = request.GET.get("interval", "").strip()
        if interval_raw:
            try:
                interval = int(interval_raw)
            except ValueError:
                return HttpResponseBadRequest(
                    "interval must be an integer.", content_type="text/plain; charset=utf-8"
                )
            if interval not in VALID_SAMPLE_INTERVALS:
                return HttpResponseBadRequest(
                    "Unsupported sampling interval.", content_type="text/plain; charset=utf-8"
                )
        else:
            interval = DEFAULT_SAMPLE_INTERVAL_SECONDS

        vehicle_raw = request.GET.get("vehicle", "").strip()
        if vehicle_raw:
            try:
                vehicle_pk = int(vehicle_raw)
            except ValueError:
                return HttpResponseBadRequest(
                    "vehicle must be an integer ID.", content_type="text/plain; charset=utf-8"
                )
            vehicles = list(Vehicle.objects.filter(pk=vehicle_pk))
            if not vehicles:
                return HttpResponseBadRequest(
                    "Selected vehicle was not found.", content_type="text/plain; charset=utf-8"
                )
        else:
            # Include inactive vehicles: their historic trips remain part of the
            # auditable record even after a vehicle leaves the active fleet.
            vehicles = list(Vehicle.objects.all())

        pdf = build_trip_history_pdf(
            vehicles=vehicles,
            on_date=on_date,
            start=start,
            end=end,
            generated_by=request.user.get_username(),
            report_type=report_type,
            sample_interval_seconds=interval,
        )
        filename = trip_history_filename(report_type=report_type)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = str(len(pdf))
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response

    @staticmethod
    def _filters(
        request: HttpRequest,
    ) -> tuple[date | None, datetime | None, datetime | None, str | None]:
        """Validate the date/time controls shared with the trip-history page."""
        date_value = request.GET.get("date", "")
        start_value = request.GET.get("start", "")
        end_value = request.GET.get("end", "")
        on_date = parse_date(date_value) if date_value else None
        if date_value and on_date is None:
            return None, None, None, "date must be YYYY-MM-DD."
        if (start_value or end_value) and on_date is None:
            return None, None, None, "start and end require a date."

        start = TripHistoryReportView._time_on_date(start_value, on_date)
        end = TripHistoryReportView._time_on_date(end_value, on_date)
        if start_value and start is None:
            return None, None, None, "start must be HH:MM."
        if end_value and end is None:
            return None, None, None, "end must be HH:MM."
        if start is not None and end is not None and start > end:
            return None, None, None, "start must not be later than end."
        return on_date, start, end, None

    @staticmethod
    def _time_on_date(raw: str, on_date: date | None) -> datetime | None:
        if not raw:
            return None
        try:
            parsed = parse_time(raw)
        except ValueError:
            return None
        if parsed is None or on_date is None:
            return None
        return timezone.make_aware(
            datetime.combine(on_date, parsed), timezone.get_current_timezone()
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class TrackerView(DriverRequiredMixin, TemplateView):
    """Driver tracker page. Sets the CSRF cookie so fetch() can post fixes."""

    template_name = "tracker/tracker.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        assignment = get_active_assignment_for_user(self.request.user)
        context["assignment"] = assignment
        context["assigned_vehicle"] = assignment.vehicle if assignment else None
        return context


class TripHistoryView(AdminRequiredMixin, TemplateView):
    """Admin trip-history playback page with configurable PDF export."""

    template_name = "trips/trip_history.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        context["all_vehicles"] = Vehicle.objects.all()
        context["trip_report_choices"] = TRIP_REPORT_CHOICES
        context["sampling_choices"] = SAMPLING_INTERVAL_CHOICES
        return context
