"""Executive and operational PDF reporting for CU Vehicle Tracking System.

Reports are built directly from Django's authoritative fleet and immutable
tracking models (``Vehicle``, ``DriverAssignment``, ``BusRoute``, ``Trip``,
``Location``) using ReportLab vector primitives so every export is deterministic,
print-ready, and self-contained without browser or native chart binaries.

Every report begins with an explicit five-part **Report Specification & System
Context** block addressing:
  i)   Purpose
  ii)  Intended Audience
  iii) Inputs & Data Scope
  iv)  Outputs & Deliverables
  v)   Platform & Environment

Instead of dumping noisy 5-second raw latitude/longitude updates by default,
analytics are computed across 100% of the recorded fixes while presenting
actionable fleet summaries, per-trip ledgers, safety scorecards, or
intelligently sampled route checkpoints depending on the selected report type.
"""

from __future__ import annotations

import platform
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from html import escape
from io import BytesIO
from math import asin, ceil, cos, radians, sin, sqrt

import django
import reportlab
from django.conf import settings
from django.db import connection
from django.db.models import QuerySet
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from apps.fleet.models import BusRoute, DriverAssignment, Vehicle

from .models import Location, Trip

# Institutional CU-VTS print palette (high contrast in both colour and greyscale).
NAVY = colors.HexColor("#0F2744")
COBALT = colors.HexColor("#1A73E8")
EMERALD = colors.HexColor("#1E8E3E")
AMBER = colors.HexColor("#D97706")
CRIMSON = colors.HexColor("#DC2626")
INK = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#64748B")
LINE = colors.HexColor("#CBD5E1")
SURFACE = colors.HexColor("#F8FAFC")
SPEC_BG = colors.HexColor("#F1F6FC")
INSIGHT_BG = colors.HexColor("#F2FBF5")
INSIGHT_BORDER = colors.HexColor("#BBF7D0")
WARN_BG = colors.HexColor("#FEF2F2")

PAGE_MARGIN = 15 * mm
FRAME_WIDTH = A4[0] - 2 * PAGE_MARGIN  # 180 mm
OVERSPEED_THRESHOLD_KMH = 45.0
DEFAULT_SAMPLE_INTERVAL_SECONDS = 120
DEFAULT_SAMPLE_DISTANCE_KM = 0.25


class ReportType:
    """Supported PDF report profiles selectable by CU Transport administrators."""

    EXECUTIVE_SUMMARY = "executive_summary"
    TRIP_SUMMARY = "trip_summary"
    SAFETY_AUDIT = "safety_audit"
    TELEMETRY_AUDIT = "telemetry_audit"

    ALL = (
        EXECUTIVE_SUMMARY,
        TRIP_SUMMARY,
        SAFETY_AUDIT,
        TELEMETRY_AUDIT,
    )


@dataclass(frozen=True)
class ReportSpec:
    """Metadata describing a report profile for UI selectors and PDF headers."""

    key: str
    title: str
    short_label: str
    header_tag: str
    kicker: str
    summary: str
    purpose: str
    audience: str
    outputs: str
    filename_slug: str


REPORT_CATALOG: dict[str, ReportSpec] = {
    ReportType.EXECUTIVE_SUMMARY: ReportSpec(
        key=ReportType.EXECUTIVE_SUMMARY,
        title="Executive Fleet Operations Overview",
        short_label="Executive Fleet Overview",
        header_tag="EXECUTIVE FLEET OVERVIEW",
        kicker="CU TRANSPORT AUTHORITY  ·  EXECUTIVE MANAGEMENT REPORT",
        summary=(
            "Compact leadership summary with fleet KPIs, per-vehicle performance, "
            "route network coverage, and visual analytics (no raw 5-second coordinate spam)."
        ),
        purpose=(
            "Provide the University of Chittagong Transport Authority with a concise, "
            "decision-ready view of campus bus utilization, trip coverage, operating "
            "speeds, GPS signal health, and active route deployment."
        ),
        audience=(
            "Director of Transport (CU Transport Authority), Assistant Registrars "
            "(Transport), Fleet Operations Supervisors, and Administrative Auditors."
        ),
        outputs=(
            "Executive KPI strip, automated operational takeaways, per-vehicle fleet "
            "performance ledger (one row per bus), fixed campus route directory, and a "
            "dedicated visual analytics page (daily volume, distance by bus, speed profile)."
        ),
        filename_slug="overview",
    ),
    ReportType.TRIP_SUMMARY: ReportSpec(
        key=ReportType.TRIP_SUMMARY,
        title="Trip Operations & Journey Ledger",
        short_label="Trip Operations Ledger",
        header_tag="TRIP OPERATIONS LEDGER",
        kicker="CU TRANSPORT AUTHORITY  ·  DISPATCH & JOURNEY LEDGER",
        summary=(
            "Actionable trip-by-trip schedule showing departures, arrivals, duration, "
            "driver, distance, speeds, and start/end coordinates."
        ),
        purpose=(
            "Document completed and ongoing campus shuttle journeys by vehicle and in "
            "combined chronological dispatch order to verify schedule adherence, driver "
            "duty logs, and route distance without bloating pages with 5-second GPS pings."
        ),
        audience=(
            "Transport Dispatch Officers, Route Supervisors, Duty Roster Coordinators, "
            "and Campus Transport Auditors."
        ),
        outputs=(
            "Trip window KPIs, per-vehicle journey summary ledgers (departure/arrival, "
            "duration, distance, average/peak speed, origin/destination coordinates), "
            "and a separate combined chronological dispatch timeline."
        ),
        filename_slug="trips",
    ),
    ReportType.SAFETY_AUDIT: ReportSpec(
        key=ReportType.SAFETY_AUDIT,
        title="Vehicle Speed Compliance & Safety Audit",
        short_label="Speed & Safety Audit",
        header_tag="SPEED & SAFETY AUDIT",
        kicker="CU TRANSPORT AUTHORITY  ·  SAFETY & COMPLIANCE AUDIT",
        summary=(
            "Per-vehicle safety scorecards, overspeed event review (>=45 km/h), "
            "GPS signal accuracy assessment, and speed-band visual breakdown."
        ),
        purpose=(
            "Evaluate campus bus speed discipline, identify recurring high-speed "
            "incidents (>=45 km/h), and assess GPS telemetry reliability so safety "
            "officers can take targeted corrective action."
        ),
        audience=(
            "CU Transport Safety Committee, Chief Transport Officer, Fleet Maintenance "
            "& Compliance Supervisors."
        ),
        outputs=(
            "Fleet safety KPIs, per-vehicle compliance scorecard with risk rating "
            "(Compliant / Review / Alert), deduplicated high-speed incident log, "
            "and dedicated speed-distribution & telemetry analytics charts."
        ),
        filename_slug="safety-audit",
    ),
    ReportType.TELEMETRY_AUDIT: ReportSpec(
        key=ReportType.TELEMETRY_AUDIT,
        title="Route Checkpoint & Telemetry Audit",
        short_label="Route Telemetry Trace",
        header_tag="ROUTE TELEMETRY TRACE",
        kicker="CU TRANSPORT AUTHORITY  ·  AUDITABLE CHECKPOINT LOG",
        summary=(
            "Chronological coordinate audit condensed via smart checkpoint sampling "
            "(trip start/end, speed peaks, and timed/distance checkpoints) plus analytics."
        ),
        purpose=(
            "Provide an auditable, compact coordinate trail for route verification, "
            "incident investigation, or technical review—preserving trip endpoints, "
            "speed peaks, and key waypoints without printing redundant 5-second rows."
        ),
        audience=(
            "Transport Compliance Investigators, Route Auditors, and CU-VTS Technical "
            "Administrators."
        ),
        outputs=(
            "Sampling compression summary, tagged chronological checkpoint log "
            "(Start, Checkpoint, Peak/Overspeed, End) with speed and GPS accuracy, "
            "and a dedicated visual analytics page."
        ),
        filename_slug="telemetry-trace",
    ),
}

REPORT_CHOICES: tuple[ReportSpec, ...] = tuple(REPORT_CATALOG[key] for key in ReportType.ALL)

TRIP_REPORT_CHOICES: tuple[ReportSpec, ...] = (
    REPORT_CATALOG[ReportType.TRIP_SUMMARY],
    REPORT_CATALOG[ReportType.TELEMETRY_AUDIT],
    REPORT_CATALOG[ReportType.SAFETY_AUDIT],
)

SAMPLING_INTERVAL_CHOICES: tuple[tuple[int, str], ...] = (
    (120, "Smart checkpoints · every 2 min or 250 m (Recommended)"),
    (60, "Detailed checkpoints · every 1 min or 250 m"),
    (300, "Compact checkpoints · every 5 min or 250 m"),
    (0, "Raw forensic log · every recorded GPS fix (large)"),
)

VALID_SAMPLE_INTERVALS: frozenset[int] = frozenset(val for val, _ in SAMPLING_INTERVAL_CHOICES)


@dataclass(frozen=True)
class _ReportMetrics:
    """Precomputed metrics shared across summary cards and visual analytics."""

    record_count: int
    vehicle_count: int
    active_vehicle_count: int
    trip_count: int
    average_speed_kmh: float | None
    peak_speed_kmh: float | None
    average_accuracy_m: float | None
    estimated_distance_km: float
    overspeed_count: int
    speed_sample_count: int
    first_captured_at: datetime | None
    last_captured_at: datetime | None
    vehicle_records: list[tuple[str, int]]
    vehicle_distances: list[tuple[str, float]]
    daily_records: list[tuple[str, int]]
    speed_buckets: list[tuple[str, int]]


@dataclass(frozen=True)
class _TripSummary:
    """Aggregated operational summary for a single bus journey."""

    trip_id: int
    vehicle_id: int
    bus_number: str
    route_label: str
    driver_name: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: float | None
    distance_km: float
    avg_speed_kmh: float | None
    peak_speed_kmh: float | None
    overspeed_count: int
    avg_accuracy_m: float | None
    fix_count: int
    start_coords: tuple[float, float] | None
    end_coords: tuple[float, float] | None


@dataclass(frozen=True)
class _VehicleSummary:
    """Aggregated operational and safety summary for a single vehicle."""

    vehicle: Vehicle
    assigned_driver: str
    trip_count: int
    fix_count: int
    distance_km: float
    operating_minutes: float
    avg_speed_kmh: float | None
    peak_speed_kmh: float | None
    avg_accuracy_m: float | None
    overspeed_count: int
    speed_sample_count: int
    last_captured_at: datetime | None

    @property
    def compliance_pct(self) -> float | None:
        if not self.speed_sample_count:
            return None
        return max(0.0, 100.0 * (1.0 - self.overspeed_count / self.speed_sample_count))

    @property
    def safety_rating(self) -> str:
        if not self.fix_count:
            return "No Data"
        if self.peak_speed_kmh is not None and self.peak_speed_kmh >= 60.0:
            return "Alert"
        if self.overspeed_count >= 5 or (
            self.compliance_pct is not None and self.compliance_pct < 90.0
        ):
            return "Alert"
        if self.overspeed_count > 0:
            return "Review"
        return "Compliant"


