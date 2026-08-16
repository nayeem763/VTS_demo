"""WSGI entrypoint. Defaults to production settings; overridden by the
DJANGO_SETTINGS_MODULE environment variable when set (e.g. locally)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
