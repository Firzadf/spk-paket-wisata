/* Live thing: sortir tabel ranking dan filter paket per kota.
   Tabel lengkap sudah tampil tanpa JavaScript; script ini hanya
   menambah sortir dan filter di atasnya. */
(function () {
  "use strict";
  var collator = new Intl.Collator("id", { numeric: true, sensitivity: "base" });

  function announce(table, text) {
    var status = table.parentElement.querySelector("[data-sort-status]");
    if (status) status.textContent = text;
  }

  function sortRows(table, th, button) {
    var tbody = table.tBodies[0];
    if (!tbody) return;
    var direction = th.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
    var headers = table.tHead ? table.tHead.rows[0].cells : [];
    for (var i = 0; i < headers.length; i++) headers[i].removeAttribute("aria-sort");
    th.setAttribute("aria-sort", direction);
    var index = th.cellIndex;
    var type = th.getAttribute("data-type") || "text";
    var rows = Array.prototype.slice.call(tbody.rows);
    var factor = direction === "ascending" ? 1 : -1;
    rows.sort(function (a, b) {
      var va = a.cells[index].getAttribute("data-value") || a.cells[index].textContent.trim();
      var vb = b.cells[index].getAttribute("data-value") || b.cells[index].textContent.trim();
      if (type === "number") return factor * (parseFloat(va) - parseFloat(vb));
      return factor * collator.compare(va, vb);
    });
    for (var j = 0; j < rows.length; j++) {
      if (tbody.moveBefore) tbody.moveBefore(rows[j], null);
      else tbody.appendChild(rows[j]);
    }
    announce(table, "Diurutkan berdasarkan " + button.textContent.trim() + ", " +
      (direction === "ascending" ? "menaik" : "menurun") + ", " + rows.length + " baris");
  }

  document.querySelectorAll("table[data-sortable]").forEach(function (table) {
    var headers = table.tHead ? table.tHead.rows[0].cells : [];
    for (var i = 0; i < headers.length; i++) {
      (function (th) {
        var label = th.textContent.trim();
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sort-btn";
        btn.textContent = label;
        btn.addEventListener("click", function () { sortRows(table, th, btn); });
        th.textContent = "";
        th.appendChild(btn);
      })(headers[i]);
    }
  });

  var filterInput = document.querySelector("[data-filter-table]");
  if (filterInput) {
    var table = document.getElementById(filterInput.getAttribute("data-filter-table"));
    var count = document.querySelector("[data-filter-count]");
    filterInput.addEventListener("input", function () {
      var q = filterInput.value.trim().toLowerCase();
      var visible = 0;
      var rows = table.tBodies[0].rows;
      for (var i = 0; i < rows.length; i++) {
        var show = !q || rows[i].textContent.toLowerCase().indexOf(q) !== -1;
        rows[i].hidden = !show;
        if (show) visible++;
      }
      if (count) count.textContent = visible + " dari " + rows.length + " paket cocok.";
    });
  }
})();
