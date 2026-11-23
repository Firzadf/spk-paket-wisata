"""Seed database dari data Langkah 2.

Cara pakai:
  .venv/bin/python seed.py --force        (Windows: .venv\\Scripts\\python seed.py --force)
Tanpa --force, seed berhenti bila database sudah berisi paket, supaya data admin
yang sudah diubah tidak tertimpa diam-diam.

PENTING: file ini sengaja dibuat bisa jalan dari folder aplikasi saja.
- Skema dicari dulu di beberapa lokasi, kalau tidak ketemu dipakai skema bawaan di bawah.
- File dataset dicari dulu di beberapa lokasi. Semua file input dicek SEBELUM database lama
  dihapus, supaya seed yang gagal tidak meninggalkan database kosong.
- Kalau dataset tidak ketemu tapi spk_wisata.db sudah ada, seed tidak perlu dijalankan:
  langsung saja jalankan app.py, karena database itu sudah berisi data.

Akun demo admin: admin / admin123. Kata sandi disimpan sebagai hash.
Ganti kata sandi ini sebelum pemakaian nyata.
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE = Path(__file__).parent
PROJECT = BASE.parent
DB_PATH = BASE / "spk_wisata.db"

# Skema bawaan, sama persis dengan perancangan/02-skema-database.sql.
# Dipakai hanya bila file skema tidak ditemukan di mana pun.
EMBEDDED_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS kota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS paket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kota_id INTEGER NOT NULL,
    nomor_paket INTEGER NOT NULL UNIQUE,
    nama_tampil TEXT NOT NULL,
    FOREIGN KEY (kota_id) REFERENCES kota (id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS tempat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL UNIQUE,
    kategori TEXT NOT NULL,
    skor_c1 REAL NOT NULL CHECK (skor_c1 BETWEEN 1 AND 5),
    skor_c2 REAL NOT NULL CHECK (skor_c2 BETWEEN 1 AND 5),
    skor_c3 REAL NOT NULL CHECK (skor_c3 BETWEEN 1 AND 5),
    skor_c4 REAL NOT NULL CHECK (skor_c4 BETWEEN 1 AND 5)
);
CREATE TABLE IF NOT EXISTS paket_tempat (
    paket_id INTEGER NOT NULL,
    tempat_id INTEGER NOT NULL,
    urutan INTEGER NOT NULL,
    PRIMARY KEY (paket_id, tempat_id),
    FOREIGN KEY (paket_id) REFERENCES paket (id) ON DELETE CASCADE,
    FOREIGN KEY (tempat_id) REFERENCES tempat (id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS kriteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT NOT NULL UNIQUE,
    nama TEXT NOT NULL,
    tipe TEXT NOT NULL CHECK (tipe IN ('Benefit', 'Cost')),
    bobot REAL NOT NULL CHECK (bobot >= 0 AND bobot <= 1)
);
CREATE TABLE IF NOT EXISTS nilai_paket (
    paket_id INTEGER NOT NULL,
    kriteria_id INTEGER NOT NULL,
    nilai REAL NOT NULL CHECK (nilai BETWEEN 1 AND 5),
    PRIMARY KEY (paket_id, kriteria_id),
    FOREIGN KEY (paket_id) REFERENCES paket (id) ON DELETE CASCADE,
    FOREIGN KEY (kriteria_id) REFERENCES kriteria (id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
INSERT OR IGNORE INTO kriteria (kode, nama, tipe, bobot) VALUES
    ('C1', 'Harga Paket', 'Cost', 0.30),
    ('C2', 'Fasilitas', 'Benefit', 0.25),
    ('C3', 'Aksesibilitas Lokasi', 'Benefit', 0.20),
    ('C4', 'Popularitas Destinasi', 'Benefit', 0.15),
    ('C5', 'Jumlah Destinasi', 'Benefit', 0.10);
INSERT OR IGNORE INTO kota (nama) VALUES
    ('Jakarta'), ('Yogyakarta'), ('Bandung'), ('Semarang'), ('Surabaya');
"""


