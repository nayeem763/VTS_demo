/* Public live map: read-only, no driver identity. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  function setupVehicleFilter() {
    const input = document.getElementById("vts-filter");
    const list = document.getElementById("vehicle-list");
    const empty = document.getElementById("vts-empty");
    if (!input || !list || !empty) return;

    function applyFilter() {
      const query = input.value.trim().toLowerCase();
      let shown = 0;
      let total = 0;
      Array.prototype.forEach.call(list.querySelectorAll(".vehicle-item"), function (item) {
        total += 1;
        const matches = !query || item.textContent.toLowerCase().includes(query);
        item.hidden = !matches;
        if (matches) shown += 1;
      });
      empty.style.display = query && total && !shown ? "block" : "none";
    }

    input.addEventListener("input", applyFilter);
    new MutationObserver(applyFilter).observe(list, { childList: true, subtree: true });
    applyFilter();
  }

  VTS.startLiveMap(mapEl, {
    admin: false,
    listEl: document.getElementById("vehicle-list"),
    statusEl: document.getElementById("map-status"),
    routePlanner: {
      sourceInput: document.getElementById("route-source"),
      destinationInput: document.getElementById("route-destination"),
      drawButton: document.getElementById("draw-route"),
      clearButton: document.getElementById("clear-route"),
      statusEl: document.getElementById("route-status"),
    },
    userLocator: {
      buttons: document.querySelectorAll("[data-locate-me]"),
      cardEl: document.getElementById("my-location-card"),
      statusEl: document.getElementById("my-location-status"),
      coordsEl: document.getElementById("my-location-coords"),
      metaEl: document.getElementById("my-location-meta"),
      nearestEl: document.getElementById("my-location-nearest"),
      copyBtn: document.getElementById("my-location-copy"),
      routeStartBtn: document.getElementById("my-location-route-start"),
      closeBtn: document.getElementById("my-location-close"),
      plannerDetails: document.getElementById("route-planner"),
    },
  });
  setupVehicleFilter();
})();
