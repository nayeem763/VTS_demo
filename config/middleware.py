"""Project middleware.

:class:`SecurityHeadersMiddleware` emits a Content-Security-Policy and a
Permissions-Policy on every response. Django's :class:`SecurityMiddleware`
already handles HSTS, referrer policy, content-type sniffing, and the
cross-origin-opener policy; those are configured in the settings instead.
"""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Attach CSP and Permissions-Policy headers.

    The policy is assembled once at startup from ``settings.CONTENT_SECURITY_POLICY``.
    The Django admin ships some inline scripts, so responses under the admin
    prefix receive a relaxed ``script-src`` that also allows ``'unsafe-inline'``;
    every other response gets the strict, self-only policy.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        policy = settings.CONTENT_SECURITY_POLICY
        self._strict_csp = self._render(policy)
        # Relaxed variant for the admin only.
        relaxed = {**policy, "script-src": [*policy["script-src"], "'unsafe-inline'"]}
        self._admin_csp = self._render(relaxed)
        self._admin_prefix = "/" + settings.ADMIN_URL_PREFIX.lstrip("/")
        self._permissions_policy = getattr(settings, "PERMISSIONS_POLICY", "")

    @staticmethod
    def _render(policy: dict[str, list[str]]) -> str:
        return "; ".join(f"{name} {' '.join(values)}" for name, values in policy.items())

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if "Content-Security-Policy" not in response:
            is_admin_path = request.path.startswith(self._admin_prefix)
            response["Content-Security-Policy"] = (
                self._admin_csp if is_admin_path else self._strict_csp
            )
        if self._permissions_policy and "Permissions-Policy" not in response:
            response["Permissions-Policy"] = self._permissions_policy
        return response
