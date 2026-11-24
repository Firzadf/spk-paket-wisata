# Uji TripRank

Jalankan dari root repo:

```bash
python -m unittest discover -s tests -v
```

Tidak ada dependensi baru: hanya `unittest` standar dan Flask yang
sudah dipakai aplikasi. GitHub Actions menjalankan perintah yang
sama di setiap push ke `main` (lihat `.github/workflows/tests.yml`).

Isi:

- `test_lab.py` — Lab Simulasi Bobot dan regresi pemenang 5 kota.
- `test_app.py` — Halaman publik, API, pagination, dan jumlah seed.
- `test_admin.py` — Login, proteksi halaman admin, ubah kriteria
  dan nilai, serta simulasi bobot admin.
- `test_security.py` — Token CSRF, batas percobaan login,
  flag cookie sesi, dan peringatan demo Vercel.
- `test_v41.py` — Polish v4.1: 0 gradient dan 0 warna emas di CSS,
  marquee hilang, animasi 3D tetap ada, halaman rekomendasi
  rata tengah. Sejak redesign Pomaii, tes typewriter diganti:
  home tetap punya bg-3d (Filosofi) tapi tanpa typewriter.
- `test_pomaii.py` — Redesign gaya Pomaii: form filter kota dan
  metode ke /rekomendasi, trust strip jujur, 5 kartu kota, kredit
  Wikimedia untuk foto asli dan tanpa label "Ilustrasi AI" di mana
  pun, pill kriteria dan banner Lab, 0 gradient dan 0 emas di CSS,
  CTA oranye dan radius kartu 18px, font hanya 2 keluarga.

Tes yang menulis (admin) memakai salinan sementara database
(lihat `base.py`), jadi `aplikasi/spk_wisata.db` yang ter-commit
tidak pernah berubah karena tes.
