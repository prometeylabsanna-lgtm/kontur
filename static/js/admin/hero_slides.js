(function () {
  function reindex(root) {
    var list = root.querySelector("[data-hero-slides-list]");
    var total = root.querySelector("#id_hero_slides-TOTAL_FORMS");
    if (!list || !total) return;
    var rows = list.querySelectorAll("[data-hero-slide-row]");
    rows.forEach(function (row, index) {
      row.querySelectorAll("input, select, textarea, label").forEach(function (el) {
        ["name", "id", "for"].forEach(function (attr) {
          var val = el.getAttribute(attr);
          if (!val) return;
          el.setAttribute(
            attr,
            val.replace(/hero_slides-\d+-/, "hero_slides-" + index + "-")
          );
        });
      });
      var sort = row.querySelector('input[name$="-sort_order"]');
      if (sort) sort.value = String(index);
    });
    total.value = String(rows.length);
  }

  function init() {
    var root = document.querySelector("[data-hero-slides]");
    if (!root) return;
    var list = root.querySelector("[data-hero-slides-list]");
    var addBtn = root.querySelector("[data-hero-slides-add]");
    var tpl = document.getElementById("hero-slide-empty-form");
    var dragEl = null;

    if (addBtn && tpl) {
      addBtn.addEventListener("click", function () {
        var node = tpl.content.cloneNode(true);
        list.appendChild(node);
        reindex(root);
      });
    }

    list.addEventListener("dragstart", function (e) {
      var row = e.target.closest("[data-hero-slide-row]");
      if (!row) return;
      dragEl = row;
      row.classList.add("is-dragging");
    });
    list.addEventListener("dragend", function () {
      if (dragEl) dragEl.classList.remove("is-dragging");
      dragEl = null;
      reindex(root);
    });
    list.addEventListener("dragover", function (e) {
      e.preventDefault();
      var row = e.target.closest("[data-hero-slide-row]");
      if (!row || !dragEl || row === dragEl) return;
      var rect = row.getBoundingClientRect();
      var before = e.clientY < rect.top + rect.height / 2;
      list.insertBefore(dragEl, before ? row : row.nextSibling);
    });

    reindex(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
