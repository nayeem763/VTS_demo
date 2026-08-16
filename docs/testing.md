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
