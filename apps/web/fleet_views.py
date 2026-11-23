"""Admin Fleet Management views: vehicles, driver assignments, and drivers.

All routes require an authenticated Admin (``AdminRequiredMixin``), use
standard Django CSRF-protected POST actions with Post-Redirect-Get, and never
expose internal ``Vehicle.admin_description`` notes outside admin sessions.
"""

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.accounts.models import DriverProfile
from apps.accounts.permissions import AdminRequiredMixin
from apps.accounts.services import (
    activate_driver,
    create_driver,
    deactivate_driver,
    update_driver,
)
from apps.fleet.forms import (
    AssignDriverForm,
    DriverCreateForm,
    DriverEditForm,
    VehicleForm,
)
from apps.fleet.models import BusRoute, DriverAssignment, Vehicle
from apps.fleet.services import (
    activate_vehicle,
    assign_driver_to_vehicle,
    create_vehicle,
    deactivate_vehicle,
    delete_vehicle_if_unused,
    end_assignment,
    update_vehicle,
)

VALID_TABS = frozenset({"vehicles", "assignments", "drivers"})


def _fleet_redirect(tab: str = "vehicles") -> HttpResponse:
    target = reverse("web:fleet_manage")
    if tab in VALID_TABS and tab != "vehicles":
        return redirect(f"{target}?{urlencode({'tab': tab})}")
    return redirect(target)


def _format_form_errors(form) -> str:
    parts: list[str] = []
    for field, errors in form.errors.items():
        prefix = "" if field == "__all__" else f"{field.replace('_', ' ').capitalize()}: "
        for err in errors:
            parts.append(f"{prefix}{err}")
    return " ".join(parts) or "Please review the submitted fields."


@method_decorator(ensure_csrf_cookie, name="dispatch")
class FleetManagementView(AdminRequiredMixin, TemplateView):
    """Unified Fleet Operations & Assignment Management console."""

    template_name = "fleet/manage.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get("tab", "vehicles").strip()
        if active_tab not in VALID_TABS:
            active_tab = "vehicles"

        active_vehicle_assignments = Prefetch(
            "assignments",
            queryset=DriverAssignment.objects.filter(is_active=True).select_related("driver__user"),
            to_attr="active_assignments",
        )
        vehicles = list(
            Vehicle.objects.prefetch_related(active_vehicle_assignments)
            .annotate(
                trip_count=Count("trips", distinct=True),
                assignment_count=Count("assignments", distinct=True),
            )
            .order_by("-is_active", "bus_number")
        )
        for v in vehicles:
            v.current_assignment = v.active_assignments[0] if v.active_assignments else None
            v.can_delete = v.trip_count == 0 and v.assignment_count == 0

        active_driver_assignments = Prefetch(
            "assignments",
            queryset=DriverAssignment.objects.filter(is_active=True).select_related("vehicle"),
            to_attr="active_assignments",
        )
        drivers = list(
            DriverProfile.objects.select_related("user")
            .prefetch_related(active_driver_assignments)
            .annotate(trip_count=Count("trips", distinct=True))
            .order_by("-is_active", "user__first_name", "user__username")
        )
        for d in drivers:
            d.current_assignment = d.active_assignments[0] if d.active_assignments else None

        active_vehicles = [v for v in vehicles if v.is_active]
        active_drivers = [d for d in drivers if d.is_active]
        assigned_vehicles = [v for v in active_vehicles if v.current_assignment is not None]
        available_drivers = [d for d in active_drivers if d.current_assignment is None]

        active_assignments = list(
            DriverAssignment.objects.filter(is_active=True)
            .select_related("vehicle", "driver__user")
            .order_by("-starts_at")
        )
        recent_assignments = list(
            DriverAssignment.objects.select_related("vehicle", "driver__user")
            .order_by("-starts_at")[:35]
        )
        bus_routes = list(BusRoute.objects.order_by("name").values_list("name", flat=True))

        context.update(
            {
                "active_tab": active_tab,
                "vehicles": vehicles,
                "drivers": drivers,
                "active_vehicles": active_vehicles,
                "active_drivers": active_drivers,
                "active_assignments": active_assignments,
                "recent_assignments": recent_assignments,
                "bus_routes": bus_routes,
                "kpi": {
                    "total_vehicles": len(vehicles),
                    "active_vehicles": len(active_vehicles),
                    "assigned_vehicles": len(assigned_vehicles),
                    "unassigned_vehicles": len(active_vehicles) - len(assigned_vehicles),
                    "total_drivers": len(drivers),
                    "active_drivers": len(active_drivers),
                    "available_drivers": len(available_drivers),
                    "active_assignments": len(active_assignments),
                },
            }
        )
        return context


