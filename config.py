"""
config.py
---------
Central configuration for the Flask application.
Keeping configuration in one place makes it easy to switch between
development / testing / production settings.
"""

import os

# Base directory of the project (absolute path)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class used by the Flask app factory."""

    # Secret key is used to sign session cookies / CSRF tokens.
    # In production this MUST be overridden with an environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # SQLite database file stored inside the /database folder
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'plant_disease.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder where uploaded leaf images are stored
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size

    # Path to the trained Random Forest model (created by ml_model/train_model.py)
    MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "model.pkl")
    LABELS_PATH = os.path.join(BASE_DIR, "ml_model", "labels.pkl")

    # Default admin credentials (used to seed the admins table on first run)
    DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    # --- Multi-language support (Flask-Babel) ---
    LANGUAGES = {
        "en": "English",
        "hi": "हिंदी",
        "gu": "ગુજરાતી",
    }
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, "translations")

    # --- Weather API (Open-Meteo — free, no API key required) ---
    WEATHER_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    DEFAULT_WEATHER_CITY = os.environ.get("DEFAULT_WEATHER_CITY", "Ahmedabad")
