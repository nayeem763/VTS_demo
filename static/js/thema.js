/* CU-VTS theme switcher (light/dark). Loaded in <head> so the saved theme is
   applied before first paint (no flash). External file => CSP-safe. */
"use strict";
(function () {
  var KEY = "vts-theme";
  var root = document.documentElement;

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function apply(theme) {
    root.setAttribute("data-bs-theme", theme);
    var icon = document.getElementById("theme-toggle-icon");
    if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  var initial = saved() ||
    (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  apply(initial);

  document.addEventListener("DOMContentLoaded", function () {
    apply(root.getAttribute("data-bs-theme") || "light");
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* private mode */ }
    });
  });
})();