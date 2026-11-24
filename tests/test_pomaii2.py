"""Tes tata letak ala Pomaii 2 (24 Nov 2026, ADR-007): rata kiri, reveal
tanpa putaran, header transparan di atas hero full-screen, footer terang,
ikon garis, gambar AI kota, maskot Garuda, login admin rapi."""
import os
import re
import unittest
from unittest import mock

from base import TripRankTestCase

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSS_PATH = os.path.join(REPO, "aplikasi", "static", "style.css")


def read_css():
    with open(CSS_PATH, encoding="utf-8") as f:
        return f.read()


class TataLetakKiriTest(TripRankTestCase):
    def test_tidak_ada_text_align_center_di_teks_section(self):
        css = read_css()
        self.assertNotIn("main section > h2 { text-align: center; }", css)
        self.assertNotIn("main section > .section-note { text-align: center;", css)
        self.assertNotIn(".mission { text-align: center; }", css)
        self.assertNotIn(".philosophy { text-align: center; }", css)
        self.assertNotIn("text-wrap: balance", css)

    def test_home_tepi_kiri_satu_grid(self):
        # Hero, header, dan footer memakai container yang sama (1120px),
        # jadi tepi kiri teks lurus dari atas sampai bawah.
        css = read_css()
        self.assertIn(".site-header .header-inner {\n  max-width: var(--measure);", css)
        # ADR-010: padding atas hero 120px supaya eyebrow tidak
        # tertutup pil header desktop yang mengambang.
        self.assertIn("max-width: var(--measure); margin: 0 auto; padding: 120px 24px 64px;", css)
        self.assertIn(".site-footer .footer-inner { max-width: var(--measure);", css)
        self.assertNotIn("var(--measure-wide)", css)


class RevealTanpaPutaranTest(TripRankTestCase):
    def test_reveal_hanya_fade_dan_naik(self):
        css = read_css()
        reveal = re.search(r"\.js \[data-reveal[^\]]*\][^{]*\{[^}]*\}", css)
        self.assertIsNotNone(reveal)
        # Blok reveal tidak boleh mengandung putaran atau blur.
        for m in re.finditer(
                r"\.js \[data-reveal[^\]]*\][^{]*\{[^}]*\}", css):
            self.assertNotIn("rotateX", m.group(0))
            self.assertNotIn("rotateY", m.group(0))
            self.assertNotIn("blur(", m.group(0))
        self.assertIn("translateY(12px)", css)
        # Transisi 3D antar halaman dan tilt kartu tetap dipertahankan.
        self.assertIn("pageEnter3d", css)
        self.assertIn("rotateX(3deg) rotateY(-3deg)", css)

    def test_tidak_ada_rotate_di_hero_headline(self):
        css = read_css()
        self.assertNotIn("rotateX(8deg)", css)


class GambarDanMaskotTest(TripRankTestCase):
    def test_home_pakai_gambar_ai_kota_dan_maskot_garuda(self):
        html = self.client.get("/").get_data(as_text=True)
        for slug in ("jakarta", "yogyakarta", "bandung", "semarang", "surabaya"):
            self.assertIn("pomaii-kota-%s.jpg" % slug, html)
        self.assertIn("maskot-garuda-3d.png", html)

    def test_home_tanpa_maskot_lama_dan_tanpa_caption_ilustrasi(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("maskot-3d.png", html)
        self.assertNotIn("Ilustrasi 3D", html)
        tentang = self.client.get("/tentang").get_data(as_text=True)
        self.assertNotIn("maskot-3d.png", tentang)
        self.assertNotIn("Ilustrasi 3D", tentang)

    def test_ikon_kriteria_garis_bukan_3d(self):
        for url in ("/", "/cara-kerja", "/paket/18"):
            html = self.client.get(url).get_data(as_text=True)
            self.assertNotIn("icon-3d-", html)
            self.assertIn("icon-criterion", html)


class HeaderFooterPomaiiTest(TripRankTestCase):
    def test_header_pil_mengambang_di_desktop(self):
        # ADR-010: header desktop kini pil mengambang seperti HP (logo +
        # nav lengkap + Masuk Admin di dalam satu pil krem). Tidak ada
        # lagi header transparan, logo putih, atau is-scrolled.
        css = read_css()
        self.assertIn("body.home-hero .site-header { position: fixed; top: 10px; left: 0; right: 0; }", css)
        self.assertIn("position: sticky; top: 10px;", css)
        self.assertIn("border-radius: 999px;", css)
        self.assertNotIn("body.home-hero .site-header.is-scrolled {", css)
        self.assertNotIn("body.home-hero .site-header:not(.is-scrolled)", css)
        self.assertNotIn(".logo-light", css)
        self.assertNotIn("min-height: 100vh; min-height: 100svh;", css)
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="home-hero"', html)
        self.assertNotIn("logo-putih.svg", html)
        self.assertIn("/static/images/logo.svg", html)

    def test_footer_terang(self):
        css = read_css()
        self.assertIn(".site-footer { background: var(--surface);", css)
        footer = re.search(r"\.site-footer \{[^}]*\}", css)
        self.assertIsNotNone(footer)
        self.assertNotIn("accent-deep", footer.group(0))
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("/static/images/logo.svg", html)
        # ADR-010: logo putih tidak lagi dipakai di mana pun (header
        # kini pil krem dengan logo gelap).
        self.assertNotIn("logo-putih.svg", html)


class LoginAdminRapiTest(TripRankTestCase):
    def test_login_tanpa_banner_vercel_tapi_admin_tetap_ada(self):
        # Banner tidak muncul di halaman login walau VERCEL=1.
        with mock.patch.dict(os.environ, {"VERCEL": "1"}):
            login = self.client.get("/admin/login").get_data(as_text=True)
            self.assertNotIn("Demo Vercel", login)
            self.assertNotIn("tidak permanen", login)
            self.assertIn("Masuk Admin", login)
            self.assertIn("login-wrap", login)
            # Setelah login, banner tetap muncul di halaman admin.
            self.login_admin()
            admin = self.client.get("/admin").get_data(as_text=True)
            self.assertIn("tidak permanen", admin)


if __name__ == "__main__":
    unittest.main()
