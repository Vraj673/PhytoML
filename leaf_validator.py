
import cv2
import numpy as np


def validate_leaf(image_path):
    try:
        image = cv2.imread(image_path)

        if image is None or image.size == 0:
            return {
                "valid": False,
                "plant_type": None,
                "message": "Please upload a valid image.",
            }

        height, width = image.shape[:2]

        if height < 32 or width < 32:
            return {
                "valid": False,
                "plant_type": None,
                "message": "Image resolution is too small.",
            }

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        green_mask = cv2.inRange(
            hsv,
            np.array([25, 30, 20]),
            np.array([100, 255, 255]),
        )

        green_ratio = float(np.mean(green_mask > 0))

        # Basic color screening only; not a reliable leaf classifier.
        if green_ratio < 0.03:
            return {
                "valid": False,
                "plant_type": None,
                "message": (
                    "Please upload a clear tomato or potato leaf image."
                ),
            }

        return {
            "valid": True,
            "plant_type": None,
            "message": "Image passed the basic image check.",
        }

    except (OSError, ValueError, cv2.error):
        return {
            "valid": False,
            "plant_type": None,
            "message": "Invalid image. Please upload a valid image.",
        }
