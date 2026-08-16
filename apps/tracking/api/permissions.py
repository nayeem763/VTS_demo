"""DRF permission classes for the tracking API."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.accounts.permissions import is_admin, is_driver
from apps.fleet.selectors import get_active_assignment_for_user


class IsDriverWithActiveAssignment(BasePermission):
    """Allow only authenticated drivers who currently hold a vehicle assignment."""

    message = "You must be an active driver with a current vehicle assignment."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not is_driver(user):
            return False
        return get_active_assignment_for_user(user) is not None


class IsAdminRole(BasePermission):
    """Allow only Admins (Admin group) and superusers."""

    message = "Administrator access is required."

    def has_permission(self, request, view) -> bool:
        return is_admin(request.user)
