# Rubrik Penilaian dan Dataset Nilai Kriteria (Langkah 2)

## Status data

- Sumber alternatif: package_tourism.csv, 100 paket.
- Jakarta paket 1-20, Yogyakarta 21-40, Bandung 41-60, Semarang 61-80, Surabaya 81-100.
- Tiap paket berisi 2-5 tempat wisata unik setelah pembersihan data (lihat bawah), total 403 relasi paket-tempat, 298 nama tempat unik. CSV asli berisi 405 slot, selisih 2 slot berasal dari duplikat di paket 54.
- File hasil: dataset_nilai_kriteria.csv (100 baris), klasifikasi_tempat.csv (298 baris), build_dataset.py (skrip pembangun, bisa dijalankan ulang).

## Cara nilai dihitung (supaya bisa diaudit dosen)

Nilai C5 adalah jumlah tempat unik dalam paket setelah pembersihan data: 2, 3, 4, atau 5.

Nilai C1 sampai C4 dihitung sebagai rata-rata skor tempat wisata dalam paket itu, dibulatkan 2 desimal.
Skor tiap tempat ditentukan oleh kategorinya, bukan ditebak per paket. Tabel kategorinya ada di
klasifikasi_tempat.csv dan di skrip build_dataset.py. Siapa pun yang memakai tabel kategori yang sama
akan mendapat nilai yang sama.

Contoh pengecekan manual, paket 4 Jakarta:
- Pulau Tidung, Pulau Bidadari, Pulau Pari, Pulau Pramuka, Pulau Pelangi, semua kategori Pulau.
- Skor Pulau: C1 5, C2 2, C3 2, C4 4.
- Maka paket 4: C1 5,00, C2 2,00, C3 2,00, C4 4,00, C5 5.
Contoh ini bisa dicek langsung di dataset_nilai_kriteria.csv.

## Tabel kategori tempat

| Kategori | C1 Harga (Cost) | C2 Fasilitas (Benefit) | C3 Aksesibilitas (Benefit) | C4 Popularitas (Benefit) | Alasan singkat |
| Pulau | 5 | 2 | 2 | 4 | Biaya penyeberangan tinggi, fasilitas terbatas, akses sulit |
| Wahana dan waterpark | 4 | 5 | 4 | 4 | Tiket relatif mahal, fasilitas lengkap, akses kota baik |
| Wahana dan taman hiburan | 4 | 5 | 4 | 4 | Sama seperti wahana, untuk Trans Studio, glamping, dan sejenisnya |
| Kawasan wahana ikonik (Ancol) | 4 | 5 | 4 | 5 | Wahana besar dan ikonik |
| Ikonik dan taman budaya (TMII) | 4 | 5 | 4 | 5 | Kawasan budaya besar dan ikonik |
| Pantai | 3 | 3 | 3 | 4 | Biaya sedang, fasilitas sedang, akses sedang |
| Alam berat (gunung, curug, bukit, goa, hutan) | 3 | 2 | 2 | 3 | Biaya sedang, fasilitas terbatas, akses sulit |
| Landmark alam dan kota (tebing, watu, jembatan, patung) | 2 | 3 | 4 | 3 | Biaya murah, fasilitas sedang, akses kota baik |
| Museum dan sejarah | 2 | 4 | 4 | 4 | Tiket relatif murah, fasilitas baik, akses kota baik |
| Landmark ikonik | 2 | 4 | 5 | 5 | Monas, Borobudur, Prambanan, Malioboro, Lawang Sewu, Kota Tua, dan sejenisnya |
| Budaya dan seni | 2 | 3 | 4 | 4 | Galeri, pura, temple, saung angklung, dan sejenisnya |
| Religi | 1 | 3 | 4 | 4 | Umumnya gratis atau murah, fasilitas sedang, akses kota baik |
| Pasar, mal, dan kuliner | 3 | 5 | 5 | 3 | Fasilitas lengkap, akses sangat baik |
| Taman kota dan ruang publik | 2 | 4 | 5 | 3 | Biaya murah, fasilitas baik, akses sangat baik |
| Taman dan kebun | 2 | 4 | 4 | 3 | Biaya murah, fasilitas baik, akses baik |
| Kampung dan desa wisata | 2 | 3 | 3 | 3 | Biaya murah, fasilitas sedang, akses sedang |
| Kawasan wisata | 2 | 4 | 4 | 4 | Kawasan wisata terpadu di kota |
| Lainnya | 3 | 3 | 3 | 3 | Nama tempat generik yang tidak masuk kategori di atas, diberi nilai tengah agar tidak mengada-ada |

