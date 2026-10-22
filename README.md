# AI-Based Plant Disease Detection and Recommendation System

A complete Flask web application that lets users upload a photo of a plant
leaf and receive an AI-powered disease diagnosis (Random Forest + OpenCV
preprocessing) along with symptoms, causes, and treatment recommendations.

## Features

- **User Module** — registration, login, logout, profile management, hashed passwords
- **Admin Module** — separate admin login, view users, view full prediction history, manage disease knowledge base
- **AI Module** — OpenCV image preprocessing + Random Forest classifier, confidence score
- **Recommendation Module** — symptoms / causes / treatment per disease
- **SQLite database** — `users`, `admins`, `predictions`, `diseases` tables
- **Bootstrap 5** responsive frontend
- **Flask Blueprints** for clean project structure

## Project Structure

```
plant_disease_system/
├── app.py                     # Application factory + entry point
├── config.py                  # Configuration (paths, upload limits, etc.)
├── requirements.txt
├── database/
│   └── schema.sql             # Reference SQL schema
├── models/
│   └── db.py                  # SQLAlchemy models (User, Admin, Prediction, Disease)
├── blueprints/
│   ├── auth/                  # Register / Login / Logout
│   ├── user/                  # Dashboard / Profile
│   ├── prediction/            # Upload / Result / History
│   └── admin/                 # Admin login / Users / Predictions / Diseases
├── ml_model/
│   ├── preprocess.py          # OpenCV feature extraction
│   ├── train_model.py         # Trains the Random Forest model
│   ├── predict.py             # Loads model + runs predictions
│   ├── disease_classes.py     # Class list + recommendation content
│   ├── model.pkl              # Generated after training
│   └── labels.pkl             # Generated after training
├── static/
│   ├── css/style.css
│   └── uploads/                # Uploaded leaf images
├── templates/
│   ├── base.html, index.html, 404.html, 403.html
│   ├── auth/  (login.html, register.html)
│   ├── user/  (dashboard.html, profile.html, upload.html, result.html, history.html)
│   └── admin/ (login.html, dashboard.html, users.html, predictions.html, diseases.html, edit_disease.html)
├── utils/
│   └── decorators.py          # admin_required decorator, file helpers
└── data/train/                # (optional) put a real labeled dataset here
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Train the AI model**

   ```bash
   python ml_model/train_model.py
   ```

   - If a real labeled dataset is placed at `data/train/<class_name>/*.jpg`
     (e.g. the public PlantVillage dataset), the script trains on those
     real images.
   - Otherwise it **automatically generates a small synthetic leaf
     dataset** so the whole application is runnable end-to-end out of
     the box for demos/coursework. For real-world accuracy, supply a
     real dataset and re-run this script.

3. **Run the application**

   ```bash
   python app.py
   ```

   The app runs at `http://127.0.0.1:5000/`. On first run it automatically:
   - Creates the SQLite database (`database/plant_disease.db`) and all tables
   - Creates a default admin account: **username `admin` / password `admin123`**
     (change this immediately in production, e.g. via environment variables
     `ADMIN_USERNAME` / `ADMIN_PASSWORD`)
   - Seeds the `diseases` knowledge-base table from `ml_model/disease_classes.py`

4. **Use the app**
   - Register a normal user account at `/register`, log in, then go to
     **Upload Image** to scan a leaf photo.
   - Log in as admin at `/admin/login` to view users, all predictions,
     and edit disease recommendation text.

## Notes on the AI Model

The classifier is a `RandomForestClassifier` (scikit-learn) trained on
hand-engineered image features extracted with OpenCV:
- HSV color histogram (captures overall leaf/lesion color)
- Grayscale intensity mean/standard deviation (texture)
- Canny edge density (lesion boundary irregularity)
- Green-pixel ratio (healthy vs. diseased tissue proportion)

This classic ML pipeline is lightweight, fast to train/retrain, and easy
to explain — well suited to a Random Forest as requested. Swap in a real
labeled dataset under `data/train/` for production-grade accuracy.

## Security Notes

- Passwords are never stored in plain text — `werkzeug.security.generate_password_hash`
  (PBKDF2-SHA256) is used for both users and admins.
- Admin sessions are kept separate from user sessions (`session['is_admin']`)
  so an admin login never grants a normal user account, and vice versa.
- Uploaded files are validated by extension and renamed with a UUID to
  prevent path traversal / filename collisions.

## New in this update: Charts, Weather & Multi-language

- **Charts (Chart.js)** — user dashboard: scans over last 14 days (line) + breakdown by disease (doughnut). Admin dashboard: predictions per day (bar), by disease class (horizontal bar), healthy vs diseased (doughnut). Data helpers live in `utils/charts.py`.
- **Weather (Open-Meteo API, no key needed)** — dashboard widget shows temperature, humidity, wind and a simple plant-disease-risk hint. Change city with the small form; default city set via `DEFAULT_WEATHER_CITY` in `config.py`. Needs internet access. Code: `utils/weather.py`.
- **Languages (Flask-Babel)** — English, Hindi, Gujarati. Switch from the navbar dropdown. Translations are in `translations/<lang>/LC_MESSAGES/messages.po`.

After editing any `.po` file, recompile with:
```
pybabel compile -d translations
```
To add a language: add it to `LANGUAGES` in `config.py`, then
`pybabel init -i messages.pot -d translations -l <code>`, translate, compile.
To re-extract after adding new `_()` strings: `pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .` then `pybabel update -i messages.pot -d translations`.

Install new dependencies: `pip install -r requirements.txt` (adds Flask-Babel, requests).

## New in v3: Percentages, Healthy/Diseased graph & translated disease content

- **Percentages on charts** — every doughnut slice now shows its percentage; tooltips show count + percentage (`static/js/chart_helpers.js`).
- **Healthy vs Diseased graph** (user dashboard) — doughnut chart plus a new "Healthy Plants" card. **Click a slice (or a card/button) to open the list** of healthy or diseased plants. Clicking a slice of "Breakdown by Disease" lists that one disease. History page has All / Healthy / Diseased filter tabs (`/predict/history?status=healthy|diseased&disease=<class>`).
- **Disease content in Hindi & Gujarati** — crop name, disease name, symptoms, causes and treatment now follow the selected language. Texts live in `ml_model/disease_translations.py` and are copied into the new `disease_translations` table on start-up (existing databases upgrade automatically; admin edits are never overwritten). Admins can edit each language on *Admin → Diseases → Edit*; a blank field falls back to English.
- Dates (month names), chart day labels, prediction class names and the navbar language indicator now follow the selected language too.
