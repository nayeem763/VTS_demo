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
