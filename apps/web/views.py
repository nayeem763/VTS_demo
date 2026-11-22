"""Presentation views and the authenticated fleet-report download.

Dashboard pages expose the minimum context they need and defer live-map data
to the REST API. The report download delegates PDF construction to tracking's
read-only reporting module.
"""

from __future__ import annotations

from datetime import date, datetime

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
    """Admin live dashboard with a vehicle selector."""

    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        context["routing_service_url"] = settings.ROUTING_SERVICE_URL
        return context


class FleetRecordReportView(AdminRequiredMixin, View):
    """Create and download an auditable fleet PDF for an authorised admin."""

    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Include inactive vehicles so historic records remain exportable.
        pdf = build_fleet_record_pdf(
            vehicles=Vehicle.objects.all(),
            generated_by=request.user.get_username(),
        )
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{fleet_record_filename()}"'
        response["Content-Length"] = str(len(pdf))
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response


class TripHistoryReportView(AdminRequiredMixin, View):
    """Download all vehicle histories plus a separate combined timeline."""

    def get(self, request, *args, **kwargs) -> HttpResponse:
        on_date, start, end, error = self._filters(request)
        if error:
            return HttpResponseBadRequest(error, content_type="text/plain; charset=utf-8")

        # Include inactive vehicles: their historic trips remain part of the
        # auditable record even after a vehicle leaves the active fleet.
        pdf = build_trip_history_pdf(
            vehicles=Vehicle.objects.all(),
            on_date=on_date,
            start=start,
            end=end,
            generated_by=request.user.get_username(),
        )
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{trip_history_filename()}"'
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
    """Admin trip-history playback page."""

    template_name = "trips/trip_history.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        return context
