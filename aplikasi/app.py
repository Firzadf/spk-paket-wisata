"""Aplikasi web SPK Rekomendasi Paket Wisata (SAW dan TOPSIS).

Jalankan dari folder aplikasi:
  .venv/bin/python seed.py --force
  .venv/bin/python app.py
Lalu buka http://127.0.0.1:5000

Akun demo admin: admin / admin123. Ganti sebelum pemakaian nyata.
"""

import hmac
import os
import secrets
import time
from functools import wraps

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash

import database
import saw as saw_mod
import topsis as topsis_mod

app = Flask(__name__)
app.secret_key = os.environ.get("SPK_SECRET_KEY", "spk-demo-key-ganti-di-produksi")
# Cookie sesi: HttpOnly dan SameSite selalu; Secure hanya saat
# SPK_SECRET_KEY di-set (produksi/Vercel, HTTPS). Lokal tanpa env var
# tetap bisa login lewat http://127.0.0.1.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("SPK_SECRET_KEY"))

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


# --- CSRF dan batas percobaan login (tanpa dependensi baru) ---
# Token CSRF dibuat per sesi dan dicek di setiap POST /admin/*.
def _csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(32)
        session["csrf_token"] = token
    return token


@app.context_processor
def _inject_globals():
    # vercel_demo: Vercel otomatis men-set VERCEL=1; dipakai untuk
    # menampilkan peringatan bahwa edit admin di sana tidak permanen.
    return {"csrf_token": _csrf_token,
            "vercel_demo": os.environ.get("VERCEL") == "1"}


@app.before_request
def _csrf_protect():
    if request.method == "POST" and request.path.startswith("/admin"):
        token = request.form.get("csrf_token", "")
        if not token or not hmac.compare_digest(
                token, session.get("csrf_token", "")):
            abort(400, "Token keamanan tidak valid. "
                       "Muat ulang halaman dan coba lagi.")


# Batas percobaan login: 5 gagal dalam 15 menit dari satu IP, lalu
# diblokir 15 menit. Disimpan di memori per instance server; di Vercel
# tiap instance punya hitungannya sendiri, jadi ini pelapis, bukan
# pengganti kata sandi admin yang kuat.
_LOGIN_FAILURES = {}
MAX_LOGIN_FAILURES = 5
LOGIN_BLOCK_SECONDS = 900


def _login_blocked(ip):
    now = time.time()
    attempts = [t for t in _LOGIN_FAILURES.get(ip, [])
                if now - t < LOGIN_BLOCK_SECONDS]
    _LOGIN_FAILURES[ip] = attempts
    return len(attempts) >= MAX_LOGIN_FAILURES


def _record_failed_login(ip):
    _LOGIN_FAILURES.setdefault(ip, []).append(time.time())


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


def paginate(total, per_page=10):
    """Pagination server-side: jalan tanpa JavaScript, parameter di URL.
    Mengembalikan (page, total_pages, start_0based, end_0based)."""
    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        page = 1
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    return page, total_pages, start, end


def render_index_404(nama_kota):
    """Halaman beranda dengan pesan kota tidak ditemukan (404).

    index.html butuh winners dan city_meta; kalau tidak dikirim,
    template gagal render (pernah jadi bug 500 di jalur 404)."""
    kota = database.get_kota_list()
    winners = {k["nama"]: city_winners(k["nama"]) for k in kota}
    return render_template("index.html", kota=kota,
                           kriteria=database.get_kriteria(),
                           winners=winners, city_meta=CITY_META,
                           error=f"Kota {nama_kota} tidak ditemukan."), 404


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
        return render_index_404(nama_kota)
    # Pagination server-side: 10 paket per halaman, tanpa JavaScript.
    page, total_pages, start, end = paginate(len(packages))
    return render_template("kota.html", kota=nama_kota, packages=packages[start:end],
                           kriteria=database.get_kriteria(), meta=city_meta(nama_kota),
                           winners=city_winners(nama_kota), page=page, total_pages=total_pages,
                           total=len(packages), start=start + 1, end=end)


@app.route("/rekomendasi")
def rekomendasi():
    nama_kota = request.args.get("kota", "")
    metode = request.args.get("metode", "keduanya")
    if metode not in ("saw", "topsis", "keduanya"):
        metode = "keduanya"
    data = compute_city(nama_kota)
    if data is None:
        return render_index_404(nama_kota)
    # Pagination server-side: 10 paket per halaman, tanpa JavaScript.
    # Satu nomor halaman berlaku untuk tabel SAW dan TOPSIS sekaligus,
    # supaya keduanya menampilkan 10 baris yang sama. Ganti metode
    # kembali ke halaman 1 (tautan metode tidak membawa parameter page).
    page, total_pages, start, end = paginate(len(data["packages"]))
    return render_template("rekomendasi.html", kota=nama_kota, metode=metode,
                           meta=city_meta(nama_kota), page=page, total_pages=total_pages,
                           total=len(data["packages"]), start=start + 1 if data["packages"] else 0,
                           end=end, slice_start=start, slice_end=end, **data)


DEFAULT_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]


@app.route("/lab")
def lab():
    """Lab Simulasi Bobot, terbuka untuk semua pengunjung tanpa login.

    Sama seperti simulasi admin, tapi lewat GET supaya tautan hasil bisa
    dibagikan, dan tanpa menyimpan apa pun. Bobot default sama dengan
    bobot resmi proyek. Jalan tanpa JavaScript; JavaScript hanya
    memperbarui tampilan total bobot saat mengetik."""
    kota_list = [k["nama"] for k in database.get_kota_list()]
    kota_dipilih = request.args.get("kota", "Jakarta")
    if kota_dipilih not in kota_list:
        return render_index_404(kota_dipilih)
    weights = []
    error = None
    for i in range(1, 6):
        raw = request.args.get(f"bobot_C{i}")
        if raw is None or raw == "":
            weights.append(DEFAULT_WEIGHTS[i - 1])
            continue
        try:
            w = float(raw)
        except ValueError:
            weights.append(DEFAULT_WEIGHTS[i - 1])
            error = "Bobot harus angka."
            continue
        if w < 0 or w > 1:
            error = "Bobot harus antara 0 dan 1."
        weights.append(w)
    hasil = None
    if error is None and abs(sum(weights) - 1.0) > 0.001:
        error = (f"Total kelima bobot harus 1,00. "
                 f"Total saat ini: {sum(weights):.4f}.")
    elif error is None:
        _, types_default, _ = database.get_weights_and_types()
        hasil = compute_city(kota_dipilih, weights=weights, types=types_default)
    return render_template("lab.html", kota=kota_dipilih, kota_list=kota_list,
                           weights=weights, kriteria=database.get_kriteria(),
                           hasil=hasil, error=error)


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
        ip = request.remote_addr or "unknown"
        if _login_blocked(ip):
            error = ("Terlalu banyak percobaan gagal. "
                     "Coba lagi dalam 15 menit.")
            return render_template("admin_login.html", error=error)
        conn = database.get_connection()
        try:
            row = conn.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        finally:
            conn.close()
        if row and check_password_hash(row["password_hash"], password):
            _LOGIN_FAILURES.pop(ip, None)
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        _record_failed_login(ip)
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
