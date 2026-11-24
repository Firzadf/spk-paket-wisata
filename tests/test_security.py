"""Uji pengerasan keamanan admin: CSRF, batas percobaan login,
flag cookie sesi, dan peringatan demo Vercel.
"""

import os
from unittest import mock

from base import TripRankTestCase
from app import app


class CsrfTest(TripRankTestCase):
    def test_post_admin_tanpa_token_ditolak_400(self):
        r = self.client.post("/admin/login", data={
            "username": "admin", "password": "admin123"})
        self.assertEqual(r.status_code, 400)

    def test_post_admin_token_salah_ditolak_400(self):
        self.client.get("/admin/login")  # buat sesi + token asli
        r = self.client.post("/admin/login", data={
            "username": "admin", "password": "admin123",
            "csrf_token": "token-palsu"})
        self.assertEqual(r.status_code, 400)

    def test_post_admin_tanpa_login_tapi_token_salah_tetap_400(self):
        r = self.client.post("/admin/kriteria", data={
            "bobot_C1": "0.30", "csrf_token": "token-palsu"})
        self.assertEqual(r.status_code, 400)

    def test_form_admin_memuat_token_csrf(self):
        self.login_admin()
        for url in ["/admin/kriteria", "/admin/paket/1/nilai",
                    "/admin/simulasi"]:
            html = self.client.get(url).get_data(as_text=True)
            self.assertIn('name="csrf_token"', html, url)


class LoginRateLimitTest(TripRankTestCase):
    def test_lima_gagal_lalu_diblokir_15_menit(self):
        for _ in range(5):
            r = self.post_admin("/admin/login",
                                {"username": "admin", "password": "salah"},
                                form_url="/admin/login")
            self.assertIn("Nama pengguna atau kata sandi salah",
                          r.get_data(as_text=True))
        # Percobaan ke-6, meski kata sandi benar, tetap diblokir.
        r = self.post_admin("/admin/login",
                            {"username": "admin", "password": "admin123"},
                            form_url="/admin/login")
        self.assertIn("Terlalu banyak percobaan gagal",
                      r.get_data(as_text=True))

    def test_login_benar_mereset_hitungan_gagal(self):
        for _ in range(4):
            self.post_admin("/admin/login",
                            {"username": "admin", "password": "salah"},
                            form_url="/admin/login")
        r = self.login_admin()
        self.assertEqual(r.status_code, 302)
        # Setelah sukses, 4 gagal baru tidak memblokir.
        for _ in range(4):
            self.post_admin("/admin/login",
                            {"username": "admin", "password": "salah"},
                            form_url="/admin/login")
        r = self.login_admin()
        self.assertEqual(r.status_code, 302)


class SessionCookieTest(TripRankTestCase):
    def test_flag_cookie_sesi(self):
        self.assertTrue(app.config["SESSION_COOKIE_HTTPONLY"])
        self.assertEqual(app.config["SESSION_COOKIE_SAMESITE"], "Lax")


class VercelNoticeTest(TripRankTestCase):
    def test_peringatan_muncul_di_vercel_tidak_di_lokal(self):
        self.login_admin()
        html = self.client.get("/admin").get_data(as_text=True)
        self.assertNotIn("tidak permanen", html)
        with mock.patch.dict(os.environ, {"VERCEL": "1"}):
            html = self.client.get("/admin").get_data(as_text=True)
        self.assertIn("tidak permanen", html)
        # Halaman publik tidak menampilkan peringatan admin.
        with mock.patch.dict(os.environ, {"VERCEL": "1"}):
            html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("tidak permanen", html)
