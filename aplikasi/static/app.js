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

/* --- Lab Simulasi: tampilkan total bobot saat mengetik.
   Server tetap memvalidasi total 1,00; ini hanya tampilan. --- */
(function () {
  "use strict";
  var totalEl = document.getElementById("lab-total");
  if (!totalEl) return;
  var inputs = [];
  for (var i = 1; i <= 5; i++) {
    var input = document.getElementById("bobot_C" + i);
    if (input) inputs.push(input);
  }
  if (!inputs.length) return;
  function updateTotal() {
    var sum = 0;
    var ok = true;
    inputs.forEach(function (input) {
      var v = parseFloat(input.value);
      if (isNaN(v)) { ok = false; return; }
      sum += v;
    });
    totalEl.textContent = ok
      ? "Total kelima bobot harus 1,00. Total saat ini: " + sum.toFixed(2) + "."
      : "Total kelima bobot harus 1,00. Isi semua bobot dengan angka.";
  }
  inputs.forEach(function (input) { input.addEventListener("input", updateTotal); });
  updateTotal();
})();

/* Scroll reveal v5: hanya fade + naik 8px, 280ms, stagger 60ms per grup.
   Tanpa JavaScript atau dengan prefers-reduced-motion, konten tampil penuh. */
(function () {
  "use strict";
  var targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced || !("IntersectionObserver" in window)) {
    targets.forEach(function (el) { el.classList.add("is-visible"); });
    return;
  }
  var groups = {};
  targets.forEach(function (el) {
    var parent = el.parentElement;
    var key = parent ? parent.className + "|" + parent.tagName : "solo";
    if (!groups[key]) groups[key] = [];
    groups[key].push(el);
  });
  Object.keys(groups).forEach(function (key) {
    var list = groups[key];
    if (list.length > 1) {
      list.forEach(function (el, idx) {
        el.style.transitionDelay = (idx * 60) + "ms";
      });
    }
  });
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  targets.forEach(function (el) { observer.observe(el); });
})();
