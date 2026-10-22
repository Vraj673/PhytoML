"""
utils/i18n.py
--------------
Small helpers for showing database content (disease names etc.) in the
language the user has selected.
"""

from flask import g
from flask_babel import get_locale


def current_lang():
    """Active language code: 'en', 'hi' or 'gu'."""
    locale = get_locale()
    return locale.language if locale else "en"


def class_display_names():
    """
    {class_label: 'Crop - Disease'} in the active language.
    Built once per request (11 rows) and cached on flask.g.
    """
    if not hasattr(g, "_class_display_names"):
        from models import Disease  # local import avoids a circular import

        lang = current_lang()
        names = {}
        for disease in Disease.query.all():
            d = disease.localized(lang)
            names[disease.class_label] = f"{d.crop_name} - {d.disease_name}"
        g._class_display_names = names
    return g._class_display_names


def pretty_class(class_label):
    """Translate a model class label like 'Potato___Late_blight' for display."""
    name = class_display_names().get(class_label)
    return name or class_label.replace("___", " - ").replace("_", " ")
