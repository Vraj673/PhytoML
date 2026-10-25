
import torch
from PIL import Image, UnidentifiedImageError
from transformers import CLIPProcessor, CLIPModel

MODEL_NAME = "openai/clip-vit-base-patch32"

_processor = None
_model = None

CANDIDATES = [
    "a photo of a tomato leaf",
    "a close-up photo of a tomato plant leaf",
    "a photo of a tomato leaf with disease spots",
    "a photo of a healthy tomato leaf",
    "a photo of a potato leaf",
    "a close-up photo of a potato plant leaf",
    "a photo of a potato leaf with disease spots",
    "a photo of a healthy potato leaf",
    "a photo of another plant leaf",
    "a photo of a car, bike, person, animal, or other object",
]

def _load_model():
    global _processor, _model

    if _processor is None or _model is None:
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _model = CLIPModel.from_pretrained(MODEL_NAME)
        _model.eval()

    return _processor, _model


def validate_leaf(image_path):
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")

        processor, model = _load_model()

        inputs = processor(
            text=CANDIDATES,
            images=image,
            return_tensors="pt",
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)

        # Compare image similarity across all descriptions.
        scores = outputs.logits_per_image[0].softmax(dim=0)

        tomato_score = sum(scores[i].item() for i in range(4))
        potato_score = sum(scores[i].item() for i in range(4, 8))
        other_plant_score = scores[8].item()
        object_score = scores[9].item()

        best_leaf_score = max(tomato_score, potato_score)

        # Initial threshold for testing, not a guaranteed confidence score.
        if (
            best_leaf_score < 0.35
            or best_leaf_score <= other_plant_score
            or best_leaf_score <= object_score
        ):
            return {
                "valid": False,
                "plant_type": None,
                "message": "Please scan only tomato or potato leaf images.",
            }

        plant_type = (
            "tomato" if tomato_score >= potato_score else "potato"
        )

        return {
            "valid": True,
            "plant_type": plant_type,
            "message": "Valid leaf image.",
        }

    except (UnidentifiedImageError, OSError, ValueError):
        return {
            "valid": False,
            "plant_type": None,
            "message": "Invalid image. Please upload a valid image.",
        }
    except Exception:
        return {
            "valid": False,
            "plant_type": None,
            "message": "Image validation failed. Please try again.",
        }
