"""Basis uji TripRank: tiap tes memakai salinan sementara database.

Kenapa: tes admin (ubah kriteria, ubah nilai) menulis ke database.
Tanpa salinan, tes akan mengubah spk_wisata.db yang ikut ter-commit
dan merusak pemenang resmi. Salinan dibuat di setUp dan dihapus di
tearDown; database.DB_PATH dibaca ulang di setiap get_connection(),
jadi mengarahkannya ke salinan sudah cukup.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

APLIKASI = Path(__file__).resolve().parent.parent / "aplikasi"
sys.path.insert(0, str(APLIKASI))

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
        Path(self._tmp.name).unlink(missing_ok=True)

    def login_admin(self):
        return self.client.post(
            "/admin/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False)
