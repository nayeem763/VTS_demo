"""Frontend asset integrity, strict Bootstrap 5.2, CSP, and Liquid Glass architecture tests."""

from __future__ import annotations

import pathlib
import re
import xml.etree.ElementTree as ET

import pytest
from django.conf import settings

BASE_DIR = pathlib.Path(settings.BASE_DIR)

TEMPLATE_FILES = sorted(
    p.relative_to(BASE_DIR).as_posix() for p in (BASE_DIR / "templates").rglob("*.html")
)
CSS_FILES = sorted(
    p.relative_to(BASE_DIR).as_posix() for p in (BASE_DIR / "static" / "css").rglob("*.css")
)
JS_FILES = sorted(
    p.relative_to(BASE_DIR).as_posix() for p in (BASE_DIR / "static" / "js").rglob("*.js")
)
ALL_FRONTEND_FILES = TEMPLATE_FILES + CSS_FILES + JS_FILES

STATIC_REFS = sorted(
    {
        match.group(1)
        for rel in TEMPLATE_FILES
        for match in re.finditer(
            r"""\{%\s*static\s+['"]([^'"]+)['"]\s*%\}""",
            (BASE_DIR / rel).read_text(encoding="utf-8"),
        )
    }
)

BS53_FORBIDDEN = re.compile(r"data-bs-theme|\bbg-[a-z-]+-subtle\b|\btext-[a-z-]+-emphasis\b")
INLINE_EVENT_RE = re.compile(r"""\son[a-z]+\s*=""", flags=re.I)
EXTERNAL_CDN_RE = re.compile(r"""(?:src|href)\s*=\s*["']https?://""", flags=re.I)


# ---------------------------------------------------------------------------
# 1. Strict Bootstrap 5.2 Compliance across every template, CSS, JS (21 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rel_path", ALL_FRONTEND_FILES)
def test_frontend_strict_bootstrap_52_no_53_features(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    matches = BS53_FORBIDDEN.findall(content)
    assert not matches, f"Forbidden Bootstrap 5.3+ token(s) in {rel_path}: {matches}"


# ---------------------------------------------------------------------------
# 2. Strict CSP & Accessibility Compliance across every template (44 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rel_path", TEMPLATE_FILES)
def test_frontend_csp_no_inline_script_blocks(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    for m in re.finditer(r"<script\b([^>]*)>", content, flags=re.I):
        attrs = m.group(1)
        assert "src=" in attrs.lower(), f"Inline <script> forbidden by CSP in {rel_path}"


@pytest.mark.parametrize("rel_path", TEMPLATE_FILES)
def test_frontend_csp_no_inline_event_handlers(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    assert not INLINE_EVENT_RE.search(content), f"Inline event handler found in {rel_path}"


@pytest.mark.parametrize("rel_path", TEMPLATE_FILES)
def test_frontend_csp_no_external_cdn_links(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    assert not EXTERNAL_CDN_RE.search(content), f"External CDN reference found in {rel_path}"


@pytest.mark.parametrize("rel_path", TEMPLATE_FILES)
def test_frontend_inline_svgs_have_explicit_dimensions(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    for m in re.finditer(r"<svg\b([^>]*)>", content, flags=re.I):
        attrs = m.group(1).lower()
        assert "width=" in attrs and "height=" in attrs, (
            f"SVG missing explicit width/height in {rel_path}: {m.group(0)}"
        )


# ---------------------------------------------------------------------------
# 3. Every {% static '...' %} reference resolves to a real asset (15 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("asset_ref", STATIC_REFS)
def test_frontend_static_reference_exists_on_disk(asset_ref):
    target = BASE_DIR / "static" / asset_ref
    assert target.is_file(), f"Missing static asset: {asset_ref}"
    assert target.stat().st_size > 0


# ---------------------------------------------------------------------------
# 4. First-party JavaScript hygiene checks (8 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rel_path", JS_FILES)
def test_frontend_js_uses_strict_mode_and_valid_utf8(rel_path):
    content = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    assert '"use strict"' in content or "'use strict'" in content or rel_path.endswith("aurora-scroll.js")
    assert len(content.strip()) > 0


# ---------------------------------------------------------------------------
# 5. CSS, Aurora Scroll & Liquid Glass Architecture Invariants (10 tests)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rel_path", CSS_FILES)
def test_frontend_css_balanced_braces(rel_path):
    raw = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    stripped = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    assert stripped.count("{") == stripped.count("}")
    assert stripped.count("{") > 20


def test_frontend_liquid_aurora_css_zero_important():
    raw = (BASE_DIR / "static/css/liquid-aurora.css").read_text(encoding="utf-8")
    stripped = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    assert "!important" not in stripped.lower()


def test_frontend_aurora_scroll_fallback_under_20_lines():
    lines = (BASE_DIR / "static/js/aurora-scroll.js").read_text(encoding="utf-8").splitlines()
    assert 0 < len(lines) < 20


def test_frontend_aurora_scroll_uses_passive_raf():
    text = (BASE_DIR / "static/js/aurora-scroll.js").read_text(encoding="utf-8")
    assert "requestAnimationFrame" in text
    assert "passive" in text


def test_frontend_liquid_aurora_respects_reduced_motion():
    text = (BASE_DIR / "static/css/liquid-aurora.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in text


def test_frontend_liquid_aurora_uses_scroll_driven_animation_supports():
    text = (BASE_DIR / "static/css/liquid-aurora.css").read_text(encoding="utf-8")
    assert "@supports (animation-timeline: scroll())" in text


def test_frontend_base_html_includes_gmaps_svg_color_filters():
    text = (BASE_DIR / "templates/base.html").read_text(encoding="utf-8")
    assert 'id="gmaps-day-filter"' in text
    assert 'id="gmaps-dark-filter"' in text


def test_frontend_base_html_includes_aurora_ambient_layer():
    text = (BASE_DIR / "templates/base.html").read_text(encoding="utf-8")
    assert 'class="aurora-ambient"' in text
    assert "aurora-orb--1" in text
    assert "aurora-orb--2" in text
    assert "aurora-orb--3" in text


def test_frontend_cu_vts_logo_svg_is_valid_xml():
    svg_text = (BASE_DIR / "static/img/cu-vts-logo.svg").read_text(encoding="utf-8")
    root = ET.fromstring(svg_text)
    assert root.tag.endswith("svg")
