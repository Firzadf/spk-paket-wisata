"""Uji halaman publik, API, pagination, dan isi database seed.

Jalankan dari root repo: python -m unittest discover -s tests -v
"""

import sqlite3

from base import APLIKASI, TripRankTestCase


class PublicPagesTest(TripRankTestCase):
    def test_semua_halaman_publik_200(self):
        for url in ["/", "/tentang", "/cara-kerja", "/lab",
                    "/kota/Jakarta", "/kota/Yogyakarta", "/kota/Bandung",
                    "/kota/Semarang", "/kota/Surabaya",
                    "/rekomendasi?kota=Jakarta&metode=keduanya",
                    "/rekomendasi?kota=Jakarta&metode=saw",
                    "/rekomendasi?kota=Jakarta&metode=topsis",
                    "/paket/18", "/paket/1", "/admin/login"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)

    def test_beranda_memuat_data_proyek(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("TripRank", html)
        self.assertIn("/lab", html)
        self.assertIn("Paket 18", html)  # pemenang SAW Jakarta

    def test_metode_tidak_valid_jatuh_ke_keduanya(self):
        html = self.client.get(
            "/rekomendasi?kota=Jakarta&metode=acak").get_data(as_text=True)
        self.assertIn("Ranking SAW", html)
        self.assertIn("Ranking TOPSIS", html)


class PaginationTest(TripRankTestCase):
    def test_kota_halaman_2_menampilkan_paket_11_sampai_20(self):
        html = self.client.get("/kota/Jakarta?page=2").get_data(as_text=True)
        self.assertIn("11-20 dari 20 paket", html)
        self.assertIn("Paket 11", html)

    def test_kota_halaman_lewat_batas_dipotong_ke_halaman_terakhir(self):
        html = self.client.get("/kota/Jakarta?page=99").get_data(as_text=True)
        self.assertIn("11-20 dari 20 paket", html)

    def test_rekomendasi_halaman_2(self):
        html = self.client.get(
            "/rekomendasi?kota=Jakarta&metode=saw&page=2").get_data(as_text=True)
        self.assertIn("11-20 dari 20 paket", html)


class ApiTest(TripRankTestCase):
    def test_api_saw_dan_topsis_20_baris(self):
        for metode in ("saw", "topsis"):
            data = self.client.get(f"/api/kota/Jakarta/{metode}").get_json()
            self.assertEqual(len(data["ranking"]), 20)
            self.assertEqual(data["kota"], "Jakarta")

    def test_api_kota_tidak_ada_404(self):
        r = self.client.get("/api/kota/Medan/saw")
        self.assertEqual(r.status_code, 404)
        self.assertIn("tidak ditemukan", r.get_json()["error"])

    def test_paket_tidak_ada_kembali_ke_beranda(self):
        r = self.client.get("/paket/9999", follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/"))


class SeedDataTest(TripRankTestCase):
    def test_jumlah_seed_sesuai_rencana(self):
        conn = sqlite3.connect(APLIKASI / "spk_wisata.db")
        try:
            counts = {}
            for tabel in ("kota", "paket", "tempat", "paket_tempat",
                          "kriteria", "nilai_paket"):
                counts[tabel] = conn.execute(
                    f"SELECT COUNT(*) FROM {tabel}").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(counts, {
            "kota": 5, "paket": 100, "tempat": 298,
            "paket_tempat": 403, "kriteria": 5, "nilai_paket": 500,
        })

    def test_total_bobot_kriteria_1(self):
        import database
        _, _, krit = database.get_weights_and_types()
        self.assertAlmostEqual(sum(k["bobot"] for k in krit), 1.0, places=3)
        self.assertEqual([k["kode"] for k in krit],
                         ["C1", "C2", "C3", "C4", "C5"])
