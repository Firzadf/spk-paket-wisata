"""Header pil desktop, hero foto, menu profil admin, loader server
(24 Nov 2026, ADR-010)."""
import os
import unittest

from base import TripRankTestCase

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSS_PATH = os.path.join(REPO, "aplikasi", "static", "style.css")
JS_PATH = os.path.join(REPO, "aplikasi", "static", "app.js")
IMG_PATH = os.path.join(REPO, "aplikasi", "static", "images",
                        "pomaii-hero-lima-kota.jpg")


def read_css():
    with open(CSS_PATH, encoding="utf-8") as f:
        return f.read()


def read_js():
    with open(JS_PATH, encoding="utf-8") as f:
        return f.read()


class HeaderPilDesktopTest(TripRankTestCase):
    def test_pil_header_desktop_ada_radius_dan_bayangan(self):
        css = read_css()
        # Pil krem di desktop: radius penuh + bayangan, sama seperti pil HP.
        self.assertIn(".site-header .header-inner {\n    background: var(--surface); border: 1px solid var(--line); border-radius: 999px;", css)
        self.assertIn("box-shadow: 0 10px 32px rgba(20, 38, 31, 0.14), 0 2px 8px rgba(20, 38, 31, 0.08);", css)

    def test_header_tanpa_transparan_dan_tanpa_logo_putih(self):
        css = read_css()
        self.assertNotIn("is-scrolled", css)
        self.assertNotIn(".logo-light", css)
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("logo-putih.svg", html)


class HeroFotoTest(TripRankTestCase):
    def test_hero_pakai_foto_lima_landmark_dengan_overlay_datar(self):
        css = read_css()
        self.assertIn('.hero-dark {\n  background: var(--accent-deep) url("images/pomaii-hero-lima-kota.jpg") center 30%/cover no-repeat;', css)
        self.assertIn(".hero-dark::before {", css)
        self.assertIn("rgba(18, 46, 35, 0.68)", css)
        self.assertNotIn("linear-gradient", css)
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="hero-dark"', html)

    def test_gambar_hero_ada_dan_terkompresi(self):
        self.assertTrue(os.path.exists(IMG_PATH))
        self.assertLess(os.path.getsize(IMG_PATH), 500 * 1024)
        resp = self.client.get("/static/images/pomaii-hero-lima-kota.jpg")
        self.assertEqual(resp.status_code, 200)


class MenuProfilAdminTest(TripRankTestCase):
    def test_belum_login_tanpa_menu_profil(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Masuk Admin", html)
        self.assertIn('class="header-action"', html)
        self.assertNotIn("profile-menu", html)
        self.assertNotIn("Keluar (admin)", html)

    def test_login_menu_profil_bukan_tautan_keluar(self):
        self.login_admin()
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("profile-menu", html)
        self.assertIn("profile-avatar", html)
        self.assertIn("profile-dropdown", html)
        self.assertIn("Dasbor Admin", html)
        self.assertIn("/admin/logout", html)
        self.assertNotIn("Keluar (admin)", html)
        self.assertNotIn('class="header-action"', html)


class LoaderServerTest(TripRankTestCase):
    def test_loader_ada_di_html_sejak_awal(self):
        # ADR-010: loader dirender server supaya menutupi layar sejak
        # paint pertama; halaman tujuan tidak sempat ke-paint dulu.
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="trip-loader"', html)
        self.assertIn("logo-3d.png", html)
        self.assertIn("loader-word", html)
        self.assertIn("loader-bar", html)

    def test_loader_tidak_tampil_tanpa_js_atau_reduced_motion(self):
        css = read_css()
        self.assertIn(".trip-loader {\n  position: fixed; inset: 0; z-index: 100; background: var(--ground);\n  display: none;", css)
        self.assertIn(".js .trip-loader { display: flex; }", css)
        self.assertIn("@media (prefers-reduced-motion: reduce) { .js .trip-loader { display: none; } }", css)

    def test_js_hanya_menyembunyikan_loader_bukan_membuat(self):
        js = read_js()
        self.assertNotIn("buildLoader", js)
        self.assertIn('document.querySelector(".trip-loader")', js)
        self.assertNotIn("is-scrolled", js)


if __name__ == "__main__":
    unittest.main()
