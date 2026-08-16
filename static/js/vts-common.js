/* Shared CU-VTS front-end helpers. Loaded before every page script.
   Exposes a single global: window.VTS. No inline scripts anywhere, so the
   strict Content-Security-Policy (script-src 'self') stays intact. */
"use strict";

window.VTS = (function () {
  // ---- CSRF (Django) ------------------------------------------------------
  function getCookie(name) {
    const match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return match ? decodeURIComponent(match.pop()) : null;
  }

  // ---- Fetch --------------------------------------------------------------
  async function getJSON(url, options) {
    const opts = Object.assign(
      { headers: { Accept: "application/json" }, credentials: "same-origin" },
      options || {}
    );
    const res = await fetch(url, opts);
    if (!res.ok) {
      let detail = "Request failed (" + res.status + ")";
      try {
        const body = await res.json();
        if (body && body.detail) {
          detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
        }
      } catch (e) {
        /* non-JSON error body */
      }
      const err = new Error(detail);
      err.status = res.status;
      throw err;
    }
    return res.status === 204 ? null : res.json();
  }

  async function postJSON(url, payload) {
    return getJSON(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken") || "",
      },
      body: JSON.stringify(payload),
    });
  }

  // ---- Formatting ---------------------------------------------------------
  function escapeHtml(value) {
    if (value == null) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function fmtAge(seconds) {
    if (seconds == null) return "no signal";
    if (seconds < 60) return seconds + "s ago";
    const m = Math.floor(seconds / 60);
    if (m < 60) return m + "m ago";
    const h = Math.floor(m / 60);
    return h + "h ago";
  }

  function fmtTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return isNaN(d) ? "—" : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function fmtSpeed(speedKmh) {
    if (speedKmh == null) return null;
    const n = parseFloat(speedKmh);
    return isNaN(n) ? null : Math.round(n) + " km/h";
  }

  // ---- Leaflet helpers ----------------------------------------------------
  function tileLayer() {
    return L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    });
  }

  function statusOf(vehicle) {
    if (!vehicle.has_signal) return "offline";
    return vehicle.is_stale ? "stale" : "live";
  }

  function markerIcon(status) {
    return L.divIcon({
      className: "vts-marker-wrap",
      html: '<div class="vts-marker is-' + status + '"></div>',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
      popupAnchor: [0, -10],
    });
  }

  // ---- Live map engine (shared by public + admin dashboards) --------------
  // Renders one marker per vehicle and an optional sidebar list. The admin
  // flag simply reveals the extra fields the admin API already returns.
  function startLiveMap(mapEl, config) {
    const settings = config || {};
    const admin = !!settings.admin;
    const listEl = settings.listEl || null;
    const focusSelect = settings.focusSelect || null;
    const statusEl = settings.statusEl || null;

    const endpoint = mapEl.dataset.endpoint;
    const poll = parseInt(mapEl.dataset.poll || "8000", 10);
    const center = [parseFloat(mapEl.dataset.centerLat), parseFloat(mapEl.dataset.centerLng)];
    const zoom = parseInt(mapEl.dataset.zoom || "13", 10);

    const map = L.map(mapEl, { center: center, zoom: zoom, zoomControl: true });
    tileLayer().addTo(map);

    const markers = new Map(); // vehicle_id -> { marker, latlng }
    let didFit = false;

    function popupHtml(v, status) {
      const rows = [];
      rows.push("<strong>" + escapeHtml(v.bus_number) + "</strong>");
      if (v.route_label) rows.push('<div class="text-muted small">' + escapeHtml(v.route_label) + "</div>");
      rows.push('<div class="small mt-1">Status: <span class="status-badge is-' + status + '">' + status.toUpperCase() + "</span></div>");
      const speed = fmtSpeed(v.speed_kmh);
      if (speed) rows.push('<div class="small">Speed: ' + speed + "</div>");
      rows.push('<div class="small">Updated: ' + escapeHtml(fmtAge(v.age_seconds)) + "</div>");
      if (admin && v.driver_name) rows.push('<div class="small">Driver: ' + escapeHtml(v.driver_name) + "</div>");
      if (admin && v.accuracy_m) rows.push('<div class="small text-muted">± ' + escapeHtml(v.accuracy_m) + " m</div>");
      return rows.join("");
    }

    function upsertMarker(v, status) {
      const latlng = [parseFloat(v.latitude), parseFloat(v.longitude)];
      let entry = markers.get(v.vehicle_id);
      if (!entry) {
        const marker = L.marker(latlng, { icon: markerIcon(status), title: v.bus_number });
        marker.addTo(map);
        marker.bindTooltip(v.bus_number, { permanent: true, direction: "top", className: "vts-label", offset: [0, -10] });
        entry = { marker: marker, latlng: latlng };
        markers.set(v.vehicle_id, entry);
      } else {
        entry.marker.setLatLng(latlng);
        entry.marker.setIcon(markerIcon(status));
        entry.latlng = latlng;
      }
      entry.marker.bindPopup(popupHtml(v, status));
      return latlng;
    }

    function removeMarker(vehicleId) {
      const entry = markers.get(vehicleId);
      if (entry) {
        map.removeLayer(entry.marker);
        markers.delete(vehicleId);
      }
    }

    function focus(vehicleId) {
      const entry = markers.get(vehicleId);
      if (entry) {
        map.setView(entry.latlng, Math.max(map.getZoom(), 16));
        entry.marker.openPopup();
      }
    }

    function renderList(vehicles) {
      if (!listEl) return;
      if (!vehicles.length) {
        listEl.innerHTML = '<div class="p-4 text-center text-muted small">No active vehicles.</div>';
        return;
      }
      const html = vehicles
        .map(function (v) {
          const status = statusOf(v);
          const speed = fmtSpeed(v.speed_kmh);
          const driver = admin && v.driver_name ? '<div class="small text-muted">👤 ' + escapeHtml(v.driver_name) + "</div>" : "";
          return (
            '<button type="button" class="list-group-item list-group-item-action vehicle-item" data-id="' + v.vehicle_id + '">' +
            '<div class="d-flex justify-content-between align-items-start">' +
            "<div><div class=\"fw-semibold\">" + escapeHtml(v.bus_number) + "</div>" +
            '<div class="small text-muted">' + escapeHtml(v.route_label || "—") + "</div>" + driver + "</div>" +
            '<div class="text-end">' +
            '<span class="status-badge is-' + status + '">' + status + "</span>" +
            '<div class="small text-muted">' + escapeHtml(fmtAge(v.age_seconds)) + "</div>" +
            (speed ? '<div class="small">' + speed + "</div>" : "") +
            "</div></div></button>"
          );
        })
        .join("");
      listEl.innerHTML = '<div class="list-group list-group-flush">' + html + "</div>";
      listEl.querySelectorAll(".vehicle-item").forEach(function (btn) {
        btn.addEventListener("click", function () {
          focus(parseInt(btn.dataset.id, 10));
        });
      });
    }

    function populateSelect(vehicles) {
      if (!focusSelect) return;
      const current = focusSelect.value;
      const opts = ['<option value="">Focus a vehicle…</option>'].concat(
        vehicles.map(function (v) {
          return '<option value="' + v.vehicle_id + '">' + escapeHtml(v.bus_number) + "</option>";
        })
      );
      focusSelect.innerHTML = opts.join("");
      if (current) focusSelect.value = current;
    }

    function setStatus(text, isError) {
      if (!statusEl) return;
      statusEl.textContent = text;
      statusEl.classList.toggle("text-danger", !!isError);
    }

    async function refresh() {
      let data;
      try {
        data = await getJSON(endpoint);
      } catch (e) {
        setStatus("Connection problem — retrying…", true);
        return;
      }
      const vehicles = (data && data.results) || [];
      const seen = new Set();
      const bounds = [];
      vehicles.forEach(function (v) {
        seen.add(v.vehicle_id);
        const status = statusOf(v);
        if (v.has_signal) {
          const latlng = upsertMarker(v, status);
          bounds.push(latlng);
        } else {
          removeMarker(v.vehicle_id);
        }
      });
      // Drop markers for vehicles that disappeared from the feed.
      Array.from(markers.keys()).forEach(function (id) {
        if (!seen.has(id)) removeMarker(id);
      });
      renderList(vehicles);
      populateSelect(vehicles);
      const live = vehicles.filter(function (v) { return v.has_signal && !v.is_stale; }).length;
      setStatus(live + " live · " + vehicles.length + " active · updated " + fmtTime(new Date().toISOString()));
      if (!didFit && bounds.length) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
        didFit = true;
      }
    }

    if (focusSelect) {
      focusSelect.addEventListener("change", function () {
        if (focusSelect.value) focus(parseInt(focusSelect.value, 10));
      });
    }

    refresh();
    const timer = setInterval(refresh, poll);
    // Pause polling when the tab is hidden to save the free-tier request budget.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") refresh();
    });

    return { map: map, refresh: refresh, focus: focus, stop: function () { clearInterval(timer); } };
  }

  return {
    getCookie: getCookie,
    getJSON: getJSON,
    postJSON: postJSON,
    escapeHtml: escapeHtml,
    fmtAge: fmtAge,
    fmtTime: fmtTime,
    fmtSpeed: fmtSpeed,
    tileLayer: tileLayer,
    statusOf: statusOf,
    markerIcon: markerIcon,
    startLiveMap: startLiveMap,
  };
})();
