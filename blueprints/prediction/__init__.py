from flask import Blueprint

# Handles image upload, AI prediction, result display, and history
prediction_bp = Blueprint(
    "prediction", __name__, url_prefix="/predict", template_folder="../../templates/user"
)

from . import routes  # noqa: E402,F401
