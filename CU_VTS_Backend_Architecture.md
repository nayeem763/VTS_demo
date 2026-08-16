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
