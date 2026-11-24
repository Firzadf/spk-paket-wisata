"""Uji polish v4.1: tombol datar tanpa gradient/emas, marquee hilang,
animasi 3D tetap ada, halaman rekomendasi rata tengah.
"""

from base import APLIKASI, TripRankTestCase


class V41CssTest(TripRankTestCase):
    def setUp(self):
        super().setUp()
        self.css = (APLIKASI / "static" / "style.css").read_text()

    def test_tanpa_gradient(self):
        self.assertEqual(self.css.lower().count("linear-gradient"), 0)

    def test_tanpa_warna_emas(self):
        for kode in ("#e8b64a", "#c98f2d", "#9a6b1a"):
            self.assertEqual(self.css.lower().count(kode), 0, kode)

    def test_tanpa_varian_tombol_lama(self):
        for kelas in ("btn-gold", "btn-leaf", "btn-sand", "btn-dark"):
            self.assertNotIn(kelas, self.css, kelas)

    def test_tombol_primer_datar_hijau_gelap(self):
        self.assertIn(".btn, button {\n  background: var(--accent);",
                      self.css)

    def test_animasi_3d_tetap_ada(self):
        for penanda in ("bg-3d", "drift3d-a", "pageEnter3d", "loaderBar"):
            self.assertIn(penanda, self.css, penanda)


class V41HtmlTest(TripRankTestCase):
    def test_home_tanpa_marquee_dan_tanpa_tombol_emas(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("marquee", html)
        for kelas in ("btn-gold", "btn-leaf", "btn-sand", "btn-dark"):
            self.assertNotIn(kelas, html, kelas)

    def test_home_tetap_punya_bg_3d_dan_typewriter(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("bg-3d", html)
        self.assertIn("data-typewriter", html)

    def test_rekomendasi_page_head_rata_tengah(self):
        html = self.client.get(
            "/rekomendasi?kota=Jakarta&metode=keduanya").get_data(as_text=True)
        self.assertIn('class="page-head center"', html)
        self.assertIn("Hanya SAW", html)
        self.assertIn("Keduanya", html)
