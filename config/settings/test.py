"""Test settings: fast and deterministic.

Inherits development, then speeds up password hashing and disables the
brute-force lockout so repeated test logins are not blocked.
"""

from __future__ import annotations

from .base import REST_FRAMEWORK
from .development import *

# Fast, insecure hashing — acceptable only for the test database.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Never lock out during automated tests.
AXES_ENABLED = False

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Deterministic API tests: JSON only (no browsable-API template rendering) and
# no rate limiting (throttle scopes are asserted structurally instead — a live
# rate-limit test would depend on wall-clock timing and shared cache state).
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

# Force SQLite for tests regardless of any DATABASE_URL in the environment.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Keep logging quiet during test runs.
import logging  # noqa: E402

logging.disable(logging.CRITICAL)
