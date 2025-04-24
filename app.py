from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO

load_dotenv()

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD')

basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)
    return render_template('index.html', year=datetime.now().year, kategorijos=duomenys)

@app.route('/paslaugos/<kategorija>')
def paslaugos(kategorija):
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)
    paslaugos = duomenys.get(kategorija, [])
    return render_template('paslaugos.html', kategorija=kategorija, paslaugos=paslaugos, kategorijos=duomenys, year=datetime.now().year)

@app.route('/paslaugos')
def visos_paslaugos():
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    paslaugos = []
    for sarasas in duomenys.values():
        paslaugos.extend(sarasas)

    return render_template('paslaugos.html', kategorija='visos paslaugos', paslaugos=paslaugos, kategorijos=duomenys, year=datetime.now().year)

@app.route('/kontaktai', methods=['GET', 'POST'])
def kontaktai():
    zinute_issiusta = False
    if request.method == 'POST':
        vardas = request.form['name']
        pastas = request.form['email']
        paslauga = request.form['service']
        zinute = request.form['message']
        print("Gauta žinutė iš Kontaktų:", vardas, pastas, paslauga, zinute)
        zinute_issiusta = True
    return render_template('kontaktai.html', zinute_issiusta=zinute_issiusta, year=datetime.now().year)

@app.route('/teisiskai')
def teisiskai():
    return render_template('teisiskai.html', year=datetime.now().year)

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    zinute = None
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    if request.method == 'POST':
        kategorija = request.form['kategorija']
        pavadinimas = request.form['pavadinimas']
        aprasymas = request.form['aprasymas']
        adresas = request.form['adresas']
        telefonas = request.form['telefonas']
        darbo_laikas = request.form['darbo_laikas']
        maps = request.form['maps']
        svetaine = request.form.get('svetaine')

        failas = request.files.get('nuotrauka')
        nuotraukos_kelias = None

        if failas and failas.filename:
            failo_pavadinimas = secure_filename(failas.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            nuotraukos_kelias = os.path.join(upload_folder, failo_pavadinimas)
            failas.save(nuotraukos_kelias)

        nauja_paslauga = {
            "pavadinimas": pavadinimas,
            "aprasymas": aprasymas,
            "adresas": adresas,
            "telefonas": telefonas,
            "darbo_laikas": darbo_laikas,
            "maps": maps
        }

        if svetaine:
            nauja_paslauga["svetaine"] = svetaine
        if nuotraukos_kelias:
            nauja_paslauga["nuotrauka"] = nuotraukos_kelias.replace("static/", "")

        duomenys.setdefault(kategorija, []).append(nauja_paslauga)

        with open(failo_kelias, 'w', encoding='utf-8') as f:
            json.dump(duomenys, f, indent=4, ensure_ascii=False)

        zinute = "Paslauga sėkmingai pridėta!"

    for kategorija in duomenys:
        duomenys[kategorija] = sorted(duomenys[kategorija], key=lambda x: x.get('pavadinimas', '').lower())

    return render_template('admin.html', year=datetime.now().year, zinute=zinute, duomenys=duomenys)

@app.route('/admin/redaguoti/<kategorija>/<int:index>', methods=['GET', 'POST'])
@basic_auth.required
def redaguoti(kategorija, index):
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    paslauga = duomenys.get(kategorija, [])[index]

    if request.method == 'POST':
        paslauga['pavadinimas'] = request.form['pavadinimas']
        paslauga['aprasymas'] = request.form['aprasymas']
        paslauga['adresas'] = request.form['adresas']
        paslauga['telefonas'] = request.form['telefonas']
        paslauga['darbo_laikas'] = request.form['darbo_laikas']
        paslauga['maps'] = request.form['maps']
        paslauga['svetaine'] = request.form.get('svetaine', '')
        paslauga['nuotrauka'] = paslauga.get('nuotrauka', '')

        duomenys[kategorija][index] = paslauga

        with open(failo_kelias, 'w', encoding='utf-8') as f:
            json.dump(duomenys, f, indent=4, ensure_ascii=False)

        return redirect(url_for('admin'))

    return render_template('redaguoti.html', year=datetime.now().year, kategorija=kategorija, index=index, paslauga=paslauga)

@app.route('/admin/istrinti/<kategorija>/<int:index>', methods=['POST'])
@basic_auth.required
def istrinti(kategorija, index):
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    if kategorija in duomenys and 0 <= index < len(duomenys[kategorija]):
        del duomenys[kategorija][index]
        with open(failo_kelias, 'w', encoding='utf-8') as f:
            json.dump(duomenys, f, indent=4, ensure_ascii=False)

    return redirect(url_for('admin'))

@app.route('/admin/eksportuoti')
@basic_auth.required
def eksportuoti():
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    rows = []
    for kategorija, sarasas in duomenys.items():
        for paslauga in sarasas:
            paslauga['kategorija'] = kategorija
            rows.append(paslauga)

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(output, download_name="paslaugos.xlsx", as_attachment=True)

@app.route('/lankytinos_vietos')
def lankytinos_vietos():
    failo_kelias = os.path.join(os.path.dirname(__file__), 'lankytinos_vietos.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        vietos = json.load(f)
    return render_template('lankytinos_vietos.html', vietos=vietos, year=datetime.now().year)

@app.route('/paslauga/<int:paslaugos_id>')
def viena_paslauga(paslaugos_id):
    failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')
    with open(failo_kelias, 'r', encoding='utf-8') as f:
        duomenys = json.load(f)

    for kategorija, sarasas in duomenys.items():
        for paslauga in sarasas:
            if paslauga.get('id') == paslaugos_id:
                return render_template('viena_paslauga.html', paslauga=paslauga, kategorija=kategorija, year=datetime.now().year)

    return "Paslauga nerasta", 404

if __name__ == '__main__':
    print("Flask aplikacija startuoja...")
    app.run(debug=True)
