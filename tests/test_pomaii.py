"""Tes redesign gaya Pomaii (24 Nov 2026, referensi landing travel Pomaii).

Diambil struktur dan presisinya, BUKAN isinya: tanpa rating bintang,
tanpa harga, tanpa testimoni, tanpa klaim jumlah traveler. Hanya angka
nyata (5 kota, 100 paket, 298 tempat, 403 relasi).

Gambar (aturan final user 24 Nov 2026 09:32 WIB): generate AI boleh
dipakai untuk gambar apa pun dan label "Ilustrasi AI" TIDAK diperlukan
di mana pun. Yang wajib hanya kredit fotografer Wikimedia untuk foto
asli yang dipakai (syarat lisensi CC). Beranda ADR-009 memakai hero
gelap + 5 panel kota AI (pomaii-kota-*.jpg); hero foto lima landmark
dan 2 gambar cerita tidak lagi dirujuk di beranda.
"""
import unittest

from base import TripRankTestCase


class TestPomaii(TripRankTestCase):
    def test_home_punya_form_filter_ke_rekomendasi(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="filter-bar"', html)
        self.assertIn('action="/rekomendasi"', html)
        self.assertIn('name="kota"', html)
        self.assertIn('name="metode"', html)
        for kota in ("Jakarta", "Yogyakarta", "Bandung", "Semarang", "Surabaya"):
            self.assertIn('value="%s"' % kota, html)
        for metode in ("keduanya", "saw", "topsis"):
            self.assertIn('value="%s"' % metode, html)
        # Label opsi singkat (ADR-008): "Keduanya" supaya teks tidak
        # terpotong di select filter bar HP yang sempit.

    def test_filter_bar_jalan_tanpa_js(self):
        # GET nyata ke /rekomendasi, sama seperti form submit browser.
        resp = self.client.get(
            "/rekomendasi?kota=Bandung&metode=saw")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Bandung", html)
        self.assertIn("Paket 47", html)

    def test_home_punya_strip_statistik_angka_nyata(self):
        # ADR-009: trust strip diganti strip statistik di hero gelap.
        # Hanya angka nyata (100 paket, 5 kota, 5 kriteria, 2 metode),
        # tanpa Spearman dan tanpa klaim lain.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="hero-stats"', html)
        for item in ("paket dinilai", "kota besar", "kriteria", "metode"):
            self.assertIn(item, html)
        for klaim in ("Spearman", "Happy Travelers", "Best Price", "4.8",
                      "$699"):
            self.assertNotIn(klaim, html)

    def test_home_punya_lima_panel_kota_berfoto(self):
        # ADR-009: kartu kota diganti 5 panel kota di hero gelap,
        # masing-masing berfoto dan bertautan ke halaman kota.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="hero-city-panels"', html)
        for kota in ("Jakarta", "Yogyakarta", "Bandung", "Semarang",
                     "Surabaya"):
            self.assertIn(kota, html)
        for slug in ("jakarta", "yogyakarta", "bandung", "semarang",
                     "surabaya"):
            self.assertIn("pomaii-kota-%s.jpg" % slug, html)
        self.assertIn("20 paket", html)

    def test_home_kredit_wikimedia_foto_asli_tanpa_label_ai(self):
        # ADR-007 (24 Nov 2026): kartu kota di beranda kini memakai gambar
        # AI (pomaii-kota-*.jpg) atas perintah user, jadi foto asli tidak
        # lagi tampil di beranda. Kredit Wikimedia tetap ada: kalimat
        # footer menjelaskan foto asli dipakai di halaman Tentang, dan
        # halaman Tentang tetap menampilkan foto asli + kredit lengkap.
        # Tidak ada label "Ilustrasi AI" (aturan final user 24 Nov 2026).
        # ADR-009: hero foto lima landmark (pomaii-hero-lima-kota.jpg)
        # dan 2 gambar cerita tidak lagi dirujuk di beranda; beranda
        # memakai hero gelap + panel kota AI + banner Lab.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Wikimedia Commons", html)
        self.assertNotIn("Ilustrasi AI", html)
        self.assertNotIn("pomaii-hero-lima-kota.jpg", html)
        self.assertNotIn("pomaii-stories-1.jpg", html)
        self.assertNotIn("pomaii-stories-2.jpg", html)
        self.assertIn("pomaii-lab.jpg", html)
        # Kartu kota memakai gambar AI, bukan foto asli.
        for slug in ("jakarta", "yogyakarta", "bandung", "semarang", "surabaya"):
            self.assertIn("pomaii-kota-%s.jpg" % slug, html)
        self.assertNotIn("/static/images/jakarta.jpg", html)
        tentang = self.client.get("/tentang").get_data(as_text=True)
        self.assertIn("/static/images/jakarta.jpg", tentang)
        self.assertIn("Wikimedia Commons", tentang)

    def test_home_punya_kartu_kriteria_dan_banner_lab(self):
        # ADR-009: pill kriteria diganti 5 kartu kriteria (bobot besar
        # + sumber data); banner Lab tetap.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="criteria-cards"', html)
        for bobot in ("0,30", "0,25", "0,20", "0,15", "0,10"):
            self.assertIn(bobot, html)
        self.assertIn('class="lab-banner"', html)
        self.assertIn("Ubah bobotnya, lihat pemenangnya berubah", html)

    def test_home_tanpa_typewriter_dan_tanpa_marquee(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("data-typewriter", html)
        self.assertNotIn("marquee", html)

    def test_css_tanpa_gradient_dan_tanpa_emas(self):
        css = self.client.get("/static/style.css").get_data(as_text=True)
        self.assertNotIn("linear-gradient", css)
        for emas in ("#e8b64a", "#c98f2d", "#9a6b1a"):
            self.assertNotIn(emas, css)

    def test_css_punya_cta_oranye_dan_radius_kartu(self):
        css = self.client.get("/static/style.css").get_data(as_text=True)
        self.assertIn("--cta: #c2410c", css)
        self.assertIn(".btn-cta", css)
        self.assertIn("--radius-card: 18px", css)
        self.assertIn("border-radius: 999px", css)

    def test_font_hanya_dua_keluarga(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("family=Fraunces", html)
        self.assertIn("family=Space+Grotesk", html)
        for font_lama in ("Playfair+Display", "Sora", "IBM+Plex+Mono",
                          "DM+Serif+Display"):
            self.assertNotIn(font_lama, html)


if __name__ == "__main__":
    unittest.main()
