(function () {
  function applyPair(picker, hex, value) {
    if (!picker || !hex || !value) return;
    var v = String(value).trim().toLowerCase();
    if (!/^#[0-9a-f]{6}$/.test(v)) return;
    picker.value = v;
    hex.value = v;
  }

  function syncPair(field, picker, hex) {
    if (!picker || !hex) return;

    picker.addEventListener("input", function () {
      hex.value = picker.value;
    });

    function applyHex() {
      applyPair(picker, hex, hex.value);
    }

    hex.addEventListener("change", applyHex);
    hex.addEventListener("blur", applyHex);

    var form = field.closest("form");
    if (form) {
      form.addEventListener("submit", applyHex);
    }

    var resetBtn = field.querySelector("[data-cms-color-reset]");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        var fallback = (field.getAttribute("data-cms-color-default") || "").trim();
        applyPair(picker, hex, fallback);
        picker.dispatchEvent(new Event("input", { bubbles: true }));
      });
    }
  }

  function bind(root) {
    root.querySelectorAll(".cms-color-field").forEach(function (field) {
      if (field.dataset.bound === "1") return;
      field.dataset.bound = "1";
      syncPair(
        field,
        field.querySelector('input[type="color"]'),
        field.querySelector("[data-cms-color-hex]")
      );
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bind(document);
  });
})();