@dataclass(frozen=True)
class _SampledCheckpoint:
    """A retained GPS coordinate fix annotated with its checkpoint role."""

    location: Location
    tag: str


class _NumberedCanvas(pdfcanvas.Canvas):
    """Canvas emitting a consistent executive header and 'Page X of Y' footer."""

    def __init__(
        self,
        *args,
        header_tag: str = "FLEET OPERATIONS REPORT",
        document_ref: str = "",
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._header_tag = header_tag
        self._document_ref = document_ref
        self._saved_page_states: list[dict] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_chrome(total_pages)
            super().showPage()
        super().save()

    def _draw_chrome(self, total_pages: int) -> None:
        page_width, page_height = A4
        self.saveState()

        # Executive institutional top banner + subtle cobalt accent line.
        self.setFillColor(NAVY)
        self.rect(0, page_height - 14.5 * mm, page_width, 14.5 * mm, fill=1, stroke=0)
        self.setFillColor(COBALT)
        self.rect(0, page_height - 15.4 * mm, page_width, 0.9 * mm, fill=1, stroke=0)

        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 8.8)
        self.drawString(
            PAGE_MARGIN,
            page_height - 9.0 * mm,
            "CU-VTS  ·  UNIVERSITY OF CHITTAGONG TRANSPORT AUTHORITY",
        )
        self.setFont("Helvetica", 7.0)
        self.drawRightString(
            page_width - PAGE_MARGIN,
            page_height - 8.9 * mm,
            self._header_tag,
        )

        # Crisp footer with provenance and Page X of Y numbering.
        self.setStrokeColor(LINE)
        self.setLineWidth(0.5)
        self.line(PAGE_MARGIN, 12 * mm, page_width - PAGE_MARGIN, 12 * mm)
        self.setFillColor(MUTED)
        self.setFont("Helvetica", 6.8)
        footer_left = "University of Chittagong · Vehicle Tracking System (CU-VTS) · Confidential"
        if self._document_ref:
            footer_left = f"{footer_left}  ·  Ref {self._document_ref}"
        self.drawString(PAGE_MARGIN, 7.6 * mm, footer_left)
        self.drawRightString(
            page_width - PAGE_MARGIN,
            7.6 * mm,
            f"Page {self._pageNumber} of {total_pages}",
        )
        self.restoreState()


class _BarChart(Flowable):
    """Compact vector bar chart with clean reference lines and semantic colours."""

    def __init__(
        self,
        *,
        title: str,
        subtitle: str,
        data: list[tuple[str, float]],
        colour,
        bar_colours: list | None = None,
        value_suffix: str = "",
        decimals: int = 0,
    ) -> None:
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.data = data
        self.colour = colour
        self.bar_colours = bar_colours
        self.value_suffix = value_suffix
        self.decimals = decimals
        self.width = FRAME_WIDTH
        self.height = 51 * mm

    def wrap(self, available_width: float, _available_height: float) -> tuple[float, float]:
        self.width = min(self.width, available_width)
        return self.width, self.height

    def draw(self) -> None:
        canvas = self.canv
        width, height = self.width, self.height

        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.roundRect(0, 0, width, height, 2.5 * mm, fill=1, stroke=1)

        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 8.8)
        canvas.drawString(5 * mm, height - 6.8 * mm, self.title)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 6.8)
        canvas.drawString(5 * mm, height - 11.2 * mm, self.subtitle)

        if not self.data or not any(value > 0 for _, value in self.data):
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(width / 2, height / 2 - 2 * mm, "No recorded data in scope.")
            canvas.restoreState()
            return

        chart_left = 15 * mm
        chart_bottom = 13.5 * mm
        chart_width = width - chart_left - 7 * mm
        chart_height = height - chart_bottom - 18.5 * mm
        max_value = max(value for _, value in self.data)
        rounded_max = _nice_maximum_float(max_value)

        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.35)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 6)
        for tick in range(4):
            tick_value = rounded_max * tick / 3
            y = chart_bottom + chart_height * tick / 3
            canvas.line(chart_left, y, chart_left + chart_width, y)
            canvas.drawRightString(
                chart_left - 2 * mm,
                y - 2,
                _format_chart_value(tick_value, decimals=self.decimals),
            )

        count = len(self.data)
        slot_width = chart_width / count
        bar_width = min(14 * mm, max(3.5 * mm, slot_width * 0.54))
        for index, (label, value) in enumerate(self.data):
            bar_height = chart_height * (value / rounded_max) if rounded_max else 0
            x = chart_left + index * slot_width + (slot_width - bar_width) / 2
            fill = (
                self.bar_colours[index]
                if self.bar_colours and index < len(self.bar_colours)
                else self.colour
            )
            canvas.setFillColor(fill)
            if bar_height > 0:
                canvas.roundRect(x, chart_bottom, bar_width, bar_height, 1.0 * mm, fill=1, stroke=0)

            label_text = (
                f"{value:.{self.decimals}f}{self.value_suffix}"
                if self.decimals
                else f"{int(round(value)):,}{self.value_suffix}"
            )
            canvas.setFillColor(INK)
            canvas.setFont("Helvetica-Bold", 6)
            canvas.drawCentredString(
                x + bar_width / 2,
                chart_bottom + bar_height + 2.2 * mm,
                label_text,
            )

            canvas.saveState()
            canvas.translate(x + bar_width / 2, chart_bottom - 2.3 * mm)
            if count > 6:
                canvas.rotate(24)
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 6.0)
            canvas.drawCentredString(0, 0, _truncate(label, 14))
            canvas.restoreState()

        canvas.restoreState()


def build_fleet_record_pdf(
    *,
    vehicles: Iterable[Vehicle] | QuerySet[Vehicle],
    generated_by: str = "",
    report_type: str = ReportType.EXECUTIVE_SUMMARY,
    date_from: date | None = None,
    date_to: date | None = None,
    sample_interval_seconds: int = DEFAULT_SAMPLE_INTERVAL_SECONDS,
    vehicle_scope_label: str = "",
) -> bytes:
    """Return a publication-grade PDF report for the selected CU fleet scope.

    Parameters
    ----------
    vehicles:
        Vehicles included in the report.
    generated_by:
        Authenticated administrator username printed in document provenance.
    report_type:
        One of :class:`ReportType` (defaults to ``executive_summary`` so admins
        get a clean executive overview instead of 5-second coordinate spam).
    date_from / date_to:
        Optional inclusive local-date window applied to telemetry and trips.
    sample_interval_seconds:
        Minimum checkpoint spacing for ``telemetry_audit`` (``0`` = raw fixes).
    """
    spec = REPORT_CATALOG.get(report_type, REPORT_CATALOG[ReportType.EXECUTIVE_SUMMARY])
    selected_vehicles = list(vehicles)
    vehicle_ids = [vehicle.pk for vehicle in selected_vehicles if vehicle.pk is not None]

    locations_qs = Location.objects.filter(vehicle_id__in=vehicle_ids)
    trips_qs = Trip.objects.filter(vehicle_id__in=vehicle_ids)

    window_start = _start_of_local_day(date_from) if date_from is not None else None
    window_end = _end_of_local_day(date_to) if date_to is not None else None
    if window_start is not None:
        locations_qs = locations_qs.filter(captured_at__gte=window_start)
        trips_qs = trips_qs.filter(started_at__gte=window_start)
    if window_end is not None:
        locations_qs = locations_qs.filter(captured_at__lte=window_end)
        trips_qs = trips_qs.filter(started_at__lte=window_end)

    locations = list(
        locations_qs.select_related("vehicle", "driver__user", "trip").order_by("captured_at", "pk")
    )
    trips = list(trips_qs.select_related("vehicle", "driver__user").order_by("started_at", "pk"))
    active_assignments = {
        assignment.vehicle_id: assignment.driver.display_name
        for assignment in DriverAssignment.objects.filter(
            vehicle_id__in=vehicle_ids, is_active=True
        ).select_related("driver__user")
    }

    trip_summaries = _summarise_trips(trips=trips, locations=locations)
    vehicle_summaries = _summarise_vehicles(
        vehicles=selected_vehicles,
        locations=locations,
        trip_summaries=trip_summaries,
        active_assignments=active_assignments,
    )
    metrics = _summarise_locations(
        locations=locations,
        vehicle_count=len(selected_vehicles),
        trip_count=len(trip_summaries),
        active_vehicle_count=sum(1 for v in selected_vehicles if v.is_active),
    )

    date_scope_text = _format_date_window(date_from=date_from, date_to=date_to)
    scope_desc = vehicle_scope_label or _default_vehicle_scope_label(selected_vehicles)

    generated_at = timezone.now()
    document_ref = f"CU-VTS-{timezone.localtime(generated_at).strftime('%Y%m%d-%H%M')}"
    output = BytesIO()
    document = _build_document(output, title=f"CU-VTS · {spec.title}")
    styles = _styles()

    if spec.key == ReportType.TRIP_SUMMARY:
        story = _build_trip_ledger_story(
            styles=styles,
            spec=spec,
            selected_vehicles=selected_vehicles,
            trip_summaries=trip_summaries,
            metrics=metrics,
            date_scope=date_scope_text,
            vehicle_scope=scope_desc,
            generated_by=generated_by,
            generated_at=generated_at,
        )
    elif spec.key == ReportType.SAFETY_AUDIT:
        story = _build_safety_audit_story(
            styles=styles,
            spec=spec,
            vehicle_summaries=vehicle_summaries,
            locations=locations,
            metrics=metrics,
            date_scope=date_scope_text,
            vehicle_scope=scope_desc,
            generated_by=generated_by,
            generated_at=generated_at,
        )
    elif spec.key == ReportType.TELEMETRY_AUDIT:
        sampled = _sample_locations(
            locations=locations,
            interval_seconds=sample_interval_seconds,
        )
        story = _build_telemetry_audit_story(
            styles=styles,
            spec=spec,
            selected_vehicles=selected_vehicles,
            locations=locations,
            sampled=sampled,
            metrics=metrics,
            sample_interval_seconds=sample_interval_seconds,
            date_scope=date_scope_text,
            vehicle_scope=scope_desc,
            generated_by=generated_by,
            generated_at=generated_at,
        )
    else:
        bus_routes = list(BusRoute.objects.prefetch_related("stops").order_by("name"))
        story = _build_executive_overview_story(
            styles=styles,
            spec=spec,
            selected_vehicles=selected_vehicles,
            vehicle_summaries=vehicle_summaries,
            bus_routes=bus_routes,
            metrics=metrics,
            date_scope=date_scope_text,
            vehicle_scope=scope_desc,
            generated_by=generated_by,
            generated_at=generated_at,
        )

    document.build(
        story,
        canvasmaker=lambda *args, **kwargs: _NumberedCanvas(
            *args,
            header_tag=spec.header_tag,
            document_ref=document_ref,
            **kwargs,
        ),
    )
    return output.getvalue()


