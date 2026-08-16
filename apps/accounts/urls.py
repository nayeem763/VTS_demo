"""Authentication URLs (login/logout) owned by the accounts app."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("admin-login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("driver-login/", views.DriverLoginView.as_view(), name="driver_login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
