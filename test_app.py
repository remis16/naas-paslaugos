from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import platform
import flask
from translations import translations

app = Flask(__name__)
load_dotenv()

# Slapto rakto ir saugumo nustatymai
app.secret_key = os.getenv('SECRET_KEY', 'tavo_slaptas_raktas')
app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD')
basic_auth = BasicAuth(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_language():
    return session.get('language', 'lt')

def get_translations():
    lang = get_language()
    return translations.get(lang, translations['lt'])

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def create_service_entry(request):
    failas = request.files.get('nuotrauka')
    kelias = ''
    if failas and allowed_file(failas.filename):
        failo_pavadinimas = secure_filename(failas.filename)
        kelias = os.path.join('uploads', failo_pavadinimas)
        failas.save(os.path.join('static', kelias))
    return {
        "pavadinimas": request.form['pavadinimas'],
        "aprasymas": request.form['aprasymas'],
        "adresas": request.form['adresas'],
        "telefonas": request.form['telefonas'],
        "darbo_laikas": request.form['darbo_laikas'],
        "maps": request.form['maps'],
        "svetaine": request.form.get('svetaine', ''),
        "nuotrauka": kelias
    }

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    session['language'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template(
        'index.html',
        translations=get_translations(),
        kategorijos=load_json('services.json'),
        year=datetime.now().year,
        lang=get_language()
    )

@app.route('/paslaugos/<kategorija>/<subkategorija>')
def paslaugos(kategorija, subkategorija):
    duomenys = load_json('services.json')
    paslaugos = duomenys.get(kategorija, {}).get(subkategorija, [])
    return render_template(
        'paslaugos.html',
        kategorija=subkategorija,
        paslaugos=paslaugos,
        kategorijos=duomenys,
        translations=get_translations(),
        year=datetime.now().year,
        lang=get_language()
    )

@app.route('/kontaktai', methods=['GET', 'POST'])
def kontaktai():
    zinute_issiusta = False
    if request.method == 'POST':
        print("Gauta žinutė:", request.form)
        zinute_issiusta = True
    return render_template(
        'kontaktai.html',
        translations=get_translations(),
        zinute_issiusta=zinute_issiusta,
        year=datetime.now().year,
        lang=get_language()
    )

@app.route('/teisiskai')
def teisiskai():
    return render_template(
        'teisiskai.html',
        translations=get_translations(),
        year=datetime.now().year,
        lang=get_language()
    )

@app.route('/lankytinos_vietos')
def lankytinos_vietos():
    vietos = load_json('lankytinos_vietos.json')
    return render_template(
        'lankytinos_vietos.html',
        vietos=vietos,
        translations=get_translations(),
        year=datetime.now().year,
        lang=get_language()
    )

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    duomenys = load_json('services.json')
    popup_message = session.pop('popup_message', None)
    popup_type = session.pop('popup_type', 'success')

    if request.method == 'POST':
        nauja = create_service_entry(request)
        kategorija = request.form['kategorija']
        subkategorija = request.form['subkategorija']
        duomenys.setdefault(kategorija, {}).setdefault(subkategorija, []).append(nauja)
        save_json('services.json', duomenys)
        session['popup_message'] = "✅ Paslauga sėkmingai pridėta!"
        session['popup_type'] = "success"
        return redirect(url_for('admin'))

    return render_template(
        'admin.html',
        duomenys=duomenys,
        translations=get_translations(),
        year=datetime.now().year,
        lang=get_language(),
        popup_message=popup_message,
        popup_type=popup_type,
        server_info=f"Python {platform.python_version()} | Flask {flask.__version__}"
    )

@app.route('/admin/istrinti', methods=['POST'])
@basic_auth.required
def istrinti_paslauga():
    kategorija = request.form['kategorija']
    subkategorija = request.form['subkategorija']
    index = int(request.form['index'])

    duomenys = load_json('services.json')
    if kategorija in duomenys and subkategorija in duomenys[kategorija]:
        if 0 <= index < len(duomenys[kategorija][subkategorija]):
            paslauga = duomenys[kategorija][subkategorija][index]
            if paslauga.get('nuotrauka'):
                nuotraukos_kelias = os.path.join('static', paslauga['nuotrauka'])
                if os.path.exists(nuotraukos_kelias):
                    os.remove(nuotraukos_kelias)
            del duomenys[kategorija][subkategorija][index]

    save_json('services.json', duomenys)
    session['popup_message'] = "❌ Paslauga sėkmingai ištrinta."
    session['popup_type'] = "error"
    return redirect(url_for('admin'))

@app.route('/admin/redaguoti', methods=['GET', 'POST'])
@basic_auth.required
def redaguoti_paslauga():
    duomenys = load_json('services.json')
    if request.method == 'GET':
        kategorija = request.args.get('kategorija')
        subkategorija = request.args.get('subkategorija')
        index = int(request.args.get('index'))
        paslauga = duomenys[kategorija][subkategorija][index]
        return render_template(
            'redaguoti.html',
            paslauga=paslauga,
            kategorija=kategorija,
            subkategorija=subkategorija,
            index=index,
            translations=get_translations(),
            year=datetime.now().year,
            lang=get_language()
        )
    elif request.method == 'POST':
        kategorija = request.form['kategorija']
        subkategorija = request.form['subkategorija']
        index = int(request.form['index'])

        sena_nuotrauka = duomenys[kategorija][subkategorija][index].get('nuotrauka')
        nauja_paslauga = create_service_entry(request)

        if sena_nuotrauka and sena_nuotrauka != nauja_paslauga['nuotrauka']:
            nuotraukos_kelias = os.path.join('static', sena_nuotrauka)
            if os.path.exists(nuotraukos_kelias):
                os.remove(nuotraukos_kelias)

        duomenys[kategorija][subkategorija][index] = nauja_paslauga
        save_json('services.json', duomenys)
        session['popup_message'] = "✅ Paslauga sėkmingai atnaujinta."
        session['popup_type'] = "success"
        return redirect(url_for('admin'))

@app.route('/admin/eksportuoti')
@basic_auth.required
def eksportuoti():
    duomenys = load_json('services.json')
    rows = [
        {**paslauga, 'kategorija': kat, 'subkategorija': subkat}
        for kat, sub in duomenys.items()
        for subkat, sarasas in sub.items()
        for paslauga in sarasas
    ]

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name="paslaugos.xlsx", as_attachment=True)

if __name__ == '__main__':
    print("Flask aplikacija startuoja...")
    app.run(debug=True)