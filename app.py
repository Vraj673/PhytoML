"""
app.py
------
Application entry point. Uses the Flask "application factory" pattern so
the app can be created fresh for testing, and wires together:
    - SQLAlchemy database (SQLite)
    - Flask-Login (user session management)
    - Blueprints: auth, user, prediction, admin
    - First-run database seeding (default admin account + disease knowledge base)

Run with:
    python app.py
"""

import os
from flask import Flask, render_template, session, request, redirect, url_for
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext

from config import Config
from models import db, User, Admin, Disease, DiseaseTranslation
from ml_model.disease_classes import DISEASE_INFO
from ml_model.disease_translations import DISEASE_TRANSLATIONS, TRANSLATABLE_FIELDS
from utils.i18n import current_lang, pretty_class


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required folders exist
    os.makedirs(os.path.join(app.root_path, "database"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Initialize extensions ---
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = lazy_gettext("Please log in to access this page.")
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- Multi-language support (Flask-Babel) ---
    def select_locale():
        # 1) explicit choice stored in the session (language switcher)
        lang = session.get("language")
        if lang in app.config["LANGUAGES"]:
            return lang
        # 2) fall back to the browser's Accept-Language header
        return request.accept_languages.best_match(app.config["LANGUAGES"].keys())

    babel = Babel(app, locale_selector=select_locale)

    @app.route("/set-language/<lang_code>")
    def set_language(lang_code):
        if lang_code in app.config["LANGUAGES"]:
            session["language"] = lang_code
        # Send the person back to whichever page they were on
        return redirect(request.referrer or url_for("index"))

    @app.context_processor
    def inject_language_context():
        return {
            "available_languages": app.config["LANGUAGES"],
            "current_language": current_lang(),
        }

    # {{ p.predicted_class|pretty_class }} -> "आलू - लेट ब्लाइट (पछेती झुलसा)"
    app.add_template_filter(pretty_class, "pretty_class")

    # --- Register blueprints ---
    from blueprints.auth import auth_bp
    from blueprints.user import user_bp
    from blueprints.prediction import prediction_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(admin_bp)

    # --- Public landing page ---
    @app.route("/")
    def index():
        return render_template("index.html")

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    # --- First-run database setup ---
    with app.app_context():
        db.create_all()
        _seed_default_admin(app)
        _seed_disease_knowledge_base()
        _seed_disease_translations()

    return app


def _seed_default_admin(app):
    """Create a default admin account on first run if none exists yet."""
    if Admin.query.first() is None:
        admin = Admin(username=app.config["DEFAULT_ADMIN_USERNAME"])
        admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(
            f"[setup] Created default admin account "
            f"(username='{app.config['DEFAULT_ADMIN_USERNAME']}', "
            f"password='{app.config['DEFAULT_ADMIN_PASSWORD']}'). "
            f"Please change this after first login."
        )


def _seed_disease_knowledge_base():
    """Populate the `diseases` table from ml_model/disease_classes.py if empty."""
    if Disease.query.first() is None:
        for class_label, info in DISEASE_INFO.items():
            db.session.add(
                Disease(
                    class_label=class_label,
                    crop_name=info["crop_name"],
                    disease_name=info["disease_name"],
                    symptoms=info["symptoms"],
                    causes=info["causes"],
                    treatment=info["treatment"],
                    is_healthy=info["is_healthy"],
                )
            )
        db.session.commit()
        print("[setup] Seeded disease knowledge base.")


def _seed_disease_translations():
    """
    Copy Hindi / Gujarati texts from ml_model/disease_translations.py into the
    `disease_translations` table. Only missing rows are created, so text an
    admin has edited is never overwritten. Safe to run on an existing database.
    """
    added = 0
    for disease in Disease.query.all():
        per_lang = DISEASE_TRANSLATIONS.get(disease.class_label, {})
        existing = {t.lang for t in disease.translations}
        for lang, fields in per_lang.items():
            if lang in existing:
                continue
            db.session.add(
                DiseaseTranslation(
                    disease_id=disease.id,
                    lang=lang,
                    **{f: fields.get(f) for f in TRANSLATABLE_FIELDS},
                )
            )
            added += 1
    if added:
        db.session.commit()
        print(f"[setup] Added {added} disease translation(s).")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
