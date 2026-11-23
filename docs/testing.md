# Testing

The suite is **1,250 automated tests** across **25 test modules** on `pytest` +
`pytest-django`, run against an in-memory SQLite database with fast hashing and
lockout/throttling disabled for determinism (`config/settings/test.py`). Total
statement + branch coverage across `apps/` is **95%** (`2,307` statements,
`514` branches), with every domain layer sitting at **91–100%**.

- [Running the tests](#running-the-tests)
- [Breakdown by test type](#breakdown-by-test-type)
- [How the suite is organized](#how-the-suite-is-organized)
- [Fixtures](#fixtures)
- [Coverage](#coverage)
- [Testing philosophy](#testing-philosophy)

---

## Running the tests

```bash
pytest                                          # whole suite (1,250 tests), quiet
pytest --cov=apps --cov-report=term-missing     # with statement + branch coverage
pytest apps/tracking/tests/test_api_contracts.py  # one module
pytest -k "idempotent"                          # filter by test name
pytest -x -vv                                   # stop on first failure, verbose
```

`DJANGO_SETTINGS_MODULE` is pinned to `config.settings.test` in
`pyproject.toml`, so no environment setup is needed. The test settings **force
SQLite** even if a `DATABASE_URL` is present in your shell, so a local `.env`
pointing at Supabase can never be touched by a test run.

---

## Breakdown by test type

| Test Type | Count | Share | What Is Verified |
|---|---:|---:|---|
| **Unit & Boundary-Value Analysis (BVA)** | **386** | 30.9% | Coordinate/speed/accuracy/timestamp boundaries, form validation (`VehicleForm`, `AssignDriverForm`, `DriverCreateForm`/`EditForm`), role predicates, Haversine & PDF formatters |
| **API Contract & Integration** | **160** | 12.8% | DRF JSON schemas, public vs. admin payload separation, stale boundaries, idempotent GPS replays, anti-spoofing, fixed bus route CRUD, trip & points playback |
| **Database, Service & Selector Integration** | **146** | 11.7% | DB `CheckConstraint` & partial `UniqueConstraint` invariants, chained reassignments, activate/deactivate cycles, stale-trip closing, management commands, ReportLab PDF generation |
| **Property-Based & Fuzz Testing** | **140** | 11.2% | Haversine metric-space axioms (identity, symmetry, triangle inequality), smart checkpoint sampler invariants, DRF serializer fuzzing |
| **Security, RBAC, Privacy & Injection Resistance** | **140** | 11.2% | 5-role × 13-endpoint access matrix, CSP/`X-Frame-Options`/`nosniff`/`no-store` headers, XSS & SQLi escaping in HTML & PDF, zero leakage of `admin_description`/PII, open-redirect & HTTP method guards |
| **Functional & End-to-End Web Workflows** | **130** | 10.4% | Multi-actor Driver → Public Map → Admin → Logout journeys, `/fleet/` CRUD/rename/assign/deassign workflows, PDF report builder parameter matrix & 400 error handling, Django Admin exports |
| **Frontend Integrity, Bootstrap 5.2 & CSP Static** | **98** | 7.8% | Strict Bootstrap 5.2 audit, zero inline `<script>`/`on*=`/external CDNs, SVG dimensions, `{% static %}` disk resolution, balanced CSS braces, zero `!important` in `liquid-aurora.css`, `aurora-scroll.js < 20` lines |
| **Performance, Anti-N+1 Query Budget & Scalability** | **50** | 4.0% | Constant `O(1)` SQL query budgets across scaling fleets, smart checkpoint compression & latency up to 1,200 fixes, Haversine throughput, PDF speed & compactness |
| **Total** | **1,250** | **100%** | **1,250 passed · 0 failed · 0 skipped · 95% coverage** |

---

## How the suite is organized

Tests live beside the app they exercise, organized by concern and test level:

```text
apps/accounts/tests/
  test_authentication.py               role-aware login, logout-closes-trip, safe next URLs (8)
  test_permissions.py                  is_admin / is_driver predicates & group checks (7)
  test_security_matrix.py              5-role RBAC matrix, CSP/headers, XSS/SQLi, privacy, open redirects (140)
  test_services.py                     create_driver and soft-deactivation (4)
apps/fleet/tests/
  test_db_and_services_integration.py  DB constraints, reassignment chains, commands, selectors (100)
  test_fleet_management.py             /fleet/ RBAC, CRUD, rename, open-trip closure, admin-note privacy (6)
  test_forms_unit.py                   VehicleForm, DriverCreate/EditForm, AssignDriverForm BVA (120)
  test_models.py                       Vehicle / DriverAssignment constraints & __str__ (6)
  test_selectors.py                    active-vehicle and active-assignment resolution (5)
  test_services.py                     assign / reassign / deactivate (unique-active rules) (7)
apps/tracking/tests/
  test_api_contracts.py                live feed schemas, anti-spoofing, routes CRUD, trips API (130)
  test_location_api.py                 POST /locations/ — auth, 201/200, 403/409/400 (9)
  test_performance_budgets.py          O(1) SQL query budgets, sampler compression, PDF latency (50)
  test_property_fuzz.py                Haversine metric axioms, sampler invariants, serializer fuzzing (140)
  test_public_api.py                   latest-locations — privacy boundary by role (10)
  test_reports.py                      4 PDF profiles, 5-part spec headings, smart sampling, exports (17)
  test_routes_api.py                   fixed BusRoute CRUD & waypoint validation (4)
  test_selectors.py                    latest-location and trip-points queries (7)
  test_services.py                     ingestion, trip open/close, staleness, idempotency (12)
  test_trip_api.py                     /trips/ and /trips/{id}/points/ — admin-only, params (9)
  test_unit_boundaries.py              coordinate/speed/accuracy/timestamp BVA & report formatters (240)
  test_validators.py                   coordinate, speed, accuracy, clock-skew rules (12)
apps/web/tests/
  test_frontend_integrity.py           Bootstrap 5.2, CSP, static refs, CSS/JS/SVG integrity (98)
  test_functional_workflows.py         end-to-end journeys, PDF builder matrix, admin exports (100)
  test_views.py                        page access control, CSRF cookie, rendered context (9)
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

## Coverage

Current `pytest --cov=apps --cov-report=term` snapshot (`branch = true`):

| Area                                                         | Coverage |
|--------------------------------------------------------------|:--------:|
| `accounts/permissions.py`, `services.py`, `models.py`, `signals.py`, `forms.py`, `context_processors.py`, `seed_roles.py` | 100% |
| `accounts/views.py`                                          | 97%      |
| `fleet/selectors.py`                                         | 100%     |
| `fleet/services.py`                                          | 98%      |
| `fleet/models.py`                                            | 96%      |
| `fleet/forms.py`                                             | 94%      |
| `tracking/validators.py`, `api/permissions.py`, `close_stale_trips.py` | 100% |
| `tracking/api/serializers.py`, `api/views.py`, `create_demo_data.py` | 98% |
| `tracking/reports.py`                                        | 97%      |
| `tracking/selectors.py`                                      | 96%      |
| `tracking/models.py`                                         | 93%      |
| `tracking/services.py`                                       | 91%      |
| `web/views.py`                                               | 97%      |
| `web/fleet_views.py`                                         | 94%      |
| `fleet/admin.py`, `tracking/admin.py`                        | 65–66%   |
| **TOTAL (`apps/`, 2,307 statements, 514 branches)**          | **95%**  |

The remaining ~5% consists almost entirely of Django Admin declarative list helpers
and rare concurrent-`IntegrityError` defensive fallbacks.

---

## Testing philosophy

- **Test the domain, not the framework.** Services, selectors, validators, forms,
  and permissions carry the logic and carry the coverage.
- **Fixtures use the real code paths.** Building test data through the service
  layer keeps test setup aligned with production behavior.
- **Assert the boundaries.** Privacy (public vs. admin fields and `admin_description`),
  authorization (`403` vs. `302`), idempotency, SQL query scaling, and constraint
  violations are tested exhaustively at their edges.
- **Deterministic by construction.** In-memory SQLite, MD5 hashing, axes and
  throttles off, cache cleared per test, logging silenced — the suite gives the
  same result on every machine and in CI ([`.github/workflows/tests.yml`](../.github/workflows/tests.yml)).
