# DECISIONS.md — Architecture Decision Records (ADR)

Rules marked `LOCKED` MUST NOT be refactored or reversed by any agent without explicit user approval.

---

### ADR-001: Proof-First UI & Recorded Replay Fallback
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** Live RPC/external APIs can be slow or offline during demos/reviews, and wallet-walls kill conversion.
- **Decision:** Render initial public views via SSR/static HTML with bundled real-world replay snapshots (`SIMULATED`/`REPLAY` tagged) that upgrade to live polling when available.
- **Why not alternatives:** Pure CSR with loading spinners fails when nodes stall; mock random numbers destroy credibility.

### ADR-002: Lab Simulasi Bobot publik (tanpa login)
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** Simulasi bobot sebelumnya terkunci di balik login admin, jadi dosen penguji tidak bisa memeriksa sendiri bahwa ranking mengikuti bobot. Jalur 404 kota/rekomendasi juga pernah gagal render (500) karena index.html butuh `winners` dan `city_meta` yang tidak dikirim.
- **Decision:** Halaman publik `/lab` (GET, tanpa login, tanpa simpan) memakai `compute_city` yang sama dengan ranking resmi; bobot default sama dengan bobot resmi. Uji regresi di `tests/test_lab.py` (unittest standar, tanpa dependensi baru) mengunci pemenang 5 kota dan jalur 404. Jalur 404 disatukan lewat helper `render_index_404`.
- **Why not alternatives:** Menyalin logika hitung ke JavaScript akan menduplikasi sumber kebenaran; membuka `/admin/simulasi` ke publik akan membuka panel admin.

### ADR-003: Test suite repo + CI di setiap push
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** Sebelum ini repo tidak punya satu pun tes otomatis; semua redesign hanya dicek manual dan berisiko merusak pemenang ranking secara diam-diam.
- **Decision:** `tests/` memakai `unittest` standar (tanpa dependensi baru) dengan 32 tes: halaman publik, API, pagination, jumlah seed, login dan proteksi admin, ubah kriteria/nilai, simulasi, dan regresi pemenang 5 kota. Tes yang menulis memakai salinan sementara database (lihat `tests/base.py`) supaya `spk_wisata.db` yang ter-commit tidak pernah berubah karena tes. GitHub Actions (`.github/workflows/tests.yml`) menjalankan suite yang sama di setiap push ke `main`.
- **Why not alternatives:** pytest akan menambah dependensi tanpa kebutuhan nyata; tes terhadap database asli akan merusak data resmi.
