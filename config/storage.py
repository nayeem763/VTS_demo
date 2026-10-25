"""Static-files storage that ignores source-map comments.

The vendored Bootstrap/Leaflet bundles end with ``sourceMappingURL=...map``
comments, but the ``.map`` files are not shipped in ``static/vendor``. Django's
manifest storage tries to resolve those references during ``collectstatic`` and
aborts with "could not be found". Dropping only the source-map patterns avoids
that without touching the vendored files.
"""

from __future__ import annotations

from whitenoise.storage import CompressedManifestStaticFilesStorage


def _without_sourcemaps(patterns):
    cleaned = []
    for extension, rules in patterns:
        kept = tuple(
            rule
            for rule in rules
            if not (isinstance(rule, tuple) and "sourceMappingURL" in rule[0])
        )
        cleaned.append((extension, kept))
    return tuple(cleaned)


class NoSourceMapManifestStorage(CompressedManifestStaticFilesStorage):
    patterns = _without_sourcemaps(CompressedManifestStaticFilesStorage.patterns)