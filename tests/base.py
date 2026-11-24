"""Basis uji TripRank: tiap tes memakai salinan sementara database.

Kenapa: tes admin (ubah kriteria, ubah nilai) menulis ke database.
Tanpa salinan, tes akan mengubah spk_wisata.db yang ikut ter-commit
dan merusak pemenang resmi. Salinan dibuat di setUp dan dihapus di
tearDown; database.DB_PATH dibaca ulang di setiap get_connection(),
jadi mengarahkannya ke salinan sudah cukup.
"""

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

APLIKASI = Path(__file__).resolve().parent.parent / "aplikasi"
sys.path.insert(0, str(APLIKASI))

import app as app_module  # noqa: E402
import database  # noqa: E402
from app import app  # noqa: E402


class TripRankTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        shutil.copyfile(APLIKASI / "spk_wisata.db", self._tmp.name)
        self._orig_db = database.DB_PATH
        database.DB_PATH = Path(self._tmp.name)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        database.DB_PATH = self._orig_db
        app_module._LOGIN_FAILURES.clear()
        Path(self._tmp.name).unlink(missing_ok=True)

    def csrf_token_for(self, url):
        """Ambil token CSRF dari form di halaman url."""
        html = self.client.get(url).get_data(as_text=True)
        m = re.search(r'name="csrf_token" value="([^"]+)"', html)
        self.assertIsNotNone(m, f"token CSRF tidak ditemukan di {url}")
        return m.group(1)

    def post_admin(self, url, data, form_url=None):
        """POST ke url dengan token CSRF yang diambil dari form_url
        (default: halaman yang sama)."""
        token = self.csrf_token_for(form_url or url)
        return self.client.post(url,
                                data={**data, "csrf_token": token},
                                follow_redirects=False)

    def login_admin(self):
        return self.post_admin("/admin/login",
                               {"username": "admin", "password": "admin123"},
                               form_url="/admin/login")
