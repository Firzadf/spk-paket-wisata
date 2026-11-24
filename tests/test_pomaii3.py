"""Tes hero gelap pen.dev (24 Nov 2026, ADR-009): menggantikan hero foto
Pomaii 3 (ADR-008). Hero gelap datar ala desain pen.dev user, huruf "g"
tidak terpotong, pemenang pindah ke section 01 dengan nama paket asli,
filter bar dalam alur normal (bukan menumpuk)."""
import os
import unittest

from base import TripRankTestCase

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSS_PATH = os.path.join(REPO, "aplikasi", "static", "style.css")
IMG_DIR = os.path.join(REPO, "aplikasi", "static", "images")


def read_css():
    with open(CSS_PATH, encoding="utf-8") as f:
        return f.read()


class HeroGelapTest(TripRankTestCase):
    def test_home_pakai_hero_gelap_bukan_foto_lima_kota(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="hero-dark"', html)
        self.assertIn("Pilih paket wisata", html)
        self.assertIn("Anda pertanggungjawabkan.", html)
        # Gambar lima landmark tidak lagi dirujuk di beranda (file-nya
        # tetap ada, tapi hero kini field hijau gelap datar).
        self.assertNotIn("pomaii-hero-lima-kota.jpg", html)
        self.assertNotIn("pomaii-hero-ai.jpg", html)

    def test_gambar_kota_bandung_ter_load(self):
        # Bandung wajib tampil benar di panel kota hero (bukan
        # placeholder abu-abu seperti di desain pen.dev).
        path = os.path.join(IMG_DIR, "pomaii-kota-bandung.jpg")
        self.assertTrue(os.path.exists(path))
        resp = self.client.get("/static/images/pomaii-kota-bandung.jpg")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.get_data()), 10 * 1024)


class HurufGTidakTerpotongTest(TripRankTestCase):
    def test_line_punya_ruang_descender(self):
        css = read_css()
        # .line tetap overflow hidden untuk animasi reveal, tapi diberi
        # padding-bottom supaya descender "g" tidak terpotong.
        self.assertIn("padding-bottom: 0.16em; margin-bottom: -0.16em;", css)
        self.assertIn(".hero-dark h1 {\n  color: var(--accent-ink);"
                      " margin: 0 0 16px; max-width: 760px;\n"
                      "  font-size: clamp(40px, 5.8vw, 64px);"
                      " line-height: 1.12;", css)


class KartuPemenangSectionTest(TripRankTestCase):
    def test_kartu_pemenang_ada_dengan_nama_paket_asli(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="winner-cards"', html)
        self.assertNotIn("hero-winners", html)
        # Nama paket pemenang asli dari database, bukan nomor saja.
        for nama in ("Paket 18 - Jakarta", "Paket 8 - Jakarta",
                     "Paket 27 - Yogyakarta", "Paket 47 - Bandung",
                     "Paket 72 - Semarang", "Paket 83 - Surabaya"):
            self.assertIn(nama, html)
        # Skor resmi tiap kota (format titik, sesuai template).
        for skor in ("0.8388", "0.7965", "0.9241", "0.7629", "0.8258",
                     "0.6933", "0.8217", "0.6795", "0.8730", "0.7170"):
            self.assertIn(skor, html)

    def test_jakarta_satu_satunya_yang_beda(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Satu-satunya kota yang pemenangnya berbeda", html)
        self.assertEqual(
            html.count("Satu-satunya kota yang pemenangnya berbeda"), 1)

    def test_kartu_pemenang_tautan_ke_rekomendasi(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("/rekomendasi?kota=Jakarta", html)


class FilterBarDalamAlurTest(TripRankTestCase):
    def test_filter_bar_tidak_lagi_menumpuk(self):
        css = read_css()
        # ADR-009: filter bar duduk di bawah hero dalam alur normal,
        # tumpangan -118px ala ADR-008 dibatalkan.
        self.assertIn("margin: 32px auto 96px;", css)
        self.assertNotIn("margin: -118px auto 0;", css)
        self.assertNotIn(".hero-winners { position: absolute; top: 50%;"
                         " right: 24px; transform: translateY(-50%);"
                         " z-index: 2; width: 360px; margin: 0; }", css)

    def test_header_hp_di_beranda_fixed_dan_hero_mulai_dari_atas(self):
        css = read_css()
        # Header pil di beranda HP tetap fixed (bukan sticky) supaya
        # hero gelap memenuhi layar dari atas; padding atas hero
        # memberi ruang untuk pil header yang mengambang.
        self.assertIn("body.home-hero .site-header { position: fixed;"
                      " top: 10px; left: 0; right: 0; }", css)
        self.assertIn(".hero-dark-inner { padding: 88px 20px 48px; }", css)


if __name__ == "__main__":
    unittest.main()
