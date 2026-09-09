(function () {
  "use strict";

  function readConfig() {
    var el = document.getElementById("calc-config");
    var defaults = {
      areaMin: 20,
      areaMax: 150,
      billableMin: 40,
      coefTo30: 1.4,
      coef3134: 1.25,
      coef3539: 1.1,
      pay1: 0.3,
      pay2: 0.3,
      pay3: 0.3,
      pay4: 0.1,
    };
    if (!el) return defaults;
    try {
      return Object.assign(defaults, JSON.parse(el.textContent || "{}"));
    } catch (e) {
      return defaults;
    }
  }

  var cfg = readConfig();
  var recBtn = document.querySelector(".calc-panel__pkg.is-active, .calc-panel__pkg[data-rec]");
  var state = {
    obj: "flat",
    rate: recBtn ? Number(recBtn.getAttribute("data-rate")) || 580 : 580,
    pkg: recBtn ? recBtn.getAttribute("data-pkg-name") || "Оптимальний" : "Оптимальний",
    area: 62,
    total: null,
  };

  function pctLabel(share, suffix) {
    var p = Math.round(Number(share) * 100);
    return p + "% · " + suffix;
  }

  function coef(area) {
    if (area <= 30) return cfg.coefTo30;
    if (area <= 34) return cfg.coef3134;
    if (area <= 39) return cfg.coef3539;
    return 1;
  }

  function formatMoney(n) {
    return Math.round(n).toLocaleString("uk-UA") + " $";
  }

  function recalc() {
    var out = document.getElementById("calcOut");
    var sumEl = document.getElementById("calcSum");
    var note = document.getElementById("calcNote");
    var pay = document.getElementById("payGrid");
    var cta = document.getElementById("calcCta");
    var flatFields = document.getElementById("calcFlatFields");
    if (!out) return;

    var p1Label = document.getElementById("p1Label");
    var p2Label = document.getElementById("p2Label");
    var p3Label = document.getElementById("p3Label");
    var p4Label = document.getElementById("p4Label");
    if (p1Label) p1Label.textContent = pctLabel(cfg.pay1, "договір");
    if (p2Label) p2Label.textContent = pctLabel(cfg.pay2, "матеріали");
    if (p3Label) p3Label.textContent = pctLabel(cfg.pay3, "75% робіт");
    if (p4Label) p4Label.textContent = pctLabel(cfg.pay4, "акт");

    if (state.obj === "house") {
      out.classList.add("calc-out--custom");
      if (flatFields) flatFields.hidden = true;
      if (sumEl) sumEl.textContent = "";
      if (note) {
        note.textContent =
          "Для будинку / котеджу потрібен індивідуальний кошторис після обміру.";
      }
      if (pay) pay.hidden = true;
      state.total = null;
      if (cta) {
        cta.textContent = "Залишити заявку на кошторис";
        cta.setAttribute("data-ctx", "Калькулятор: Будинок / Котедж");
      }
      return;
    }

    out.classList.remove("calc-out--custom");
    if (flatFields) flatFields.hidden = false;
    if (pay) pay.hidden = false;
    if (cta) cta.textContent = "Отримати точний розрахунок";

    var k = coef(state.area);
    var billable = Math.max(state.area, cfg.billableMin);
    var total = state.rate * k * billable;
    state.total = total;
    if (sumEl) sumEl.textContent = formatMoney(total);
    if (note) {
      note.textContent =
        "Ефективна ставка " +
        Math.round(state.rate * k) +
        " $/м² · розрахункова площа " +
        billable +
        " м². Точна ціна — після заміру.";
    }
    var p1 = document.getElementById("p1");
    var p2 = document.getElementById("p2");
    var p3 = document.getElementById("p3");
    var p4 = document.getElementById("p4");
    if (p1) p1.textContent = formatMoney(total * cfg.pay1);
    if (p2) p2.textContent = formatMoney(total * cfg.pay2);
    if (p3) p3.textContent = formatMoney(total * cfg.pay3);
    if (p4) p4.textContent = formatMoney(total * cfg.pay4);
    if (cta) {
      cta.setAttribute(
        "data-ctx",
        "Калькулятор: " + state.pkg + ", " + state.area + " м², ~" + formatMoney(total)
      );
    }
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
    v = Math.min(cfg.areaMax, Math.max(cfg.areaMin, Number(v) || cfg.areaMin));
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

  if (range || num) {
    var initial = Number((range && range.value) || (num && num.value) || 62);
    setArea(initial);
  } else {
    recalc();
  }

  window.KonturCalc = {
    getState: function () {
      return state;
    },
    formatMoney: formatMoney,
  };
})();
