/* Driver tracker. Watches GPS, buffers the latest fix, and POSTs it on a
   fixed cadence with an idempotent client_event_id so retries never double
   count. The server derives vehicle/driver/trip from the session. */
"use strict";
(function () {
  const root = document.getElementById("tracker");
  if (!root) return; // no active assignment -> nothing to wire up

  const endpoint = root.dataset.endpoint;
  const intervalMs = parseInt(root.dataset.interval || "5000", 10);

  const els = {
    toggle: document.getElementById("toggle-btn"),
    state: document.getElementById("tracker-state"),
    card: document.getElementById("status-card"),
    lastSent: document.getElementById("last-sent"),
    accuracy: document.getElementById("accuracy"),
    coords: document.getElementById("coords"),
    speed: document.getElementById("speed"),
    error: document.getElementById("tracker-error"),
    count: document.getElementById("sent-count"),
  };

  let enabled = false;
  let watchId = null;
  let timer = null;
  let lastPosition = null; // freshest GeolocationPosition
  let pending = null;      // { payload } awaiting successful send
  let sentCount = 0;
  let wakeLock = null;

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    // RFC4122 v4 fallback using getRandomValues.
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    const h = Array.from(b, function (x) { return x.toString(16).padStart(2, "0"); });
    return h[0] + h[1] + h[2] + h[3] + "-" + h[4] + h[5] + "-" + h[6] + h[7] + "-" + h[8] + h[9] + "-" + h[10] + h[11] + h[12] + h[13] + h[14] + h[15];
  }

  function round(value, places) {
    if (value == null || isNaN(value)) return null;
    return Number(value.toFixed(places));
  }

  function setError(msg) {
    if (!els.error) return;
    els.error.textContent = msg || "";
    els.error.classList.toggle("d-none", !msg);
  }

  function setState(text, live) {
    if (els.state) els.state.textContent = text;
    if (els.card) els.card.classList.toggle("pulse-live", !!live);
  }

  async function requestWakeLock() {
    try {
      if ("wakeLock" in navigator) wakeLock = await navigator.wakeLock.request("screen");
    } catch (e) {
      /* wake lock is best-effort */
    }
  }
  function releaseWakeLock() {
    if (wakeLock) { wakeLock.release().catch(function () {}); wakeLock = null; }
  }

  function buildPayload(position) {
    const c = position.coords;
    const speedKmh = c.speed != null && c.speed >= 0 ? round(c.speed * 3.6, 2) : null;
    return {
      client_event_id: uuid(),
      latitude: round(c.latitude, 6),
      longitude: round(c.longitude, 6),
      speed_kmh: speedKmh,
      accuracy_m: c.accuracy != null ? round(c.accuracy, 2) : null,
      captured_at: new Date(position.timestamp).toISOString(),
    };
  }

  function onPosition(position) {
    lastPosition = position;
    const c = position.coords;
    if (els.coords) els.coords.textContent = c.latitude.toFixed(5) + ", " + c.longitude.toFixed(5);
    if (els.accuracy) els.accuracy.textContent = c.accuracy != null ? "± " + Math.round(c.accuracy) + " m" : "—";
    if (els.speed) els.speed.textContent = c.speed != null && c.speed >= 0 ? Math.round(c.speed * 3.6) + " km/h" : "—";
    setError("");
  }

  function onGeoError(err) {
    if (err.code === err.PERMISSION_DENIED) {
      setError("Location permission denied. Enable it in your browser settings, then start again.");
      stop();
    } else if (err.code === err.POSITION_UNAVAILABLE) {
      setError("Location unavailable right now — searching for signal…");
    } else if (err.code === err.TIMEOUT) {
      setError("Still acquiring GPS…");
    }
  }

  async function tick() {
    if (!enabled) return;
    if (!pending) {
      if (!lastPosition) { setState("Waiting for GPS…", true); return; }
      pending = { payload: buildPayload(lastPosition) };
    }
    try {
      const res = await VTS.postJSON(endpoint, pending.payload);
      pending = null;
      if (res && !res.duplicate) sentCount += 1;
      if (els.count) els.count.textContent = String(sentCount);
      if (els.lastSent) els.lastSent.textContent = VTS.fmtTime(new Date().toISOString());
      setState("Sharing location", true);
      setError("");
    } catch (e) {
      if (e.status === 403) {
        setError("You have no active vehicle assignment. Contact an administrator.");
        stop();
      } else if (e.status === 409) {
        setError("Your assigned vehicle is inactive. Contact an administrator.");
        stop();
      } else if (e.status === 400) {
        // Bad fix (e.g. clock skew). Drop it and continue with the next one.
        pending = null;
        setError("A GPS reading was rejected; continuing…");
      } else if (e.status === 429) {
        setError("Sending too fast — easing off briefly…");
      } else {
        setError("Network issue — will retry.");
      }
    }
  }

  function start() {
    if (enabled) return;
    if (!("geolocation" in navigator)) {
      setError("This device/browser does not support location sharing.");
      return;
    }
    enabled = true;
    sentCount = 0;
    if (els.count) els.count.textContent = "0";
    setState("Starting…", true);
    setButton();
    requestWakeLock();
    watchId = navigator.geolocation.watchPosition(onPosition, onGeoError, {
      enableHighAccuracy: true,
      maximumAge: 4000,
      timeout: 15000,
    });
    timer = setInterval(tick, intervalMs);
    tick();
  }

  function stop() {
    enabled = false;
    if (watchId != null) { navigator.geolocation.clearWatch(watchId); watchId = null; }
    if (timer != null) { clearInterval(timer); timer = null; }
    pending = null;
    releaseWakeLock();
    setState("Not sharing", false);
    setButton();
  }

  function setButton() {
    if (!els.toggle) return;
    if (enabled) {
      els.toggle.textContent = "Stop sharing";
      els.toggle.classList.remove("btn-success");
      els.toggle.classList.add("btn-danger");
    } else {
      els.toggle.textContent = "Start sharing";
      els.toggle.classList.remove("btn-danger");
      els.toggle.classList.add("btn-success");
    }
  }

  if (els.toggle) {
    els.toggle.addEventListener("click", function () {
      if (enabled) stop();
      else start();
    });
  }

  // Re-acquire the wake lock when returning to the tab while sharing.
  document.addEventListener("visibilitychange", function () {
    if (enabled && document.visibilityState === "visible") requestWakeLock();
  });

  // Best-effort: stop cleanly if the page is being unloaded.
  window.addEventListener("pagehide", function () { releaseWakeLock(); });

  setButton();
  setState("Not sharing", false);
})();
