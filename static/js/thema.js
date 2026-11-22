/* CU-VTS theme switcher (light/dark) and small CSP-safe UI enhancements.
   Loaded in <head> so the saved theme is applied before first paint (no flash). */
"use strict";
(function () {
  var KEY = "vts-theme";
  var root = document.documentElement;

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function apply(theme) {
    root.setAttribute("data-vts-theme", theme);
    var button = document.getElementById("theme-toggle");
    if (button) {
      var isDark = theme === "dark";
      button.setAttribute("aria-pressed", String(isDark));
      button.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
    }
  }

  var initial = saved() ||
    (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  apply(initial);

  document.addEventListener("DOMContentLoaded", function () {
    apply(root.getAttribute("data-vts-theme") || "light");

    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        var next = root.getAttribute("data-vts-theme") === "dark" ? "light" : "dark";
        apply(next);
        try { localStorage.setItem(KEY, next); } catch (e) { /* private mode */ }
      });
    }

    document.querySelectorAll("[data-password-toggle]").forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        var field = toggle.closest(".vts-password-field");
        if (!field) return;
        var input = field.querySelector("input");
        if (!input) return;
        var reveal = input.type === "password";
        input.type = reveal ? "text" : "password";
        toggle.classList.toggle("is-visible", reveal);
        toggle.setAttribute("aria-pressed", String(reveal));
        toggle.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
      });
    });

    /* Google Maps-style collapsible right panel & vertical shortcut rail */
    var split = document.querySelector(".vts-split");
    if (split) {
      var toggles = Array.prototype.slice.call(split.querySelectorAll("[data-side-toggle]"));
      function notifyMapResize() {
        window.dispatchEvent(new Event("resize"));
        window.setTimeout(function () { window.dispatchEvent(new Event("resize")); }, 240);
      }
      function setSideCollapsed(collapsed) {
        if (collapsed) split.classList.remove("is-dashboard-expanded");
        split.classList.toggle("is-side-collapsed", collapsed);
        toggles.forEach(function (t) {
          t.setAttribute("aria-expanded", String(!collapsed));
          t.setAttribute("aria-label", collapsed ? "Expand side panel" : "Collapse side panel");
          t.title = collapsed ? "Expand panel" : "Collapse panel";
        });
        notifyMapResize();
      }
      toggles.forEach(function (t) {
        t.addEventListener("click", function () {
          setSideCollapsed(!split.classList.contains("is-side-collapsed"));
        });
      });

      var railOpenBtns = Array.prototype.slice.call(split.querySelectorAll("[data-rail-open]"));
      railOpenBtns.forEach(function (rb) {
        rb.addEventListener("click", function () {
          var target = rb.getAttribute("data-rail-open");
          railOpenBtns.forEach(function (b) { b.classList.toggle("is-active", b === rb); });
          setSideCollapsed(false);
          window.requestAnimationFrame(function () {
            if (target === "fleet") {
              var ft = document.getElementById("fleet-tab");
              if (ft) ft.click();
            } else if (target === "routes") {
              var rt = document.getElementById("routes-tab");
              if (rt) rt.click();
            } else if (target === "planner") {
              var ft2 = document.getElementById("fleet-tab");
              if (ft2) ft2.click();
              var rp = document.getElementById("route-planner");
              if (rp) {
                rp.open = true;
                var src = document.getElementById("route-source");
                if (src) src.focus();
              }
            } else if (target === "focus") {
              var ft3 = document.getElementById("fleet-tab");
              if (ft3) ft3.click();
              var sel = document.getElementById("focus-select");
              if (sel) sel.focus();
            } else if (target === "search") {
              var q = document.getElementById("vts-filter");
              if (q) q.focus();
            } else if (target === "filters") {
              var vs = document.getElementById("vehicle-select");
              if (vs) vs.focus();
            } else if (target === "playback") {
              var pf = split.querySelector(".vts-side-footer");
              if (pf && pf.scrollIntoView) pf.scrollIntoView({ behavior: "smooth", block: "end" });
            }
          });
        });
      });

      var railMax = split.querySelector("[data-rail-maximize]");
      if (railMax) {
        railMax.addEventListener("click", function () {
          setSideCollapsed(false);
          var maxBtn = document.getElementById("dashboard-expand-toggle");
          if (maxBtn && !split.classList.contains("is-dashboard-expanded")) maxBtn.click();
        });
      }
    }
  });
})();
