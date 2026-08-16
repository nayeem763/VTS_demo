"""Presentation views. These render templates only; domain logic lives in the
accounts, fleet, and tracking apps. Each view exposes the minimum context the
page needs and defers all data fetching to the REST API via polling.
"""

from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.accounts.permissions import AdminRequiredMixin, DriverRequiredMixin
from apps.fleet.selectors import get_active_assignment_for_user, get_active_vehicles


class PublicMapView(TemplateView):
    """Public, read-only live map of active vehicles."""

    template_name = "public/vehicle_map.html"


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin live dashboard with a vehicle selector."""

    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        return context


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
