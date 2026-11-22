/* Admin live dashboard: same map engine, richer fields, focus selector,
   plus UI-only maximize/split-view, KPI counters, and roster filter controls. */
"use strict";
(function () {
  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  const vehicleListEl = document.getElementById("vehicle-list");
  const liveMap = VTS.startLiveMap(mapEl, {
    admin: true,
    listEl: vehicleListEl,
    focusSelect: document.getElementById("focus-select"),
    statusEl: document.getElementById("map-status"),
    routePlanner: {
      sourceInput: document.getElementById("route-source"),
      destinationInput: document.getElementById("route-destination"),
      drawButton: document.getElementById("draw-route"),
      clearButton: document.getElementById("clear-route"),
      statusEl: document.getElementById("route-status"),
    },
    routeManager: {
      form: document.getElementById("fixed-route-form"),
      nameInput: document.getElementById("new-route-name"),
      startInput: document.getElementById("new-route-start"),
      endInput: document.getElementById("new-route-end"),
      stopsEl: document.getElementById("new-route-stops"),
      addStopButton: document.getElementById("add-route-stop"),
      saveButton: document.getElementById("save-fixed-route"),
      statusEl: document.getElementById("fixed-route-status"),
      listEl: document.getElementById("fixed-route-list"),
      countEl: document.getElementById("route-count"),
      numberEl: document.getElementById("new-route-number"),
    },
  });

  const splitEl = document.getElementById("dashboard-split");
  const toggleBtn = document.getElementById("dashboard-expand-toggle");
  const filterInput = document.getElementById("dashboard-filter");
  const filterEmptyEl = document.getElementById("dashboard-filter-empty");
  const filterButtons = Array.from(document.querySelectorAll("[data-status-filter]"));
  const kpiTotal = document.getElementById("kpi-total");
  const kpiLive = document.getElementById("kpi-live");
  const kpiStale = document.getElementById("kpi-stale");
  const kpiOffline = document.getElementById("kpi-offline");
  let activeStatusFilter = "all";

  function syncDashboardUi() {
    if (!vehicleListEl) return;
    const items = Array.from(vehicleListEl.querySelectorAll(".vehicle-item"));
    let liveCount = 0;
    let staleCount = 0;
    let offlineCount = 0;
    let shownCount = 0;
    const isExpanded = !!(splitEl && splitEl.classList.contains("is-dashboard-expanded"));
    const query = isExpanded && filterInput ? filterInput.value.trim().toLowerCase() : "";
    const statusMode = isExpanded ? activeStatusFilter : "all";

    items.forEach(function (item) {
      const isLive = !!item.querySelector(".status-badge.is-live");
      const isStale = !!item.querySelector(".status-badge.is-stale");
      const status = isLive ? "live" : (isStale ? "stale" : "offline");
      if (status === "live") liveCount += 1;
      else if (status === "stale") staleCount += 1;
      else offlineCount += 1;

      const matchesStatus = statusMode === "all" || status === statusMode;
      const matchesQuery = !query || item.textContent.toLowerCase().includes(query);
      const visible = matchesStatus && matchesQuery;
      item.hidden = !visible;
      if (visible) shownCount += 1;
    });

    if (kpiTotal) kpiTotal.textContent = String(items.length);
    if (kpiLive) kpiLive.textContent = String(liveCount);
    if (kpiStale) kpiStale.textContent = String(staleCount);
    if (kpiOffline) kpiOffline.textContent = String(offlineCount);
    if (filterEmptyEl) {
      filterEmptyEl.style.display = isExpanded && items.length && !shownCount ? "block" : "none";
    }
  }

  function resetDashboardFilters() {
    activeStatusFilter = "all";
    if (filterInput) filterInput.value = "";
    filterButtons.forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.statusFilter === "all");
    });
    syncDashboardUi();
  }

  function setExpanded(expanded) {
    if (!splitEl || !toggleBtn) return;
    if (expanded) splitEl.classList.remove("is-side-collapsed");
    splitEl.classList.toggle("is-dashboard-expanded", expanded);
    document.documentElement.classList.toggle("vts-dashboard-maximized", expanded);
    toggleBtn.setAttribute("aria-pressed", String(expanded));
    toggleBtn.setAttribute(
      "aria-label",
      expanded ? "Minimize dashboard to show map and dashboard" : "Maximize dashboard to full screen"
    );
    toggleBtn.title = expanded ? "Show map and dashboard" : "Maximize dashboard";
    if (!expanded) {
      resetDashboardFilters();
      if (liveMap && liveMap.map) {
        window.requestAnimationFrame(function () {
          liveMap.map.invalidateSize({ animate: false });
        });
        window.setTimeout(function () {
          liveMap.map.invalidateSize({ animate: false });
        }, 200);
      }
    } else {
      syncDashboardUi();
    }
  }

  if (toggleBtn && splitEl) {
    toggleBtn.addEventListener("click", function () {
      setExpanded(!splitEl.classList.contains("is-dashboard-expanded"));
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      if (!splitEl.classList.contains("is-dashboard-expanded")) return;
      const tag = document.activeElement ? document.activeElement.tagName : "";
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      setExpanded(false);
    });
  }

  filterButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeStatusFilter = btn.dataset.statusFilter || "all";
      filterButtons.forEach(function (other) {
        other.classList.toggle("active", other === btn);
      });
      syncDashboardUi();
    });
  });

  if (filterInput) {
    filterInput.addEventListener("input", syncDashboardUi);
  }

  if (vehicleListEl) {
    new MutationObserver(syncDashboardUi).observe(vehicleListEl, { childList: true, subtree: true });
    syncDashboardUi();
  }
})();
