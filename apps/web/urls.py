"""Web (server-rendered) page routes. Auth routes are included from accounts."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.PublicMapView.as_view(), name="public_map"),
    path("dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("tracker/", views.TrackerView.as_view(), name="tracker"),
    path("trips/", views.TripHistoryView.as_view(), name="trip_history"),
]
