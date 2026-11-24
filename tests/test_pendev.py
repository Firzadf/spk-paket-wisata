"""Tes redesign pen.dev (24 Nov 2026, ADR-009): homepage mengikuti desain
pen.dev user (hero gelap, 8 section bernomor, tabel SAW vs TOPSIS), tapi
SEMUA data diganti data asli proyek. Tanpa korelasi Spearman (karangan
di desain), tanpa peringkat nasional top 10 (metodologi kita per kota;
membandingkan Ci antar kota tidak valid)."""
import unittest

from base import TripRankTestCase


class TestPenDevDataAsli(TripRankTestCase):
    def test_home_pakai_headline_pen_dev_dan_data_asli(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertEqual(self.client.get("/").status_code, 200)
        # Headline desain pen.dev, kata per kata.
        self.assertIn("Pilih paket wisata", html)
        self.assertIn("dengan cara yang bisa", html)
        self.assertIn("Anda pertanggungjawabkan.", html)
        # Angka nyata saja. "100 paket", "5 kota", "5 kriteria" muncul
        # utuh di subteks hero; "2 metode", "298 tempat", "403 relasi"
        # tampil sebagai angka + label terpisah di strip statistik.
        for angka in ("100 paket", "5 kota", "5 kriteria"):
            self.assertIn(angka, html)
        for stat in ('<span class="num">2</span><span class="lbl">metode</span>',
                     '<span class="num">298</span><span class="lbl">tempat wisata</span>',
                     '<span class="num">403</span><span class="lbl">relasi paket dan tempat</span>'):
            self.assertIn(stat, html)
        # Nama paket pemenang asli dari database.
        for nama in ("Paket 18 - Jakarta", "Paket 8 - Jakarta",
                     "Paket 27 - Yogyakarta", "Paket 47 - Bandung",
                     "Paket 72 - Semarang", "Paket 83 - Surabaya"):
            self.assertIn(nama, html)

    def test_home_tanpa_spearman_dan_tanpa_peringkat_nasional(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Spearman", html)
        self.assertNotIn("0,936", html)
        self.assertNotIn("0.936", html)
        for frasa in ("Peringkat Nasional", "peringkat nasional",
                      "Top 10", "top 10", "10 besar"):
            self.assertNotIn(frasa, html)

    def test_home_punya_delapan_section_bernomor(self):
        html = self.client.get("/").get_data(as_text=True)
        for label in ("01 · Pemenang tiap kota", "02 · Cara Kerja",
                      "03 · Kriteria &amp; Bobot",
                      "04 · SAW vs TOPSIS per kota", "05 · Lab Simulasi",
                      "06 · Dua Metode", "07 · Tanya Jawab", "08 · Mulai"):
            self.assertIn(label, html)

    def test_tabel_saw_vs_topsis_lima_baris(self):
        # Pengganti Peringkat Nasional: 5 baris, satu per kota, dengan
        # kolom Sama/Berbeda. Tanpa grafik batang lintas kota.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Pemenang SAW dan TOPSIS per kota", html)
        self.assertIn("Pemenang SAW", html)
        self.assertNotIn("grafik", html)
        self.assertEqual(html.count("<td>Berbeda</td>"), 1)

    def test_lab_hanya_teaser_tanpa_simulator_kedua(self):
        # /lab sudah ada dan itu satu-satunya simulator; beranda hanya
        # teaser dengan 5 bobot asli + tombol ke /lab, tanpa slider.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="lab-banner"', html)
        self.assertIn("Ubah bobotnya, lihat pemenangnya berubah", html)
        for bobot in ("0,30", "0,25", "0,20", "0,15", "0,10"):
            self.assertIn(bobot, html)
        self.assertNotIn('type="range"', html)
        self.assertNotIn("slider", html.lower())

    def test_dua_metode_dengan_rumus_dan_catatan_jakarta(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Vi = jumlah (wj × rj)", html)
        self.assertIn("Ci = D− / (D+ + D−)", html)
        self.assertIn("SAW memilih Paket 18, TOPSIS memilih Paket 8", html)
        self.assertIn("4 dari 5 kota pemenangnya sama", html)

    def test_faq_jawaban_jujur(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Apakah TripRank bisa dipakai untuk memesan paket?",
                      html)
        self.assertIn("Tidak. TripRank hanya alat bantu keputusan", html)
        self.assertIn("Bisakah saya memakai bobot sendiri?", html)

    def test_gambar_bandung_tampil(self):
        # Bandung wajib tampil benar di panel kota hero, bukan
        # placeholder abu-abu seperti di desain pen.dev.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("pomaii-kota-bandung.jpg", html)
        resp = self.client.get("/static/images/pomaii-kota-bandung.jpg")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.get_data()), 10 * 1024)

    def test_semua_halaman_publik_200(self):
        # /rekomendasi tanpa parameter kota memang 404 (jalur 404 yang
        # sudah diuji di test_lab.py); yang diuji di sini adalah URL
        # rekomendasi dengan parameter, seperti yang dikirim filter bar.
        for url in ("/", "/tentang", "/cara-kerja", "/lab",
                    "/rekomendasi?kota=Jakarta&metode=keduanya",
                    "/rekomendasi?kota=Jakarta&metode=saw",
                    "/rekomendasi?kota=Bandung&metode=topsis",
                    "/kota/Jakarta", "/kota/Yogyakarta", "/kota/Bandung",
                    "/kota/Semarang", "/kota/Surabaya",
                    "/paket/18", "/paket/8", "/paket/27", "/paket/47",
                    "/paket/72", "/paket/83", "/admin/login"):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, url)

    def test_api_ranking_tidak_berubah(self):
        # Ranking SAW/TOPSIS 5 kota tetap sama seperti sebelum redesign.
        for kota, saw, topsis in (
                ("Jakarta", 18, 8), ("Yogyakarta", 27, 27),
                ("Bandung", 47, 47), ("Semarang", 72, 72),
                ("Surabaya", 83, 83)):
            saw_resp = self.client.get("/api/kota/%s/saw" % kota)
            self.assertEqual(saw_resp.status_code, 200, kota)
            self.assertEqual(saw_resp.get_json()["ranking"][0]["paket"],
                             saw, kota)
            topsis_resp = self.client.get("/api/kota/%s/topsis" % kota)
            self.assertEqual(topsis_resp.status_code, 200, kota)
            self.assertEqual(topsis_resp.get_json()["ranking"][0]["paket"],
                             topsis, kota)


if __name__ == "__main__":
    unittest.main()
