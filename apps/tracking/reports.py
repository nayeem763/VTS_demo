"""PDF fleet-record reporting built from immutable tracking history.

The report deliberately reads the append-only :class:`Location` log rather
than maintaining a second reporting table.  That keeps an exported record
faithful to the source data and makes an on-demand admin export immediately
useful without a background job or a migration.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from io import BytesIO
from math import asin, cos, radians, sin, sqrt

from django.db.models import QuerySet
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from apps.fleet.models import Vehicle

from .models import Location, Trip

# A restrained, accessible palette that prints cleanly in colour and greyscale.
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1677C8")
TEAL = colors.HexColor("#0F9D8A")
GOLD = colors.HexColor("#D69E2E")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
LINE = colors.HexColor("#D9E2EC")
SURFACE = colors.HexColor("#F5F8FA")


@dataclass(frozen=True)
class _ReportMetrics:
    """Precomputed values shared by the summary and analytics page."""

    record_count: int
    vehicle_count: int
    trip_count: int
    average_speed_kmh: float | None
    peak_speed_kmh: float | None
    estimated_distance_km: float
    first_captured_at: datetime | None
    last_captured_at: datetime | None
    vehicle_records: list[tuple[str, int]]
    daily_records: list[tuple[str, int]]
    speed_buckets: list[tuple[str, int]]


class _BarChart(Flowable):
    """A compact vector bar chart with a graceful empty-data state.

    Keeping this as a small ReportLab flowable avoids external browser or
    native chart dependencies, so the admin action remains reliable on the
    same deployment environments as Django itself.
    """

    def __init__(self, *, title: str, subtitle: str, data: list[tuple[str, int]], colour) -> None:
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.data = data
        self.colour = colour
        self.width = 170 * mm
        # Three charts and their headings fit on a single A4 analytics page.
        self.height = 50 * mm

    def wrap(self, available_width: float, _available_height: float) -> tuple[float, float]:
        self.width = min(self.width, available_width)
        return self.width, self.height

    def draw(self) -> None:
        canvas = self.canv
        width, height = self.width, self.height

        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.setStrokeColor(LINE)
        canvas.roundRect(0, 0, width, height, 3 * mm, fill=1, stroke=1)

        canvas.setFillColor(INK)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(5 * mm, height - 7 * mm, self.title)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(5 * mm, height - 11.5 * mm, self.subtitle)

        if not self.data or not any(value for _, value in self.data):
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(width / 2, height / 2, "No recorded data is available.")
            canvas.restoreState()
            return

        chart_left = 13 * mm
        chart_bottom = 14 * mm
        chart_width = width - chart_left - 7 * mm
        chart_height = height - chart_bottom - 16 * mm
        max_value = max(value for _, value in self.data)
        rounded_max = max(1, _nice_maximum(max_value))

        # Three unobtrusive reference lines make values readable without
        # cluttering the page with a full charting framework.
        canvas.setStrokeColor(LINE)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 6)
        for tick in range(4):
            value = rounded_max * tick / 3
            y = chart_bottom + chart_height * tick / 3
            canvas.line(chart_left, y, chart_left + chart_width, y)
            canvas.drawRightString(chart_left - 2 * mm, y - 2, _format_chart_value(value))

        count = len(self.data)
        slot_width = chart_width / count
        bar_width = min(12 * mm, max(3 * mm, slot_width * 0.58))
        for index, (label, value) in enumerate(self.data):
            bar_height = chart_height * value / rounded_max
            x = chart_left + index * slot_width + (slot_width - bar_width) / 2
            canvas.setFillColor(self.colour)
            canvas.roundRect(x, chart_bottom, bar_width, bar_height, 1.1 * mm, fill=1, stroke=0)

            canvas.setFillColor(INK)
            canvas.setFont("Helvetica-Bold", 6)
            canvas.drawCentredString(
                x + bar_width / 2,
                chart_bottom + bar_height + 2.5 * mm,
                str(value),
            )

            canvas.saveState()
            canvas.translate(x + bar_width / 2, chart_bottom - 2 * mm)
            canvas.rotate(28)
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 5.8)
            canvas.drawCentredString(0, 0, _truncate(label, 14))
            canvas.restoreState()

        canvas.restoreState()


def build_fleet_record_pdf(
    *,
    vehicles: Iterable[Vehicle] | QuerySet[Vehicle],
    generated_by: str = "",
) -> bytes:
    """Return a polished PDF record for the supplied vehicles.

    The detailed log always comes first.  A forced page break then begins a
    separate analytics page, even when a large log naturally spans many pages.
    The function has no side effects; callers can stream its bytes directly to
    an authenticated administrator.
    """
    selected_vehicles = list(vehicles)
    vehicle_ids = [vehicle.pk for vehicle in selected_vehicles if vehicle.pk is not None]
    locations = list(
        Location.objects.filter(vehicle_id__in=vehicle_ids)
        .select_related("vehicle", "driver__user", "trip")
        .order_by("captured_at", "pk")
    )
    trip_count = Trip.objects.filter(vehicle_id__in=vehicle_ids).count()
    metrics = _summarise_locations(
        locations=locations,
        vehicle_count=len(selected_vehicles),
        trip_count=trip_count,
    )

    output = BytesIO()
    document = _build_document(output)
    styles = _styles()
    story = _build_log_story(
        styles=styles,
        selected_vehicles=selected_vehicles,
        locations=locations,
        metrics=metrics,
        generated_by=generated_by,
    )
    # The analytics section must never share its first page with raw log data.
    story.extend(_build_analytics_story(styles=styles, metrics=metrics))
    document.build(story)
    return output.getvalue()


def fleet_record_filename(*, generated_at: datetime | None = None) -> str:
    """Return an ASCII-only attachment filename safe for every browser."""
    stamp = timezone.localtime(generated_at or timezone.now()).strftime("%Y%m%d-%H%M")
    return f"fleet-record-{stamp}.pdf"


def build_trip_history_pdf(
    *,
    vehicles: Iterable[Vehicle] | QuerySet[Vehicle],
    on_date: date | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    generated_by: str = "",
) -> bytes:
    """Export vehicle-by-vehicle and combined chronological GPS history.

    The first part has one clearly labelled section for every selected vehicle,
    including vehicles with no matching records.  A forced page break then
    starts the all-vehicle timeline, so the combined chronology can be printed
    or shared independently from the per-vehicle sections.
    """
    selected_vehicles = list(vehicles)
    vehicle_ids = [vehicle.pk for vehicle in selected_vehicles if vehicle.pk is not None]
    locations_query = Location.objects.filter(vehicle_id__in=vehicle_ids)
    if on_date is not None:
        day_start = timezone.make_aware(datetime.combine(on_date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(on_date, datetime.max.time()))
        locations_query = locations_query.filter(captured_at__range=(day_start, day_end))
    if start is not None:
        locations_query = locations_query.filter(captured_at__gte=start)
    if end is not None:
        locations_query = locations_query.filter(captured_at__lte=end)

    locations = list(
        locations_query.select_related("vehicle", "driver__user", "trip").order_by(
            "captured_at", "pk"
        )
    )
    locations_by_vehicle: dict[int, list[Location]] = defaultdict(list)
    for location in locations:
        locations_by_vehicle[location.vehicle_id].append(location)

    output = BytesIO()
    document = _build_document(output)
    styles = _styles()
    story = _build_trip_history_story(
        styles=styles,
        selected_vehicles=selected_vehicles,
        locations=locations,
        locations_by_vehicle=locations_by_vehicle,
        on_date=on_date,
        start=start,
        end=end,
        generated_by=generated_by,
    )
    document.build(story)
    return output.getvalue()


def trip_history_filename(*, generated_at: datetime | None = None) -> str:
    """Return an ASCII-only filename for a trip-history PDF export."""
    stamp = timezone.localtime(generated_at or timezone.now()).strftime("%Y%m%d-%H%M")
    return f"trip-history-{stamp}.pdf"


def _build_document(output: BytesIO) -> BaseDocTemplate:
    page_width, page_height = A4
    document = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title="CU VTS Fleet Record",
        author="CU Vehicle Tracking System",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        page_width - document.leftMargin - document.rightMargin,
        page_height - document.topMargin - document.bottomMargin,
        id="record-body",
    )
    document.addPageTemplates(
        PageTemplate(id="fleet-record", frames=[frame], onPage=_draw_page_chrome)
    )
    return document


def _draw_page_chrome(canvas, document) -> None:
    """Draw the shared letterhead and footer outside the content frame."""
    page_width, page_height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 15 * mm, page_width, 15 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(15 * mm, page_height - 8.8 * mm, "CU VTS")
    canvas.setFont("Helvetica", 7.2)
    canvas.drawRightString(
        page_width - 15 * mm,
        page_height - 8.7 * mm,
        "FLEET OPERATIONS  /  CONFIDENTIAL ADMINISTRATIVE RECORD",
    )

    canvas.setStrokeColor(LINE)
    canvas.line(15 * mm, 12 * mm, page_width - 15 * mm, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(15 * mm, 7.5 * mm, "Generated by CU Vehicle Tracking System")
    canvas.drawRightString(page_width - 15 * mm, 7.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "FleetRecordTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            spaceAfter=2 * mm,
        ),
        "kicker": ParagraphStyle(
            "FleetRecordKicker",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=BLUE,
            spaceAfter=1 * mm,
        ),
        "body": ParagraphStyle(
            "FleetRecordBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "muted": ParagraphStyle(
            "FleetRecordMuted",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=10,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "FleetRecordSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=NAVY,
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
        ),
        "table": ParagraphStyle(
            "FleetRecordTable",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=6.5,
            leading=8,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "FleetRecordTableHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.2,
            leading=7,
            textColor=colors.white,
        ),
        "metric": ParagraphStyle(
            "FleetRecordMetric",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=15,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "FleetRecordMetricLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.6,
            leading=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "metric_note": ParagraphStyle(
            "FleetRecordMetricNote",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
    }


def _build_log_story(
    *,
    styles: dict[str, ParagraphStyle],
    selected_vehicles: list[Vehicle],
    locations: list[Location],
    metrics: _ReportMetrics,
    generated_by: str,
) -> list[Flowable]:
    vehicle_labels = ", ".join(vehicle.bus_number for vehicle in selected_vehicles)
    vehicle_labels = vehicle_labels or "No vehicles selected"
    generated_at = _format_datetime(timezone.now())
    scope = f"{metrics.vehicle_count} vehicle{'s' if metrics.vehicle_count != 1 else ''} selected"
    if generated_by:
        scope = f"{scope}  ·  Requested by {generated_by}"

    story: list[Flowable] = [
        Paragraph("FLEET RECORD / ON-DEMAND EXPORT", styles["kicker"]),
        Paragraph("Fleet activity record", styles["title"]),
        Paragraph(
            "<br/>".join(
                _safe_text(value) for value in (scope, vehicle_labels, f"Prepared {generated_at}")
            ),
            styles["muted"],
        ),
        Spacer(1, 4 * mm),
        _summary_cards(metrics, styles),
        Spacer(1, 4 * mm),
        Paragraph("GPS log entries", styles["section"]),
        Paragraph(
            "Chronological, append-only tracking records. Times are shown in the configured local "
            "timezone.",
            styles["muted"],
        ),
        Spacer(1, 2.5 * mm),
    ]

    if locations:
        story.append(_log_table(locations, styles))
    else:
        story.append(_empty_log_state(styles))
    return story


def _build_trip_history_story(
    *,
    styles: dict[str, ParagraphStyle],
    selected_vehicles: list[Vehicle],
    locations: list[Location],
    locations_by_vehicle: dict[int, list[Location]],
    on_date: date | None,
    start: datetime | None,
    end: datetime | None,
    generated_by: str,
) -> list[Flowable]:
    """Build the two-part trip-history export in the requested order."""
    scope = _trip_history_scope(on_date=on_date, start=start, end=end)
    requested_by = f"  ·  Requested by {generated_by}" if generated_by else ""
    story: list[Flowable] = [
        Paragraph("TRIP HISTORY / ON-DEMAND EXPORT", styles["kicker"]),
        Paragraph("Vehicle trip history", styles["title"]),
        Paragraph(
            _safe_text(
                f"{scope}  ·  {len(selected_vehicles)} vehicle"
                f"{'s' if len(selected_vehicles) != 1 else ''}  ·  Prepared "
                f"{_format_datetime(timezone.now())}{requested_by}"
            ),
            styles["muted"],
        ),
        Spacer(1, 4 * mm),
    ]

    if not selected_vehicles:
        story.append(_empty_history_state(styles, "No vehicles are available for this export."))
    for index, vehicle in enumerate(selected_vehicles, start=1):
        vehicle_locations = locations_by_vehicle.get(vehicle.pk, [])
        vehicle_trip_ids = {location.trip_id for location in vehicle_locations}
        route_label = vehicle.route_label or "No route label"
        vehicle_state = "Active" if vehicle.is_active else "Inactive"
        vehicle_description = (
            f"Section {index}  ·  {_format_number(len(vehicle_locations))} GPS record"
            f"{'s' if len(vehicle_locations) != 1 else ''}  ·  "
            f"{_format_number(len(vehicle_trip_ids))} trip"
            f"{'s' if len(vehicle_trip_ids) != 1 else ''}"
        )
        if vehicle.registration_number:
            vehicle_description += f"  ·  Registration {vehicle.registration_number}"

        story.extend(
            [
                Paragraph(f"Vehicle {index} · {_safe_text(vehicle.bus_number)}", styles["section"]),
                Paragraph(
                    f"{_safe_text(route_label)}  ·  {_safe_text(vehicle_state)}<br/>"
                    f"{_safe_text(vehicle_description)}",
                    styles["muted"],
                ),
                Spacer(1, 2.5 * mm),
            ]
        )
        if vehicle_locations:
            story.append(_log_table(vehicle_locations, styles))
        else:
            story.append(
                _empty_history_state(
                    styles, "No GPS records match the selected date and time range."
                )
            )
        if index != len(selected_vehicles):
            story.append(Spacer(1, 5 * mm))

    # This page boundary is intentional: the combined timeline must never
    # begin beneath a vehicle-specific section.
    story.extend(
        [
            PageBreak(),
            Paragraph("COMBINED HISTORY / CHRONOLOGICAL TIMELINE", styles["kicker"]),
            Paragraph("All vehicle activity in time order", styles["title"]),
            Paragraph(
                _safe_text(
                    f"{scope}  ·  {_format_number(len(locations))} GPS record"
                    f"{'s' if len(locations) != 1 else ''} across "
                    f"{len(selected_vehicles)} vehicle{'s' if len(selected_vehicles) != 1 else ''}."
                ),
                styles["muted"],
            ),
            Spacer(1, 4 * mm),
        ]
    )
    if locations:
        story.append(_log_table(locations, styles))
    else:
        story.append(
            _empty_history_state(styles, "No GPS records match the selected date and time range.")
        )
    return story


def _trip_history_scope(
    *, on_date: date | None, start: datetime | None, end: datetime | None
) -> str:
    """Describe the filters used to create a trip-history export."""
    if on_date is None:
        return "All recorded dates"

    label = on_date.strftime("%d %b %Y")
    if start is None and end is None:
        return f"Date: {label}"
    start_label = (
        timezone.localtime(start).strftime("%H:%M") if start is not None else "start of day"
    )
    end_label = timezone.localtime(end).strftime("%H:%M") if end is not None else "end of day"
    return f"Date: {label}  ·  Time: {start_label} — {end_label}"


def _empty_history_state(styles: dict[str, ParagraphStyle], message: str) -> Table:
    table = Table([[Paragraph(_safe_text(message), styles["body"])]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
            ]
        )
    )
    return table


def _summary_cards(metrics: _ReportMetrics, styles: dict[str, ParagraphStyle]) -> Table:
    cards = [
        ("GPS RECORDS", _format_number(metrics.record_count)),
        ("TRIPS", _format_number(metrics.trip_count)),
        ("AVG. SPEED", _format_speed(metrics.average_speed_kmh)),
        ("EST. DISTANCE", _format_distance(metrics.estimated_distance_km)),
    ]
    data = [
        [Paragraph(value, styles["metric"]) for _, value in cards],
        [Paragraph(label, styles["metric_label"]) for label, _ in cards],
    ]
    table = Table(data, colWidths=[42.5 * mm] * 4, rowHeights=[9 * mm, 5.5 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
            ]
        )
    )
    return table


def _log_table(locations: list[Location], styles: dict[str, ParagraphStyle]) -> Table:
    headers = (
        "#",
        "Captured",
        "Vehicle / route",
        "Driver",
        "Trip",
        "Speed",
        "Accuracy",
        "Coordinates",
    )
    rows: list[list[Paragraph]] = [
        [Paragraph(header, styles["table_header"]) for header in headers]
    ]
    for location in locations:
        route = location.vehicle.route_label or "Route not set"
        rows.append(
            [
                Paragraph(str(location.pk), styles["table"]),
                Paragraph(_safe_text(_format_datetime(location.captured_at)), styles["table"]),
                Paragraph(
                    f"{_safe_text(location.vehicle.bus_number)}<br/>"
                    f"<font color='#627D98'>{_safe_text(route)}</font>",
                    styles["table"],
                ),
                Paragraph(_safe_text(location.driver.display_name), styles["table"]),
                Paragraph(str(location.trip_id), styles["table"]),
                Paragraph(
                    _safe_text(_format_speed(_as_float(location.speed_kmh))),
                    styles["table"],
                ),
                Paragraph(
                    _safe_text(_format_accuracy(_as_float(location.accuracy_m))),
                    styles["table"],
                ),
                Paragraph(
                    _safe_text(f"{float(location.latitude):.6f}, {float(location.longitude):.6f}"),
                    styles["table"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[8 * mm, 24 * mm, 28 * mm, 24 * mm, 11 * mm, 15 * mm, 16 * mm, 44 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SURFACE]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3 * mm),
                ("LEFTPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ]
        )
    )
    return table


def _empty_log_state(styles: dict[str, ParagraphStyle]) -> Table:
    message = Paragraph(
        "No GPS log entries match this fleet selection. The analytics page is retained so the "
        "empty report is still a complete, auditable export.",
        styles["body"],
    )
    table = Table([[message]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
            ]
        )
    )
    return table


def _build_analytics_story(
    *, styles: dict[str, ParagraphStyle], metrics: _ReportMetrics
) -> list[Flowable]:
    interval = _recording_interval(metrics)
    story: list[Flowable] = [
        PageBreak(),
        Paragraph("ANALYTICS / RECORD VISUALIZATION", styles["kicker"]),
        Paragraph("Fleet activity at a glance", styles["title"]),
        Paragraph(
            _safe_text(
                f"Record interval: {interval}  ·  {metrics.record_count:,} records across "
                f"{metrics.vehicle_count} vehicle{'s' if metrics.vehicle_count != 1 else ''}."
            ),
            styles["muted"],
        ),
        Spacer(1, 4 * mm),
        _analytics_note(metrics, styles),
        Spacer(1, 4 * mm),
        _BarChart(
            title="Daily GPS record volume",
            subtitle="Most recent fourteen recording days",
            data=metrics.daily_records,
            colour=BLUE,
        ),
        Spacer(1, 4 * mm),
        _BarChart(
            title="Vehicle activity",
            subtitle="GPS records by vehicle (up to ten most active)",
            data=metrics.vehicle_records,
            colour=TEAL,
        ),
        Spacer(1, 4 * mm),
        _BarChart(
            title="Speed distribution",
            subtitle="Records grouped by reported speed; omitted when speed was not submitted",
            data=metrics.speed_buckets,
            colour=GOLD,
        ),
        Spacer(1, 2 * mm),
        Paragraph(
            "Distance is an approximate trace length calculated from consecutive GPS fixes within "
            "each trip; it is not an odometer reading.",
            styles["metric_note"],
        ),
    ]
    return story


def _analytics_note(metrics: _ReportMetrics, styles: dict[str, ParagraphStyle]) -> Table:
    values = [
        ("PEAK SPEED", _format_speed(metrics.peak_speed_kmh)),
        ("AVG. SPEED", _format_speed(metrics.average_speed_kmh)),
        ("EST. DISTANCE", _format_distance(metrics.estimated_distance_km)),
    ]
    table = Table(
        [
            [Paragraph(value, styles["metric"]) for _, value in values],
            [Paragraph(label, styles["metric_label"]) for label, _ in values],
        ],
        colWidths=[170 * mm / 3] * 3,
        rowHeights=[9 * mm, 5.5 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
            ]
        )
    )
    return table


def _summarise_locations(
    *, locations: list[Location], vehicle_count: int, trip_count: int
) -> _ReportMetrics:
    vehicle_records: Counter[str] = Counter()
    speed_buckets: Counter[str] = Counter({"Idle <5": 0, "5-24": 0, "25-44": 0, "45+": 0})
    speeds: list[float] = []
    distance_km = 0.0
    previous_by_trip: dict[int, Location] = {}

    for location in locations:
        vehicle_records[location.vehicle.bus_number] += 1

        speed = _as_float(location.speed_kmh)
        if speed is not None:
            speeds.append(speed)
            if speed < 5:
                speed_buckets["Idle <5"] += 1
            elif speed < 25:
                speed_buckets["5-24"] += 1
            elif speed < 45:
                speed_buckets["25-44"] += 1
            else:
                speed_buckets["45+"] += 1

        previous = previous_by_trip.get(location.trip_id)
        if previous is not None:
            distance_km += _haversine_km(
                float(previous.latitude),
                float(previous.longitude),
                float(location.latitude),
                float(location.longitude),
            )
        previous_by_trip[location.trip_id] = location

    # Dict order is not enough for a report crossing months/years: rebuild a
    # date-aware sequence from the chronological log, then expose presentation
    # labels only after the last fourteen dates have been chosen.
    daily_by_date: Counter[date] = Counter()
    for location in locations:
        daily_by_date[timezone.localtime(location.captured_at).date()] += 1
    latest_days = sorted(daily_by_date.items())[-14:]

    return _ReportMetrics(
        record_count=len(locations),
        vehicle_count=vehicle_count,
        trip_count=trip_count,
        average_speed_kmh=(sum(speeds) / len(speeds)) if speeds else None,
        peak_speed_kmh=max(speeds) if speeds else None,
        estimated_distance_km=distance_km,
        first_captured_at=locations[0].captured_at if locations else None,
        last_captured_at=locations[-1].captured_at if locations else None,
        vehicle_records=sorted(vehicle_records.items(), key=lambda item: (-item[1], item[0]))[:10],
        daily_records=[
            (record_date.strftime("%d %b"), count) for record_date, count in latest_days
        ],
        speed_buckets=list(speed_buckets.items()),
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
    return 2 * 6371.0088 * asin(sqrt(a))


def _nice_maximum(value: int) -> int:
    """Round a positive chart maximum upward to a readable tick value."""
    if value <= 5:
        return 5
    magnitude = 10 ** max(0, len(str(value)) - 1)
    return int(((value + magnitude - 1) // magnitude) * magnitude)


def _format_chart_value(value: float) -> str:
    return f"{value:.0f}" if value < 1000 else f"{value / 1000:.1f}k"


def _recording_interval(metrics: _ReportMetrics) -> str:
    if metrics.first_captured_at is None or metrics.last_captured_at is None:
        return "No records"
    if metrics.first_captured_at.date() == metrics.last_captured_at.date():
        return _format_datetime(metrics.first_captured_at)
    first = _format_datetime(metrics.first_captured_at)
    last = _format_datetime(metrics.last_captured_at)
    return f"{first} — {last}"


def _format_datetime(value: datetime) -> str:
    return timezone.localtime(value).strftime("%d %b %Y · %H:%M")


def _format_number(value: int) -> str:
    return f"{value:,}"


def _format_speed(value: float | None) -> str:
    return f"{value:.1f} km/h" if value is not None else "—"


def _format_accuracy(value: float | None) -> str:
    return f"{value:.0f} m" if value is not None else "—"


def _format_distance(value: float) -> str:
    return f"{value:.2f} km"


def _as_float(value) -> float | None:
    return float(value) if value is not None else None


def _safe_text(value: str) -> str:
    """Escape dynamic values before they are passed into ReportLab Paragraph."""
    return escape(value).replace("\n", "<br/>")


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    ellipsis_width = stringWidth("…", "Helvetica", 5.8)
    if ellipsis_width:  # Kept explicit: makes the intent clear for PDF fonts.
        return f"{value[: limit - 1]}…"
    return f"{value[: limit - 3]}..."
