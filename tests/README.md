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

Tes yang menulis (admin) memakai salinan sementara database
(lihat `base.py`), jadi `aplikasi/spk_wisata.db` yang ter-commit
tidak pernah berubah karena tes.
