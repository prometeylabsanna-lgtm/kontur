(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(
      new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1") + "=([^;]*)")
    );
    return match ? decodeURIComponent(match[1]) : "";
  }

  function readUtm() {
    var params = new URLSearchParams(window.location.search);
    return {
      source: params.get("utm_source") || "",
      medium: params.get("utm_medium") || "",
      campaign: params.get("utm_campaign") || "",
    };
  }

  function applyUtmFields() {
    var utm = readUtm();
    setHidden("leadUtmSource", utm.source);
    setHidden("leadUtmMedium", utm.medium);
    setHidden("leadUtmCampaign", utm.campaign);
  }

  function trackLeadConversion() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "generate_lead",
      event_category: "lead",
      event_label: "lead_form",
    });
    if (typeof window.fbq === "function") {
      window.fbq("track", "Lead");
    }
  }

  var slides = document.querySelectorAll(".hero__slide");
  var dots = document.querySelectorAll("[data-hero-dot]");
  var heroIndex = 0;
  var heroTimer;

  function syncHeroMedia(activeIndex) {
    slides.forEach(function (el, n) {
      var video = el.querySelector("video");
      if (!video) return;
      if (n === activeIndex) {
        var playPromise = video.play();
        if (playPromise && typeof playPromise.catch === "function") {
          playPromise.catch(function () {});
        }
      } else {
        video.pause();
        try {
          video.currentTime = 0;
        } catch (e) {}
      }
    });
  }

  function goHero(i) {
    if (!slides.length) return;
    heroIndex = (i + slides.length) % slides.length;
    slides.forEach(function (el, n) {
      el.classList.toggle("is-active", n === heroIndex);
    });
    dots.forEach(function (el, n) {
      var on = n === heroIndex;
      el.classList.toggle("is-active", on);
      el.setAttribute("aria-pressed", on ? "true" : "false");
    });
    syncHeroMedia(heroIndex);
  }

  function startHero() {
    if (slides.length < 2) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    clearInterval(heroTimer);
    heroTimer = window.setInterval(function () {
      goHero(heroIndex + 1);
    }, 6500);
  }

  dots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      goHero(Number(dot.getAttribute("data-hero-dot")));
      startHero();
    });
  });
  syncHeroMedia(0);
  startHero();

  var nav = document.getElementById("navSheet");
  function openNav() {
    if (!nav) return;
    nav.hidden = false;
    nav.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function closeNav() {
    if (!nav) return;
    nav.classList.remove("is-open");
    nav.hidden = true;
    document.body.style.overflow = "";
  }
  document.querySelectorAll("[data-open-nav]").forEach(function (el) {
    el.addEventListener("click", openNav);
  });
  document.querySelectorAll("[data-close-nav]").forEach(function (el) {
    el.addEventListener("click", function () {
      closeNav();
    });
  });

  var modal = document.getElementById("leadModal");
  var modalCtx = document.getElementById("modalCtx");
  var modalDefault = document.getElementById("modalDefault");
  var modalSuccess = document.getElementById("modalSuccess");
  var form = document.getElementById("leadForm");
  var submitBtn = document.getElementById("submitBtn");
  var formError = document.getElementById("formError");

  function setHidden(id, value) {
    var el = document.getElementById(id);
    if (el) el.value = value == null ? "" : String(value);
  }

  function fillLeadMeta(trigger) {
    var ctx = (trigger && trigger.getAttribute("data-ctx")) || "Заявка";
    var pkg = (trigger && trigger.getAttribute("data-pkg")) || "";
    var fromCalc = trigger && trigger.id === "calcCta";
    var calc =
      window.KonturCalc && typeof window.KonturCalc.getState === "function"
        ? window.KonturCalc.getState()
        : null;
    var money =
      window.KonturCalc && typeof window.KonturCalc.formatMoney === "function"
        ? window.KonturCalc.formatMoney
        : function (n) {
            return Math.round(n).toLocaleString("uk-UA") + " $";
          };

    if (fromCalc && calc) {
      pkg = calc.obj === "flat" ? calc.pkg : "";
      setHidden(
        "leadObjectType",
        calc.obj === "house" ? "Будинок / Котедж" : "Квартира у новобудові"
      );
      setHidden("leadArea", calc.obj === "flat" ? calc.area : "");
      setHidden(
        "leadCalcSummary",
        calc.obj === "house"
          ? "Індивідуальний кошторис"
          : "Пакет " +
              calc.pkg +
              "; площа " +
              calc.area +
              " м²; ставка " +
              calc.rate +
              "; сума ~" +
              (calc.total != null ? money(calc.total) : "—")
      );
    } else {
      setHidden("leadObjectType", "");
      setHidden("leadArea", "");
      setHidden("leadCalcSummary", "");
    }

    setHidden("leadContext", ctx);
    setHidden("leadPackage", pkg);
    applyUtmFields();
    if (modalCtx) modalCtx.textContent = "Контекст: " + ctx;
  }

  function openModal(trigger) {
    if (!modal) return;
    fillLeadMeta(trigger || null);
    if (modalDefault) modalDefault.hidden = false;
    if (modalSuccess) modalSuccess.hidden = true;
    if (form) form.reset();
    fillLeadMeta(trigger || null);
    clearErrors();
    if (formError) formError.hidden = true;
    modal.hidden = false;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
    var nameInput = document.getElementById("name");
    if (nameInput) nameInput.focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.hidden = true;
    document.body.style.overflow = "";
  }

  document.querySelectorAll("[data-open-modal]").forEach(function (el) {
    el.addEventListener("click", function () {
      if (el.hasAttribute("data-close-nav")) closeNav();
      openModal(el);
    });
  });
  document.querySelectorAll("[data-close-modal]").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });

  function clearErrors() {
    ["fieldName", "fieldPhone"].forEach(function (id) {
      var f = document.getElementById(id);
      if (!f) return;
      f.classList.remove("field--error");
      var hint = f.querySelector(".field__hint");
      if (hint) hint.hidden = true;
    });
  }

  function uaPhone(v) {
    var d = String(v).replace(/\D/g, "");
    if (d.indexOf("380") === 0 && d.length === 12) return true;
    if (d.indexOf("0") === 0 && d.length === 10) return true;
    return false;
  }

  if (form) {
    applyUtmFields();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearErrors();
      if (formError) formError.hidden = true;
      applyUtmFields();

      var name = document.getElementById("name");
      var phone = document.getElementById("phone");
      var agree = document.getElementById("agree");
      var ok = true;

      if (!name.value.trim()) {
        document.getElementById("fieldName").classList.add("field--error");
        document.querySelector("#fieldName .field__hint").hidden = false;
        ok = false;
      }
      if (!uaPhone(phone.value)) {
        document.getElementById("fieldPhone").classList.add("field--error");
        document.querySelector("#fieldPhone .field__hint").hidden = false;
        ok = false;
      }
      if (!agree.checked) ok = false;
      if (!ok) {
        if (!agree.checked && formError) {
          formError.textContent = "Потрібна згода з політикою конфіденційності";
          formError.hidden = false;
        }
        return;
      }

      var csrf =
        (form.querySelector("[name=csrfmiddlewaretoken]") || {}).value ||
        getCookie("csrftoken");
      var body = new FormData(form);
      if (!body.get("agree")) body.set("agree", "true");

      submitBtn.disabled = true;
      submitBtn.textContent = "Надсилаємо…";

      fetch(form.action, {
        method: "POST",
        body: body,
        headers: {
          "X-CSRFToken": csrf,
          Accept: "application/json",
        },
        credentials: "same-origin",
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok || !result.data.ok) {
            var errors = (result.data && result.data.errors) || {};
            if (errors.name) {
              document.getElementById("fieldName").classList.add("field--error");
              document.querySelector("#fieldName .field__hint").hidden = false;
            }
            if (errors.phone) {
              document.getElementById("fieldPhone").classList.add("field--error");
              document.querySelector("#fieldPhone .field__hint").hidden = false;
            }
            if (formError) {
              formError.textContent = "Спробуйте ще раз";
              formError.hidden = false;
            }
            return;
          }
          trackLeadConversion();
          modalDefault.hidden = true;
          modalSuccess.hidden = false;
        })
        .catch(function () {
          if (formError) {
            formError.textContent = "Спробуйте ще раз";
            formError.hidden = false;
          }
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = "Надіслати";
        });
    });
  }

  function initAdvRail(root) {
    var track = root.querySelector("[data-adv-track]");
    var prev = root.querySelector("[data-adv-prev]");
    var next = root.querySelector("[data-adv-next]");
    if (!track || !prev || !next) return;

    var cachedStep = 0;
    var syncScheduled = false;

    function measureStep() {
      var card = track.querySelector(".adv-card");
      if (!card) {
        cachedStep = Math.round(track.clientWidth * 0.8);
        return cachedStep;
      }
      var styles = window.getComputedStyle(track);
      var gap = parseFloat(styles.columnGap || styles.gap) || 16;
      cachedStep = Math.round(card.getBoundingClientRect().width + gap);
      return cachedStep;
    }

    function sync() {
      var max = track.scrollWidth - track.clientWidth;
      var x = track.scrollLeft;
      prev.disabled = x <= 2;
      next.disabled = x >= max - 2;
    }

    function scheduleSync() {
      if (syncScheduled) return;
      syncScheduled = true;
      window.requestAnimationFrame(function () {
        syncScheduled = false;
        sync();
      });
    }

    function go(dir) {
      if (!cachedStep) measureStep();
      track.scrollBy({ left: dir * cachedStep, behavior: "smooth" });
    }

    prev.addEventListener("click", function () {
      go(-1);
    });
    next.addEventListener("click", function () {
      go(1);
    });
    track.addEventListener("scroll", scheduleSync, { passive: true });
    window.addEventListener(
      "resize",
      function () {
        measureStep();
        scheduleSync();
      },
      { passive: true }
    );
    measureStep();
    sync();
  }

  document.querySelectorAll("[data-adv-rail]").forEach(initAdvRail);

  function initReviewsRail(root) {
    var track = root.querySelector("[data-reviews-track]");
    var prev = root.querySelector("[data-reviews-prev]");
    var next = root.querySelector("[data-reviews-next]");
    if (!track || !prev || !next) return;

    var cachedStep = 0;
    var syncScheduled = false;

    function measureStep() {
      var card = track.querySelector(".review");
      if (!card) {
        cachedStep = Math.round(track.clientWidth * 0.8);
        return cachedStep;
      }
      var styles = window.getComputedStyle(track);
      var gap = parseFloat(styles.columnGap || styles.gap) || 16;
      cachedStep = Math.round(card.getBoundingClientRect().width + gap);
      return cachedStep;
    }

    function sync() {
      var max = track.scrollWidth - track.clientWidth;
      var x = track.scrollLeft;
      var canScroll = max > 4;
      prev.disabled = !canScroll || x <= 2;
      next.disabled = !canScroll || x >= max - 2;
    }

    function scheduleSync() {
      if (syncScheduled) return;
      syncScheduled = true;
      window.requestAnimationFrame(function () {
        syncScheduled = false;
        sync();
      });
    }

    function go(dir) {
      if (!cachedStep) measureStep();
      track.scrollBy({ left: dir * cachedStep, behavior: "smooth" });
    }

    prev.addEventListener("click", function () {
      go(-1);
    });
    next.addEventListener("click", function () {
      go(1);
    });
    track.addEventListener("scroll", scheduleSync, { passive: true });
    window.addEventListener(
      "resize",
      function () {
        measureStep();
        scheduleSync();
      },
      { passive: true }
    );
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(function () {
        measureStep();
        scheduleSync();
      }).observe(track);
    }
    measureStep();
    sync();
  }

  document.querySelectorAll("[data-reviews-rail]").forEach(initReviewsRail);

  document.querySelectorAll("[data-google-reviews]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      var href = link.getAttribute("href");
      if (!href || href === "#") e.preventDefault();
    });
  });

  document.querySelectorAll(".accordion__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.parentElement;
      var open = item.classList.contains("is-open");
      document.querySelectorAll(".accordion__item").forEach(function (i) {
        i.classList.remove("is-open");
        var b = i.querySelector(".accordion__btn");
        if (b) b.setAttribute("aria-expanded", "false");
      });
      if (!open) {
        item.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });
})();
