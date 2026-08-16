"""Close trips left open past the inactivity threshold.

Run on a schedule (e.g. a free GitHub Actions cron) so trips do not remain
open forever when a phone dies, loses signal, or the driver forgets to log out.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.tracking.services import close_stale_trips


class Command(BaseCommand):
    help = "Close open trips that have received no location within the threshold."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--minutes",
            type=int,
            default=None,
            help="Override the inactivity threshold (defaults to TRIP_INACTIVITY_MINUTES).",
        )

    def handle(self, *args, **options) -> None:
        closed = close_stale_trips(threshold_minutes=options["minutes"])
        self.stdout.write(self.style.SUCCESS(f"Closed {closed} stale trip(s)."))
