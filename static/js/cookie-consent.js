(function () {
  "use strict";

  var STORAGE_KEY = "kontur_cookie_consent";
  var CHOICE_ALL = "all";
  var CHOICE_NECESSARY = "necessary";
  var root = document.getElementById("cookie-consent");

  if (!root) return;

  function readChoice() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (err) {
      return null;
    }
  }

  function writeChoice(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (err) {
      /* private mode / blocked storage */
    }
  }

  function hideBanner() {
    root.classList.remove("is-visible");
    root.setAttribute("hidden", "");
  }

  function showBanner() {
    root.removeAttribute("hidden");
    root.classList.add("is-visible");
  }

  function injectScript(src, attrs) {
    var existing = document.querySelector('script[src="' + src + '"]');
    if (existing) return;
    var el = document.createElement("script");
    el.src = src;
    el.async = true;
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        el.setAttribute(key, attrs[key]);
      });
    }
    document.head.appendChild(el);
  }

  function loadGtm(id) {
    if (!id || window.__konturGtmLoaded) return;
    window.__konturGtmLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      "gtm.start": new Date().getTime(),
      event: "gtm.js",
    });
    injectScript(
      "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(id),
      { "data-cookieconsent": "marketing" }
    );
  }

  function loadMetaPixel(id) {
    if (!id || window.__konturMetaLoaded) return;
    window.__konturMetaLoaded = true;
    if (!window.fbq) {
      var n = function () {
        n.callMethod
          ? n.callMethod.apply(n, arguments)
          : n.queue.push(arguments);
      };
      n.push = n;
      n.loaded = true;
      n.version = "2.0";
      n.queue = [];
      window.fbq = n;
      window._fbq = n;
    }
    injectScript("https://connect.facebook.net/en_US/fbevents.js", {
      "data-cookieconsent": "marketing",
    });
    window.fbq("init", id);
    window.fbq("track", "PageView");
  }

  function loadAnalytics() {
    var gtmId = (root.getAttribute("data-gtm-id") || "").trim();
    var metaId = (root.getAttribute("data-meta-pixel-id") || "").trim();
    if (gtmId) loadGtm(gtmId);
    if (metaId) loadMetaPixel(metaId);
  }

  function applyChoice(choice) {
    writeChoice(choice);
    hideBanner();
    if (choice === CHOICE_ALL) {
      loadAnalytics();
    }
  }

  var saved = readChoice();
  if (saved === CHOICE_ALL) {
    loadAnalytics();
  } else if (saved === CHOICE_NECESSARY) {
    /* no marketing scripts */
  } else {
    showBanner();
  }

  root.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-cookie-choice]");
    if (!btn || !root.contains(btn)) return;
    var choice = btn.getAttribute("data-cookie-choice");
    if (choice === CHOICE_ALL || choice === CHOICE_NECESSARY) {
      applyChoice(choice);
    }
  });
})();
