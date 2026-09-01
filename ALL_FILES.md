# Vehicle Tracking System — All Files

Consolidated contents of the project's source, config, and docs. Excludes `Vehicle_Tracking/` and `backup/`, plus VCS/virtualenv/cache directories, generated output, binaries, and vendored third-party libraries (`static/vendor/`).

**114 files.**

## Table of contents

- [`.claude/settings.local.json`](#claudesettingslocaljson)
- [`.editorconfig`](#editorconfig)
- [`.env`](#env)
- [`.env.example`](#envexample)
- [`.gitattributes`](#gitattributes)
- [`.github/pull_request_template.md`](#githubpull_request_templatemd)
- [`.github/workflows/ci.yml`](#githubworkflowsciyml)
- [`.gitignore`](#gitignore)
- [`.python-version`](#python-version)
- [`CU_VTS_Backend_Architecture.md`](#cu_vts_backend_architecturemd)
- [`Procfile`](#procfile)
- [`README.md`](#readmemd)
- [`apps/__init__.py`](#apps__init__py)
- [`apps/accounts/__init__.py`](#appsaccounts__init__py)
- [`apps/accounts/admin.py`](#appsaccountsadminpy)
- [`apps/accounts/apps.py`](#appsaccountsappspy)
- [`apps/accounts/context_processors.py`](#appsaccountscontext_processorspy)
- [`apps/accounts/forms.py`](#appsaccountsformspy)
- [`apps/accounts/management/__init__.py`](#appsaccountsmanagement__init__py)
- [`apps/accounts/management/commands/__init__.py`](#appsaccountsmanagementcommands__init__py)
- [`apps/accounts/management/commands/seed_roles.py`](#appsaccountsmanagementcommandsseed_rolespy)
- [`apps/accounts/migrations/0001_initial.py`](#appsaccountsmigrations0001_initialpy)
- [`apps/accounts/migrations/__init__.py`](#appsaccountsmigrations__init__py)
- [`apps/accounts/models.py`](#appsaccountsmodelspy)
- [`apps/accounts/permissions.py`](#appsaccountspermissionspy)
- [`apps/accounts/services.py`](#appsaccountsservicespy)
- [`apps/accounts/signals.py`](#appsaccountssignalspy)
- [`apps/accounts/tests/__init__.py`](#appsaccountstests__init__py)
- [`apps/accounts/tests/test_authentication.py`](#appsaccountsteststest_authenticationpy)
- [`apps/accounts/tests/test_permissions.py`](#appsaccountsteststest_permissionspy)
- [`apps/accounts/tests/test_services.py`](#appsaccountsteststest_servicespy)
- [`apps/accounts/urls.py`](#appsaccountsurlspy)
- [`apps/accounts/views.py`](#appsaccountsviewspy)
- [`apps/fleet/__init__.py`](#appsfleet__init__py)
- [`apps/fleet/admin.py`](#appsfleetadminpy)
- [`apps/fleet/apps.py`](#appsfleetappspy)
- [`apps/fleet/migrations/0001_initial.py`](#appsfleetmigrations0001_initialpy)
- [`apps/fleet/migrations/__init__.py`](#appsfleetmigrations__init__py)
- [`apps/fleet/models.py`](#appsfleetmodelspy)
- [`apps/fleet/selectors.py`](#appsfleetselectorspy)
- [`apps/fleet/services.py`](#appsfleetservicespy)
- [`apps/fleet/tests/__init__.py`](#appsfleettests__init__py)
- [`apps/fleet/tests/test_models.py`](#appsfleetteststest_modelspy)
- [`apps/fleet/tests/test_selectors.py`](#appsfleetteststest_selectorspy)
- [`apps/fleet/tests/test_services.py`](#appsfleetteststest_servicespy)
- [`apps/tracking/__init__.py`](#appstracking__init__py)
- [`apps/tracking/admin.py`](#appstrackingadminpy)
- [`apps/tracking/api/__init__.py`](#appstrackingapi__init__py)
- [`apps/tracking/api/permissions.py`](#appstrackingapipermissionspy)
- [`apps/tracking/api/serializers.py`](#appstrackingapiserializerspy)
- [`apps/tracking/api/urls.py`](#appstrackingapiurlspy)
- [`apps/tracking/api/views.py`](#appstrackingapiviewspy)
- [`apps/tracking/apps.py`](#appstrackingappspy)
- [`apps/tracking/management/__init__.py`](#appstrackingmanagement__init__py)
- [`apps/tracking/management/commands/__init__.py`](#appstrackingmanagementcommands__init__py)
- [`apps/tracking/management/commands/close_stale_trips.py`](#appstrackingmanagementcommandsclose_stale_tripspy)
- [`apps/tracking/management/commands/create_demo_data.py`](#appstrackingmanagementcommandscreate_demo_datapy)
- [`apps/tracking/migrations/0001_initial.py`](#appstrackingmigrations0001_initialpy)
- [`apps/tracking/migrations/__init__.py`](#appstrackingmigrations__init__py)
- [`apps/tracking/models.py`](#appstrackingmodelspy)
- [`apps/tracking/selectors.py`](#appstrackingselectorspy)
- [`apps/tracking/services.py`](#appstrackingservicespy)
- [`apps/tracking/tests/__init__.py`](#appstrackingtests__init__py)
- [`apps/tracking/tests/test_location_api.py`](#appstrackingteststest_location_apipy)
- [`apps/tracking/tests/test_public_api.py`](#appstrackingteststest_public_apipy)
- [`apps/tracking/tests/test_selectors.py`](#appstrackingteststest_selectorspy)
- [`apps/tracking/tests/test_services.py`](#appstrackingteststest_servicespy)
- [`apps/tracking/tests/test_trip_api.py`](#appstrackingteststest_trip_apipy)
- [`apps/tracking/tests/test_validators.py`](#appstrackingteststest_validatorspy)
- [`apps/tracking/validators.py`](#appstrackingvalidatorspy)
- [`apps/web/__init__.py`](#appsweb__init__py)
- [`apps/web/apps.py`](#appswebappspy)
- [`apps/web/tests/__init__.py`](#appswebtests__init__py)
- [`apps/web/tests/test_views.py`](#appswebteststest_viewspy)
- [`apps/web/urls.py`](#appsweburlspy)
- [`apps/web/views.py`](#appswebviewspy)
- [`build.sh`](#buildsh)
- [`config/__init__.py`](#config__init__py)
- [`config/asgi.py`](#configasgipy)
- [`config/middleware.py`](#configmiddlewarepy)
- [`config/settings/__init__.py`](#configsettings__init__py)
- [`config/settings/base.py`](#configsettingsbasepy)
- [`config/settings/development.py`](#configsettingsdevelopmentpy)
- [`config/settings/production.py`](#configsettingsproductionpy)
- [`config/settings/test.py`](#configsettingstestpy)
- [`config/urls.py`](#configurlspy)
- [`config/wsgi.py`](#configwsgipy)
- [`conftest.py`](#conftestpy)
- [`docs/api-contract.md`](#docsapi-contractmd)
- [`docs/architecture.md`](#docsarchitecturemd)
- [`docs/decisions.md`](#docsdecisionsmd)
- [`docs/testing.md`](#docstestingmd)
- [`manage.py`](#managepy)
- [`pyproject.toml`](#pyprojecttoml)
- [`render.yaml`](#renderyaml)
- [`requirements/base.txt`](#requirementsbasetxt)
- [`requirements/development.txt`](#requirementsdevelopmenttxt)
- [`requirements/production.txt`](#requirementsproductiontxt)
- [`runtime.txt`](#runtimetxt)
- [`static/css/app.css`](#staticcssappcss)
- [`static/js/admin-map.js`](#staticjsadmin-mapjs)
- [`static/js/public-map.js`](#staticjspublic-mapjs)
- [`static/js/tracker.js`](#staticjstrackerjs)
- [`static/js/trip-history.js`](#staticjstrip-historyjs)
- [`static/js/vts-common.js`](#staticjsvts-commonjs)
- [`templates/accounts/_login_card.html`](#templatesaccounts_login_cardhtml)
- [`templates/accounts/admin_login.html`](#templatesaccountsadmin_loginhtml)
- [`templates/accounts/driver_login.html`](#templatesaccountsdriver_loginhtml)
- [`templates/accounts/lockout.html`](#templatesaccountslockouthtml)
- [`templates/base.html`](#templatesbasehtml)
- [`templates/dashboard/admin_dashboard.html`](#templatesdashboardadmin_dashboardhtml)
- [`templates/public/vehicle_map.html`](#templatespublicvehicle_maphtml)
- [`templates/tracker/tracker.html`](#templatestrackertrackerhtml)
- [`templates/trips/trip_history.html`](#templatestripstrip_historyhtml)

---

## `.claude/settings.local.json`

- **Folder:** `.claude/`
- **File:** `settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(curl -s -o /dev/null http://127.0.0.1:8931/healthz)",
      "Bash(curl -s -w \"\\\\n[HTTP %{http_code}]\\\\n\" http://127.0.0.1:8931/healthz)",
      "Bash(curl -s -o /dev/null -w \"[HTTP %{http_code}] %{content_type}\\\\n\" http://127.0.0.1:8931/)",
      "Bash(curl -s -w \"\\\\n[HTTP %{http_code}]\\\\n\" http://127.0.0.1:8931/api/v1/vehicles/latest-locations/)",
      "Bash(curl -s -o /dev/null -w \"[HTTP %{http_code}]\\\\n\" -X POST http://127.0.0.1:8931/api/v1/locations/ -H \"Content-Type: application/json\" -d '{}')",
      "Bash(curl -s -o /dev/null -w \"[HTTP %{http_code}] -> %{redirect_url}\\\\n\" http://127.0.0.1:8931/dashboard/)",
      "Bash(awk '{print $NF}')",
      "Bash(grep -vE \"^\\\\.?$\")"
    ]
  }
}
```

## `.editorconfig`

- **Folder:** `./ (project root)`
- **File:** `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.py]
indent_size = 4
max_line_length = 100

[*.{html,css,js,json,yml,yaml,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## `.env`

- **Folder:** `./ (project root)`
- **File:** `.env`

```bash
# ===========================================================================
# CU-VTS environment configuration.
#
# Copy this file to ``.env`` for local development:  cp .env.example .env
# In production (Render), set these as service environment variables instead.
# NEVER commit a real .env — it is git-ignored.
# ===========================================================================

# --- Which settings module to load ----------------------------------------
# Local dev:   config.settings.development   (default in manage.py)
# Test:        config.settings.test
# Production:  config.settings.production     (default in wsgi.py)
DJANGO_SETTINGS_MODULE=config.settings.development

# --- Core -------------------------------------------------------------------
# Generate one with:  python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
# In production this is MANDATORY (no fallback). On Render, use generateValue.
SECRET_KEY=change-me-in-production-use-a-50-char-random-string

# Debug must be False in production. Leave unset (defaults to False) for prod.
DEBUG=True

# Comma-separated. Production auto-appends the Render hostname; add custom domains here.
ALLOWED_HOSTS=localhost,127.0.0.1
# Comma-separated full origins (scheme + host). Needed for POSTs behind HTTPS/custom domains.
# CSRF_TRUSTED_ORIGINS=https://your-domain.example

# Obscure the admin path (must end with a slash). Change from the default in production.
ADMIN_URL_PREFIX=django-admin/

# --- Database ---------------------------------------------------------------
# Leave DATABASE_URL empty to use a local SQLite file (dev/test).
# In production, set the Supabase connection string. Prefer the SESSION-mode
# pooler (port 5432, IPv4) for Render:
#   postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
DATABASE_URL=
# Persistent-connection lifetime (seconds). 0 disables connection reuse.
DB_CONN_MAX_AGE=600
# Require TLS to the database (recommended for Supabase).
DB_SSL_REQUIRE=True
# Set True ONLY if using the Supabase TRANSACTION-mode pooler (port 6543).
DB_DISABLE_SERVER_SIDE_CURSORS=False

# --- Sessions & security ----------------------------------------------------
# Session lifetime in seconds (default 14 days).
SESSION_COOKIE_AGE=1209600
# Redirect all HTTP to HTTPS (production only; True by default there).
# SECURE_SSL_REDIRECT=True
# HSTS max-age in seconds (production only; default 1 year).
# SECURE_HSTS_SECONDS=31536000

# --- Brute-force lockout (django-axes) --------------------------------------
AXES_FAILURE_LIMIT=5
AXES_COOLOFF_HOURS=1

# --- API throttling ---------------------------------------------------------
THROTTLE_LOCATION_INGEST=120/min
THROTTLE_PUBLIC_READ=240/min

# --- Domain tuning ----------------------------------------------------------
TIME_ZONE=Asia/Dhaka
# Close trips idle longer than this many minutes.
TRIP_INACTIVITY_MINUTES=10
# Reject fixes timestamped further than this into the future (clock-skew guard).
LOCATION_MAX_FUTURE_SKEW_SECONDS=120
# Reject fixes older than this (stale/replayed submissions).
LOCATION_MAX_AGE_SECONDS=3600
# A live marker older than this is rendered as "stale" on the maps.
LOCATION_STALE_SECONDS=30
# Space-separated map tile hosts allowed by the Content-Security-Policy.
MAP_TILE_HOSTS=https://*.tile.openstreetmap.org https://tile.openstreetmap.org

# --- Logging ----------------------------------------------------------------
LOG_LEVEL=INFO

# --- Error reporting (optional) ---------------------------------------------
# Leave empty to disable Sentry entirely.
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.0
```

## `.env.example`

- **Folder:** `./ (project root)`
- **File:** `.env.example`

```bash
# ===========================================================================
# CU-VTS environment configuration.
#
# Copy this file to ``.env`` for local development:  cp .env.example .env
# In production (Render), set these as service environment variables instead.
# NEVER commit a real .env — it is git-ignored.
# ===========================================================================

# --- Which settings module to load ----------------------------------------
# Local dev:   config.settings.development   (default in manage.py)
# Test:        config.settings.test
# Production:  config.settings.production     (default in wsgi.py)
DJANGO_SETTINGS_MODULE=config.settings.development

# --- Core -------------------------------------------------------------------
# Generate one with:  python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
# In production this is MANDATORY (no fallback). On Render, use generateValue.
SECRET_KEY=change-me-in-production-use-a-50-char-random-string

# Debug must be False in production. Leave unset (defaults to False) for prod.
DEBUG=True

# Comma-separated. Production auto-appends the Render hostname; add custom domains here.
ALLOWED_HOSTS=localhost,127.0.0.1
# Comma-separated full origins (scheme + host). Needed for POSTs behind HTTPS/custom domains.
# CSRF_TRUSTED_ORIGINS=https://your-domain.example

# Obscure the admin path (must end with a slash). Change from the default in production.
ADMIN_URL_PREFIX=django-admin/

# --- Database ---------------------------------------------------------------
# Leave DATABASE_URL empty to use a local SQLite file (dev/test).
# In production, set the Supabase connection string. Prefer the SESSION-mode
# pooler (port 5432, IPv4) for Render:
#   postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
DATABASE_URL=
# Persistent-connection lifetime (seconds). 0 disables connection reuse.
DB_CONN_MAX_AGE=600
# Require TLS to the database (recommended for Supabase).
DB_SSL_REQUIRE=True
# Set True ONLY if using the Supabase TRANSACTION-mode pooler (port 6543).
DB_DISABLE_SERVER_SIDE_CURSORS=False

# --- Sessions & security ----------------------------------------------------
# Session lifetime in seconds (default 14 days).
SESSION_COOKIE_AGE=1209600
# Redirect all HTTP to HTTPS (production only; True by default there).
# SECURE_SSL_REDIRECT=True
# HSTS max-age in seconds (production only; default 1 year).
# SECURE_HSTS_SECONDS=31536000

# --- Brute-force lockout (django-axes) --------------------------------------
AXES_FAILURE_LIMIT=5
AXES_COOLOFF_HOURS=1

# --- API throttling ---------------------------------------------------------
THROTTLE_LOCATION_INGEST=120/min
THROTTLE_PUBLIC_READ=240/min

# --- Domain tuning ----------------------------------------------------------
TIME_ZONE=Asia/Dhaka
# Close trips idle longer than this many minutes.
TRIP_INACTIVITY_MINUTES=10
# Reject fixes timestamped further than this into the future (clock-skew guard).
LOCATION_MAX_FUTURE_SKEW_SECONDS=120
# Reject fixes older than this (stale/replayed submissions).
LOCATION_MAX_AGE_SECONDS=3600
# A live marker older than this is rendered as "stale" on the maps.
LOCATION_STALE_SECONDS=30
# Space-separated map tile hosts allowed by the Content-Security-Policy.
MAP_TILE_HOSTS=https://*.tile.openstreetmap.org https://tile.openstreetmap.org

# --- Logging ----------------------------------------------------------------
LOG_LEVEL=INFO

# --- Error reporting (optional) ---------------------------------------------
# Leave empty to disable Sentry entirely.
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.0
```

## `.gitattributes`

- **Folder:** `./ (project root)`
- **File:** `.gitattributes`

```ini
# Normalise line endings across platforms.
* text=auto eol=lf

# Shell scripts and the build script must keep LF endings to run on Render (Linux).
*.sh text eol=lf

# Binary assets — never diff or convert.
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.woff binary
*.woff2 binary

# Keep vendored front-end libraries out of language stats and diffs.
static/vendor/** linguist-vendored
```

## `.github/pull_request_template.md`

- **Folder:** `.github/`
- **File:** `pull_request_template.md`

```markdown
<!-- Thanks for contributing to CU-VTS. Keep PRs small and focused. -->

## What & why

<!-- What does this change do, and why? Link any issue: Closes #NN -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [ ] Docs / tooling
- [ ] Security fix

## How to test

<!-- Steps for a reviewer to verify locally. -->

## Quality gates

All four must be green locally (CI runs them too):

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy .`
- [ ] `pytest` (added/updated tests for the change)

## Checklist

- [ ] Business logic lives in **services** (writes) / **selectors** (reads), not in views.
- [ ] No secrets, keys, or real `.env` values committed.
- [ ] Model changes include a migration (`makemigrations`), and `migrate` runs clean.
- [ ] The [privacy boundary](../docs/architecture.md#the-privacy-boundary) is preserved — no driver identity leaked to public serializers.
- [ ] Docs updated if behavior, the API contract, or a decision changed.
```

## `.github/workflows/ci.yml`

- **Folder:** `.github/workflows/`
- **File:** `ci.yml`

```yaml
name: CI

# Runs the same four quality gates you run locally — lint, format, types,
# tests — plus the production deploy check and a migration-drift guard.

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

# Cancel superseded runs on the same ref to save free-tier minutes.
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  quality:
    name: Lint, type-check & test
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Check out the repository
        uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: "3.13.1"
          cache: pip
          cache-dependency-path: requirements/*.txt

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/development.txt

      - name: Ruff (lint)
        run: ruff check --output-format=github .

      - name: Ruff (format check)
        run: ruff format --check .

      - name: mypy (static types)
        run: mypy .

      - name: pytest (with coverage)
        run: pytest --cov=apps --cov-report=term-missing

      - name: Migration drift check
        # Fails if a model change was made without a matching migration.
        run: python manage.py makemigrations --check --dry-run

      - name: Django deploy check (production settings)
        env:
          DJANGO_SETTINGS_MODULE: config.settings.production
          # A throwaway key just for the check; real deploys generate their own.
          SECRET_KEY: ci-only-ephemeral-secret-key-not-used-in-production
          ALLOWED_HOSTS: example.com
        run: python manage.py check --deploy --fail-level WARNING
```

## `.gitignore`

- **Folder:** `./ (project root)`
- **File:** `.gitignore`

```ini
# ---- Python ----
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# ---- Virtual environments ----
.venv/
venv/
env/
ENV/

# ---- Django ----
*.log
db.sqlite3
db.sqlite3-journal
# Collected static output (regenerated by `collectstatic`; vendored source in static/ IS committed)
/static_collected/
/media/

# ---- Environment / secrets ----
.env
.env.*
!.env.example

# ---- Test / coverage / type-check caches ----
.pytest_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml
.mypy_cache/
.ruff_cache/
.dmypy.json

# ---- Editors / OS ----
.idea/
.vscode/
*.swp
*~
.DS_Store
Thumbs.db
```

## `.python-version`

- **Folder:** `./ (project root)`
- **File:** `.python-version`

```text
3.13.1
```

## `CU_VTS_Backend_Architecture.md`

- **Folder:** `./ (project root)`
- **File:** `CU_VTS_Backend_Architecture.md`

````markdown
# CU Vehicle Tracking System (CU-VTS)

## Backend Architecture and File Structure Proposal

**Document status:** Proposed architecture baseline  
**Version:** 1.0  
**Submitted by:** Tahmid Fahim, Group 7  
**Submitted to:** Project Supervisor / CTO  
**Source of truth:** Finalised CU-VTS Functional Requirements  
**Scope:** Backend architecture, repository structure, Supabase PostgreSQL integration, security boundaries, and implementation sequence

> **Professional limitation:** No architecture can honestly be guaranteed never to change. This proposal is designed to keep the core boundaries stable. Configuration values, minor fields, and implementation details may be adjusted without replacing the architecture.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Architectural Rationale](#2-architectural-rationale)
- [3. High-Level System Context](#3-high-level-system-context)
- [4. System Responsibility Boundaries](#4-system-responsibility-boundaries)
- [5. Django Module Design](#5-django-module-design)
- [6. Final Repository and File Structure](#6-final-repository-and-file-structure)
- [7. Backend Layering Rules](#7-backend-layering-rules)
- [8. Authentication and Authorisation](#8-authentication-and-authorisation)
- [9. Data Model](#9-data-model)
- [10. Database Constraints and Indexes](#10-database-constraints-and-indexes)
- [11. Versioned REST API Contract](#11-versioned-rest-api-contract)
- [12. Trip Lifecycle](#12-trip-lifecycle)
- [13. Supabase PostgreSQL Integration](#13-supabase-postgresql-integration)
- [14. Deployment Topology](#14-deployment-topology)
- [15. Security Baseline](#15-security-baseline)
- [16. Testing Baseline](#16-testing-baseline)
- [17. Implementation Sequence](#17-implementation-sequence)
- [18. Primary Technical Risks and Mitigations](#18-primary-technical-risks-and-mitigations)
- [19. Architectural Decisions Requested for Approval](#19-architectural-decisions-requested-for-approval)
- [20. Backend Definition of Ready](#20-backend-definition-of-ready)
- [21. Closing Recommendation](#21-closing-recommendation)
- [Appendix A. Short Presentation Script](#appendix-a-short-presentation-script)
- [Appendix B. Technical References](#appendix-b-technical-references)

---

## 1. Executive Summary

CU-VTS will use a **modular Django monolith**. Django will be the sole application backend and will control authentication, permissions, business rules, REST APIs, validation, migrations, and transactions. Supabase will be used only as the hosted PostgreSQL database. The Django application will be deployed as one Render web service.

### Final technology decisions

| Technical area | Final proposal |
| --- | --- |
| Architecture style | Modular Django monolith |
| Backend framework | Django 5.2 LTS |
| API layer | Django REST Framework |
| Frontend delivery | Django templates, Bootstrap, Leaflet.js, and vanilla JavaScript |
| Authentication | Django session authentication |
| Authorisation | Django Groups, model permissions, and DRF permission classes |
| Production database | PostgreSQL hosted on Supabase |
| Application hosting | Render web service |
| Production server | Gunicorn |
| Static-file delivery | WhiteNoise |
| Live dashboard updates | Periodic HTTP polling |
| GPS source | Assigned Android phone browser |
| API namespace | `/api/v1/` |

### Deliberately excluded from the MVP

- Microservices
- WebSockets
- Redis or Celery
- Supabase Auth or Supabase Realtime
- Direct browser-to-database access
- Native Android or iOS applications
- Dynamic Route management
- ETA prediction
- AI-based analytics
- External traffic or navigation APIs

---

## 2. Architectural Rationale

The architecture is selected for the actual project constraints:

- Three contributing team members
- A limited MVP delivery period
- Approximately 5–10 university Vehicles
- One web application and one relational database
- Browser-based GPS collection from an assigned phone
- Live monitoring through periodic polling
- Historical Trip playback
- No native application requirement

### Why a modular monolith?

A modular monolith provides clear responsibility boundaries without introducing the deployment, networking, monitoring, and synchronisation overhead associated with distributed services. Each Django application remains independently testable, while the complete system is deployed as one unit.

---

## 3. High-Level System Context

```text
Driver Phone Browser
        |
        | HTTPS GPS POST
        v
Django Backend
(Authentication, Permissions, Services, REST API, ORM)
        |
        | Django ORM / psycopg
        v
Supabase PostgreSQL
        ^
        |
Admin Dashboard and Public Dashboard
```

### Primary runtime flow

1. The Driver opens the tracker page on the assigned phone.
2. Django verifies the authenticated session.
3. The browser requests GPS permission.
4. The browser collects latitude, longitude, speed, accuracy, and capture time.
5. The browser submits the Location through HTTPS.
6. Django finds the Driver's active Vehicle assignment.
7. Django validates and stores the Location under an active Trip.
8. Admin and Public dashboards poll the latest-location endpoints.
9. Django returns role-appropriate JSON.
10. Leaflet updates the relevant Vehicle marker.

---

## 4. System Responsibility Boundaries

### 4.1 Django application backend

Django owns:

- Authentication and session management
- Role-based authorisation
- Driver-to-Vehicle assignment validation
- Business rules
- REST API endpoints
- Input validation
- Transactions
- ORM queries
- Database migrations
- Django administration
- Template rendering
- Security controls

### 4.2 Supabase database service

Supabase owns:

- Hosted PostgreSQL
- Database persistence
- PostgreSQL connection endpoints
- Supported connection-pooling options

> **Strict boundary:** The Driver, Admin, and Public frontend clients will never connect directly to Supabase. All application data access passes through Django.

The MVP will not use:

- Supabase Auth
- Supabase Realtime
- Supabase Data API as the application data-access path
- Supabase frontend client libraries
- A second authorisation system

### 4.3 Render application host

Render will host:

- One Gunicorn process serving Django
- Production environment variables
- HTTPS termination
- Static assets delivered through WhiteNoise

---

## 5. Django Module Design

The backend will use four focused Django applications:

```text
apps/
|-- accounts/
|-- fleet/
|-- tracking/
`-- web/
```

### 5.1 `accounts`

Responsible for:

- User authentication
- Driver profiles
- Admin and Driver Groups
- Login and logout
- Persistent sessions
- Permission helpers

Must not own:

- Vehicle business logic
- GPS storage logic
- Trip-history queries

### 5.2 `fleet`

Responsible for:

- Vehicle records
- Driver-to-Vehicle assignments
- Vehicle activation and deactivation
- Driver assignment history
- Fleet administration

Must not own:

- Authentication implementation
- Location ingestion
- Trip-history rendering

### 5.3 `tracking`

Responsible for:

- GPS Location ingestion
- Location validation
- Latest-location queries
- Trip lifecycle
- Trip-history queries
- Tracking REST API

This is the central backend domain application.

### 5.4 `web`

Responsible for:

- Driver tracker page
- Admin dashboard page
- Public dashboard page
- Trip-history page
- Template views

The `web` application contains presentation logic only. Domain logic belongs to `accounts`, `fleet`, or `tracking`.

---

## 6. Final Repository and File Structure

```text
Vehicle_Tracking/
|-- .github/
|   |-- workflows/
|   |   `-- ci.yml
|   `-- pull_request_template.md
|
|-- apps/
|   |-- accounts/
|   |   |-- migrations/
|   |   |-- tests/
|   |   |   |-- test_authentication.py
|   |   |   `-- test_permissions.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- permissions.py
|   |   |-- services.py
|   |   |-- urls.py
|   |   `-- views.py
|   |
|   |-- fleet/
|   |   |-- migrations/
|   |   |-- tests/
|   |   |   |-- test_models.py
|   |   |   |-- test_selectors.py
|   |   |   `-- test_services.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- selectors.py
|   |   `-- services.py
|   |
|   |-- tracking/
|   |   |-- api/
|   |   |   |-- permissions.py
|   |   |   |-- serializers.py
|   |   |   |-- urls.py
|   |   |   `-- views.py
|   |   |-- migrations/
|   |   |-- tests/
|   |   |   |-- test_location_api.py
|   |   |   |-- test_trip_api.py
|   |   |   |-- test_permissions.py
|   |   |   |-- test_selectors.py
|   |   |   `-- test_services.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- selectors.py
|   |   |-- services.py
|   |   `-- validators.py
|   |
|   `-- web/
|       |-- tests/
|       |-- apps.py
|       |-- urls.py
|       `-- views.py
|
|-- config/
|   |-- settings/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- development.py
|   |   |-- test.py
|   |   `-- production.py
|   |-- asgi.py
|   |-- urls.py
|   `-- wsgi.py
|
|-- docs/
|   |-- architecture.md
|   |-- api-contract.md
|   |-- decisions.md
|   `-- testing.md
|
|-- requirements/
|   |-- base.txt
|   |-- development.txt
|   `-- production.txt
|
|-- static/
|   |-- css/
|   |   `-- app.css
|   `-- js/
|       |-- tracker.js
|       |-- admin-map.js
|       |-- public-map.js
|       `-- trip-history.js
|
|-- templates/
|   |-- accounts/
|   |   |-- admin_login.html
|   |   `-- driver_login.html
|   |-- dashboard/
|   |   `-- admin_dashboard.html
|   |-- public/
|   |   `-- vehicle_map.html
|   |-- tracker/
|   |   `-- tracker.html
|   |-- trips/
|   |   `-- trip_history.html
|   `-- base.html
|
|-- .editorconfig
|-- .env.example
|-- .gitattributes
|-- .gitignore
|-- manage.py
|-- pyproject.toml
|-- README.md
`-- PRD_Vehicle_Tracking.md
```

---

## 7. Backend Layering Rules

Every request follows one direction:

```text
URL
  -> View or API View
  -> Authentication
  -> Permission
  -> Serializer or Form Validation
  -> Service or Selector
  -> Django ORM
  -> PostgreSQL
  -> Response
```

### 7.1 Services

Services perform state-changing operations:

```python
assign_driver_to_vehicle(...)
deactivate_vehicle(...)
record_vehicle_location(...)
open_trip(...)
close_trip(...)
```

### 7.2 Selectors

Selectors perform read-only database operations:

```python
get_active_vehicles(...)
get_latest_vehicle_location(...)
get_latest_active_vehicle_locations(...)
get_vehicle_trips(...)
get_trip_points(...)
```

### 7.3 Validators

Validators enforce reusable domain rules:

```python
validate_coordinates(...)
validate_speed(...)
validate_capture_timestamp(...)
validate_active_assignment(...)
```

### 7.4 View restrictions

Views will not:

- Contain complex database queries
- Implement Trip lifecycle rules
- Assign Drivers directly
- Duplicate validation logic
- Duplicate permission logic

---

## 8. Authentication and Authorisation

The MVP will use:

- Django User accounts
- Django Groups for Admin and Driver roles
- Django `is_superuser` for technical Superuser access
- Anonymous read-only access for Public Viewer
- Django session authentication
- CSRF protection for state-changing requests

JWT is intentionally excluded because all clients are served by the same Django application. Session authentication minimises unnecessary credential and token-management complexity.

### Permission matrix

| Capability | Admin | Driver | Viewer | Superuser |
| --- | ---: | ---: | ---: | ---: |
| Login | Yes | Yes | Not required | Yes |
| Admin dashboard | Yes | No | No | Yes |
| Driver tracker | No | Assigned Driver only | No | Yes |
| Submit GPS data | No | Assigned Vehicle only | No | Yes |
| View public map | Yes | Yes | Yes | Yes |
| Manage Vehicles | Yes | No | No | Yes |
| Manage Drivers | Yes | No | No | Yes |
| Review Trip history | Yes | No | No | Yes |
| Django admin | Staff Admin only | No | No | Yes |

### Critical assignment rule

The Driver client will not provide an authoritative Vehicle identity.

The backend resolves:

```text
Authenticated User
    -> DriverProfile
    -> Active DriverAssignment
    -> Vehicle
```

This prevents one Driver from submitting Location records for another Vehicle.

---

## 9. Data Model

### 9.1 `DriverProfile`

| Field | Type | Purpose |
| --- | --- | --- |
| `user` | One-to-one Django User | Authentication identity |
| `employee_id` | Unique text, optional | University identifier |
| `phone_number` | Text, optional | Administrative contact |
| `is_active` | Boolean | Soft account status |
| `created_at` | DateTime | Creation audit value |
| `updated_at` | DateTime | Modification audit value |

### 9.2 `Vehicle`

| Field | Type | Purpose |
| --- | --- | --- |
| `bus_number` | Unique text | User-facing Vehicle identity |
| `registration_number` | Unique text, optional | Registration identity |
| `route_label` | Text | Descriptive metadata only |
| `is_active` | Boolean | Live-fleet inclusion status |
| `created_at` | DateTime | Creation audit value |
| `updated_at` | DateTime | Modification audit value |

`route_label` is descriptive metadata only. Dynamic Route management is outside the MVP.

### 9.3 `DriverAssignment`

| Field | Type | Purpose |
| --- | --- | --- |
| `driver` | Foreign key to DriverProfile | Assigned Driver |
| `vehicle` | Foreign key to Vehicle | Assigned Vehicle |
| `starts_at` | DateTime | Assignment start |
| `ends_at` | DateTime, nullable | Assignment end |
| `is_active` | Boolean | Current assignment status |
| `created_at` | DateTime | Creation audit value |

A separate DriverAssignment entity:

- Preserves assignment history
- Supports reassignment
- Maintains accurate historical responsibility
- Keeps Driver and Vehicle lifecycles independent

### 9.4 `Trip`

| Field | Type | Purpose |
| --- | --- | --- |
| `vehicle` | Protected foreign key | Vehicle used for the Trip |
| `driver` | Protected foreign key | Driver operating the Vehicle |
| `started_at` | DateTime | Trip start |
| `ended_at` | DateTime, nullable | Trip end |
| `status` | Choice | `OPEN` or `COMPLETED` |
| `created_at` | DateTime | Creation audit value |
| `updated_at` | DateTime | Modification audit value |

### 9.5 `Location`

| Field | Type | Purpose |
| --- | --- | --- |
| `vehicle` | Protected foreign key | Vehicle identity |
| `driver` | Protected foreign key | Submitting Driver |
| `trip` | Protected foreign key | Parent Trip |
| `latitude` | Decimal | GPS latitude |
| `longitude` | Decimal | GPS longitude |
| `speed_kmh` | Decimal, nullable | Reported speed |
| `accuracy_m` | Decimal, nullable | GPS accuracy |
| `captured_at` | DateTime | Device capture time |
| `received_at` | DateTime | Server receipt time |
| `client_event_id` | Unique UUID | Retry and duplication protection |

`accuracy_m`, `received_at`, and `client_event_id` are technical reliability fields, not new user-facing features.

### 9.6 Entity relationships

```text
Django User 1 ---- 1 DriverProfile
DriverProfile 1 ---- N DriverAssignment
Vehicle 1 ---- N DriverAssignment
DriverProfile 1 ---- N Trip
Vehicle 1 ---- N Trip
Trip 1 ---- N Location
Vehicle 1 ---- N Location
DriverProfile 1 ---- N Location
```

---

## 10. Database Constraints and Indexes

### Required constraints

- Latitude must be between `-90` and `90`.
- Longitude must be between `-180` and `180`.
- Speed must be null or non-negative.
- Accuracy must be null or non-negative.
- Each `client_event_id` must be unique.
- A Driver can have at most one active assignment.
- A Vehicle can have at most one active Driver assignment.
- A Vehicle can have at most one open Trip.
- Completed Trips cannot receive new Locations.

### Required indexes

```text
Location(vehicle, captured_at DESC)
Location(trip, captured_at ASC)
Trip(vehicle, started_at DESC)
Trip(vehicle, status)
DriverAssignment(driver, is_active)
DriverAssignment(vehicle, is_active)
```

---

## 11. Versioned REST API Contract

All API routes begin with:

```text
/api/v1/
```

### 11.1 Submit Driver Location

```http
POST /api/v1/locations/
```

Authentication requirement:

```text
Authenticated Driver with an active Vehicle assignment
```

Example request:

```json
{
  "client_event_id": "20fb4ce3-3795-4f19-b35d-62788922de25",
  "latitude": 22.471234,
  "longitude": 91.789456,
  "speed_kmh": 24.5,
  "accuracy_m": 8.0,
  "captured_at": "2026-08-09T10:20:15Z"
}
```

The backend derives:

- Driver from `request.user`
- Vehicle from the active DriverAssignment
- Trip from the current open Trip

The browser does not provide authoritative Driver or Vehicle identifiers.

### 11.2 Latest active Vehicle locations

```http
GET /api/v1/vehicles/latest-locations/
```

Used by:

- Admin dashboard
- Public dashboard

### 11.3 Latest Location of one Vehicle

```http
GET /api/v1/vehicles/{vehicle_id}/latest-location/
```

### 11.4 Trip list

```http
GET /api/v1/trips/?vehicle_id=3&date=2026-08-09
```

Admin access only.

### 11.5 Trip points

```http
GET /api/v1/trips/{trip_id}/points/?start=08:00&end=10:00
```

Admin access only. Points are returned in ascending `captured_at` order.

### Public response boundary

Public responses exclude:

- Driver contact details
- Login username
- Email address
- Internal assignment identifiers

---

## 12. Trip Lifecycle

### 12.1 Opening a Trip

A Trip opens when:

1. The Driver is authenticated.
2. An active DriverAssignment exists.
3. The assigned Vehicle is active.
4. No Trip is currently open for the Vehicle.
5. The first valid Location is received.

### 12.2 Continuing a Trip

Every accepted Location is attached to the current open Trip.

### 12.3 Closing a Trip

A Trip closes when:

- The Driver logs out.
- A configurable period passes without receiving a valid Location.
- An authorised Admin closes an invalid open Trip.

The inactivity threshold will be configuration, not a hard-coded architectural value.

This prevents Trips from remaining permanently open if:

- The browser closes unexpectedly.
- Mobile data disappears.
- The phone battery dies.
- The Driver forgets to log out.

---

## 13. Supabase PostgreSQL Integration

```text
Django ORM
    -> psycopg PostgreSQL driver
    -> encrypted PostgreSQL connection
    -> Supabase PostgreSQL
```

### Environment configuration

```env
DATABASE_URL=postgresql://...
```

The real credential will exist only in:

- Local `.env`
- Render environment settings
- CI secret storage, if required

The credential must never be committed.

### Schema ownership

Django migrations are the only source of application schema changes:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations --check --dry-run
```

The Supabase dashboard will not be used to create competing application schemas.

### Connection decision

Before production deployment, the team will verify:

1. Whether Render can use the Supabase direct PostgreSQL endpoint.
2. If direct connectivity is unsuitable, whether the Supabase session-mode pooler is required for persistent application traffic.

---

## 14. Deployment Topology

```text
Internet Clients over HTTPS
            |
            v
Render Web Service
            |
            v
Gunicorn
            |
            v
Django Application
    |               |
    |               `-> Static files through WhiteNoise
    |
    `-> Supabase PostgreSQL
```

One Render web service is sufficient for the MVP.

No additional worker, Redis, Celery, or WebSocket service is required.

---

## 15. Security Baseline

- Authentication is required for Driver and Admin operations.
- Public endpoints allow safe read-only requests only.
- Session-authenticated writes require CSRF protection.
- Passwords use Django's password-hashing framework.
- Driver assignment is validated on the server.
- Arbitrary Vehicle submission by Drivers is prohibited.
- Production cookies are marked secure.
- Production traffic uses HTTPS.
- All input is validated before persistence.
- Secrets are excluded from Git.
- Public serializers exclude private Driver information.
- Direct frontend access to PostgreSQL is prohibited.

---

## 16. Testing Baseline

### Model tests

- Active assignment uniqueness
- Driver and Vehicle deactivation
- One open Trip per Vehicle
- GPS-value constraints
- Trip closure rules

### API tests

- Valid Driver Location submission
- Invalid coordinate rejection
- Anonymous Location submission rejection
- Unassigned Driver rejection
- Duplicate client-event handling
- Admin Trip-history access
- Public Trip-history denial
- Public response privacy

### Permission tests

Each protected endpoint will be tested against:

```text
Anonymous
Driver
Admin
Superuser
```

---

## 17. Implementation Sequence

| Phase | Area | Deliverable |
| ---: | --- | --- |
| 1 | Foundation | Django project, settings split, four applications, environment-variable structure, and CI foundation |
| 2 | Accounts and Fleet | Django Groups, DriverProfile, Vehicle, and DriverAssignment |
| 3 | Tracking Models | Trip, Location, constraints, indexes, and migrations |
| 4 | Access Control | Login, logout, persistent sessions, permissions, and Django admin |
| 5 | Location Ingestion | Validation, Location service, POST endpoint, and duplicate-event protection |
| 6 | Live Queries | Latest-location selectors, Admin representation, and Public representation |
| 7 | Trip History | Trip list endpoint, Trip points endpoint, and chronological retrieval |
| 8 | Quality and Deployment | Integration tests, Supabase connection, production settings, and Render deployment |

---

## 18. Primary Technical Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Mobile browser suspends tracking | Missing GPS records | Do not promise unrestricted background tracking; test active-session behaviour on target Android browsers |
| Driver forgets to log out | Trip remains open | Close Trips after configurable Location inactivity |
| Duplicate GPS retry | Duplicate historical points | Use unique `client_event_id` |
| Incorrect Vehicle submission | Corrupted tracking ownership | Resolve Vehicle through the authenticated DriverAssignment |
| Public information exposure | Privacy issue | Use separate Public and Admin serializers |
| Supabase connection incompatibility | Deployment failure | Validate direct connection, then use session-mode pooling if required |
| Excessive scope | Missed MVP deadline | Implement Must requirements before Should requirements |

---

## 19. Architectural Decisions Requested for Approval

- [ ] **AD-01:** Modular Django monolith
- [ ] **AD-02:** Four applications: `accounts`, `fleet`, `tracking`, and `web`
- [ ] **AD-03:** Django session authentication instead of JWT
- [ ] **AD-04:** Django Groups and DRF permissions
- [ ] **AD-05:** Supabase used only as hosted PostgreSQL
- [ ] **AD-06:** No direct frontend-to-Supabase access
- [ ] **AD-07:** Separate DriverAssignment model
- [ ] **AD-08:** Trip and append-only Location history
- [ ] **AD-09:** Versioned API under `/api/v1/`
- [ ] **AD-10:** HTTP polling instead of WebSockets
- [ ] **AD-11:** Render as the Django deployment target
- [ ] **AD-12:** Proposed repository structure

> **Requested outcome:** Approval to freeze the listed architecture boundaries and begin implementation. Any later change to an approved boundary should be recorded in `docs/decisions.md`.

---

## 20. Backend Definition of Ready

Implementation may begin when:

- [ ] Architecture style is approved.
- [ ] Django modules are approved.
- [ ] Data entities and relationships are approved.
- [ ] DriverAssignment is approved.
- [ ] Trip lifecycle is approved.
- [ ] API boundaries are approved.
- [ ] Supabase database-only boundary is approved.
- [ ] Render deployment target is approved.
- [ ] File structure is approved.
- [ ] Relevant PRD Scope, Architecture, and Data Model sections will be updated from the approved decisions.

---

## 21. Closing Recommendation

The proposed backend is a modular Django monolith with PostgreSQL hosted on Supabase. Django remains the sole application backend and controls authentication, permissions, validation, business rules, and migrations.

The Driver phone sends GPS data only through authenticated Django endpoints. Admin and Public dashboards receive role-appropriate data through versioned REST APIs. The design fulfils the finalised MVP requirements without introducing microservices, WebSockets, native applications, or duplicate Supabase authentication.

**Approval is requested to freeze these boundaries and begin implementation using the proposed file structure.**

---

## Appendix A. Short Presentation Script

> Sir, we propose a modular Django monolith for CU-VTS. Django will be the sole application backend, while Supabase will only host PostgreSQL.
>
> The Driver's assigned Android phone will send GPS coordinates through authenticated Django REST endpoints. The backend will validate the Driver's active Vehicle assignment before saving any Location. Admin and Public dashboards will retrieve role-appropriate data through versioned APIs and periodic polling.
>
> The backend is divided into `accounts`, `fleet`, `tracking`, and `web` modules. The primary entities are DriverProfile, Vehicle, DriverAssignment, Trip, and Location. A separate DriverAssignment model preserves assignment history, while append-only Location records support current-location viewing and Trip-history playback.
>
> We are deliberately excluding microservices, WebSockets, Supabase Auth, native applications, and direct frontend database access. This keeps the architecture achievable for the three-member team and the MVP deadline.
>
> We request approval to freeze these architectural boundaries and begin implementation with the proposed file structure.

---

## Appendix B. Technical References

- [Django 5.2 release notes](https://docs.djangoproject.com/en/6.0/releases/5.2/)
- [Django authentication system](https://docs.djangoproject.com/en/6.0/ref/contrib/auth/)
- [Django REST Framework authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [Django REST Framework permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [Supabase PostgreSQL connection guidance](https://supabase.com/docs/guides/database/connecting-to-postgres)
````

## `Procfile`

- **Folder:** `./ (project root)`
- **File:** `Procfile`

```text
# Process definitions for Procfile-based hosts (Railway, Heroku-style PaaS).
# Render uses render.yaml instead, but this keeps the app portable.
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread --timeout 60 --graceful-timeout 30 --access-logfile - --error-logfile -
release: python manage.py migrate --no-input
```

## `README.md`

- **Folder:** `./ (project root)`
- **File:** `README.md`

````markdown
# CU-VTS — Campus Vehicle Tracking System

A modular Django monolith for **live campus bus tracking**. Drivers stream GPS
fixes from their phones; anyone can watch the fleet move on a public map; admins
review trip history and manage the fleet. Designed to deploy **100% free** on
Render (web) + Supabase (Postgres), and to run just as well locally on SQLite.

- **Public map** — live vehicle positions, no login required (driver identity hidden).
- **Driver tracker** — one-tap "go live" that streams location to the server.
- **Admin dashboard** — fleet overview, live map, and historical trip playback.
- **Versioned REST API** (`/api/v1/`) — session-authenticated, deny-by-default,
  rate-limited, with a privacy boundary between public and admin views.

> **New here?** Read [`docs/architecture.md`](docs/architecture.md) for the design,
> [`docs/api-contract.md`](docs/api-contract.md) for the endpoints, and
> [`docs/decisions.md`](docs/decisions.md) for the *why* behind the big choices.

---

## Table of contents

- [Tech stack](#tech-stack)
- [Quick start (local)](#quick-start-local)
- [Configuration](#configuration)
- [Management commands](#management-commands)
- [Quality gates](#quality-gates)
- [Project layout](#project-layout)
- [Deployment (free tier)](#deployment-free-tier)
- ["Can the templates run on Cloudflare Pages?"](#can-the-templates-run-on-cloudflare-pages)
- [Security overview](#security-overview)
- [License](#license)

---

## Tech stack

| Layer            | Choice                                                        |
|------------------|---------------------------------------------------------------|
| Language/runtime | Python **3.13.1**                                             |
| Framework        | **Django 5.2 LTS**, **Django REST Framework**                 |
| Auth             | Django sessions + Groups (`Admin`, `Driver`), `django-axes`   |
| Database         | **PostgreSQL** (Supabase) in prod · SQLite in dev/test        |
| Static files     | **WhiteNoise** (compressed, cache-busted) — served in-process |
| App server       | **Gunicorn** (`gthread` worker)                               |
| Frontend         | Server-rendered templates + **Bootstrap 5** + **Leaflet** (self-hosted); OpenStreetMap tiles |
| Config           | `python-decouple` (12-factor env vars)                        |
| Tooling          | `ruff`, `mypy` + `django-stubs`, `pytest` + `pytest-django`   |

No build step, no Node toolchain, no SPA — the browser assets are vendored under
`static/vendor/` and served by Django itself.

---

## Quick start (local)

Requires Python 3.13.

```bash
# 1. Create and activate a virtualenv
python3.13 -m venv .venv
source .venv/bin/activate

# 2. Install dev dependencies (includes prod deps + test/lint tooling)
pip install -r requirements/development.txt

# 3. Configure the environment
cp .env.example .env          # defaults are dev-ready; leave DATABASE_URL empty for SQLite

# 4. Create the database schema
python manage.py migrate

# 5. Seed demo users, vehicles and live trips (prints a one-time admin password)
python manage.py create_demo_data

# 6. Run it
python manage.py runserver
```

Then visit:

| URL                 | Who        | What                                            |
|---------------------|------------|-------------------------------------------------|
| `/`                 | Everyone   | Public live map                                 |
| `/driver-login/`    | Drivers    | Log in → `/tracker/` to broadcast location      |
| `/admin-login/`     | Admins     | Log in → `/dashboard/` (fleet + live map)       |
| `/trips/`           | Admins     | Historical trip playback                        |
| `/healthz`          | —          | Liveness probe (returns `ok`)                   |
| `/django-admin/`    | Superusers | Django admin (path is configurable, see below)  |

The `create_demo_data` command creates an `admin` account (and `driver1…N`) and
prints each generated password **once** — copy it from the console.

---

## Configuration

All settings come from environment variables (or a local `.env`). The three
settings modules layer on a shared base:

- `config.settings.development` — `DEBUG=True`, SQLite, browsable API. *(manage.py default)*
- `config.settings.test` — SQLite in-memory, fast hashing, throttling/axes off.
- `config.settings.production` — `DEBUG=False`, HTTPS/HSTS, secure cookies, Postgres. *(wsgi.py default)*

[`.env.example`](.env.example) documents **every** variable with inline notes.
The ones you are most likely to touch:

| Variable                | Purpose                                                              |
|-------------------------|----------------------------------------------------------------------|
| `SECRET_KEY`            | **Mandatory in production** (no fallback). 50+ random chars.          |
| `DATABASE_URL`          | Supabase Postgres URL. Empty ⇒ local SQLite.                         |
| `ALLOWED_HOSTS`         | Extra hostnames (Render's is auto-added in prod).                    |
| `ADMIN_URL_PREFIX`      | Obscures the admin path (default `django-admin/`).                   |
| `THROTTLE_*`            | API rate limits (ingest / public read).                             |
| `TRIP_INACTIVITY_MINUTES`, `LOCATION_*` | Trip-lifecycle and staleness tuning.                |

---

## Management commands

```bash
python manage.py create_demo_data          # idempotent seed: admin, drivers, vehicles, live trips
python manage.py create_demo_data --drivers 4 --vehicles 6 --points 10
python manage.py close_stale_trips          # close trips idle past TRIP_INACTIVITY_MINUTES (cron-friendly)
```

`create_demo_data` is safe to re-run — existing objects are reused, never
duplicated. Run `close_stale_trips` from a scheduled job (e.g. a Render cron)
to auto-close trips a driver forgot to end.

---

## Quality gates

The project ships green across four gates. Run them all before pushing:

```bash
ruff check .                 # lint
ruff format --check .        # formatting
mypy .                       # static types (django-stubs)
pytest                       # test suite (104 tests)
pytest --cov=apps --cov-report=term-missing   # with coverage
```

Domain layers (services, selectors, validators, permissions, serializers, API &
web views) sit at **89–100%** coverage. See [`docs/testing.md`](docs/testing.md).

Before a release, also run the production deploy check:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production SECRET_KEY=$(python -c \
  'from django.core.management.utils import get_random_secret_key as k; print(k())') \
  python manage.py check --deploy
```

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the same gates
on every push and pull request.

---

## Project layout

```
config/                     Project config
  settings/                 base.py + development/test/production
  urls.py  middleware.py  wsgi.py  asgi.py
apps/
  accounts/                 Users, roles, DriverProfile, auth views, permissions
  fleet/                    Vehicles, driver↔vehicle assignments
  tracking/                 Locations, trips, ingestion, staleness
    api/                    DRF serializers, permissions, views, urls (/api/v1/)
    management/commands/    create_demo_data, close_stale_trips
  web/                      Server-rendered pages (map, dashboard, tracker, history)
templates/                  base.html + per-app templates
static/                     app CSS/JS + vendored Bootstrap & Leaflet
requirements/               base.txt · development.txt · production.txt
docs/                       architecture · api-contract · decisions · testing
render.yaml  build.sh  Procfile  runtime.txt   Deployment
```

Each app follows the same internal layering — **models → validators → services
(writes) → selectors (reads)** — so business rules live in one obvious place.
Full detail in [`docs/architecture.md`](docs/architecture.md).

---

## Deployment (free tier)

The entire app runs as **one Render free web service** backed by **Supabase's
free Postgres**. Nothing else is required.

1. Push this repo to GitHub.
2. In Render: **New + → Blueprint**, point it at the repo. [`render.yaml`](render.yaml)
   provisions the web service, generates `SECRET_KEY`, sets
   `DJANGO_SETTINGS_MODULE=config.settings.production`, and wires the
   `/healthz` health check. [`build.sh`](build.sh) installs deps, runs
   `collectstatic`, and applies migrations on every deploy.
3. Create a free Supabase project and set `DATABASE_URL` in the Render service
   to its **session-mode pooler** URL (port 5432).
4. First deploy done — open a shell and run `python manage.py create_demo_data`
   (or create your own admin) to get started.

WhiteNoise serves all CSS/JS/vendor assets from within the Django process, so
there is **no separate static host to configure**. A step-by-step operator
manual can be generated separately (see below).

---

## "Can the templates run on Cloudflare Pages?"

**No — and they don't need to.** Cloudflare Pages hosts *static* sites and edge
functions; it cannot run a long-lived Django (WSGI) process or hold pooled
PostgreSQL connections. This app's pages are **server-rendered per request**:
they depend on the session cookie (who is logged in), a CSRF token, role-based
template context, and live database reads. Those are server responsibilities,
not static assets.

The correct shape for this project is a **single service** on Render that serves
both the HTML pages and the JSON API, with WhiteNoise handling the static files
in-process. You *could* optionally put Cloudflare's CDN in front of Render for
edge caching of static assets, but Cloudflare Pages as the application host does
not apply here. See [`docs/decisions.md`](docs/decisions.md) for the full rationale.

---

## Security overview

- **Session authentication**, deny-by-default (`IsAuthenticated`) on the API;
  public endpoints opt in explicitly with `AllowAny`.
- **Role enforcement in code** (not just group membership) via permission
  predicates and DRF permission classes; wrong role → `403`, not a redirect loop.
- **Brute-force lockout** with `django-axes`.
- **Rate limiting** (DRF scoped throttles) on ingest and public reads.
- **Privacy boundary** — the public serializer omits driver identity and
  accuracy; only admins see them.
- **Idempotent ingestion** — a client-supplied `client_event_id` makes retries
  safe; a clock-skew guard rejects implausible timestamps.
- **Hardened production** — `check --deploy` passes clean: HTTPS redirect, HSTS
  (1y, preload), secure/HttpOnly/SameSite cookies, nosniff, `X-Frame-Options:
  DENY`, a Content-Security-Policy, and a configurable (obscured) admin path.

Details in [`docs/architecture.md`](docs/architecture.md#security-architecture).

---

## License

Add a license of your choice (e.g. MIT) before publishing.
````

## `apps/__init__.py`

- **Folder:** `apps/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/__init__.py`

- **Folder:** `apps/accounts/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/admin.py`

- **Folder:** `apps/accounts/`
- **File:** `admin.py`

```python
from __future__ import annotations

from django.contrib import admin

from .models import DriverProfile


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "employee_id", "phone_number", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "employee_id")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Driver")
    def display_name(self, obj: DriverProfile) -> str:
        return obj.display_name
```

## `apps/accounts/apps.py`

- **Folder:** `apps/accounts/`
- **File:** `apps.py`

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Accounts"

    def ready(self) -> None:
        # Ensure role groups exist after migrations on a fresh database.
        from . import signals  # noqa: F401
```

## `apps/accounts/context_processors.py`

- **Folder:** `apps/accounts/`
- **File:** `context_processors.py`

```python
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
```

## `apps/accounts/forms.py`

- **Folder:** `apps/accounts/`
- **File:** `forms.py`

```python
"""Authentication forms with Bootstrap-friendly widgets."""

from __future__ import annotations

from django.contrib.auth.forms import AuthenticationForm


class StyledAuthenticationForm(AuthenticationForm):
    """Standard Django login form with Bootstrap classes applied."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autofocus": True, "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "current-password"}
        )
```

## `apps/accounts/management/__init__.py`

- **Folder:** `apps/accounts/management/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/management/commands/__init__.py`

- **Folder:** `apps/accounts/management/commands/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/management/commands/seed_roles.py`

- **Folder:** `apps/accounts/management/commands/`
- **File:** `seed_roles.py`

```python
"""Create the Admin and Driver role groups. Idempotent."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the Admin and Driver role groups if they do not exist."

    def handle(self, *args, **options) -> None:
        for name in (settings.ADMIN_GROUP, settings.DRIVER_GROUP):
            _, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "exists"
            self.stdout.write(f"Group {name!r}: {status}")
        self.stdout.write(self.style.SUCCESS("Role groups are ready."))
```

## `apps/accounts/migrations/0001_initial.py`

- **Folder:** `apps/accounts/migrations/`
- **File:** `0001_initial.py`

```python
# Generated by Django 5.2.17 on 2026-08-16 07:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='driver_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Driver profile',
                'verbose_name_plural': 'Driver profiles',
                'ordering': ['user__username'],
            },
        ),
    ]
```

## `apps/accounts/migrations/__init__.py`

- **Folder:** `apps/accounts/migrations/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/models.py`

- **Folder:** `apps/accounts/`
- **File:** `models.py`

```python
"""Accounts models.

The MVP uses Django's built-in ``User`` for authentication and attaches a
one-to-one ``DriverProfile`` for driver-specific attributes. There is no custom
user model, keeping authentication conventional and low-risk.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class DriverProfile(models.Model):
    """Driver-specific data attached to a Django ``User``."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Driver profile"
        verbose_name_plural = "Driver profiles"
        ordering = ["user__username"]

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        """Human-friendly name for dashboards (never exposes username/email)."""
        full = self.user.get_full_name().strip()
        return full or self.user.get_username()
```

## `apps/accounts/permissions.py`

- **Folder:** `apps/accounts/`
- **File:** `permissions.py`

```python
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
```

## `apps/accounts/services.py`

- **Folder:** `apps/accounts/`
- **File:** `services.py`

```python
"""Account services: state-changing operations for users and driver profiles."""

from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.db import transaction

from .models import DriverProfile


@transaction.atomic
def create_driver(
    *,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    employee_id: str | None = None,
    phone_number: str = "",
) -> DriverProfile:
    """Create a User in the Driver group with an attached DriverProfile."""
    from django.conf import settings

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    driver_group, _ = Group.objects.get_or_create(name=settings.DRIVER_GROUP)
    user.groups.add(driver_group)
    return DriverProfile.objects.create(
        user=user,
        employee_id=employee_id or None,
        phone_number=phone_number,
    )


@transaction.atomic
def deactivate_driver(profile: DriverProfile) -> DriverProfile:
    """Soft-deactivate a driver and disable login without deleting history."""
    profile.is_active = False
    profile.save(update_fields=["is_active", "updated_at"])
    user = profile.user
    user.is_active = False
    user.save(update_fields=["is_active"])
    return profile
```

## `apps/accounts/signals.py`

- **Folder:** `apps/accounts/`
- **File:** `signals.py`

```python
"""Signals that keep role groups present on any freshly migrated database."""

from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_role_groups(sender, **kwargs) -> None:
    """Create the Admin and Driver groups if they do not yet exist.

    Runs after this app's migrations so the auth tables are available.
    """
    if getattr(sender, "label", None) != "accounts":
        return

    from django.contrib.auth.models import Group

    for group_name in (settings.ADMIN_GROUP, settings.DRIVER_GROUP):
        Group.objects.get_or_create(name=group_name)
```

## `apps/accounts/tests/__init__.py`

- **Folder:** `apps/accounts/tests/`
- **File:** `__init__.py`

```python

```

## `apps/accounts/tests/test_authentication.py`

- **Folder:** `apps/accounts/tests/`
- **File:** `test_authentication.py`

```python
"""Authentication flow tests: role-aware login, logout, trip closing."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.views import role_landing_url
from apps.tracking.models import Trip, TripStatus

pytestmark = pytest.mark.django_db


def test_role_landing_url_by_role(admin_user, driver_user):
    from django.contrib.auth.models import AnonymousUser

    assert str(role_landing_url(admin_user)) == reverse("web:admin_dashboard")
    assert str(role_landing_url(driver_user)) == reverse("web:tracker")
    assert str(role_landing_url(AnonymousUser())) == reverse("web:public_map")


def test_admin_login_page_renders(client):
    resp = client.get(reverse("accounts:admin_login"))
    assert resp.status_code == 200
    assert "accounts/admin_login.html" in [t.name for t in resp.templates]


def test_admin_login_redirects_to_dashboard(client, admin_user, password):
    resp = client.post(
        reverse("accounts:admin_login"),
        {"username": admin_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("web:admin_dashboard")


def test_driver_login_redirects_to_tracker(client, driver_user, password):
    resp = client.post(
        reverse("accounts:driver_login"),
        {"username": driver_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("web:tracker")


def test_login_respects_safe_next(client, admin_user, password):
    target = reverse("web:trip_history")
    resp = client.post(
        reverse("accounts:admin_login") + f"?next={target}",
        {"username": admin_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp.url == target


def test_logout_requires_post(client, driver_user):
    client.force_login(driver_user)
    assert client.get(reverse("accounts:logout")).status_code == 405


def test_logout_closes_open_trip_and_redirects(client, driver_user, open_trip):
    client.force_login(driver_user)
    resp = client.post(reverse("accounts:logout"))
    assert resp.status_code == 302
    assert resp.url == reverse("web:public_map")

    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED
    assert open_trip.ended_at is not None


def test_logout_without_open_trip_is_safe(client, driver_user):
    client.force_login(driver_user)
    resp = client.post(reverse("accounts:logout"))
    assert resp.status_code == 302
    assert not Trip.objects.filter(status=TripStatus.OPEN).exists()
```

## `apps/accounts/tests/test_permissions.py`

- **Folder:** `apps/accounts/tests/`
- **File:** `test_permissions.py`

```python
"""Role-predicate and mixin authorisation tests."""

from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Group, User

from apps.accounts.permissions import is_admin, is_driver

pytestmark = pytest.mark.django_db


def test_anonymous_is_neither_admin_nor_driver():
    anon = AnonymousUser()
    assert is_admin(anon) is False
    assert is_driver(anon) is False


def test_admin_group_member_is_admin(admin_user):
    assert is_admin(admin_user) is True
    assert is_driver(admin_user) is False


def test_superuser_is_admin(superuser):
    assert is_admin(superuser) is True


def test_active_driver_is_driver(driver_user):
    assert is_driver(driver_user) is True
    assert is_admin(driver_user) is False


def test_inactive_driver_profile_is_not_driver(driver_profile):
    from apps.accounts.services import deactivate_driver

    deactivate_driver(driver_profile)
    driver_profile.user.refresh_from_db()
    assert is_driver(driver_profile.user) is False


def test_user_in_driver_group_without_profile_is_not_driver(driver_group):
    user = User.objects.create_user(username="ghost", password="x")
    user.groups.add(driver_group)
    assert is_driver(user) is False


def test_group_names_match_settings():
    assert Group.objects.filter(name=settings.ADMIN_GROUP).exists()
    assert Group.objects.filter(name=settings.DRIVER_GROUP).exists()
```

## `apps/accounts/tests/test_services.py`

- **Folder:** `apps/accounts/tests/`
- **File:** `test_services.py`

```python
"""Account service tests: driver creation and deactivation."""

from __future__ import annotations

import pytest
from django.conf import settings

from apps.accounts.models import DriverProfile
from apps.accounts.services import create_driver, deactivate_driver

pytestmark = pytest.mark.django_db


def test_create_driver_creates_user_group_and_profile():
    profile = create_driver(
        username="newdriver",
        password="pw-1234-strong",
        first_name="Sam",
        last_name="Road",
        employee_id="E-42",
        phone_number="+8801000000",
    )
    assert isinstance(profile, DriverProfile)
    assert profile.user.username == "newdriver"
    assert profile.user.groups.filter(name=settings.DRIVER_GROUP).exists()
    assert profile.employee_id == "E-42"
    assert profile.is_active is True
    assert profile.display_name == "Sam Road"


def test_create_driver_blank_employee_id_stored_as_null():
    profile = create_driver(username="noid", password="pw-1234-strong")
    assert profile.employee_id is None


def test_display_name_falls_back_to_username():
    profile = create_driver(username="justusername", password="pw-1234-strong")
    assert profile.display_name == "justusername"


def test_deactivate_driver_disables_profile_and_login():
    profile = create_driver(username="leaving", password="pw-1234-strong")
    deactivate_driver(profile)
    profile.refresh_from_db()
    profile.user.refresh_from_db()
    assert profile.is_active is False
    assert profile.user.is_active is False
```

## `apps/accounts/urls.py`

- **Folder:** `apps/accounts/`
- **File:** `urls.py`

```python
"""Authentication URLs (login/logout) owned by the accounts app."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("admin-login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("driver-login/", views.DriverLoginView.as_view(), name="driver_login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
```

## `apps/accounts/views.py`

- **Folder:** `apps/accounts/`
- **File:** `views.py`

```python
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
```

## `apps/fleet/__init__.py`

- **Folder:** `apps/fleet/`
- **File:** `__init__.py`

```python

```

## `apps/fleet/admin.py`

- **Folder:** `apps/fleet/`
- **File:** `admin.py`

```python
from __future__ import annotations

from django.contrib import admin
from django.utils import timezone

from .models import DriverAssignment, Vehicle
from .services import deactivate_vehicle, end_assignment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("bus_number", "registration_number", "route_label", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("bus_number", "registration_number", "route_label")
    readonly_fields = ("created_at", "updated_at")
    actions = ("action_deactivate",)

    @admin.action(description="Deactivate selected vehicles (ends active assignment)")
    def action_deactivate(self, request, queryset) -> None:
        for vehicle in queryset:
            deactivate_vehicle(vehicle)
        self.message_user(request, f"Deactivated {queryset.count()} vehicle(s).")


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("driver", "vehicle", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active",)
    search_fields = (
        "driver__user__username",
        "driver__user__first_name",
        "driver__user__last_name",
        "vehicle__bus_number",
    )
    autocomplete_fields = ("driver", "vehicle")
    readonly_fields = ("created_at",)
    actions = ("action_end",)

    def get_changeform_initial_data(self, request) -> dict:
        return {"starts_at": timezone.now()}

    @admin.action(description="End selected assignments")
    def action_end(self, request, queryset) -> None:
        for assignment in queryset:
            end_assignment(assignment)
        self.message_user(request, f"Ended {queryset.count()} assignment(s).")
```

## `apps/fleet/apps.py`

- **Folder:** `apps/fleet/`
- **File:** `apps.py`

```python
from django.apps import AppConfig


class FleetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fleet"
    label = "fleet"
    verbose_name = "Fleet"
```

## `apps/fleet/migrations/0001_initial.py`

- **Folder:** `apps/fleet/migrations/`
- **File:** `0001_initial.py`

```python
# Generated by Django 5.2.17 on 2026-08-16 07:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_number', models.CharField(max_length=32, unique=True)),
                ('registration_number', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('route_label', models.CharField(blank=True, max_length=120)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['bus_number'],
            },
        ),
        migrations.CreateModel(
            name='DriverAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='accounts.driverprofile')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='fleet.vehicle')),
            ],
            options={
                'ordering': ['-starts_at'],
                'indexes': [models.Index(fields=['driver', 'is_active'], name='idx_assign_driver_active'), models.Index(fields=['vehicle', 'is_active'], name='idx_assign_vehicle_active')],
                'constraints': [models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('driver',), name='uniq_active_assignment_per_driver'), models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('vehicle',), name='uniq_active_assignment_per_vehicle')],
            },
        ),
    ]
```

## `apps/fleet/migrations/__init__.py`

- **Folder:** `apps/fleet/migrations/`
- **File:** `__init__.py`

```python

```

## `apps/fleet/models.py`

- **Folder:** `apps/fleet/`
- **File:** `models.py`

```python
"""Fleet models: vehicles and the driver-to-vehicle assignment history.

A separate ``DriverAssignment`` entity preserves assignment history, supports
reassignment, and keeps driver and vehicle lifecycles independent. Partial
unique constraints guarantee at most one *active* assignment per driver and
per vehicle at the database level.
"""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from apps.accounts.models import DriverProfile


class Vehicle(models.Model):
    """A university vehicle (bus) that can be tracked."""

    bus_number = models.CharField(max_length=32, unique=True)
    registration_number = models.CharField(max_length=64, unique=True, null=True, blank=True)
    # Descriptive metadata only. Dynamic route management is out of MVP scope.
    route_label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bus_number"]

    def __str__(self) -> str:
        return self.bus_number


class DriverAssignment(models.Model):
    """Links a driver to a vehicle for a period of time."""

    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="assignments")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="assignments")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["driver"],
                condition=Q(is_active=True),
                name="uniq_active_assignment_per_driver",
            ),
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(is_active=True),
                name="uniq_active_assignment_per_vehicle",
            ),
        ]
        indexes = [
            models.Index(fields=["driver", "is_active"], name="idx_assign_driver_active"),
            models.Index(fields=["vehicle", "is_active"], name="idx_assign_vehicle_active"),
        ]

    def __str__(self) -> str:
        state = "active" if self.is_active else "ended"
        return f"{self.driver} -> {self.vehicle} ({state})"
```

## `apps/fleet/selectors.py`

- **Folder:** `apps/fleet/`
- **File:** `selectors.py`

```python
"""Fleet selectors: read-only queries. No side effects."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import DriverProfile
from apps.accounts.permissions import RequestUser

from .models import DriverAssignment, Vehicle


def get_active_vehicles() -> QuerySet[Vehicle]:
    """All vehicles currently included in the live fleet."""
    return Vehicle.objects.filter(is_active=True).order_by("bus_number")


def get_active_assignment_for_driver(
    driver: DriverProfile,
) -> DriverAssignment | None:
    """The driver's single active assignment, or None."""
    return (
        DriverAssignment.objects.select_related("vehicle", "driver__user")
        .filter(driver=driver, is_active=True)
        .first()
    )


def get_active_assignment_for_user(
    user: RequestUser,
) -> DriverAssignment | None:
    """Resolve an authenticated user to their active assignment.

    Returns None if the user has no driver profile or no active assignment.
    This is the authoritative driver -> vehicle resolution path.
    """
    profile = getattr(user, "driver_profile", None)
    if profile is None or not profile.is_active:
        return None
    return get_active_assignment_for_driver(profile)


def get_active_assignment_for_vehicle(vehicle: Vehicle) -> DriverAssignment | None:
    """The vehicle's single active assignment, or None."""
    return (
        DriverAssignment.objects.select_related("driver__user")
        .filter(vehicle=vehicle, is_active=True)
        .first()
    )
```

## `apps/fleet/services.py`

- **Folder:** `apps/fleet/`
- **File:** `services.py`

```python
"""Fleet services: state-changing operations for vehicles and assignments."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile

from .models import DriverAssignment, Vehicle


@transaction.atomic
def assign_driver_to_vehicle(
    *,
    driver: DriverProfile,
    vehicle: Vehicle,
    starts_at=None,
) -> DriverAssignment:
    """Assign ``driver`` to ``vehicle``, ending any conflicting active assignments.

    Because a driver and a vehicle may each have only one active assignment,
    any existing active assignment for either side is closed first, inside the
    same transaction.
    """
    now = timezone.now()
    starts_at = starts_at or now

    # Close the driver's current active assignment, if any.
    DriverAssignment.objects.filter(driver=driver, is_active=True).update(
        is_active=False, ends_at=now
    )
    # Close whatever driver currently holds this vehicle, if any.
    DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).update(
        is_active=False, ends_at=now
    )

    return DriverAssignment.objects.create(
        driver=driver,
        vehicle=vehicle,
        starts_at=starts_at,
        is_active=True,
    )


@transaction.atomic
def end_assignment(assignment: DriverAssignment) -> DriverAssignment:
    """End a single active assignment."""
    if assignment.is_active:
        assignment.is_active = False
        assignment.ends_at = timezone.now()
        assignment.save(update_fields=["is_active", "ends_at"])
    return assignment


@transaction.atomic
def deactivate_vehicle(vehicle: Vehicle) -> Vehicle:
    """Remove a vehicle from the live fleet and end its active assignment."""
    now = timezone.now()
    DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).update(
        is_active=False, ends_at=now
    )
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active", "updated_at"])
    return vehicle


@transaction.atomic
def activate_vehicle(vehicle: Vehicle) -> Vehicle:
    """Return a vehicle to the live fleet."""
    vehicle.is_active = True
    vehicle.save(update_fields=["is_active", "updated_at"])
    return vehicle
```

## `apps/fleet/tests/__init__.py`

- **Folder:** `apps/fleet/tests/`
- **File:** `__init__.py`

```python

```

## `apps/fleet/tests/test_models.py`

- **Folder:** `apps/fleet/tests/`
- **File:** `test_models.py`

```python
"""Fleet model constraint tests."""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.fleet.models import DriverAssignment, Vehicle

pytestmark = pytest.mark.django_db


def test_vehicle_str_is_bus_number(vehicle):
    assert str(vehicle) == "BUS-001"


def test_assignment_str_reflects_state(assignment):
    assert "active" in str(assignment)


def test_bus_number_is_unique(vehicle):
    with pytest.raises(IntegrityError), transaction.atomic():
        Vehicle.objects.create(bus_number="BUS-001")


def test_only_one_active_assignment_per_driver(driver_profile, make_vehicle):
    v1 = make_vehicle()
    v2 = make_vehicle()
    now = timezone.now()
    DriverAssignment.objects.create(driver=driver_profile, vehicle=v1, starts_at=now)
    with pytest.raises(IntegrityError), transaction.atomic():
        DriverAssignment.objects.create(driver=driver_profile, vehicle=v2, starts_at=now)


def test_only_one_active_assignment_per_vehicle(make_driver, vehicle):
    d1 = make_driver(username="d1")
    d2 = make_driver(username="d2")
    now = timezone.now()
    DriverAssignment.objects.create(driver=d1, vehicle=vehicle, starts_at=now)
    with pytest.raises(IntegrityError), transaction.atomic():
        DriverAssignment.objects.create(driver=d2, vehicle=vehicle, starts_at=now)


def test_ended_assignments_do_not_conflict(driver_profile, vehicle):
    now = timezone.now()
    DriverAssignment.objects.create(
        driver=driver_profile, vehicle=vehicle, starts_at=now, is_active=False, ends_at=now
    )
    # A second, also-ended assignment is allowed (partial constraint only guards active).
    DriverAssignment.objects.create(
        driver=driver_profile, vehicle=vehicle, starts_at=now, is_active=False, ends_at=now
    )
    assert DriverAssignment.objects.filter(is_active=False).count() == 2
```

## `apps/fleet/tests/test_selectors.py`

- **Folder:** `apps/fleet/tests/`
- **File:** `test_selectors.py`

```python
"""Fleet selector tests: read-only assignment/vehicle resolution."""

from __future__ import annotations

import pytest

from apps.fleet.selectors import (
    get_active_assignment_for_driver,
    get_active_assignment_for_user,
    get_active_assignment_for_vehicle,
    get_active_vehicles,
)

pytestmark = pytest.mark.django_db


def test_get_active_vehicles_excludes_inactive_and_orders(make_vehicle):
    b = make_vehicle(bus_number="B-2")
    a = make_vehicle(bus_number="A-1")
    inactive = make_vehicle(bus_number="Z-9", is_active=False)

    result = list(get_active_vehicles())
    assert result == [a, b]
    assert inactive not in result


def test_active_assignment_for_user_resolves(assigned_driver, vehicle):
    assignment = get_active_assignment_for_user(assigned_driver)
    assert assignment is not None
    assert assignment.vehicle == vehicle


def test_active_assignment_for_user_none_without_assignment(driver_user):
    assert get_active_assignment_for_user(driver_user) is None


def test_active_assignment_for_user_none_for_non_driver(admin_user):
    assert get_active_assignment_for_user(admin_user) is None


def test_active_assignment_for_driver_and_vehicle(assignment, driver_profile, vehicle):
    assert get_active_assignment_for_driver(driver_profile) == assignment
    assert get_active_assignment_for_vehicle(vehicle) == assignment
```

## `apps/fleet/tests/test_services.py`

- **Folder:** `apps/fleet/tests/`
- **File:** `test_services.py`

```python
"""Fleet service tests: assignment lifecycle and vehicle activation."""

from __future__ import annotations

import pytest

from apps.fleet.models import DriverAssignment
from apps.fleet.services import (
    activate_vehicle,
    assign_driver_to_vehicle,
    deactivate_vehicle,
    end_assignment,
)

pytestmark = pytest.mark.django_db


def test_assign_creates_active_assignment(driver_profile, vehicle):
    assignment = assign_driver_to_vehicle(driver=driver_profile, vehicle=vehicle)
    assert assignment.is_active is True
    assert assignment.ends_at is None


def test_reassigning_driver_closes_previous(driver_profile, make_vehicle):
    v1 = make_vehicle()
    v2 = make_vehicle()
    first = assign_driver_to_vehicle(driver=driver_profile, vehicle=v1)
    second = assign_driver_to_vehicle(driver=driver_profile, vehicle=v2)

    first.refresh_from_db()
    assert first.is_active is False
    assert first.ends_at is not None
    assert second.is_active is True
    assert DriverAssignment.objects.filter(driver=driver_profile, is_active=True).count() == 1


def test_assigning_new_driver_frees_occupied_vehicle(make_driver, vehicle):
    d1 = make_driver(username="d1")
    d2 = make_driver(username="d2")
    a1 = assign_driver_to_vehicle(driver=d1, vehicle=vehicle)
    a2 = assign_driver_to_vehicle(driver=d2, vehicle=vehicle)

    a1.refresh_from_db()
    assert a1.is_active is False
    assert a2.is_active is True
    assert DriverAssignment.objects.filter(vehicle=vehicle, is_active=True).count() == 1


def test_end_assignment(assignment):
    ended = end_assignment(assignment)
    assert ended.is_active is False
    assert ended.ends_at is not None


def test_end_assignment_is_idempotent(assignment):
    end_assignment(assignment)
    first_ends_at = assignment.ends_at
    end_assignment(assignment)
    assert assignment.ends_at == first_ends_at


def test_deactivate_vehicle_ends_active_assignment(assignment, vehicle):
    deactivate_vehicle(vehicle)
    vehicle.refresh_from_db()
    assignment.refresh_from_db()
    assert vehicle.is_active is False
    assert assignment.is_active is False


def test_activate_vehicle(vehicle):
    deactivate_vehicle(vehicle)
    activate_vehicle(vehicle)
    vehicle.refresh_from_db()
    assert vehicle.is_active is True
```

## `apps/tracking/__init__.py`

- **Folder:** `apps/tracking/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/admin.py`

- **Folder:** `apps/tracking/`
- **File:** `admin.py`

```python
from __future__ import annotations

from django.contrib import admin

from .models import Location, Trip
from .services import close_trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "driver", "status", "started_at", "ended_at")
    list_filter = ("status", "vehicle")
    search_fields = ("vehicle__bus_number", "driver__user__username")
    date_hierarchy = "started_at"
    readonly_fields = ("created_at", "updated_at")
    actions = ("action_close",)

    @admin.action(description="Close selected open trips")
    def action_close(self, request, queryset) -> None:
        count = 0
        for trip in queryset:
            if trip.is_open:
                close_trip(trip, reason="admin_close")
                count += 1
        self.message_user(request, f"Closed {count} open trip(s).")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Locations are append-only; the admin is read-only to preserve integrity."""

    list_display = ("id", "vehicle", "trip", "latitude", "longitude", "speed_kmh", "captured_at")
    list_filter = ("vehicle",)
    search_fields = ("vehicle__bus_number",)
    date_hierarchy = "captured_at"
    readonly_fields = (
        "vehicle",
        "driver",
        "trip",
        "latitude",
        "longitude",
        "speed_kmh",
        "accuracy_m",
        "captured_at",
        "received_at",
        "client_event_id",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        # Only superusers may prune raw data; normal admins cannot.
        return bool(request.user and request.user.is_superuser)
```

## `apps/tracking/api/__init__.py`

- **Folder:** `apps/tracking/api/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/api/permissions.py`

- **Folder:** `apps/tracking/api/`
- **File:** `permissions.py`

```python
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
```

## `apps/tracking/api/serializers.py`

- **Folder:** `apps/tracking/api/`
- **File:** `serializers.py`

```python
"""DRF serializers for the tracking API.

The privacy boundary lives here: :class:`PublicVehicleLocationSerializer`
never exposes driver contact details, usernames, emails, or internal
assignment identifiers. The admin serializer adds only a display name and
accuracy on top of the public fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from apps.fleet.models import Vehicle

from ..models import Location, Trip


# ---------------------------------------------------------------------------
# Ingestion (input)
# ---------------------------------------------------------------------------
class LocationIngestSerializer(serializers.Serializer):
    """Validates a single GPS submission. Driver/vehicle/trip are server-derived."""

    client_event_id = serializers.UUIDField()
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, min_value=Decimal("-90"), max_value=Decimal("90")
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, min_value=Decimal("-180"), max_value=Decimal("180")
    )
    speed_kmh = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, allow_null=True, min_value=Decimal("0")
    )
    accuracy_m = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False, allow_null=True, min_value=Decimal("0")
    )
    captured_at = serializers.DateTimeField()


class LocationCreatedSerializer(serializers.ModelSerializer):
    """Confirmation returned after a fix is accepted."""

    trip_id = serializers.IntegerField(source="trip.id", read_only=True)

    class Meta:
        model = Location
        fields = ["id", "trip_id", "captured_at", "received_at"]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Live locations (output)
# ---------------------------------------------------------------------------
@dataclass
class VehicleSnapshot:
    """A vehicle plus its latest location (which may be missing)."""

    vehicle: Vehicle
    location: Location | None
    now: datetime


class PublicVehicleLocationSerializer(serializers.Serializer):
    """Public-safe view of a vehicle's latest position. No driver identity."""

    def to_representation(self, snapshot: VehicleSnapshot) -> dict:
        vehicle = snapshot.vehicle
        loc = snapshot.location
        data: dict = {
            "vehicle_id": vehicle.id,
            "bus_number": vehicle.bus_number,
            "route_label": vehicle.route_label,
            "has_signal": loc is not None,
            "latitude": None,
            "longitude": None,
            "speed_kmh": None,
            "captured_at": None,
            "age_seconds": None,
            "is_stale": True,
        }
        if loc is not None:
            age = (snapshot.now - loc.captured_at).total_seconds()
            data.update(
                {
                    "latitude": str(loc.latitude),
                    "longitude": str(loc.longitude),
                    "speed_kmh": str(loc.speed_kmh) if loc.speed_kmh is not None else None,
                    "captured_at": loc.captured_at.isoformat(),
                    "age_seconds": int(age),
                    "is_stale": age > settings.LOCATION_STALE_SECONDS,
                }
            )
        return data


class AdminVehicleLocationSerializer(PublicVehicleLocationSerializer):
    """Admin view: adds driver display name and accuracy to the public fields."""

    def to_representation(self, snapshot: VehicleSnapshot) -> dict:
        data = super().to_representation(snapshot)
        loc = snapshot.location
        data["driver_name"] = loc.driver.display_name if loc is not None else None
        data["accuracy_m"] = (
            str(loc.accuracy_m) if loc is not None and loc.accuracy_m is not None else None
        )
        return data


# ---------------------------------------------------------------------------
# Trip history (output, admin only)
# ---------------------------------------------------------------------------
class TripSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source="vehicle.bus_number", read_only=True)
    driver_name = serializers.CharField(source="driver.display_name", read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "vehicle_id",
            "bus_number",
            "driver_name",
            "started_at",
            "ended_at",
            "status",
        ]
        read_only_fields = fields


class TripPointSerializer(serializers.ModelSerializer):
    """A single point for polyline playback."""

    class Meta:
        model = Location
        fields = ["latitude", "longitude", "speed_kmh", "captured_at"]
        read_only_fields = fields
```

## `apps/tracking/api/urls.py`

- **Folder:** `apps/tracking/api/`
- **File:** `urls.py`

```python
"""URL routes for the versioned tracking API (mounted at ``/api/v1/``)."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("locations/", views.LocationCreateView.as_view(), name="location-create"),
    path(
        "vehicles/latest-locations/",
        views.LatestActiveVehicleLocationsView.as_view(),
        name="vehicle-latest-locations",
    ),
    path(
        "vehicles/<int:vehicle_id>/latest-location/",
        views.VehicleLatestLocationView.as_view(),
        name="vehicle-latest-location",
    ),
    path("trips/", views.TripListView.as_view(), name="trip-list"),
    path("trips/<int:trip_id>/points/", views.TripPointsView.as_view(), name="trip-points"),
]
```

## `apps/tracking/api/views.py`

- **Folder:** `apps/tracking/api/`
- **File:** `views.py`

```python
"""Versioned tracking API views under ``/api/v1/``.

- ``POST /locations/`` — a driver submits a GPS fix (idempotent).
- ``GET  /vehicles/latest-locations/`` — latest fix per active vehicle.
- ``GET  /vehicles/<id>/latest-location/`` — latest fix for one vehicle.
- ``GET  /trips/`` — trips for a vehicle/date (admin).
- ``GET  /trips/<id>/points/`` — trip points for polyline playback (admin).
"""

from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import is_admin
from apps.fleet.models import Vehicle

from ..selectors import (
    get_latest_active_vehicle_locations,
    get_latest_vehicle_location,
    get_trip_points,
    get_vehicle_trips,
)
from ..services import (
    NoActiveAssignment,
    VehicleInactive,
    record_vehicle_location,
)
from .permissions import IsAdminRole, IsDriverWithActiveAssignment
from .serializers import (
    AdminVehicleLocationSerializer,
    LocationCreatedSerializer,
    LocationIngestSerializer,
    PublicVehicleLocationSerializer,
    TripPointSerializer,
    TripSerializer,
    VehicleSnapshot,
)


def _location_serializer_for(request: Request):
    """Admins get the richer serializer; everyone else gets the public one."""
    return (
        AdminVehicleLocationSerializer
        if is_admin(request.user)
        else PublicVehicleLocationSerializer
    )


class LocationCreateView(APIView):
    """Accept a driver's GPS fix. Vehicle/driver/trip are derived server-side."""

    permission_classes = [IsDriverWithActiveAssignment]
    throttle_scope = "location_ingest"

    def post(self, request: Request) -> Response:
        serializer = LocationIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            location, created = record_vehicle_location(
                user=request.user,
                client_event_id=data["client_event_id"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                captured_at=data["captured_at"],
                speed_kmh=data.get("speed_kmh"),
                accuracy_m=data.get("accuracy_m"),
            )
        except NoActiveAssignment as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except VehicleInactive as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message_dict if hasattr(exc, "message_dict") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        body = LocationCreatedSerializer(location).data
        body["duplicate"] = not created
        return Response(
            body,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class LatestActiveVehicleLocationsView(APIView):
    """Latest location for every active vehicle. Public, role-aware output."""

    permission_classes = [AllowAny]
    throttle_scope = "public_read"

    def get(self, request: Request) -> Response:
        now = timezone.now()
        snapshots = [
            VehicleSnapshot(vehicle=vehicle, location=location, now=now)
            for vehicle, location in get_latest_active_vehicle_locations()
        ]
        serializer_cls = _location_serializer_for(request)
        data = serializer_cls(snapshots, many=True).data
        return Response({"count": len(data), "results": data})


class VehicleLatestLocationView(APIView):
    """Latest location for a single active vehicle. Public, role-aware output."""

    permission_classes = [AllowAny]
    throttle_scope = "public_read"

    def get(self, request: Request, vehicle_id: int) -> Response:
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id, is_active=True)
        snapshot = VehicleSnapshot(
            vehicle=vehicle,
            location=get_latest_vehicle_location(vehicle),
            now=timezone.now(),
        )
        serializer_cls = _location_serializer_for(request)
        return Response(serializer_cls(snapshot).data)


class TripListView(APIView):
    """List trips for a vehicle, optionally on a date. Admin only."""

    permission_classes = [IsAdminRole]

    def get(self, request: Request) -> Response:
        vehicle_id = request.query_params.get("vehicle_id")
        if not vehicle_id:
            return Response(
                {"detail": "vehicle_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

        on_date = None
        date_param = request.query_params.get("date")
        if date_param:
            on_date = parse_date(date_param)
            if on_date is None:
                return Response(
                    {"detail": "date must be YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        trips = get_vehicle_trips(vehicle=vehicle, on_date=on_date)
        data = TripSerializer(trips, many=True).data
        return Response({"count": len(data), "results": data})


class TripPointsView(APIView):
    """Return a trip's points (ascending) for polyline playback. Admin only."""

    permission_classes = [IsAdminRole]

    def get(self, request: Request, trip_id: int) -> Response:
        from ..models import Trip

        trip = get_object_or_404(Trip, pk=trip_id)

        # start/end are HH:MM times interpreted on the trip's local date.
        trip_local_date = timezone.localtime(trip.started_at).date()
        start_dt = self._time_on_date(request.query_params.get("start"), trip_local_date)
        end_dt = self._time_on_date(request.query_params.get("end"), trip_local_date)
        if request.query_params.get("start") and start_dt is None:
            return Response({"detail": "start must be HH:MM."}, status=400)
        if request.query_params.get("end") and end_dt is None:
            return Response({"detail": "end must be HH:MM."}, status=400)

        points = get_trip_points(trip=trip, start=start_dt, end=end_dt)
        data = TripPointSerializer(points, many=True).data
        return Response(
            {
                "trip_id": trip.id,
                "vehicle_id": trip.vehicle_id,
                "status": trip.status,
                "count": len(data),
                "points": data,
            }
        )

    @staticmethod
    def _time_on_date(raw: str | None, on_date):
        """Combine an HH:MM string with a date into an aware datetime, or None.

        Returns None for both missing and malformed input. ``parse_time`` may
        *raise* ValueError on a well-formed but out-of-range value (e.g.
        ``"99:99"``), so that is caught and treated as invalid rather than
        surfacing as a 500.
        """
        if not raw:
            return None
        try:
            parsed = parse_time(raw)
        except ValueError:
            return None
        if parsed is None:
            return None
        from datetime import datetime

        naive = datetime.combine(on_date, parsed)
        return timezone.make_aware(naive, timezone.get_current_timezone())
```

## `apps/tracking/apps.py`

- **Folder:** `apps/tracking/`
- **File:** `apps.py`

```python
from django.apps import AppConfig


class TrackingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tracking"
    label = "tracking"
    verbose_name = "Tracking"
```

## `apps/tracking/management/__init__.py`

- **Folder:** `apps/tracking/management/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/management/commands/__init__.py`

- **Folder:** `apps/tracking/management/commands/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/management/commands/close_stale_trips.py`

- **Folder:** `apps/tracking/management/commands/`
- **File:** `close_stale_trips.py`

```python
"""Close trips left open past the inactivity threshold.

Run on a schedule (e.g. a free GitHub Actions cron) so trips do not remain
open forever when a phone dies, loses signal, or the driver forgets to log out.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.tracking.services import close_stale_trips


class Command(BaseCommand):
    help = "Close open trips that have received no location within the threshold."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--minutes",
            type=int,
            default=None,
            help="Override the inactivity threshold (defaults to TRIP_INACTIVITY_MINUTES).",
        )

    def handle(self, *args, **options) -> None:
        closed = close_stale_trips(threshold_minutes=options["minutes"])
        self.stdout.write(self.style.SUCCESS(f"Closed {closed} stale trip(s)."))
```

## `apps/tracking/management/commands/create_demo_data.py`

- **Folder:** `apps/tracking/management/commands/`
- **File:** `create_demo_data.py`

```python
"""Seed a fresh database with demo users, vehicles, assignments and live trips.

Idempotent and safe to re-run: existing objects are reused, never duplicated.
Intended for first-run demos and local development — not for production data.

Examples::

    python manage.py create_demo_data
    python manage.py create_demo_data --drivers 4 --vehicles 6 --admin-password 's3cret...'

If ``--admin-password`` is omitted a strong random password is generated and
printed once. The command never prints an existing admin's password.
"""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.accounts.models import DriverProfile
from apps.accounts.services import create_driver
from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_assignment_for_vehicle
from apps.fleet.services import assign_driver_to_vehicle
from apps.tracking.models import Location, Trip, TripStatus

# Approximate campus centre (Chittagong University). Demo points scatter nearby.
BASE_LAT = Decimal("22.469500")
BASE_LON = Decimal("91.788400")

ROUTE_LABELS = [
    "Main Gate - Faculty",
    "Station - Campus",
    "Hostel Loop",
    "City Shuttle",
    "Medical - Science",
    "Library Express",
]


class Command(BaseCommand):
    help = "Create demo users, vehicles, assignments and sample live trips (idempotent)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--drivers", type=int, default=3, help="Number of driver accounts.")
        parser.add_argument("--vehicles", type=int, default=5, help="Number of vehicles.")
        parser.add_argument("--admin-username", default="admin", help="Admin username.")
        parser.add_argument(
            "--admin-password",
            default=None,
            help="Admin password. If omitted, a strong one is generated and printed.",
        )
        parser.add_argument(
            "--points",
            type=int,
            default=6,
            help="Recent location points to generate per assigned vehicle (0 to skip).",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        admin_group, _ = Group.objects.get_or_create(name=settings.ADMIN_GROUP)
        Group.objects.get_or_create(name=settings.DRIVER_GROUP)

        self._ensure_admin(options["admin_username"], options["admin_password"], admin_group)
        drivers = self._ensure_drivers(options["drivers"])
        vehicles = self._ensure_vehicles(options["vehicles"])
        self._ensure_assignments(drivers, vehicles)
        if options["points"] > 0:
            self._ensure_live_trips(options["points"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {len(drivers)} driver(s), {len(vehicles)} vehicle(s)."
            )
        )

    # -- admin ---------------------------------------------------------------
    def _ensure_admin(self, username: str, password: str | None, admin_group: Group) -> None:
        user = User.objects.filter(username=username).first()
        if user is not None:
            user.groups.add(admin_group)
            self.stdout.write(f"Admin {username!r}: already exists (password unchanged).")
            return

        password = password or get_random_string(16)
        user = User.objects.create_user(username=username, password=password, is_staff=True)
        user.groups.add(admin_group)
        self.stdout.write(self.style.WARNING(f"Admin created — username: {username}"))
        self.stdout.write(self.style.WARNING(f"Admin password (shown once): {password}"))

    # -- drivers -------------------------------------------------------------
    def _ensure_drivers(self, count: int) -> list[DriverProfile]:
        drivers: list[DriverProfile] = []
        for i in range(1, count + 1):
            username = f"driver{i}"
            existing = User.objects.filter(username=username).first()
            if existing is not None:
                profile = getattr(existing, "driver_profile", None)
                if profile is not None:
                    drivers.append(profile)
                continue
            profile = create_driver(
                username=username,
                password=get_random_string(12),
                first_name="Driver",
                last_name=str(i),
                employee_id=f"EMP-{i:03d}",
            )
            drivers.append(profile)
            self.stdout.write(f"Driver {username!r}: created.")
        return drivers

    # -- vehicles ------------------------------------------------------------
    def _ensure_vehicles(self, count: int) -> list[Vehicle]:
        vehicles: list[Vehicle] = []
        for i in range(1, count + 1):
            bus_number = f"CU-{i:02d}"
            vehicle, created = Vehicle.objects.get_or_create(
                bus_number=bus_number,
                defaults={"route_label": ROUTE_LABELS[(i - 1) % len(ROUTE_LABELS)]},
            )
            vehicles.append(vehicle)
            if created:
                self.stdout.write(f"Vehicle {bus_number!r}: created.")
        return vehicles

    # -- assignments ---------------------------------------------------------
    def _ensure_assignments(self, drivers: list[DriverProfile], vehicles: list[Vehicle]) -> None:
        for driver, vehicle in zip(drivers, vehicles, strict=False):
            if get_active_assignment_for_vehicle(vehicle) is not None:
                continue
            assign_driver_to_vehicle(driver=driver, vehicle=vehicle)
            self.stdout.write(f"Assigned {driver} -> {vehicle}.")

    # -- live trips ----------------------------------------------------------
    def _ensure_live_trips(self, points: int) -> None:
        now = timezone.now()
        for vehicle in Vehicle.objects.filter(is_active=True):
            assignment = get_active_assignment_for_vehicle(vehicle)
            if assignment is None:
                continue
            if Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).exists():
                continue

            started_at = now - timedelta(seconds=points * 20)
            trip = Trip.objects.create(
                vehicle=vehicle,
                driver=assignment.driver,
                started_at=started_at,
                status=TripStatus.OPEN,
            )
            for step in range(points):
                jitter_lat = Decimal(str(round(random.uniform(-0.01, 0.01), 6)))
                jitter_lon = Decimal(str(round(random.uniform(-0.01, 0.01), 6)))
                Location.objects.create(
                    vehicle=vehicle,
                    driver=assignment.driver,
                    trip=trip,
                    latitude=BASE_LAT + jitter_lat,
                    longitude=BASE_LON + jitter_lon,
                    speed_kmh=Decimal(str(round(random.uniform(0, 45), 2))),
                    accuracy_m=Decimal("8.00"),
                    captured_at=now - timedelta(seconds=(points - step - 1) * 20),
                )
            self.stdout.write(f"Live trip for {vehicle}: {points} point(s).")
```

## `apps/tracking/migrations/0001_initial.py`

- **Folder:** `apps/tracking/migrations/`
- **File:** `0001_initial.py`

```python
# Generated by Django 5.2.17 on 2026-08-16 07:17

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('fleet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('COMPLETED', 'Completed')], default='OPEN', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trips', to='accounts.driverprofile')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trips', to='fleet.vehicle')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('speed_kmh', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('accuracy_m', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('captured_at', models.DateTimeField()),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('client_event_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='accounts.driverprofile')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='fleet.vehicle')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='tracking.trip')),
            ],
            options={
                'ordering': ['-captured_at'],
            },
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['vehicle', '-started_at'], name='idx_trip_vehicle_started'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['vehicle', 'status'], name='idx_trip_vehicle_status'),
        ),
        migrations.AddConstraint(
            model_name='trip',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'OPEN')), fields=('vehicle',), name='uniq_open_trip_per_vehicle'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['vehicle', '-captured_at'], name='idx_loc_vehicle_captured'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['trip', 'captured_at'], name='idx_loc_trip_captured'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.CheckConstraint(condition=models.Q(('latitude__gte', -90), ('latitude__lte', 90)), name='chk_latitude_range'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.CheckConstraint(condition=models.Q(('longitude__gte', -180), ('longitude__lte', 180)), name='chk_longitude_range'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.CheckConstraint(condition=models.Q(('speed_kmh__isnull', True), ('speed_kmh__gte', 0), _connector='OR'), name='chk_speed_non_negative'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.CheckConstraint(condition=models.Q(('accuracy_m__isnull', True), ('accuracy_m__gte', 0), _connector='OR'), name='chk_accuracy_non_negative'),
        ),
    ]
```

## `apps/tracking/migrations/__init__.py`

- **Folder:** `apps/tracking/migrations/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/models.py`

- **Folder:** `apps/tracking/`
- **File:** `models.py`

```python
"""Tracking models: Trips and append-only Location history.

A ``Trip`` groups the ``Location`` points recorded between a vehicle starting
and stopping movement for a session. Locations are append-only: they are never
edited after insertion, which keeps trip-history playback trustworthy.

Database-level constraints enforce the domain rules (valid coordinates,
non-negative speed/accuracy, one open trip per vehicle, unique client events)
so invalid data cannot be persisted even if application code has a bug.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.db.models import Q

from apps.accounts.models import DriverProfile
from apps.fleet.models import Vehicle


class TripStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    COMPLETED = "COMPLETED", "Completed"


class Trip(models.Model):
    """A single tracking session for a vehicle."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="trips")
    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="trips")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=TripStatus.choices, default=TripStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(status="OPEN"),
                name="uniq_open_trip_per_vehicle",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "-started_at"], name="idx_trip_vehicle_started"),
            models.Index(fields=["vehicle", "status"], name="idx_trip_vehicle_status"),
        ]

    def __str__(self) -> str:
        return f"Trip #{self.pk} {self.vehicle} ({self.status})"

    @property
    def is_open(self) -> bool:
        return self.status == TripStatus.OPEN


class Location(models.Model):
    """A single GPS fix. Append-only."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="locations")
    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT, related_name="locations")
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="locations")

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    accuracy_m = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    captured_at = models.DateTimeField()  # device capture time
    received_at = models.DateTimeField(auto_now_add=True)  # server receipt time
    # Idempotency key so a retried submission does not create duplicate points.
    client_event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-captured_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__gte=-90) & Q(latitude__lte=90),
                name="chk_latitude_range",
            ),
            models.CheckConstraint(
                condition=Q(longitude__gte=-180) & Q(longitude__lte=180),
                name="chk_longitude_range",
            ),
            models.CheckConstraint(
                condition=Q(speed_kmh__isnull=True) | Q(speed_kmh__gte=0),
                name="chk_speed_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(accuracy_m__isnull=True) | Q(accuracy_m__gte=0),
                name="chk_accuracy_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "-captured_at"], name="idx_loc_vehicle_captured"),
            models.Index(fields=["trip", "captured_at"], name="idx_loc_trip_captured"),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle} @ ({self.latitude}, {self.longitude}) {self.captured_at:%H:%M:%S}"
```

## `apps/tracking/selectors.py`

- **Folder:** `apps/tracking/`
- **File:** `selectors.py`

```python
"""Tracking selectors: read-only queries for live and historical views."""

from __future__ import annotations

from datetime import date, datetime

from django.db.models import QuerySet

from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_vehicles

from .models import Location, Trip, TripStatus


def get_latest_vehicle_location(vehicle: Vehicle) -> Location | None:
    """The most recently captured location for a vehicle, or None."""
    return (
        Location.objects.filter(vehicle=vehicle)
        .select_related("driver__user", "vehicle")
        .order_by("-captured_at")
        .first()
    )


def get_latest_active_vehicle_locations() -> list[tuple[Vehicle, Location | None]]:
    """Return (vehicle, latest_location_or_None) for every active vehicle.

    Including vehicles without a location lets dashboards mark them as
    unavailable. The fleet is small (5-10 vehicles), so a per-vehicle lookup is
    clear and inexpensive.
    """
    results: list[tuple[Vehicle, Location | None]] = []
    for vehicle in get_active_vehicles():
        results.append((vehicle, get_latest_vehicle_location(vehicle)))
    return results


def get_vehicle_trips(*, vehicle: Vehicle, on_date: date | None = None) -> QuerySet[Trip]:
    """Trips for a vehicle, optionally limited to a single local calendar date."""
    qs = Trip.objects.filter(vehicle=vehicle).select_related("vehicle", "driver__user")
    if on_date is not None:
        # __date compares in the active timezone when USE_TZ is True.
        qs = qs.filter(started_at__date=on_date)
    return qs.order_by("-started_at")


def get_trip_points(
    *,
    trip: Trip,
    start: datetime | None = None,
    end: datetime | None = None,
) -> QuerySet[Location]:
    """Points for a trip in ascending capture order, optionally time-bounded."""
    qs = Location.objects.filter(trip=trip)
    if start is not None:
        qs = qs.filter(captured_at__gte=start)
    if end is not None:
        qs = qs.filter(captured_at__lte=end)
    return qs.order_by("captured_at")


def get_open_trip_for_vehicle(vehicle: Vehicle) -> Trip | None:
    """The vehicle's current open trip, or None."""
    return Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).first()
```

## `apps/tracking/services.py`

- **Folder:** `apps/tracking/`
- **File:** `services.py`

```python
"""Tracking services: the authoritative state-changing tracking operations.

The central service, :func:`record_vehicle_location`, resolves the vehicle from
the authenticated driver's active assignment (never from client input),
validates the fix, attaches it to the correct open trip (opening one when
needed), and is idempotent on ``client_event_id``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import DriverProfile
from apps.accounts.permissions import RequestUser
from apps.fleet.models import Vehicle
from apps.fleet.selectors import get_active_assignment_for_user

from .models import Location, Trip, TripStatus
from .validators import (
    validate_accuracy,
    validate_capture_timestamp,
    validate_coordinates,
    validate_speed,
)

logger = logging.getLogger("apps.tracking")


class DomainError(Exception):
    """Base class for tracking domain errors that map to a 4xx response."""


class NoActiveAssignment(DomainError):
    """The user has no active driver assignment, so cannot submit locations."""


class VehicleInactive(DomainError):
    """The assigned vehicle is not part of the live fleet."""


# ---------------------------------------------------------------------------
# Trip lifecycle
# ---------------------------------------------------------------------------
def _is_trip_stale(trip: Trip, *, now: datetime, threshold: timedelta) -> bool:
    """True if the trip has had no fix within ``threshold``."""
    last_captured = (
        trip.locations.order_by("-captured_at").values_list("captured_at", flat=True).first()
    )
    reference = last_captured or trip.started_at
    return (now - reference) > threshold


def open_trip(*, vehicle: Vehicle, driver: DriverProfile, started_at: datetime) -> Trip:
    """Open a new trip for a vehicle, tolerating a concurrent opener."""
    try:
        return Trip.objects.create(
            vehicle=vehicle,
            driver=driver,
            started_at=started_at,
            status=TripStatus.OPEN,
        )
    except IntegrityError:
        # A concurrent request opened the trip first; reuse it.
        existing = Trip.objects.filter(vehicle=vehicle, status=TripStatus.OPEN).first()
        if existing is None:  # pragma: no cover - defensive
            raise
        return existing


def close_trip(trip: Trip, *, reason: str = "") -> Trip:
    """Mark a trip completed. Completed trips accept no further locations."""
    if trip.status != TripStatus.COMPLETED:
        trip.status = TripStatus.COMPLETED
        trip.ended_at = timezone.now()
        trip.save(update_fields=["status", "ended_at", "updated_at"])
        logger.info("Closed trip %s (reason=%s)", trip.pk, reason or "unspecified")
    return trip


def close_open_trip_for_user(user: RequestUser, *, reason: str = "") -> Trip | None:
    """Close the open trip belonging to a driver (used on logout)."""
    profile = getattr(user, "driver_profile", None)
    if profile is None:
        return None
    trip = Trip.objects.filter(driver=profile, status=TripStatus.OPEN).first()
    if trip is not None:
        close_trip(trip, reason=reason)
    return trip


def close_stale_trips(*, threshold_minutes: int | None = None) -> int:
    """Close every open trip with no fix within the inactivity threshold.

    Returns the number of trips closed. Intended to be run on a schedule.
    """
    minutes = threshold_minutes or settings.TRIP_INACTIVITY_MINUTES
    threshold = timedelta(minutes=minutes)
    now = timezone.now()
    closed = 0
    for trip in Trip.objects.filter(status=TripStatus.OPEN):
        if _is_trip_stale(trip, now=now, threshold=threshold):
            close_trip(trip, reason="stale_batch")
            closed += 1
    return closed


def _get_or_open_trip(*, vehicle: Vehicle, driver: DriverProfile, captured_at: datetime) -> Trip:
    """Return the vehicle's current open trip, starting a fresh one if needed.

    A stale open trip (idle past the inactivity threshold) is closed and a new
    trip is opened, so a resumed session after a long gap starts cleanly.
    """
    threshold = timedelta(minutes=settings.TRIP_INACTIVITY_MINUTES)
    now = timezone.now()
    open_trip_qs = Trip.objects.select_for_update().filter(vehicle=vehicle, status=TripStatus.OPEN)
    current = open_trip_qs.first()
    if current is not None:
        if _is_trip_stale(current, now=now, threshold=threshold):
            close_trip(current, reason="stale_on_ingest")
        else:
            return current
    return open_trip(vehicle=vehicle, driver=driver, started_at=captured_at)


# ---------------------------------------------------------------------------
# Location ingestion
# ---------------------------------------------------------------------------
@transaction.atomic
def record_vehicle_location(
    *,
    user: RequestUser,
    client_event_id,
    latitude: Decimal,
    longitude: Decimal,
    captured_at: datetime,
    speed_kmh: Decimal | None = None,
    accuracy_m: Decimal | None = None,
) -> tuple[Location, bool]:
    """Validate and persist a driver's GPS fix under the correct trip.

    Returns ``(location, created)``. ``created`` is False when the
    ``client_event_id`` was already recorded (idempotent retry).
    """
    # Idempotency: a retried submission returns the original record.
    existing = Location.objects.filter(client_event_id=client_event_id).first()
    if existing is not None:
        return existing, False

    # Authoritative vehicle resolution: from the assignment, never the client.
    assignment = get_active_assignment_for_user(user)
    if assignment is None:
        raise NoActiveAssignment("No active vehicle assignment for this driver.")
    if not assignment.vehicle.is_active:
        raise VehicleInactive("The assigned vehicle is not active.")

    # Authoritative domain validation (mirrors DB constraints).
    validate_coordinates(latitude, longitude)
    validate_speed(speed_kmh)
    validate_accuracy(accuracy_m)
    validate_capture_timestamp(captured_at)

    driver = assignment.driver
    vehicle = assignment.vehicle
    trip = _get_or_open_trip(vehicle=vehicle, driver=driver, captured_at=captured_at)

    try:
        location = Location.objects.create(
            vehicle=vehicle,
            driver=driver,
            trip=trip,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            accuracy_m=accuracy_m,
            captured_at=captured_at,
            client_event_id=client_event_id,
        )
    except IntegrityError:
        # Concurrent duplicate of the same client_event_id.
        duplicate = Location.objects.filter(client_event_id=client_event_id).first()
        if duplicate is not None:
            return duplicate, False
        raise

    return location, True
```

## `apps/tracking/tests/__init__.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `__init__.py`

```python

```

## `apps/tracking/tests/test_location_api.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_location_api.py`

```python
"""Location ingestion API tests (``POST /api/v1/locations/``)."""

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.api.views import LocationCreateView
from apps.tracking.models import Location

pytestmark = pytest.mark.django_db

URL = reverse("api:location-create")


def _payload(**overrides):
    data = {
        "client_event_id": str(uuid.uuid4()),
        "latitude": "23.777100",
        "longitude": "90.399400",
        "speed_kmh": "31.50",
        "captured_at": timezone.now().isoformat(),
    }
    data.update(overrides)
    return data


def test_throttle_scope_is_declared():
    assert LocationCreateView.throttle_scope == "location_ingest"


def test_assigned_driver_can_post_location(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["duplicate"] is False
    assert body["trip_id"] is not None
    assert "received_at" in body
    assert Location.objects.count() == 1


def test_duplicate_client_event_id_returns_200(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    payload = _payload()
    first = api_client.post(URL, payload, format="json")
    second = api_client.post(URL, payload, format="json")
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["duplicate"] is True
    assert first.json()["id"] == second.json()["id"]
    assert Location.objects.count() == 1


def test_non_driver_is_forbidden(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_anonymous_is_forbidden(api_client):
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_driver_without_assignment_is_forbidden(api_client, driver_user):
    api_client.force_authenticate(user=driver_user)
    resp = api_client.post(URL, _payload(), format="json")
    assert resp.status_code == 403


def test_invalid_coordinates_rejected_by_serializer(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.post(URL, _payload(latitude="120.0"), format="json")
    assert resp.status_code == 400
    assert "latitude" in resp.json()


def test_future_timestamp_rejected_by_service(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    future = (timezone.now() + timedelta(minutes=10)).isoformat()
    resp = api_client.post(URL, _payload(captured_at=future), format="json")
    assert resp.status_code == 400
    assert Location.objects.count() == 0


def test_missing_required_field_rejected(api_client, assigned_driver):
    api_client.force_authenticate(user=assigned_driver)
    payload = _payload()
    del payload["captured_at"]
    resp = api_client.post(URL, payload, format="json")
    assert resp.status_code == 400
```

## `apps/tracking/tests/test_public_api.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_public_api.py`

```python
"""Public live-location API tests and the public/admin privacy boundary."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.api.views import (
    LatestActiveVehicleLocationsView,
    VehicleLatestLocationView,
)

pytestmark = pytest.mark.django_db

LIST_URL = reverse("api:vehicle-latest-locations")


def test_public_read_throttle_scopes_declared():
    assert LatestActiveVehicleLocationsView.throttle_scope == "public_read"
    assert VehicleLatestLocationView.throttle_scope == "public_read"


def test_latest_locations_public_shape(api_client, open_trip, vehicle, add_point):
    add_point(trip=open_trip, speed_kmh=Decimal("20.00"), accuracy_m=Decimal("5.00"))
    resp = api_client.get(LIST_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    row = body["results"][0]
    assert row["vehicle_id"] == vehicle.id
    assert row["bus_number"] == vehicle.bus_number
    assert row["has_signal"] is True
    assert isinstance(row["latitude"], str)
    assert isinstance(row["age_seconds"], int)
    # Privacy boundary: no driver identity or accuracy on the public view.
    assert "driver_name" not in row
    assert "accuracy_m" not in row


def test_latest_locations_admin_adds_driver_and_accuracy(
    api_client, admin_user, open_trip, add_point
):
    add_point(trip=open_trip, accuracy_m=Decimal("7.50"))
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(LIST_URL)
    row = resp.json()["results"][0]
    assert row["driver_name"] == open_trip.driver.display_name
    assert row["accuracy_m"] == "7.50"


def test_vehicle_without_fix_reports_no_signal(api_client, vehicle):
    resp = api_client.get(LIST_URL)
    row = resp.json()["results"][0]
    assert row["has_signal"] is False
    assert row["latitude"] is None
    assert row["is_stale"] is True


def test_fresh_fix_is_not_stale(api_client, open_trip, add_point):
    add_point(trip=open_trip, captured_at=timezone.now())
    resp = api_client.get(LIST_URL)
    assert resp.json()["results"][0]["is_stale"] is False


def test_old_fix_is_stale(api_client, open_trip, add_point):
    add_point(trip=open_trip, captured_at=timezone.now() - timedelta(seconds=90))
    resp = api_client.get(LIST_URL)
    assert resp.json()["results"][0]["is_stale"] is True


def test_single_vehicle_latest_location(api_client, vehicle, open_trip, add_point):
    add_point(trip=open_trip)
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[vehicle.id]))
    assert resp.status_code == 200
    assert resp.json()["vehicle_id"] == vehicle.id


def test_single_vehicle_latest_location_404_when_inactive(api_client, vehicle):
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active"])
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[vehicle.id]))
    assert resp.status_code == 404


def test_single_vehicle_latest_location_404_when_missing(api_client):
    resp = api_client.get(reverse("api:vehicle-latest-location", args=[999999]))
    assert resp.status_code == 404
```

## `apps/tracking/tests/test_selectors.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_selectors.py`

```python
"""Tracking selector tests: live and historical read queries."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus
from apps.tracking.selectors import (
    get_latest_active_vehicle_locations,
    get_latest_vehicle_location,
    get_open_trip_for_vehicle,
    get_trip_points,
    get_vehicle_trips,
)

pytestmark = pytest.mark.django_db


def test_get_latest_vehicle_location_returns_most_recent(open_trip, vehicle, add_point):
    now = timezone.now()
    add_point(trip=open_trip, captured_at=now - timedelta(minutes=5))
    newest = add_point(trip=open_trip, captured_at=now - timedelta(seconds=5))
    assert get_latest_vehicle_location(vehicle) == newest


def test_get_latest_vehicle_location_none_when_empty(vehicle):
    assert get_latest_vehicle_location(vehicle) is None


def test_latest_active_locations_include_vehicles_without_fix(
    open_trip, vehicle, make_vehicle, add_point
):
    silent = make_vehicle(bus_number="SILENT")
    add_point(trip=open_trip)

    results = {veh.id: loc for veh, loc in get_latest_active_vehicle_locations()}
    assert results[vehicle.id] is not None
    assert results[silent.id] is None


def test_get_vehicle_trips_filters_by_date(vehicle, driver_profile):
    today = timezone.localtime(timezone.now())
    Trip.objects.create(
        vehicle=vehicle, driver=driver_profile, started_at=today, status=TripStatus.OPEN
    )
    Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=today - timedelta(days=3),
        status=TripStatus.COMPLETED,
    )

    all_trips = get_vehicle_trips(vehicle=vehicle)
    todays = get_vehicle_trips(vehicle=vehicle, on_date=today.date())
    assert all_trips.count() == 2
    assert todays.count() == 1


def test_get_trip_points_orders_ascending_and_bounds(open_trip, add_point):
    now = timezone.now()
    p1 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=3))
    p2 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=2))
    p3 = add_point(trip=open_trip, captured_at=now - timedelta(minutes=1))

    ordered = list(get_trip_points(trip=open_trip))
    assert ordered == [p1, p2, p3]

    bounded = list(
        get_trip_points(
            trip=open_trip,
            start=now - timedelta(minutes=2, seconds=30),
            end=now - timedelta(seconds=90),
        )
    )
    assert bounded == [p2]


def test_get_open_trip_for_vehicle(open_trip, vehicle):
    assert get_open_trip_for_vehicle(vehicle) == open_trip


def test_get_open_trip_for_vehicle_none_when_completed(open_trip, vehicle):
    open_trip.status = TripStatus.COMPLETED
    open_trip.save(update_fields=["status"])
    assert get_open_trip_for_vehicle(vehicle) is None
```

## `apps/tracking/tests/test_services.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_services.py`

```python
"""Tracking service tests: location ingestion and trip lifecycle."""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.tracking.models import Location, Trip, TripStatus
from apps.tracking.services import (
    NoActiveAssignment,
    VehicleInactive,
    close_open_trip_for_user,
    close_stale_trips,
    close_trip,
    record_vehicle_location,
)

pytestmark = pytest.mark.django_db


def _record(user, **overrides):
    payload = {
        "user": user,
        "client_event_id": overrides.pop("client_event_id", uuid.uuid4()),
        "latitude": Decimal("23.777100"),
        "longitude": Decimal("90.399400"),
        "captured_at": overrides.pop("captured_at", timezone.now()),
    }
    payload.update(overrides)
    return record_vehicle_location(**payload)


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
def test_record_creates_trip_and_location(assigned_driver, vehicle, driver_profile):
    location, created = _record(assigned_driver, speed_kmh=Decimal("30.00"))
    assert created is True
    assert location.vehicle == vehicle
    assert location.driver == driver_profile
    assert location.trip.status == TripStatus.OPEN
    assert Trip.objects.count() == 1
    assert Location.objects.count() == 1


def test_record_is_idempotent_on_client_event_id(assigned_driver):
    eid = uuid.uuid4()
    first, created1 = _record(assigned_driver, client_event_id=eid)
    second, created2 = _record(assigned_driver, client_event_id=eid)
    assert created1 is True
    assert created2 is False
    assert first.id == second.id
    assert Location.objects.count() == 1


def test_record_without_assignment_raises(driver_user):
    with pytest.raises(NoActiveAssignment):
        _record(driver_user)


def test_record_with_inactive_vehicle_raises(assigned_driver, vehicle):
    # Force the vehicle inactive WITHOUT ending the assignment.
    vehicle.is_active = False
    vehicle.save(update_fields=["is_active"])
    with pytest.raises(VehicleInactive):
        _record(assigned_driver)


def test_record_rejects_future_timestamp(assigned_driver):
    with pytest.raises(ValidationError):
        _record(assigned_driver, captured_at=timezone.now() + timedelta(minutes=10))


def test_consecutive_fixes_share_open_trip(assigned_driver):
    _record(assigned_driver)
    _record(assigned_driver)
    assert Trip.objects.count() == 1
    assert Location.objects.count() == 2


def test_stale_open_trip_is_closed_and_new_one_opened(assigned_driver, vehicle, driver_profile):
    stale = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=30),
        status=TripStatus.OPEN,
    )
    location, _ = _record(assigned_driver)

    stale.refresh_from_db()
    assert stale.status == TripStatus.COMPLETED
    assert location.trip.id != stale.id
    assert location.trip.status == TripStatus.OPEN
    assert Trip.objects.count() == 2


# ---------------------------------------------------------------------------
# Trip closing
# ---------------------------------------------------------------------------
def test_close_trip_sets_completed(open_trip):
    close_trip(open_trip, reason="test")
    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED
    assert open_trip.ended_at is not None


def test_close_trip_is_idempotent(open_trip):
    close_trip(open_trip)
    ended = Trip.objects.get(pk=open_trip.pk).ended_at
    close_trip(open_trip)
    assert Trip.objects.get(pk=open_trip.pk).ended_at == ended


def test_close_open_trip_for_user(driver_user, open_trip):
    result = close_open_trip_for_user(driver_user, reason="logout")
    assert result is not None
    open_trip.refresh_from_db()
    assert open_trip.status == TripStatus.COMPLETED


def test_close_open_trip_for_non_driver_returns_none(admin_user):
    assert close_open_trip_for_user(admin_user) is None


def test_close_stale_trips_closes_only_stale(vehicle, make_vehicle, driver_profile, make_driver):
    now = timezone.now()
    stale = Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=now - timedelta(minutes=30),
        status=TripStatus.OPEN,
    )
    v2 = make_vehicle()
    d2 = make_driver(username="d2")
    fresh = Trip.objects.create(
        vehicle=v2,
        driver=d2,
        started_at=now - timedelta(minutes=1),
        status=TripStatus.OPEN,
    )

    closed = close_stale_trips()
    assert closed == 1
    stale.refresh_from_db()
    fresh.refresh_from_db()
    assert stale.status == TripStatus.COMPLETED
    assert fresh.status == TripStatus.OPEN
```

## `apps/tracking/tests/test_trip_api.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_trip_api.py`

```python
"""Trip-history API tests (admin-only ``/trips/`` and ``/trips/<id>/points/``)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tracking.models import Trip, TripStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def a_trip(vehicle, driver_profile):
    return Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=5),
        status=TripStatus.OPEN,
    )


# ---------------------------------------------------------------------------
# /trips/
# ---------------------------------------------------------------------------
def test_trip_list_requires_vehicle_id(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"))
    assert resp.status_code == 400


def test_trip_list_returns_trips_for_vehicle(api_client, admin_user, a_trip, vehicle):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    row = body["results"][0]
    assert row["id"] == a_trip.id
    assert row["bus_number"] == vehicle.bus_number
    assert row["driver_name"] == a_trip.driver.display_name
    assert row["status"] == TripStatus.OPEN


def test_trip_list_bad_date_returns_400(api_client, admin_user, vehicle):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(
        reverse("api:trip-list"), {"vehicle_id": vehicle.id, "date": "not-a-date"}
    )
    assert resp.status_code == 400


def test_trip_list_unknown_vehicle_returns_404(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": 999999})
    assert resp.status_code == 404


def test_trip_list_forbidden_for_driver(api_client, assigned_driver, vehicle):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 403


def test_trip_list_forbidden_for_anonymous(api_client, vehicle):
    resp = api_client.get(reverse("api:trip-list"), {"vehicle_id": vehicle.id})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# /trips/<id>/points/
# ---------------------------------------------------------------------------
def test_trip_points_returns_ascending_points(api_client, admin_user, a_trip, add_point):
    now = timezone.now()
    add_point(trip=a_trip, captured_at=now - timedelta(minutes=2))
    add_point(trip=a_trip, captured_at=now - timedelta(minutes=1))
    api_client.force_authenticate(user=admin_user)

    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]))
    assert resp.status_code == 200
    body = resp.json()
    assert body["trip_id"] == a_trip.id
    assert body["count"] == 2
    times = [p["captured_at"] for p in body["points"]]
    assert times == sorted(times)
    assert set(body["points"][0]) == {"latitude", "longitude", "speed_kmh", "captured_at"}


def test_trip_points_bad_start_returns_400(api_client, admin_user, a_trip):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]), {"start": "99:99"})
    assert resp.status_code == 400


def test_trip_points_forbidden_for_driver(api_client, assigned_driver, a_trip):
    api_client.force_authenticate(user=assigned_driver)
    resp = api_client.get(reverse("api:trip-points", args=[a_trip.id]))
    assert resp.status_code == 403
```

## `apps/tracking/tests/test_validators.py`

- **Folder:** `apps/tracking/tests/`
- **File:** `test_validators.py`

```python
"""Tracking validator tests (authoritative server-side domain checks)."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.tracking.validators import (
    validate_accuracy,
    validate_capture_timestamp,
    validate_coordinates,
    validate_speed,
)


def test_valid_coordinates_pass():
    validate_coordinates(Decimal("23.7771"), Decimal("90.3994"))


@pytest.mark.parametrize(
    "lat,lon",
    [
        (Decimal("91"), Decimal("0")),
        (Decimal("-91"), Decimal("0")),
        (Decimal("0"), Decimal("181")),
        (Decimal("0"), Decimal("-181")),
    ],
)
def test_out_of_range_coordinates_raise(lat, lon):
    with pytest.raises(ValidationError):
        validate_coordinates(lat, lon)


def test_missing_coordinates_raise():
    with pytest.raises(ValidationError):
        validate_coordinates(None, None)


def test_speed_validation():
    validate_speed(None)
    validate_speed(Decimal("0"))
    validate_speed(Decimal("42.5"))
    with pytest.raises(ValidationError):
        validate_speed(Decimal("-1"))


def test_accuracy_validation():
    validate_accuracy(None)
    validate_accuracy(Decimal("0"))
    with pytest.raises(ValidationError):
        validate_accuracy(Decimal("-0.5"))


def test_capture_timestamp_accepts_recent():
    now = timezone.now()
    validate_capture_timestamp(now, now=now)
    validate_capture_timestamp(now - timedelta(seconds=30), now=now)


def test_capture_timestamp_rejects_future_skew():
    now = timezone.now()
    with pytest.raises(ValidationError):
        validate_capture_timestamp(now + timedelta(minutes=10), now=now)


def test_capture_timestamp_rejects_too_old():
    now = timezone.now()
    with pytest.raises(ValidationError):
        validate_capture_timestamp(now - timedelta(hours=2), now=now)


def test_capture_timestamp_required():
    with pytest.raises(ValidationError):
        validate_capture_timestamp(None)
```

## `apps/tracking/validators.py`

- **Folder:** `apps/tracking/`
- **File:** `validators.py`

```python
"""Reusable domain validators for tracking data.

These raise Django's ``ValidationError`` and are the authoritative server-side
checks, independent of any serializer. They mirror the database CheckConstraints
so bad data is rejected early with a clear message.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

LAT_MIN, LAT_MAX = Decimal("-90"), Decimal("90")
LON_MIN, LON_MAX = Decimal("-180"), Decimal("180")


def validate_coordinates(latitude: Decimal, longitude: Decimal) -> None:
    """Latitude in [-90, 90] and longitude in [-180, 180]."""
    if latitude is None or longitude is None:
        raise ValidationError("Latitude and longitude are required.")
    if not (LAT_MIN <= latitude <= LAT_MAX):
        raise ValidationError({"latitude": "Latitude must be between -90 and 90."})
    if not (LON_MIN <= longitude <= LON_MAX):
        raise ValidationError({"longitude": "Longitude must be between -180 and 180."})


def validate_speed(speed_kmh: Decimal | None) -> None:
    """Speed must be null or non-negative."""
    if speed_kmh is not None and speed_kmh < 0:
        raise ValidationError({"speed_kmh": "Speed must be zero or positive."})


def validate_accuracy(accuracy_m: Decimal | None) -> None:
    """Accuracy must be null or non-negative."""
    if accuracy_m is not None and accuracy_m < 0:
        raise ValidationError({"accuracy_m": "Accuracy must be zero or positive."})


def validate_capture_timestamp(captured_at: datetime, *, now: datetime | None = None) -> None:
    """Reject fixes from the far future (clock skew/spoofing) or the distant past."""
    if captured_at is None:
        raise ValidationError({"captured_at": "Capture time is required."})
    now = now or timezone.now()
    future_skew = timedelta(seconds=settings.LOCATION_MAX_FUTURE_SKEW_SECONDS)
    max_age = timedelta(seconds=settings.LOCATION_MAX_AGE_SECONDS)
    if captured_at > now + future_skew:
        raise ValidationError({"captured_at": "Capture time is too far in the future."})
    if captured_at < now - max_age:
        raise ValidationError({"captured_at": "Capture time is too old to accept."})
```

## `apps/web/__init__.py`

- **Folder:** `apps/web/`
- **File:** `__init__.py`

```python

```

## `apps/web/apps.py`

- **Folder:** `apps/web/`
- **File:** `apps.py`

```python
from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.web"
    label = "web"
    verbose_name = "Web"
```

## `apps/web/tests/__init__.py`

- **Folder:** `apps/web/tests/`
- **File:** `__init__.py`

```python

```

## `apps/web/tests/test_views.py`

- **Folder:** `apps/web/tests/`
- **File:** `test_views.py`

```python
"""Web page view tests: rendering and role-based access control."""

from __future__ import annotations

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Public map — open to everyone
# ---------------------------------------------------------------------------
def test_public_map_renders_for_anonymous(client):
    resp = client.get(reverse("web:public_map"))
    assert resp.status_code == 200
    assert "public/vehicle_map.html" in [t.name for t in resp.templates]


# ---------------------------------------------------------------------------
# Admin dashboard — admin only
# ---------------------------------------------------------------------------
def test_dashboard_redirects_anonymous_to_login(client):
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 302
    assert reverse("accounts:admin_login") in resp.url


def test_dashboard_forbidden_for_driver(client, driver_user):
    client.force_login(driver_user)
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 403


def test_dashboard_ok_for_admin(client, admin_user, vehicle):
    client.force_login(admin_user)
    resp = client.get(reverse("web:admin_dashboard"))
    assert resp.status_code == 200
    assert list(resp.context["vehicles"]) == [vehicle]


# ---------------------------------------------------------------------------
# Tracker — driver only
# ---------------------------------------------------------------------------
def test_tracker_redirects_anonymous_to_driver_login(client):
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 302
    assert reverse("accounts:driver_login") in resp.url


def test_tracker_forbidden_for_admin(client, admin_user):
    client.force_login(admin_user)
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 403


def test_tracker_ok_for_driver_and_sets_csrf_cookie(client, assigned_driver, vehicle):
    client.force_login(assigned_driver)
    resp = client.get(reverse("web:tracker"))
    assert resp.status_code == 200
    assert resp.context["assigned_vehicle"] == vehicle
    assert "csrftoken" in resp.cookies


# ---------------------------------------------------------------------------
# Trip history — admin only
# ---------------------------------------------------------------------------
def test_trip_history_ok_for_admin(client, admin_user):
    client.force_login(admin_user)
    resp = client.get(reverse("web:trip_history"))
    assert resp.status_code == 200


def test_trip_history_forbidden_for_driver(client, driver_user):
    client.force_login(driver_user)
    resp = client.get(reverse("web:trip_history"))
    assert resp.status_code == 403
```

## `apps/web/urls.py`

- **Folder:** `apps/web/`
- **File:** `urls.py`

```python
"""Web (server-rendered) page routes. Auth routes are included from accounts."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.PublicMapView.as_view(), name="public_map"),
    path("dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("tracker/", views.TrackerView.as_view(), name="tracker"),
    path("trips/", views.TripHistoryView.as_view(), name="trip_history"),
]
```

## `apps/web/views.py`

- **Folder:** `apps/web/`
- **File:** `views.py`

```python
"""Presentation views. These render templates only; domain logic lives in the
accounts, fleet, and tracking apps. Each view exposes the minimum context the
page needs and defers all data fetching to the REST API via polling.
"""

from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from apps.accounts.permissions import AdminRequiredMixin, DriverRequiredMixin
from apps.fleet.selectors import get_active_assignment_for_user, get_active_vehicles


class PublicMapView(TemplateView):
    """Public, read-only live map of active vehicles."""

    template_name = "public/vehicle_map.html"


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin live dashboard with a vehicle selector."""

    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        return context


@method_decorator(ensure_csrf_cookie, name="dispatch")
class TrackerView(DriverRequiredMixin, TemplateView):
    """Driver tracker page. Sets the CSRF cookie so fetch() can post fixes."""

    template_name = "tracker/tracker.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        assignment = get_active_assignment_for_user(self.request.user)
        context["assignment"] = assignment
        context["assigned_vehicle"] = assignment.vehicle if assignment else None
        return context


class TripHistoryView(AdminRequiredMixin, TemplateView):
    """Admin trip-history playback page."""

    template_name = "trips/trip_history.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["vehicles"] = get_active_vehicles()
        return context
```

## `build.sh`

- **Folder:** `./ (project root)`
- **File:** `build.sh`

```bash
#!/usr/bin/env bash
# Render build step. Runs on every deploy, with the service's environment
# variables (SECRET_KEY, DATABASE_URL, …) already available.
set -o errexit   # abort on first error
set -o nounset   # treat unset variables as an error
set -o pipefail  # a failing command in a pipe fails the whole pipe

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing production dependencies"
pip install -r requirements/production.txt

echo "==> Collecting static files"
python manage.py collectstatic --no-input

echo "==> Applying database migrations"
python manage.py migrate --no-input

echo "==> Build complete"
```

## `config/__init__.py`

- **Folder:** `config/`
- **File:** `__init__.py`

```python

```

## `config/asgi.py`

- **Folder:** `config/`
- **File:** `asgi.py`

```python
"""ASGI entrypoint. Present for completeness; the MVP runs under WSGI/Gunicorn."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
```

## `config/middleware.py`

- **Folder:** `config/`
- **File:** `middleware.py`

```python
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
```

## `config/settings/__init__.py`

- **Folder:** `config/settings/`
- **File:** `__init__.py`

```python

```

## `config/settings/base.py`

- **Folder:** `config/settings/`
- **File:** `base.py`

```python
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
```

## `config/settings/development.py`

- **Folder:** `config/settings/`
- **File:** `development.py`

```python
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
```

## `config/settings/production.py`

- **Folder:** `config/settings/`
- **File:** `production.py`

```python
"""Production settings: DEBUG off, full security, PostgreSQL, WhiteNoise.

Verify with ``python manage.py check --deploy`` before every release.
"""

from __future__ import annotations

from decouple import config

from .base import *
from .base import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS

DEBUG = False

# SECRET_KEY is mandatory in production (no insecure fallback).
SECRET_KEY = config("SECRET_KEY")

# Render provides the public hostname automatically; trust it without manual
# configuration so the service works out of the box.
RENDER_EXTERNAL_HOSTNAME = config("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# ---------------------------------------------------------------------------
# HTTPS / cookies / headers
# ---------------------------------------------------------------------------
# Render terminates TLS at its edge and forwards this header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Static files (WhiteNoise, cache-busted + compressed)
# ---------------------------------------------------------------------------
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Optional error monitoring (Sentry) — enabled only if SENTRY_DSN is set.
# ---------------------------------------------------------------------------
SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=0.0, cast=float),
        send_default_pii=False,
    )
```

## `config/settings/test.py`

- **Folder:** `config/settings/`
- **File:** `test.py`

```python
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
```

## `config/urls.py`

- **Folder:** `config/`
- **File:** `urls.py`

```python
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
```

## `config/wsgi.py`

- **Folder:** `config/`
- **File:** `wsgi.py`

```python
"""WSGI entrypoint. Defaults to production settings; overridden by the
DJANGO_SETTINGS_MODULE environment variable when set (e.g. locally)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
```

## `conftest.py`

- **Folder:** `./ (project root)`
- **File:** `conftest.py`

```python
"""Project-wide pytest fixtures.

Fixtures build the common object graph (admin, driver, vehicle, assignment)
through the real service layer, so the fixtures themselves exercise the code
they set up. Every fixture that touches the ORM depends on ``db`` so tests that
use them are granted database access transitively.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.utils import timezone

PASSWORD = "test-pass-9f2xQ"


@pytest.fixture
def password() -> str:
    """The plaintext password shared by all fixture users."""
    return PASSWORD


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset the cache around every test (isolates throttle/axes state)."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def admin_group(db) -> Group:
    return Group.objects.get_or_create(name=settings.ADMIN_GROUP)[0]


@pytest.fixture
def driver_group(db) -> Group:
    return Group.objects.get_or_create(name=settings.DRIVER_GROUP)[0]


@pytest.fixture
def admin_user(db, admin_group) -> User:
    """An authenticated Admin (group member, not a superuser)."""
    user = User.objects.create_user(username="admin1", password=PASSWORD)
    user.groups.add(admin_group)
    return user


@pytest.fixture
def superuser(db) -> User:
    return User.objects.create_superuser(username="root", password=PASSWORD)


@pytest.fixture
def make_driver(db, driver_group):
    """Factory: create a Driver user + active DriverProfile via the service."""
    from apps.accounts.services import create_driver

    def _make(username: str = "driver1", **kwargs):
        return create_driver(username=username, password=PASSWORD, **kwargs)

    return _make


@pytest.fixture
def driver_profile(make_driver):
    """A single active driver profile."""
    return make_driver(username="driver1", first_name="Dana", last_name="Rider")


@pytest.fixture
def driver_user(driver_profile) -> User:
    return driver_profile.user


@pytest.fixture
def make_vehicle(db):
    """Factory: create a Vehicle."""
    from apps.fleet.models import Vehicle

    counter = {"n": 0}

    def _make(bus_number: str | None = None, **kwargs):
        counter["n"] += 1
        if bus_number is None:
            bus_number = f"BUS-{counter['n']:03d}"
        return Vehicle.objects.create(bus_number=bus_number, **kwargs)

    return _make


@pytest.fixture
def vehicle(make_vehicle):
    return make_vehicle(bus_number="BUS-001", route_label="Campus Loop")


@pytest.fixture
def assignment(db, driver_profile, vehicle):
    """Active assignment linking the fixture driver to the fixture vehicle."""
    from apps.fleet.services import assign_driver_to_vehicle

    return assign_driver_to_vehicle(driver=driver_profile, vehicle=vehicle)


@pytest.fixture
def assigned_driver(driver_user, assignment) -> User:
    """A driver user who already holds an active vehicle assignment."""
    return driver_user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def add_point(db):
    """Factory: append a Location to a trip with full control over capture time.

    Bypasses the ingestion service so tests can create fixes at arbitrary
    (including stale/backdated) timestamps.
    """
    from apps.tracking.models import Location

    def _add(
        *,
        trip,
        captured_at=None,
        latitude=Decimal("23.777100"),
        longitude=Decimal("90.399400"),
        speed_kmh=None,
        accuracy_m=None,
    ) -> Location:
        return Location.objects.create(
            vehicle=trip.vehicle,
            driver=trip.driver,
            trip=trip,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            accuracy_m=accuracy_m,
            captured_at=captured_at or timezone.now(),
        )

    return _add


@pytest.fixture
def open_trip(db, vehicle, driver_profile):
    """An open trip for the fixture vehicle/driver."""
    from apps.tracking.models import Trip, TripStatus

    return Trip.objects.create(
        vehicle=vehicle,
        driver=driver_profile,
        started_at=timezone.now() - timedelta(minutes=1),
        status=TripStatus.OPEN,
    )
```

## `docs/api-contract.md`

- **Folder:** `docs/`
- **File:** `api-contract.md`

````markdown
# API contract (`/api/v1/`)

The tracking API is a small, versioned, session-authenticated JSON API. It is
the single data source for the map, the dashboard, the tracker, and trip
playback — the server-rendered pages load, then poll these endpoints.

- [Conventions](#conventions)
- [Authentication & roles](#authentication--roles)
- [Rate limits](#rate-limits)
- [Endpoints](#endpoints)
  - [POST `/locations/`](#post-locations)
  - [GET `/vehicles/latest-locations/`](#get-vehicleslatest-locations)
  - [GET `/vehicles/{id}/latest-location/`](#get-vehiclesidlatest-location)
  - [GET `/trips/`](#get-trips)
  - [GET `/trips/{id}/points/`](#get-tripsidpoints)
- [Error format](#error-format)
- [Status codes](#status-codes)

---

## Conventions

- **Base path:** `/api/v1/`. The version is in the path; a breaking change ships
  as `/api/v2/`.
- **Content type:** JSON only. The API renders `application/json` (no browsable
  HTML API in production).
- **Decimals as strings.** Latitude, longitude, speed, and accuracy are returned
  as **strings** (`"23.780000"`), never JSON floats, to preserve exact precision.
- **Timestamps** are ISO-8601, timezone-aware (UTC in storage).
- **Coordinates** are decimal degrees: latitude ∈ [-90, 90], longitude ∈ [-180, 180].

---

## Authentication & roles

Auth is **session cookie** based (`SessionAuthentication`) — the same session
issued by the web login. There are no API tokens. The API is **deny-by-default**
(`IsAuthenticated` globally); each endpoint below states its actual requirement.

| Endpoint                             | Who may call it                                  |
|--------------------------------------|--------------------------------------------------|
| `POST /locations/`                   | Active **driver** with a current vehicle assignment |
| `GET  /vehicles/latest-locations/`   | **Anyone** (output fields depend on role)        |
| `GET  /vehicles/{id}/latest-location/` | **Anyone** (output fields depend on role)      |
| `GET  /trips/`                       | **Admin** only                                   |
| `GET  /trips/{id}/points/`           | **Admin** only                                   |

The two public read endpoints return **more fields to an admin** (driver name,
accuracy) than to the public — the serializer is chosen by role server-side. See
the [privacy boundary](architecture.md#the-privacy-boundary).

State-changing requests (`POST`) require a valid **CSRF token**, since auth is
cookie-based. The tracker page sets the CSRF cookie (`ensure_csrf_cookie`) so its
`fetch()` calls can include the `X-CSRFToken` header.

---

## Rate limits

Two scoped throttles (per client, tunable via env):

| Scope             | Applies to                          | Default    | Env var                    |
|-------------------|-------------------------------------|------------|----------------------------|
| `location_ingest` | `POST /locations/`                  | `120/min`  | `THROTTLE_LOCATION_INGEST` |
| `public_read`     | the two `latest-location(s)` reads  | `240/min`  | `THROTTLE_PUBLIC_READ`     |

Exceeding a limit returns `429 Too Many Requests`.

---

## Endpoints

### POST `/locations/`

Submit one GPS fix. **The vehicle, driver, and trip are derived server-side**
from the caller's active assignment — the request body carries no vehicle field.
Idempotent on `client_event_id`.

**Auth:** active driver with an assignment. **Throttle:** `location_ingest`.

**Request body**

| Field             | Type            | Required | Notes                                    |
|-------------------|-----------------|:--------:|------------------------------------------|
| `client_event_id` | UUID            | ✅       | Client-generated; makes retries safe.    |
| `latitude`        | decimal string  | ✅       | [-90, 90], 6 dp.                          |
| `longitude`       | decimal string  | ✅       | [-180, 180], 6 dp.                        |
| `captured_at`     | ISO-8601        | ✅       | Device capture time; clock-skew checked.  |
| `speed_kmh`       | decimal string  | ➖       | ≥ 0 if present.                          |
| `accuracy_m`      | decimal string  | ➖       | ≥ 0 if present.                          |

```jsonc
// Example request
{
  "client_event_id": "5f2b1c9a-3e77-4a1c-9b0e-2a4d6f8c1e00",
  "latitude": "23.780123",
  "longitude": "90.412345",
  "captured_at": "2026-08-16T09:15:04Z",
  "speed_kmh": "28.50",
  "accuracy_m": "8.00"
}
```

**Response** — `201 Created` for a new fix, `200 OK` for a duplicate replay:

```jsonc
{
  "id": 4821,
  "trip_id": 137,
  "captured_at": "2026-08-16T09:15:04Z",
  "received_at": "2026-08-16T09:15:05.221Z",
  "duplicate": false          // true when client_event_id was already recorded
}
```

**Failure modes**

| Situation                                   | Status | Body                          |
|---------------------------------------------|:------:|-------------------------------|
| Not a driver / no active assignment         | `403`  | permission `detail`           |
| Assigned vehicle is inactive                | `409`  | `{"detail": "..."}`           |
| Coordinates / speed / timestamp invalid     | `400`  | field-keyed `detail`          |
| Over rate limit                             | `429`  | throttle `detail`             |

---

### GET `/vehicles/latest-locations/`

Latest fix for **every active vehicle** (vehicles with no fix yet are included,
marked `has_signal: false`, so the map can show them as unavailable).

**Auth:** anyone. **Throttle:** `public_read`.

```jsonc
{
  "count": 2,
  "results": [
    {
      "vehicle_id": 3,
      "bus_number": "CU-07",
      "route_label": "Main Gate - Faculty",
      "has_signal": true,
      "latitude": "23.780123",
      "longitude": "90.412345",
      "speed_kmh": "28.50",
      "captured_at": "2026-08-16T09:15:04Z",
      "age_seconds": 6,
      "is_stale": false
      // admin session ALSO receives: "driver_name": "...", "accuracy_m": "8.00"
    },
    {
      "vehicle_id": 5,
      "bus_number": "CU-11",
      "route_label": "Station - Campus",
      "has_signal": false,
      "latitude": null, "longitude": null, "speed_kmh": null,
      "captured_at": null, "age_seconds": null, "is_stale": true
    }
  ]
}
```

`is_stale` is `true` when the latest fix is older than `LOCATION_STALE_SECONDS`
(default 30). `driver_name` and `accuracy_m` appear **only** for an admin session.

---

### GET `/vehicles/{id}/latest-location/`

The single-vehicle version of the above. `404` if the vehicle does not exist or
is inactive. Same object shape as one `results` entry (again role-aware).

**Auth:** anyone. **Throttle:** `public_read`.

---

### GET `/trips/`

List trips for one vehicle, optionally on a single local date. **Admin only.**

**Query parameters**

| Param        | Required | Notes                                            |
|--------------|:--------:|--------------------------------------------------|
| `vehicle_id` | ✅       | Missing → `400`. Unknown → `404`.                |
| `date`       | ➖       | `YYYY-MM-DD` (local calendar day). Malformed → `400`. |

```jsonc
{
  "count": 1,
  "results": [
    {
      "id": 137,
      "vehicle_id": 3,
      "bus_number": "CU-07",
      "driver_name": "Rafiq Hasan",
      "started_at": "2026-08-16T08:55:00Z",
      "ended_at": null,
      "status": "OPEN"
    }
  ]
}
```

---

### GET `/trips/{id}/points/`

All points of a trip in **ascending** capture order — the polyline for playback.
**Admin only.** `404` if the trip does not exist.

**Query parameters** (optional time window within the trip's local day)

| Param   | Notes                                                    |
|---------|----------------------------------------------------------|
| `start` | `HH:MM` on the trip's local date. Malformed → `400`.     |
| `end`   | `HH:MM` on the trip's local date. Malformed → `400`.     |

```jsonc
{
  "trip_id": 137,
  "vehicle_id": 3,
  "status": "OPEN",
  "count": 2,
  "points": [
    { "latitude": "23.780010", "longitude": "90.412000", "speed_kmh": "0.00",  "captured_at": "2026-08-16T08:55:00Z" },
    { "latitude": "23.780123", "longitude": "90.412345", "speed_kmh": "28.50", "captured_at": "2026-08-16T08:55:10Z" }
  ]
}
```

---

## Error format

Errors are a JSON object with a `detail` key. For field validation, `detail` is
an object keyed by field name:

```jsonc
// 400 from an out-of-range coordinate
{ "detail": { "latitude": ["Latitude must be between -90 and 90."] } }

// 403 permission failure
{ "detail": "You must be an active driver with a current vehicle assignment." }
```

---

## Status codes

| Code  | Meaning in this API                                                    |
|-------|------------------------------------------------------------------------|
| `200` | OK — read succeeded, or an idempotent duplicate location replay.       |
| `201` | Created — a new location fix was stored.                               |
| `400` | Bad request — malformed body or query parameter, or invalid domain value. |
| `403` | Forbidden — not authenticated, or authenticated in the wrong role.     |
| `404` | Not found — unknown/inactive vehicle, or unknown trip.                 |
| `409` | Conflict — the driver's assigned vehicle is inactive.                  |
| `429` | Too many requests — a throttle scope was exceeded.                     |
````

## `docs/architecture.md`

- **Folder:** `docs/`
- **File:** `architecture.md`

````markdown
# Architecture

CU-VTS is a **modular Django monolith**: one deployable process, cleanly divided
into apps, each app internally layered so business rules live in one obvious
place. This document explains the shape of the system, why it is shaped that
way, and how a request flows through it.

- [System at a glance](#system-at-a-glance)
- [Apps and their responsibilities](#apps-and-their-responsibilities)
- [Internal layering](#internal-layering)
- [Data model](#data-model)
- [Request flows](#request-flows)
- [Trip lifecycle](#trip-lifecycle)
- [The privacy boundary](#the-privacy-boundary)
- [Configuration layering](#configuration-layering)
- [Security architecture](#security-architecture)
- [Why a monolith](#why-a-monolith)

---

## System at a glance

```
                        ┌─────────────────────────────────────────┐
   Driver phone  ──────▶│  /api/v1/locations/   (POST, session)    │
   (GPS, polling)       │      IsDriverWithActiveAssignment        │
                        └───────────────┬─────────────────────────┘
                                        │ record_vehicle_location()
                                        ▼
   Public browser ─────▶ GET /api/v1/vehicles/latest-locations/    │
   (Leaflet map, poll)         AllowAny · role-aware serializer     │
                                        ▲
   Admin browser  ─────▶ /dashboard/ /trips/  (server-rendered)     │
   (dashboard, poll)           AdminRequiredMixin                   │
                        └───────────────┴─────────────────────────┘
                                        │
                                        ▼
                        PostgreSQL (prod) / SQLite (dev, test)
```

Everything is one Gunicorn process. The browser pages are **server-rendered
Django templates** that, once loaded, poll the JSON API over HTTP for live data.
There are no WebSockets and no separate frontend build — the JavaScript that
drives the map and the tracker is plain vendored code served by WhiteNoise.

---

## Apps and their responsibilities

| App             | Owns                                                                 |
|-----------------|----------------------------------------------------------------------|
| `apps.accounts` | Users, the `Admin`/`Driver` role groups, `DriverProfile`, auth views, and the role predicates + view mixins used everywhere else. |
| `apps.fleet`    | `Vehicle` and `DriverAssignment` (which driver is driving which bus, right now). |
| `apps.tracking` | `Trip` and `Location`, GPS ingestion, trip lifecycle, staleness, and the **`/api/v1/` REST API** (`apps.tracking.api`). |
| `apps.web`      | Server-rendered pages: public map, admin dashboard, driver tracker, trip history. Presentation only — it renders templates and delegates all data work to the other apps. |

Dependencies flow one way: `web` and `tracking.api` depend on the domain apps;
the domain apps do not depend on the web layer. `accounts` is the base everyone
builds on (it defines `RequestUser` and the role checks).

---

## Internal layering

Every domain app follows the same four-layer split. This is the single most
important convention in the codebase:

| Layer          | File            | Rule                                                        |
|----------------|-----------------|-------------------------------------------------------------|
| **models**     | `models.py`     | Schema + database-level constraints. No business logic.     |
| **validators** | `validators.py` | Pure functions that assert domain rules; raise `ValidationError`. |
| **services**   | `services.py`   | The *only* place that writes. Transactional, idempotent, authoritative. |
| **selectors**  | `selectors.py`  | The *only* place reads are shaped. Return querysets/objects, no side effects. |

Views (both DRF and web) are thin: they parse input, call a service or selector,
and serialize the result. They never build a write inline. This keeps the
interesting logic — "which trip does this fix belong to?", "is this driver
allowed to submit?" — testable without an HTTP request, and it means the API and
the admin can share the exact same rules.

> **Reads and writes are deliberately separated.** A view that only displays data
> imports from `selectors`; a view that changes data imports from `services`.
> If you find yourself writing to the database from a selector, it belongs in a
> service instead.

---

## Data model

```
User ──1:1── DriverProfile ──┐
  │                          │ (driver)
  │ groups: Admin | Driver   │
                             ▼
        DriverAssignment ── FK(PROTECT) ──▶ Vehicle
        (is_active, starts_at, ends_at)        │
                                               │ (vehicle)
                             Trip ── FK(PROTECT) ──▶ Vehicle
                             (OPEN | COMPLETED)      │
                                  │                  │
                                  │ (trip)           │
                             Location ── FK(PROTECT) ─┘
                             (append-only GPS fixes)
```

### `accounts.DriverProfile`
One-to-one with the auth `User` (`related_name="driver_profile"`,
`on_delete=CASCADE`). Adds `employee_id` (unique, optional), `phone_number`,
and `is_active`. The `display_name` property returns the user's full name or
falls back to the username — this is the *only* driver identity ever shown, and
even then only to admins (see [privacy boundary](#the-privacy-boundary)).

Role membership is **not** stored on the profile. It lives in Django Groups
(`Admin`, `Driver`), which the `ensure_role_groups` signal creates automatically
on `post_migrate`. A user is a driver when they are in the `Driver` group **and**
have an active profile — `is_driver()` checks both.

### `fleet.Vehicle`
`bus_number` (unique), optional `registration_number` (unique), `route_label`,
and `is_active`. Only active vehicles appear on maps and in the API.

### `fleet.DriverAssignment`
The live "who drives what" link. `driver` and `vehicle` are both
`on_delete=PROTECT` (you cannot delete a driver or bus that has history).
Lifecycle is expressed with `is_active` + `starts_at`/`ends_at`. Two **partial
unique constraints** (`condition=Q(is_active=True)`) guarantee at the database
level that a driver has at most one active assignment and a vehicle has at most
one active driver:

```python
UniqueConstraint(fields=["driver"],  condition=Q(is_active=True), name="uniq_active_assignment_per_driver")
UniqueConstraint(fields=["vehicle"], condition=Q(is_active=True), name="uniq_active_assignment_per_vehicle")
```

This is why the API never trusts the client to say which vehicle it is: the
assignment *is* the authority. `get_active_assignment_for_user()` resolves an
authenticated driver to their one active assignment.

### `tracking.Trip`
Groups the location points for one driving session. `status` is `OPEN` or
`COMPLETED`; `started_at`/`ended_at` bound it. A partial unique constraint
enforces **one open trip per vehicle**:

```python
UniqueConstraint(fields=["vehicle"], condition=Q(status="OPEN"), name="uniq_open_trip_per_vehicle")
```

### `tracking.Location`
An **append-only** GPS fix — never edited after insert, which is what makes trip
playback trustworthy. Coordinates and speed/accuracy are `DecimalField`s.
`captured_at` is the device clock; `received_at` is the server clock.
`client_event_id` is a unique UUID supplied by the client for idempotency.
Four `CheckConstraint`s enforce valid ranges *in the database* (latitude
∈ [-90, 90], longitude ∈ [-180, 180], non-negative speed and accuracy) so bad
data cannot land even if application code has a bug. The validators in
`validators.py` mirror these exactly, giving a clean 400 before the DB is hit.

---

## Request flows

### A driver submits a location (`POST /api/v1/locations/`)

1. **Permission** — `IsDriverWithActiveAssignment` confirms the session user is
   an active driver *and* holds an active assignment. No assignment → `403`.
2. **Input validation** — `LocationIngestSerializer` validates the payload
   shape (UUID, decimal ranges, timestamp).
3. **Service** — `record_vehicle_location()` runs in a transaction:
   - If the `client_event_id` already exists, return the original row —
     `created=False`, `200`. (Idempotent retry.)
   - Resolve the vehicle **from the assignment**, never from the request body.
   - Run the domain validators (coordinates, speed, accuracy, clock-skew).
   - Find or open the vehicle's current trip (see below), then insert the fix.
4. **Response** — `201` on a new fix, `200` on a duplicate, with the trip id.

The driver *cannot* spoof another vehicle: the request body has no vehicle field
at all. The only identity it carries is `client_event_id`, and that only makes
retries safe.

### The public map reads positions (`GET /api/v1/vehicles/latest-locations/`)

`AllowAny`, but the output serializer is chosen by role:
`_location_serializer_for(request)` returns the **admin** serializer for admins
and the **public** serializer for everyone else. Same endpoint, different
disclosure — the privacy decision is made server-side, not by trusting a query
parameter.

### An admin opens the dashboard (`GET /dashboard/`)

`AdminDashboardView` extends `AdminRequiredMixin`. An anonymous user is
redirected to the admin login; an authenticated **non-admin** gets a `403`
(not a redirect loop). The template loads and then polls the same API as the
public map — but because the request carries an admin session, it receives the
admin serializer's richer fields.

---

## Trip lifecycle

```
      first fix arrives
   (no open trip for bus)
            │
            ▼
        ┌───────┐   fix arrives, trip fresh      ┌───────────┐
        │ OPEN  │ ─────────────────────────────▶ │  (append) │
        └───┬───┘                                 └───────────┘
            │
            │  (a) driver logs out
            │  (b) idle > TRIP_INACTIVITY_MINUTES, next fix arrives
            │  (c) close_stale_trips cron run
            ▼
        ┌───────────┐
        │ COMPLETED │  accepts no further locations
        └───────────┘
```

- **Opening** is lazy: the first fix for a bus with no open trip opens one
  (`_get_or_open_trip`). `open_trip()` tolerates a concurrent opener by catching
  the `IntegrityError` from `uniq_open_trip_per_vehicle` and reusing the winner.
- **Staleness** is defined by `TRIP_INACTIVITY_MINUTES` (default 10). If a fix
  arrives for a trip that has been idle past the threshold, that trip is closed
  (`reason="stale_on_ingest"`) and a fresh one opened — so a driver resuming
  after a long gap starts a clean session.
- **Logout** closes a driver's open trip (`close_open_trip_for_user`,
  `reason="driver_logout"`), so ending a shift ends the trip.
- **The safety net** is `manage.py close_stale_trips`, meant to run on a
  schedule (a Render cron): it closes every open trip idle past the threshold,
  catching trips a driver forgot to end.

---

## The privacy boundary

The public must see *where the buses are* but not *who is driving them*. That
line is drawn in exactly one place — `apps/tracking/api/serializers.py` — so it
cannot drift:

| Field                       | Public serializer | Admin serializer |
|-----------------------------|:-----------------:|:----------------:|
| `bus_number`, `route_label` | ✅                | ✅               |
| `latitude`, `longitude`     | ✅                | ✅               |
| `speed_kmh`                 | ✅                | ✅               |
| `is_stale`, `age_seconds`   | ✅                | ✅               |
| **`driver_name`**           | ❌                | ✅               |
| **`accuracy_m`**            | ❌                | ✅               |

`AdminVehicleLocationSerializer` *extends* the public one and adds only those two
fields, so the public serializer can never accidentally leak more than it lists —
disclosure is additive and explicit. Decimals are rendered as **strings**
(`str(loc.latitude)`) so JSON consumers get exact values with no float rounding.

---

## Configuration layering

Three settings modules stack on a shared `base.py`, all values read from the
environment through `python-decouple`:

```
config/settings/base.py           # everything shared; 12-factor env reads
        │
        ├── development.py         # DEBUG=True, SQLite, browsable API  (manage.py default)
        ├── test.py                # in-memory SQLite, fast hashing, axes/throttle off
        └── production.py          # DEBUG=False, HTTPS/HSTS, secure cookies, Postgres  (wsgi.py default)
```

Secrets never live in the repo. `base.py` carries an insecure dev-only
`SECRET_KEY` fallback so `manage.py` works without a `.env`; `production.py`
re-reads `SECRET_KEY` **with no default**, so a missing key fails fast at boot
rather than shipping a known key. See [`docs/decisions.md`](decisions.md) for
the reasoning behind the split.

---

## Security architecture

Defense is layered — no single check is load-bearing.

**Authentication & sessions.** DRF is configured **deny-by-default**: the global
permission is `IsAuthenticated`, and only the two public read endpoints opt into
`AllowAny`. Auth is session-based (`SessionAuthentication`); there are no API
tokens to leak. Sessions are HttpOnly, `SameSite=Lax`, and `Secure` in
production.

**Authorization in code.** Roles are enforced by predicates (`is_admin`,
`is_driver`) and the mixins/permission classes that call them — not by trusting
group membership at the template level. An authenticated user in the wrong role
gets a `403`, deliberately *not* a redirect to login (which would loop).

**Brute force.** `django-axes` locks an account after
`AXES_FAILURE_LIMIT` (default 5) failed logins per `(username, ip)`, cooling off
after `AXES_COOLOFF_HOURS`. `AxesStandaloneBackend` is first in the auth backends
so lockout is checked before password validation.

**Rate limiting.** DRF `ScopedRateThrottle` with two scopes:
`location_ingest` (default `120/min`) on the write path and `public_read`
(default `240/min`) on the map endpoints — both tunable via env.

**Ingestion integrity.** The vehicle is resolved from the server-side
assignment, never the client. `client_event_id` makes retries idempotent. A
clock-skew guard (`LOCATION_MAX_FUTURE_SKEW_SECONDS`,
`LOCATION_MAX_AGE_SECONDS`) rejects fixes from the far future or distant past.

**Response headers.** `config.middleware.SecurityHeadersMiddleware` emits a
**Content-Security-Policy** (`script-src 'self'` — injected inline scripts are
blocked; the Django admin gets a narrowly relaxed variant because it ships inline
scripts) and a **Permissions-Policy** (`geolocation=(self)` for the tracker,
camera/mic/payment denied). OpenStreetMap tile hosts are the only third-party
origin allowed, and only for `img-src`. Django's `SecurityMiddleware` adds HSTS
(1 year, `includeSubDomains`, `preload`), TLS redirect, nosniff, and referrer
policy; `X-Frame-Options: DENY` and `frame-ancestors 'none'` prevent framing.

**Reduced attack surface.** The Django admin is mounted behind a configurable
`ADMIN_URL_PREFIX` (default `django-admin/`, not `/admin/`) to cut automated
probing. `python manage.py check --deploy` passes with zero warnings under the
production settings.

---

## Why a monolith

A microservice split would add network hops, deployment surface, and cost — for
a system whose entire job is "receive small GPS writes, serve small position
reads" at campus scale (5–10 vehicles). A modular monolith keeps the operational
footprint to **one free Render service** while the internal layering preserves
the boundaries that matter. If a piece ever needs to scale independently, the
app/layer seams are already the natural extraction points. The full rationale,
including the Cloudflare Pages question, is in [`docs/decisions.md`](decisions.md).
````

## `docs/decisions.md`

- **Folder:** `docs/`
- **File:** `decisions.md`

```markdown
# Design decisions

Short, honest records of the choices that shaped CU-VTS — what was decided, why,
and what was given up. Newest concerns first.

- [ADR-1: A modular monolith, not microservices](#adr-1-a-modular-monolith-not-microservices)
- [ADR-2: Can the templates run on Cloudflare Pages?](#adr-2-can-the-templates-run-on-cloudflare-pages)
- [ADR-3: Render + Supabase for a 100%-free deploy](#adr-3-render--supabase-for-a-100-free-deploy)
- [ADR-4: HTTP polling, not WebSockets](#adr-4-http-polling-not-websockets)
- [ADR-5: Server-rendered templates, not an SPA](#adr-5-server-rendered-templates-not-an-spa)
- [ADR-6: Roles in Groups, enforced in code](#adr-6-roles-in-groups-enforced-in-code)
- [ADR-7: The services/selectors layering](#adr-7-the-servicesselectors-layering)
- [ADR-8: Idempotent ingestion + server-derived vehicle](#adr-8-idempotent-ingestion--server-derived-vehicle)
- [ADR-9: Decimals as strings; append-only locations](#adr-9-decimals-as-strings-append-only-locations)
- [ADR-10: Layered settings with a fail-fast prod secret](#adr-10-layered-settings-with-a-fail-fast-prod-secret)

---

## ADR-1: A modular monolith, not microservices

**Decision.** Ship one Django process, divided into apps (`accounts`, `fleet`,
`tracking`, `web`), each internally layered.

**Why.** The workload is tiny — a campus fleet of 5–10 buses posting small GPS
writes and serving small position reads. Microservices would add network hops,
multiple deploys, and cost, buying nothing at this scale. A modular monolith
runs as a single free service while keeping the boundaries that matter as clean
app/layer seams — the natural extraction points if anything ever needs to scale
alone.

**Trade-off.** Everything scales together. Acceptable: the free tier is the
constraint, not per-component scaling.

---

## ADR-2: Can the templates run on Cloudflare Pages?

**This was an explicit open question. The answer is _no_ — and they don't need to.**

**Decision.** Serve the HTML pages and the JSON API from the **same Django
service** on Render. Do not host the template layer on Cloudflare Pages.

**Why.** Cloudflare Pages hosts *static* assets and short-lived edge functions.
It cannot run a long-lived Python/WSGI process or hold pooled PostgreSQL
connections. But these pages are **server-rendered per request** and depend on
exactly the things Pages does not provide:

- the **session cookie** — the page renders differently for anonymous vs. driver
  vs. admin;
- a **CSRF token** minted per session for the tracker's `POST`s;
- **role-based template context** (`apps.accounts.context_processors.roles`);
- **live database reads** for the dashboard's vehicle list and trip history.

None of that is a static asset. Splitting the HTML onto Pages would mean
rebuilding server responsibilities at the edge — for no benefit, since the API
call still has to reach Django anyway.

**What is true instead.** The only genuinely static things are the vendored CSS/JS
(Bootstrap, Leaflet) and images, and **WhiteNoise already serves those from
inside the Django process**, compressed and cache-busted. There is no separate
static host to configure.

**The optional nuance.** You *could* place Cloudflare's **CDN/proxy** in front of
the Render URL to cache static assets at the edge and add DDoS protection. That
is Cloudflare-as-CDN, which is fine — but it is *not* "hosting the templates on
Cloudflare Pages." The application still runs on Render. For this project the CDN
is unnecessary at campus scale; it is noted only so the distinction is clear.

**Bottom line.** One Render service serves pages + API; WhiteNoise serves static
in-process; Cloudflare Pages does not apply.

---

## ADR-3: Render + Supabase for a 100%-free deploy

**Decision.** One Render **free web service** (Gunicorn) + **Supabase free
Postgres**. Config lives in [`render.yaml`](../render.yaml) and
[`build.sh`](../build.sh).

**Why.** Both have real free tiers with no card required to start, Render reads a
blueprint from the repo, and `dj-database-url` makes the database a single
`DATABASE_URL` swap. Use Supabase's **session-mode pooler (port 5432)**, which
supports the persistent connections Django expects (`conn_max_age`); the
transaction-mode pooler (6543) needs `DISABLE_SERVER_SIDE_CURSORS=True`, exposed
as an env toggle for that case.

**Trade-offs.** Render's free web service **sleeps when idle** and cold-starts on
the next request — hence `/healthz`, which an external uptime pinger can hit to
keep it warm. Free Postgres has limited storage/connections; fine for this
workload. SQLite remains the zero-setup local/test database.

---

## ADR-4: HTTP polling, not WebSockets

**Decision.** Browsers **poll** the REST API on an interval; no WebSockets, no
Channels, no ASGI server.

**Why.** WebSockets on free tiers are the first thing to be constrained, and they
force an ASGI deployment and connection-state management. For a map that is
perfectly useful refreshed every few seconds, polling a cache-cheap JSON endpoint
is simpler, survives reconnects trivially, and works within a plain Gunicorn WSGI
setup.

**Trade-off.** Updates are interval-fresh, not instant, and there is steady
low-volume request traffic (bounded by the `public_read` throttle). Right call
for the scale and the budget.

---

## ADR-5: Server-rendered templates, not an SPA

**Decision.** Django templates + Bootstrap 5 + Leaflet, all **self-hosted** under
`static/vendor/`. No React/Vue, no Node build step.

**Why.** The UI is a handful of pages. Server rendering gives session/CSRF/role
handling for free and keeps deployment to "collectstatic + Gunicorn." Self-hosting
the vendor libraries means the strict CSP (`script-src 'self'`) needs no CDN
exceptions, and the app has no runtime dependency on a third-party CDN. The only
external asset is OpenStreetMap map tiles.

**Trade-off.** No rich client-side app framework. Not needed here.

---

## ADR-6: Roles in Groups, enforced in code

**Decision.** Two Django Groups, `Admin` and `Driver` (auto-created by the
`ensure_role_groups` `post_migrate` signal). Authorization runs through the
`is_admin`/`is_driver` predicates and the mixins/DRF permission classes that call
them — **not** through template-level group checks.

**Why.** No custom user model needed; Groups are built in. Centralizing the
checks in predicates means one definition of "is this an admin," reused by web
views and the API alike. `is_driver` deliberately requires **both** group
membership and an active `DriverProfile`, so deactivating a driver's profile
revokes access without touching groups. A wrong-role user gets a **403**, not a
login redirect (which would loop).

**Trade-off.** Two sources to keep aligned (group + profile). The predicate hides
that behind one function.

---

## ADR-7: The services/selectors layering

**Decision.** In every domain app: **models → validators → services (writes) →
selectors (reads)**. Views are thin and call into services/selectors.

**Why.** It puts each kind of logic in one predictable place. All writes are
transactional and testable without HTTP; all reads are shaped in one spot and
reused by the API and the admin. Reads and writes are physically separated so a
display path can never accidentally mutate state.

**Trade-off.** More files per app and a little ceremony for trivial operations.
Pays off the moment logic is shared between the API and the web layer — which is
immediately.

---

## ADR-8: Idempotent ingestion + server-derived vehicle

**Decision.** Each fix carries a client-generated `client_event_id` (unique);
replays return the original row. The vehicle/driver/trip are resolved from the
**server-side active assignment**, never from the request body.

**Why.** Phones on flaky networks retry. Without idempotency, one fix becomes
many duplicate points and a corrupted trip. And if the client could name its own
vehicle, one driver could spoof another's bus — so the request body has no
vehicle field at all; the assignment is the sole authority. A clock-skew guard
rejects implausible `captured_at` values.

**Trade-off.** The client must generate a UUID per fix and drivers must hold an
active assignment to post. Both are cheap and correct.

---

## ADR-9: Decimals as strings; append-only locations

**Decision.** Coordinates/speed/accuracy are `DecimalField`s serialized as JSON
**strings**. `Location` rows are **append-only** (never edited after insert), and
value ranges are enforced by database `CheckConstraint`s mirrored by validators.

**Why.** JSON floats lose precision; strings keep exact decimal values. Immutable
location history is what makes trip playback trustworthy. Enforcing ranges in the
database means invalid data cannot persist even through an application bug; the
matching validators return a clean `400` before the DB is reached.

**Trade-off.** Clients parse numeric strings, and constraints are duplicated in
DB + validators. Both are deliberate: precision and defense-in-depth.

---

## ADR-10: Layered settings with a fail-fast prod secret

**Decision.** `base.py` + `development.py` / `test.py` / `production.py`, all env
values read via `python-decouple`. `base.py` has an insecure dev-only
`SECRET_KEY` fallback; `production.py` re-reads `SECRET_KEY` **with no default**.

**Why.** One codebase runs everywhere; only environment differs. The dev fallback
keeps `manage.py` usable with no `.env`. Making production's secret mandatory
means a missing key **fails at boot** instead of silently shipping a known,
public key. `manage.py check --deploy` passes clean under production settings.

**Trade-off.** Production must set real env vars — enforced on purpose, and
pre-wired in [`render.yaml`](../render.yaml) (`SECRET_KEY` is generated).
```

## `docs/testing.md`

- **Folder:** `docs/`
- **File:** `testing.md`

````markdown
# Testing

The suite is **104 tests** on `pytest` + `pytest-django`, run against an
in-memory SQLite database with fast hashing and lockout/throttling disabled for
determinism (`config/settings/test.py`). Total line+branch coverage is **79%**,
concentrated where it matters: the domain layers sit at **89–100%**.

- [Running the tests](#running-the-tests)
- [How the suite is organized](#how-the-suite-is-organized)
- [Fixtures](#fixtures)
- [What each area covers](#what-each-area-covers)
- [Coverage, and where the gaps are](#coverage-and-where-the-gaps-are)
- [Testing philosophy](#testing-philosophy)

---

## Running the tests

```bash
pytest                                          # whole suite, quiet
pytest --cov=apps --cov-report=term-missing     # with a coverage report
pytest apps/tracking/tests/test_location_api.py  # one file
pytest -k "idempotent"                          # by name
pytest -x -vv                                   # stop on first failure, verbose
```

`DJANGO_SETTINGS_MODULE` is pinned to `config.settings.test` in
`pyproject.toml`, so no environment setup is needed. The test settings **force
SQLite** even if a `DATABASE_URL` is present in your shell, so a local `.env`
pointing at Supabase can never be touched by a test run.

---

## How the suite is organized

Tests live beside the app they exercise, one file per concern:

```
apps/accounts/tests/
  test_authentication.py   role-aware login, logout-closes-trip, axes wiring
  test_permissions.py      is_admin / is_driver, the view mixins (403 vs redirect)
  test_services.py         create_driver and role assignment
apps/fleet/tests/
  test_models.py           Vehicle / DriverAssignment constraints & __str__
  test_selectors.py        active-vehicle and active-assignment resolution
  test_services.py         assign / reassign / deactivate (unique-active rules)
apps/tracking/tests/
  test_validators.py       coordinate, speed, accuracy, clock-skew rules
  test_services.py         ingestion, trip open/close, staleness, idempotency
  test_selectors.py        latest-location and trip-points queries
  test_location_api.py     POST /locations/ — auth, 201/200, 403/409/400
  test_public_api.py       latest-locations — privacy boundary by role
  test_trip_api.py         /trips/ and /trips/{id}/points/ — admin-only, params
apps/web/tests/
  test_views.py            page access control and rendered context
```

---

## Fixtures

`conftest.py` builds the common object graph **through the real service layer**,
so the fixtures themselves exercise the code they set up (creating a driver goes
through `accounts.services.create_driver`; assigning goes through
`fleet.services.assign_driver_to_vehicle`). Key fixtures:

| Fixture            | Gives you                                                        |
|--------------------|------------------------------------------------------------------|
| `admin_user`       | A member of the `Admin` group (not a superuser).                 |
| `superuser`        | A Django superuser (admin-by-superuser path).                    |
| `make_driver`      | Factory → Driver user + active `DriverProfile`.                  |
| `driver_profile` / `driver_user` | A single active driver and their `User`.           |
| `make_vehicle` / `vehicle` | Factory / one vehicle.                                   |
| `assignment` / `assigned_driver` | An active driver↔vehicle link, and the driver holding it. |
| `open_trip`        | An open trip for the fixture vehicle.                            |
| `add_point`        | Factory that appends a `Location` at an **arbitrary** `captured_at` (bypasses ingestion, so staleness/backdating can be tested). |
| `api_client`       | DRF `APIClient`.                                                 |

An autouse fixture clears the cache around every test, isolating throttle/axes
state between cases.

---

## What each area covers

- **Permissions & roles.** `is_admin`/`is_driver` for anonymous, wrong-group,
  right-group, superuser, and inactive-profile drivers; the mixins return a
  **403 for a logged-in wrong role** and redirect only the anonymous.
- **Ingestion service.** The happy path; **idempotent replay** of a
  `client_event_id` returning the original row; no-assignment and inactive-vehicle
  rejections; the trip open/reuse decision; staleness closing an idle trip and
  opening a fresh one.
- **Validators.** Boundary values for latitude/longitude, negative speed/accuracy,
  and both ends of the clock-skew window.
- **The API.** Status codes (201 vs 200 duplicate, 403/409/400), the **privacy
  boundary** (public response omits `driver_name`/`accuracy_m`; the same endpoint
  returns them to an admin session), and admin-only enforcement on the trip
  endpoints with parameter validation.
- **Web pages.** Access control per role and the context each page exposes.

---

## Coverage, and where the gaps are

Current `--cov=apps` snapshot (`branch = true`):

| Area                                   | Coverage |
|----------------------------------------|:--------:|
| `accounts/permissions.py`              | 100%     |
| `accounts/services.py`, `models.py`, `signals.py` | 100% |
| `accounts/views.py`                    | 97%      |
| `fleet/selectors.py`, `services.py`, `models.py` | 100% |
| `tracking/validators.py`               | 100%     |
| `tracking/selectors.py`                | 100%     |
| `tracking/api/serializers.py`, `permissions.py` | 100% |
| `tracking/api/views.py`                | 89%      |
| `tracking/services.py`                 | 91%      |
| `tracking/models.py`                   | 93%      |
| `web/views.py`                         | 100%     |
| **TOTAL**                              | **79%**  |

The gap between 79% and the high-90s is **deliberate and accounted for** — it is
almost entirely code that isn't domain logic:

- **`create_demo_data.py` (0%)** — the demo/seed command. Exercised by hand and
  intentionally not unit-tested; it exists to populate a dev/first-deploy database.
- **`close_stale_trips.py` (0%) and `seed_roles.py` (0%)** — thin management-command
  wrappers. The *logic* they call (`services.close_stale_trips`, the role signal)
  is fully covered; only the CLI shell around it is not.
- **`admin.py` (65–92%)** — Django admin registration/config. Declarative glue,
  low value to unit-test.
- The few missed lines in `tracking/services.py` and `api/views.py` are
  defensive branches (concurrent-`IntegrityError` fallbacks) that are hard to
  hit deterministically without racing the database.

In other words: **every business rule is tested; the untested remainder is
scaffolding and defensive fallbacks.**

---

## Testing philosophy

- **Test the domain, not the framework.** Services, selectors, validators, and
  permissions carry the logic and carry the coverage. Django's ORM and DRF are
  assumed to work.
- **Fixtures use the real code paths.** Building test data through the service
  layer means the setup is itself under test and can't drift from production
  behavior.
- **Assert the boundaries.** Privacy (public vs admin fields), authorization
  (403 vs redirect), idempotency, and constraint violations are tested at their
  edges, because those are the security- and correctness-critical seams.
- **Deterministic by construction.** In-memory SQLite, MD5 hashing, axes and
  throttles off, cache cleared per test, logging silenced — the suite gives the
  same result on every machine and in CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
````

## `manage.py`

- **Folder:** `./ (project root)`
- **File:** `manage.py`

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

## `pyproject.toml`

- **Folder:** `./ (project root)`
- **File:** `pyproject.toml`

```toml
[project]
name = "cu-vts"
version = "1.0.0"
description = "CU Vehicle Tracking System — a modular Django monolith for live campus bus tracking."
requires-python = ">=3.12,<3.14"

# ---------------------------------------------------------------------------
# Ruff — linter + formatter (replaces black, isort, flake8)
# ---------------------------------------------------------------------------
[tool.ruff]
line-length = 100
target-version = "py313"
# ``docs/*`` holds prose with illustrative (sometimes abbreviated) code fences;
# they are documentation, not source, so the formatter should not police them.
extend-exclude = ["**/migrations/*", "static/vendor/*", "docs/*"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "DJ",   # flake8-django
    "SIM",  # flake8-simplify
    "RUF",  # ruff-specific rules
]

[tool.ruff.lint.per-file-ignores]
# Settings modules layer via ``from .base import *`` — star imports are intentional.
"config/settings/*.py" = ["F403", "F405"]
# Migrations are generated; do not lint their style.
"**/migrations/*.py" = ["E501", "RUF012"]
# Django model ``Meta`` (ordering/constraints/indexes), DRF serializer ``Meta``
# and view ``permission_classes`` are framework idioms declared as plain
# class-level lists. RUF012's ``ClassVar`` demand does not fit them.
"**/models.py" = ["RUF012"]
"apps/*/api/serializers.py" = ["RUF012"]
"apps/*/api/views.py" = ["RUF012"]

[tool.ruff.lint.isort]
known-first-party = ["apps", "config"]

# ---------------------------------------------------------------------------
# pytest / pytest-django
# ---------------------------------------------------------------------------
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py", "*_test.py", "tests.py"]
testpaths = ["apps"]
addopts = "-q --strict-markers --strict-config"
filterwarnings = [
    # WhiteNoise warns that STATIC_ROOT has no collected files; expected in
    # tests/dev where collectstatic has not run. Harmless — silence just this.
    "ignore:No directory at:UserWarning",
]

# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------
[tool.coverage.run]
branch = true
source = ["apps"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/apps.py",
    "manage.py",
]

[tool.coverage.report]
show_missing = true
skip_covered = false
exclude_also = [
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "def __repr__",
]

# ---------------------------------------------------------------------------
# mypy (+ django-stubs). Configured pragmatically: type-checks first-party
# code without demanding annotations on every Django/DRF internal.
# ---------------------------------------------------------------------------
[tool.mypy]
python_version = "3.13"
plugins = ["mypy_django_plugin.main"]
ignore_missing_imports = true
warn_unused_configs = true
check_untyped_defs = true
exclude = ['(^|/)(migrations|tests)/', 'manage\.py']

[[tool.mypy.overrides]]
module = ["*.migrations.*", "config.settings.*"]
ignore_errors = true

[tool.django-stubs]
django_settings_module = "config.settings.development"
```

## `render.yaml`

- **Folder:** `./ (project root)`
- **File:** `render.yaml`

```yaml
# Render Blueprint for CU-VTS. Deploy by pointing Render at this repo
# (New + → Blueprint). Everything below provisions on Render's FREE tier.
#
# The database is NOT declared here: it lives on Supabase's free Postgres tier.
# After the first deploy, set DATABASE_URL (Supabase session-mode pooler) in the
# service's Environment settings. RENDER_EXTERNAL_HOSTNAME is injected by Render
# and auto-added to ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS by production settings.

services:
  - type: web
    name: cu-vts
    runtime: python
    plan: free
    region: singapore          # closest free region to Asia/Dhaka
    branch: main
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread --timeout 60 --graceful-timeout 30 --access-logfile - --error-logfile -"
    healthCheckPath: /healthz
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.1
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PIP_DISABLE_PIP_VERSION_CHECK
        value: "1"
      # Auto-generated 50+ char secret; never printed.
      - key: SECRET_KEY
        generateValue: true
      # Set these in the Render dashboard after the first deploy:
      - key: DATABASE_URL          # Supabase session-mode pooler URL (port 5432)
        sync: false
      - key: ALLOWED_HOSTS         # optional extra hostnames (custom domains)
        sync: false
      - key: ADMIN_URL_PREFIX      # obscure the admin path, e.g. "control-panel-9f2/"
        sync: false
      - key: SENTRY_DSN            # optional error reporting
        sync: false
```

## `requirements/base.txt`

- **Folder:** `requirements/`
- **File:** `base.txt`

```text
# Base runtime dependencies — required in every environment (dev, test, prod).
# These are imported at settings-load time (middleware / installed apps), so
# they must be present even when running the test suite against SQLite.
#
# Pinned with compatible-release ranges: patch/minor updates are allowed, but
# a major bump (which may break the API) requires a deliberate change here.

Django>=5.2,<5.3                 # LTS; security support through ~2028
djangorestframework>=3.15,<4.0   # versioned REST API layer
dj-database-url>=2.2,<3.0        # parse DATABASE_URL (Supabase Postgres)
python-decouple>=3.8,<4.0        # 12-factor settings from env / .env
django-axes>=6.5,<8.0            # brute-force login lockout
whitenoise>=6.6,<7.0             # static file serving (middleware, always on)
```

## `requirements/development.txt`

- **Folder:** `requirements/`
- **File:** `development.txt`

```text
# Local development & CI dependencies. Install with:
#   pip install -r requirements/development.txt
#
# Includes the production driver/server too, so a local venv can mirror
# production behaviour (e.g. run gunicorn or connect to Postgres) when needed.
-r production.txt

# Testing
pytest>=8.2,<9.0
pytest-django>=4.8,<5.0
pytest-cov>=5.0,<7.0

# Linting, formatting & typing
ruff>=0.6,<1.0
mypy>=1.10,<2.0
django-stubs[compatible-mypy]>=5.0,<6.0
djangorestframework-stubs>=3.15,<4.0
```

## `requirements/production.txt`

- **Folder:** `requirements/`
- **File:** `production.txt`

```text
# Production dependencies. Install with:  pip install -r requirements/production.txt
-r base.txt

gunicorn>=22.0,<24.0       # WSGI application server
psycopg[binary]>=3.2,<4.0  # PostgreSQL driver (Supabase); binary wheels, no build toolchain
sentry-sdk>=2.8,<3.0       # optional error reporting (enabled only when SENTRY_DSN is set)
```

## `runtime.txt`

- **Folder:** `./ (project root)`
- **File:** `runtime.txt`

```text
python-3.13.1
```

## `static/css/app.css`

- **Folder:** `static/css/`
- **File:** `app.css`

```css
/* CU-VTS application styles. Kept intentionally small; Bootstrap does the
   heavy lifting. Everything here supports the live maps and the tracker. */

:root {
  --vts-live: #198754;
  --vts-stale: #f0ad4e;
  --vts-offline: #adb5bd;
}

/* ---- Full-height map layouts --------------------------------------------- */
.vts-split {
  display: flex;
  flex: 1 1 auto;
  min-height: calc(100vh - 128px);
}

.vts-map {
  flex: 1 1 auto;
  min-height: 60vh;
  z-index: 0; /* keep tiles beneath Bootstrap dropdowns/navbar */
  background: #e9ecef;
}

.vts-side {
  width: 340px;
  flex: 0 0 340px;
  overflow-y: auto;
  background: var(--bs-body-bg);
  border-left: 1px solid var(--bs-border-color);
}

@media (max-width: 768px) {
  .vts-split { flex-direction: column; min-height: 0; }
  .vts-map { min-height: 55vh; }
  .vts-side {
    width: auto;
    flex: 1 1 auto;
    max-height: 45vh;
    border-left: 0;
    border-top: 1px solid var(--bs-border-color);
  }
}

/* ---- Vehicle list items -------------------------------------------------- */
.vehicle-item { cursor: pointer; border: 0; border-bottom: 1px solid var(--bs-border-color); }
.vehicle-item:hover { background: var(--bs-tertiary-bg); }
.vehicle-item.active { background: var(--bs-primary-bg-subtle); }

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  font-size: .75rem;
  font-weight: 600;
}
.status-badge::before {
  content: "";
  width: .6rem;
  height: .6rem;
  border-radius: 50%;
  background: var(--vts-offline);
}
.status-badge.is-live::before { background: var(--vts-live); }
.status-badge.is-stale::before { background: var(--vts-stale); }
.status-badge.is-offline::before { background: var(--vts-offline); }

/* ---- Map markers (div icons, no external images) ------------------------- */
.vts-marker {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, .35);
  background: var(--vts-offline);
}
.vts-marker.is-live { background: var(--vts-live); }
.vts-marker.is-stale { background: var(--vts-stale); }
.vts-marker.is-offline { background: var(--vts-offline); }

.vts-marker.is-live::after {
  content: "";
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  border: 2px solid var(--vts-live);
  animation: vts-pulse 1.8s ease-out infinite;
}
@keyframes vts-pulse {
  0%   { transform: scale(.6); opacity: .8; }
  100% { transform: scale(1.8); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .vts-marker.is-live::after { animation: none; }
}

.vts-label {
  background: rgba(33, 37, 41, .85);
  color: #fff;
  border-radius: .25rem;
  padding: 1px 6px;
  font-size: .7rem;
  font-weight: 600;
  white-space: nowrap;
  border: 0;
  box-shadow: none;
}
.vts-label::before { display: none; } /* hide Leaflet tooltip arrow */

/* ---- Tracker ------------------------------------------------------------- */
.tracker-power {
  width: 100%;
  max-width: 320px;
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: .05em;
}
.tracker-metric { font-variant-numeric: tabular-nums; }

.pulse-live { position: relative; }
.pulse-live::after {
  content: "";
  position: absolute;
  top: .35rem; right: .35rem;
  width: .6rem; height: .6rem;
  border-radius: 50%;
  background: var(--vts-live);
  box-shadow: 0 0 0 0 rgba(25, 135, 84, .6);
  animation: vts-beacon 1.5s infinite;
}
@keyframes vts-beacon {
  0%   { box-shadow: 0 0 0 0 rgba(25, 135, 84, .6); }
  70%  { box-shadow: 0 0 0 .6rem rgba(25, 135, 84, 0); }
  100% { box-shadow: 0 0 0 0 rgba(25, 135, 84, 0); }
}
@media (prefers-reduced-motion: reduce) {
  .pulse-live::after { animation: none; }
}

/* ---- Trip playback ------------------------------------------------------- */
.playback-controls { gap: .5rem; }
#playback-range { flex: 1 1 auto; }
```

## `static/js/admin-map.js`

- **Folder:** `static/js/`
- **File:** `admin-map.js`

```javascript
/* Admin live dashboard: same map engine, richer fields, plus a focus selector.
   The admin API returns driver name + accuracy, which the shared engine shows
   when admin:true. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;
  VTS.startLiveMap(mapEl, {
    admin: true,
    listEl: document.getElementById("vehicle-list"),
    focusSelect: document.getElementById("focus-select"),
    statusEl: document.getElementById("map-status"),
  });
})();
```

## `static/js/public-map.js`

- **Folder:** `static/js/`
- **File:** `public-map.js`

```javascript
/* Public live map: read-only, no driver identity. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;
  VTS.startLiveMap(mapEl, {
    admin: false,
    listEl: document.getElementById("vehicle-list"),
    statusEl: document.getElementById("map-status"),
  });
})();
```

## `static/js/tracker.js`

- **Folder:** `static/js/`
- **File:** `tracker.js`

```javascript
/* Driver tracker. Watches GPS, buffers the latest fix, and POSTs it on a
   fixed cadence with an idempotent client_event_id so retries never double
   count. The server derives vehicle/driver/trip from the session. */
"use strict";
(function () {
  const root = document.getElementById("tracker");
  if (!root) return; // no active assignment -> nothing to wire up

  const endpoint = root.dataset.endpoint;
  const intervalMs = parseInt(root.dataset.interval || "5000", 10);

  const els = {
    toggle: document.getElementById("toggle-btn"),
    state: document.getElementById("tracker-state"),
    card: document.getElementById("status-card"),
    lastSent: document.getElementById("last-sent"),
    accuracy: document.getElementById("accuracy"),
    coords: document.getElementById("coords"),
    speed: document.getElementById("speed"),
    error: document.getElementById("tracker-error"),
    count: document.getElementById("sent-count"),
  };

  let enabled = false;
  let watchId = null;
  let timer = null;
  let lastPosition = null; // freshest GeolocationPosition
  let pending = null;      // { payload } awaiting successful send
  let sentCount = 0;
  let wakeLock = null;

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    // RFC4122 v4 fallback using getRandomValues.
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    const h = Array.from(b, function (x) { return x.toString(16).padStart(2, "0"); });
    return h[0] + h[1] + h[2] + h[3] + "-" + h[4] + h[5] + "-" + h[6] + h[7] + "-" + h[8] + h[9] + "-" + h[10] + h[11] + h[12] + h[13] + h[14] + h[15];
  }

  function round(value, places) {
    if (value == null || isNaN(value)) return null;
    return Number(value.toFixed(places));
  }

  function setError(msg) {
    if (!els.error) return;
    els.error.textContent = msg || "";
    els.error.classList.toggle("d-none", !msg);
  }

  function setState(text, live) {
    if (els.state) els.state.textContent = text;
    if (els.card) els.card.classList.toggle("pulse-live", !!live);
  }

  async function requestWakeLock() {
    try {
      if ("wakeLock" in navigator) wakeLock = await navigator.wakeLock.request("screen");
    } catch (e) {
      /* wake lock is best-effort */
    }
  }
  function releaseWakeLock() {
    if (wakeLock) { wakeLock.release().catch(function () {}); wakeLock = null; }
  }

  function buildPayload(position) {
    const c = position.coords;
    const speedKmh = c.speed != null && c.speed >= 0 ? round(c.speed * 3.6, 2) : null;
    return {
      client_event_id: uuid(),
      latitude: round(c.latitude, 6),
      longitude: round(c.longitude, 6),
      speed_kmh: speedKmh,
      accuracy_m: c.accuracy != null ? round(c.accuracy, 2) : null,
      captured_at: new Date(position.timestamp).toISOString(),
    };
  }

  function onPosition(position) {
    lastPosition = position;
    const c = position.coords;
    if (els.coords) els.coords.textContent = c.latitude.toFixed(5) + ", " + c.longitude.toFixed(5);
    if (els.accuracy) els.accuracy.textContent = c.accuracy != null ? "± " + Math.round(c.accuracy) + " m" : "—";
    if (els.speed) els.speed.textContent = c.speed != null && c.speed >= 0 ? Math.round(c.speed * 3.6) + " km/h" : "—";
    setError("");
  }

  function onGeoError(err) {
    if (err.code === err.PERMISSION_DENIED) {
      setError("Location permission denied. Enable it in your browser settings, then start again.");
      stop();
    } else if (err.code === err.POSITION_UNAVAILABLE) {
      setError("Location unavailable right now — searching for signal…");
    } else if (err.code === err.TIMEOUT) {
      setError("Still acquiring GPS…");
    }
  }

  async function tick() {
    if (!enabled) return;
    if (!pending) {
      if (!lastPosition) { setState("Waiting for GPS…", true); return; }
      pending = { payload: buildPayload(lastPosition) };
    }
    try {
      const res = await VTS.postJSON(endpoint, pending.payload);
      pending = null;
      if (res && !res.duplicate) sentCount += 1;
      if (els.count) els.count.textContent = String(sentCount);
      if (els.lastSent) els.lastSent.textContent = VTS.fmtTime(new Date().toISOString());
      setState("Sharing location", true);
      setError("");
    } catch (e) {
      if (e.status === 403) {
        setError("You have no active vehicle assignment. Contact an administrator.");
        stop();
      } else if (e.status === 409) {
        setError("Your assigned vehicle is inactive. Contact an administrator.");
        stop();
      } else if (e.status === 400) {
        // Bad fix (e.g. clock skew). Drop it and continue with the next one.
        pending = null;
        setError("A GPS reading was rejected; continuing…");
      } else if (e.status === 429) {
        setError("Sending too fast — easing off briefly…");
      } else {
        setError("Network issue — will retry.");
      }
    }
  }

  function start() {
    if (enabled) return;
    if (!("geolocation" in navigator)) {
      setError("This device/browser does not support location sharing.");
      return;
    }
    enabled = true;
    sentCount = 0;
    if (els.count) els.count.textContent = "0";
    setState("Starting…", true);
    setButton();
    requestWakeLock();
    watchId = navigator.geolocation.watchPosition(onPosition, onGeoError, {
      enableHighAccuracy: true,
      maximumAge: 4000,
      timeout: 15000,
    });
    timer = setInterval(tick, intervalMs);
    tick();
  }

  function stop() {
    enabled = false;
    if (watchId != null) { navigator.geolocation.clearWatch(watchId); watchId = null; }
    if (timer != null) { clearInterval(timer); timer = null; }
    pending = null;
    releaseWakeLock();
    setState("Not sharing", false);
    setButton();
  }

  function setButton() {
    if (!els.toggle) return;
    if (enabled) {
      els.toggle.textContent = "Stop sharing";
      els.toggle.classList.remove("btn-success");
      els.toggle.classList.add("btn-danger");
    } else {
      els.toggle.textContent = "Start sharing";
      els.toggle.classList.remove("btn-danger");
      els.toggle.classList.add("btn-success");
    }
  }

  if (els.toggle) {
    els.toggle.addEventListener("click", function () {
      if (enabled) stop();
      else start();
    });
  }

  // Re-acquire the wake lock when returning to the tab while sharing.
  document.addEventListener("visibilitychange", function () {
    if (enabled && document.visibilityState === "visible") requestWakeLock();
  });

  // Best-effort: stop cleanly if the page is being unloaded.
  window.addEventListener("pagehide", function () { releaseWakeLock(); });

  setButton();
  setState("Not sharing", false);
})();
```

## `static/js/trip-history.js`

- **Folder:** `static/js/`
- **File:** `trip-history.js`

```javascript
/* Admin trip history: pick a vehicle + date, list that day's trips, then draw a
   selected trip as a polyline with a scrubber/playback cursor. */
"use strict";
(function () {
  const mapEl = document.getElementById("history-map");
  if (!mapEl) return;

  const tripsUrl = mapEl.dataset.tripsUrl; // /api/v1/trips/
  const center = [parseFloat(mapEl.dataset.centerLat), parseFloat(mapEl.dataset.centerLng)];
  const zoom = parseInt(mapEl.dataset.zoom || "13", 10);

  const vehicleSelect = document.getElementById("vehicle-select");
  const dateInput = document.getElementById("date-input");
  const startTime = document.getElementById("start-time");
  const endTime = document.getElementById("end-time");
  const loadBtn = document.getElementById("load-trips");
  const tripListEl = document.getElementById("trip-list");
  const playRange = document.getElementById("playback-range");
  const playBtn = document.getElementById("play-btn");
  const playInfo = document.getElementById("play-info");
  const errorEl = document.getElementById("history-error");

  const map = L.map(mapEl, { center: center, zoom: zoom });
  VTS.tileLayer().addTo(map);

  let layers = [];
  let cursor = null;
  let points = [];
  let playTimer = null;
  let activeTripId = null;

  function setError(msg) {
    if (!errorEl) return;
    errorEl.textContent = msg || "";
    errorEl.classList.toggle("d-none", !msg);
  }

  function clearMap() {
    stopPlayback();
    layers.forEach(function (l) { map.removeLayer(l); });
    layers = [];
    cursor = null;
    points = [];
    if (playRange) { playRange.value = 0; playRange.max = 0; playRange.disabled = true; }
    if (playBtn) playBtn.disabled = true;
    if (playInfo) playInfo.textContent = "";
  }

  async function loadTrips() {
    setError("");
    clearMap();
    if (tripListEl) tripListEl.innerHTML = "";
    activeTripId = null;
    const vid = vehicleSelect ? vehicleSelect.value : "";
    if (!vid) { setError("Choose a vehicle first."); return; }
    const params = new URLSearchParams({ vehicle_id: vid });
    if (dateInput && dateInput.value) params.set("date", dateInput.value);
    let data;
    try {
      data = await VTS.getJSON(tripsUrl + "?" + params.toString());
    } catch (e) {
      setError(e.message);
      return;
    }
    renderTripList((data && data.results) || []);
  }

  function renderTripList(trips) {
    if (!tripListEl) return;
    if (!trips.length) {
      tripListEl.innerHTML = '<div class="p-3 text-center text-muted small">No trips found for that day.</div>';
      return;
    }
    const html = trips
      .map(function (t) {
        const span = VTS.fmtTime(t.started_at) + " – " + (t.ended_at ? VTS.fmtTime(t.ended_at) : "ongoing");
        const isOpen = String(t.status || "").toUpperCase() === "OPEN";
        const badge = isOpen
          ? '<span class="badge text-bg-success">open</span>'
          : '<span class="badge text-bg-secondary">done</span>';
        return (
          '<button type="button" class="list-group-item list-group-item-action" data-id="' + t.id + '">' +
          '<div class="d-flex justify-content-between align-items-center">' +
          "<span class=\"fw-semibold\">Trip #" + t.id + "</span>" + badge + "</div>" +
          '<div class="small text-muted">' + VTS.escapeHtml(span) + "</div>" +
          (t.driver_name ? '<div class="small text-muted">👤 ' + VTS.escapeHtml(t.driver_name) + "</div>" : "") +
          "</button>"
        );
      })
      .join("");
    tripListEl.innerHTML = '<div class="list-group list-group-flush">' + html + "</div>";
    tripListEl.querySelectorAll("button[data-id]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        tripListEl.querySelectorAll("button[data-id]").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        loadPoints(parseInt(btn.dataset.id, 10));
      });
    });
  }

  async function loadPoints(tripId) {
    setError("");
    activeTripId = tripId;
    const params = new URLSearchParams();
    if (startTime && startTime.value) params.set("start", startTime.value);
    if (endTime && endTime.value) params.set("end", endTime.value);
    const qs = params.toString();
    const url = tripsUrl + tripId + "/points/" + (qs ? "?" + qs : "");
    let data;
    try {
      data = await VTS.getJSON(url);
    } catch (e) {
      setError(e.message);
      return;
    }
    drawTrip((data && data.points) || []);
  }

  function drawTrip(rawPoints) {
    clearMap();
    points = rawPoints.map(function (p) {
      return {
        latlng: [parseFloat(p.latitude), parseFloat(p.longitude)],
        time: p.captured_at,
        speed: p.speed_kmh,
      };
    });
    if (!points.length) {
      setError("This trip has no points in the selected range.");
      return;
    }
    const latlngs = points.map(function (p) { return p.latlng; });
    const line = L.polyline(latlngs, { color: "#0d6efd", weight: 4, opacity: 0.85 }).addTo(map);
    const startDot = L.circleMarker(latlngs[0], { radius: 6, color: "#198754", fillColor: "#198754", fillOpacity: 1 }).addTo(map).bindTooltip("Start");
    const endDot = L.circleMarker(latlngs[latlngs.length - 1], { radius: 6, color: "#dc3545", fillColor: "#dc3545", fillOpacity: 1 }).addTo(map).bindTooltip("End");
    cursor = L.marker(latlngs[0], { icon: VTS.markerIcon("live") }).addTo(map);
    layers.push(line, startDot, endDot, cursor);
    map.fitBounds(line.getBounds(), { padding: [40, 40] });

    if (playRange) {
      playRange.max = String(points.length - 1);
      playRange.value = "0";
      playRange.disabled = points.length < 2;
    }
    if (playBtn) playBtn.disabled = points.length < 2;
    setCursor(0);
  }

  function setCursor(i) {
    if (!points.length) return;
    const idx = Math.max(0, Math.min(i, points.length - 1));
    const p = points[idx];
    if (cursor) cursor.setLatLng(p.latlng);
    if (playRange) playRange.value = String(idx);
    if (playInfo) {
      const speed = VTS.fmtSpeed(p.speed);
      playInfo.textContent =
        "Point " + (idx + 1) + " / " + points.length + " · " + VTS.fmtTime(p.time) + (speed ? " · " + speed : "");
    }
  }

  function stopPlayback() {
    if (playTimer != null) { clearInterval(playTimer); playTimer = null; }
    if (playBtn) playBtn.textContent = "▶ Play";
  }

  function togglePlayback() {
    if (playTimer != null) { stopPlayback(); return; }
    if (!points.length) return;
    let i = playRange ? parseInt(playRange.value, 10) : 0;
    if (i >= points.length - 1) i = 0; // restart from beginning
    if (playBtn) playBtn.textContent = "⏸ Pause";
    playTimer = setInterval(function () {
      if (i >= points.length - 1) { setCursor(points.length - 1); stopPlayback(); return; }
      i += 1;
      setCursor(i);
    }, 400);
  }

  if (loadBtn) loadBtn.addEventListener("click", loadTrips);
  if (playRange) playRange.addEventListener("input", function () { stopPlayback(); setCursor(parseInt(playRange.value, 10)); });
  if (playBtn) playBtn.addEventListener("click", togglePlayback);

  clearMap();
})();
```

## `static/js/vts-common.js`

- **Folder:** `static/js/`
- **File:** `vts-common.js`

```javascript
/* Shared CU-VTS front-end helpers. Loaded before every page script.
   Exposes a single global: window.VTS. No inline scripts anywhere, so the
   strict Content-Security-Policy (script-src 'self') stays intact. */
"use strict";

window.VTS = (function () {
  // ---- CSRF (Django) ------------------------------------------------------
  function getCookie(name) {
    const match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return match ? decodeURIComponent(match.pop()) : null;
  }

  // ---- Fetch --------------------------------------------------------------
  async function getJSON(url, options) {
    const opts = Object.assign(
      { headers: { Accept: "application/json" }, credentials: "same-origin" },
      options || {}
    );
    const res = await fetch(url, opts);
    if (!res.ok) {
      let detail = "Request failed (" + res.status + ")";
      try {
        const body = await res.json();
        if (body && body.detail) {
          detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
        }
      } catch (e) {
        /* non-JSON error body */
      }
      const err = new Error(detail);
      err.status = res.status;
      throw err;
    }
    return res.status === 204 ? null : res.json();
  }

  async function postJSON(url, payload) {
    return getJSON(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken") || "",
      },
      body: JSON.stringify(payload),
    });
  }

  // ---- Formatting ---------------------------------------------------------
  function escapeHtml(value) {
    if (value == null) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function fmtAge(seconds) {
    if (seconds == null) return "no signal";
    if (seconds < 60) return seconds + "s ago";
    const m = Math.floor(seconds / 60);
    if (m < 60) return m + "m ago";
    const h = Math.floor(m / 60);
    return h + "h ago";
  }

  function fmtTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return isNaN(d) ? "—" : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function fmtSpeed(speedKmh) {
    if (speedKmh == null) return null;
    const n = parseFloat(speedKmh);
    return isNaN(n) ? null : Math.round(n) + " km/h";
  }

  // ---- Leaflet helpers ----------------------------------------------------
  function tileLayer() {
    return L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    });
  }

  function statusOf(vehicle) {
    if (!vehicle.has_signal) return "offline";
    return vehicle.is_stale ? "stale" : "live";
  }

  function markerIcon(status) {
    return L.divIcon({
      className: "vts-marker-wrap",
      html: '<div class="vts-marker is-' + status + '"></div>',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
      popupAnchor: [0, -10],
    });
  }

  // ---- Live map engine (shared by public + admin dashboards) --------------
  // Renders one marker per vehicle and an optional sidebar list. The admin
  // flag simply reveals the extra fields the admin API already returns.
  function startLiveMap(mapEl, config) {
    const settings = config || {};
    const admin = !!settings.admin;
    const listEl = settings.listEl || null;
    const focusSelect = settings.focusSelect || null;
    const statusEl = settings.statusEl || null;

    const endpoint = mapEl.dataset.endpoint;
    const poll = parseInt(mapEl.dataset.poll || "8000", 10);
    const center = [parseFloat(mapEl.dataset.centerLat), parseFloat(mapEl.dataset.centerLng)];
    const zoom = parseInt(mapEl.dataset.zoom || "13", 10);

    const map = L.map(mapEl, { center: center, zoom: zoom, zoomControl: true });
    tileLayer().addTo(map);

    const markers = new Map(); // vehicle_id -> { marker, latlng }
    let didFit = false;

    function popupHtml(v, status) {
      const rows = [];
      rows.push("<strong>" + escapeHtml(v.bus_number) + "</strong>");
      if (v.route_label) rows.push('<div class="text-muted small">' + escapeHtml(v.route_label) + "</div>");
      rows.push('<div class="small mt-1">Status: <span class="status-badge is-' + status + '">' + status.toUpperCase() + "</span></div>");
      const speed = fmtSpeed(v.speed_kmh);
      if (speed) rows.push('<div class="small">Speed: ' + speed + "</div>");
      rows.push('<div class="small">Updated: ' + escapeHtml(fmtAge(v.age_seconds)) + "</div>");
      if (admin && v.driver_name) rows.push('<div class="small">Driver: ' + escapeHtml(v.driver_name) + "</div>");
      if (admin && v.accuracy_m) rows.push('<div class="small text-muted">± ' + escapeHtml(v.accuracy_m) + " m</div>");
      return rows.join("");
    }

    function upsertMarker(v, status) {
      const latlng = [parseFloat(v.latitude), parseFloat(v.longitude)];
      let entry = markers.get(v.vehicle_id);
      if (!entry) {
        const marker = L.marker(latlng, { icon: markerIcon(status), title: v.bus_number });
        marker.addTo(map);
        marker.bindTooltip(v.bus_number, { permanent: true, direction: "top", className: "vts-label", offset: [0, -10] });
        entry = { marker: marker, latlng: latlng };
        markers.set(v.vehicle_id, entry);
      } else {
        entry.marker.setLatLng(latlng);
        entry.marker.setIcon(markerIcon(status));
        entry.latlng = latlng;
      }
      entry.marker.bindPopup(popupHtml(v, status));
      return latlng;
    }

    function removeMarker(vehicleId) {
      const entry = markers.get(vehicleId);
      if (entry) {
        map.removeLayer(entry.marker);
        markers.delete(vehicleId);
      }
    }

    function focus(vehicleId) {
      const entry = markers.get(vehicleId);
      if (entry) {
        map.setView(entry.latlng, Math.max(map.getZoom(), 16));
        entry.marker.openPopup();
      }
    }

    function renderList(vehicles) {
      if (!listEl) return;
      if (!vehicles.length) {
        listEl.innerHTML = '<div class="p-4 text-center text-muted small">No active vehicles.</div>';
        return;
      }
      const html = vehicles
        .map(function (v) {
          const status = statusOf(v);
          const speed = fmtSpeed(v.speed_kmh);
          const driver = admin && v.driver_name ? '<div class="small text-muted">👤 ' + escapeHtml(v.driver_name) + "</div>" : "";
          return (
            '<button type="button" class="list-group-item list-group-item-action vehicle-item" data-id="' + v.vehicle_id + '">' +
            '<div class="d-flex justify-content-between align-items-start">' +
            "<div><div class=\"fw-semibold\">" + escapeHtml(v.bus_number) + "</div>" +
            '<div class="small text-muted">' + escapeHtml(v.route_label || "—") + "</div>" + driver + "</div>" +
            '<div class="text-end">' +
            '<span class="status-badge is-' + status + '">' + status + "</span>" +
            '<div class="small text-muted">' + escapeHtml(fmtAge(v.age_seconds)) + "</div>" +
            (speed ? '<div class="small">' + speed + "</div>" : "") +
            "</div></div></button>"
          );
        })
        .join("");
      listEl.innerHTML = '<div class="list-group list-group-flush">' + html + "</div>";
      listEl.querySelectorAll(".vehicle-item").forEach(function (btn) {
        btn.addEventListener("click", function () {
          focus(parseInt(btn.dataset.id, 10));
        });
      });
    }

    function populateSelect(vehicles) {
      if (!focusSelect) return;
      const current = focusSelect.value;
      const opts = ['<option value="">Focus a vehicle…</option>'].concat(
        vehicles.map(function (v) {
          return '<option value="' + v.vehicle_id + '">' + escapeHtml(v.bus_number) + "</option>";
        })
      );
      focusSelect.innerHTML = opts.join("");
      if (current) focusSelect.value = current;
    }

    function setStatus(text, isError) {
      if (!statusEl) return;
      statusEl.textContent = text;
      statusEl.classList.toggle("text-danger", !!isError);
    }

    async function refresh() {
      let data;
      try {
        data = await getJSON(endpoint);
      } catch (e) {
        setStatus("Connection problem — retrying…", true);
        return;
      }
      const vehicles = (data && data.results) || [];
      const seen = new Set();
      const bounds = [];
      vehicles.forEach(function (v) {
        seen.add(v.vehicle_id);
        const status = statusOf(v);
        if (v.has_signal) {
          const latlng = upsertMarker(v, status);
          bounds.push(latlng);
        } else {
          removeMarker(v.vehicle_id);
        }
      });
      // Drop markers for vehicles that disappeared from the feed.
      Array.from(markers.keys()).forEach(function (id) {
        if (!seen.has(id)) removeMarker(id);
      });
      renderList(vehicles);
      populateSelect(vehicles);
      const live = vehicles.filter(function (v) { return v.has_signal && !v.is_stale; }).length;
      setStatus(live + " live · " + vehicles.length + " active · updated " + fmtTime(new Date().toISOString()));
      if (!didFit && bounds.length) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
        didFit = true;
      }
    }

    if (focusSelect) {
      focusSelect.addEventListener("change", function () {
        if (focusSelect.value) focus(parseInt(focusSelect.value, 10));
      });
    }

    refresh();
    const timer = setInterval(refresh, poll);
    // Pause polling when the tab is hidden to save the free-tier request budget.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") refresh();
    });

    return { map: map, refresh: refresh, focus: focus, stop: function () { clearInterval(timer); } };
  }

  return {
    getCookie: getCookie,
    getJSON: getJSON,
    postJSON: postJSON,
    escapeHtml: escapeHtml,
    fmtAge: fmtAge,
    fmtTime: fmtTime,
    fmtSpeed: fmtSpeed,
    tileLayer: tileLayer,
    statusOf: statusOf,
    markerIcon: markerIcon,
    startLiveMap: startLiveMap,
  };
})();
```

## `templates/accounts/_login_card.html`

- **Folder:** `templates/accounts/`
- **File:** `_login_card.html`

```html
{% comment %}
Shared login card. Included by admin_login.html and driver_login.html.
Expected context: form (from LoginView), next, and the caller-supplied
heading / subtitle / accent / alt_text / alt_url / alt_label.
{% endcomment %}
<div class="row justify-content-center">
  <div class="col-12 col-sm-10 col-md-7 col-lg-5">
    <div class="card shadow-sm mt-4">
      <div class="card-body p-4 p-md-5">
        <h1 class="h4 mb-1">{{ heading }}</h1>
        <p class="text-muted small mb-4">{{ subtitle }}</p>

        {% if form.non_field_errors %}
          <div class="alert alert-danger py-2 mb-3">
            {% for error in form.non_field_errors %}<div>{{ error }}</div>{% endfor %}
          </div>
        {% endif %}

        <form method="post" novalidate>
          {% csrf_token %}
          <input type="hidden" name="next" value="{{ next }}">
          <div class="mb-3">
            <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
            {{ form.username }}
            {% for error in form.username.errors %}
              <div class="text-danger small mt-1">{{ error }}</div>
            {% endfor %}
          </div>
          <div class="mb-3">
            <label for="{{ form.password.id_for_label }}" class="form-label">Password</label>
            {{ form.password }}
            {% for error in form.password.errors %}
              <div class="text-danger small mt-1">{{ error }}</div>
            {% endfor %}
          </div>
          <button type="submit" class="btn btn-{{ accent|default:'primary' }} w-100">Sign in</button>
        </form>

        {% if alt_url %}
          <hr class="my-4">
          <p class="small text-center text-muted mb-0">
            {{ alt_text }} <a href="{{ alt_url }}">{{ alt_label }}</a>
          </p>
        {% endif %}
      </div>
    </div>
  </div>
</div>
```

## `templates/accounts/admin_login.html`

- **Folder:** `templates/accounts/`
- **File:** `admin_login.html`

```html
{% extends "base.html" %}
{% block title %}Admin Login · CU-VTS{% endblock %}
{% block content %}
  {% url 'accounts:driver_login' as driver_url %}
  {% include "accounts/_login_card.html" with heading="Admin sign in" subtitle="Manage the fleet, monitor live vehicles, and review trip history." accent="primary" alt_text="Are you a driver?" alt_url=driver_url alt_label="Use the driver login" %}
{% endblock %}
```

## `templates/accounts/driver_login.html`

- **Folder:** `templates/accounts/`
- **File:** `driver_login.html`

```html
{% extends "base.html" %}
{% block title %}Driver Login · CU-VTS{% endblock %}
{% block content %}
  {% url 'accounts:admin_login' as admin_url %}
  {% include "accounts/_login_card.html" with heading="Driver sign in" subtitle="Sign in to start sharing your bus location while on duty." accent="success" alt_text="Fleet administrator?" alt_url=admin_url alt_label="Use the admin login" %}
{% endblock %}
```

## `templates/accounts/lockout.html`

- **Folder:** `templates/accounts/`
- **File:** `lockout.html`

```html
{% extends "base.html" %}
{% block title %}Account Locked · CU-VTS{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-12 col-sm-10 col-md-7 col-lg-5">
    <div class="card border-danger shadow-sm mt-4">
      <div class="card-body p-4 p-md-5 text-center">
        <div class="display-6 mb-2" aria-hidden="true">🔒</div>
        <h1 class="h4 text-danger">Too many attempts</h1>
        <p class="text-muted">
          This account has been temporarily locked after several failed sign-in
          attempts. Please wait a while before trying again, or contact your
          administrator if you believe this is a mistake.
        </p>
        <a href="{% url 'web:public_map' %}" class="btn btn-outline-secondary mt-2">Back to live map</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

## `templates/base.html`

- **Folder:** `templates/`
- **File:** `base.html`

```html
{% load static %}<!doctype html>
<html lang="en" data-bs-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="referrer" content="same-origin">
  <title>{% block title %}CU-VTS{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'vendor/bootstrap/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'vendor/leaflet/leaflet.css' %}">
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  {% block extra_head %}{% endblock %}
</head>
<body class="d-flex flex-column min-vh-100 bg-body-tertiary">
  <nav class="navbar navbar-expand-lg bg-primary" data-bs-theme="dark">
    <div class="container-fluid">
      <a class="navbar-brand fw-semibold" href="{% url 'web:public_map' %}">
        <span aria-hidden="true">🚌</span> CU-VTS
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
              data-bs-target="#mainNav" aria-controls="mainNav"
              aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="mainNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <a class="nav-link {% block nav_public %}{% endblock %}" href="{% url 'web:public_map' %}">Live Map</a>
          </li>
          {% if is_admin %}
            <li class="nav-item">
              <a class="nav-link {% block nav_dashboard %}{% endblock %}" href="{% url 'web:admin_dashboard' %}">Dashboard</a>
            </li>
            <li class="nav-item">
              <a class="nav-link {% block nav_trips %}{% endblock %}" href="{% url 'web:trip_history' %}">Trip History</a>
            </li>
          {% endif %}
          {% if is_driver %}
            <li class="nav-item">
              <a class="nav-link {% block nav_tracker %}{% endblock %}" href="{% url 'web:tracker' %}">My Tracker</a>
            </li>
          {% endif %}
        </ul>
        <ul class="navbar-nav mb-2 mb-lg-0">
          {% if user.is_authenticated %}
            <li class="nav-item d-flex align-items-center me-lg-2">
              <span class="navbar-text text-white-50 small">
                {{ user.get_full_name|default:user.get_username }}
              </span>
            </li>
            <li class="nav-item">
              <form method="post" action="{% url 'accounts:logout' %}" class="d-inline">
                {% csrf_token %}
                <button type="submit" class="btn btn-sm btn-outline-light">Log out</button>
              </form>
            </li>
          {% else %}
            <li class="nav-item">
              <a class="nav-link" href="{% url 'accounts:driver_login' %}">Driver Login</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="{% url 'accounts:admin_login' %}">Admin Login</a>
            </li>
          {% endif %}
        </ul>
      </div>
    </div>
  </nav>

  {% if messages %}
    <div class="container-fluid mt-3">
      {% for message in messages %}
        <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">
          {{ message }}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      {% endfor %}
    </div>
  {% endif %}

  <main class="flex-grow-1 d-flex flex-column {% block main_class %}container py-4{% endblock %}">
    {% block content %}{% endblock %}
  </main>

  <footer class="border-top py-3 mt-auto bg-body">
    <div class="container-fluid text-center text-muted small">
      CU Vehicle Tracking System &middot; <a href="{% url 'healthz' %}" class="link-secondary">status</a>
    </div>
  </footer>

  <script src="{% static 'vendor/bootstrap/bootstrap.bundle.min.js' %}"></script>
  {% block body_js %}{% endblock %}
</body>
</html>
```

## `templates/dashboard/admin_dashboard.html`

- **Folder:** `templates/dashboard/`
- **File:** `admin_dashboard.html`

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Dashboard · CU-VTS{% endblock %}
{% block nav_dashboard %}active{% endblock %}
{% block main_class %}d-flex flex-column p-0{% endblock %}

{% block content %}
<div class="vts-split">
  <div id="map" class="vts-map"
       data-endpoint="{% url 'api:vehicle-latest-locations' %}"
       data-poll="6000"
       data-center-lat="22.4716" data-center-lng="91.7876" data-zoom="14"></div>
  <aside class="vts-side">
    <div class="p-3 border-bottom">
      <div class="d-flex justify-content-between align-items-center">
        <h1 class="h6 mb-0">Fleet monitor</h1>
        <a href="{% url 'admin:index' %}" class="btn btn-sm btn-outline-secondary">Manage</a>
      </div>
      <div id="map-status" class="small text-muted mt-1">Loading…</div>
      <label for="focus-select" class="visually-hidden">Focus a vehicle</label>
      <select id="focus-select" class="form-select form-select-sm mt-2">
        <option value="">Focus a vehicle…</option>
      </select>
    </div>
    <div id="vehicle-list">
      <div class="p-4 text-center text-muted small">Loading…</div>
    </div>
    <div class="p-3 border-top small text-muted">
      Manage vehicles, drivers, and assignments from the
      <a href="{% url 'admin:index' %}">admin console</a>.
    </div>
  </aside>
</div>
{% endblock %}

{% block body_js %}
<script src="{% static 'vendor/leaflet/leaflet.js' %}"></script>
<script src="{% static 'js/vts-common.js' %}"></script>
<script src="{% static 'js/admin-map.js' %}"></script>
{% endblock %}
```

## `templates/public/vehicle_map.html`

- **Folder:** `templates/public/`
- **File:** `vehicle_map.html`

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Live Map · CU-VTS{% endblock %}
{% block nav_public %}active{% endblock %}
{% block main_class %}d-flex flex-column p-0{% endblock %}

{% block content %}
<div class="vts-split">
  <div id="map" class="vts-map"
       data-endpoint="{% url 'api:vehicle-latest-locations' %}"
       data-poll="8000"
       data-center-lat="22.4716" data-center-lng="91.7876" data-zoom="14"></div>
  <aside class="vts-side">
    <div class="p-3 border-bottom">
      <h1 class="h6 mb-1">Live vehicles</h1>
      <div id="map-status" class="small text-muted">Loading…</div>
    </div>
    <div id="vehicle-list">
      <div class="p-4 text-center text-muted small">Loading…</div>
    </div>
  </aside>
</div>
{% endblock %}

{% block body_js %}
<script src="{% static 'vendor/leaflet/leaflet.js' %}"></script>
<script src="{% static 'js/vts-common.js' %}"></script>
<script src="{% static 'js/public-map.js' %}"></script>
{% endblock %}
```

## `templates/tracker/tracker.html`

- **Folder:** `templates/tracker/`
- **File:** `tracker.html`

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Tracker · CU-VTS{% endblock %}
{% block nav_tracker %}active{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-12 col-md-8 col-lg-6">
    {% if assigned_vehicle %}
      <div id="tracker"
           data-endpoint="{% url 'api:location-create' %}"
           data-interval="5000">
        <div class="text-center mb-3">
          <h1 class="h4 mb-0">{{ assigned_vehicle.bus_number }}</h1>
          <div class="text-muted">{{ assigned_vehicle.route_label|default:"No route label" }}</div>
        </div>

        <div id="status-card" class="card shadow-sm mb-3">
          <div class="card-body text-center">
            <div class="text-uppercase small text-muted">Status</div>
            <div id="tracker-state" class="h5 mb-3">Not sharing</div>
            <button id="toggle-btn" type="button" class="btn btn-success tracker-power mx-auto d-block">
              Start sharing
            </button>
          </div>
        </div>

        <div id="tracker-error" class="alert alert-warning d-none" role="alert"></div>

        <div class="card shadow-sm">
          <div class="card-body">
            <div class="row text-center g-3">
              <div class="col-6">
                <div class="small text-muted">Coordinates</div>
                <div id="coords" class="tracker-metric">—</div>
              </div>
              <div class="col-6">
                <div class="small text-muted">Accuracy</div>
                <div id="accuracy" class="tracker-metric">—</div>
              </div>
              <div class="col-6">
                <div class="small text-muted">Speed</div>
                <div id="speed" class="tracker-metric">—</div>
              </div>
              <div class="col-6">
                <div class="small text-muted">Last sent</div>
                <div id="last-sent" class="tracker-metric">—</div>
              </div>
              <div class="col-12">
                <div class="small text-muted">Fixes sent this session</div>
                <div id="sent-count" class="tracker-metric">0</div>
              </div>
            </div>
          </div>
        </div>

        <p class="small text-muted mt-3 mb-0">
          Keep this page open while driving. Your location is only shared while
          sharing is on, and stops the moment you log out.
        </p>
      </div>
    {% else %}
      <div class="card border-warning shadow-sm mt-4">
        <div class="card-body text-center p-4">
          <div class="display-6 mb-2" aria-hidden="true">🚐</div>
          <h1 class="h4">No vehicle assigned</h1>
          <p class="text-muted mb-0">
            You are not currently assigned to a vehicle. Please contact your
            administrator to be assigned before you can share your location.
          </p>
        </div>
      </div>
    {% endif %}
  </div>
</div>
{% endblock %}

{% block body_js %}
<script src="{% static 'js/vts-common.js' %}"></script>
<script src="{% static 'js/tracker.js' %}"></script>
{% endblock %}
```

## `templates/trips/trip_history.html`

- **Folder:** `templates/trips/`
- **File:** `trip_history.html`

```html
{% extends "base.html" %}
{% load static %}
{% block title %}Trip History · CU-VTS{% endblock %}
{% block nav_trips %}active{% endblock %}
{% block main_class %}d-flex flex-column p-0{% endblock %}

{% block content %}
<div class="vts-split">
  <div id="history-map" class="vts-map"
       data-trips-url="{% url 'api:trip-list' %}"
       data-center-lat="22.4716" data-center-lng="91.7876" data-zoom="14"></div>
  <aside class="vts-side">
    <div class="p-3 border-bottom">
      <h1 class="h6 mb-2">Trip history</h1>
      <div class="mb-2">
        <label for="vehicle-select" class="form-label small mb-1">Vehicle</label>
        <select id="vehicle-select" class="form-select form-select-sm">
          <option value="">Choose a vehicle…</option>
          {% for vehicle in vehicles %}
            <option value="{{ vehicle.id }}">{{ vehicle.bus_number }}{% if vehicle.route_label %} · {{ vehicle.route_label }}{% endif %}</option>
          {% endfor %}
        </select>
      </div>
      <div class="mb-2">
        <label for="date-input" class="form-label small mb-1">Date</label>
        <input type="date" id="date-input" class="form-control form-control-sm" value="{% now 'Y-m-d' %}">
      </div>
      <div class="row g-2 mb-2">
        <div class="col-6">
          <label for="start-time" class="form-label small mb-1">From</label>
          <input type="time" id="start-time" class="form-control form-control-sm">
        </div>
        <div class="col-6">
          <label for="end-time" class="form-label small mb-1">To</label>
          <input type="time" id="end-time" class="form-control form-control-sm">
        </div>
      </div>
      <button id="load-trips" type="button" class="btn btn-primary btn-sm w-100">Load trips</button>
      <div id="history-error" class="alert alert-warning small mt-2 mb-0 d-none" role="alert"></div>
    </div>

    <div id="trip-list" class="flex-grow-1 overflow-auto">
      <div class="p-4 text-center text-muted small">Choose a vehicle and date, then load trips.</div>
    </div>

    <div class="p-3 border-top">
      <div class="d-flex align-items-center gap-2">
        <button id="play-btn" type="button" class="btn btn-outline-secondary btn-sm" disabled>▶ Play</button>
        <input type="range" id="playback-range" class="form-range flex-grow-1" min="0" max="0" value="0" disabled
               aria-label="Trip playback position">
      </div>
      <div id="play-info" class="small text-muted mt-1">Select a trip to replay its route.</div>
    </div>
  </aside>
</div>
{% endblock %}

{% block body_js %}
<script src="{% static 'vendor/leaflet/leaflet.js' %}"></script>
<script src="{% static 'js/vts-common.js' %}"></script>
<script src="{% static 'js/trip-history.js' %}"></script>
{% endblock %}
```

