/* Admin trip history: pick a vehicle + date, list that day's trips, then
   replay the selected trip with a scrubber/playback cursor. */
"use strict";
(function () {
  const mapEl = document.getElementById("history-map");
  if (!mapEl) return;

  const ICON_USER = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 19.5a7 7 0 0 1 14 0"/></svg>';
  const ICON_PLAY = '<svg class="vts-btn-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="7 5 19 12 7 19 7 5" fill="currentColor" stroke="none"/></svg>';
  const ICON_PAUSE = '<svg class="vts-btn-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1" fill="currentColor" stroke="none"/><rect x="14" y="5" width="4" height="14" rx="1" fill="currentColor" stroke="none"/></svg>';

  const tripsUrl = mapEl.dataset.tripsUrl; // /api/v1/trips/
  const tripHistoryPdfUrl = mapEl.dataset.tripHistoryPdfUrl;
  const center = [parseFloat(mapEl.dataset.centerLat), parseFloat(mapEl.dataset.centerLng)];
  const zoom = parseInt(mapEl.dataset.zoom || "13", 10);

  const vehicleSelect = document.getElementById("vehicle-select");
  const dateInput = document.getElementById("date-input");
  const startTime = document.getElementById("start-time");
  const endTime = document.getElementById("end-time");
  const loadBtn = document.getElementById("load-trips");
  const exportPdfBtn = document.getElementById("export-trip-history");
  const tripListEl = document.getElementById("trip-list");
  const playRange = document.getElementById("playback-range");
  const playBtn = document.getElementById("play-btn");
  const playInfo = document.getElementById("play-info");
  const errorEl = document.getElementById("history-error");

  const map = L.map(mapEl, { center: center, zoom: zoom });
  VTS.tileLayer().addTo(map);

  let layers = [];
  let cursor = null;
  let points = [];
  let playTimer = null;
  let activeTripId = null;

  function setError(msg) {
    if (!errorEl) return;
    errorEl.textContent = msg || "";
    errorEl.classList.toggle("d-none", !msg);
  }

  function clearMap() {
    stopPlayback();
    layers.forEach(function (l) { map.removeLayer(l); });
    layers = [];
    cursor = null;
    points = [];
    if (playRange) { playRange.value = 0; playRange.max = 0; playRange.disabled = true; }
    if (playBtn) playBtn.disabled = true;
    if (playInfo) playInfo.textContent = "";
  }

  async function loadTrips() {
    setError("");
    clearMap();
    if (tripListEl) tripListEl.innerHTML = "";
    activeTripId = null;
    const vid = vehicleSelect ? vehicleSelect.value : "";
    if (!vid) { setError("Choose a vehicle first."); return; }
    const params = new URLSearchParams({ vehicle_id: vid });
    if (dateInput && dateInput.value) params.set("date", dateInput.value);
    let data;
    try {
      data = await VTS.getJSON(tripsUrl + "?" + params.toString());
    } catch (e) {
      setError(e.message);
      return;
    }
    renderTripList((data && data.results) || []);
  }

  function renderTripList(trips) {
    if (!tripListEl) return;
    if (!trips.length) {
      tripListEl.innerHTML = '<div class="vts-list-placeholder">No trips found for that day.</div>';
      return;
    }
    const html = trips
      .map(function (t) {
        const span = VTS.fmtTime(t.started_at) + " – " + (t.ended_at ? VTS.fmtTime(t.ended_at) : "ongoing");
        const isOpen = String(t.status || "").toUpperCase() === "OPEN";
        const badge = isOpen
          ? '<span class="status-badge is-live">Open</span>'
          : '<span class="status-badge is-offline">Done</span>';
        return (
          '<button type="button" class="list-group-item list-group-item-action vts-trip-item" data-id="' + t.id + '">' +
            '<div class="d-flex justify-content-between align-items-center gap-2">' +
              '<span class="vts-trip-title">Trip #' + t.id + "</span>" + badge +
            "</div>" +
            '<div class="vts-trip-span">' + VTS.escapeHtml(span) + "</div>" +
            (t.driver_name ? '<div class="vts-meta-inline">' + ICON_USER + "<span>" + VTS.escapeHtml(t.driver_name) + "</span></div>" : "") +
          "</button>"
        );
      })
      .join("");
    tripListEl.innerHTML = '<div class="list-group list-group-flush">' + html + "</div>";
    tripListEl.querySelectorAll("button[data-id]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        tripListEl.querySelectorAll("button[data-id]").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        loadPoints(parseInt(btn.dataset.id, 10));
      });
    });
  }

  async function loadPoints(tripId) {
    setError("");
    activeTripId = tripId;
    const params = new URLSearchParams();
    if (startTime && startTime.value) params.set("start", startTime.value);
    if (endTime && endTime.value) params.set("end", endTime.value);
    const qs = params.toString();
    const url = tripsUrl + tripId + "/points/" + (qs ? "?" + qs : "");
    let data;
    try {
      data = await VTS.getJSON(url);
    } catch (e) {
      setError(e.message);
      return;
    }
    drawTrip((data && data.points) || []);
  }

  function drawTrip(rawPoints) {
    clearMap();
    points = rawPoints.map(function (p) {
      return {
        latlng: [parseFloat(p.latitude), parseFloat(p.longitude)],
        time: p.captured_at,
        speed: p.speed_kmh,
      };
    });
    if (!points.length) {
      setError("This trip has no points in the selected range.");
      return;
    }
    const latlngs = points.map(function (p) { return p.latlng; });
    const startDot = L.circleMarker(latlngs[0], { radius: 7, color: "#ffffff", fillColor: "#1E8E3E", fillOpacity: 1, weight: 2.5 }).addTo(map).bindTooltip("Start");
    const endDot = L.circleMarker(latlngs[latlngs.length - 1], { radius: 7, color: "#ffffff", fillColor: "#EA4335", fillOpacity: 1, weight: 2.5 }).addTo(map).bindTooltip("End");
    cursor = L.marker(latlngs[0], { icon: VTS.markerIcon("live") }).addTo(map);
    layers.push(startDot, endDot, cursor);
    map.fitBounds(L.latLngBounds(latlngs), { padding: [40, 40] });

    if (playRange) {
      playRange.max = String(points.length - 1);
      playRange.value = "0";
      playRange.disabled = points.length < 2;
    }
    if (playBtn) playBtn.disabled = points.length < 2;
    setCursor(0);
  }

  function setCursor(i) {
    if (!points.length) return;
    const idx = Math.max(0, Math.min(i, points.length - 1));
    const p = points[idx];
    if (cursor) cursor.setLatLng(p.latlng);
    if (playRange) playRange.value = String(idx);
    if (playInfo) {
      const speed = VTS.fmtSpeed(p.speed);
      playInfo.textContent =
        "Point " + (idx + 1) + " / " + points.length + " · " + VTS.fmtTime(p.time) + (speed ? " · " + speed : "");
    }
  }

  function stopPlayback() {
    if (playTimer != null) { clearInterval(playTimer); playTimer = null; }
    if (playBtn) playBtn.innerHTML = ICON_PLAY + "<span>Play</span>";
  }

  function syncTripReportModal() {
    const modalEl = document.getElementById("trip-report-modal");
    const formEl = document.getElementById("trip-report-form");
    if (!modalEl || !formEl) return;

    const modalVehicle = document.getElementById("trip-report-vehicle");
    const modalDate = document.getElementById("trip-report-date");
    const modalStart = document.getElementById("trip-report-start");
    const modalEnd = document.getElementById("trip-report-end");
    const intervalWrap = document.getElementById("trip-report-interval-wrap");
    const specBox = document.getElementById("trip-report-spec");
    const typeRadios = Array.from(formEl.querySelectorAll('input[name="report_type"]'));

    function updateTypeMeta() {
      const active = typeRadios.find(function (r) { return r.checked; }) || typeRadios[0];
      if (active && specBox) {
        ["purpose", "audience", "outputs"].forEach(function (field) {
          const target = specBox.querySelector('[data-spec-field="' + field + '"]');
          if (target) target.textContent = active.dataset[field] || "";
        });
      }
      if (intervalWrap) {
        intervalWrap.classList.toggle("d-none", !(active && active.value === "telemetry_audit"));
      }
    }

    modalEl.addEventListener("show.bs.modal", function () {
      if (modalVehicle && vehicleSelect) modalVehicle.value = vehicleSelect.value || "";
      if (modalDate && dateInput) modalDate.value = dateInput.value || "";
      if (modalStart && startTime) modalStart.value = startTime.value || "";
      if (modalEnd && endTime) modalEnd.value = endTime.value || "";
      updateTypeMeta();
    });

    typeRadios.forEach(function (radio) { radio.addEventListener("change", updateTypeMeta); });
    updateTypeMeta();
  }

  function togglePlayback() {
    if (playTimer != null) { stopPlayback(); return; }
    if (!points.length) return;
    let i = playRange ? parseInt(playRange.value, 10) : 0;
    if (i >= points.length - 1) i = 0; // restart from beginning
    if (playBtn) playBtn.innerHTML = ICON_PAUSE + "<span>Pause</span>";
    playTimer = setInterval(function () {
      if (i >= points.length - 1) { setCursor(points.length - 1); stopPlayback(); return; }
      i += 1;
      setCursor(i);
    }, 400);
  }

  if (loadBtn) loadBtn.addEventListener("click", loadTrips);
  if (playRange) playRange.addEventListener("input", function () { stopPlayback(); setCursor(parseInt(playRange.value, 10)); });
  if (playBtn) playBtn.addEventListener("click", togglePlayback);

  syncTripReportModal();
  clearMap();
})();