class VehicleCreateView(AdminRequiredMixin, View):
    """Create a new vehicle from the Fleet Management console."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = VehicleForm(request.POST)
        if not form.is_valid():
            messages.error(request, _format_form_errors(form))
            return _fleet_redirect("vehicles")

        vehicle = create_vehicle(
            bus_number=form.cleaned_data["bus_number"],
            registration_number=form.cleaned_data["registration_number"],
            route_label=form.cleaned_data["route_label"],
            admin_description=form.cleaned_data["admin_description"],
            is_active=bool(form.cleaned_data.get("is_active", True)),
        )
        messages.success(request, f"Added vehicle {vehicle.bus_number} to the fleet.")
        return _fleet_redirect("vehicles")


class VehicleEditView(AdminRequiredMixin, View):
    """Rename or update an existing vehicle and its admin-only description."""

    def post(self, request: HttpRequest, vehicle_id: int, *args, **kwargs) -> HttpResponse:
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        old_name = vehicle.bus_number
        form = VehicleForm(request.POST, instance=vehicle)
        if not form.is_valid():
            messages.error(request, _format_form_errors(form))
            return _fleet_redirect("vehicles")

        updated = update_vehicle(
            vehicle,
            bus_number=form.cleaned_data["bus_number"],
            registration_number=form.cleaned_data["registration_number"],
            route_label=form.cleaned_data["route_label"],
            admin_description=form.cleaned_data["admin_description"],
        )
        if old_name != updated.bus_number:
            messages.success(request, f"Renamed {old_name} to {updated.bus_number} and saved changes.")
        else:
            messages.success(request, f"Updated vehicle {updated.bus_number}.")
        return _fleet_redirect("vehicles")


class VehicleToggleActiveView(AdminRequiredMixin, View):
    """Activate or deactivate a vehicle (deactivating closes active assignment & trip)."""

    def post(self, request: HttpRequest, vehicle_id: int, *args, **kwargs) -> HttpResponse:
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        if vehicle.is_active:
            deactivate_vehicle(vehicle)
            messages.success(
                request,
                f"Deactivated {vehicle.bus_number} and ended any active driver assignment.",
            )
        else:
            activate_vehicle(vehicle)
            messages.success(request, f"Reactivated vehicle {vehicle.bus_number}.")
        return _fleet_redirect("vehicles")


class VehicleDeleteView(AdminRequiredMixin, View):
    """Delete a vehicle only if it has zero historical tracking or assignment records."""

    def post(self, request: HttpRequest, vehicle_id: int, *args, **kwargs) -> HttpResponse:
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        deleted, msg = delete_vehicle_if_unused(vehicle)
        if deleted:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)
        return _fleet_redirect("vehicles")


class DriverAssignView(AdminRequiredMixin, View):
    """Assign (or reassign) an active driver to an active vehicle."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return_tab = request.POST.get("return_tab", "vehicles").strip()
        form = AssignDriverForm(request.POST)
        if not form.is_valid():
            messages.error(request, _format_form_errors(form))
            return _fleet_redirect(return_tab)

        vehicle: Vehicle = form.cleaned_data["vehicle"]
        driver: DriverProfile = form.cleaned_data["driver"]
        try:
            assign_driver_to_vehicle(driver=driver, vehicle=vehicle)
        except ValueError as exc:
            messages.error(request, str(exc))
            return _fleet_redirect(return_tab)

        messages.success(request, f"Assigned {driver.display_name} to {vehicle.bus_number}.")
        return _fleet_redirect(return_tab)


class DriverDeassignView(AdminRequiredMixin, View):
    """Deassign an active driver-to-vehicle assignment and close any open trip."""

    def post(self, request: HttpRequest, assignment_id: int, *args, **kwargs) -> HttpResponse:
        return_tab = request.POST.get("return_tab", "vehicles").strip()
        assignment = get_object_or_404(
            DriverAssignment.objects.select_related("vehicle", "driver__user"),
            pk=assignment_id,
        )
        end_assignment(assignment)
        messages.success(
            request,
            f"Deassigned {assignment.driver.display_name} from {assignment.vehicle.bus_number}.",
        )
        return _fleet_redirect(return_tab)


class DriverCreateView(AdminRequiredMixin, View):
    """Create a new driver user account and DriverProfile."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = DriverCreateForm(request.POST)
        if not form.is_valid():
            messages.error(request, _format_form_errors(form))
            return _fleet_redirect("drivers")

        profile = create_driver(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            employee_id=form.cleaned_data["employee_id"] or None,
            phone_number=form.cleaned_data["phone_number"],
        )
        messages.success(
            request,
            f"Created driver account {profile.display_name} (@{profile.user.username}).",
        )
        return _fleet_redirect("drivers")


class DriverEditView(AdminRequiredMixin, View):
    """Update a driver's profile metadata and optional password reset."""

    def post(self, request: HttpRequest, driver_id: int, *args, **kwargs) -> HttpResponse:
        profile = get_object_or_404(DriverProfile.objects.select_related("user"), pk=driver_id)
        form = DriverEditForm(request.POST, instance=profile)
        if not form.is_valid():
            messages.error(request, _format_form_errors(form))
            return _fleet_redirect("drivers")

        update_driver(
            profile,
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            employee_id=form.cleaned_data["employee_id"] or None,
            phone_number=form.cleaned_data["phone_number"],
            new_password=form.cleaned_data["new_password"],
        )
        messages.success(request, f"Updated driver {profile.display_name}.")
        return _fleet_redirect("drivers")


class DriverToggleActiveView(AdminRequiredMixin, View):
    """Activate or deactivate a driver (deactivating closes active assignment & trip)."""

    def post(self, request: HttpRequest, driver_id: int, *args, **kwargs) -> HttpResponse:
        profile = get_object_or_404(DriverProfile.objects.select_related("user"), pk=driver_id)
        if profile.is_active:
            deactivate_driver(profile)
            messages.success(
                request,
                f"Deactivated driver {profile.display_name} and ended any active assignment.",
            )
        else:
            activate_driver(profile)
            messages.success(request, f"Reactivated driver {profile.display_name}.")
        return _fleet_redirect("drivers")
