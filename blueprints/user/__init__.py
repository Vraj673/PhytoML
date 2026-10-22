from flask import Blueprint

# Handles dashboard + profile management for logged-in users
user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="../../templates/user")

from . import routes  # noqa: E402,F401
