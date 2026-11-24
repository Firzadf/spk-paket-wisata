"""Uji Lab Simulasi Bobot dan regresi ranking TripRank.

Jalankan dari root repo (hosting/vercel) dengan venv aplikasi:
  ../aplikasi/.venv/bin/python -m unittest discover -s tests -v

Tidak ada dependensi baru: hanya unittest standar dan Flask.
Pemenang di bawah ini adalah nilai resmi yang sudah diverifikasi
terhadap Excel (hitungan_SAW_TOPSIS_per_kota.xlsx) dan terhadap
aplikasi sejak Langkah 3; kalau ada yang berubah, ada yang rusak.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "aplikasi"))

from app import app  # noqa: E402

# (kota, pemenang SAW, Vi, pemenang TOPSIS, Ci)
WINNERS = [
    ("Jakarta", 18, 0.8388, 8, 0.7965),
    ("Yogyakarta", 27, 0.9241, 27, 0.7629),
    ("Bandung", 47, 0.8258, 47, 0.6933),
    ("Semarang", 72, 0.8217, 72, 0.6795),
    ("Surabaya", 83, 0.8730, 83, 0.7170),
]


class LabTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_lab_terbuka_tanpa_login(self):
        r = self.client.get("/lab")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Lab Simulasi Bobot", r.get_data(as_text=True))

    def test_lab_bobot_resmi_sama_dengan_pemenang_resmi(self):
        for kota, saw, vi, topsis, ci in WINNERS:
            r = self.client.get(f"/lab?kota={kota}")
            self.assertEqual(r.status_code, 200)
            html = r.get_data(as_text=True)
            self.assertIn(f"Pemenang SAW: Paket {saw} (Vi {vi:.4f})", html)
            self.assertIn(f"Pemenang TOPSIS: Paket {topsis} (Ci {ci:.4f})", html)

    def test_lab_bobot_kustom_mengubah_hasil(self):
        # Bobot harga 1,00: paket termurah harus menang SAW dengan Vi 1,0000
        # (normalisasi cost: nilai minimum dibagi nilai paket).
        r = self.client.get(
            "/lab?kota=Jakarta&bobot_C1=1&bobot_C2=0&bobot_C3=0&bobot_C4=0&bobot_C5=0")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("Pemenang SAW: Paket", html)
        self.assertIn("(Vi 1.0000)", html)

    def test_lab_total_bobot_salah_ditolak(self):
        r = self.client.get(
            "/lab?kota=Jakarta&bobot_C1=0.5&bobot_C2=0.5&bobot_C3=0.5&bobot_C4=0&bobot_C5=0")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("Total kelima bobot harus 1,00", html)
        self.assertNotIn("Hasil simulasi", html)

    def test_lab_bobot_bukan_angka_ditolak(self):
        r = self.client.get("/lab?kota=Jakarta&bobot_C1=abc")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Bobot harus angka", r.get_data(as_text=True))

    def test_lab_kota_tidak_ada_404(self):
        self.assertEqual(self.client.get("/lab?kota=Medan").status_code, 404)

    def test_kota_dan_rekomendasi_tidak_ada_404_bukan_500(self):
        # Jalur 404 lama pernah gagal render karena index.html butuh
        # winners dan city_meta; uji ini mengunci perbaikannya.
        for url in ["/kota/Medan", "/rekomendasi?kota=Medan"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 404, url)
            self.assertIn("tidak ditemukan", r.get_data(as_text=True))

    def test_api_pemenang_tidak_berubah(self):
        for kota, saw, vi, topsis, ci in WINNERS:
            saw_data = self.client.get(f"/api/kota/{kota}/saw").get_json()
            self.assertEqual(saw_data["ranking"][0]["paket"], saw)
            self.assertAlmostEqual(saw_data["ranking"][0]["nilai"], vi, places=4)
            topsis_data = self.client.get(f"/api/kota/{kota}/topsis").get_json()
            self.assertEqual(topsis_data["ranking"][0]["paket"], topsis)
            self.assertAlmostEqual(topsis_data["ranking"][0]["nilai"], ci, places=4)

    def test_halaman_publik_200_dan_tautan_lab_ada(self):
        for url in ["/", "/tentang", "/cara-kerja", "/kota/Jakarta",
                    "/rekomendasi?kota=Jakarta&metode=keduanya", "/paket/18"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
        self.assertIn("/lab", self.client.get("/").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
