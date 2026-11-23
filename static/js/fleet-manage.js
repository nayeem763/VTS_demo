/* CU-VTS Fleet Management UI controller (CSP-safe, zero dependencies).
   Handles vehicle/driver table filters, modal pre-filling, live admin-only
   vehicle note previews, and reassignment conflict warnings. */
"use strict";
(function () {
  /* Use the same eye-soothing 2-tone cartographic luminance as maximized dashboard */
  document.documentElement.classList.add("vts-dashboard-maximized");

  function setupFilterTable(rowSelector, filterAttr, searchInputId, emptyId) {
    const rows = Array.from(document.querySelectorAll(rowSelector));
    const filterButtons = Array.from(document.querySelectorAll("[" + filterAttr + "]"));
    const searchInput = document.getElementById(searchInputId);
    const emptyEl = document.getElementById(emptyId);
    if (!rows.length && !filterButtons.length) return;

    let activeFilter = "all";

    function apply() {
      const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
      let visible = 0;
      rows.forEach(function (row) {
        const status = row.dataset.status || "";
        const hay = row.dataset.search || "";
        const matchStatus = activeFilter === "all" || status === activeFilter;
        const matchQuery = !query || hay.indexOf(query) !== -1;
        const show = matchStatus && matchQuery;
        row.classList.toggle("d-none", !show);
        if (show) visible += 1;
      });
      if (emptyEl) emptyEl.classList.toggle("d-none", !(rows.length && visible === 0));
    }

    filterButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeFilter = btn.getAttribute(filterAttr) || "all";
        filterButtons.forEach(function (b) { b.classList.toggle("active", b === btn); });
        apply();
      });
    });

    if (searchInput) searchInput.addEventListener("input", apply);
  }

  function updateCharCounter(inputEl) {
    if (!inputEl || !inputEl.id) return;
    const counter = document.querySelector('[data-char-count-for="' + inputEl.id + '"]');
    if (!counter) return;
    const maxLen = inputEl.getAttribute("maxlength") || "280";
    counter.textContent = String((inputEl.value || "").length) + " / " + maxLen;
  }

  function setupAssignForm(formEl) {
    const vehicleSel = formEl.querySelector("[data-assign-vehicle]");
    const driverSel = formEl.querySelector("[data-assign-driver]");
    const briefBox = formEl.querySelector("[data-vehicle-brief]");
    const briefMeta = formEl.querySelector("[data-brief-meta]");
    const briefNote = formEl.querySelector("[data-brief-note]");
    const warningEl = formEl.querySelector("[data-assign-warning]");

    function sync() {
      const vOpt = vehicleSel && vehicleSel.selectedIndex >= 0 ? vehicleSel.options[vehicleSel.selectedIndex] : null;
      const dOpt = driverSel && driverSel.selectedIndex >= 0 ? driverSel.options[driverSel.selectedIndex] : null;
      const hasVehicle = !!(vOpt && vOpt.value);
      const hasDriver = !!(dOpt && dOpt.value);

      if (briefBox && briefNote) {
        if (hasVehicle) {
          const note = (vOpt.dataset.adminDescription || "").trim();
          const metaParts = [];
          if (vOpt.dataset.route) metaParts.push(vOpt.dataset.route);
          if (vOpt.dataset.registration) metaParts.push(vOpt.dataset.registration);
          if (briefMeta) briefMeta.textContent = metaParts.join(" · ");
          briefNote.textContent = note || "No admin-only note recorded for this vehicle yet (you can add one via Edit / Rename).";
          briefNote.classList.toggle("text-muted", !note);
          briefBox.classList.remove("d-none");
        } else {
          briefBox.classList.add("d-none");
        }
      }

      if (warningEl) {
        const notices = [];
        if (hasVehicle && hasDriver) {
          const curDriverId = vOpt.dataset.currentDriverId || "";
          const curDriverName = vOpt.dataset.currentDriverName || "";
          const curVehicleId = dOpt.dataset.currentVehicleId || "";
          const curVehicleName = dOpt.dataset.currentVehicleName || "";
          const busName = vOpt.dataset.busNumber || "this vehicle";
          const drvName = dOpt.dataset.driverName || "this driver";

          if (curDriverId && curDriverId === dOpt.value) {
            notices.push(drvName + " is already assigned to " + busName + ".");
          } else {
            if (curDriverId && curDriverName) {
              notices.push(
                busName + " is currently assigned to " + curDriverName +
                " — confirming will end that assignment and close any open trip."
              );
            }
            if (curVehicleId && curVehicleName && curVehicleId !== vOpt.value) {
              notices.push(
                drvName + " is currently driving " + curVehicleName +
                " — confirming will switch them to " + busName + " and close any open trip."
              );
            }
          }
        }
        warningEl.textContent = notices.join(" ");
        warningEl.classList.toggle("d-none", notices.length === 0);
      }
    }

    if (vehicleSel) vehicleSel.addEventListener("change", sync);
    if (driverSel) driverSel.addEventListener("change", sync);
    formEl._syncAssignPreview = sync;
    sync();
  }

  /* Wire filters */
  setupFilterTable("[data-vehicle-row]", "data-vehicle-filter", "fleet-vehicle-search", "fleet-vehicles-empty");
  setupFilterTable("[data-driver-row]", "data-driver-filter", "fleet-driver-search", "fleet-drivers-empty");

  /* Wire character counters */
  document.querySelectorAll("[data-char-count-for]").forEach(function (el) {
    const target = document.getElementById(el.getAttribute("data-char-count-for"));
    if (!target) return;
    target.addEventListener("input", function () { updateCharCounter(target); });
    updateCharCounter(target);
  });

  /* Wire assign forms (inline + modal) */
  document.querySelectorAll("[data-assign-form]").forEach(setupAssignForm);

  /* Populate Edit / Rename Vehicle modal */
  document.querySelectorAll("[data-edit-vehicle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const form = document.getElementById("vehicle-edit-form");
      const busInput = document.getElementById("edit-bus-number");
      const regInput = document.getElementById("edit-reg");
      const routeInput = document.getElementById("edit-route");
      const descInput = document.getElementById("edit-admin-desc");
      if (form) form.action = btn.dataset.action || "";
      if (busInput) busInput.value = btn.dataset.busNumber || "";
      if (regInput) regInput.value = btn.dataset.registration || "";
      if (routeInput) routeInput.value = btn.dataset.routeLabel || "";
      if (descInput) {
        descInput.value = btn.dataset.adminDescription || "";
        updateCharCounter(descInput);
      }
    });
  });

  /* Populate Assign / Reassign modal */
  document.querySelectorAll("[data-open-assign]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const form = document.getElementById("modal-assign-form");
      const vSel = document.getElementById("modal-assign-vehicle");
      const dSel = document.getElementById("modal-assign-driver");
      const tabInput = document.getElementById("modal-assign-return-tab");
      if (vSel) vSel.value = btn.dataset.vehicleId || "";
      if (dSel) dSel.value = btn.dataset.driverId || "";
      if (tabInput && btn.dataset.returnTab) tabInput.value = btn.dataset.returnTab;
      if (form && typeof form._syncAssignPreview === "function") {
        form._syncAssignPreview();
      }
    });
  });

  /* Populate Edit Driver modal */
  document.querySelectorAll("[data-edit-driver]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const form = document.getElementById("driver-edit-form");
      const label = document.getElementById("driver-edit-username-label");
      const firstInput = document.getElementById("driver-edit-first");
      const lastInput = document.getElementById("driver-edit-last");
      const empInput = document.getElementById("driver-edit-empid");
      const phoneInput = document.getElementById("driver-edit-phone");
      const passInput = document.getElementById("driver-edit-password");
      if (form) form.action = btn.dataset.action || "";
      if (label) label.textContent = "@" + (btn.dataset.username || "");
      if (firstInput) firstInput.value = btn.dataset.firstName || "";
      if (lastInput) lastInput.value = btn.dataset.lastName || "";
      if (empInput) empInput.value = btn.dataset.employeeId || "";
      if (phoneInput) phoneInput.value = btn.dataset.phone || "";
      if (passInput) passInput.value = "";
    });
  });

  /* Confirm destructive delete forms without inline JS */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      const msg = form.getAttribute("data-confirm");
      if (msg && !window.confirm(msg)) {
        event.preventDefault();
      }
    });
  });
})();