def fleet_record_filename(
    *,
    generated_at: datetime | None = None,
    report_type: str = ReportType.EXECUTIVE_SUMMARY,
) -> str:
    """Return an ASCII-only attachment filename safe for every browser."""
    stamp = timezone.localtime(generated_at or timezone.now()).strftime("%Y%m%d-%H%M")
    spec = REPORT_CATALOG.get(report_type)
    if spec and spec.key != ReportType.EXECUTIVE_SUMMARY:
        return f"fleet-record-{spec.filename_slug}-{stamp}.pdf"
    return f"fleet-record-{stamp}.pdf"


def build_trip_history_pdf(
    *,
    vehicles: Iterable[Vehicle] | QuerySet[Vehicle],
    on_date: date | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    generated_by: str = "",
    report_type: str = ReportType.TRIP_SUMMARY,
    sample_interval_seconds: int = DEFAULT_SAMPLE_INTERVAL_SECONDS,
) -> bytes:
    """Export per-vehicle and combined chronological trip history without 5s spam.

    Defaults to ``trip_summary`` (clean one-row-per-trip ledgers per vehicle
    followed by a separate combined dispatch schedule page). Admins can also
    request ``telemetry_audit`` (smart-sampled checkpoints per vehicle +
    combined chronological checkpoint trace) or ``safety_audit``.
    """
    spec = REPORT_CATALOG.get(report_type, REPORT_CATALOG[ReportType.TRIP_SUMMARY])
    selected_vehicles = list(vehicles)
    vehicle_ids = [vehicle.pk for vehicle in selected_vehicles if vehicle.pk is not None]

    locations_query = Location.objects.filter(vehicle_id__in=vehicle_ids)
    trips_query = Trip.objects.filter(vehicle_id__in=vehicle_ids)
    if on_date is not None:
        day_start = _start_of_local_day(on_date)
        day_end = _end_of_local_day(on_date)
        locations_query = locations_query.filter(captured_at__range=(day_start, day_end))
        trips_query = trips_query.filter(started_at__range=(day_start, day_end))
    if start is not None:
        locations_query = locations_query.filter(captured_at__gte=start)
        trips_query = trips_query.filter(started_at__gte=start)
    if end is not None:
        locations_query = locations_query.filter(captured_at__lte=end)
        trips_query = trips_query.filter(started_at__lte=end)

    locations = list(
        locations_query.select_related("vehicle", "driver__user", "trip").order_by(
            "captured_at", "pk"
        )
    )
    trips = list(trips_query.select_related("vehicle", "driver__user").order_by("started_at", "pk"))

    trip_summaries = _summarise_trips(trips=trips, locations=locations)
    active_assignments = {
        assignment.vehicle_id: assignment.driver.display_name
        for assignment in DriverAssignment.objects.filter(
            vehicle_id__in=vehicle_ids, is_active=True
        ).select_related("driver__user")
    }
    vehicle_summaries = _summarise_vehicles(
        vehicles=selected_vehicles,
        locations=locations,
        trip_summaries=trip_summaries,
        active_assignments=active_assignments,
    )
    metrics = _summarise_locations(
        locations=locations,
        vehicle_count=len(selected_vehicles),
        trip_count=len(trip_summaries),
        active_vehicle_count=sum(1 for v in selected_vehicles if v.is_active),
    )

    date_scope = _trip_history_scope(on_date=on_date, start=start, end=end)
    vehicle_scope = _default_vehicle_scope_label(selected_vehicles)
    generated_at = timezone.now()
    document_ref = f"CU-VTS-TH-{timezone.localtime(generated_at).strftime('%Y%m%d-%H%M')}"

    output = BytesIO()
    document = _build_document(output, title=f"CU-VTS · {spec.title}")
    styles = _styles()

    if spec.key == ReportType.SAFETY_AUDIT:
        story = _build_safety_audit_story(
            styles=styles,
            spec=spec,
            vehicle_summaries=vehicle_summaries,
            locations=locations,
            metrics=metrics,
            date_scope=date_scope,
            vehicle_scope=vehicle_scope,
            generated_by=generated_by,
            generated_at=generated_at,
        )
    elif spec.key == ReportType.TELEMETRY_AUDIT:
        story = _build_trip_history_telemetry_story(
            styles=styles,
            spec=spec,
            selected_vehicles=selected_vehicles,
            locations=locations,
            metrics=metrics,
            sample_interval_seconds=sample_interval_seconds,
            date_scope=date_scope,
            vehicle_scope=vehicle_scope,
            generated_by=generated_by,
            generated_at=generated_at,
        )
    else:
        story = _build_trip_ledger_story(
            styles=styles,
            spec=spec,
            selected_vehicles=selected_vehicles,
            trip_summaries=trip_summaries,
            metrics=metrics,
            date_scope=date_scope,
            vehicle_scope=vehicle_scope,
            generated_by=generated_by,
            generated_at=generated_at,
        )

    document.build(
        story,
        canvasmaker=lambda *args, **kwargs: _NumberedCanvas(
            *args,
            header_tag=spec.header_tag,
            document_ref=document_ref,
            **kwargs,
        ),
    )
    return output.getvalue()


def trip_history_filename(
    *,
    generated_at: datetime | None = None,
    report_type: str = ReportType.TRIP_SUMMARY,
) -> str:
    """Return an ASCII-only filename for a trip-history PDF export."""
    stamp = timezone.localtime(generated_at or timezone.now()).strftime("%Y%m%d-%H%M")
    spec = REPORT_CATALOG.get(report_type)
    if spec and spec.key != ReportType.TRIP_SUMMARY:
        return f"trip-history-{spec.filename_slug}-{stamp}.pdf"
    return f"trip-history-{stamp}.pdf"


# ---------------------------------------------------------------------------
# Document shell & styles
# ---------------------------------------------------------------------------


