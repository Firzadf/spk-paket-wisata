# SPK Rekomendasi Paket Wisata

Sistem Pendukung Keputusan untuk rekomendasi paket wisata di 5 kota besar Indonesia, menggunakan metode SAW dan TOPSIS. Proyek akhir mata kuliah SPK, Rekayasa Perangkat Lunak, dan Proyek Sistem Informasi, Universitas Bina Sarana Informatika.

## Yang dibangun

- Aplikasi web Python Flask + SQLite, jalan offline di `http://127.0.0.1:5000`.
- 100 paket wisata, 20 paket per kota: Jakarta, Yogyakarta, Bandung, Semarang, Surabaya.
- 298 tempat wisata, 403 relasi paket-tempat, 500 nilai paket.
- Perhitungan SAW dan TOPSIS ditampilkan tahap demi tahap: matriks, normalisasi, matriks terbobot, solusi ideal, jarak, dan ranking.
- Panel admin: ubah kriteria dan bobot, ubah nilai paket, simulasi bobot tanpa menyimpan.

## Kriteria dan bobot

| Kode | Kriteria | Tipe | Bobot |
| --- | --- | --- | --- |
| C1 | Harga Paket | Cost | 0,30 |
| C2 | Fasilitas | Benefit | 0,25 |
| C3 | Aksesibilitas Lokasi | Benefit | 0,20 |
| C4 | Popularitas Destinasi | Benefit | 0,15 |
| C5 | Jumlah Destinasi | Benefit | 0,10 |

Nilai C1 sampai C4 adalah skor rubrik tim, bukan harga atau rating resmi. Nilai C5 adalah jumlah tempat unik dalam paket.

## Pemenang per kota

| Kota | SAW | TOPSIS |
| --- | --- | --- |
| Jakarta | Paket 18 (Vi 0,8388) | Paket 8 (Ci 0,7965) |
| Yogyakarta | Paket 27 (0,9241) | Paket 27 (0,7629) |
| Bandung | Paket 47 (0,8258) | Paket 47 (0,6933) |
| Semarang | Paket 72 (0,8217) | Paket 72 (0,6795) |
| Surabaya | Paket 83 (0,8730) | Paket 83 (0,7170) |

Jakarta adalah satu-satunya kota yang pemenang SAW dan TOPSIS-nya berbeda, karena SAW menjumlahkan skor terbobot sedangkan TOPSIS mengukur jarak ke solusi ideal.

## Cara menjalankan lokal

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py --force
.venv/bin/python app.py
```

Lalu buka http://127.0.0.1:5000

Akun demo admin: `admin` / `admin123`. Ganti kata sandi ini sebelum pemakaian nyata, dengan `python aplikasi/ubah_password_admin.py` dari folder `aplikasi/`.

Database bisa dibuat ulang dari data di `data/` dengan `seed.py --force`. Perhatian, perintah itu menghapus database lama.

## Deploy ke Vercel

Folder ini adalah proyek Vercel yang siap deploy, dengan `api/index.py` dan `vercel.json`. Lihat `README_VERCEL.md` untuk langkah deploy lewat GitHub atau Vercel CLI, dan batasannya: perubahan dari panel admin di Vercel hanya tersimpan sementara di `/tmp` per instance serverless, jadi Vercel cocok untuk demo baca, bukan untuk edit admin permanen.

## Desain

Redesign 23 November 2026, mode Operate. Token warna dan tipografi di `:root` di `aplikasi/static/style.css`, headline serif editorial plus system-ui, sudut persegi, tanpa gradien dan tanpa shadow. Tabel ranking bisa disortir dan paket per kota bisa difilter, tabel tetap lengkap tanpa JavaScript. Data, logika, dan hasil hitungan SAW/TOPSIS tidak berubah pada redesign ini.

## Struktur

- `aplikasi/` — aplikasi Flask, template, dan database SQLite hasil seed.
- `api/index.py` — entry point serverless Vercel, menyalin database ke `/tmp`.
- `data/` — dataset nilai kriteria dan klasifikasi tempat, sumber seed database.
- `vercel.json` — rewrite semua route ke `api/index.py`.
