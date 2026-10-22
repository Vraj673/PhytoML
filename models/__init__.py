"""
models package
--------------
Exposes the SQLAlchemy `db` instance and all ORM models so they can be
imported as `from models import db, User, Admin, Prediction, Disease`.
"""

from .db import db, User, Admin, Prediction, Disease, DiseaseTranslation

__all__ = ["db", "User", "Admin", "Prediction", "Disease", "DiseaseTranslation"]
