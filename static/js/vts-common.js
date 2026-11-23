/* Shared CU-VTS front-end helpers. Loaded before every page script.
   Exposes a single global: window.VTS. No inline scripts anywhere, so the
   strict Content-Security-Policy (script-src 'self') stays intact. */
"use strict";

window.VTS = (function () {
  const ICON_USER = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 19.5a7 7 0 0 1 14 0"/></svg>';
  const ICON_EYE = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12Z"/><circle cx="12" cy="12" r="2.75"/></svg>';
  const ICON_EYE_OFF = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3l18 18"/><path d="M10.6 5.7A10.7 10.7 0 0 1 12 5.5c6.5 0 10 6.5 10 6.5a17.6 17.6 0 0 1-3.3 4.3"/><path d="M6.4 7.7A17.7 17.7 0 0 0 2 12s3.5 6.5 10 6.5a9.9 9.9 0 0 0 4.4-1"/></svg>';
  const ICON_TRASH = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 7h16M10 11v6M14 11v6"/><path d="M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/></svg>';
  const ICON_CLOSE = '<svg class="vts-inline-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';
  const ICON_BUS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3.5" width="16" height="13.5" rx="3"/><path d="M4 11h16M7.5 17v2.5M16.5 17v2.5"/></svg>';
  const CAMPUS_LANDMARKS = [
    { name: "Chittagong University", lat: 22.4716, lng: 91.7876 },
    { name: "CU Railway Station", lat: 22.47068, lng: 91.79423 },
  ];

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
        if (body) {
          const message = body.detail || body;
          detail = typeof message === "string" ? message : JSON.stringify(message);
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

  async function deleteJSON(url) {
    return getJSON(url, {
      method: "DELETE",
      headers: {
        Accept: "application/json",
        "X-CSRFToken": getCookie("csrftoken") || "",
      },
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

  function haversineMeters(lat1, lng1, lat2, lng2) {
    const toRad = Math.PI / 180;
    const dLat = (lat2 - lat1) * toRad;
    const dLng = (lng2 - lng1) * toRad;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * toRad) * Math.cos(lat2 * toRad) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return 6371000 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(Math.max(0, 1 - a)));
  }

  function fmtDistance(meters) {
    if (!isFinite(meters) || meters < 0) return "";
    if (meters < 1000) return Math.round(meters) + " m";
    return (meters / 1000).toFixed(meters >= 10000 ? 1 : 2) + " km";
  }

  function userLocationIcon() {
    return L.divIcon({
      className: "vts-user-marker-wrap",
      html: '<div class="vts-user-marker" aria-hidden="true"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 10],
      popupAnchor: [0, -12],
    });
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
    const routePlanner = settings.routePlanner || null;
    const routeManager = settings.routeManager || null;
    const userLocator = settings.userLocator || null;

    const endpoint = mapEl.dataset.endpoint;
    const poll = parseInt(mapEl.dataset.poll || "8000", 10);
    const center = [parseFloat(mapEl.dataset.centerLat), parseFloat(mapEl.dataset.centerLng)];
    const zoom = parseInt(mapEl.dataset.zoom || "13", 10);
    const routingUrl = (mapEl.dataset.routingUrl || "").replace(/\/+$/, "");
    const routesEndpoint = mapEl.dataset.routesEndpoint || "";

    const map = L.map(mapEl, { center: center, zoom: zoom, zoomControl: true });
    tileLayer().addTo(map);

    const markers = new Map(); // vehicle_id -> { marker, latlng }
    let latestVehicles = [];
    let didFit = false;
    let selectedVehicleId = null;
    let plannedRouteLayer = null;
    let routeRequestController = null;
    let routeRequestId = 0;
    const userLocation = {
      lat: null,
      lng: null,
      accuracy: null,
      timestamp: null,
      marker: null,
      accuracyCircle: null,
      locating: false,
      copyTimer: null,
    };
    const fixedRouteStates = new Map(); // route_id -> rendered route state
    const hiddenFixedRouteIds = loadHiddenFixedRouteIds();
    // Google Maps official transit/navigation palette (vibrant core + crisp darker border casing)
    const fixedRoutePalette = [
      { core: "#4285F4", casing: "#174EA6" },
      { core: "#34A853", casing: "#137333" },
      { core: "#A142F4", casing: "#681DA8" },
      { core: "#FA7B17", casing: "#B06000" },
      { core: "#24C1E0", casing: "#007B83" },
      { core: "#EA4335", casing: "#A50E0E" },
    ];

    function popupHtml(v, status) {
      const details = [];
      details.push('<div class="vts-popup-row"><span>Updated</span><strong>' + escapeHtml(fmtAge(v.age_seconds)) + "</strong></div>");
      const speed = fmtSpeed(v.speed_kmh);
      if (speed) details.push('<div class="vts-popup-row"><span>Speed</span><strong>' + escapeHtml(speed) + "</strong></div>");
      if (admin && v.driver_name) details.push('<div class="vts-popup-row"><span>Driver</span><strong>' + escapeHtml(v.driver_name) + "</strong></div>");
      if (admin && v.accuracy_m) details.push('<div class="vts-popup-row"><span>Accuracy</span><strong>± ' + escapeHtml(v.accuracy_m) + " m</strong></div>");

      return (
        '<div class="vts-popup-card">' +
          '<div class="vts-popup-head">' +
            '<strong class="vts-popup-title">' + escapeHtml(v.bus_number) + "</strong>" +
            '<span class="status-badge is-' + status + '">' + status.charAt(0).toUpperCase() + status.slice(1) + "</span>" +
          "</div>" +
          (v.route_label ? '<div class="vts-popup-route">' + escapeHtml(v.route_label) + "</div>" : "") +
          '<div class="vts-popup-grid">' + details.join("") + "</div>" +
        "</div>"
      );
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

    function setupRoadRoutePlanner() {
      if (!routePlanner) return;

      const sourceInput = routePlanner.sourceInput;
      const destinationInput = routePlanner.destinationInput;
      const drawButton = routePlanner.drawButton;
      const clearButton = routePlanner.clearButton;
      const plannerStatusEl = routePlanner.statusEl;
      if (!sourceInput || !destinationInput || !drawButton || !clearButton || !plannerStatusEl) return;

      function setPlannerStatus(text, isError) {
        plannerStatusEl.textContent = text;
        plannerStatusEl.classList.toggle("text-danger", !!isError);
      }

      function setPlannerBusy(isBusy) {
        drawButton.disabled = isBusy;
        drawButton.textContent = isBusy ? "Finding road route…" : "Show driving route";
      }

      function clearPlannedRoute() {
        if (!plannedRouteLayer) return;
        map.removeLayer(plannedRouteLayer);
        plannedRouteLayer = null;
      }

      function clearInputError(input) {
        input.setCustomValidity("");
        input.removeAttribute("aria-invalid");
      }

      function readCoordinates(input, label) {
        const value = input.value.trim();
        const parts = value.match(/^([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*,\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))$/);
        if (!parts) {
          const message = label + ' must use the format "latitude, longitude".';
          input.setCustomValidity(message);
          input.setAttribute("aria-invalid", "true");
          input.reportValidity();
          throw new Error(message);
        }

        const latitude = Number(parts[1]);
        const longitude = Number(parts[2]);
        if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
          const message = label + " coordinates are outside the valid range.";
          input.setCustomValidity(message);
          input.setAttribute("aria-invalid", "true");
          input.reportValidity();
          throw new Error(message);
        }
        clearInputError(input);
        return { latitude: latitude, longitude: longitude };
      }

      function routeUrl(source, destination) {
        const coordinates = [
          source.longitude + "," + source.latitude,
          destination.longitude + "," + destination.latitude,
        ].join(";");
        return routingUrl + "/route/v1/driving/" + coordinates +
          "?alternatives=false&overview=full&geometries=geojson&steps=false";
      }

      function formatRouteDistance(metres) {
        if (!isFinite(metres)) return "";
        return metres >= 1000 ? (metres / 1000).toFixed(1) + " km" : Math.round(metres) + " m";
      }

      function formatRouteDuration(seconds) {
        if (!isFinite(seconds)) return "";
        const minutes = Math.max(1, Math.round(seconds / 60));
        if (minutes < 60) return minutes + " min";
        return Math.floor(minutes / 60) + "h " + (minutes % 60) + "m";
      }

      async function drawRoadRoute() {
        let source;
        let destination;
        try {
          source = readCoordinates(sourceInput, "Source");
          destination = readCoordinates(destinationInput, "Destination");
        } catch (error) {
          setPlannerStatus(error.message, true);
          return;
        }

        if (source.latitude === destination.latitude && source.longitude === destination.longitude) {
          const message = "Source and destination must be different coordinates.";
          destinationInput.setCustomValidity(message);
          destinationInput.setAttribute("aria-invalid", "true");
          destinationInput.reportValidity();
          setPlannerStatus(message, true);
          return;
        }
        if (!routingUrl) {
          setPlannerStatus("Road routing is not configured for this map.", true);
          return;
        }

        if (routeRequestController) routeRequestController.abort();
        const requestId = ++routeRequestId;
        routeRequestController = new AbortController();
        clearPlannedRoute();
        setPlannerBusy(true);
        setPlannerStatus("Finding the driving route…", false);

        try {
          const response = await fetch(routeUrl(source, destination), {
            headers: { Accept: "application/json" },
            signal: routeRequestController.signal,
          });
          let payload;
          try {
            payload = await response.json();
          } catch (parseError) {
            throw new Error("The routing service returned an invalid response.");
          }
          if (!response.ok || !payload || payload.code !== "Ok") {
            throw new Error((payload && payload.message) || "No drivable route was found.");
          }
          const route = Array.isArray(payload.routes) ? payload.routes[0] : null;
          const coordinates = route && route.geometry && Array.isArray(route.geometry.coordinates)
            ? route.geometry.coordinates
            : [];
          const latlngs = coordinates
            .map(function (point) {
              return Array.isArray(point) && isFinite(point[0]) && isFinite(point[1])
                ? [point[1], point[0]]
                : null;
            })
            .filter(function (point) { return point !== null; });
          if (latlngs.length < 2) throw new Error("The routing service returned no road geometry.");
          if (requestId !== routeRequestId) return;

          const routeCasing = L.polyline(latlngs, {
            color: "#174EA6",
            weight: 9,
            opacity: 0.96,
            interactive: false,
            lineCap: "round",
            lineJoin: "round",
          });
          const routeLine = L.polyline(latlngs, {
            color: "#4285F4",
            weight: 5.5,
            opacity: 1,
            lineCap: "round",
            lineJoin: "round",
          });
          const sourceMarker = L.circleMarker([source.latitude, source.longitude], {
            radius: 7.5,
            color: "#ffffff",
            fillColor: "#1E8E3E",
            fillOpacity: 1,
            weight: 3,
          }).bindTooltip("Source");
          const destinationMarker = L.circleMarker([destination.latitude, destination.longitude], {
            radius: 7.5,
            color: "#ffffff",
            fillColor: "#EA4335",
            fillOpacity: 1,
            weight: 3,
          }).bindTooltip("Destination");
          plannedRouteLayer = L.layerGroup([routeCasing, routeLine, sourceMarker, destinationMarker]).addTo(map);
          const summary = [formatRouteDistance(route.distance), formatRouteDuration(route.duration)]
            .filter(function (value) { return value; })
            .join(" · ");
          setPlannerStatus("Driving route ready" + (summary ? " · " + summary : ""), false);
          map.fitBounds(routeLine.getBounds(), { padding: [40, 40], maxZoom: 16 });
        } catch (error) {
          if (error.name === "AbortError" || requestId !== routeRequestId) return;
          clearPlannedRoute();
          const message = error instanceof TypeError
            ? "The routing service could not be reached. Please try again."
            : error.message || "The driving route could not be loaded.";
          setPlannerStatus(message, true);
        } finally {
          if (requestId === routeRequestId) {
            routeRequestController = null;
            setPlannerBusy(false);
          }
        }
      }

      sourceInput.addEventListener("input", function () { clearInputError(sourceInput); });
      destinationInput.addEventListener("input", function () { clearInputError(destinationInput); });
      [sourceInput, destinationInput].forEach(function (input) {
        input.addEventListener("keydown", function (event) {
          if (event.key === "Enter") {
            event.preventDefault();
            drawRoadRoute();
          }
        });
      });
      drawButton.addEventListener("click", drawRoadRoute);
      clearButton.addEventListener("click", function () {
        routeRequestId += 1;
        if (routeRequestController) routeRequestController.abort();
        routeRequestController = null;
        clearPlannedRoute();
        setPlannerBusy(false);
        setPlannerStatus("", false);
      });
    }

    // ---- Fixed bus routes -------------------------------------------------
    // A saved route stores only its named waypoints. The form accepts the
    // familiar latitude, longitude notation; the router request is converted
    // to its required longitude, latitude order. The browser asks the
    // same OSRM-compatible router used by the one-off planner for one road
    // route with all waypoints in order, so the line follows actual roads
    // rather than joining stops with straight segments.
    function loadHiddenFixedRouteIds() {
      try {
        const stored = JSON.parse(window.localStorage.getItem("vts-hidden-route-ids") || "[]");
        return new Set(
          Array.isArray(stored)
            ? stored.filter(function (id) { return Number.isInteger(id) && id > 0; })
            : []
        );
      } catch (error) {
        return new Set();
      }
    }

    function saveHiddenFixedRouteIds() {
      try {
        window.localStorage.setItem(
          "vts-hidden-route-ids",
          JSON.stringify(Array.from(hiddenFixedRouteIds).sort(function (a, b) { return a - b; }))
        );
      } catch (error) {
        // Visibility still works for this visit if browser storage is unavailable.
      }
    }

    function fixedRouteSwatch(routeId) {
      return fixedRoutePalette[routeId % fixedRoutePalette.length];
    }

    function fixedRouteColour(routeId) {
      return fixedRouteSwatch(routeId).core;
    }

    function formatRoadDistance(metres) {
      if (!isFinite(metres)) return "";
      return metres >= 1000 ? (metres / 1000).toFixed(1) + " km" : Math.round(metres) + " m";
    }

    function formatRoadDuration(seconds) {
      if (!isFinite(seconds)) return "";
      const minutes = Math.max(1, Math.round(seconds / 60));
      if (minutes < 60) return minutes + " min";
      return Math.floor(minutes / 60) + "h " + (minutes % 60) + "m";
    }

    function fixedRoutePoints(route) {
      const rawPoints = [
        { type: "start", name: "Start", longitude: route.start_longitude, latitude: route.start_latitude },
      ].concat(
        (Array.isArray(route.stops) ? route.stops : []).map(function (stop) {
          return {
            type: "stop",
            name: stop.name,
            longitude: stop.longitude,
            latitude: stop.latitude,
            sequence: stop.sequence,
          };
        })
      ).concat([
        { type: "end", name: "End", longitude: route.end_longitude, latitude: route.end_latitude },
      ]);

      return rawPoints.map(function (point) {
        return {
          type: point.type,
          name: point.name,
          sequence: point.sequence,
          longitude: Number(point.longitude),
          latitude: Number(point.latitude),
        };
      }).filter(function (point) {
        return isFinite(point.longitude) && isFinite(point.latitude);
      });
    }

    function fixedRouteUrl(points) {
      const coordinates = points.map(function (point) {
        return point.longitude + "," + point.latitude;
      }).join(";");
      return routingUrl + "/route/v1/driving/" + coordinates +
        "?alternatives=false&overview=full&geometries=geojson&steps=false";
    }

    function removeFixedRouteLayer(state) {
      if (state.layer && map.hasLayer(state.layer)) map.removeLayer(state.layer);
    }

    function setFixedRouteManagerStatus(text, isError, isSuccess) {
      if (!routeManager || !routeManager.statusEl) return;
      routeManager.statusEl.textContent = text || "";
      routeManager.statusEl.classList.toggle("text-danger", !!isError);
      routeManager.statusEl.classList.toggle("text-success", !!isSuccess);
    }

    function updateNewRouteNumber() {
      if (!routeManager || !routeManager.numberEl) return;
      routeManager.numberEl.textContent = String(fixedRouteStates.size + 1);
    }

    function renderFixedRouteList() {
      if (!routeManager || !routeManager.listEl) return;
      const states = Array.from(fixedRouteStates.values()).sort(function (left, right) {
        return left.route.name.localeCompare(right.route.name);
      });
      if (routeManager.countEl) {
        routeManager.countEl.textContent = states.length + (states.length === 1 ? " route" : " routes");
      }
      updateNewRouteNumber();

      if (!states.length) {
        routeManager.listEl.innerHTML =
          '<div class="vts-list-placeholder">No fixed routes yet.</div>';
        return;
      }

      routeManager.listEl.innerHTML = states.map(function (state, index) {
        const route = state.route;
        const stopCount = Array.isArray(route.stops) ? route.stops.length : 0;
        const status = state.error
          ? state.error
          : (state.loading ? "Finding road path…" : (state.summary || (state.visible ? "Visible" : "Hidden")));
        const eyeTitle = state.visible ? "Hide route on map" : "Show route on map";
        const eyeIcon = state.visible ? ICON_EYE : ICON_EYE_OFF;
        return (
          '<article class="route-list-item' + (state.visible ? "" : " is-hidden") + '" ' +
            'style="--route-color: ' + fixedRouteColour(route.id) + '">' +
            '<div class="min-w-0">' +
              '<div class="route-list-name">Route ' + (index + 1) + " · " + escapeHtml(route.name) + "</div>" +
              '<div class="route-list-meta">Start → ' + stopCount + (stopCount === 1 ? " stop" : " stops") + " → End</div>" +
              '<div class="route-list-status' + (state.error ? " is-error" : "") + '">' + escapeHtml(status) + "</div>" +
            "</div>" +
            '<div class="route-list-actions">' +
              '<button class="btn btn-sm btn-outline-secondary route-eye-button' + (state.visible ? "" : " is-hidden") + '" type="button" data-route-visibility="' + route.id + '" aria-label="' + eyeTitle + '" title="' + eyeTitle + '">' + eyeIcon + "</button>" +
              '<button class="btn btn-sm btn-outline-danger route-delete-button" type="button" data-route-delete="' + route.id + '" aria-label="Delete ' + escapeHtml(route.name) + '" title="Delete route">' + ICON_TRASH + "</button>" +
            "</div>" +
          "</article>"
        );
      }).join("");

      routeManager.listEl.querySelectorAll("[data-route-visibility]").forEach(function (button) {
        button.addEventListener("click", function () {
          toggleFixedRouteVisibility(Number(button.dataset.routeVisibility));
        });
      });
      routeManager.listEl.querySelectorAll("[data-route-delete]").forEach(function (button) {
        button.addEventListener("click", function () {
          deleteFixedRoute(Number(button.dataset.routeDelete));
        });
      });
    }

    function makeFixedRouteLayer(state, latlngs, routeData) {
      const swatch = fixedRouteSwatch(state.route.id);
      const casingLine = L.polyline(latlngs, {
        color: swatch.casing,
        weight: 8.5,
        opacity: 0.95,
        interactive: false,
        lineCap: "round",
        lineJoin: "round",
      });
      const routeLine = L.polyline(latlngs, {
        color: swatch.core,
        weight: 5,
        opacity: 1,
        lineCap: "round",
        lineJoin: "round",
      }).bindTooltip(escapeHtml(state.route.name), {
        sticky: true,
        direction: "top",
        className: "vts-route-tooltip",
      });
      const pointMarkers = fixedRoutePoints(state.route).map(function (point) {
        const isStop = point.type === "stop";
        const appearance = point.type === "start"
          ? { color: "#ffffff", fillColor: "#1E8E3E", radius: 7.5, weight: 3 }
          : (point.type === "end"
            ? { color: "#ffffff", fillColor: "#EA4335", radius: 7.5, weight: 3 }
            : { color: swatch.casing, fillColor: "#ffffff", radius: 5.5, weight: 2.8 });
        const title = isStop
          ? "Stop " + point.sequence + ": " + point.name
          : point.type === "start" ? "Start" : "End";
        return L.circleMarker([point.latitude, point.longitude], {
          radius: appearance.radius,
          fillOpacity: 1,
          weight: appearance.weight,
          color: appearance.color,
          fillColor: appearance.fillColor,
        }).bindTooltip(escapeHtml(title), { direction: "top", className: "vts-route-tooltip" });
      });
      state.routeLine = routeLine;
      state.layer = L.layerGroup([casingLine, routeLine].concat(pointMarkers));
      state.summary = [formatRoadDistance(routeData.distance), formatRoadDuration(routeData.duration)]
        .filter(function (value) { return value; })
        .join(" · ") || "Road path ready";
    }

    async function loadFixedRouteGeometry(state, fitWhenReady) {
      if (state.layer) {
        if (state.visible && !map.hasLayer(state.layer)) state.layer.addTo(map);
        if (fitWhenReady && state.routeLine && state.routeLine.getBounds().isValid()) {
          map.fitBounds(state.routeLine.getBounds(), { padding: [40, 40], maxZoom: 16 });
        }
        return;
      }
      if (state.loading) {
        state.fitWhenReady = state.fitWhenReady || fitWhenReady;
        return;
      }
      if (!routingUrl) {
        state.error = "Road routing is not configured.";
        renderFixedRouteList();
        return;
      }

      const points = fixedRoutePoints(state.route);
      if (points.length < 2) {
        state.error = "This route has invalid coordinates.";
        renderFixedRouteList();
        return;
      }

      state.loading = true;
      state.error = "";
      state.fitWhenReady = fitWhenReady;
      state.controller = new AbortController();
      renderFixedRouteList();
      try {
        const response = await fetch(fixedRouteUrl(points), {
          headers: { Accept: "application/json" },
          signal: state.controller.signal,
        });
        let payload;
        try {
          payload = await response.json();
        } catch (parseError) {
          throw new Error("The routing service returned an invalid response.");
        }
        if (!response.ok || !payload || payload.code !== "Ok") {
          throw new Error((payload && payload.message) || "No drivable route was found.");
        }
        const roadRoute = Array.isArray(payload.routes) ? payload.routes[0] : null;
        const coordinates = roadRoute && roadRoute.geometry && Array.isArray(roadRoute.geometry.coordinates)
          ? roadRoute.geometry.coordinates
          : [];
        const latlngs = coordinates.map(function (point) {
          return Array.isArray(point) && isFinite(point[0]) && isFinite(point[1])
            ? [point[1], point[0]]
            : null;
        }).filter(function (point) { return point !== null; });
        if (latlngs.length < 2) throw new Error("The routing service returned no road geometry.");
        if (fixedRouteStates.get(state.route.id) !== state) return;

        makeFixedRouteLayer(state, latlngs, roadRoute);
        if (state.visible) state.layer.addTo(map);
        if (state.fitWhenReady && state.routeLine.getBounds().isValid()) {
          map.fitBounds(state.routeLine.getBounds(), { padding: [40, 40], maxZoom: 16 });
        }
      } catch (error) {
        if (error.name !== "AbortError" && fixedRouteStates.get(state.route.id) === state) {
          state.error = error instanceof TypeError
            ? "Road path could not be reached."
            : error.message || "Road path could not be loaded.";
        }
      } finally {
        if (fixedRouteStates.get(state.route.id) === state) {
          state.loading = false;
          state.controller = null;
          state.fitWhenReady = false;
          renderFixedRouteList();
        }
      }
    }

    function toggleFixedRouteVisibility(routeId) {
      const state = fixedRouteStates.get(routeId);
      if (!state) return;
      state.visible = !state.visible;
      if (state.visible) {
        hiddenFixedRouteIds.delete(routeId);
        loadFixedRouteGeometry(state, false);
      } else {
        hiddenFixedRouteIds.add(routeId);
        removeFixedRouteLayer(state);
      }
      saveHiddenFixedRouteIds();
      renderFixedRouteList();
    }

    async function deleteFixedRoute(routeId) {
      const state = fixedRouteStates.get(routeId);
      if (!state || !routesEndpoint) return;
      if (!window.confirm('Delete the fixed route "' + state.route.name + '"?')) return;

      try {
        await deleteJSON(routesEndpoint + routeId + "/");
      } catch (error) {
        setFixedRouteManagerStatus(error.message || "The route could not be deleted.", true, false);
        return;
      }
      if (state.controller) state.controller.abort();
      removeFixedRouteLayer(state);
      fixedRouteStates.delete(routeId);
      hiddenFixedRouteIds.delete(routeId);
      saveHiddenFixedRouteIds();
      setFixedRouteManagerStatus("Route deleted.", false, true);
      renderFixedRouteList();
    }

    async function fetchFixedRoutes(fitRouteId) {
      if (!routeManager || !routesEndpoint) return;
      try {
        const data = await getJSON(routesEndpoint);
        const routes = data && Array.isArray(data.results) ? data.results : [];
        const incomingIds = new Set();
        routes.forEach(function (route) {
          incomingIds.add(route.id);
          let state = fixedRouteStates.get(route.id);
          if (!state) {
            state = {
              route: route,
              visible: !hiddenFixedRouteIds.has(route.id),
              layer: null,
              routeLine: null,
              controller: null,
              loading: false,
              summary: "",
              error: "",
              fitWhenReady: false,
            };
            fixedRouteStates.set(route.id, state);
          } else {
            state.route = route;
          }
        });
        Array.from(fixedRouteStates.entries()).forEach(function (entry) {
          const routeId = entry[0];
          const state = entry[1];
          if (!incomingIds.has(routeId)) {
            if (state.controller) state.controller.abort();
            removeFixedRouteLayer(state);
            fixedRouteStates.delete(routeId);
            hiddenFixedRouteIds.delete(routeId);
          }
        });
        saveHiddenFixedRouteIds();
        renderFixedRouteList();
        fixedRouteStates.forEach(function (state) {
          if (state.visible) loadFixedRouteGeometry(state, state.route.id === fitRouteId);
        });
      } catch (error) {
        routeManager.listEl.innerHTML =
          '<div class="text-center text-danger small py-3">Routes could not be loaded.</div>';
      }
    }

    function setupFixedRouteManager() {
      if (!routeManager || !routesEndpoint) return;
      const form = routeManager.form;
      const nameInput = routeManager.nameInput;
      const startInput = routeManager.startInput;
      const endInput = routeManager.endInput;
      const stopsEl = routeManager.stopsEl;
      const addStopButton = routeManager.addStopButton;
      const saveButton = routeManager.saveButton;
      if (!form || !nameInput || !startInput || !endInput || !stopsEl || !addStopButton || !saveButton) return;

      function clearInputError(input) {
        input.setCustomValidity("");
        input.removeAttribute("aria-invalid");
      }

      function readCoordinates(input, label) {
        const value = input.value.trim();
        const parts = value.match(/^([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*,\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))$/);
        if (!parts) {
          const message = label + ' must use the format "latitude, longitude".';
          input.setCustomValidity(message);
          input.setAttribute("aria-invalid", "true");
          input.reportValidity();
          throw new Error(message);
        }
        const latitude = Number(parts[1]);
        const longitude = Number(parts[2]);
        if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
          const message = label + " coordinates are outside the valid range.";
          input.setCustomValidity(message);
          input.setAttribute("aria-invalid", "true");
          input.reportValidity();
          throw new Error(message);
        }
        clearInputError(input);
        // Database coordinates are stored at six decimal places (about 11 cm
        // at the equator). Accept normal full-precision GPS input, then
        // normalize it before posting so valid readings never fail precision
        // validation on the server.
        return {
          longitude: Number(longitude.toFixed(6)),
          latitude: Number(latitude.toFixed(6)),
        };
      }

      function renumberStopEditors() {
        stopsEl.querySelectorAll(".route-stop-editor").forEach(function (editor, index) {
          const number = index + 1;
          editor.querySelector(".route-stop-label").textContent = "Stop " + number + " →";
          editor.querySelector(".route-stop-name").setAttribute("aria-label", "Stop " + number + " name");
          editor.querySelector(".route-stop-coordinate").setAttribute(
            "aria-label", "Stop " + number + " coordinates"
          );
        });
      }

      function addStopEditor() {
        const editor = document.createElement("div");
        editor.className = "route-stop-editor";
        const header = document.createElement("div");
        header.className = "route-stop-header";
        const label = document.createElement("span");
        label.className = "route-stop-label";
        const name = document.createElement("input");
        name.className = "form-control form-control-sm route-stop-name";
        name.type = "text";
        name.maxLength = 120;
        name.required = true;
        name.autocomplete = "off";
        name.placeholder = "Stop name";
        const remove = document.createElement("button");
        remove.className = "btn btn-sm btn-outline-danger route-stop-remove";
        remove.type = "button";
        remove.setAttribute("aria-label", "Remove stop");
        remove.title = "Remove stop";
        remove.innerHTML = ICON_CLOSE;
        const coordinate = document.createElement("input");
        coordinate.className = "form-control form-control-sm route-coordinate-input route-stop-coordinate";
        coordinate.type = "text";
        coordinate.inputMode = "decimal";
        coordinate.autocomplete = "off";
        coordinate.spellcheck = false;
        coordinate.required = true;
        coordinate.placeholder = "Latitude, longitude";
        [name, coordinate].forEach(function (input) {
          input.addEventListener("input", function () { clearInputError(input); });
        });
        remove.addEventListener("click", function () {
          editor.remove();
          renumberStopEditors();
        });
        header.append(label, name, remove);
        editor.append(header, coordinate);
        stopsEl.append(editor);
        renumberStopEditors();
        name.focus();
      }

      function resetForm() {
        form.reset();
        stopsEl.innerHTML = "";
        [nameInput, startInput, endInput].forEach(clearInputError);
      }

      function setSaving(isSaving) {
        saveButton.disabled = isSaving;
        saveButton.textContent = isSaving ? "Saving route…" : "Save route";
      }

      [nameInput, startInput, endInput].forEach(function (input) {
        input.addEventListener("input", function () { clearInputError(input); });
      });
      addStopButton.addEventListener("click", addStopEditor);
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const name = nameInput.value.trim();
        if (!name) {
          const message = "Route name is required.";
          nameInput.setCustomValidity(message);
          nameInput.setAttribute("aria-invalid", "true");
          nameInput.reportValidity();
          setFixedRouteManagerStatus(message, true, false);
          return;
        }

        let start;
        let end;
        let stops;
        try {
          start = readCoordinates(startInput, "Start");
          end = readCoordinates(endInput, "End");
          stops = Array.from(stopsEl.querySelectorAll(".route-stop-editor")).map(function (editor, index) {
            const stopNameInput = editor.querySelector(".route-stop-name");
            const stopName = stopNameInput.value.trim();
            if (!stopName) {
              const message = "Stop " + (index + 1) + " name is required.";
              stopNameInput.setCustomValidity(message);
              stopNameInput.setAttribute("aria-invalid", "true");
              stopNameInput.reportValidity();
              throw new Error(message);
            }
            clearInputError(stopNameInput);
            const point = readCoordinates(
              editor.querySelector(".route-stop-coordinate"), "Stop " + (index + 1)
            );
            return { name: stopName, longitude: point.longitude, latitude: point.latitude };
          });
        } catch (error) {
          setFixedRouteManagerStatus(error.message, true, false);
          return;
        }

        setSaving(true);
        setFixedRouteManagerStatus("Saving the fixed route…", false, false);
        try {
          const route = await postJSON(routesEndpoint, {
            name: name,
            start_longitude: start.longitude,
            start_latitude: start.latitude,
            stops: stops,
            end_longitude: end.longitude,
            end_latitude: end.latitude,
          });
          resetForm();
          setFixedRouteManagerStatus("Route saved. Finding its road path…", false, true);
          await fetchFixedRoutes(route.id);
        } catch (error) {
          setFixedRouteManagerStatus(error.message || "The route could not be saved.", true, false);
        } finally {
          setSaving(false);
        }
      });

      fetchFixedRoutes();
    }

    function removeMarker(vehicleId) {
      const entry = markers.get(vehicleId);
      if (entry) {
        map.removeLayer(entry.marker);
        markers.delete(vehicleId);
      }
    }

    function focus(vehicleId) {
      selectedVehicleId = vehicleId;
      if (listEl) {
        listEl.querySelectorAll(".vehicle-item").forEach(function (btn) {
          btn.classList.toggle("active", parseInt(btn.dataset.id, 10) === vehicleId);
        });
      }
      const entry = markers.get(vehicleId);
      if (entry) {
        map.setView(entry.latlng, Math.max(map.getZoom(), 16));
        entry.marker.openPopup();
      }
    }

    function renderList(vehicles) {
      if (!listEl) return;
      if (!vehicles.length) {
        listEl.innerHTML = '<div class="vts-list-placeholder">No active vehicles.</div>';
        return;
      }
      const html = vehicles
        .map(function (v) {
          const status = statusOf(v);
          const speed = fmtSpeed(v.speed_kmh);
          const isActive = v.vehicle_id === selectedVehicleId;
          const driver = admin && v.driver_name
            ? '<div class="vehicle-item__driver">' + ICON_USER + "<span>" + escapeHtml(v.driver_name) + "</span></div>"
            : "";
          return (
            '<button type="button" class="list-group-item list-group-item-action vehicle-item' + (isActive ? " active" : "") + '" data-id="' + v.vehicle_id + '">' +
              '<div class="vehicle-item__row">' +
                '<span class="vehicle-item__icon is-' + status + '" aria-hidden="true">' + ICON_BUS + "</span>" +
                '<div class="vehicle-item__main">' +
                  '<div class="vehicle-item__title">' + escapeHtml(v.bus_number) + "</div>" +
                  '<div class="vehicle-item__route">' + escapeHtml(v.route_label || "—") + "</div>" +
                  driver +
                "</div>" +
                '<div class="vehicle-item__meta">' +
                  '<span class="status-badge is-' + status + '">' + status + "</span>" +
                  '<div class="vehicle-item__age">' + escapeHtml(fmtAge(v.age_seconds)) + "</div>" +
                  (speed ? '<div class="vehicle-item__speed">' + escapeHtml(speed) + "</div>" : "") +
                "</div>" +
              "</div>" +
            "</button>"
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

    // ---- User "My Location" finder (available to all personas) ------------
    function locatorButtons() {
      if (!userLocator || !userLocator.buttons) return [];
      return Array.prototype.slice.call(userLocator.buttons);
    }

    function nearestCampusLandmark(lat, lng) {
      let best = null;
      CAMPUS_LANDMARKS.forEach(function (lm) {
        const dist = haversineMeters(lat, lng, lm.lat, lm.lng);
        if (!best || dist < best.distance) {
          best = { name: lm.name, distance: dist };
        }
      });
      if (!best) return "";
      if (best.distance < 80) return "At " + best.name;
      return fmtDistance(best.distance) + " from " + best.name;
    }

    function findNearestActiveVehicle(lat, lng) {
      let best = null;
      latestVehicles.forEach(function (v) {
        if (!v || !v.has_signal) return;
        const vLat = parseFloat(v.latitude);
        const vLng = parseFloat(v.longitude);
        if (!isFinite(vLat) || !isFinite(vLng)) return;
        const dist = haversineMeters(lat, lng, vLat, vLng);
        if (!best || dist < best.distance) {
          best = { vehicle: v, distance: dist };
        }
      });
      return best;
    }

    function formatUserCoords() {
      if (userLocation.lat == null || userLocation.lng == null) return "";
      return userLocation.lat.toFixed(6) + ", " + userLocation.lng.toFixed(6);
    }

    function userPopupHtml() {
      const coordsText = formatUserCoords();
      const landmark = nearestCampusLandmark(userLocation.lat, userLocation.lng);
      const nearest = findNearestActiveVehicle(userLocation.lat, userLocation.lng);
      const details = [];
      details.push('<div class="vts-popup-row"><span>Coordinates</span><strong>' + escapeHtml(coordsText) + "</strong></div>");
      if (isFinite(userLocation.accuracy)) {
        details.push('<div class="vts-popup-row"><span>Accuracy</span><strong>± ' + escapeHtml(String(Math.round(userLocation.accuracy))) + " m</strong></div>");
      }
      if (nearest) {
        details.push(
          '<div class="vts-popup-row"><span>Nearest bus</span><strong>' +
            escapeHtml(nearest.vehicle.bus_number) + " · " + escapeHtml(fmtDistance(nearest.distance)) +
          "</strong></div>"
        );
      }
      return (
        '<div class="vts-popup-card">' +
          '<div class="vts-popup-head">' +
            '<strong class="vts-popup-title">Your location</strong>' +
            '<span class="status-badge is-user">You</span>' +
          "</div>" +
          (landmark ? '<div class="vts-popup-route">' + escapeHtml(landmark) + "</div>" : "") +
          '<div class="vts-popup-grid">' + details.join("") + "</div>" +
        "</div>"
      );
    }

    function setLocatorBusy(isBusy) {
      userLocation.locating = isBusy;
      locatorButtons().forEach(function (btn) {
        btn.classList.toggle("is-locating", isBusy);
        btn.setAttribute("aria-busy", String(isBusy));
        btn.disabled = isBusy;
      });
    }

    function setLocatorActive(isActive) {
      locatorButtons().forEach(function (btn) {
        btn.classList.toggle("is-located", isActive);
        btn.setAttribute("aria-pressed", String(isActive));
      });
    }

    function renderUserLocationCard() {
      if (!userLocator || !userLocator.cardEl) return;
      const hasFix = userLocation.lat != null && userLocation.lng != null;
      if (!hasFix) return;
      const card = userLocator.cardEl;
      card.hidden = false;
      card.classList.remove("d-none", "is-error", "is-loading", "is-no-fix");

      const coordsText = formatUserCoords();
      const landmark = nearestCampusLandmark(userLocation.lat, userLocation.lng);
      const accuracyText = isFinite(userLocation.accuracy)
        ? "± " + Math.round(userLocation.accuracy) + " m"
        : "GPS fix";
      const updatedText = userLocation.timestamp ? fmtTime(userLocation.timestamp) : "";

      if (userLocator.statusEl) {
        userLocator.statusEl.textContent = landmark || "Current GPS position";
      }
      if (userLocator.coordsEl) {
        userLocator.coordsEl.textContent = coordsText;
      }
      if (userLocator.metaEl) {
        userLocator.metaEl.textContent = [accuracyText, updatedText ? "Updated " + updatedText : ""]
          .filter(function (part) { return part; })
          .join(" · ");
      }
      if (userLocator.nearestEl) {
        const nearest = findNearestActiveVehicle(userLocation.lat, userLocation.lng);
        if (nearest) {
          const v = nearest.vehicle;
          const label = v.bus_number + (v.route_label ? " (" + v.route_label + ")" : "");
          userLocator.nearestEl.innerHTML =
            '<button type="button" class="vts-my-loc__nearest-btn" data-focus-nearest-vehicle="' +
              escapeHtml(String(v.vehicle_id)) + '">' +
              '<span class="vts-my-loc__nearest-label">Nearest bus: <strong>' + escapeHtml(label) + "</strong></span>" +
              '<span class="vts-my-loc__nearest-dist">' + escapeHtml(fmtDistance(nearest.distance)) + "</span>" +
            "</button>";
          const focusBtn = userLocator.nearestEl.querySelector("[data-focus-nearest-vehicle]");
          if (focusBtn) {
            focusBtn.addEventListener("click", function () {
              focus(parseInt(focusBtn.dataset.focusNearestVehicle, 10));
            });
          }
        } else {
          userLocator.nearestEl.innerHTML =
            '<span class="vts-my-loc__nearest-empty">No active buses reporting GPS right now.</span>';
        }
      }
      if (userLocator.copyBtn) userLocator.copyBtn.disabled = false;
      if (userLocator.routeStartBtn) userLocator.routeStartBtn.disabled = false;
    }

    function showUserLocationStatus(message, isError) {
      if (!userLocator || !userLocator.cardEl) return;
      const card = userLocator.cardEl;
      card.hidden = false;
      card.classList.remove("d-none");
      card.classList.toggle("is-error", !!isError);
      card.classList.toggle("is-loading", !isError);
      if (userLocator.statusEl) userLocator.statusEl.textContent = message;
      const hasFix = userLocation.lat != null && userLocation.lng != null;
      card.classList.toggle("is-no-fix", !hasFix);
      if (!hasFix) {
        if (userLocator.coordsEl) userLocator.coordsEl.textContent = "—";
        if (userLocator.metaEl) userLocator.metaEl.textContent = "";
        if (userLocator.nearestEl) userLocator.nearestEl.textContent = "";
        if (userLocator.copyBtn) userLocator.copyBtn.disabled = true;
        if (userLocator.routeStartBtn) userLocator.routeStartBtn.disabled = true;
      }
      if (isError) {
        const split = mapEl.closest(".vts-split");
        if (split && split.classList.contains("is-side-collapsed")) {
          const expandBtn = split.querySelector("[data-side-toggle]");
          if (expandBtn) expandBtn.click();
        }
      }
    }

    function applyUserPosition(lat, lng, accuracy, timestampIso) {
      userLocation.lat = lat;
      userLocation.lng = lng;
      userLocation.accuracy = isFinite(accuracy) && accuracy > 0 ? accuracy : null;
      userLocation.timestamp = timestampIso || new Date().toISOString();

      const latlng = [lat, lng];
      const radius = isFinite(accuracy) && accuracy > 0 ? Math.min(Math.max(accuracy, 8), 2000) : 25;
      if (!userLocation.accuracyCircle) {
        userLocation.accuracyCircle = L.circle(latlng, {
          radius: radius,
          color: "#1a73e8",
          fillColor: "#4285f4",
          fillOpacity: 0.14,
          weight: 1.5,
          interactive: false,
        }).addTo(map);
      } else {
        userLocation.accuracyCircle.setLatLng(latlng);
        userLocation.accuracyCircle.setRadius(radius);
      }

      if (!userLocation.marker) {
        userLocation.marker = L.marker(latlng, {
          icon: userLocationIcon(),
          title: "Your location",
          zIndexOffset: 900,
        }).addTo(map);
      } else {
        userLocation.marker.setLatLng(latlng);
      }

      userLocation.marker.bindPopup(userPopupHtml());
      didFit = true;
      setLocatorActive(true);
      renderUserLocationCard();
      map.setView(latlng, Math.max(map.getZoom(), 16));
      userLocation.marker.openPopup();
    }

    function clearUserLocation() {
      if (userLocation.marker && map.hasLayer(userLocation.marker)) {
        map.removeLayer(userLocation.marker);
      }
      if (userLocation.accuracyCircle && map.hasLayer(userLocation.accuracyCircle)) {
        map.removeLayer(userLocation.accuracyCircle);
      }
      userLocation.lat = null;
      userLocation.lng = null;
      userLocation.accuracy = null;
      userLocation.timestamp = null;
      userLocation.marker = null;
      userLocation.accuracyCircle = null;
      setLocatorActive(false);
      if (userLocator && userLocator.cardEl) {
        userLocator.cardEl.hidden = true;
        userLocator.cardEl.classList.add("d-none", "is-no-fix");
        userLocator.cardEl.classList.remove("is-error", "is-loading");
      }
    }

    function locateUser() {
      if (userLocation.locating) return;
      if (!navigator.geolocation) {
        showUserLocationStatus("Geolocation is not supported by this browser.", true);
        return;
      }
      if (window.isSecureContext === false) {
        showUserLocationStatus("Location access requires a secure (HTTPS) connection.", true);
        return;
      }

      setLocatorBusy(true);
      showUserLocationStatus("Locating your position…", false);

      navigator.geolocation.getCurrentPosition(
        function (position) {
          setLocatorBusy(false);
          const coords = position && position.coords;
          if (!coords || !isFinite(coords.latitude) || !isFinite(coords.longitude)) {
            showUserLocationStatus("Received invalid coordinates from your device.", true);
            return;
          }
          if (coords.latitude < -90 || coords.latitude > 90 || coords.longitude < -180 || coords.longitude > 180) {
            showUserLocationStatus("Received out-of-range coordinates from your device.", true);
            return;
          }
          const ts = position.timestamp ? new Date(position.timestamp).toISOString() : new Date().toISOString();
          applyUserPosition(coords.latitude, coords.longitude, coords.accuracy, ts);
        },
        function (err) {
          setLocatorBusy(false);
          let message = "Your current location could not be determined right now. Please try again.";
          if (err && err.code === 1) {
            message = "Location permission was denied. Allow location access in your browser settings and try again.";
          } else if (err && err.code === 3) {
            message = "Location request timed out. Move to an open area or try again.";
          }
          showUserLocationStatus(message, true);
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 15000 }
      );
    }

    function setupUserLocator() {
      if (!userLocator) return;
      locatorButtons().forEach(function (btn) {
        btn.addEventListener("click", locateUser);
      });
      if (userLocator.closeBtn) {
        userLocator.closeBtn.addEventListener("click", clearUserLocation);
      }
      if (userLocator.copyBtn) {
        userLocator.copyBtn.addEventListener("click", function () {
          const text = formatUserCoords();
          if (!text) return;
          const finishCopy = function () {
            const label = userLocator.copyBtn.querySelector("[data-copy-label]") || userLocator.copyBtn;
            if (!label.dataset.copyDefault) label.dataset.copyDefault = label.textContent;
            label.textContent = "Copied";
            if (userLocation.copyTimer) window.clearTimeout(userLocation.copyTimer);
            userLocation.copyTimer = window.setTimeout(function () {
              label.textContent = label.dataset.copyDefault;
            }, 1800);
          };
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(finishCopy, function () {
              /* fallback ignored if clipboard blocked */
            });
          } else {
            const ta = document.createElement("textarea");
            ta.value = text;
            ta.setAttribute("readonly", "");
            ta.style.position = "fixed";
            ta.style.opacity = "0";
            document.body.appendChild(ta);
            ta.select();
            try {
              document.execCommand("copy");
              finishCopy();
            } catch (e) {
              /* clipboard unavailable */
            }
            ta.remove();
          }
        });
      }
      if (userLocator.routeStartBtn && routePlanner && routePlanner.sourceInput) {
        userLocator.routeStartBtn.addEventListener("click", function () {
          const text = formatUserCoords();
          if (!text) return;
          if (userLocator.fleetTab) userLocator.fleetTab.click();
          if (userLocator.plannerDetails) userLocator.plannerDetails.open = true;
          routePlanner.sourceInput.value = text;
          routePlanner.sourceInput.dispatchEvent(new Event("input", { bubbles: true }));
          if (routePlanner.destinationInput) {
            routePlanner.destinationInput.focus();
            if (routePlanner.destinationInput.scrollIntoView) {
              routePlanner.destinationInput.scrollIntoView({ behavior: "smooth", block: "center" });
            }
          }
        });
      }
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
      latestVehicles = vehicles;
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
      if (userLocation.lat != null && userLocation.lng != null) {
        renderUserLocationCard();
        if (userLocation.marker) userLocation.marker.setPopupContent(userPopupHtml());
      }
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

    setupRoadRoutePlanner();
    setupFixedRouteManager();
    setupUserLocator();
    refresh();
    const timer = setInterval(refresh, poll);
    // Pause polling when the tab is hidden to save the free-tier request budget.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") refresh();
    });

    return {
      map: map,
      refresh: refresh,
      focus: focus,
      locateUser: locateUser,
      clearUserLocation: clearUserLocation,
      stop: function () { clearInterval(timer); },
    };
  }

  return {
    getCookie: getCookie,
    getJSON: getJSON,
    postJSON: postJSON,
    deleteJSON: deleteJSON,
    escapeHtml: escapeHtml,
    fmtAge: fmtAge,
    fmtTime: fmtTime,
    fmtSpeed: fmtSpeed,
    haversineMeters: haversineMeters,
    fmtDistance: fmtDistance,
    tileLayer: tileLayer,
    statusOf: statusOf,
    markerIcon: markerIcon,
    userLocationIcon: userLocationIcon,
    startLiveMap: startLiveMap,
  };
})();
