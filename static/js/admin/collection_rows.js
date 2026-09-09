(function () {
  function reindex(root) {
    var prefix = root.getAttribute("data-collection-prefix");
    if (!prefix) return;
    var list = root.querySelector("[data-collection-list]");
    var total = root.querySelector("#id_" + prefix + "-TOTAL_FORMS");
    if (!list || !total) return;
    var rows = list.querySelectorAll("[data-collection-row]");
    var re = new RegExp(prefix + "-\\d+-");
    rows.forEach(function (row, index) {
      row.querySelectorAll("input, select, textarea, label").forEach(function (el) {
        ["name", "id", "for"].forEach(function (attr) {
          var val = el.getAttribute(attr);
          if (!val) return;
          el.setAttribute(attr, val.replace(re, prefix + "-" + index + "-"));
        });
      });
      var sort = row.querySelector('input[name$="-sort_order"]');
      if (sort) sort.value = String(index);
    });
    total.value = String(rows.length);
  }

  function bindCollection(root) {
    var prefix = root.getAttribute("data-collection-prefix");
    var list = root.querySelector("[data-collection-list]");
    var addBtn = root.querySelector("[data-collection-add]");
    var tpl = document.getElementById("collection-empty-" + prefix);
    var dragEl = null;
    if (!list) return;

    if (addBtn && tpl) {
      addBtn.addEventListener("click", function (e) {
        e.preventDefault();
        list.appendChild(tpl.content.cloneNode(true));
        reindex(root);
      });
    }

    list.addEventListener("dragstart", function (e) {
      var row = e.target.closest("[data-collection-row]");
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
      var row = e.target.closest("[data-collection-row]");
      if (!row || !dragEl || row === dragEl) return;
      var rect = row.getBoundingClientRect();
      var before = e.clientY < rect.top + rect.height / 2;
      list.insertBefore(dragEl, before ? row : row.nextSibling);
    });

    reindex(root);
  }

  function init() {
    document.querySelectorAll("[data-collection]").forEach(bindCollection);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
