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

/* Loading screen dan scroll reveal (v4 r2; reveal tanpa putaran sejak
   ADR-007). Typewriter DIHAPUS pada redesign Pomaii (24 Nov 2026). Semua ini lapisan di atas konten:
   tanpa JavaScript, konten tetap tampil penuh; dengan
   prefers-reduced-motion, semuanya dimatikan. */
(function () {
  "use strict";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- Loading screen TripRank --- */
  function buildLoader() {
    var loader = document.createElement("div");
    loader.className = "trip-loader";
    loader.setAttribute("aria-hidden", "true");
    var img = document.createElement("img");
    img.src = "/static/images/logo-3d.png";
    img.alt = "";
    img.width = 96;
    var word = document.createElement("div");
    word.className = "loader-word";
    word.textContent = "TripRank";
    var bar = document.createElement("div");
    bar.className = "loader-bar";
    bar.appendChild(document.createElement("i"));
    loader.appendChild(img);
    loader.appendChild(word);
    loader.appendChild(bar);
    return loader;
  }
  function hideLoader(loader, after) {
    setTimeout(function () {
      loader.classList.add("is-hidden");
      setTimeout(function () { if (loader.parentNode) loader.parentNode.removeChild(loader); }, 350);
    }, after);
    setTimeout(function () { if (loader.parentNode) loader.parentNode.removeChild(loader); }, 2500);
  }
  if (!reduced) {
    var viaNav = false;
    try { viaNav = sessionStorage.getItem("triprank-nav") === "1"; sessionStorage.removeItem("triprank-nav"); } catch (e) {}
    var loader = buildLoader();
    document.body.appendChild(loader);
    hideLoader(loader, viaNav ? 450 : 900);
    /* Transisi 3D ganti halaman (v4 r3): halaman masuk dengan rotateY
       kecil (class page-entering, dilepas setelah animasi selesai supaya
       transisi keluar nanti tidak tertahan fill mode animasi), halaman
       lama keluar dengan rotateY berlawanan saat tautan internal diklik,
       lalu navigasi setelah 420ms. Tanpa JS, navigasi normal. */
    document.body.classList.add("page-entering");
    setTimeout(function () { document.body.classList.remove("page-entering"); }, 650);
    document.querySelectorAll("a[href]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        var href = a.getAttribute("href");
        if (!href || href.charAt(0) === "#" || a.target === "_blank") return;
        if (/^(https?:)?\/\//i.test(href) && a.origin !== location.origin) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        try { sessionStorage.setItem("triprank-nav", "1"); } catch (err) {}
        e.preventDefault();
        document.body.classList.add("page-leaving");
        setTimeout(function () { location.href = a.href; }, 420);
      });
    });
    /* pageshow: bersihkan kelas hanya saat kembali dari cache
       (e.persisted). Di muat awal JANGAN hapus page-entering, karena
       itu membatalkan animasi masuk 3D sebelum sempat tampil
       (bug v4: kelas ditambah lalu langsung dihapus 38ms kemudian). */
    window.addEventListener("pageshow", function (e) {
      document.body.classList.remove("page-leaving");
      if (e.persisted) {
        document.body.classList.remove("page-entering");
        var old = document.querySelector(".trip-loader");
        if (old && old.parentNode) old.parentNode.removeChild(old);
      }
    });
  }

  /* --- Parallax mouse untuk background 3D: bentuk di Filosofi bergeser
     pelan mengikuti kursor. Hanya di perangkat ber-pointer. (Hero tidak
     lagi memakai bg-3d sejak redesign Pomaii.) --- */
  if (!reduced && window.matchMedia("(hover: hover)").matches) {
    document.querySelectorAll(".philosophy").forEach(function (section) {
      section.addEventListener("mousemove", function (e) {
        var r = section.getBoundingClientRect();
        if (!r.width || !r.height) return;
        var mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
        var my = ((e.clientY - r.top) / r.height - 0.5) * 2;
        section.style.setProperty("--mx", mx.toFixed(2));
        section.style.setProperty("--my", my.toFixed(2));
      });
      section.addEventListener("mouseleave", function () {
        section.style.setProperty("--mx", 0);
        section.style.setProperty("--my", 0);
      });
    });
  }

  /* --- Scroll reveal: IntersectionObserver, stagger per grup. --- */
  var targets = document.querySelectorAll("[data-reveal]");
  if (targets.length && !reduced && "IntersectionObserver" in window) {
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
          el.style.transitionDelay = (idx * 90) + "ms";
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
  } else if (targets.length) {
    targets.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();

/* Header transparan di atas hero (home, desktop, gaya Pomaii): saat
   halaman di-scroll, header berubah jadi solid krem. Hanya aktif bila
   body.home-hero ada; tanpa JavaScript header tetap transparan di atas
   foto dan teks tetap terbaca karena foto bagian atas terang. */
(function () {
  "use strict";
  var header = document.querySelector("body.home-hero .site-header");
  if (!header) return;
  function onScroll() {
    header.classList.toggle("is-scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
