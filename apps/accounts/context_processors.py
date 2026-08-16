"""Template context processors for role-aware navigation."""

from __future__ import annotations

from django.http import HttpRequest

from .permissions import is_admin, is_driver


def roles(request: HttpRequest) -> dict[str, bool]:
    """Expose ``is_admin`` / ``is_driver`` to every template for nav rendering."""
    user = getattr(request, "user", None)
    return {
        "is_admin": is_admin(user) if user is not None else False,
        "is_driver": is_driver(user) if user is not None else False,
    }
