from flask import Flask, render_template, request, redirect, url_for, send_file, session
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
print("✅ Flask STARTED from this app.py file")

app = Flask(__name__)
load_dotenv()

# Security configuration
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD')
basic_auth = BasicAuth(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def load_json(filename):
    print(f"📂 Bandom įkelti failą: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def create_service_entry(request):
    file = request.files.get('image')
    path = ''
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join('uploads', filename)
        file.save(os.path.join('static', path))
    return {
        "name": request.form['name'],
        "description": request.form['description'],
        "address": request.form['address'],
        "phone": request.form['phone'],
        "working_hours": request.form['working_hours'],
        "maps": request.form['maps'],
        "website": request.form.get('website', ''),
        "image": path
    }
@app.route('/')
def index():
    return render_template('index.html', categories=load_json('services.json'), year=datetime.now().year)

@app.route('/services/<category>/<subcategory>')
def services(category, subcategory):
    print(f"📥 Užklausa: category={category}, subcategory={subcategory}")
    data = load_json('services.json')
    if category not in data or subcategory not in data[category]:
        return "❌ Category or subcategory not found", 404
    service_list = data[category][subcategory]
    return render_template('services.html', category=subcategory, services=service_list, categories=data, year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        print("Message received:", request.form)
        message_sent = True
    return render_template('contact.html', message_sent=message_sent, year=datetime.now().year)

@app.route('/legal')
def legal():
    return render_template('legal.html', year=datetime.now().year)

@app.route('/places')
def places():
    data = load_json('places.json')
    return render_template('places.html', places=data, year=datetime.now().year)

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    data = load_json('services.json')
    popup_message = session.pop('popup_message', None)
    popup_type = session.pop('popup_type', 'success')

    if request.method == 'POST':
        new_service = create_service_entry(request)
        category = request.form['category']
        subcategory = request.form['subcategory']
        data.setdefault(category, {}).setdefault(subcategory, []).append(new_service)
        save_json('services.json', data)
        session['popup_message'] = "✅ Service added successfully!"
        session['popup_type'] = "success"
        return redirect(url_for('admin'))

    return render_template('admin.html', data=data, year=datetime.now().year, popup_message=popup_message, popup_type=popup_type, server_info=f"Python {platform.python_version()} | Flask {flask.__version__}")

@app.route('/admin/delete', methods=['POST'])
@basic_auth.required
def delete_service():
    category = request.form['category']
    subcategory = request.form['subcategory']
    index = int(request.form['index'])

    data = load_json('services.json')
    if category in data and subcategory in data[category]:
        if 0 <= index < len(data[category][subcategory]):
            service = data[category][subcategory][index]
            if service.get('image'):
                image_path = os.path.join('static', service['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            del data[category][subcategory][index]

    save_json('services.json', data)
    session['popup_message'] = "❌ Service deleted successfully."
    session['popup_type'] = "error"
    return redirect(url_for('admin'))

@app.route('/admin/edit', methods=['GET', 'POST'])
@basic_auth.required
def edit_service():
    data = load_json('services.json')
    if request.method == 'GET':
        category = request.args.get('category')
        subcategory = request.args.get('subcategory')
        index = int(request.args.get('index'))
        service = data[category][subcategory][index]
        return render_template('edit.html', service=service, category=category, subcategory=subcategory, index=index, year=datetime.now().year)
    elif request.method == 'POST':
        category = request.form['category']
        subcategory = request.form['subcategory']
        index = int(request.form['index'])

        old_image = data[category][subcategory][index].get('image')
        new_service = create_service_entry(request)

        if old_image and old_image != new_service['image']:
            image_path = os.path.join('static', old_image)
            if os.path.exists(image_path):
                os.remove(image_path)

        data[category][subcategory][index] = new_service
        save_json('services.json', data)
        session['popup_message'] = "✅ Service updated successfully."
        session['popup_type'] = "success"
        return redirect(url_for('admin'))

@app.route('/admin/export')
@basic_auth.required
def export():
    data = load_json('services.json')
    rows = [
        {**service, 'category': cat, 'subcategory': subcat}
        for cat, sub in data.items()
        for subcat, services in sub.items()
        for service in services
    ]

    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name="services.xlsx", as_attachment=True)

if __name__ == '__main__':
    print("Flask app is starting...")
    app.run(debug=True)
