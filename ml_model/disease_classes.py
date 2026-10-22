"""
ml_model/disease_classes.py
----------------------------
Single source of truth for the set of disease classes the Random Forest
model can predict. Each entry also carries the recommendation content
(symptoms / causes / treatment) which is used to seed the `diseases`
table in the database on first run.

To use a REAL dataset instead of the bundled demo data:
    1. Create a folder structure:  data/train/<class_label>/*.jpg
       where <class_label> matches one of the keys below (or add new
       keys here for new classes).
    2. Run:  python ml_model/train_model.py
       The script automatically detects the data/train folder and
       trains on the real images. If it is not found, a small synthetic
       dataset is generated instead so the app still works out of the box.
"""

DISEASE_INFO = {
    "Apple___Apple_scab": {
        "crop_name": "Apple",
        "disease_name": "Apple Scab",
        "symptoms": "Olive-green to brown velvety spots on leaves and fruit; "
                    "leaves may curl, yellow, and drop early; fruit develops "
                    "corky, scabby lesions.",
        "causes": "Caused by the fungus Venturia inaequalis, which spreads via "
                  "wind-blown spores during cool, wet spring weather.",
        "treatment": "Remove and destroy fallen leaves, prune for better air "
                     "circulation, apply fungicide sprays (e.g. captan or "
                     "myclobutanil) starting at bud break, and choose "
                     "scab-resistant apple varieties.",
        "is_healthy": False,
    },
    "Apple___Black_rot": {
        "crop_name": "Apple",
        "disease_name": "Apple Black Rot",
        "symptoms": "Purple-bordered brown leaf spots ('frog-eye leaf spot'), "
                    "rotting fruit with concentric rings, and cankers on branches.",
        "causes": "Fungus Botryosphaeria obtusa, which overwinters in dead wood, "
                  "mummified fruit, and cankers, spreading during warm, humid weather.",
        "treatment": "Prune out dead/diseased wood and cankers, remove mummified "
                     "fruit, apply appropriate fungicide during the growing season, "
                     "and maintain tree vigor with proper fertilization.",
        "is_healthy": False,
    },
    "Apple___healthy": {
        "crop_name": "Apple",
        "disease_name": "Healthy",
        "symptoms": "No visible lesions, discoloration, or deformities; leaves are "
                    "uniformly green with a normal glossy texture.",
        "causes": "N/A - plant is healthy.",
        "treatment": "Continue regular watering, balanced fertilization, and "
                     "routine monitoring to maintain plant health.",
        "is_healthy": True,
    },
    "Corn___Common_rust": {
        "crop_name": "Corn (Maize)",
        "disease_name": "Common Rust",
        "symptoms": "Small, round to elongate, cinnamon-brown pustules scattered "
                    "on both leaf surfaces that rupture and release rust-colored spores.",
        "causes": "Fungus Puccinia sorghi; favored by cool temperatures (16-25°C) "
                  "and high humidity or leaf wetness.",
        "treatment": "Plant rust-resistant hybrids, apply foliar fungicides "
                     "(e.g. strobilurins or triazoles) when pustules first appear, "
                     "and rotate crops to reduce inoculum.",
        "is_healthy": False,
    },
    "Corn___healthy": {
        "crop_name": "Corn (Maize)",
        "disease_name": "Healthy",
        "symptoms": "Leaves are uniformly green with no pustules, lesions, or "
                    "discoloration; normal growth pattern.",
        "causes": "N/A - plant is healthy.",
        "treatment": "Maintain balanced nitrogen fertilization, adequate spacing, "
                     "and regular field scouting.",
        "is_healthy": True,
    },
    "Potato___Early_blight": {
        "crop_name": "Potato",
        "disease_name": "Early Blight",
        "symptoms": "Dark brown spots with concentric 'target board' rings, "
                    "usually starting on older/lower leaves, surrounded by a "
                    "yellow halo.",
        "causes": "Fungus Alternaria solani; thrives in warm temperatures with "
                  "alternating wet and dry periods, and is worsened by plant stress.",
        "treatment": "Remove infected leaves, apply fungicide (chlorothalonil or "
                     "mancozeb), rotate crops with non-solanaceous plants, and "
                     "avoid overhead irrigation to keep foliage dry.",
        "is_healthy": False,
    },
    "Potato___Late_blight": {
        "crop_name": "Potato",
        "disease_name": "Late Blight",
        "symptoms": "Water-soaked, irregular gray-green lesions on leaves that "
                    "rapidly turn brown/black; white fungal growth may appear on "
                    "the underside in humid conditions; can destroy a field in days.",
        "causes": "Oomycete Phytophthora infestans, spread rapidly in cool, "
                  "wet, humid weather (the same pathogen that caused the Irish "
                  "potato famine).",
        "treatment": "Apply protectant fungicides preventively (e.g. copper-based "
                     "or chlorothalonil), destroy infected plants immediately, "
                     "improve field drainage/airflow, and avoid overhead watering.",
        "is_healthy": False,
    },
    "Potato___healthy": {
        "crop_name": "Potato",
        "disease_name": "Healthy",
        "symptoms": "Uniform green foliage with no spots, wilting, or lesions.",
        "causes": "N/A - plant is healthy.",
        "treatment": "Maintain proper irrigation, hilling, and balanced fertilization.",
        "is_healthy": True,
    },
    "Tomato___Bacterial_spot": {
        "crop_name": "Tomato",
        "disease_name": "Bacterial Spot",
        "symptoms": "Small, water-soaked, dark spots on leaves, stems, and fruit "
                    "that later turn brown with a yellow halo; leaves may become "
                    "ragged and drop.",
        "causes": "Xanthomonas bacteria species; spread by splashing water, rain, "
                  "and contaminated tools, favored by warm and wet conditions.",
        "treatment": "Use copper-based bactericides, avoid overhead irrigation, "
                     "remove and destroy infected plant debris, and use "
                     "disease-free certified seed/transplants.",
        "is_healthy": False,
    },
    "Tomato___Late_blight": {
        "crop_name": "Tomato",
        "disease_name": "Late Blight",
        "symptoms": "Large, irregular, greasy-looking gray-green to brown "
                    "blotches on leaves; white mold ring on the underside in "
                    "humid weather; fruit shows firm, dark, greasy lesions.",
        "causes": "Oomycete Phytophthora infestans, spreading fast in cool, "
                  "wet weather via wind-blown spores.",
        "treatment": "Apply fungicides preventively (chlorothalonil, copper), "
                     "remove infected plants promptly, stake plants for airflow, "
                     "and avoid working in wet fields to reduce spread.",
        "is_healthy": False,
    },
    "Tomato___healthy": {
        "crop_name": "Tomato",
        "disease_name": "Healthy",
        "symptoms": "Vigorous green foliage, no spots or wilting, normal fruit development.",
        "causes": "N/A - plant is healthy.",
        "treatment": "Continue consistent watering, staking, and balanced fertilization.",
        "is_healthy": True,
    },
}

CLASS_LABELS = sorted(DISEASE_INFO.keys())
