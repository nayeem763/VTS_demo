/* Public live map: read-only, no driver identity. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;
  VTS.startLiveMap(mapEl, {
    admin: false,
    listEl: document.getElementById("vehicle-list"),
    statusEl: document.getElementById("map-status"),
  });
})();
