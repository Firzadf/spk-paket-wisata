"""Aplikasi web SPK Rekomendasi Paket Wisata (SAW dan TOPSIS).

Jalankan dari folder aplikasi:
  .venv/bin/python seed.py --force
  .venv/bin/python app.py
Lalu buka http://127.0.0.1:5000

Akun demo admin: admin / admin123. Ganti sebelum pemakaian nyata.
"""

import os
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash

import database
import saw as saw_mod
import topsis as topsis_mod

app = Flask(__name__)
app.secret_key = os.environ.get("SPK_SECRET_KEY", "spk-demo-key-ganti-di-produksi")

# Metadata foto kota (Wikimedia Commons, lisensi jelas, file lokal di static/images/).
# Foto bukan milik proyek; kredit lengkap ditampilkan di halaman Tentang.
CITY_META = {
    "Jakarta": {
        "file": "jakarta.jpg", "width": 1280, "height": 800, "position": "50% 42%",
        "subject": "Monumen Nasional (Monas), Jakarta",
        "photographer": "Ramayoni", "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Monumen_Nasional,_Jakarta,_Indonesia.jpg",
        "symbol": "monas",
    },
    "Yogyakarta": {
        "file": "yogyakarta.jpg", "width": 1280, "height": 800, "position": "50% 55%",
        "subject": "Candi Borobudur, Jawa Tengah",
        "photographer": "Jakub Ha\u0142un", "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Borobudur,_Java,_Indonesia,_20220817_1013_8739.jpg",
        "symbol": "borobudur",
    },
    "Bandung": {
        "file": "bandung.jpg", "width": 1280, "height": 800, "position": "50% 42%",
        "subject": "Gedung Sate, Bandung",
        "photographer": "Gunawan Kartapranata", "license": "CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Gedung_Sate_Bandung.jpg",
        "symbol": "gedung-sate",
    },
    "Semarang": {
        "file": "semarang.jpg", "width": 1280, "height": 800, "position": "50% 42%",
        "subject": "Lawang Sewu, Semarang",
        "photographer": "Philip Nalangan", "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Lawang_Sewu_Semarang_Indonesia_1.jpg",
        "symbol": "lawang-sewu",
    },
    "Surabaya": {
        "file": "surabaya.jpg", "width": 1280, "height": 800, "position": "50% 42%",
        "subject": "Tugu Pahlawan, Surabaya",
        "photographer": "Eny Santiati", "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Tugu_Pahlawan_Surabaya_Jawa_Timur.jpg",
        "symbol": "tugu-pahlawan",
    },
}


def city_meta(nama_kota):
    return CITY_META.get(nama_kota)


def city_winners(nama_kota):
    """Pemenang SAW/TOPSIS per kota, dipakai kartu kota di beranda."""
    data = compute_city(nama_kota)
    if data is None:
        return None
    saw_top = data["packages"][data["saw"]["order"][0]]
    topsis_top = data["packages"][data["topsis"]["order"][0]]
    return {
        "saw_paket": saw_top["nomor_paket"],
        "saw_vi": data["saw"]["values"][data["saw"]["order"][0]],
        "topsis_paket": topsis_top["nomor_paket"],
        "topsis_ci": data["topsis"]["values"][data["topsis"]["order"][0]],
    }



def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapper


def compute_city(nama_kota, weights=None, types=None):
    packages = database.get_paket_by_kota(nama_kota)
    if not packages:
        return None
    if weights is None or types is None:
        weights, types, _ = database.get_weights_and_types()
    matrix = [p["matrix"] for p in packages]
    saw_result = saw_mod.calculate(matrix, weights, types)
    topsis_result = topsis_mod.calculate(matrix, weights, types)
    kriteria = database.get_kriteria()
    return {
        "packages": packages,
        "matrix": matrix,
        "saw": saw_result,
        "topsis": topsis_result,
        "weights": weights,
        "types": types,
        "kriteria": kriteria,
    }


@app.route("/")
def index():
    kota = database.get_kota_list()
    kriteria = database.get_kriteria()
    winners = {k["nama"]: city_winners(k["nama"]) for k in kota}
    return render_template("index.html", kota=kota, kriteria=kriteria,
                           winners=winners, city_meta=CITY_META)


