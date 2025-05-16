# 🇮🇪 Naas City Services Guide

**All local services in one place – restaurants, beauty salons, gyms, and more in Naas, Ireland.**

---

## 🔍 About the Project

This project is an information platform that helps residents and visitors quickly find all essential services in Naas, Ireland.

### Features:

- ✅ Browse services by category
- ✅ Search and filtering
- ✅ Add, edit, and delete services via the admin panel
- ✅ Export services to Excel
- ✅ Attractions page with maps

---

## 📸 Example

![Website screenshot](static/uploads/pavyzdys.png)

---

## 🚀 Running Locally

1. Clone the project:

```bash
git clone https://github.com/remis16/naas-paslaugos.git
cd naas-paslaugos
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your credentials:

```
SECRET_KEY=your_secret_key
BASIC_AUTH_USERNAME=your_admin_username
BASIC_AUTH_PASSWORD=your_admin_password
```

4. Run the application:

```bash
python app.py
```

---

## 📁 Project Structure

- `app.py` – main Flask application file
- `templates/` – HTML templates
- `static/` – CSS, images, JS
- `services.json` – all services data
- `places.json` – attractions data

---

## 📬 Contact

Developer: Remi  
Email: [el.paštas@example.com]

---

⚠️ License  
This project is open source, but commercial use requires the author's permission.