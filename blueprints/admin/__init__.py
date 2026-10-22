from flask import Blueprint

# Handles admin login/logout + management screens (users, predictions, diseases)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../../templates/admin")

from . import routes  # noqa: E402,F401
