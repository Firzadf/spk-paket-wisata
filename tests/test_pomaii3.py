"""Tes hero Pomaii 3 (24 Nov 2026, ADR-008): gambar utama lima landmark,
huruf "g" tidak terpotong, kartu pemenang di sisi kanan hero, hero pas
satu layar saat landing (panel + tombol + filter bar terlihat penuh)."""
import os
import unittest

from base import TripRankTestCase

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSS_PATH = os.path.join(REPO, "aplikasi", "static", "style.css")
IMG_PATH = os.path.join(REPO, "aplikasi", "static", "images",
                        "pomaii-hero-lima-kota.jpg")


def read_css():
    with open(CSS_PATH, encoding="utf-8") as f:
        return f.read()


class GambarUtamaLimaKotaTest(TripRankTestCase):
    def test_home_pakai_gambar_lima_kota_bukan_hero_lama(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("pomaii-hero-lima-kota.jpg", html)
        self.assertNotIn("pomaii-hero-ai.jpg", html)

    def test_gambar_hero_ada_dan_terkompresi(self):
        self.assertTrue(os.path.exists(IMG_PATH))
        # JPG 1920px, di bawah 500 KB supaya hero cepat dimuat.
        self.assertLess(os.path.getsize(IMG_PATH), 500 * 1024)

    def test_gambar_hero_ter_load(self):
        resp = self.client.get("/static/images/pomaii-hero-lima-kota.jpg")
        self.assertEqual(resp.status_code, 200)


class HurufGTidakTerpotongTest(TripRankTestCase):
    def test_line_punya_ruang_descender(self):
        css = read_css()
        # .line tetap overflow hidden untuk animasi reveal, tapi diberi
        # padding-bottom supaya descender "g" tidak terpotong.
        self.assertIn("padding-bottom: 0.16em; margin-bottom: -0.16em;", css)
        self.assertIn(".hero-pomaii-body h1 {\n  color: var(--ink);"
                      " margin: 0 0 16px; max-width: 640px;\n"
                      "  font-size: clamp(40px, 5.8vw, 64px);"
                      " line-height: 1.12;", css)


class KartuPemenangHeroTest(TripRankTestCase):
    def test_kartu_pemenang_ada_dengan_data_nyata(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("hero-winners", html)
        self.assertIn("Pemenang per kota", html)
        # Pemenang resmi tiap kota, diambil dari data yang sama dengan
        # kartu kota di bawahnya.
        for kota, saw, topsis in (
                ("Jakarta", 18, 8), ("Yogyakarta", 27, 27),
                ("Bandung", 47, 47), ("Semarang", 72, 72),
                ("Surabaya", 83, 83)):
            self.assertIn(kota, html)
            self.assertIn("SAW Paket <strong>%d</strong>" % saw, html)
            self.assertIn("TOPSIS Paket <strong>%d</strong>" % topsis, html)

    def test_kartu_pemenang_tautan_ke_rekomendasi(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("/rekomendasi?kota=Jakarta", html)


class HeroPasSatuLayarTest(TripRankTestCase):
    def test_filter_bar_menumpuk_cukup_tinggi(self):
        css = read_css()
        # Tumpangan -118px supaya seluruh filter bar terlihat dalam satu
        # viewport 900px saat landing.
        self.assertIn("margin: -118px auto 0;", css)

    def test_kartu_pemenang_absolut_di_kanan_hero_desktop(self):
        css = read_css()
        # Desktop: kartu diposisikan absolut di kanan hero (sejajar
        # vertikal dengan panel). Di HP ia mengalir normal di bawah
        # filter bar, jadi tidak pernah tertutup.
        self.assertIn(".hero-winners { position: absolute; top: 50%;"
                      " right: 24px; transform: translateY(-50%);"
                      " z-index: 2; width: 360px; margin: 0; }", css)

    def test_header_hp_di_beranda_fixed_dan_body_mulai_dari_atas(self):
        css = read_css()
        # Header pil di beranda HP fixed (bukan sticky) supaya foto
        # memenuhi layar dari atas; panel mulai dari atas, bukan di
        # tengah, supaya filter bar muat dalam satu viewport 844px.
        self.assertIn("body.home-hero .site-header { position: fixed;"
                      " top: 10px; left: 0; right: 0; }", css)
        self.assertIn(".hero-pomaii-body { padding: 88px 20px 24px;"
                      " justify-content: flex-start; }", css)


if __name__ == "__main__":
    unittest.main()
