"""URL routes for the versioned tracking API (mounted at ``/api/v1/``)."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("locations/", views.LocationCreateView.as_view(), name="location-create"),
    path(
        "vehicles/latest-locations/",
        views.LatestActiveVehicleLocationsView.as_view(),
        name="vehicle-latest-locations",
    ),
    path(
        "vehicles/<int:vehicle_id>/latest-location/",
        views.VehicleLatestLocationView.as_view(),
        name="vehicle-latest-location",
    ),
    path("trips/", views.TripListView.as_view(), name="trip-list"),
    path("trips/<int:trip_id>/points/", views.TripPointsView.as_view(), name="trip-points"),
]
