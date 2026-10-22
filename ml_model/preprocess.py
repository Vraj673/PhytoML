"""
ml_model/preprocess.py
-----------------------
Image preprocessing + feature extraction used by BOTH the training script
and the live prediction pipeline. Using the exact same function in both
places guarantees the Random Forest sees data in a consistent format.

Feature engineering approach (classic ML, no deep learning required):
    1. Resize the leaf image to a fixed size.
    2. Convert to HSV color space (better separates leaf color / disease
       spots than RGB) and compute a normalized color histogram.
    3. Convert to grayscale and compute simple texture statistics
       (mean, standard deviation) plus an edge-density score using Canny
       edge detection (diseased leaves tend to have more irregular edges
       / lesion boundaries than healthy leaves).

The final feature vector is a fixed-length 1D numpy array that is fed
into the scikit-learn RandomForestClassifier.
"""

import cv2
import numpy as np

IMAGE_SIZE = (128, 128)  # width, height used for every image
HIST_BINS = (8, 8, 8)  # bins per HSV channel for the color histogram


def load_image(image_path):
    """Read an image file from disk using OpenCV (BGR format)."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at path: {image_path}")
    return image


def extract_features(image):
    """
    Convert a raw OpenCV image (BGR numpy array) into a fixed-length
    feature vector suitable for the Random Forest classifier.
    """
    # --- Step 1: resize for a consistent input shape ---
    resized = cv2.resize(image, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

    # --- Step 2: light denoising to reduce camera/sensor noise ---
    denoised = cv2.GaussianBlur(resized, (3, 3), 0)

    # --- Step 3: color histogram features (HSV space) ---
    hsv = cv2.cvtColor(denoised, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist(
        [hsv], [0, 1, 2], None, HIST_BINS,
        [0, 180, 0, 256, 0, 256]
    )
    hist = cv2.normalize(hist, hist).flatten()  # normalize + flatten to 1D

    # --- Step 4: texture / shape features from grayscale ---
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    mean_intensity = np.mean(gray)
    std_intensity = np.std(gray)

    # Edge density: proportion of pixels detected as edges by Canny.
    # Disease lesions create irregular boundaries -> higher edge density.
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges > 0) / edges.size

    # --- Step 5: dominant "green-ness" ratio (healthy leaves are greener) ---
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    green_ratio = np.sum(green_mask > 0) / green_mask.size

    texture_features = np.array(
        [mean_intensity, std_intensity, edge_density, green_ratio]
    )

    # --- Step 6: concatenate all features into one vector ---
    feature_vector = np.concatenate([hist, texture_features]).astype(np.float32)
    return feature_vector


def preprocess_image_file(image_path):
    """Convenience wrapper: load an image from disk and extract features."""
    image = load_image(image_path)
    return extract_features(image)
