"""
blueprints/admin/routes.py
-----------------------------
Admin module: separate login from normal users (session-based, guarded by
the `admin_required` decorator), plus screens to view registered users,
browse the full prediction history of all users, and manage the disease
knowledge base (symptoms / causes / treatment) shown on result pages.
"""

from flask_babel import gettext as _
from flask import render_template, request, redirect, url_for, flash, session, current_app

from . import admin_bp
from models import db, Admin, User, Prediction, Disease, DiseaseTranslation
from ml_model.disease_translations import TRANSLATABLE_FIELDS
from utils.decorators import admin_required
from utils.charts import daily_prediction_counts, disease_class_rows, healthy_vs_diseased_counts
from utils.i18n import pretty_class


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin login - intentionally separate from Flask-Login (used by users)."""
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["is_admin"] = True
            session["admin_username"] = admin.username
            flash(_("Welcome back, admin!"), "success")
            return redirect(url_for("admin.dashboard"))

        flash(_("Invalid admin credentials."), "danger")
        return redirect(url_for("admin.login"))

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@admin_required
def logout():
    session.pop("is_admin", None)
    session.pop("admin_username", None)
    flash(_("Admin logged out."), "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Admin overview: quick stats across the whole system."""
    stats = {
        "total_users": User.query.count(),
        "total_predictions": Prediction.query.count(),
        "total_diseases": Disease.query.count(),
        "diseased_cases": Prediction.query.filter(
            ~Prediction.predicted_class.contains("healthy")
        ).count(),
    }
    recent_predictions = (
        Prediction.query.order_by(Prediction.created_at.desc()).limit(8).all()
    )

    # Site-wide chart data (every user, no user_id filter)
    trend_labels, trend_values = daily_prediction_counts(days=14)
    class_rows = disease_class_rows()
    disease_labels = [pretty_class(cls) for cls, _n in class_rows]   # translated names
    disease_values = [n for _cls, n in class_rows]
    healthy_count, diseased_count = healthy_vs_diseased_counts()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_predictions=recent_predictions,
        trend_labels=trend_labels,
        trend_values=trend_values,
        disease_labels=disease_labels,
        disease_values=disease_values,
        healthy_count=healthy_count,
        diseased_count_chart=diseased_count,
    )


@admin_bp.route("/users")
@admin_required
def users():
    """List every registered user."""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/predictions")
@admin_required
def predictions():
    """Full prediction history across all users."""
    all_predictions = (
        Prediction.query.order_by(Prediction.created_at.desc()).all()
    )
    return render_template("admin/predictions.html", predictions=all_predictions)


@admin_bp.route("/diseases")
@admin_required
def diseases():
    """List every disease in the knowledge base."""
    all_diseases = Disease.query.order_by(Disease.crop_name, Disease.disease_name).all()
    return render_template("admin/diseases.html", diseases=all_diseases)


@admin_bp.route("/diseases/<int:disease_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_disease(disease_id):
    """Edit the symptoms/causes/treatment text for one disease (English + translations)."""
    disease = Disease.query.get_or_404(disease_id)

    # Every language except English has its own translation row
    other_languages = {
        code: name for code, name in current_app.config["LANGUAGES"].items() if code != "en"
    }
    translations = {t.lang: t for t in disease.translations}

    if request.method == "POST":
        disease.disease_name = request.form.get("disease_name", disease.disease_name).strip()
        disease.symptoms = request.form.get("symptoms", disease.symptoms).strip()
        disease.causes = request.form.get("causes", disease.causes).strip()
        disease.treatment = request.form.get("treatment", disease.treatment).strip()

        for code in other_languages:
            row = translations.get(code)
            if row is None:
                row = DiseaseTranslation(disease_id=disease.id, lang=code)
                db.session.add(row)
            for field in TRANSLATABLE_FIELDS:
                value = request.form.get(f"{code}_{field}")
                if value is not None:
                    setattr(row, field, value.strip() or None)  # blank -> falls back to English

        db.session.commit()
        flash(_("Updated information for %(name)s.", name=disease.disease_name), "success")
        return redirect(url_for("admin.diseases"))

    return render_template(
        "admin/edit_disease.html",
        disease=disease,
        other_languages=other_languages,
        translations=translations,
    )
