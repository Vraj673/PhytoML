"""
utils/decorators.py
--------------------
Small reusable helpers used across blueprints.
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from flask_babel import gettext as _


def admin_required(view_func):
    """
    Route decorator that protects admin-only pages.
    Admin authentication is kept separate from Flask-Login (which is used
    for normal users) by storing a simple flag in the session.
    """

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            flash(_("Please log in as admin to continue."), "warning")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def allowed_file(filename, allowed_extensions):
    """Check that an uploaded filename has an approved image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )
