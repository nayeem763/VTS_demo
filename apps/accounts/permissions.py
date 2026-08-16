"""Role helpers and view mixins shared across the project.

Roles are enforced in code (here and in the DRF permission classes) rather
than relying on group membership alone, so authorisation stays explicit.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import AnonymousUser, User

#: The type of ``request.user``: an authenticated ``User`` or an anonymous one.
#: Both expose ``is_authenticated``, ``is_superuser`` and ``groups``, so the
#: role predicates below type-check without narrowing casts.
RequestUser = User | AnonymousUser


def is_admin(user: RequestUser) -> bool:
    """True for superusers and members of the Admin group."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=settings.ADMIN_GROUP).exists()


def is_driver(user: RequestUser) -> bool:
    """True for authenticated users in the Driver group with an active profile."""
    if not user or not user.is_authenticated:
        return False
    if not user.groups.filter(name=settings.DRIVER_GROUP).exists():
        return False
    profile = getattr(user, "driver_profile", None)
    return bool(profile and profile.is_active)


class RoleRequiredMixin(AccessMixin):
    """Base mixin that checks a role predicate before dispatching a view."""

    #: Callable taking a user and returning bool.
    role_check = staticmethod(is_admin)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.role_check(request.user):
            # Authenticated but wrong role -> 403, not a login redirect loop.
            self.raise_exception = True
            return self.handle_no_permission()
        # AccessMixin is contractually combined with a View, which supplies dispatch().
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


class AdminRequiredMixin(RoleRequiredMixin):
    """Require an authenticated Admin (or superuser)."""

    role_check = staticmethod(is_admin)
    login_url = "accounts:admin_login"


class DriverRequiredMixin(RoleRequiredMixin):
    """Require an authenticated, active Driver."""

    role_check = staticmethod(is_driver)
    login_url = "accounts:driver_login"
