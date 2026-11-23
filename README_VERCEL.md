# Varian Vercel: SPK Rekomendasi Paket Wisata (demo baca)

Isi folder ini adalah proyek Vercel yang siap deploy, isinya salinan aplikasi
Flask yang sama dengan versi laptop, plus `api/index.py` dan `vercel.json`.

Redesign modern v2, 23 November 2026: tampilan diganti ke modern minimal
sans-serif bersih (ground putih, ink hampir hitam, aksen hijau #00754a,
radius kecil 8px, layout rapat, header putih lengket). Serif Georgia v1
dihapus karena terasa kuno. Halaman baru: `/tentang` (Tentang Kami, sumber
data, FAQ, disclaimer) dan `/cara-kerja` (metodologi SAW dan TOPSIS),
ditautkan dari navigasi, beranda, dan footer. Animasi hanya lapisan CSS
(transform dan opacity, stagger 60ms, fallback prefers-reduced-motion).
Semua halaman di `aplikasi/templates/` sudah v2, dan ada
`aplikasi/static/app.js` untuk sortir tabel dan filter paket per kota
(tabel tetap lengkap tanpa JavaScript). Data, logika, dan hasil hitungan
SAW/TOPSIS tidak berubah. `api/index.py`, `vercel.json`, dan
`requirements.txt` tidak berubah, cara deploy di bawah tetap berlaku.

## Cara deploy, pilih salah satu

### A. Lewat GitHub (paling rapi)

1. Buat repository GitHub baru, lalu push SELURUH isi folder ini ke repository itu.
2. Buka vercel.com, login dengan akun Vercel kamu, klik Add New lalu Project,
   lalu pilih repository itu.
3. Framework Preset: biarkan Other. Root Directory: root repository ini.
4. Environment Variables, tambahkan satu: nama `SPK_SECRET_KEY`, nilainya
   string acak panjang yang kamu buat sendiri (misalnya hasil perintah
   `python -c "import secrets; print(secrets.token_hex(32))"` di laptop kamu).
   Jangan kirim nilai ini ke siapa pun lewat chat.
5. Klik Deploy. Alamatnya nanti seperti `https://nama-project.vercel.app`.

### B. Lewat Vercel CLI dari laptop kamu

1. Instal CLI sekali saja: `npm i -g vercel`
2. Di terminal, masuk ke folder ini, lalu `vercel login` dan ikuti login di browser.
3. Jalankan `vercel --prod`, lalu atur environment variable `SPK_SECRET_KEY`
   di dasbor Vercel seperti langkah A nomor 4, lalu deploy ulang bila perlu.

## Yang jalan dan yang tidak

Jalan normal:
- Beranda, daftar paket per kota, detail paket.
- Rekomendasi SAW, rekomendasi TOPSIS, dan perbandingan keduanya.
- Simulasi bobot, karena simulasi memang tidak menyimpan apa pun.
- Login admin dan dasbor admin (baca data).

Tidak permanen:
- Perubahan dari panel admin (ubah bobot, ubah nilai paket) hanya tersimpan di
  salinan database sementara di `/tmp` per instance serverless. Perubahan itu
  bisa hilang saat cold start atau saat instance berganti, dan pengunjung lain
  bisa melihat data yang berbeda setelah ada yang mengedit. Ini batas bawaan
  Vercel untuk SQLite, bukan bug aplikasi.
- Jadi untuk demo ke dosen, pakai Vercel untuk melihat ranking, dan pakai
  demo lokal di laptop untuk menunjukkan edit admin.

## Sebelum dibagikan ke dosen

Ubah dulu kata sandi admin demo di database bawaan, supaya link online tidak
bisa diedit sembarang orang. Jalankan dari folder `aplikasi/`:

```
python ubah_password_admin.py
```

Kata sandi diminta lewat terminal dan tidak tampil di layar, dan tidak
ditulis ke file mana pun. Setelah diubah, deploy ulang supaya database bawaan
yang ter-deploy sudah berisi kata sandi baru.

Akun demo bawaan sebelum diubah: username `admin`, kata sandi `admin123`.
