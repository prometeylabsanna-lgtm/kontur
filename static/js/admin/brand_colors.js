(function () {
  function syncPair(picker, hex) {
    if (!picker || !hex) return;
    picker.addEventListener("input", function () {
      hex.value = picker.value;
    });
    function applyHex() {
      var v = (hex.value || "").trim();
      if (/^#[0-9A-Fa-f]{6}$/.test(v)) {
        picker.value = v.toLowerCase();
        hex.value = v.toLowerCase();
      }
    }
    hex.addEventListener("change", applyHex);
    hex.addEventListener("blur", applyHex);
    field.closest("form")?.addEventListener("submit", applyHex);
  }

  function bind(root) {
    root.querySelectorAll(".cms-color-field").forEach(function (field) {
      if (field.dataset.bound === "1") return;
      field.dataset.bound = "1";
      syncPair(
        field.querySelector('input[type="color"]'),
        field.querySelector("[data-cms-color-hex]")
      );
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bind(document);
  });
})();
