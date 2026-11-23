"""Akses database SQLite untuk aplikasi SPK Paket Wisata.

Satu aturan penting: setiap koneksi mengaktifkan PRAGMA foreign_keys = ON,
supaya aturan di skema benar-benar berlaku, bukan hanya tertulis.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "spk_wisata.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_kriteria():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM kriteria ORDER BY kode").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_weights_and_types():
    krit = get_kriteria()
    weights = [r["bobot"] for r in krit]
    types = [r["tipe"] for r in krit]
    return weights, types, krit


def get_kota_list():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT k.nama, COUNT(p.id) AS jumlah FROM kota k "
            "LEFT JOIN paket p ON p.kota_id = k.id GROUP BY k.id ORDER BY k.id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_paket_by_kota(nama_kota):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT p.id, p.nomor_paket, p.nama_tampil, k.nama AS kota "
            "FROM paket p JOIN kota k ON k.id = p.kota_id "
            "WHERE k.nama = ? ORDER BY p.nomor_paket",
            (nama_kota,),
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            tempat = conn.execute(
                "SELECT t.nama FROM paket_tempat pt JOIN tempat t ON t.id = pt.tempat_id "
                "WHERE pt.paket_id = ? ORDER BY pt.urutan",
                (d["id"],),
            ).fetchall()
            d["tempat"] = [t["nama"] for t in tempat]
            nilai = conn.execute(
                "SELECT kr.kode, np.nilai FROM nilai_paket np "
                "JOIN kriteria kr ON kr.id = np.kriteria_id "
                "WHERE np.paket_id = ? ORDER BY kr.kode",
                (d["id"],),
            ).fetchall()
            d["nilai"] = {n["kode"]: n["nilai"] for n in nilai}
            d["matrix"] = [d["nilai"][f"C{i}"] for i in range(1, 6)]
            result.append(d)
        return result
    finally:
        conn.close()


def get_paket_detail(paket_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT p.id, p.nomor_paket, p.nama_tampil, k.nama AS kota "
            "FROM paket p JOIN kota k ON k.id = p.kota_id WHERE p.id = ?",
            (paket_id,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        tempat = conn.execute(
            "SELECT t.nama, t.kategori FROM paket_tempat pt JOIN tempat t ON t.id = pt.tempat_id "
            "WHERE pt.paket_id = ? ORDER BY pt.urutan",
            (paket_id,),
        ).fetchall()
        d["tempat"] = [dict(t) for t in tempat]
        nilai = conn.execute(
            "SELECT kr.kode, np.nilai FROM nilai_paket np "
            "JOIN kriteria kr ON kr.id = np.kriteria_id "
            "WHERE np.paket_id = ? ORDER BY kr.kode",
            (paket_id,),
        ).fetchall()
        d["nilai"] = {n["kode"]: n["nilai"] for n in nilai}
        d["matrix"] = [d["nilai"][f"C{i}"] for i in range(1, 6)]
        return d
    finally:
        conn.close()


def update_kriteria(updates):
    """updates: list dict {kode, tipe, bobot}. Mengembalikan pesan error atau None."""
    total = sum(u["bobot"] for u in updates)
    if abs(total - 1.0) > 0.001:
        return f"Total bobot harus 1,00. Total yang dimasukkan: {total:.4f}."
    for u in updates:
        if u["tipe"] not in ("Benefit", "Cost"):
            return f"Tipe kriteria {u['kode']} tidak valid."
        if not (0 <= u["bobot"] <= 1):
            return f"Bobot kriteria {u['kode']} harus antara 0 dan 1."
    conn = get_connection()
    try:
        for u in updates:
            conn.execute(
                "UPDATE kriteria SET tipe = ?, bobot = ? WHERE kode = ?",
                (u["tipe"], u["bobot"], u["kode"]),
            )
        conn.commit()
    finally:
        conn.close()
    return None


def update_nilai_paket(paket_id, values):
    """values: dict kode -> nilai. Mengembalikan pesan error atau None."""
    for kode, val in values.items():
        if not (1 <= val <= 5):
            return f"Nilai {kode} harus antara 1 dan 5."
    conn = get_connection()
    try:
        for kode, val in values.items():
            conn.execute(
                "UPDATE nilai_paket SET nilai = ? WHERE paket_id = ? AND kriteria_id = "
                "(SELECT id FROM kriteria WHERE kode = ?)",
                (val, paket_id, kode),
            )
        conn.commit()
    finally:
        conn.close()
    return None
