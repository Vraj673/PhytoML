"""
blueprints/auth/routes.py
--------------------------
Registration, login, and logout for normal (non-admin) users.
Passwords are hashed with Werkzeug's `generate_password_hash`
(PBKDF2-SHA256 by default) - plain text passwords are never stored.
"""

from flask_babel import gettext as _
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import auth_bp
from models import db, User


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """New user self-registration."""
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # --- Basic server-side validation ---
        if not all([full_name, username, email, password]):
            flash(_("Please fill in all required fields."), "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash(_("Passwords do not match."), "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash(_("Password must be at least 6 characters long."), "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash(_("That username is already taken."), "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash(_("An account with that email already exists."), "danger")
            return redirect(url_for("auth.register"))

        # --- Create the new user with a HASHED password ---
        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            phone=request.form.get("phone", "").strip(),
            address=request.form.get("address", "").strip(),
        )
        new_user.set_password(password)  # hashing happens here

        db.session.add(new_user)
        db.session.commit()

        flash(_("Registration successful! Please log in."), "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Normal user login."""
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()

        # check_password() compares against the stored hash
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(_("Welcome back, %(name)s!", name=user.full_name), "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("user.dashboard"))

        flash(_("Invalid username/email or password."), "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("You have been logged out."), "info")
    return redirect(url_for("auth.login"))
