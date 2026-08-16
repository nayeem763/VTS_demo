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
