(function () {
  "use strict";

  var state = {
    obj: "flat",
    rate: 580,
    pkg: "Оптимальний",
    area: 62,
    total: null,
  };

  function getCookie(name) {
    var match = document.cookie.match(
      new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1") + "=([^;]*)")
    );
    return match ? decodeURIComponent(match[1]) : "";
  }

  function coef(area) {
    if (area <= 30) return 1.4;
    if (area <= 34) return 1.25;
    if (area <= 39) return 1.1;
    return 1;
  }

  function formatMoney(n) {
    return Math.round(n).toLocaleString("uk-UA") + " $";
  }

  var calcDockApply = null;

  function recalc() {
    var out = document.getElementById("calcOut");
    var sumEl = document.getElementById("calcSum");
    var note = document.getElementById("calcNote");
    var pay = document.getElementById("payGrid");
    var cta = document.getElementById("calcCta");
    var flatFields = document.getElementById("calcFlatFields");
    if (!out) return;

    if (state.obj === "house") {
      out.classList.add("calc-out--custom");
      flatFields.hidden = true;
      sumEl.textContent = "";
      note.textContent =
        "Для будинку / котеджу потрібен індивідуальний кошторис після обміру.";
      pay.hidden = true;
      state.total = null;
      cta.textContent = "Залишити заявку на кошторис";
      cta.setAttribute("data-ctx", "Калькулятор: Будинок / Котедж");
      if (calcDockApply) window.requestAnimationFrame(calcDockApply);
      return;
    }

    out.classList.remove("calc-out--custom");
    flatFields.hidden = false;
    pay.hidden = false;
    cta.textContent = "Отримати точний розрахунок";

    var k = coef(state.area);
    var billable = Math.max(state.area, 40);
    var total = state.rate * k * billable;
    state.total = total;
    sumEl.textContent = formatMoney(total);
    note.textContent =
      "Ефективна ставка " +
      Math.round(state.rate * k) +
      " $/м² · розрахункова площа " +
      billable +
      " м². Точна ціна — після заміру.";
    document.getElementById("p1").textContent = formatMoney(total * 0.3);
    document.getElementById("p2").textContent = formatMoney(total * 0.3);
    document.getElementById("p3").textContent = formatMoney(total * 0.3);
    document.getElementById("p4").textContent = formatMoney(total * 0.1);
    cta.setAttribute(
      "data-ctx",
      "Калькулятор: " + state.pkg + ", " + state.area + " м², ~" + formatMoney(total)
    );
    if (calcDockApply) window.requestAnimationFrame(calcDockApply);
  }

  document.querySelectorAll("[data-obj]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll("[data-obj]").forEach(function (b) {
        b.classList.remove("is-active");
      });
      btn.classList.add("is-active");
      state.obj = btn.getAttribute("data-obj");
      recalc();
    });
  });

  document.querySelectorAll(".calc-panel__pkg").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".calc-panel__pkg").forEach(function (b) {
        b.classList.remove("is-active");
      });
      btn.classList.add("is-active");
      state.rate = Number(btn.getAttribute("data-rate"));
      state.pkg = btn.getAttribute("data-pkg-name");
      recalc();
    });
  });

  var range = document.getElementById("areaRange");
  var num = document.getElementById("areaNum");
  function setArea(v) {
    v = Math.min(150, Math.max(20, Number(v) || 20));
    state.area = v;
    if (range) range.value = v;
    if (num) num.value = v;
    recalc();
  }
  if (range) {
    range.addEventListener("input", function () {
      setArea(range.value);
    });
  }
  if (num) {
    num.addEventListener("change", function () {
      setArea(num.value);
    });
  }

  var slides = document.querySelectorAll(".hero__slide");
  var dots = document.querySelectorAll("[data-hero-dot]");
  var heroIndex = 0;
  var heroTimer;

  function goHero(i) {
    if (!slides.length) return;
    heroIndex = (i + slides.length) % slides.length;
    slides.forEach(function (el, n) {
      el.classList.toggle("is-active", n === heroIndex);
    });
    dots.forEach(function (el, n) {
      el.classList.toggle("is-active", n === heroIndex);
    });
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

    if (fromCalc) {
      pkg = state.obj === "flat" ? state.pkg : "";
      setHidden(
        "leadObjectType",
        state.obj === "house" ? "Будинок / Котедж" : "Квартира у новобудові"
      );
      setHidden("leadArea", state.obj === "flat" ? state.area : "");
      setHidden(
        "leadCalcSummary",
        state.obj === "house"
          ? "Індивідуальний кошторис"
          : "Пакет " +
              state.pkg +
              "; площа " +
              state.area +
              " м²; ставка " +
              state.rate +
              "; сума ~" +
              (state.total != null ? formatMoney(state.total) : "—")
      );
    } else {
      setHidden("leadObjectType", "");
      setHidden("leadArea", "");
      setHidden("leadCalcSummary", "");
    }

    setHidden("leadContext", ctx);
    setHidden("leadPackage", pkg);
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
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearErrors();
      if (formError) formError.hidden = true;

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

    function step() {
      var card = track.querySelector(".adv-card");
      if (!card) return Math.round(track.clientWidth * 0.8);
      var styles = window.getComputedStyle(track);
      var gap = parseFloat(styles.columnGap || styles.gap) || 16;
      return Math.round(card.getBoundingClientRect().width + gap);
    }

    function sync() {
      var max = track.scrollWidth - track.clientWidth;
      var x = track.scrollLeft;
      prev.disabled = x <= 2;
      next.disabled = x >= max - 2;
    }

    function go(dir) {
      track.scrollBy({ left: dir * step(), behavior: "smooth" });
    }

    prev.addEventListener("click", function () {
      go(-1);
    });
    next.addEventListener("click", function () {
      go(1);
    });
    track.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
    sync();
  }

  document.querySelectorAll("[data-adv-rail]").forEach(initAdvRail);

  function initReviewsRail(root) {
    var track = root.querySelector("[data-reviews-track]");
    var prev = root.querySelector("[data-reviews-prev]");
    var next = root.querySelector("[data-reviews-next]");
    if (!track || !prev || !next) return;

    function step() {
      var card = track.querySelector(".review");
      if (!card) return Math.round(track.clientWidth * 0.8);
      var styles = window.getComputedStyle(track);
      var gap = parseFloat(styles.columnGap || styles.gap) || 16;
      return Math.round(card.getBoundingClientRect().width + gap);
    }

    function sync() {
      var max = track.scrollWidth - track.clientWidth;
      var x = track.scrollLeft;
      var canScroll = max > 4;
      prev.disabled = !canScroll || x <= 2;
      next.disabled = !canScroll || x >= max - 2;
    }

    function go(dir) {
      track.scrollBy({ left: dir * step(), behavior: "smooth" });
    }

    prev.addEventListener("click", function () {
      go(-1);
    });
    next.addEventListener("click", function () {
      go(1);
    });
    track.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(sync).observe(track);
    }
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

  (function initCalcDock() {
    var section = document.getElementById("calculator");
    var shell = section && section.querySelector(".calc-shell");
    var dock = section && section.querySelector(".calc-panel--dark");
    if (!section || !shell || !dock) return;

    var mq = window.matchMedia("(max-width: 767.98px)");
    var visible = false;

    function apply() {
      var on = mq.matches && visible;
      dock.classList.toggle("is-docked", on);
      shell.classList.toggle("is-dock-pad", on);
      if (on) {
        shell.style.setProperty(
          "--calc-dock-h",
          Math.ceil(dock.getBoundingClientRect().height) + "px"
        );
      } else {
        shell.style.removeProperty("--calc-dock-h");
      }
    }

    calcDockApply = apply;

    if (typeof IntersectionObserver !== "undefined") {
      var io = new IntersectionObserver(
        function (entries) {
          visible = entries.some(function (e) {
            return e.isIntersecting;
          });
          apply();
        },
        { threshold: 0.08, rootMargin: "0px" }
      );
      io.observe(section);
    }

    function onMq() {
      apply();
    }
    if (mq.addEventListener) mq.addEventListener("change", onMq);
    else if (mq.addListener) mq.addListener(onMq);

    window.addEventListener(
      "resize",
      function () {
        if (dock.classList.contains("is-docked")) apply();
      },
      { passive: true }
    );
  })();

  recalc();
})();
