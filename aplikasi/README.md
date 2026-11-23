# Aplikasi Web SPK Paket Wisata (Langkah 5)

## Cara menjalankan (offline, tanpa internet)

Dari folder aplikasi ini:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py --force
.venv/bin/python app.py
```

Lalu buka http://127.0.0.1:5000

Catatan: folder .venv sudah dibuat di mesin ini dengan Flask 3.1.3, jadi di mesin ini
cukup jalankan dua perintah terakhir. Di laptop lain, jalankan semua perintah di atas.

## Akun demo

- Nama pengguna: admin
- Kata sandi: admin123
- Kata sandi disimpan sebagai hash, bukan teks biasa.
- Ganti kata sandi ini sebelum pemakaian nyata.
- Kalau lupa, jalankan seed ulang dengan --force, akun demo akan dibuat ulang.
  Perhatian: seed --force menghapus database lama.

## Halaman utama

- Beranda (/): 5 kartu kota dan tabel kriteria dan bobot.
- Daftar kota (/kota/<nama>): 20 paket kota itu beserta tempat dan nilai kriteria.
- Rekomendasi (/rekomendasi?kota=<nama>&metode=saw|topsis|keduanya):
  ranking lengkap beserta tahap hitungan (matriks, normalisasi, matriks terbobot,
  solusi ideal, jarak, dan perbandingan).
- Detail paket (/paket/<id>): tempat, nilai, dan peringkat SAW dan TOPSIS paket itu.
- API JSON: /api/kota/<nama>/saw dan /api/kota/<nama>/topsis, dipakai untuk pengujian Langkah 6.

## Halaman admin (wajib login)

- Dasbor (/admin): ringkasan jumlah paket per kota.
- Kriteria (/admin/kriteria): ubah tipe dan bobot. Total bobot harus 1,00, kalau tidak ditolak.
- Paket dan nilai (/admin/paket, /admin/paket/<id>/nilai): ubah nilai C1-C5 dalam skala 1-5.
- Simulasi bobot (/admin/simulasi): hitung ranking dengan bobot sementara tanpa menyimpan.
  Dipakai untuk uji sensitivitas di Langkah 6.

## Struktur kode

- saw.py: hitungan SAW murni, tanpa database dan tanpa web.
- topsis.py: hitungan TOPSIS murni, tanpa database dan tanpa web.
- database.py: akses SQLite, selalu mengaktifkan foreign key.
- seed.py: seed database dari data Langkah 2.
- app.py: route Flask dan halaman admin.
- templates/: halaman HTML.
- static/style.css: gaya tampilan, tanpa CDN, supaya jalan offline.
- spk_wisata.db: database SQLite hasil seed (5 kota, 100 paket, 298 tempat, 403 relasi paket-tempat, 500 nilai paket).

## Data

Nilai C1-C4 adalah skor rubrik tim dari Langkah 2, bukan harga atau rating resmi.
Nilai C5 adalah jumlah tempat unik dalam paket setelah pembersihan data.
Pembersihan data: tiga nama tempat di CSV asli diawali karakter pipa nyasar sudah dibersihkan,
dan paket 54 Bandung yang mencantumkan tempat yang sama dua kali sudah dideduplikasi
menjadi 2 tempat unik.
