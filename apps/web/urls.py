"""Web (server-rendered) page routes. Auth routes are included from accounts."""

from __future__ import annotations

from django.urls import path

from . import fleet_views, views

app_name = "web"

urlpatterns = [
    path("", views.PublicMapView.as_view(), name="public_map"),
    path("dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path(
        "dashboard/fleet-record.pdf", views.FleetRecordReportView.as_view(), name="fleet_record_pdf"
    ),
    path("fleet/", fleet_views.FleetManagementView.as_view(), name="fleet_manage"),
    path(
        "fleet/vehicles/create/",
        fleet_views.VehicleCreateView.as_view(),
        name="fleet_vehicle_create",
    ),
    path(
        "fleet/vehicles/<int:vehicle_id>/edit/",
        fleet_views.VehicleEditView.as_view(),
        name="fleet_vehicle_edit",
    ),
    path(
        "fleet/vehicles/<int:vehicle_id>/toggle/",
        fleet_views.VehicleToggleActiveView.as_view(),
        name="fleet_vehicle_toggle",
    ),
    path(
        "fleet/vehicles/<int:vehicle_id>/delete/",
        fleet_views.VehicleDeleteView.as_view(),
        name="fleet_vehicle_delete",
    ),
    path(
        "fleet/assignments/assign/",
        fleet_views.DriverAssignView.as_view(),
        name="fleet_assign",
    ),
    path(
        "fleet/assignments/<int:assignment_id>/end/",
        fleet_views.DriverDeassignView.as_view(),
        name="fleet_deassign",
    ),
    path(
        "fleet/drivers/create/",
        fleet_views.DriverCreateView.as_view(),
        name="fleet_driver_create",
    ),
    path(
        "fleet/drivers/<int:driver_id>/edit/",
        fleet_views.DriverEditView.as_view(),
        name="fleet_driver_edit",
    ),
    path(
        "fleet/drivers/<int:driver_id>/toggle/",
        fleet_views.DriverToggleActiveView.as_view(),
        name="fleet_driver_toggle",
    ),
    path("tracker/", views.TrackerView.as_view(), name="tracker"),
    path("trips/", views.TripHistoryView.as_view(), name="trip_history"),
    path("trips/history.pdf", views.TripHistoryReportView.as_view(), name="trip_history_pdf"),
]
