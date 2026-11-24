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

### ADR-004: Pengerasan keamanan admin tanpa dependensi baru
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** Form admin tidak punya token CSRF, login tanpa batas percobaan, dan edit admin di Vercel diam-diam hilang saat cold start.
- **Decision:** Token CSRF per sesi dicek di setiap POST `/admin/*` (400 kalau tidak ada atau salah), login dibatasi 5 gagal dalam 15 menit per IP lalu diblokir 15 menit (hitungan di memori per instance, direset saat login benar), cookie sesi HttpOnly + SameSite Lax + Secure saat `SPK_SECRET_KEY` di-set (produksi), dan banner peringatan "tidak permanen" tampil di semua halaman admin saat `VERCEL=1`. Dikunci 8 tes di `tests/test_security.py`.
- **Why not alternatives:** Flask-WTF akan menambah dependensi hanya untuk CSRF yang bisa dibuat dengan `secrets` + `hmac` standar; rate limit di database akan menambah tabel dan migrasi untuk ancaman yang ditangani cukup di memori.

### ADR-005: Polish v4.1 — tombol datar tanpa gradient/emas, teks rapi, animasi 3D tetap
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** User menilai v4 lebih oke dari v5 Tenang karena suka animasi 3D dan transisi, tapi penempatan kalimat/paragraf masih ngaco, warna tombol dan font norak, dan tampilan tombol norak. Bukti screenshot: tombol emas gradient dengan bayangan 3D tebal, tiga perlakuan tombol berbeda dalam satu baris, marquee terpotong di tepi viewport, bentuk bg-3d menabrak tepi panel dan teks, typewriter tertangkap terpotong, paragraf hero berakhir dengan baris yatim.
- **Decision:** Satu sistem tombol datar dua warna (primer hijau gelap #1d4a38 teks putih, sekunder krem #fffdf9 ber-border ink teks ink), 0 `linear-gradient` dan 0 warna emas di CSS, bayangan offset 3D diganti bayangan lembut saat hover. Marquee dihapus total. Bentuk bg-3d dibatasi di dalam panel (inset 0), diredupkan, dan dipindah ke area kosong bawah panel supaya tidak menabrak teks. Hero dan judul memakai `text-wrap: balance`, typewriter dicadangkan tinggi 2 baris penuh (3 baris di HP). Halaman rekomendasi rata tengah (judul, lede, tombol metode, pagination) lewat class `page-head center`. Animasi 3D dipertahankan penuh: bg-3d melayang, loading screen, typewriter, transisi 3D halaman, scroll reveal 3D, tilt kartu, maskot dan ikon 3D clay. Perbaikan bonus: bug v4 di `app.js` — handler `pageshow` menghapus class `page-entering` 38ms setelah ditambah sehingga animasi masuk 3D tidak pernah tampil; sekarang hanya dihapus saat kembali dari cache (`e.persisted`). Dikunci 8 tes di `tests/test_v41.py`.
- **Why not alternatives:** Menghapus semua animasi (v5 Tenang) sudah ditolak user; membiarkan emas/gradient berarti mempertahankan keluhan utama user.

### ADR-006: Redesign gaya Pomaii — hero foto, filter bar, kartu kota, banner Lab
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** User mengirim referensi landing travel Pomaii dan meminta UI/UX dibuat seperti itu; pass presisi v4.2 dibatalkan dan diganti redesign ini. Aturan gambar berubah tiga kali selama pengerjaan: awalnya generate semua gambar, lalu koreksi 09:22 WIB (pakai foto asli Wikimedia yang digrading), lalu aturan final 09:32 WIB (generate AI boleh untuk gambar apa pun, label "Ilustrasi AI" tidak diperlukan; situs referensi Pomaii itu sendiri hasil generate AI tanpa label).
- **Decision:** Struktur dan presisi Pomaii diadopsi, BUKAN isinya: tanpa rating bintang, tanpa harga, tanpa testimoni, tanpa klaim jumlah traveler, tanpa newsletter; hanya angka nyata (5 kota, 100 paket, 298 tempat, 403 relasi). Urutan home: hero full-bleed teks rata kiri + filter bar mengambang (form GET nyata ke `/rekomendasi`, jalan tanpa JS) + trust strip 4 item jujur + 5 kartu kota (foto, 20 paket, pemenang SAW/TOPSIS asli) + pill kriteria (5 pill dengan bobot) + Misi, Filosofi, Janji (konten tetap) + Cara Kerja 4 langkah + 2 kartu cerita + banner Lab (panel hijau gelap + foto danau + CTA) + "Bukan situs booking" (maskot 3D tetap) + stats strip angka nyata + footer yang sudah ada. Font 2 keluarga (Fraunces display + Space Grotesk semua sisanya); tombol CTA berbentuk pil, CTA primer oranye hangat #c2410c (kontras 5,18:1 dengan teks putih, lolos AA) hanya untuk ajakan utama; kartu radius 18px dengan bayangan lembut, hover naik; 0 `linear-gradient`, 0 emas di CSS. Typewriter dihapus (tes `test_v41` yang mengharuskannya diperbarui, bukan dihapus diam-diam); bg-3d tetap di Filosofi, loading screen, transisi 3D halaman, scroll reveal, dan tilt kartu dipertahankan. Gambar, dipilih per gambar mana yang paling bagus: hero Monas hasil generate AI (detail dicek benar: tugu, api emas, cawan, dek observasi), 5 kartu kota memakai foto asli Wikimedia yang digrading konsisten dengan PIL (kontras, saturasi, sharpness naik, sedikit tone hangat, skrip `/tmp/grade-pomaii.py`), 2 gambar traveler dan 1 gambar gunung dan danau hasil generate AI. Kredit fotografer Wikimedia tetap dicantumkan untuk foto asli yang dipakai (syarat lisensi CC); label "Ilustrasi AI" tidak dipakai di mana pun. Dikunci 10 tes baru di `tests/test_pomaii.py` (total suite 58 tes).
- **Why not alternatives:** Menyalin isi Pomaii (rating, harga, testimoni, klaim traveler) akan memalsukan data proyek; memakai foto asli tanpa grading membuat hero terlihat kusam seperti keluhan user sebelumnya; memakai foto Monas asli yang digrading sebagai hero kalah terang dibanding hasil generate AI yang detailnya benar.
