"""Root URL configuration.

Web (server-rendered) pages live under ``apps.web``. The versioned REST API
lives under ``/api/v1/`` in ``apps.tracking.api``. A lightweight ``/healthz``
endpoint supports uptime monitoring and keeping the free host warm.
"""

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def healthz(_request) -> HttpResponse:
    """Liveness probe used by uptime monitors and keep-alive pingers."""
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path(settings.ADMIN_URL_PREFIX, admin.site.urls),
    path("api/v1/", include("apps.tracking.api.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.web.urls")),
]