Catatan: tempat ikonik yang masuk kategori lain tetap dinaikkan popularitasnya ke 5 oleh skrip,
misalnya Monas, Istiqlal, dan Tangkuban Perahu. Daftar ikonik lengkap ada di skrip.

## Kriteria dan bobot (dari Langkah 1, tidak berubah)

- C1 Harga Paket, Cost, bobot 0,30. Nilai 1 = paling murah, 5 = paling mahal. Karena Cost, nilai kecil lebih baik.
- C2 Fasilitas, Benefit, bobot 0,25.
- C3 Aksesibilitas Lokasi, Benefit, bobot 0,20.
- C4 Popularitas Destinasi, Benefit, bobot 0,15.
- C5 Jumlah Destinasi, Benefit, bobot 0,10.
- Total bobot 1,00.

## Rentang nilai hasil (verifikasi)

- C1: 1,00 sampai 5,00.
- C2: 2,00 sampai 5,00.
- C3: 2,00 sampai 5,00.
- C4: 3,00 sampai 5,00.
- C5: 2, 3, 4, atau 5, dengan sebaran 1 paket berisi 2 tempat (paket 54, setelah duplikat dibuang), 34 paket berisi 3 tempat, 26 paket berisi 4 tempat, dan 39 paket berisi 5 tempat.
- Tidak ada paket yang kosong, tidak ada nilai di luar skala 1-5, dan tidak ada duplikat nomor paket.

## Kejujuran data (wajib ditulis di laporan)

- Nilai C1 sampai C4 adalah skor penilaian tim berdasarkan rubrik di atas, bukan harga resmi,
  rating resmi, atau hasil survei yang diklaim sudah dilakukan.
- Keterbatasan ini ditulis terbuka di Bab II dan Bab VIII laporan, beserta rencana perbaikan:
  mengganti skor rubrik dengan harga paket riil dari agen travel dan rating riil dari platform
  ulasan bila kelompok berhasil mengumpulkannya sebelum pengumpulan akhir.
- Nama tempat dan kota berasal dari dataset awal, bukan karangan.

## Yang belum diputuskan di Langkah 2 (menunggu kelompok)

- Template laporan resmi kampus belum diterima di chat ini. Begitu file template dikirim,
  format laporan di Langkah 7 wajib mengikuti template itu, bukan hanya juknis SPK.
- Langkah 7 (laporan) dan Langkah 8 (video, flyer, presentasi) DITAHAN atas permintaan user
  tanggal 24 Okt 2026, karena user mau melihat referensi orang lain dulu.

## Pembersihan data sumber (temuan saat seed aplikasi)

- Tiga nama tempat di CSV asli diawali karakter pipa nyasar dan sudah dibersihkan di build_dataset.py: "| Peta Park", "| Atlantis Land Surabaya", "| Food Junction Grand Pakuwon". Dua nama terakhir menyatu dengan nama bersih yang sama di paket lain, sehingga total nama unik turun dari 300 menjadi 298.
- Paket 54 Bandung mencantumkan Rainbow Garden dan Kota Mini masing-masing dua kali. Duplikat itu dibuang dengan urutan dipertahankan, sehingga paket 54 berisi 2 tempat unik, bukan 4 slot. Rata-rata C1-C4 paket 54 tidak berubah, karena tiap tempat yang diduplikasi muncul dengan jumlah yang sama. Nilai C5 paket 54 berubah dari 4 menjadi 2, dan itu mengubah sedikit nilai Ci TOPSIS Bandung, tapi tidak mengubah pemenang maupun urutan 3 besar Bandung.
