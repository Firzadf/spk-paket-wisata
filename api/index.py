"""Entry point Vercel serverless untuk aplikasi Flask SPK Paket Wisata.

Kenapa file ini ada:
- Vercel tidak menjalankan `python app.py` seperti di laptop. Ia menjalankan
  fungsi serverless dari folder `api/`.
- File ini mengimpor aplikasi Flask dari folder `aplikasi/` dan mengeksposnya
  sebagai `app`, yang dibaca Vercel sebagai aplikasi WSGI.

Kenapa database disalin ke /tmp:
- Di Vercel, semua file deployment hanya bisa dibaca, tidak bisa ditulis.
- Kalau aplikasi langsung memakai `aplikasi/spk_wisata.db`, setiap simpan dari
  panel admin akan gagal (readonly database).
- Solusinya: salin database bawaan ke /tmp saat fungsi pertama kali jalan,
  lalu arahkan `database.DB_PATH` ke salinan itu. Baca dan tulis jadi jalan,
  tapi ingat batasnya (lihat README_VERCEL.md): salinan /tmp itu sementara
  per instance serverless, perubahan admin TIDAK permanen dan bisa hilang
  saat cold start atau instance berganti. Untuk demo baca (beranda, daftar
  paket, rekomendasi, simulasi) ini tidak masalah, karena simulasi memang
  tidak menyimpan apa pun.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APLIKASI = ROOT / "aplikasi"
sys.path.insert(0, str(APLIKASI))

import database  # noqa: E402

_BUNDLED = APLIKASI / "spk_wisata.db"
_TMP = Path("/tmp/spk_wisata.db")
try:
    if not _TMP.exists():
        shutil.copyfile(_BUNDLED, _TMP)
    database.DB_PATH = _TMP
except Exception:
    # Fallback: pakai database bawaan. Halaman baca tetap jalan,
    # hanya simpan admin yang akan gagal.
    pass

from app import app  # noqa: E402,F401
