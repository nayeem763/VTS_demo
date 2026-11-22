"use strict";
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (window.CSS && CSS.supports("animation-timeline: scroll()")) return;
  var root = document.documentElement, ticking = false;
  function update() {
    ticking = false;
    var max = Math.max(1, root.scrollHeight - window.innerHeight);
    var p = Math.min(1, Math.max(0, window.scrollY / max));
    root.style.setProperty("--aurora-p", p.toFixed(4));
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();
})();