@app.route("/tentang")
def tentang():
    return render_template("tentang.html", kriteria=database.get_kriteria(),
                           city_meta=CITY_META)


@app.route("/cara-kerja")
def cara_kerja():
    return render_template("cara-kerja.html", kriteria=database.get_kriteria())


@app.route("/kota/<nama_kota>")
def kota_page(nama_kota):
    packages = database.get_paket_by_kota(nama_kota)
    if not packages:
        return render_template("index.html", kota=database.get_kota_list(), kriteria=database.get_kriteria(), error=f"Kota {nama_kota} tidak ditemukan."), 404
    return render_template("kota.html", kota=nama_kota, packages=packages,
                           kriteria=database.get_kriteria(), meta=city_meta(nama_kota),
                           winners=city_winners(nama_kota))


@app.route("/rekomendasi")
def rekomendasi():
    nama_kota = request.args.get("kota", "")
    metode = request.args.get("metode", "keduanya")
    if metode not in ("saw", "topsis", "keduanya"):
        metode = "keduanya"
    data = compute_city(nama_kota)
    if data is None:
        return render_template("index.html", kota=database.get_kota_list(), kriteria=database.get_kriteria(), error=f"Kota {nama_kota} tidak ditemukan."), 404
    return render_template("rekomendasi.html", kota=nama_kota, metode=metode,
                           meta=city_meta(nama_kota), **data)


@app.route("/paket/<int:paket_id>")
def paket_detail(paket_id):
    detail = database.get_paket_detail(paket_id)
    if detail is None:
        return redirect(url_for("index"))
    data = compute_city(detail["kota"])
    saw_rank = None
    topsis_rank = None
    for i, p in enumerate(data["packages"]):
        if p["id"] == paket_id:
            saw_rank = data["saw"]["ranks"][i]
            topsis_rank = data["topsis"]["ranks"][i]
    return render_template("paket.html", detail=detail, saw_rank=saw_rank, topsis_rank=topsis_rank,
                           kriteria=database.get_kriteria(), meta=city_meta(detail["kota"]))


@app.route("/api/kota/<nama_kota>/saw")
def api_saw(nama_kota):
    data = compute_city(nama_kota)
    if data is None:
        return jsonify({"error": "kota tidak ditemukan"}), 404
    ranking = []
    for idx in data["saw"]["order"]:
        p = data["packages"][idx]
        ranking.append({"paket": p["nomor_paket"], "nama": p["nama_tampil"], "nilai": data["saw"]["values"][idx], "ranking": data["saw"]["ranks"][idx], "tempat": p["tempat"]})
    return jsonify({"kota": nama_kota, "metode": "SAW", "bobot": data["weights"], "ranking": ranking})


@app.route("/api/kota/<nama_kota>/topsis")
def api_topsis(nama_kota):
    data = compute_city(nama_kota)
    if data is None:
        return jsonify({"error": "kota tidak ditemukan"}), 404
    ranking = []
    for idx in data["topsis"]["order"]:
        p = data["packages"][idx]
        ranking.append({"paket": p["nomor_paket"], "nama": p["nama_tampil"], "nilai": data["topsis"]["values"][idx], "ranking": data["topsis"]["ranks"][idx], "tempat": p["tempat"]})
    return jsonify({"kota": nama_kota, "metode": "TOPSIS", "bobot": data["weights"], "ranking": ranking})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = database.get_connection()
        try:
            row = conn.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        finally:
            conn.close()
        if row and check_password_hash(row["password_hash"], password):
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        error = "Nama pengguna atau kata sandi salah."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
@login_required
def admin_dashboard():
    kota = database.get_kota_list()
    total_paket = sum(k["jumlah"] for k in kota)
    return render_template("admin_dashboard.html", kota=kota, total_paket=total_paket, kriteria=database.get_kriteria())