def find_file(*candidates):
    for c in candidates:
        if c.is_file():
            return c
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Hapus database lama dan seed ulang")
    args = parser.parse_args()

    if DB_PATH.exists() and not args.force:
        conn = sqlite3.connect(DB_PATH)
        try:
            count = conn.execute("SELECT COUNT(*) FROM paket").fetchone()[0]
        except sqlite3.Error:
            count = 0
        finally:
            conn.close()
        if count > 0:
            print(f"Database sudah berisi {count} paket. Pakai --force untuk seed ulang.")
            return 0

    # Cari semua input SEBELUM menghapus database lama.
    schema_path = find_file(
        PROJECT / "perancangan" / "02-skema-database.sql",
        BASE / "perancangan" / "02-skema-database.sql",
        BASE / "02-skema-database.sql",
    )
    dataset_path = find_file(
        PROJECT / "data" / "dataset_nilai_kriteria.csv",
        BASE / "data" / "dataset_nilai_kriteria.csv",
        BASE / "dataset_nilai_kriteria.csv",
    )
    klasifikasi_path = find_file(
        PROJECT / "data" / "klasifikasi_tempat.csv",
        BASE / "data" / "klasifikasi_tempat.csv",
        BASE / "klasifikasi_tempat.csv",
    )
    if dataset_path is None or klasifikasi_path is None:
        print("Seed dibatalkan: file dataset tidak ditemukan.")
        print("Yang dicari:")
        print(f"  - dataset_nilai_kriteria.csv di: {PROJECT / 'data'} atau {BASE / 'data'} atau {BASE}")
        print(f"  - klasifikasi_tempat.csv di: {PROJECT / 'data'} atau {BASE / 'data'} atau {BASE}")
        if DB_PATH.exists():
            print("Database lama TIDAK dihapus. Langsung saja jalankan app.py, karena database itu sudah berisi data.")
        else:
            print("Database belum ada. Salin folder data dari paket proyek, atau pakai file spk_wisata.db yang sudah ada di zip aplikasi.")
        return 1
    if schema_path is not None:
        schema_sql = schema_path.read_text(encoding="utf-8")
        print(f"Memakai skema dari: {schema_path}")
    else:
        schema_sql = EMBEDDED_SCHEMA
        print("File skema tidak ditemukan, memakai skema bawaan di dalam seed.py.")

    if args.force and DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(schema_sql)
        tempat_id = {}
        with open(klasifikasi_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cur = conn.execute(
                    "INSERT INTO tempat (nama, kategori, skor_c1, skor_c2, skor_c3, skor_c4) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (r["Place"], r["Category"], float(r["C1_Harga_Cost"]), float(r["C2_Fasilitas_Benefit"]),
                     float(r["C3_Aksesibilitas_Benefit"]), float(r["C4_Popularitas_Benefit"])),
                )
                tempat_id[r["Place"]] = cur.lastrowid
        kota_id = {r[1]: r[0] for r in conn.execute("SELECT id, nama FROM kota").fetchall()}
        kriteria_id = {r[1]: r[0] for r in conn.execute("SELECT id, kode FROM kriteria").fetchall()}
        with open(dataset_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                nomor = int(r["Package"])
                kota = r["City"]
                cur = conn.execute(
                    "INSERT INTO paket (kota_id, nomor_paket, nama_tampil) VALUES (?, ?, ?)",
                    (kota_id[kota], nomor, f"Paket {nomor} - {kota}"),
                )
                paket_id = cur.lastrowid
                places = [p.strip() for p in r["Places"].split("|") if p.strip()]
                for urutan, nama in enumerate(places, start=1):
                    conn.execute(
                        "INSERT INTO paket_tempat (paket_id, tempat_id, urutan) VALUES (?, ?, ?)",
                        (paket_id, tempat_id[nama], urutan),
                    )
                nilai_map = {
                    "C1": float(r["C1_Harga_Cost"]),
                    "C2": float(r["C2_Fasilitas_Benefit"]),
                    "C3": float(r["C3_Aksesibilitas_Benefit"]),
                    "C4": float(r["C4_Popularitas_Benefit"]),
                    "C5": float(r["C5_Jumlah_Destinasi_Benefit"]),
                }
                for kode, val in nilai_map.items():
                    conn.execute(
                        "INSERT INTO nilai_paket (paket_id, kriteria_id, nilai) VALUES (?, ?, ?)",
                        (paket_id, kriteria_id[kode], val),
                    )
        conn.execute(
            "INSERT OR REPLACE INTO admin (id, username, password_hash) VALUES (1, ?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        conn.commit()
        counts = {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ["kota", "paket", "tempat", "paket_tempat", "kriteria", "nilai_paket"]
        }
        print(f"Seed selesai: {DB_PATH}")
        print(counts)
        print("Akun demo admin: admin / admin123 (ganti sebelum pemakaian nyata)")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