def _build_document(output: BytesIO, *, title: str) -> BaseDocTemplate:
    page_width, page_height = A4
    document = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=22 * mm,
        bottomMargin=17 * mm,
        title=title,
        author="University of Chittagong Vehicle Tracking System (CU-VTS)",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        page_width - document.leftMargin - document.rightMargin,
        page_height - document.topMargin - document.bottomMargin,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="record-body",
    )
    document.addPageTemplates(PageTemplate(id="cu-vts-report", frames=[frame]))
    return document


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle(
            "ReportKicker",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9.5,
            textColor=COBALT,
            spaceAfter=1 * mm,
        ),
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22.5,
            textColor=NAVY,
            spaceAfter=1.2 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=10.5,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14.5,
            textColor=NAVY,
            spaceBefore=2.5 * mm,
            spaceAfter=1.2 * mm,
        ),
        "subsection": ParagraphStyle(
            "ReportSubsection",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.4,
            leading=12,
            textColor=NAVY,
            spaceBefore=2 * mm,
            spaceAfter=0.8 * mm,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.8,
            textColor=INK,
        ),
        "muted": ParagraphStyle(
            "ReportMuted",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.8,
            textColor=MUTED,
        ),
        "spec_label": ParagraphStyle(
            "ReportSpecLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.0,
            leading=9.5,
            textColor=NAVY,
        ),
        "spec_value": ParagraphStyle(
            "ReportSpecValue",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.1,
            leading=9.8,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.6,
            leading=8.2,
            textColor=colors.white,
        ),
        "table": ParagraphStyle(
            "ReportTable",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=6.7,
            leading=8.6,
            textColor=INK,
        ),
        "table_right": ParagraphStyle(
            "ReportTableRight",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=6.7,
            leading=8.6,
            textColor=INK,
            alignment=TA_RIGHT,
        ),
        "table_center": ParagraphStyle(
            "ReportTableCenter",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.5,
            leading=8.4,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "metric": ParagraphStyle(
            "ReportMetric",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=15,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "ReportMetricLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.4,
            leading=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "metric_sub": ParagraphStyle(
            "ReportMetricSub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=6.2,
            leading=7.8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "insight_title": ParagraphStyle(
            "ReportInsightTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=10,
            textColor=NAVY,
            spaceAfter=1 * mm,
        ),
        "insight_item": ParagraphStyle(
            "ReportInsightItem",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=10.2,
            textColor=INK,
        ),
    }


# ---------------------------------------------------------------------------
# Report 1: Executive Fleet Overview (Default Fleet PDF — zero 5s spam)
# ---------------------------------------------------------------------------


def _build_executive_overview_story(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    selected_vehicles: list[Vehicle],
    vehicle_summaries: list[_VehicleSummary],
    bus_routes: list[BusRoute],
    metrics: _ReportMetrics,
    date_scope: str,
    vehicle_scope: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    inputs_summary = (
        f"Scope: {vehicle_scope} ({len(selected_vehicles)} vehicle"
        f"{'s' if len(selected_vehicles) != 1 else ''}); Date window: {date_scope}. "
        f"Aggregated across {_format_number(metrics.record_count)} immutable GPS fixes "
        f"and {_format_number(metrics.trip_count)} trips from Django models "
        f"(Vehicle, DriverAssignment, BusRoute, Trip, Location). Raw 5-second "
        f"coordinates are omitted for readability."
    )
    story = _report_header_block(
        styles=styles,
        spec=spec,
        inputs_summary=inputs_summary,
        generated_by=generated_by,
        generated_at=generated_at,
    )

    compliance_rate = _fleet_compliance_pct(metrics)
    story.append(
        _kpi_strip(
            cards=[
                (
                    "FLEET COVERAGE",
                    f"{metrics.active_vehicle_count} / {metrics.vehicle_count}",
                    "Active / Selected buses",
                ),
                (
                    "RECORDED TRIPS",
                    _format_number(metrics.trip_count),
                    f"{_format_number(metrics.record_count)} GPS fixes analysed",
                ),
                (
                    "EST. DISTANCE",
                    _format_distance(metrics.estimated_distance_km),
                    f"Avg {_format_speed(metrics.average_speed_kmh)}",
                ),
                (
                    "SPEED COMPLIANCE",
                    f"{compliance_rate:.1f}%" if compliance_rate is not None else "—",
                    f"Peak {_format_speed(metrics.peak_speed_kmh)}",
                ),
            ],
            styles=styles,
        )
    )
    story.append(Spacer(1, 3.2 * mm))
    story.append(_insights_box(_generate_executive_insights(vehicle_summaries, metrics), styles))
    story.append(Spacer(1, 3.2 * mm))

    story.append(Paragraph("Fleet performance by vehicle", styles["section"]))
    story.append(
        Paragraph(
            "One consolidated operational row per vehicle. Distances are Haversine trace sums "
            "computed over every recorded GPS fix within each trip.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 2 * mm))
    if vehicle_summaries:
        story.append(_vehicle_performance_table(vehicle_summaries, styles))
    else:
        story.append(_empty_box(styles, "No vehicles are included in this report selection."))

    if bus_routes:
        story.append(Spacer(1, 3.5 * mm))
        story.append(
            KeepTogether(
                [
                    Paragraph("Configured campus bus route network", styles["section"]),
                    Paragraph(
                        "Fixed shuttle corridors registered in CU-VTS with ordered stops.",
                        styles["muted"],
                    ),
                    Spacer(1, 1.8 * mm),
                    _bus_routes_table(bus_routes, styles),
                ]
            )
        )

    story.extend(_build_analytics_story(styles=styles, metrics=metrics))
    return story


# ---------------------------------------------------------------------------
# Report 2: Trip Operations & Journey Ledger (Default Trip History PDF)
# ---------------------------------------------------------------------------


def _build_trip_ledger_story(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    selected_vehicles: list[Vehicle],
    trip_summaries: list[_TripSummary],
    metrics: _ReportMetrics,
    date_scope: str,
    vehicle_scope: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    inputs_summary = (
        f"Scope: {vehicle_scope} ({len(selected_vehicles)} vehicle"
        f"{'s' if len(selected_vehicles) != 1 else ''}); Window: {date_scope}. "
        f"Summarises {_format_number(len(trip_summaries))} recorded trips computed from "
        f"{_format_number(metrics.record_count)} underlying GPS fixes (Trip, Location, "
        f"Vehicle, DriverProfile). Raw 5-second fixes are condensed into one row per trip."
    )
    story = _report_header_block(
        styles=styles,
        spec=spec,
        inputs_summary=inputs_summary,
        generated_by=generated_by,
        generated_at=generated_at,
    )

    total_minutes = sum(t.duration_minutes or 0.0 for t in trip_summaries)
    vehicles_with_trips = len({t.vehicle_id for t in trip_summaries})
    story.append(
        _kpi_strip(
            cards=[
                (
                    "TOTAL TRIPS",
                    _format_number(len(trip_summaries)),
                    f"Across {vehicles_with_trips} active bus{'es' if vehicles_with_trips != 1 else ''}",
                ),
                (
                    "OPERATING TIME",
                    _format_duration(total_minutes) if total_minutes > 0 else "—",
                    "Cumulative trip duration",
                ),
                (
                    "EST. DISTANCE",
                    _format_distance(metrics.estimated_distance_km),
                    f"From {_format_number(metrics.record_count)} GPS fixes",
                ),
                (
                    "AVG / PEAK SPEED",
                    _format_speed(metrics.average_speed_kmh),
                    f"Peak {_format_speed(metrics.peak_speed_kmh)}",
                ),
            ],
            styles=styles,
        )
    )
    story.append(Spacer(1, 3.5 * mm))
    story.append(Paragraph("Part 1 · Journey ledger by vehicle", styles["section"]))
    story.append(
        Paragraph(
            "Each vehicle section lists every recorded trip in chronological order with "
            "departure/arrival times, driver, duration, distance, and start/end coordinates.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 2 * mm))

    trips_by_vehicle: dict[int, list[_TripSummary]] = defaultdict(list)
    for item in trip_summaries:
        trips_by_vehicle[item.vehicle_id].append(item)

    if not selected_vehicles:
        story.append(_empty_box(styles, "No vehicles are available for this trip ledger."))

    for index, vehicle in enumerate(selected_vehicles, start=1):
        v_trips = trips_by_vehicle.get(vehicle.pk, [])
        v_distance = sum(t.distance_km for t in v_trips)
        v_fixes = sum(t.fix_count for t in v_trips)
        route = vehicle.route_label or "Route not assigned"
        state = "Active" if vehicle.is_active else "Inactive"
        reg = f" · Reg. {vehicle.registration_number}" if vehicle.registration_number else ""
        meta = (
            f"{route} · {state}{reg}  |  {len(v_trips)} trip{'s' if len(v_trips) != 1 else ''} · "
            f"{_format_distance(v_distance)} · {_format_number(v_fixes)} raw GPS fixes condensed"
        )
        section_header = [
            Paragraph(f"{index}. {_safe_text(vehicle.bus_number)}", styles["subsection"]),
            Paragraph(_safe_text(meta), styles["muted"]),
            Spacer(1, 1.5 * mm),
        ]
        if v_trips:
            story.extend(section_header)
            story.append(_trip_ledger_table(v_trips, styles, include_vehicle=False))
        else:
            story.append(
                KeepTogether(
                    section_header
                    + [
                        _empty_box(
                            styles,
                            "No trips recorded for this vehicle within the selected date/time window.",
                        )
                    ]
                )
            )
        if index != len(selected_vehicles):
            story.append(Spacer(1, 3 * mm))

    # Dedicated page for combined chronological dispatch schedule across all buses.
    story.extend(
        [
            PageBreak(),
            Paragraph("PART 2  ·  COMBINED DISPATCH CHRONOLOGY", styles["kicker"]),
            Paragraph("All-vehicle chronological trip schedule", styles["title"]),
            Paragraph(
                _safe_text(
                    f"{date_scope}  ·  {_format_number(len(trip_summaries))} trip"
                    f"{'s' if len(trip_summaries) != 1 else ''} across "
                    f"{len(selected_vehicles)} selected vehicle"
                    f"{'s' if len(selected_vehicles) != 1 else ''}."
                ),
                styles["subtitle"],
            ),
            Spacer(1, 3.5 * mm),
        ]
    )
    if trip_summaries:
        story.append(_trip_ledger_table(trip_summaries, styles, include_vehicle=True))
    else:
        story.append(
            _empty_box(
                styles,
                "No trips match the selected date and time range across the fleet.",
            )
        )
    return story


# ---------------------------------------------------------------------------
# Report 3: Vehicle Speed Compliance & Safety Audit
# ---------------------------------------------------------------------------


def _build_safety_audit_story(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    vehicle_summaries: list[_VehicleSummary],
    locations: list[Location],
    metrics: _ReportMetrics,
    date_scope: str,
    vehicle_scope: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    overspeed_events = _extract_overspeed_events(locations)
    compliance_pct = _fleet_compliance_pct(metrics)

    inputs_summary = (
        f"Scope: {vehicle_scope} ({len(vehicle_summaries)} vehicle"
        f"{'s' if len(vehicle_summaries) != 1 else ''}); Window: {date_scope}. "
        f"Audited {_format_number(metrics.record_count)} GPS fixes "
        f"({_format_number(metrics.speed_sample_count)} with speed telemetry) against "
        f"the {OVERSPEED_THRESHOLD_KMH:.0f} km/h campus threshold. Consecutive overspeed "
        f"pings within 60 seconds per bus are grouped into distinct incidents."
    )
    story = _report_header_block(
        styles=styles,
        spec=spec,
        inputs_summary=inputs_summary,
        generated_by=generated_by,
        generated_at=generated_at,
    )

    story.append(
        _kpi_strip(
            cards=[
                (
                    "COMPLIANCE RATE",
                    f"{compliance_pct:.1f}%" if compliance_pct is not None else "—",
                    f"Fixes below {OVERSPEED_THRESHOLD_KMH:.0f} km/h",
                ),
                (
                    "OVERSPEED EVENTS",
                    _format_number(len(overspeed_events)),
                    f"{_format_number(metrics.overspeed_count)} raw fixes >=45 km/h",
                ),
                (
                    "PEAK SPEED",
                    _format_speed(metrics.peak_speed_kmh),
                    f"Fleet avg {_format_speed(metrics.average_speed_kmh)}",
                ),
                (
                    "MEAN GPS ACCURACY",
                    _format_accuracy(metrics.average_accuracy_m),
                    "Lower value = sharper signal",
                ),
            ],
            styles=styles,
        )
    )
    story.append(Spacer(1, 3.2 * mm))

    story.append(Paragraph("Vehicle safety & telemetry scorecard", styles["section"]))
    story.append(
        Paragraph(
            "Ratings: Compliant (0 overspeed fixes), Review (1–4 overspeed fixes and >=90% "
            "compliance), Alert (>=5 overspeed fixes, <90% compliance, or peak >=60 km/h).",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 1.8 * mm))
    if vehicle_summaries:
        story.append(_safety_scorecard_table(vehicle_summaries, styles))
    else:
        story.append(_empty_box(styles, "No vehicles are included in this safety audit."))

    story.append(Spacer(1, 3.5 * mm))
    story.append(
        Paragraph(
            f"Flagged high-speed incidents (>={OVERSPEED_THRESHOLD_KMH:.0f} km/h)",
            styles["section"],
        )
    )
    story.append(
        Paragraph(
            "Distinct high-speed occurrences (deduplicated at 60-second intervals per vehicle, "
            "capped at the 40 highest-speed incidents for focused supervisor review).",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 1.8 * mm))
    if overspeed_events:
        story.append(_overspeed_events_table(overspeed_events[:40], styles))
    else:
        story.append(
            _empty_box(
                styles,
                f"No overspeed incidents (>={OVERSPEED_THRESHOLD_KMH:.0f} km/h) were recorded "
                "within the selected fleet and date window.",
            )
        )

    story.extend(_build_analytics_story(styles=styles, metrics=metrics))
    return story


# ---------------------------------------------------------------------------
# Report 4: Smart-Sampled Route Telemetry Trace (Optional Coordinate Audit)
# ---------------------------------------------------------------------------


def _build_telemetry_audit_story(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    selected_vehicles: list[Vehicle],
    locations: list[Location],
    sampled: list[_SampledCheckpoint],
    metrics: _ReportMetrics,
    sample_interval_seconds: int,
    date_scope: str,
    vehicle_scope: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    sampling_note = _sampling_description(
        raw_count=len(locations),
        sampled_count=len(sampled),
        interval_seconds=sample_interval_seconds,
    )
    inputs_summary = (
        f"Scope: {vehicle_scope} ({len(selected_vehicles)} vehicle"
        f"{'s' if len(selected_vehicles) != 1 else ''}); Window: {date_scope}. "
        f"{sampling_note}."
    )
    story = _report_header_block(
        styles=styles,
        spec=spec,
        inputs_summary=inputs_summary,
        generated_by=generated_by,
        generated_at=generated_at,
    )
    story.append(
        _kpi_strip(
            cards=[
                (
                    "CHECKPOINTS SHOWN",
                    _format_number(len(sampled)),
                    f"From {_format_number(len(locations))} raw GPS fixes",
                ),
                (
                    "TRIPS COVERED",
                    _format_number(metrics.trip_count),
                    f"{metrics.vehicle_count} vehicle{'s' if metrics.vehicle_count != 1 else ''}",
                ),
                (
                    "EST. DISTANCE",
                    _format_distance(metrics.estimated_distance_km),
                    "Calculated on full trace",
                ),
                (
                    "AVG / PEAK SPEED",
                    _format_speed(metrics.average_speed_kmh),
                    f"Peak {_format_speed(metrics.peak_speed_kmh)}",
                ),
            ],
            styles=styles,
        )
    )
    story.append(Spacer(1, 3.2 * mm))
    story.append(Paragraph("Auditable route checkpoints", styles["section"]))
    story.append(Paragraph(_safe_text(sampling_note), styles["muted"]))
    story.append(Spacer(1, 2 * mm))

    if sampled:
        story.append(_checkpoint_table(sampled, styles))
    else:
        story.append(
            _empty_box(
                styles,
                "No GPS fixes match this selection. The analytics page is still included so "
                "this export remains a complete auditable record.",
            )
        )

    story.extend(_build_analytics_story(styles=styles, metrics=metrics))
    return story


def _build_trip_history_telemetry_story(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    selected_vehicles: list[Vehicle],
    locations: list[Location],
    metrics: _ReportMetrics,
    sample_interval_seconds: int,
    date_scope: str,
    vehicle_scope: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    sampled_all = _sample_locations(locations=locations, interval_seconds=sample_interval_seconds)
    sampling_note = _sampling_description(
        raw_count=len(locations),
        sampled_count=len(sampled_all),
        interval_seconds=sample_interval_seconds,
    )
    inputs_summary = (
        f"Scope: {vehicle_scope} ({len(selected_vehicles)} vehicle"
        f"{'s' if len(selected_vehicles) != 1 else ''}); Window: {date_scope}. "
        f"{sampling_note}."
    )
    story = _report_header_block(
        styles=styles,
        spec=spec,
        inputs_summary=inputs_summary,
        generated_by=generated_by,
        generated_at=generated_at,
    )
    story.append(Paragraph("Part 1 · Sampled checkpoints by vehicle", styles["section"]))
    story.append(Paragraph(_safe_text(sampling_note), styles["muted"]))
    story.append(Spacer(1, 2 * mm))

    sampled_by_vehicle: dict[int, list[_SampledCheckpoint]] = defaultdict(list)
    for cp in sampled_all:
        sampled_by_vehicle[cp.location.vehicle_id].append(cp)

    for index, vehicle in enumerate(selected_vehicles, start=1):
        v_cps = sampled_by_vehicle.get(vehicle.pk, [])
        route = vehicle.route_label or "Route not assigned"
        story.extend(
            [
                Paragraph(f"{index}. {_safe_text(vehicle.bus_number)}", styles["subsection"]),
                Paragraph(
                    _safe_text(
                        f"{route}  ·  {_format_number(len(v_cps))} checkpoint"
                        f"{'s' if len(v_cps) != 1 else ''}"
                    ),
                    styles["muted"],
                ),
                Spacer(1, 1.5 * mm),
            ]
        )
        if v_cps:
            story.append(_checkpoint_table(v_cps, styles))
        else:
            story.append(
                _empty_box(styles, "No GPS records match the selected date and time range.")
            )
        if index != len(selected_vehicles):
            story.append(Spacer(1, 3 * mm))

    story.extend(
        [
            PageBreak(),
            Paragraph("PART 2  ·  COMBINED CHRONOLOGICAL CHECKPOINTS", styles["kicker"]),
            Paragraph("All-vehicle route trace in time order", styles["title"]),
            Paragraph(
                _safe_text(f"{date_scope}  ·  {sampling_note}"),
                styles["subtitle"],
            ),
            Spacer(1, 3.5 * mm),
        ]
    )
    if sampled_all:
        story.append(_checkpoint_table(sampled_all, styles))
    else:
        story.append(_empty_box(styles, "No GPS records match the selected date and time range."))
    return story


# ---------------------------------------------------------------------------
# Shared components: 5-Point Teacher Specification Panel, KPIs, Tables, Charts
# ---------------------------------------------------------------------------


def _report_header_block(
    *,
    styles: dict[str, ParagraphStyle],
    spec: ReportSpec,
    inputs_summary: str,
    generated_by: str,
    generated_at: datetime,
) -> list[Flowable]:
    prepared_line = f"Prepared {_format_datetime(generated_at)}"
    if generated_by:
        prepared_line = f"{prepared_line}  ·  Requested by {generated_by}"

    return [
        Paragraph(_safe_text(spec.kicker), styles["kicker"]),
        Paragraph(_safe_text(spec.title), styles["title"]),
        Paragraph(_safe_text(prepared_line), styles["subtitle"]),
        Spacer(1, 3 * mm),
        _build_spec_panel(spec=spec, inputs_summary=inputs_summary, styles=styles),
        Spacer(1, 3.5 * mm),
    ]


def _build_spec_panel(
    *,
    spec: ReportSpec,
    inputs_summary: str,
    styles: dict[str, ParagraphStyle],
) -> Table:
    """Structured five-part Report Specification & System Context panel.

    Explicitly answers: (i) Purpose, (ii) Intended Audience, (iii) Inputs,
    (iv) Outputs, and (v) Platform & Environment.
    """
    rows = [
        [
            Paragraph("REPORT SPECIFICATION & SYSTEM CONTEXT", styles["table_header"]),
            Paragraph("", styles["table_header"]),
        ],
        [
            Paragraph("i. Purpose", styles["spec_label"]),
            Paragraph(_safe_text(spec.purpose), styles["spec_value"]),
        ],
        [
            Paragraph("ii. Intended Audience", styles["spec_label"]),
            Paragraph(_safe_text(spec.audience), styles["spec_value"]),
        ],
        [
            Paragraph("iii. Inputs & Scope", styles["spec_label"]),
            Paragraph(_safe_text(inputs_summary), styles["spec_value"]),
        ],
        [
            Paragraph("iv. Outputs Delivered", styles["spec_label"]),
            Paragraph(_safe_text(spec.outputs), styles["spec_value"]),
        ],
        [
            Paragraph("v. Platform & Environment", styles["spec_label"]),
            Paragraph(_safe_text(_platform_environment_summary()), styles["spec_value"]),
        ],
    ]
    table = Table(rows, colWidths=[38 * mm, 142 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("BACKGROUND", (0, 0), (1, 0), NAVY),
                ("BACKGROUND", (0, 1), (0, -1), SPEC_BG),
                ("BACKGROUND", (1, 1), (1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 1), (-1, -1), 0.3, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, 0), 1.8 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 1.8 * mm),
                ("TOPPADDING", (0, 1), (-1, -1), 1.4 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 1.4 * mm),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    return table


def _platform_environment_summary() -> str:
    """Return a concise, secret-free runtime & delivery environment summary."""
    db_vendor = (connection.vendor or "sqlite").upper()
    tz_name = getattr(settings, "TIME_ZONE", "UTC")
    return (
        f"CU-VTS Web Platform (Django {django.get_version()} + DRF on Python "
        f"{platform.python_version()}, {db_vendor} database, ReportLab "
        f"{reportlab.__version__} vector PDF engine); Driver HTML5 Geolocation "
        f"browser client; Local timezone {tz_name}; Standard A4 print & digital PDF."
    )


def _kpi_strip(
    *, cards: list[tuple[str, str, str]], styles: dict[str, ParagraphStyle]
) -> Table:
    col_width = FRAME_WIDTH / len(cards)
    data = [
        [Paragraph(_safe_text(label), styles["metric_label"]) for label, _, _ in cards],
        [Paragraph(_safe_text(value), styles["metric"]) for _, value, _ in cards],
        [Paragraph(_safe_text(sub), styles["metric_sub"]) for _, _, sub in cards],
    ]
    table = Table(data, colWidths=[col_width] * len(cards))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("LINEABOVE", (0, 0), (-1, 0), 1.6, COBALT),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("LINEBEFORE", (1, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, 0), 2.0 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 0.4 * mm),
                ("TOPPADDING", (0, 1), (-1, 1), 0.4 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 0.4 * mm),
                ("TOPPADDING", (0, 2), (-1, 2), 0.2 * mm),
                ("BOTTOMPADDING", (0, 2), (-1, 2), 1.8 * mm),
            ]
        )
    )
    return table


def _insights_box(insights: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    body = "<br/>".join(f"•  {_safe_text(line)}" for line in insights)
    rows = [
        [Paragraph("KEY OPERATIONAL TAKEAWAYS", styles["insight_title"])],
        [Paragraph(body, styles["insight_item"])],
    ]
    table = Table(rows, colWidths=[FRAME_WIDTH], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), INSIGHT_BG),
                ("LINEBEFORE", (0, 0), (0, -1), 2.2, EMERALD),
                ("BOX", (0, 0), (-1, -1), 0.45, INSIGHT_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.0 * mm),
                ("TOPPADDING", (0, 0), (-1, 0), 2.0 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 0.4 * mm),
                ("TOPPADDING", (0, 1), (-1, 1), 0.4 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 2.0 * mm),
            ]
        )
    )
    return table


def _vehicle_performance_table(
    summaries: list[_VehicleSummary], styles: dict[str, ParagraphStyle]
) -> Table:
    headers = (
        "Bus / Reg.",
        "Assigned Route",
        "Driver",
        "Status",
        "Trips",
        "Est. Dist.",
        "Avg / Peak",
        "Signal / Last Seen",
    )
    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for item in summaries:
        reg = item.vehicle.registration_number or "—"
        route = item.vehicle.route_label or "Unassigned"
        status_colour = "#1E8E3E" if item.vehicle.is_active else "#64748B"
        status_text = "Active" if item.vehicle.is_active else "Inactive"
        last_seen = _format_datetime(item.last_captured_at) if item.last_captured_at else "No signal"
        acc_text = _format_accuracy(item.avg_accuracy_m)
        rows.append(
            [
                Paragraph(
                    f"<b>{_safe_text(item.vehicle.bus_number)}</b><br/>"
                    f"<font color='#64748B'>{_safe_text(reg)}</font>",
                    styles["table"],
                ),
                Paragraph(_safe_text(route), styles["table"]),
                Paragraph(_safe_text(item.assigned_driver), styles["table"]),
                Paragraph(
                    f"<font color='{status_colour}'><b>{status_text}</b></font>",
                    styles["table_center"],
                ),
                Paragraph(_format_number(item.trip_count), styles["table_right"]),
                Paragraph(_format_distance(item.distance_km), styles["table_right"]),
                Paragraph(
                    _format_speed_pair(item.avg_speed_kmh, item.peak_speed_kmh, prefix="Peak"),
                    styles["table_right"],
                ),
                Paragraph(
                    f"{_safe_text(last_seen)}<br/>"
                    f"<font color='#64748B'>GPS acc. {_safe_text(acc_text)}</font>",
                    styles["table"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[25 * mm, 34 * mm, 26 * mm, 15 * mm, 12 * mm, 18 * mm, 24 * mm, 26 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(_standard_table_style())
    return table


def _bus_routes_table(routes: list[BusRoute], styles: dict[str, ParagraphStyle]) -> Table:
    headers = ("Route Name", "Stops", "Ordered Intermediate Stops", "Start -> End Coordinates")
    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for route in routes:
        stops = list(route.stops.all())
        stop_names = " -> ".join(stop.name for stop in stops) if stops else "Direct corridor (no intermediate stops)"
        coords = (
            f"Start: {float(route.start_latitude):.4f}, {float(route.start_longitude):.4f}<br/>"
            f"End: {float(route.end_latitude):.4f}, {float(route.end_longitude):.4f}"
        )
        rows.append(
            [
                Paragraph(f"<b>{_safe_text(route.name)}</b>", styles["table"]),
                Paragraph(str(len(stops)), styles["table_center"]),
                Paragraph(_safe_text(stop_names), styles["table"]),
                Paragraph(coords, styles["table"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[42 * mm, 14 * mm, 70 * mm, 54 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(_standard_table_style())
    return table


def _trip_ledger_table(
    trips: list[_TripSummary],
    styles: dict[str, ParagraphStyle],
    *,
    include_vehicle: bool,
) -> Table:
    if include_vehicle:
        headers = (
            "Trip",
            "Vehicle / Route",
            "Driver",
            "Departure -> Arrival",
            "Duration",
            "Distance",
            "Avg / Peak",
            "Origin -> Dest.",
        )
        col_widths = [12 * mm, 29 * mm, 24 * mm, 34 * mm, 15 * mm, 16 * mm, 22 * mm, 28 * mm]
    else:
        headers = (
            "Trip",
            "Driver",
            "Departure -> Arrival",
            "Status",
            "Duration",
            "Distance",
            "Avg / Peak",
            "Origin -> Dest. (Lat, Lng)",
        )
        col_widths = [13 * mm, 28 * mm, 36 * mm, 16 * mm, 15 * mm, 17 * mm, 22 * mm, 33 * mm]

    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for item in trips:
        start_str = _format_datetime(item.started_at)
        end_str = (
            _format_time(item.ended_at)
            if item.ended_at and timezone.localdate(item.ended_at) == timezone.localdate(item.started_at)
            else (_format_datetime(item.ended_at) if item.ended_at else "Ongoing")
        )
        coords_html = _format_origin_dest(item.start_coords, item.end_coords)
        speed_html = _format_speed_pair(item.avg_speed_kmh, item.peak_speed_kmh, prefix="Max")
        if include_vehicle:
            rows.append(
                [
                    Paragraph(f"#{item.trip_id}", styles["table"]),
                    Paragraph(
                        f"<b>{_safe_text(item.bus_number)}</b><br/>"
                        f"<font color='#64748B'>{_safe_text(item.route_label)}</font>",
                        styles["table"],
                    ),
                    Paragraph(_safe_text(item.driver_name), styles["table"]),
                    Paragraph(
                        f"{_safe_text(start_str)}<br/>"
                        f"<font color='#64748B'>to {_safe_text(end_str)}</font>",
                        styles["table"],
                    ),
                    Paragraph(_format_duration(item.duration_minutes), styles["table_right"]),
                    Paragraph(_format_distance(item.distance_km), styles["table_right"]),
                    Paragraph(speed_html, styles["table_right"]),
                    Paragraph(coords_html, styles["table"]),
                ]
            )
        else:
            status_col = "#1E8E3E" if item.status == "COMPLETED" else "#1A73E8"
            status_lbl = "Completed" if item.status == "COMPLETED" else "Open"
            rows.append(
                [
                    Paragraph(f"#{item.trip_id}", styles["table"]),
                    Paragraph(_safe_text(item.driver_name), styles["table"]),
                    Paragraph(
                        f"{_safe_text(start_str)}<br/>"
                        f"<font color='#64748B'>to {_safe_text(end_str)}</font>",
                        styles["table"],
                    ),
                    Paragraph(
                        f"<font color='{status_col}'><b>{status_lbl}</b></font>",
                        styles["table_center"],
                    ),
                    Paragraph(_format_duration(item.duration_minutes), styles["table_right"]),
                    Paragraph(_format_distance(item.distance_km), styles["table_right"]),
                    Paragraph(speed_html, styles["table_right"]),
                    Paragraph(coords_html, styles["table"]),
                ]
            )

    table = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(_standard_table_style())
    return table


def _safety_scorecard_table(
    summaries: list[_VehicleSummary], styles: dict[str, ParagraphStyle]
) -> Table:
    headers = (
        "Vehicle / Route",
        "Driver",
        "Trips / Fixes",
        "GPS Acc.",
        "Avg / Peak",
        ">=45 km/h",
        "Compliance",
        "Safety Rating",
    )
    rating_colours = {
        "Compliant": "#1E8E3E",
        "Review": "#D97706",
        "Alert": "#DC2626",
        "No Data": "#64748B",
    }
    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for item in summaries:
        rating = item.safety_rating
        rating_hex = rating_colours.get(rating, "#64748B")
        comp = f"{item.compliance_pct:.1f}%" if item.compliance_pct is not None else "—"
        rows.append(
            [
                Paragraph(
                    f"<b>{_safe_text(item.vehicle.bus_number)}</b><br/>"
                    f"<font color='#64748B'>{_safe_text(item.vehicle.route_label or 'Unassigned')}</font>",
                    styles["table"],
                ),
                Paragraph(_safe_text(item.assigned_driver), styles["table"]),
                Paragraph(
                    f"{_format_number(item.trip_count)} trip{'s' if item.trip_count != 1 else ''}<br/>"
                    f"<font color='#64748B'>{_format_number(item.fix_count)} fix{'es' if item.fix_count != 1 else ''}</font>",
                    styles["table_right"],
                ),
                Paragraph(_format_accuracy(item.avg_accuracy_m), styles["table_right"]),
                Paragraph(
                    _format_speed_pair(item.avg_speed_kmh, item.peak_speed_kmh, prefix="Max"),
                    styles["table_right"],
                ),
                Paragraph(_format_number(item.overspeed_count), styles["table_right"]),
                Paragraph(comp, styles["table_right"]),
                Paragraph(
                    f"<font color='{rating_hex}'><b>{rating}</b></font>",
                    styles["table_center"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[36 * mm, 26 * mm, 20 * mm, 16 * mm, 24 * mm, 18 * mm, 18 * mm, 22 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(_standard_table_style())
    return table


def _overspeed_events_table(
    events: list[Location], styles: dict[str, ParagraphStyle]
) -> Table:
    headers = ("Timestamp", "Vehicle / Route", "Driver", "Trip", "Speed", "GPS Acc.", "Coordinates")
    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for loc in events:
        route = loc.vehicle.route_label or "Route not set"
        speed_val = _as_float(loc.speed_kmh)
        rows.append(
            [
                Paragraph(_safe_text(_format_datetime(loc.captured_at)), styles["table"]),
                Paragraph(
                    f"<b>{_safe_text(loc.vehicle.bus_number)}</b><br/>"
                    f"<font color='#64748B'>{_safe_text(route)}</font>",
                    styles["table"],
                ),
                Paragraph(_safe_text(loc.driver.display_name), styles["table"]),
                Paragraph(f"#{loc.trip_id}", styles["table"]),
                Paragraph(
                    f"<font color='#DC2626'><b>{_safe_text(_format_speed(speed_val))}</b></font>",
                    styles["table_right"],
                ),
                Paragraph(_format_accuracy(_as_float(loc.accuracy_m)), styles["table_right"]),
                Paragraph(
                    f"{float(loc.latitude):.5f}, {float(loc.longitude):.5f}",
                    styles["table"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[28 * mm, 34 * mm, 28 * mm, 14 * mm, 20 * mm, 16 * mm, 40 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(_standard_table_style())
    return table


def _checkpoint_table(
    checkpoints: list[_SampledCheckpoint], styles: dict[str, ParagraphStyle]
) -> Table:
    headers = ("Timestamp", "Event", "Vehicle / Route", "Driver", "Trip", "Speed", "Acc.", "Coordinates")
    tag_colours = {
        "Start": "#1E8E3E",
        "End": "#0F2744",
        "Overspeed": "#DC2626",
        "Peak": "#D97706",
        "Checkpoint": "#1A73E8",
        "Fix": "#64748B",
    }
    rows: list[list[Paragraph]] = [
        [Paragraph(h, styles["table_header"]) for h in headers]
    ]
    for cp in checkpoints:
        loc = cp.location
        route = loc.vehicle.route_label or "Route not set"
        colour = tag_colours.get(cp.tag, "#64748B")
        rows.append(
            [
                Paragraph(_safe_text(_format_datetime(loc.captured_at)), styles["table"]),
                Paragraph(f"<font color='{colour}'><b>{_safe_text(cp.tag)}</b></font>", styles["table_center"]),
                Paragraph(
                    f"<b>{_safe_text(loc.vehicle.bus_number)}</b><br/>"
                    f"<font color='#64748B'>{_safe_text(route)}</font>",
                    styles["table"],
                ),
                Paragraph(_safe_text(loc.driver.display_name), styles["table"]),
                Paragraph(f"#{loc.trip_id}", styles["table"]),
                Paragraph(_format_speed(_as_float(loc.speed_kmh)), styles["table_right"]),
                Paragraph(_format_accuracy(_as_float(loc.accuracy_m)), styles["table_right"]),
                Paragraph(
                    f"{float(loc.latitude):.5f}, {float(loc.longitude):.5f}",
                    styles["table"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[26 * mm, 18 * mm, 30 * mm, 24 * mm, 12 * mm, 16 * mm, 14 * mm, 40 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(_standard_table_style())
    return table


def _build_analytics_story(
    *, styles: dict[str, ParagraphStyle], metrics: _ReportMetrics
) -> list[Flowable]:
    interval = _recording_interval(metrics)
    distance_data: list[tuple[str, float]] = list(metrics.vehicle_distances)
    use_distance = any(val > 0 for _, val in distance_data)
    second_chart = (
        _BarChart(
            title="Estimated distance by vehicle (km)",
            subtitle="Haversine trace distance per bus across the selected period (top 10)",
            data=distance_data,
            colour=EMERALD,
            value_suffix=" km",
            decimals=1,
        )
        if use_distance
        else _BarChart(
            title="Telemetry activity by vehicle",
            subtitle="Recorded GPS fixes by vehicle (up to 10 most active)",
            data=[(label, float(val)) for label, val in metrics.vehicle_records],
            colour=EMERALD,
        )
    )

    return [
        PageBreak(),
        Paragraph("VISUAL ANALYTICS  ·  FLEET INSIGHTS", styles["kicker"]),
        Paragraph("Fleet activity & speed profile", styles["title"]),
        Paragraph(
            _safe_text(
                f"Observation window: {interval}  ·  {_format_number(metrics.record_count)} "
                f"GPS fixes analysed across {metrics.vehicle_count} vehicle"
                f"{'s' if metrics.vehicle_count != 1 else ''}."
            ),
            styles["subtitle"],
        ),
        Spacer(1, 3.5 * mm),
        _BarChart(
            title="Daily telemetry activity",
            subtitle="GPS fix volume across the most recent fourteen active recording days",
            data=[(label, float(val)) for label, val in metrics.daily_records],
            colour=COBALT,
        ),
        Spacer(1, 3.8 * mm),
        second_chart,
        Spacer(1, 3.8 * mm),
        _BarChart(
            title="Speed compliance distribution (km/h)",
            subtitle="Distribution of speed-bearing GPS fixes across operational speed bands",
            data=[(label, float(val)) for label, val in metrics.speed_buckets],
            colour=COBALT,
            bar_colours=[MUTED, EMERALD, COBALT, CRIMSON],
        ),
        Spacer(1, 2.5 * mm),
        Paragraph(
            "Methodology note: Distances represent cumulative great-circle (Haversine) trace "
            "lengths between consecutive GPS fixes within each trip rather than wheel odometer "
            "readings. Speed bands omit fixes where the client device did not report velocity.",
            styles["muted"],
        ),
    ]


def _empty_box(styles: dict[str, ParagraphStyle], message: str) -> Table:
    table = Table([[Paragraph(_safe_text(message), styles["body"])]], colWidths=[FRAME_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2 * mm),
            ]
        )
    )
    return table


def _standard_table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, LINE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SURFACE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 1.8 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 1.8 * mm),
            ("TOPPADDING", (0, 1), (-1, -1), 1.3 * mm),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 1.3 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.6 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1.6 * mm),
        ]
    )


# ---------------------------------------------------------------------------
# Aggregation, smart checkpoint sampling & executive insight derivation
# ---------------------------------------------------------------------------


def _sample_locations(
    *,
    locations: list[Location],
    interval_seconds: int = DEFAULT_SAMPLE_INTERVAL_SECONDS,
    min_distance_km: float = DEFAULT_SAMPLE_DISTANCE_KM,
) -> list[_SampledCheckpoint]:
    """Condense dense 5-second GPS updates into meaningful route checkpoints.

    For every trip:
      - Always retains the first fix (``Start``) and last fix (``End``).
      - Always retains the highest-speed fix if speed >= 45 km/h (``Overspeed``)
        or if it represents a clear journey speed peak.
      - Retains intermediate fixes whenever elapsed time >= ``interval_seconds``
        or movement since the last kept checkpoint >= ``min_distance_km``.
      - When ``interval_seconds <= 0``, returns all raw fixes transparently.
    """
    if not locations:
        return []

    by_trip: dict[int, list[Location]] = defaultdict(list)
    for loc in locations:
        by_trip[loc.trip_id].append(loc)

    kept_by_pk: dict[int, str] = {}
    for trip_locs in by_trip.values():
        if interval_seconds <= 0:
            for idx, loc in enumerate(trip_locs):
                if idx == 0:
                    kept_by_pk[loc.pk] = "Start"
                elif idx == len(trip_locs) - 1:
                    kept_by_pk[loc.pk] = "End"
                else:
                    speed = _as_float(loc.speed_kmh)
                    kept_by_pk[loc.pk] = (
                        "Overspeed"
                        if speed is not None and speed >= OVERSPEED_THRESHOLD_KMH
                        else "Fix"
                    )
            continue

        last_kept: Location | None = None
        peak_loc: Location | None = None
        peak_speed = -1.0

        for idx, loc in enumerate(trip_locs):
            speed = _as_float(loc.speed_kmh)
            if speed is not None and speed > peak_speed:
                peak_speed = speed
                peak_loc = loc

            if idx == 0:
                kept_by_pk[loc.pk] = "Start"
                last_kept = loc
                continue
            if idx == len(trip_locs) - 1:
                kept_by_pk[loc.pk] = "End"
                last_kept = loc
                continue

            if last_kept is None:
                kept_by_pk[loc.pk] = "Checkpoint"
                last_kept = loc
                continue

            elapsed = (loc.captured_at - last_kept.captured_at).total_seconds()
            moved_km = _haversine_km(
                float(last_kept.latitude),
                float(last_kept.longitude),
                float(loc.latitude),
                float(loc.longitude),
            )
            if elapsed >= interval_seconds or moved_km >= min_distance_km:
                tag = (
                    "Overspeed"
                    if speed is not None and speed >= OVERSPEED_THRESHOLD_KMH
                    else "Checkpoint"
                )
                kept_by_pk[loc.pk] = tag
                last_kept = loc

        if peak_loc is not None and peak_loc.pk not in kept_by_pk and peak_speed > 0:
            kept_by_pk[peak_loc.pk] = (
                "Overspeed" if peak_speed >= OVERSPEED_THRESHOLD_KMH else "Peak"
            )

    return [
        _SampledCheckpoint(location=loc, tag=kept_by_pk[loc.pk])
        for loc in locations
        if loc.pk in kept_by_pk
    ]


def _extract_overspeed_events(
    locations: list[Location], *, min_gap_seconds: int = 60
) -> list[Location]:
    """Return deduplicated high-speed events sorted by highest speed first."""
    last_flagged_by_vehicle: dict[int, datetime] = {}
    events: list[Location] = []
    for loc in locations:
        speed = _as_float(loc.speed_kmh)
        if speed is None or speed < OVERSPEED_THRESHOLD_KMH:
            continue
        prev = last_flagged_by_vehicle.get(loc.vehicle_id)
        if prev is not None and (loc.captured_at - prev).total_seconds() < min_gap_seconds:
            continue
        events.append(loc)
        last_flagged_by_vehicle[loc.vehicle_id] = loc.captured_at

    return sorted(events, key=lambda item: (-float(item.speed_kmh or 0), item.captured_at))


def _summarise_trips(
    *, trips: list[Trip], locations: list[Location]
) -> list[_TripSummary]:
    """Build one clean operational summary row per trip from full GPS traces."""
    locs_by_trip: dict[int, list[Location]] = defaultdict(list)
    trips_by_id: dict[int, Trip] = {trip.pk: trip for trip in trips}
    for loc in locations:
        locs_by_trip[loc.trip_id].append(loc)
        if loc.trip_id not in trips_by_id and loc.trip is not None:
            trips_by_id[loc.trip_id] = loc.trip

    ordered_trips = sorted(
        trips_by_id.values(), key=lambda t: (t.started_at, t.pk)
    )
    summaries: list[_TripSummary] = []
    for trip in ordered_trips:
        t_locs = locs_by_trip.get(trip.pk, [])
        distance_km = 0.0
        speeds: list[float] = []
        accuracies: list[float] = []
        overspeed = 0
        previous: Location | None = None

        for loc in t_locs:
            spd = _as_float(loc.speed_kmh)
            if spd is not None:
                speeds.append(spd)
                if spd >= OVERSPEED_THRESHOLD_KMH:
                    overspeed += 1
            acc = _as_float(loc.accuracy_m)
            if acc is not None:
                accuracies.append(acc)
            if previous is not None:
                distance_km += _haversine_km(
                    float(previous.latitude),
                    float(previous.longitude),
                    float(loc.latitude),
                    float(loc.longitude),
                )
            previous = loc

        started_at = trip.started_at or (t_locs[0].captured_at if t_locs else timezone.now())
        ended_at = trip.ended_at or (t_locs[-1].captured_at if t_locs else None)
        duration_minutes = (
            max(0.0, (ended_at - started_at).total_seconds() / 60.0)
            if ended_at is not None
            else None
        )
        start_coords = (
            (float(t_locs[0].latitude), float(t_locs[0].longitude)) if t_locs else None
        )
        end_coords = (
            (float(t_locs[-1].latitude), float(t_locs[-1].longitude)) if t_locs else None
        )
        summaries.append(
            _TripSummary(
                trip_id=trip.pk,
                vehicle_id=trip.vehicle_id,
                bus_number=trip.vehicle.bus_number,
                route_label=trip.vehicle.route_label or "Route not set",
                driver_name=trip.driver.display_name,
                status=trip.status,
                started_at=started_at,
                ended_at=ended_at,
                duration_minutes=duration_minutes,
                distance_km=distance_km,
                avg_speed_kmh=(sum(speeds) / len(speeds)) if speeds else None,
                peak_speed_kmh=max(speeds) if speeds else None,
                overspeed_count=overspeed,
                avg_accuracy_m=(sum(accuracies) / len(accuracies)) if accuracies else None,
                fix_count=len(t_locs),
                start_coords=start_coords,
                end_coords=end_coords,
            )
        )
    return summaries


def _summarise_vehicles(
    *,
    vehicles: list[Vehicle],
    locations: list[Location],
    trip_summaries: list[_TripSummary],
    active_assignments: dict[int, str],
) -> list[_VehicleSummary]:
    locs_by_vehicle: dict[int, list[Location]] = defaultdict(list)
    for loc in locations:
        locs_by_vehicle[loc.vehicle_id].append(loc)

    trips_by_vehicle: dict[int, list[_TripSummary]] = defaultdict(list)
    for trip in trip_summaries:
        trips_by_vehicle[trip.vehicle_id].append(trip)

    summaries: list[_VehicleSummary] = []
    for vehicle in vehicles:
        v_locs = locs_by_vehicle.get(vehicle.pk, [])
        v_trips = trips_by_vehicle.get(vehicle.pk, [])
        speeds = [_as_float(loc.speed_kmh) for loc in v_locs if loc.speed_kmh is not None]
        speeds_clean = [s for s in speeds if s is not None]
        accs = [_as_float(loc.accuracy_m) for loc in v_locs if loc.accuracy_m is not None]
        accs_clean = [a for a in accs if a is not None]
        overspeed = sum(1 for s in speeds_clean if s >= OVERSPEED_THRESHOLD_KMH)

        driver_name = active_assignments.get(vehicle.pk)
        if not driver_name and v_trips:
            driver_name = v_trips[-1].driver_name
        driver_name = driver_name or "Unassigned"

        summaries.append(
            _VehicleSummary(
                vehicle=vehicle,
                assigned_driver=driver_name,
                trip_count=len(v_trips),
                fix_count=len(v_locs),
                distance_km=sum(t.distance_km for t in v_trips),
                operating_minutes=sum(t.duration_minutes or 0.0 for t in v_trips),
                avg_speed_kmh=(sum(speeds_clean) / len(speeds_clean)) if speeds_clean else None,
                peak_speed_kmh=max(speeds_clean) if speeds_clean else None,
                avg_accuracy_m=(sum(accs_clean) / len(accs_clean)) if accs_clean else None,
                overspeed_count=overspeed,
                speed_sample_count=len(speeds_clean),
                last_captured_at=v_locs[-1].captured_at if v_locs else None,
            )
        )
    return summaries


def _summarise_locations(
    *,
    locations: list[Location],
    vehicle_count: int,
    trip_count: int,
    active_vehicle_count: int | None = None,
) -> _ReportMetrics:
    """Compute fleet-wide summary metrics across all raw GPS fixes."""
    vehicle_records: Counter[str] = Counter()
    vehicle_distances: defaultdict[str, float] = defaultdict(float)
    speed_buckets: Counter[str] = Counter({"Idle <5": 0, "5-24": 0, "25-44": 0, "45+": 0})
    speeds: list[float] = []
    accuracies: list[float] = []
    overspeed_count = 0
    distance_km = 0.0
    previous_by_trip: dict[int, Location] = {}

    for location in locations:
        bus_num = location.vehicle.bus_number
        vehicle_records[bus_num] += 1

        speed = _as_float(location.speed_kmh)
        if speed is not None:
            speeds.append(speed)
            if speed < 5:
                speed_buckets["Idle <5"] += 1
            elif speed < 25:
                speed_buckets["5-24"] += 1
            elif speed < OVERSPEED_THRESHOLD_KMH:
                speed_buckets["25-44"] += 1
            else:
                speed_buckets["45+"] += 1
                overspeed_count += 1

        accuracy = _as_float(location.accuracy_m)
        if accuracy is not None:
            accuracies.append(accuracy)

        previous = previous_by_trip.get(location.trip_id)
        if previous is not None:
            step = _haversine_km(
                float(previous.latitude),
                float(previous.longitude),
                float(location.latitude),
                float(location.longitude),
            )
            distance_km += step
            vehicle_distances[bus_num] += step
        previous_by_trip[location.trip_id] = location

    daily_by_date: Counter[date] = Counter()
    for location in locations:
        daily_by_date[timezone.localtime(location.captured_at).date()] += 1
    latest_days = sorted(daily_by_date.items())[-14:]

    return _ReportMetrics(
        record_count=len(locations),
        vehicle_count=vehicle_count,
        active_vehicle_count=(
            vehicle_count if active_vehicle_count is None else active_vehicle_count
        ),
        trip_count=trip_count,
        average_speed_kmh=(sum(speeds) / len(speeds)) if speeds else None,
        peak_speed_kmh=max(speeds) if speeds else None,
        average_accuracy_m=(sum(accuracies) / len(accuracies)) if accuracies else None,
        estimated_distance_km=distance_km,
        overspeed_count=overspeed_count,
        speed_sample_count=len(speeds),
        first_captured_at=locations[0].captured_at if locations else None,
        last_captured_at=locations[-1].captured_at if locations else None,
        vehicle_records=sorted(vehicle_records.items(), key=lambda item: (-item[1], item[0]))[:10],
        vehicle_distances=sorted(
            vehicle_distances.items(), key=lambda item: (-item[1], item[0])
        )[:10],
        daily_records=[
            (record_date.strftime("%d %b"), count) for record_date, count in latest_days
        ],
        speed_buckets=list(speed_buckets.items()),
    )


def _generate_executive_insights(
    summaries: list[_VehicleSummary], metrics: _ReportMetrics
) -> list[str]:
    if not metrics.record_count:
        return [
            f"{metrics.active_vehicle_count} of {metrics.vehicle_count} selected vehicles are "
            "marked active, with no GPS telemetry recorded in the selected time window.",
            "Confirm driver tracker sessions are active on assigned devices to populate "
            "utilization and speed compliance metrics.",
        ]

    insights: list[str] = []
    reporting_buses = sum(1 for item in summaries if item.fix_count > 0)
    insights.append(
        f"Fleet utilization: {reporting_buses} of {metrics.vehicle_count} selected buses "
        f"reported telemetry across {_format_number(metrics.trip_count)} trips, covering "
        f"an estimated {_format_distance(metrics.estimated_distance_km)}."
    )

    busiest = max(summaries, key=lambda s: (s.distance_km, s.trip_count, s.fix_count), default=None)
    if busiest and busiest.fix_count > 0:
        insights.append(
            f"Highest activity: {busiest.vehicle.bus_number} "
            f"({busiest.vehicle.route_label or 'route unassigned'}) logged "
            f"{_format_number(busiest.trip_count)} trip{'s' if busiest.trip_count != 1 else ''} and "
            f"{_format_distance(busiest.distance_km)}."
        )

    compliance = _fleet_compliance_pct(metrics)
    if compliance is not None:
        if metrics.overspeed_count == 0:
            insights.append(
                f"Speed discipline: 100.0% of speed-bearing fixes remained below the "
                f"{OVERSPEED_THRESHOLD_KMH:.0f} km/h campus threshold "
                f"(peak {_format_speed(metrics.peak_speed_kmh)})."
            )
        else:
            insights.append(
                f"Speed discipline: {compliance:.1f}% compliance overall; "
                f"{_format_number(metrics.overspeed_count)} fixes reached or exceeded "
                f"{OVERSPEED_THRESHOLD_KMH:.0f} km/h (peak {_format_speed(metrics.peak_speed_kmh)})."
            )

    if metrics.average_accuracy_m is not None:
        quality = (
            "strong"
            if metrics.average_accuracy_m <= 15
            else ("moderate" if metrics.average_accuracy_m <= 35 else "weak")
        )
        insights.append(
            f"Telemetry quality: Mean GPS horizontal accuracy is "
            f"{_format_accuracy(metrics.average_accuracy_m)} ({quality} signal precision)."
        )
    return insights


# ---------------------------------------------------------------------------
# Helpers & formatters
# ---------------------------------------------------------------------------


def _fleet_compliance_pct(metrics: _ReportMetrics) -> float | None:
    if not metrics.speed_sample_count:
        return None
    return max(0.0, 100.0 * (1.0 - metrics.overspeed_count / metrics.speed_sample_count))


def _sampling_description(*, raw_count: int, sampled_count: int, interval_seconds: int) -> str:
    if interval_seconds <= 0:
        return (
            f"Forensic raw mode: showing all {_format_number(raw_count)} recorded GPS fixes "
            "(unsampled)"
        )
    mins = interval_seconds // 60
    unit = f"{mins} min" if mins >= 1 and interval_seconds % 60 == 0 else f"{interval_seconds}s"
    return (
        f"Smart checkpoint sampling ({unit} or >=250 m + trip start/end & speed peaks): "
        f"condensed {_format_number(raw_count)} raw GPS fixes into "
        f"{_format_number(sampled_count)} key checkpoints"
    )


def _default_vehicle_scope_label(vehicles: list[Vehicle]) -> str:
    if not vehicles:
        return "No vehicles selected"
    if len(vehicles) == 1:
        return f"Single vehicle ({vehicles[0].bus_number})"
    if len(vehicles) <= 5:
        return ", ".join(v.bus_number for v in vehicles)
    preview = ", ".join(v.bus_number for v in vehicles[:4])
    return f"{preview} +{len(vehicles) - 4} more"


def _format_date_window(*, date_from: date | None, date_to: date | None) -> str:
    if date_from is None and date_to is None:
        return "All recorded dates"
    if date_from is not None and date_to is not None:
        if date_from == date_to:
            return date_from.strftime("%d %b %Y")
        return f"{date_from.strftime('%d %b %Y')} — {date_to.strftime('%d %b %Y')}"
    if date_from is not None:
        return f"From {date_from.strftime('%d %b %Y')}"
    return f"Up to {date_to.strftime('%d %b %Y')}"


def _trip_history_scope(
    *, on_date: date | None, start: datetime | None, end: datetime | None
) -> str:
    if on_date is None:
        return "All recorded dates"
    label = on_date.strftime("%d %b %Y")
    if start is None and end is None:
        return f"Date: {label}"
    start_label = (
        timezone.localtime(start).strftime("%H:%M") if start is not None else "00:00"
    )
    end_label = timezone.localtime(end).strftime("%H:%M") if end is not None else "23:59"
    return f"Date: {label} · {start_label} — {end_label}"


def _start_of_local_day(target: date) -> datetime:
    return timezone.make_aware(
        datetime.combine(target, time.min), timezone.get_current_timezone()
    )


def _end_of_local_day(target: date) -> datetime:
    return timezone.make_aware(
        datetime.combine(target, time.max), timezone.get_current_timezone()
    )


def _haversine_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Return great-circle distance in km between two latitude/longitude fixes."""
    delta_latitude = radians(latitude_2 - latitude_1)
    delta_longitude = radians(longitude_2 - longitude_1)
    a = (
        sin(delta_latitude / 2) ** 2
        + cos(radians(latitude_1)) * cos(radians(latitude_2)) * sin(delta_longitude / 2) ** 2
    )
    return 2 * 6371.0088 * asin(sqrt(min(1.0, a)))


def _nice_maximum_float(value: float) -> float:
    """Round chart ceiling cleanly above the tallest bar with label headroom."""
    if value <= 0:
        return 1.0
    target = value * 1.12
    if target <= 1.0:
        return 1.0
    if target <= 3.0:
        return float(ceil(target))
    if target <= 10.0:
        return float(ceil(target / 2.0) * 2)
    magnitude = 10 ** max(0, len(str(int(ceil(target)))) - 1)
    step = magnitude / 2 if target <= magnitude * 2.5 else magnitude
    return float(ceil(target / step) * step)


def _format_chart_value(value: float, *, decimals: int = 0) -> str:
    if value >= 1000:
        return f"{value / 1000:.1f}k"
    if decimals:
        return f"{value:.{decimals}f}"
    return f"{value:.0f}"


def _recording_interval(metrics: _ReportMetrics) -> str:
    if metrics.first_captured_at is None or metrics.last_captured_at is None:
        return "No records"
    if timezone.localdate(metrics.first_captured_at) == timezone.localdate(
        metrics.last_captured_at
    ):
        return (
            f"{_format_datetime(metrics.first_captured_at)} — "
            f"{_format_time(metrics.last_captured_at)}"
        )
    return (
        f"{_format_datetime(metrics.first_captured_at)} — "
        f"{_format_datetime(metrics.last_captured_at)}"
    )


def _format_datetime(value: datetime) -> str:
    return timezone.localtime(value).strftime("%d %b %Y · %H:%M")


def _format_time(value: datetime) -> str:
    return timezone.localtime(value).strftime("%H:%M")


def _format_duration(minutes: float | None) -> str:
    if minutes is None:
        return "—"
    rounded = int(round(minutes))
    if rounded < 1:
        return "<1m"
    if rounded < 60:
        return f"{rounded}m"
    hours, rem = divmod(rounded, 60)
    return f"{hours}h {rem:02d}m"


def _format_origin_dest(
    start_coords: tuple[float, float] | None,
    end_coords: tuple[float, float] | None,
) -> str:
    if start_coords is None:
        return "—"
    start_str = f"{start_coords[0]:.4f}, {start_coords[1]:.4f}"
    if end_coords is None or end_coords == start_coords:
        return _safe_text(start_str)
    end_str = f"{end_coords[0]:.4f}, {end_coords[1]:.4f}"
    return f"{_safe_text(start_str)}<br/><font color='#64748B'>to {_safe_text(end_str)}</font>"


def _format_number(value: int) -> str:
    return f"{value:,}"


def _format_speed(value: float | None) -> str:
    return f"{value:.1f} km/h" if value is not None else "—"


def _format_speed_pair(
    avg_speed: float | None, peak_speed: float | None, *, prefix: str = "Peak"
) -> str:
    if avg_speed is None and peak_speed is None:
        return "—"
    return (
        f"{_safe_text(_format_speed(avg_speed))}<br/>"
        f"<font color='#64748B'>{prefix} {_safe_text(_format_speed(peak_speed))}</font>"
    )


def _format_accuracy(value: float | None) -> str:
    return f"{value:.0f} m" if value is not None else "—"


def _format_distance(value: float) -> str:
    return f"{value:.2f} km"


def _as_float(value) -> float | None:
    return float(value) if value is not None else None


def _safe_text(value: str) -> str:
    """Escape dynamic values before passing into ReportLab Paragraph."""
    return escape(value).replace("\n", "<br/>")


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    if stringWidth("…", "Helvetica", 6.0):
        return f"{value[: limit - 1]}…"
    return f"{value[: limit - 3]}..."
