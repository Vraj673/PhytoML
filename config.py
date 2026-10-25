
"""
config.py
---------
Central configuration for the Flask application.
"""

import os

# Absolute path of the project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the Flask application."""

    # Secret key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-this-secret-key"
    )

    # Database configuration
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Convert Render's legacy PostgreSQL URL format if necessary
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )

    # Use PostgreSQL when configured; otherwise use local SQLite
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        DATABASE_PATH = os.path.join(
            BASE_DIR, "database", "plant_disease.db"
        )

        # Ensure the database directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" + DATABASE_PATH.replace("\\", "/")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploaded leaf images
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR, "static", "uploads"
    )
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Machine learning model files
    MODEL_PATH = os.path.join(
        BASE_DIR, "ml_model", "model.pkl"
    )
    LABELS_PATH = os.path.join(
        BASE_DIR, "ml_model", "labels.pkl"
    )

    # Default admin credentials
    DEFAULT_ADMIN_USERNAME = os.environ.get(
        "ADMIN_USERNAME", "admin"
    )
    DEFAULT_ADMIN_PASSWORD = os.environ.get(
        "ADMIN_PASSWORD", "admin123"
    )

    # Language support
    LANGUAGES = {
        "en": "English",
        "hi": "हिंदी",
        "gu": "ગુજરાતી",
    }
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(
        BASE_DIR, "translations"
    )

    # Weather API
    WEATHER_GEOCODE_URL = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )
    WEATHER_FORECAST_URL = (
        "https://api.open-meteo.com/v1/forecast"
    )
    DEFAULT_WEATHER_CITY = os.environ.get(
        "DEFAULT_WEATHER_CITY", "Ahmedabad"
    )
