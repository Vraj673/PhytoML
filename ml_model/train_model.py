"""
ml_model/train_model.py
-------------------------
Trains a RandomForestClassifier to classify plant leaf images into one of
the classes defined in `disease_classes.py`.

Two modes of operation:

  1. REAL DATASET (preferred for production use):
     If a folder `data/train/<class_label>/*.jpg` exists (e.g. the public
     "PlantVillage" dataset organized by class folder), every image found
     there is loaded, preprocessed, and used to train the model.

  2. SYNTHETIC DEMO DATASET (automatic fallback):
     If no real dataset is present, this script procedurally generates a
     small synthetic leaf-image dataset (green leaf background + colored
     "lesion" blobs whose color/count/shape vary per disease class) so
     that the whole application is runnable end-to-end out of the box for
     demonstration purposes. For real-world accuracy, replace this with
     the PlantVillage dataset (or your own labeled images) and re-run.

Run with:
    python ml_model/train_model.py
"""

import os
import sys
import random
import numpy as np
import cv2
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocess import extract_features, IMAGE_SIZE   # noqa: E402
from disease_classes import CLASS_LABELS               # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
REAL_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "train")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
LABELS_PATH = os.path.join(BASE_DIR, "labels.pkl")

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def _generate_synthetic_leaf(class_label, rng):
    """
    Procedurally draw a synthetic leaf image whose color/texture pattern
    is characteristic of the given class label. Used only when a real
    labeled dataset is not available, so the app can be demoed end-to-end.
    """
    w, h = IMAGE_SIZE
    img = np.zeros((h, w, 3), dtype=np.uint8)

    is_healthy = class_label.endswith("healthy")

    # Base leaf color: healthy leaves = vivid green, diseased = slightly
    # duller / yellowed green (randomized so the model must generalize).
    base_green = (
        int(rng.integers(30, 60)),                                  # B
        int(rng.integers(120, 180)) if is_healthy else int(rng.integers(90, 150)),  # G
        int(rng.integers(20, 60)),                                  # R
    )
    img[:] = base_green

    # Add subtle random noise for texture realism
    noise = rng.integers(-10, 10, size=img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if not is_healthy:
        # Diseased classes get lesion blobs; color/count depends on class
        # so that different diseases are visually (and thus, feature-wise)
        # distinguishable to the classifier.
        class_seed = abs(hash(class_label)) % (2 ** 32)
        local_rng = np.random.default_rng(class_seed + int(rng.integers(0, 10000)))
        n_lesions = int(local_rng.integers(5, 15))

        # Derive a consistent lesion color per-class (browns/blacks/yellows)
        color_variants = {
            "scab": (30, 70, 90),
            "rot": (10, 10, 40),
            "rust": (30, 90, 160),
            "blight": (20, 40, 70),
            "spot": (15, 15, 15),
        }
        lesion_color = (40, 60, 90)  # default brownish
        for key, color in color_variants.items():
            if key.lower() in class_label.lower():
                lesion_color = color
                break

        for _ in range(n_lesions):
            cx, cy = int(local_rng.integers(5, w - 5)), int(local_rng.integers(5, h - 5))
            radius = int(local_rng.integers(3, 10))
            jitter = tuple(int(c + local_rng.integers(-15, 15)) for c in lesion_color)
            jitter = tuple(max(0, min(255, c)) for c in jitter)
            cv2.circle(img, (cx, cy), radius, jitter, -1)

    return img


def _load_real_dataset():
    """Load images from data/train/<class_label>/*.jpg if that folder exists."""
    features, labels = [], []
    if not os.path.isdir(REAL_DATA_DIR):
        return features, labels

    for class_label in os.listdir(REAL_DATA_DIR):
        class_dir = os.path.join(REAL_DATA_DIR, class_label)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            fpath = os.path.join(class_dir, fname)
            image = cv2.imread(fpath)
            if image is None:
                continue
            features.append(extract_features(image))
            labels.append(class_label)
    return features, labels


def _generate_synthetic_dataset(samples_per_class=60):
    """Generate a synthetic dataset covering every class in CLASS_LABELS."""
    rng = np.random.default_rng(RANDOM_SEED)
    features, labels = [], []
    for class_label in CLASS_LABELS:
        for _ in range(samples_per_class):
            img = _generate_synthetic_leaf(class_label, rng)
            features.append(extract_features(img))
            labels.append(class_label)
    return features, labels


def train():
    print("Loading dataset...")
    features, labels = _load_real_dataset()

    if features:
        print(f"Found real dataset in {REAL_DATA_DIR} with {len(features)} images.")
    else:
        print("No real dataset found under data/train/. "
              "Generating a synthetic demo dataset instead...")
        features, labels = _generate_synthetic_dataset()
        print(f"Generated {len(features)} synthetic training samples "
              f"across {len(CLASS_LABELS)} classes.")

    X = np.array(features)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nValidation accuracy: {acc * 100:.2f}%")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Persist the trained model and the ordered class label list
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(list(clf.classes_), LABELS_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Labels saved to: {LABELS_PATH}")


if __name__ == "__main__":
    train()