@app.route("/admin/kriteria", methods=["GET", "POST"])
@login_required
def admin_kriteria():
    kriteria = database.get_kriteria()
    if request.method == "POST":
        updates = []
        for k in kriteria:
            try:
                bobot = float(request.form.get(f"bobot_{k['kode']}", k["bobot"]))
            except ValueError:
                bobot = k["bobot"]
            tipe = request.form.get(f"tipe_{k['kode']}", k["tipe"])
            updates.append({"kode": k["kode"], "tipe": tipe, "bobot": bobot})
        error = database.update_kriteria(updates)
        if error:
            return render_template("admin_kriteria.html", kriteria=kriteria, error=error)
        flash("Kriteria berhasil disimpan. Total bobot 1,00.")
        return redirect(url_for("admin_kriteria"))
    return render_template("admin_kriteria.html", kriteria=kriteria)


@app.route("/admin/paket")
@login_required
def admin_paket():
    # Filter dan pagination server-side: jalan tanpa JavaScript, parameter di URL.
    # Default 10 paket per halaman, pilihan 10/20/50. Filter tetap berlaku saat pindah halaman.
    kota_filter = request.args.get("kota", "")
    q = request.args.get("q", "").strip()
    try:
        per_page = int(request.args.get("per_page", "10"))
    except ValueError:
        per_page = 10
    if per_page not in (10, 20, 50):
        per_page = 10
    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        page = 1
    kota = database.get_kota_list()
    semua = []
    for k in kota:
        semua.extend(database.get_paket_by_kota(k["nama"]))
    if kota_filter:
        semua = [p for p in semua if p["kota"] == kota_filter]
    if q:
        ql = q.lower()
        semua = [p for p in semua
                 if ql in f"paket {p['nomor_paket']}".lower()
                 or ql in p["kota"].lower()
                 or ql in ", ".join(p["tempat"]).lower()]
    total = len(semua)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    return render_template("admin_paket.html", packages=semua[start:end],
                           kota_list=kota, kota_filter=kota_filter, q=q,
                           page=page, per_page=per_page, total=total,
                           total_pages=total_pages, start=start + 1 if total else 0, end=end)


@app.route("/admin/paket/<int:paket_id>/nilai", methods=["GET", "POST"])
@login_required
def admin_nilai(paket_id):
    detail = database.get_paket_detail(paket_id)
    if detail is None:
        return redirect(url_for("admin_paket"))
    if request.method == "POST":
        values = {}
        try:
            for i in range(1, 6):
                values[f"C{i}"] = float(request.form.get(f"C{i}", detail["nilai"][f"C{i}"]))
        except ValueError:
            return render_template("admin_nilai.html", detail=detail, error="Nilai harus angka.")
        error = database.update_nilai_paket(paket_id, values)
        if error:
            return render_template("admin_nilai.html", detail=detail, error=error)
        flash("Nilai paket berhasil disimpan.")
        return redirect(url_for("admin_paket"))
    return render_template("admin_nilai.html", detail=detail)


@app.route("/admin/simulasi", methods=["GET", "POST"])
@login_required
def admin_simulasi():
    kriteria = database.get_kriteria()
    weights_default, types_default, _ = database.get_weights_and_types()
    hasil = None
    kota_dipilih = "Jakarta"
    weights = weights_default
    if request.method == "POST":
        kota_dipilih = request.form.get("kota", "Jakarta")
        try:
            weights = [float(request.form.get(f"bobot_C{i}", weights_default[i - 1])) for i in range(1, 6)]
        except ValueError:
            weights = weights_default
        if abs(sum(weights) - 1.0) > 0.001:
            return render_template("admin_simulasi.html", kriteria=kriteria, weights_default=weights_default, weights=weights, kota=kota_dipilih, hasil=None, error=f"Total bobot simulasi harus 1,00. Total saat ini: {sum(weights):.4f}. Bobot tidak disimpan.")
        hasil = compute_city(kota_dipilih, weights=weights, types=types_default)
        if hasil is None:
            return render_template("admin_simulasi.html", kriteria=kriteria, weights_default=weights_default, weights=weights, kota=kota_dipilih, hasil=None, error="Kota tidak ditemukan.")
    return render_template("admin_simulasi.html", kriteria=kriteria, weights_default=weights_default, hasil=hasil, kota=kota_dipilih, weights=weights)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
