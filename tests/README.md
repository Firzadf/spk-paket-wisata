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
- `test_v5.py` — Rombak v5 Tenang: tidak ada gradient, transform 3D,
  maskot/logo/ikon 3D, marquee, atau typewriter; font hanya 2 keluarga.

Tes yang menulis (admin) memakai salinan sementara database
(lihat `base.py`), jadi `aplikasi/spk_wisata.db` yang ter-commit
tidak pernah berubah karena tes.
