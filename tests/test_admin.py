"""Uji alur admin: login, proteksi halaman, ubah kriteria/nilai, simulasi.

Semua tulis memakai salinan database sementara (lihat base.py),
jadi database resmi tidak berubah apa pun yang dilakukan tes ini.
"""

from base import TripRankTestCase
import database  # noqa: E402  (base.py sudah mengatur sys.path)

BOBOT_RESMI = {"bobot_C1": "0.30", "bobot_C2": "0.25", "bobot_C3": "0.20",
               "bobot_C4": "0.15", "bobot_C5": "0.10"}
TIPE_RESMI = {"tipe_C1": "Cost", "tipe_C2": "Benefit", "tipe_C3": "Benefit",
              "tipe_C4": "Benefit", "tipe_C5": "Benefit"}


class AdminLoginTest(TripRankTestCase):
    def test_halaman_admin_tanpa_login_dialihkan(self):
        for url in ["/admin", "/admin/kriteria", "/admin/paket",
                    "/admin/simulasi"]:
            r = self.client.get(url, follow_redirects=False)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/admin/login", r.headers["Location"])

    def test_login_salah_menampilkan_error(self):
        r = self.post_admin("/admin/login",
                            {"username": "admin", "password": "salah"},
                            form_url="/admin/login")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Nama pengguna atau kata sandi salah",
                      r.get_data(as_text=True))

    def test_login_benar_masuk_dashboard(self):
        r = self.login_admin()
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/admin"))
        r = self.client.get("/admin")
        self.assertEqual(r.status_code, 200)

    def test_logout_menghapus_sesi(self):
        self.login_admin()
        self.client.get("/admin/logout")
        r = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/admin/login", r.headers["Location"])


class AdminKriteriaTest(TripRankTestCase):
    def setUp(self):
        super().setUp()
        self.login_admin()

    def test_ubah_bobot_valid_tersimpan(self):
        r = self.post_admin("/admin/kriteria",
                            {**BOBOT_RESMI, **TIPE_RESMI})
        r = self.client.get("/admin/kriteria")
        self.assertIn("Kriteria berhasil disimpan",
                      r.get_data(as_text=True))
        weights, _, _ = database.get_weights_and_types()
        self.assertEqual(weights, [0.30, 0.25, 0.20, 0.15, 0.10])

    def test_total_bobot_salah_ditolak_dan_tidak_tersimpan(self):
        data = {**BOBOT_RESMI, **TIPE_RESMI, "bobot_C1": "0.50"}
        r = self.post_admin("/admin/kriteria", data)
        self.assertIn("Total bobot harus 1,00", r.get_data(as_text=True))
        weights, _, _ = database.get_weights_and_types()
        self.assertEqual(weights, [0.30, 0.25, 0.20, 0.15, 0.10])

    def test_tipe_tidak_valid_ditolak(self):
        data = {**BOBOT_RESMI, **TIPE_RESMI, "tipe_C1": "Acak"}
        r = self.post_admin("/admin/kriteria", data)
        self.assertIn("tidak valid", r.get_data(as_text=True))


class AdminNilaiTest(TripRankTestCase):
    def setUp(self):
        super().setUp()
        self.login_admin()

    def test_ubah_nilai_valid_tersimpan(self):
        r = self.post_admin("/admin/paket/1/nilai",
                            {"C1": "3", "C2": "4", "C3": "3",
                             "C4": "4", "C5": "3"},
                            form_url="/admin/paket/1/nilai")
        r = self.client.get("/admin/paket/1/nilai")
        self.assertIn("Nilai paket berhasil disimpan",
                      r.get_data(as_text=True))
        detail = database.get_paket_detail(1)
        self.assertEqual(detail["nilai"]["C2"], 4)

    def test_nilai_di_luar_1_sampai_5_ditolak(self):
        r = self.post_admin("/admin/paket/1/nilai",
                            {"C1": "6", "C2": "4", "C3": "3",
                             "C4": "4", "C5": "3"},
                            form_url="/admin/paket/1/nilai")
        self.assertIn("harus antara 1 dan 5", r.get_data(as_text=True))

    def test_paket_tidak_ada_kembali_ke_daftar(self):
        r = self.client.get("/admin/paket/9999/nilai",
                            follow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/admin/paket", r.headers["Location"])


class AdminSimulasiTest(TripRankTestCase):
    def setUp(self):
        super().setUp()
        self.login_admin()

    def test_simulasi_valid_menampilkan_hasil(self):
        r = self.post_admin("/admin/simulasi", {
            "kota": "Jakarta", "bobot_C1": "0.2", "bobot_C2": "0.2",
            "bobot_C3": "0.2", "bobot_C4": "0.2", "bobot_C5": "0.2"},
            form_url="/admin/simulasi")
        html = r.get_data(as_text=True)
        self.assertIn("Hasil simulasi", html)
        self.assertIn("Paket 18", html)

    def test_simulasi_total_salah_ditolak(self):
        r = self.post_admin("/admin/simulasi", {
            "kota": "Jakarta", "bobot_C1": "0.5", "bobot_C2": "0.5",
            "bobot_C3": "0.5", "bobot_C4": "0", "bobot_C5": "0"},
            form_url="/admin/simulasi")
        self.assertIn("Total bobot simulasi harus 1,00",
                      r.get_data(as_text=True))
