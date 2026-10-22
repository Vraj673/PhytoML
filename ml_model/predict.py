"""
ml_model/predict.py
--------------------
Loads the trained Random Forest model and exposes a single function,
`predict_disease(image_path)`, used by the Flask prediction blueprint.
"""

import os
import joblib

from .preprocess import preprocess_image_file

_MODEL = None
_LABELS = None


def _get_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return (
        os.path.join(base_dir, "model.pkl"),
        os.path.join(base_dir, "labels.pkl"),
    )


def _load_model():
    """Lazily load the model + labels into memory (singleton pattern)."""
    global _MODEL, _LABELS
    if _MODEL is None:
        model_path, labels_path = _get_paths()
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "Trained model not found. Please run "
                "'python ml_model/train_model.py' first."
            )
        _MODEL = joblib.load(model_path)
        _LABELS = joblib.load(labels_path)
    return _MODEL, _LABELS


def predict_disease(image_path):
    """
    Run the full pipeline: preprocess image -> extract features -> predict.

    Returns:
        dict with keys:
            predicted_class (str)
            confidence (float, 0-100)
            all_probabilities (dict of class_label -> probability %)
    """
    model, labels = _load_model()

    features = preprocess_image_file(image_path)
    features = features.reshape(1, -1)

    probabilities = model.predict_proba(features)[0]
    predicted_index = probabilities.argmax()
    predicted_class = model.classes_[predicted_index]
    confidence = float(probabilities[predicted_index]) * 100

    all_probs = {
        cls: round(float(prob) * 100, 2)
        for cls, prob in zip(model.classes_, probabilities)
    }

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "all_probabilities": all_probs,
    }
