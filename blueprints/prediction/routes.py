
"""
Prediction routes:
1. Validate uploaded image.
2. Predict disease for accepted images.
3. Save prediction and display the result.
"""

import os
import uuid

from flask_babel import gettext as _
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import prediction_bp
from models import db, Prediction, Disease
from utils.decorators import allowed_file
from utils.i18n import current_lang
from ml_model.predict import predict_disease
from leaf_validator import validate_leaf


@prediction_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Show upload form and process an uploaded image."""

    if request.method == "POST":
        if "leaf_image" not in request.files:
            flash(_("No file part in the request."), "danger")
            return redirect(url_for("prediction.upload"))

        file = request.files["leaf_image"]

        if file.filename == "":
            flash(_("Please select an image to upload."), "danger")
            return redirect(url_for("prediction.upload"))

        if not allowed_file(
            file.filename,
            current_app.config["ALLOWED_EXTENSIONS"],
        ):
            flash(
                _("Invalid file type. Please upload a PNG or JPG image."),
                "danger",
            )
            return redirect(url_for("prediction.upload"))

        original_name = secure_filename(file.filename)

        if not original_name:
            flash(_("Invalid filename."), "danger")
            return redirect(url_for("prediction.upload"))

        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]

        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)

        # Step 1: Validate the image before disease prediction.
        try:
            validation = validate_leaf(file_path)
        except Exception:
            validation = {"valid": False}

        if not validation.get("valid", False):
            try:
                os.remove(file_path)
            except OSError:
                pass

            flash(
                _("Please scan only tomato or potato leaf images."),
                "danger",
            )
            return redirect(url_for("prediction.upload"))

        # Step 2: Run the existing disease prediction model.
        try:
            result = predict_disease(file_path)

        except FileNotFoundError:
            flash(
                _("The AI model has not been trained yet. Please run "
                  "'python ml_model/train_model.py' on the server first."),
                "danger",
            )
            return redirect(url_for("prediction.upload"))

        except Exception as exc:
            current_app.logger.exception(
                "Disease prediction failed."
            )
            flash(
                _("Could not process the image: %(err)s", err=str(exc)),
                "danger",
            )
            return redirect(url_for("prediction.upload"))

        # Step 3: Save the prediction in the database.
        record = Prediction(
            user_id=current_user.id,
            image_path=f"uploads/{unique_name}",
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
        )

        db.session.add(record)
        db.session.commit()

        return redirect(
            url_for("prediction.result", prediction_id=record.id)
        )

    return render_template("user/upload.html")


@prediction_bp.route("/result/<int:prediction_id>")
@login_required
def result(prediction_id):
    """Show the prediction result and recommendation information."""

    record = Prediction.query.get_or_404(prediction_id)

    if record.user_id != current_user.id:
        abort(403)

    disease = Disease.query.filter_by(
        class_label=record.predicted_class
    ).first()

    disease_t = disease.localized(current_lang()) if disease else None

    return render_template(
        "user/result.html",
        record=record,
        disease=disease_t,
    )


@prediction_bp.route("/history")
@login_required
def history():
    """Show this user's prediction history with optional filters."""

    base = Prediction.query.filter_by(user_id=current_user.id)
    healthy_filter = Prediction.predicted_class.contains("healthy")

    counts = {
        "all": base.count(),
        "healthy": base.filter(healthy_filter).count(),
    }
    counts["diseased"] = counts["all"] - counts["healthy"]

    status = request.args.get("status")
    disease_label = request.args.get("disease") or None

    query = base

    if status == "healthy":
        query = query.filter(healthy_filter)
    elif status == "diseased":
        query = query.filter(~healthy_filter)
    else:
        status = None

    if disease_label:
        query = query.filter(
            Prediction.predicted_class == disease_label
        )

    predictions = query.order_by(
        Prediction.created_at.desc()
    ).all()

    return render_template(
        "user/history.html",
        predictions=predictions,
        counts=counts,
        status=status,
        disease_label=disease_label,
    )
