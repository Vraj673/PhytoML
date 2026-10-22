from flask import Blueprint

# Handles registration / login / logout for normal (non-admin) users
auth_bp = Blueprint("auth", __name__, template_folder="../../templates/auth")

from . import routes  # noqa: E402,F401  (import at bottom avoids circular imports)
