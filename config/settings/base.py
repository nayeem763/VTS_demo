"""Base settings shared by every environment.

Anything that differs between environments (secrets, database location, the
``DEBUG`` flag, allowed hosts) is read from the environment via ``python-decouple``
so the same code runs everywhere and secrets never live in the repository.
"""

from __future__ import annotations

from pathlib import Path

import dj_database_url
from decouple import Csv, config

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# base.py -> settings -> config -> repository root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
# A development-only fallback keeps `manage.py` usable without a .env file.
# `production.py` re-reads SECRET_KEY with no default, so production must set it.
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-only-key-change-me-in-production",
)
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# The Django admin is mounted behind an obscure prefix (not ``/admin/``) to
# reduce automated probing. Keep this in sync with ``config/urls.py``.
ADMIN_URL_PREFIX = config("ADMIN_URL_PREFIX", default="django-admin/")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "axes",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.fleet",
    "apps.tracking",
    "apps.web",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must come immediately after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Adds Content-Security-Policy and Permissions-Policy headers.
    "config.middleware.SecurityHeadersMiddleware",
    # AxesMiddleware must be the last authentication-related middleware.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.accounts.context_processors.roles",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Local development falls back to SQLite. Production supplies a single
# ``DATABASE_URL`` (Supabase PostgreSQL). Prefer the Supabase *session-mode*
# pooler connection string on Render (IPv4, supports persistent connections).
DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=config("DB_CONN_MAX_AGE", default=600, cast=int),
            ssl_require=config("DB_SSL_REQUIRE", default=True, cast=bool),
        )
    }
    # Set to True only when using the Supabase *transaction-mode* pooler (6543).
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = config(
        "DB_DISABLE_SERVER_SIDE_CURSORS", default=False, cast=bool
    )
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

# ---------------------------------------------------------------------------
# Authentication & authorisation
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend must be first so lockouts are enforced.
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Role group names used across the project.
ADMIN_GROUP = "Admin"
DRIVER_GROUP = "Driver"

# Where @login_required and LoginRequiredMixin send anonymous users by default.
LOGIN_URL = "accounts:admin_login"

# Sessions: persistent by default so drivers are not logged out on tab close.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=60 * 60 * 24 * 14, cast=int)

# ---------------------------------------------------------------------------
# Brute-force protection (django-axes)
# ---------------------------------------------------------------------------
AXES_ENABLED = True
AXES_FAILURE_LIMIT = config("AXES_FAILURE_LIMIT", default=5, cast=int)
AXES_COOLOFF_TIME = config("AXES_COOLOFF_HOURS", default=1, cast=int)  # hours
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "accounts/lockout.html"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
# Deny by default: endpoints opt in to AllowAny explicitly (public read paths).
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "location_ingest": config("THROTTLE_LOCATION_INGEST", default="120/min"),
        "public_read": config("THROTTLE_PUBLIC_READ", default="240/min"),
    },
    "UNAUTHENTICATED_USER": "django.contrib.auth.models.AnonymousUser",
}

# ---------------------------------------------------------------------------
# Internationalisation & time
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="Asia/Dhaka")
USE_I18N = True
USE_TZ = True  # Always store UTC in the DB; TIME_ZONE controls display only.

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static_collected"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Security headers (Content-Security-Policy / Permissions-Policy)
# ---------------------------------------------------------------------------
# Emitted by ``config.middleware.SecurityHeadersMiddleware``. All first-party
# scripts and styles are self-hosted, so ``script-src 'self'`` blocks injected
# inline scripts (XSS mitigation). Map tiles are the only third-party asset.
# ``style-src`` keeps ``'unsafe-inline'`` because Bootstrap and Leaflet apply
# inline style attributes for layout; that is a deliberate, narrow allowance.
MAP_TILE_HOSTS = config(
    "MAP_TILE_HOSTS",
    default="https://*.tile.openstreetmap.org https://tile.openstreetmap.org",
    cast=Csv(delimiter=" "),
)
# Applied to non-admin responses. The Django admin gets a relaxed script-src
# (it ships inline scripts) via the middleware.
CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "base-uri": ["'self'"],
    "frame-ancestors": ["'none'"],
    "object-src": ["'none'"],
    "form-action": ["'self'"],
    "font-src": ["'self'"],
    "img-src": ["'self'", "data:", *MAP_TILE_HOSTS],
    "style-src": ["'self'", "'unsafe-inline'"],
    "script-src": ["'self'"],
    "connect-src": ["'self'"],
}
PERMISSIONS_POLICY = "geolocation=(self), camera=(), microphone=(), payment=()"

# ---------------------------------------------------------------------------
# Domain configuration
# ---------------------------------------------------------------------------
# A Trip with no accepted Location for this many minutes is treated as stale
# and closed by `manage.py close_stale_trips` (see docs). Configuration, not a
# hard-coded architectural value.
TRIP_INACTIVITY_MINUTES = config("TRIP_INACTIVITY_MINUTES", default=10, cast=int)

# A captured_at further than this many seconds into the future is rejected as
# clock skew / spoofing. Also bounds how old a reported fix may be.
LOCATION_MAX_FUTURE_SKEW_SECONDS = config("LOCATION_MAX_FUTURE_SKEW_SECONDS", default=120, cast=int)
LOCATION_MAX_AGE_SECONDS = config("LOCATION_MAX_AGE_SECONDS", default=60 * 60, cast=int)

# A vehicle whose latest fix is older than this is shown as "stale" on maps.
LOCATION_STALE_SECONDS = config("LOCATION_STALE_SECONDS", default=30, cast=int)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {
        "handlers": ["console"],
        "level": config("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {
            "handlers": ["console"],
            "level": config("LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}
