"""Authentication views: role-aware login and a trip-closing logout."""

from __future__ import annotations

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from .forms import StyledAuthenticationForm
from .permissions import RequestUser, is_admin, is_driver


def role_landing_url(user: RequestUser) -> str:
    """Return the page a freshly authenticated user should land on."""
    if is_admin(user):
        return reverse("web:admin_dashboard")
    if is_driver(user):
        return reverse("web:tracker")
    return reverse("web:public_map")


class _BaseLoginView(LoginView):
    """Shared login behaviour: styled form and role-aware redirect."""

    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        # Respect a safe ?next= target, otherwise route by role.
        return self.get_redirect_url() or role_landing_url(self.request.user)


class AdminLoginView(_BaseLoginView):
    template_name = "accounts/admin_login.html"


class DriverLoginView(_BaseLoginView):
    template_name = "accounts/driver_login.html"


class LogoutView(View):
    """Log out via POST. For drivers, close any open trip first (§12.3)."""

    def post(self, request):
        user = request.user
        if user.is_authenticated and is_driver(user):
            # Imported lazily to avoid an app-load import cycle.
            from apps.tracking.services import close_open_trip_for_user

            close_open_trip_for_user(user, reason="driver_logout")
        auth_logout(request)
        return redirect("web:public_map")
