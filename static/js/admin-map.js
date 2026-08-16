/* Admin live dashboard: same map engine, richer fields, plus a focus selector.
   The admin API returns driver name + accuracy, which the shared engine shows
   when admin:true. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;
  VTS.startLiveMap(mapEl, {
    admin: true,
    listEl: document.getElementById("vehicle-list"),
    focusSelect: document.getElementById("focus-select"),
    statusEl: document.getElementById("map-status"),
  });
})();
