"""Uji rombak v5 Tenang: tidak ada lagi gradient, transform 3D,
maskot/logo/ikon 3D, marquee, atau typewriter; font hanya 2 keluarga.

Jalankan dari root repo: python -m unittest discover -s tests -v
"""

from base import APLIKASI, TripRankTestCase

CSS = (APLIKASI / "static" / "style.css").read_text()
IMAGES = APLIKASI / "static" / "images"

HAPUS_GAMBAR = ["maskot-3d.png", "logo-3d.png",
                "icon-3d-c1.webp", "icon-3d-c2.webp", "icon-3d-c3.webp",
                "icon-3d-c4.webp", "icon-3d-c5.webp"]


class CssV5Test(TripRankTestCase):
    def test_tidak_ada_gradient(self):
        self.assertEqual(CSS.count("linear-gradient"), 0)

    def test_tidak_ada_transform_3d(self):
        for token in ("rotateX", "rotateY", "perspective("):
            self.assertEqual(CSS.count(token), 0, token)

    def test_tidak_ada_sisa_nama_3d(self):
        for token in ("bg-3d", "maskot-3d", "icon-3d", "logo-3d",
                      "trip-loader", "drift3d"):
            self.assertEqual(CSS.count(token), 0, token)

    def test_tidak_ada_marquee_atau_typewriter(self):
        for token in ("marquee", "typewriter"):
            self.assertEqual(CSS.count(token), 0, token)

    def test_tidak_ada_varian_tombol_warna(self):
        for token in ("btn-leaf", "btn-gold", "btn-sand", "btn-dark"):
            self.assertEqual(CSS.count(token), 0, token)

    def test_tidak_ada_token_font_lama(self):
        for token in ("--sans-alt", "--mono", "--brand",
                      "Playfair", "Sora", "Plex Mono", "DM Serif"):
            self.assertEqual(CSS.count(token), 0, token)

    def test_font_baru_hanya_dua_keluarga(self):
        self.assertIn('"Fraunces"', CSS)
        self.assertIn('"Space Grotesk"', CSS)


class GambarV5Test(TripRankTestCase):
    def test_gambar_3d_sudah_dihapus(self):
        for nama in HAPUS_GAMBAR:
            self.assertFalse((IMAGES / nama).exists(), nama)

    def test_logo_datar_dan_foto_kota_tetap_ada(self):
        for nama in ("logo.svg", "logo-putih.svg", "jakarta.jpg",
                     "yogyakarta.jpg", "bandung.jpg", "semarang.jpg",
                     "surabaya.jpg"):
            self.assertTrue((IMAGES / nama).exists(), nama)


class HtmlV5Test(TripRankTestCase):
    def test_home_tanpa_sisa_v4(self):
        html = self.client.get("/").get_data(as_text=True)
        for token in ("bg-3d", "maskot-3d", "icon-3d", "marquee",
                      "typewriter", "data-reveal=\"left\"",
                      "data-reveal=\"right\"", "btn-leaf", "btn-gold",
                      "btn-sand", "btn-dark"):
            self.assertNotIn(token, html, token)
        # Kalimat hero tampil utuh secara statis, tanpa pengetik.
        self.assertIn("TripRank menimbang harga, fasilitas, akses, "
                      "popularitas, dan jumlah destinasi.", html)

    def test_font_hanya_dua_keluarga(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("family=Fraunces", html)
        self.assertIn("family=Space+Grotesk", html)
        for token in ("Playfair", "family=Sora", "Plex+Mono", "DM+Serif"):
            self.assertNotIn(token, html, token)

    def test_tentang_dan_login_pakai_logo_datar(self):
        for url in ("/tentang", "/admin/login"):
            html = self.client.get(url).get_data(as_text=True)
            self.assertNotIn("logo-3d", html, url)
            self.assertNotIn("maskot-3d", html, url)
            self.assertIn("images/logo.svg", html, url)

    def test_halaman_kriteria_pakai_ikon_svg(self):
        for url in ("/cara-kerja", "/paket/18"):
            html = self.client.get(url).get_data(as_text=True)
            self.assertNotIn("icon-3d", html, url)
            self.assertIn('use href="#icon-c1"', html, url)
