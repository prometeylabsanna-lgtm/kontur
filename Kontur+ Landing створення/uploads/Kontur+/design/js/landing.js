(function () {
  "use strict";

  var rates = { basic: 460, optimal: 580, maximum: 700 };
  var state = {
    obj: "flat",
    rate: 580,
    pkg: "Оптимальний",
    area: 62,
  };

  function coef(area) {
    if (area <= 30) return 1.4;
    if (area <= 34) return 1.25;
    if (area <= 39) return 1.1;
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

    if (state.obj === "house") {
      out.classList.add("calc-out--custom");
      flatFields.hidden = true;
      sumEl.textContent = "";
      note.textContent =
        "Для будинку / котеджу потрібен індивідуальний кошторис після обміру.";
      pay.hidden = true;
      cta.textContent = "Залишити заявку на кошторис";
      cta.setAttribute("data-ctx", "Калькулятор: Будинок / Котедж");
      return;
    }

    out.classList.remove("calc-out--custom");
    flatFields.hidden = false;
    pay.hidden = false;
    cta.textContent = "Отримати точний розрахунок";

    var k = coef(state.area);
    var billable = Math.max(state.area, 40);
    var total = state.rate * k * billable;
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
    range.value = v;
    num.value = v;
    recalc();
  }
  range.addEventListener("input", function () {
    setArea(range.value);
  });
  num.addEventListener("change", function () {
    setArea(num.value);
  });

  var header = document.getElementById("siteHeader");
  window.addEventListener(
    "scroll",
    function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    },
    { passive: true }
  );

  var nav = document.getElementById("navSheet");
  function openNav() {
    nav.hidden = false;
    nav.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function closeNav() {
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

  function openModal(ctx) {
    modalCtx.textContent = "Контекст: " + (ctx || "Заявка");
    modalDefault.hidden = false;
    modalSuccess.hidden = true;
    form.reset();
    clearErrors();
    modal.hidden = false;
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    modal.classList.remove("is-open");
    modal.hidden = true;
    document.body.style.overflow = "";
  }
  document.querySelectorAll("[data-open-modal]").forEach(function (el) {
    el.addEventListener("click", function () {
      openModal(el.getAttribute("data-ctx"));
    });
  });
  document.querySelectorAll("[data-close-modal]").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });

  function clearErrors() {
    ["fieldName", "fieldPhone"].forEach(function (id) {
      var f = document.getElementById(id);
      f.classList.remove("field--error");
      f.querySelector(".field__hint").hidden = true;
    });
  }

  function uaPhone(v) {
    var d = String(v).replace(/\D/g, "");
    if (d.indexOf("380") === 0 && d.length === 12) return true;
    if (d.indexOf("0") === 0 && d.length === 10) return true;
    return false;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearErrors();
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
    if (!ok) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Надсилаємо…";
    window.setTimeout(function () {
      submitBtn.disabled = false;
      submitBtn.textContent = "Надіслати";
      modalDefault.hidden = true;
      modalSuccess.hidden = false;
    }, 900);
  });

  document.querySelectorAll(".accordion__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.parentElement;
      var open = item.classList.contains("is-open");
      document.querySelectorAll(".accordion__item").forEach(function (i) {
        i.classList.remove("is-open");
      });
      if (!open) item.classList.add("is-open");
    });
  });

  recalc();
})();
