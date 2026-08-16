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
