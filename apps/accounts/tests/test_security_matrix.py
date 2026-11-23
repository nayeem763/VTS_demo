"""Security, RBAC matrix, CSP headers, privacy, XSS/SQLi, and open-redirect tests."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.fleet.models import Vehicle
from apps.tracking.reports import ReportType, build_fleet_record_pdf

pytestmark = pytest.mark.django_db

# ---------------------------------------------------------------------------
# 1. Role x Endpoint Access Control Matrix (65 tests: 5 roles x 13 endpoints)
# ---------------------------------------------------------------------------
RBAC_MATRIX = [
    # (role, url_name, method, expected_status)
    # Public map
    ("anon", "web:public_map", "get", 200),
    ("driver", "web:public_map", "get", 200),
    ("inactive_driver", "web:public_map", "get", 200),
    ("admin", "web:public_map", "get", 200),
    ("superuser", "web:public_map", "get", 200),
    # Admin dashboard
    ("anon", "web:admin_dashboard", "get", 302),
    ("driver", "web:admin_dashboard", "get", 403),
    ("inactive_driver", "web:admin_dashboard", "get", 403),
    ("admin", "web:admin_dashboard", "get", 200),
    ("superuser", "web:admin_dashboard", "get", 200),
    # Fleet management workspace
    ("anon", "web:fleet_manage", "get", 302),
    ("driver", "web:fleet_manage", "get", 403),
    ("inactive_driver", "web:fleet_manage", "get", 403),
    ("admin", "web:fleet_manage", "get", 200),
    ("superuser", "web:fleet_manage", "get", 200),
    # Trip history page
    ("anon", "web:trip_history", "get", 302),
    ("driver", "web:trip_history", "get", 403),
    ("inactive_driver", "web:trip_history", "get", 403),
    ("admin", "web:trip_history", "get", 200),
    ("superuser", "web:trip_history", "get", 200),
    # Driver tracker page
    ("anon", "web:tracker", "get", 302),
    ("driver", "web:tracker", "get", 200),
    ("inactive_driver", "web:tracker", "get", 403),
    ("admin", "web:tracker", "get", 403),
    ("superuser", "web:tracker", "get", 403),
    # Fleet PDF download
    ("anon", "web:fleet_record_pdf", "get", 302),
    ("driver", "web:fleet_record_pdf", "get", 403),
    ("inactive_driver", "web:fleet_record_pdf", "get", 403),
    ("admin", "web:fleet_record_pdf", "get", 200),
    ("superuser", "web:fleet_record_pdf", "get", 200),
    # Trip History PDF download
    ("anon", "web:trip_history_pdf", "get", 302),
    ("driver", "web:trip_history_pdf", "get", 403),
    ("inactive_driver", "web:trip_history_pdf", "get", 403),
    ("admin", "web:trip_history_pdf", "get", 200),
    ("superuser", "web:trip_history_pdf", "get", 200),
    # Fleet vehicle create POST
    ("anon", "web:fleet_vehicle_create", "post", 302),
    ("driver", "web:fleet_vehicle_create", "post", 403),
    ("inactive_driver", "web:fleet_vehicle_create", "post", 403),
    ("admin", "web:fleet_vehicle_create", "post", 302),
    ("superuser", "web:fleet_vehicle_create", "post", 302),
    # Fleet driver assign POST
    ("anon", "web:fleet_assign", "post", 302),
    ("driver", "web:fleet_assign", "post", 403),
    ("inactive_driver", "web:fleet_assign", "post", 403),
    ("admin", "web:fleet_assign", "post", 302),
    ("superuser", "web:fleet_assign", "post", 302),
    # Fleet driver create POST
    ("anon", "web:fleet_driver_create", "post", 302),
    ("driver", "web:fleet_driver_create", "post", 403),
    ("inactive_driver", "web:fleet_driver_create", "post", 403),
    ("admin", "web:fleet_driver_create", "post", 302),
    ("superuser", "web:fleet_driver_create", "post", 302),
    # Public live API
    ("anon", "api:vehicle-latest-locations", "get", 200),
    ("driver", "api:vehicle-latest-locations", "get", 200),
    ("inactive_driver", "api:vehicle-latest-locations", "get", 200),
    ("admin", "api:vehicle-latest-locations", "get", 200),
    ("superuser", "api:vehicle-latest-locations", "get", 200),
    # Fixed routes API (admin only)
    ("anon", "api:bus-route-list", "get", 403),
    ("driver", "api:bus-route-list", "get", 403),
    ("inactive_driver", "api:bus-route-list", "get", 403),
    ("admin", "api:bus-route-list", "get", 200),
    ("superuser", "api:bus-route-list", "get", 200),
    # Trip list API (admin only; missing vehicle_id -> 400 for admins)
    ("anon", "api:trip-list", "get", 403),
    ("driver", "api:trip-list", "get", 403),
    ("inactive_driver", "api:trip-list", "get", 403),
    ("admin", "api:trip-list", "get", 400),
    ("superuser", "api:trip-list", "get", 400),
]


@pytest.mark.parametrize(("role", "url_name", "method", "expected"), RBAC_MATRIX)
def test_security_rbac_matrix(
    client,
    admin_user,
    superuser,
    driver_user,
    make_driver,
    role,
    url_name,
    method,
    expected,
):
    if role == "admin":
        client.force_login(admin_user)
    elif role == "superuser":
        client.force_login(superuser)
    elif role == "driver":
        client.force_login(driver_user)
    elif role == "inactive_driver":
        inact = make_driver(username="inact_rbac")
        inact.is_active = False
        inact.save(update_fields=["is_active"])
        client.force_login(inact.user)

    url = reverse(url_name)
    resp = getattr(client, method)(url)
    assert resp.status_code == expected


# ---------------------------------------------------------------------------
# 2. Security Headers & CSP Compliance (25 tests)
# ---------------------------------------------------------------------------
HEADER_PAGES = [
    ("anon", "web:public_map"),
    ("anon", "accounts:admin_login"),
    ("anon", "accounts:driver_login"),
    ("admin", "web:admin_dashboard"),
    ("admin", "web:fleet_manage"),
    ("admin", "web:trip_history"),
    ("driver", "web:tracker"),
    ("anon", "api:vehicle-latest-locations"),
]


@pytest.mark.parametrize(("role", "url_name"), HEADER_PAGES)
def test_security_csp_and_permissions_headers_present(client, admin_user, driver_user, role, url_name):
    if role == "admin":
        client.force_login(admin_user)
    elif role == "driver":
        client.force_login(driver_user)

    resp = client.get(reverse(url_name))
    assert resp.status_code == 200
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "unsafe-eval" not in csp
    assert "frame-ancestors 'none'" in csp
    assert "Permissions-Policy" in resp.headers
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"


@pytest.mark.parametrize("url_name", ["web:public_map", "web:admin_dashboard", "web:fleet_manage", "web:trip_history"])
def test_security_csp_allows_osrm_connect_src_and_osm_tiles(client, admin_user, url_name):
    client.force_login(admin_user)
    resp = client.get(reverse(url_name))
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "connect-src 'self' https://" in csp
    assert "openstreetmap.org" in csp


@pytest.mark.parametrize("url_name", ["web:fleet_record_pdf", "web:trip_history_pdf"])
def test_security_pdf_exports_enforce_no_store_and_nosniff(client, admin_user, url_name):
    client.force_login(admin_user)
    resp = client.get(reverse(url_name))
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "private, no-store"
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("Content-Disposition", "").startswith("attachment; filename=")


@pytest.mark.parametrize("rtype", ReportType.ALL)
def test_security_pdf_exports_content_disposition_is_ascii(client, admin_user, rtype):
    client.force_login(admin_user)
    resp = client.get(reverse("web:fleet_record_pdf"), {"report_type": rtype})
    assert resp.status_code == 200
    cd = resp.headers["Content-Disposition"]
    assert cd.isascii()
    assert "\r" not in cd and "\n" not in cd


@pytest.mark.parametrize("url_name", ["web:public_map", "accounts:admin_login", "accounts:driver_login", "web:admin_dashboard", "web:fleet_manage", "web:trip_history", "web:tracker"])
def test_security_clickjacking_x_frame_options_deny(client, admin_user, driver_user, url_name):
    if url_name in ("web:admin_dashboard", "web:fleet_manage", "web:trip_history"):
        client.force_login(admin_user)
    elif url_name == "web:tracker":
        client.force_login(driver_user)
    resp = client.get(reverse(url_name))
    assert resp.headers.get("X-Frame-Options") == "DENY"


# ---------------------------------------------------------------------------
# 3. XSS Escaping, SQLi Safety & Privacy Isolation (30 tests)
# ---------------------------------------------------------------------------
HOSTILE_STRINGS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    '"><svg onload=alert(1)>',
    "' OR '1'='1",
    "'; DROP TABLE fleet_vehicle; --",
    "<b onclick=x>Bus & Co</b>",
    "{{ 7*7 }}",
    "${7*7}",
    "CU-X\r\nInjected: yes",
    "<!-- comment -->",
]


@pytest.mark.parametrize("payload", HOSTILE_STRINGS)
def test_security_xss_and_sqli_escaped_in_fleet_ui(client, admin_user, payload):
    client.force_login(admin_user)
    v = Vehicle.objects.create(
        bus_number=f"SEC-{abs(hash(payload)) % 99999}",
        route_label=payload[:120],
        admin_description=payload[:280],
    )
    resp = client.get(reverse("web:fleet_manage"))
    assert resp.status_code == 200
    body = resp.content.decode("utf-8")
    assert "<script>alert(1)</script>" not in body
    assert "<img src=x onerror=alert(1)>" not in body
    assert "<svg onload=alert(1)>" not in body
    assert Vehicle.objects.filter(pk=v.pk).exists()


@pytest.mark.parametrize("payload", HOSTILE_STRINGS)
def test_security_hostile_strings_safe_in_reportlab_pdf(payload):
    v = Vehicle.objects.create(
        bus_number=f"PDF-{abs(hash(payload)) % 99999}",
        route_label=payload[:120],
        admin_description=payload[:280],
    )
    pdf = build_fleet_record_pdf(vehicles=[v], generated_by=payload[:40])
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 3_000


@pytest.mark.parametrize("payload", HOSTILE_STRINGS)
def test_security_admin_note_never_leaks_to_public_api_or_driver(
    client, assigned_driver, vehicle, payload
):
    marker = f"ADMIN-SECRET-{abs(hash(payload)) % 99999}-{payload[:20]}"
    vehicle.admin_description = marker
    vehicle.save(update_fields=["admin_description"])

    pub_api = client.get(reverse("api:vehicle-latest-locations"))
    assert marker.encode() not in pub_api.content
    assert b"admin_description" not in pub_api.content
    assert b"driver_name" not in pub_api.content

    client.force_login(assigned_driver)
    tracker = client.get(reverse("web:tracker"))
    assert marker.encode() not in tracker.content


# ---------------------------------------------------------------------------
# 4. Open-Redirect & HTTP Method-Safety Tests (20 tests)
# ---------------------------------------------------------------------------
MALICIOUS_NEXT_URLS = [
    "//evil.example.com/phish",
    "https://evil.example.com/login",
    "http://evil.example.com/",
    "///evil.example.com",
    "javascript:alert(1)",
    "data:text/html,<h1>hi</h1>",
    "https://github.com/evil",
    "//127.0.0.1.evil.com/dashboard",
    "\\\\evil.example.com",
    "ftp://evil.example.com/file",
]


@pytest.mark.parametrize("bad_next", MALICIOUS_NEXT_URLS)
def test_security_login_blocks_open_redirect(client, admin_user, password, bad_next):
    resp = client.post(
        reverse("accounts:admin_login") + f"?next={bad_next}",
        {"username": admin_user.username, "password": password},
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("web:admin_dashboard")


STATE_CHANGING_POST_ONLY = [
    ("accounts:logout", []),
    ("web:fleet_vehicle_create", []),
    ("web:fleet_assign", []),
    ("web:fleet_driver_create", []),
]


@pytest.mark.parametrize(("url_name", "args"), STATE_CHANGING_POST_ONLY)
def test_security_mutation_endpoints_reject_get(client, admin_user, url_name, args):
    client.force_login(admin_user)
    resp = client.get(reverse(url_name, args=args))
    assert resp.status_code == 405


@pytest.mark.parametrize("method", ["put", "patch", "delete", "head", "options", "trace"])
def test_security_logout_only_allows_post(client, admin_user, method):
    client.force_login(admin_user)
    resp = getattr(client, method)(reverse("accounts:logout"))
    assert resp.status_code in (405, 200)
    # Verify session was NOT logged out by non-POST request
    assert client.get(reverse("web:admin_dashboard")).status_code == 200
