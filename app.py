# app.py – Galutinė, saugesnė Flask aplikacija
# SU SAUGOS PATIKRINIMAIS IR CSRF APSAUGA

from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, session, flash
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import threading
import platform
import flask
import json
import os
import uuid
import sys

# --- Inicializacija ir Saugumo Patikrinimai ---
load_dotenv()
print("✅ Flask STARTED from app.py")

# Absoliutūs keliai (stabilumui)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(APP_ROOT, "static", "uploads")
SERVICES_PATH = os.path.join(APP_ROOT, "services.json")
ADS_PATH = os.path.join(APP_ROOT, "ads.json")
PLACES_PATH = os.path.join(APP_ROOT, "places.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔐 Prisijungimo duomenys
ADMIN_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
# Pirmenybė HASH; jei nėra – naudoti BASIC_AUTH_PASSWORD (mažiau saugu, bet veiks)
ADMIN_PASSWORD_HASH = os.environ.get("BASIC_AUTH_PASSWORD_HASH")
ADMIN_PASSWORD_FALLBACK = os.environ.get("BASIC_AUTH_PASSWORD")
SECRET_KEY = os.environ.get("SECRET_KEY")

if not ADMIN_USERNAME or not SECRET_KEY:
    print("\n\n##################################################################")
    print("FATAL ERROR: Būtina nustatyti BASIC_AUTH_USERNAME ir SECRET_KEY .env faile.")
    print("##################################################################\n\n")
    sys.exit(1)

if not ADMIN_PASSWORD_HASH and (not ADMIN_PASSWORD_FALLBACK or ADMIN_PASSWORD_FALLBACK == "changeme"):
    print("\n\n##################################################################")
    print("FATAL ERROR: Nėra BASIC_AUTH_PASSWORD_HASH ir nepriimtinas BASIC_AUTH_PASSWORD.")
    print("Sugeneruok hash (Werkzeug generate_password_hash) ir įdėk į BASIC_AUTH_PASSWORD_HASH.")
    print("##################################################################\n\n")
    sys.exit(1)

# --- Aplikacijos Konfigūracija ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# CSRF pagal nutylėjimą
app.config.update(
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_CHECK_DEFAULT=True,
)

# Sesijos/cookie sauga
app.config.update(
    SESSION_COOKIE_SECURE=True,        # Nustatyk True gamyboje su HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)

# Upload apsaugos
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# Debug valdymas per ENV
# FLASK_DEBUG=1 įjungs debug; kitu atveju – išjungta (saugu)
DEBUG_FLAG = os.getenv("FLASK_DEBUG", "0") == "1"

csrf = CSRFProtect(app)
json_lock = threading.Lock()

# CSRF token injektorius į šablonus: naudok {{ csrf_token() }} formose
@app.context_processor
def inject_csrf():
    return dict(csrf_token=generate_csrf)

# Baziniai saugos antraščių headeriai
@app.after_request
def set_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return resp

# --- Pagalbinės funkcijos ---
def allowed_file(filename, fileobj=None):
    """Tikrina, ar failo plėtinys leidžiamas ir ar MIME yra image/*"""
    if not filename or "." not in filename:
        return False
    ext_ok = filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    if not ext_ok:
        return False
    if fileobj is not None:
        mime = (getattr(fileobj, "mimetype", None) or "").lower()
        # Pvz.: image/png, image/jpeg
        if not mime.startswith("image/"):
            return False
    return True


def safe_load_json(filename, default=None):
    """Saugiai įkelia JSON failą, gerbiant default tipą"""
    if not os.path.exists(filename):
        return default if default is not None else {}
    with json_lock:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Klaida nuskaitant {filename}, atkuriama tuščia struktūra.")
            return default if default is not None else {}


def safe_save_json(filename, data):
    """Saugiai ir atomiškai išsaugo JSON failą"""
    tmp = f"{filename}.tmp-{uuid.uuid4().hex}"
    with json_lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, filename)


def save_uploaded_file(file):
    """Saugiai įkelia paveikslėlį į uploads"""
    if file and allowed_file(file.filename, file):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        unique_name = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
        path_rel = os.path.join("uploads", unique_name)
        path_abs = os.path.join(UPLOAD_DIR, unique_name)
        file.save(path_abs)
        return path_rel
    return None


# --- VIEŠIEJI MARŠRUTAI ---
@app.route("/")
def index():
    categories = safe_load_json(SERVICES_PATH, default={})
    ads = safe_load_json(ADS_PATH, default=[])
    ads = [ad for ad in ads if ad.get('title') and ad.get('link')]

    show_server_info = os.getenv("SHOW_SERVER_INFO", "0") == "1"
    server_info = None
    if show_server_info:
        server_info = f"Python {platform.python_version()} | Flask {flask.__version__}"

    return render_template(
        "index.html",
        categories=categories,
        ads=ads,
        year=datetime.now().year,
        server_info=server_info
    )


@app.route("/services/<category>/<subcategory>")
def services(category, subcategory):
    data = safe_load_json(SERVICES_PATH, default={})
    category = (category or "").lower()
    subcategory = (subcategory or "").lower()

    if category not in data or subcategory not in data.get(category, {}):
        flash(f"❌ Kategorija ar subkategorija '{category}'/'{subcategory}' nerasta.", "error")
        return redirect(url_for('index'))

    service_list = data[category][subcategory]
    return render_template(
        "services.html",
        category=subcategory.replace('_', ' ').title(),
        services=service_list,
        categories=data,
        year=datetime.now().year
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        print("📩 Message received:", request.form)
        flash("✅ Jūsų žinutė išsiųsta. Ačiū!", "success")
        return redirect(url_for('contact', message_sent=True))

    return render_template(
        "contact.html",
        message_sent=request.args.get('message_sent', False),
        year=datetime.now().year
    )


@app.route("/legal")
def legal():
    return render_template("legal.html", year=datetime.now().year)


@app.route("/places")
def places():
    data = safe_load_json(PLACES_PATH, default=[])
    return render_template("places.html", places=data, year=datetime.now().year)


# --- LOGIN SISTEMA ---
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Pirma – HASH, jei yra; kitaip – fallback į plaintext (mažiau saugu)
        password_ok = False
        if ADMIN_PASSWORD_HASH:
            password_ok = check_password_hash(ADMIN_PASSWORD_HASH, password)
        elif ADMIN_PASSWORD_FALLBACK:
            password_ok = (password == ADMIN_PASSWORD_FALLBACK)

        if username == ADMIN_USERNAME and password_ok:
            session.clear()              # nuo session fixation
            session.permanent = True     # taikomas PERMANENT_SESSION_LIFETIME
            session["logged_in"] = True
            flash("✅ Prisijungėte sėkmingai!", "success")
            return redirect(url_for("admin"))
        else:
            error = "❌ Neteisingas vardas arba slaptažodis."

    return render_template("login.html", error=error, year=datetime.now().year)


@app.route("/logout")
def logout():
    session.clear()
    flash("Atsijungėte. Iki greito!", "info")
    return redirect(url_for("index"))


# --- ADMIN PANELĖ: PASLAUGOS (CREATE) ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    data = safe_load_json(SERVICES_PATH, default={})

    if request.method == "POST":
        try:
            category = request.form["category"].lower().replace(' ', '_')
            subcategory = request.form["subcategory"].lower().replace(' ', '_')

            new_service = {
                "name": request.form["name"],
                "description": request.form["description"],
                "address": request.form["address"],
                "phone": request.form["phone"],
                "working_hours": request.form["working_hours"],
                "maps": request.form["maps"],
                "website": request.form.get("website", ""),
                "image": save_uploaded_file(request.files.get("image")) or "",
            }

            data.setdefault(category, {}).setdefault(subcategory, []).append(new_service)
            safe_save_json(SERVICES_PATH, data)
            flash("✅ Paslauga pridėta sėkmingai!", "success")
        except Exception as e:
            flash(f"❌ Klaida pridedant paslaugą: {e}", "error")

        return redirect(url_for("admin"))

    show_server_info = os.getenv("SHOW_SERVER_INFO", "0") == "1"
    server_info = None
    if show_server_info:
        server_info = f"Python {platform.python_version()} | Flask {flask.__version__}"

    return render_template(
        "admin.html",
        data=data,
        year=datetime.now().year,
        server_info=server_info
    )


# --- ADMIN PANELĖ: PASLAUGOS (DELETE) ---
@app.route("/admin/delete", methods=["POST"])
def delete_service():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    category = request.form.get("category", "")
    subcategory = request.form.get("subcategory", "")
    index = int(request.form.get("index", -1))
    data = safe_load_json(SERVICES_PATH, default={})

    try:
        if (category in data and subcategory in data[category]
                and 0 <= index < len(data[category][subcategory])):

            service = data[category][subcategory][index]

            if service.get("image"):
                image_path = os.path.join(APP_ROOT, "static", service["image"])
                if os.path.exists(image_path):
                    os.remove(image_path)

            del data[category][subcategory][index]

            if not data[category][subcategory]:
                del data[category][subcategory]
            if not data[category]:
                del data[category]

            safe_save_json(SERVICES_PATH, data)
            flash("🗑️ Paslauga ištrinta sėkmingai.", "success")
        else:
            flash("❌ Paslauga nerasta arba neteisingas indeksas.", "error")
    except Exception as e:
        flash(f"⚠️ Klaida trinant: {e}", "error")

    return redirect(url_for("admin"))


# --- ADMIN PANELĖ: PASLAUGOS (UPDATE) ---
@app.route("/admin/edit", methods=["GET", "POST"])
def edit_service():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    category = request.args.get("category") or request.form.get("category")
    subcategory = request.args.get("subcategory") or request.form.get("subcategory")
    index_str = request.args.get("index") or request.form.get("index")

    try:
        index = int(index_str)
    except (ValueError, TypeError):
        flash("❌ Neteisingas paslaugos indeksas.", "error")
        return redirect(url_for("admin"))

    data = safe_load_json(SERVICES_PATH, default={})

    if (category not in data or
        subcategory not in data[category] or
        not (0 <= index < len(data[category][subcategory]))):
        flash("❌ Paslauga redagavimui nerasta.", "error")
        return redirect(url_for("admin"))

    current_service = data[category][subcategory][index]

    if request.method == "POST":
        try:
            new_image_file = request.files.get("image")
            image_path = current_service.get("image", "")

            if new_image_file and new_image_file.filename:
                if image_path:
                    old_path = os.path.join(APP_ROOT, "static", image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                image_path = save_uploaded_file(new_image_file) or image_path

            updated_service = {
                "name": request.form["name"],
                "description": request.form["description"],
                "address": request.form["address"],
                "phone": request.form["phone"],
                "working_hours": request.form["working_hours"],
                "maps": request.form["maps"],
                "website": request.form.get("website", ""),
                "image": image_path,
            }

            data[category][subcategory][index] = updated_service
            safe_save_json(SERVICES_PATH, data)
            flash("✅ Paslaugos duomenys atnaujinti sėkmingai!", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            flash(f"❌ Klaida atnaujinant: {e}", "error")
            return redirect(url_for("edit_service", category=category, subcategory=subcategory, index=index))

    return render_template(
        "edit_service.html",
        service=current_service,
        category=category,
        subcategory=subcategory,
        index=index,
        year=datetime.now().year
    )


# --- ADMIN PANELĖ: REKLAMOS (ADS) (CREATE) ---
@app.route("/admin/ads", methods=["GET", "POST"])
def admin_ads():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    ads = safe_load_json(ADS_PATH, default=[])

    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            link = request.form.get("link", "").strip()
            category = request.form.get("category", "").strip()
            image = save_uploaded_file(request.files.get("image"))

            if not title or not link:
                flash("❌ Pavadinimas ir nuoroda yra privalomi.", "error")
                return redirect(url_for("admin_ads"))

            new_ad = {
                "id": uuid.uuid4().hex,
                "title": title,
                "link": link,
                "category": category or "General",
                "image": image or "",
            }
            ads.append(new_ad)
            safe_save_json(ADS_PATH, ads)
            flash("✅ Reklama pridėta sėkmingai!", "success")
        except Exception as e:
            flash(f"❌ Klaida pridedant reklamą: {e}", "error")

        return redirect(url_for("admin_ads"))

    return render_template("manage_ads.html", ads=ads, year=datetime.now().year)


# --- ADMIN PANELĖ: REKLAMOS (ADS) (DELETE) ---
@app.route("/admin/ads/delete", methods=["POST"])
def delete_ad():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    ad_id = request.form.get("ad_id")

    if not ad_id:
        flash("❌ Reklamos ID nerastas.", "error")
        return redirect(url_for("admin_ads"))

    ads = safe_load_json(ADS_PATH, default=[])
    ad_to_delete = next((a for a in ads if a.get("id") == ad_id), None)

    if ad_to_delete:
        if ad_to_delete.get("image"):
            try:
                image_path = os.path.join(APP_ROOT, "static", ad_to_delete["image"])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception:
                pass

        ads = [a for a in ads if a.get("id") != ad_id]
        safe_save_json(ADS_PATH, ads)
        flash("🗑️ Reklama ištrinta sėkmingai.", "success")
    else:
        flash("❌ Reklama nerasta.", "error")

    return redirect(url_for("admin_ads"))


# --- EKSPORTAS ---
@app.route("/admin/export")
def export():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    data = safe_load_json(SERVICES_PATH, default={})
    rows = [
        {**service, "category": cat, "subcategory": subcat}
        for cat, sub in data.items()
        for subcat, services in sub.items()
        for service in services
    ]

    if not rows:
        flash("⚠️ Nėra paslaugų eksportavimui.", "info")
        return redirect(url_for("admin"))

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    return send_file(
        output,
        download_name=f"naas_services_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
        as_attachment=True
    )


# --- PALEIDIMAS ---
if __name__ == "__main__":
    print("🚀 Flask app is starting...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=DEBUG_FLAG)
