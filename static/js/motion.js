/* Kontur+ motion — header scroll + IntersectionObserver reveal */
(function () {
  "use strict";

  var header = document.getElementById("siteHeader");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  var nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;

  var reduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function settle(el) {
    el.classList.add("is-inview", "is-settled");
  }

  function show(el) {
    el.classList.add("is-inview");
    el.addEventListener(
      "animationend",
      function (e) {
        if (String(e.animationName || "").indexOf("kp-reveal") !== 0) return;
        el.classList.add("is-settled");
      },
      { once: true }
    );
  }

  function showAll() {
    for (var i = 0; i < nodes.length; i++) {
      settle(nodes[i]);
    }
  }

  if (reduce || !("IntersectionObserver" in window)) {
    showAll();
    return;
  }

  var io = new IntersectionObserver(
    function (entries) {
      for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (!entry.isIntersecting) continue;
        show(entry.target);
        io.unobserve(entry.target);
      }
    },
    {
      root: null,
      rootMargin: "0px 0px -8% 0px",
      threshold: 0.14,
    }
  );

  for (var n = 0; n < nodes.length; n++) {
    io.observe(nodes[n]);
  }
})();
