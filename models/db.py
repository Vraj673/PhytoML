"""
models/db.py
------------
Defines the SQLite database schema using Flask-SQLAlchemy ORM models.

Tables:
    users        -> registered end users of the system
    admins       -> admin accounts (separate from normal users)
    predictions  -> history of every disease prediction made by a user
    diseases     -> disease knowledge base (symptoms / causes / treatment)
"""

from datetime import datetime
from types import SimpleNamespace
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Registered application user (farmer / gardener / student, etc.)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user can have many predictions (one-to-many relationship)
    predictions = db.relationship(
        "Prediction", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        """Hash and store the user's password (never store plain text)."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


class Admin(db.Model):
    """Administrator account, kept separate from regular users."""

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<Admin {self.username}>"


class Disease(db.Model):
    """Knowledge base entry describing a plant disease (or healthy state)."""

    __tablename__ = "diseases"

    id = db.Column(db.Integer, primary_key=True)
    class_label = db.Column(db.String(120), unique=True, nullable=False)  # ML model class name
    crop_name = db.Column(db.String(80), nullable=False)
    disease_name = db.Column(db.String(120), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    causes = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    is_healthy = db.Column(db.Boolean, default=False)

    def localized(self, lang=None):
        """
        Return this disease's text in the requested language ('hi', 'gu', ...).
        Any field missing a translation falls back to the English text, so the
        page never shows blanks.
        """
        translation = None
        if lang and lang != "en":
            translation = next((t for t in self.translations if t.lang == lang), None)

        def pick(field):
            value = getattr(translation, field, None) if translation else None
            return value or getattr(self, field)

        return SimpleNamespace(
            id=self.id,
            class_label=self.class_label,
            is_healthy=self.is_healthy,
            crop_name=pick("crop_name"),
            disease_name=pick("disease_name"),
            symptoms=pick("symptoms"),
            causes=pick("causes"),
            treatment=pick("treatment"),
        )

    def __repr__(self):
        return f"<Disease {self.disease_name}>"


class DiseaseTranslation(db.Model):
    """Translated knowledge-base text for one disease in one language."""

    __tablename__ = "disease_translations"
    __table_args__ = (db.UniqueConstraint("disease_id", "lang", name="uq_disease_lang"),)

    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey("diseases.id"), nullable=False)
    lang = db.Column(db.String(8), nullable=False)  # e.g. 'hi', 'gu'
    crop_name = db.Column(db.String(80))
    disease_name = db.Column(db.String(160))
    symptoms = db.Column(db.Text)
    causes = db.Column(db.Text)
    treatment = db.Column(db.Text)

    disease = db.relationship(
        "Disease",
        backref=db.backref("translations", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<DiseaseTranslation {self.disease_id}/{self.lang}>"


class Prediction(db.Model):
    """One prediction event: an uploaded image + the AI model's result."""

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_class = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # 0-100 %
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction {self.predicted_class} ({self.confidence:.2f}%)>"
