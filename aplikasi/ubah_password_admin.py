"""Ubah kata sandi admin di spk_wisata.db, tanpa menulis kata sandi ke file mana pun.

Jalankan dari folder aplikasi:
  python ubah_password_admin.py

Kata sandi diminta lewat getpass, jadi tidak tampil di layar, tidak tercetak
di output, dan tidak dikirim ke siapa pun. Skrip ini hanya memperbarui hash
di database lokal tempat ia dijalankan.
"""

import getpass
import sqlite3
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).parent / "spk_wisata.db"


def main():
    if not DB_PATH.exists():
        print(f"Database tidak ditemukan: {DB_PATH}")
        print("Jalankan dulu: python seed.py --force")
        return 1
    username = input("Username admin [admin]: ").strip() or "admin"
    pw1 = getpass.getpass("Kata sandi baru: ")
    pw2 = getpass.getpass("Ulangi kata sandi baru: ")
    if not pw1:
        print("Kata sandi tidak boleh kosong.")
        return 1
    if pw1 != pw2:
        print("Kata sandi tidak sama. Tidak ada yang diubah.")
        return 1
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            "UPDATE admin SET password_hash = ? WHERE username = ?",
            (generate_password_hash(pw1), username),
        )
        if cur.rowcount == 0:
            print(f"Username {username} tidak ditemukan. Tidak ada yang diubah.")
            return 1
        conn.commit()
    finally:
        conn.close()
    print(f"Kata sandi admin {username} berhasil diubah.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
