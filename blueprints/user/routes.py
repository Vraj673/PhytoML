"""
blueprints/user/routes.py
---------------------------
Dashboard and profile management for logged-in users.

The dashboard additionally shows:
  - Two Chart.js charts (predictions over the last 14 days, and a
    breakdown by disease class) built from utils/charts.py.
  - A current-weather widget (utils/weather.py, Open-Meteo API) with a
    simple plant-disease-risk hint based on humidity/temperature.
"""

from flask_babel import gettext as _
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user

from . import user_bp
from models import db, Prediction
from utils.charts import daily_prediction_counts, disease_class_rows
from utils.i18n import pretty_class
from utils.weather import get_weather_for_city


@user_bp.route("/dashboard")
@login_required
def dashboard():
    """Landing page after login: quick stats, charts, weather + recent predictions."""
    recent_predictions = (
        Prediction.query.filter_by(user_id=current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    diseased_count = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        ~Prediction.predicted_class.contains("healthy"),
    ).count()

    # Chart data (personal, this user only)
    trend_labels, trend_values = daily_prediction_counts(user_id=current_user.id, days=14)
    class_rows = disease_class_rows(user_id=current_user.id)
    disease_labels = [pretty_class(cls) for cls, _n in class_rows]   # translated names
    disease_values = [n for _cls, n in class_rows]
    # Clicking a slice opens the history list filtered to that disease / status
    disease_urls = [url_for("prediction.history", disease=cls) for cls, _n in class_rows]
    healthy_count = total_predictions - diseased_count
    health_urls = [
        url_for("prediction.history", status="healthy"),
        url_for("prediction.history", status="diseased"),
    ]

    # Weather widget — city comes from the session (set via the dashboard's
    # small search form) or falls back to the configured default city.
    weather_city = session.get("weather_city", current_app.config["DEFAULT_WEATHER_CITY"])
    weather = get_weather_for_city(weather_city)

    return render_template(
        "user/dashboard.html",
        recent_predictions=recent_predictions,
        total_predictions=total_predictions,
        diseased_count=diseased_count,
        healthy_count=healthy_count,
        health_urls=health_urls,
        disease_urls=disease_urls,
        trend_labels=trend_labels,
        trend_values=trend_values,
        disease_labels=disease_labels,
        disease_values=disease_values,
        weather=weather,
        weather_city=weather_city,
    )


@user_bp.route("/weather", methods=["POST"])
@login_required
def set_weather_city():
    """Update which city's weather is shown on the dashboard."""
    city = request.form.get("city", "").strip()
    if city:
        session["weather_city"] = city
    else:
        flash(_("Please enter a city name."), "warning")
    return redirect(url_for("user.dashboard"))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and update profile information."""
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name).strip()
        current_user.phone = request.form.get("phone", "").strip()
        current_user.address = request.form.get("address", "").strip()

        new_password = request.form.get("new_password", "").strip()
        if new_password:
            if len(new_password) < 6:
                flash(_("New password must be at least 6 characters."), "danger")
                return redirect(url_for("user.profile"))
            current_user.set_password(new_password)  # re-hash on change
            flash(_("Password updated successfully."), "success")

        db.session.commit()
        flash(_("Profile updated successfully."), "success")
        return redirect(url_for("user.profile"))

    return render_template("user/profile.html")
