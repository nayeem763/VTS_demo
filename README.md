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
