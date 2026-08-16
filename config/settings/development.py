"""Development settings: optimised for local speed and convenience.

Never used in production. Enables DEBUG, the browsable API, and SQLite.
"""

from __future__ import annotations

from .base import *
from .base import REST_FRAMEWORK

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

# Show the DRF browsable API while developing.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Email to console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
