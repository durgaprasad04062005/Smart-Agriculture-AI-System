"""
predict.py
----------
Inference pipeline: loads saved model artifacts and returns
crop recommendation + yield prediction + natural-language explanation.
"""

import os
import pickle
import numpy as np
from typing import Dict, Any

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "crop_model.pkl")

# ── Explanation templates ──────────────────────────────────────────────────────
EXPLANATION_TEMPLATES = {
    "rice":        "High humidity ({humidity:.0f}%) and abundant rainfall ({rainfall:.0f}mm) create ideal conditions for rice cultivation.",
    "maize":       "Moderate temperature ({temperature:.1f}°C) and balanced NPK levels support healthy maize growth.",
    "wheat":       "Cool temperature ({temperature:.1f}°C) with moderate humidity ({humidity:.0f}%) is perfect for wheat.",
    "cotton":      "High nitrogen ({N:.0f}) and warm temperature ({temperature:.1f}°C) favor cotton production.",
    "sugarcane":   "Warm climate ({temperature:.1f}°C) and high humidity ({humidity:.0f}%) are ideal for sugarcane.",
    "coffee":      "Moderate rainfall ({rainfall:.0f}mm) and balanced pH ({ph:.1f}) suit coffee cultivation.",
    "jute":        "High humidity ({humidity:.0f}%) and warm temperature ({temperature:.1f}°C) are excellent for jute.",
    "coconut":     "Very high humidity ({humidity:.0f}%) and tropical temperature ({temperature:.1f}°C) favor coconut.",
    "banana":      "High potassium ({K:.0f}) and warm humid conditions ({humidity:.0f}%) support banana growth.",
    "mango":       "Warm temperature ({temperature:.1f}°C) with moderate rainfall ({rainfall:.0f}mm) suits mango trees.",
    "grapes":      "High potassium ({K:.0f}) and moderate humidity ({humidity:.0f}%) are ideal for grape cultivation.",
    "apple":       "Cool temperature ({temperature:.1f}°C) and high phosphorus ({P:.0f}) favor apple orchards.",
    "orange":      "Moderate temperature ({temperature:.1f}°C) and high humidity ({humidity:.0f}%) suit orange trees.",
    "papaya":      "High temperature ({temperature:.1f}°C) and abundant rainfall ({rainfall:.0f}mm) favor papaya.",
    "watermelon":  "Warm temperature ({temperature:.1f}°C) and high nitrogen ({N:.0f}) support watermelon growth.",
    "muskmelon":   "High temperature ({temperature:.1f}°C) and very high humidity ({humidity:.0f}%) suit muskmelon.",
    "pomegranate": "Moderate temperature ({temperature:.1f}°C) and high humidity ({humidity:.0f}%) favor pomegranate.",
    "chickpea":    "Cool temperature ({temperature:.1f}°C) and low humidity ({humidity:.0f}%) are ideal for chickpea.",
    "kidneybeans": "Moderate temperature ({temperature:.1f}°C) and balanced pH ({ph:.1f}) suit kidney beans.",
    "lentil":      "Moderate temperature ({temperature:.1f}°C) and low rainfall ({rainfall:.0f}mm) favor lentils.",
    "blackgram":   "High temperature ({temperature:.1f}°C) and moderate humidity ({humidity:.0f}%) suit black gram.",
    "mungbean":    "Warm temperature ({temperature:.1f}°C) and high humidity ({humidity:.0f}%) favor mung beans.",
    "mothbeans":   "High temperature ({temperature:.1f}°C) and low rainfall ({rainfall:.0f}mm) suit moth beans.",
    "pigeonpeas":  "Warm temperature ({temperature:.1f}°C) and moderate rainfall ({rainfall:.0f}mm) favor pigeon peas.",
}

DEFAULT_TEMPLATE = (
    "Based on your soil conditions (pH {ph:.1f}, N:{N:.0f}, P:{P:.0f}, K:{K:.0f}) "
    "and climate data (temperature {temperature:.1f}°C, humidity {humidity:.0f}%, "
    "rainfall {rainfall:.0f}mm), {crop} is the most suitable crop."
)

# Soil type yield multipliers
SOIL_MULTIPLIERS = {
    "loamy":  1.10,
    "clay":   0.95,
    "sandy":  0.85,
    "silty":  1.05,
    "peaty":  1.00,
    "chalky": 0.90,
    "other":  1.00,
}


def load_model() -> Dict[str, Any]:
    """Load model artifacts from disk."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Please run `python model/train.py` first."
        )
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def build_explanation(crop: str, features: Dict[str, float]) -> str:
    """Generate a human-readable explanation for the prediction."""
    template = EXPLANATION_TEMPLATES.get(crop, DEFAULT_TEMPLATE)
    try:
        return template.format(crop=crop, **features)
    except KeyError:
        return DEFAULT_TEMPLATE.format(crop=crop, **features)


def predict(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run inference on a single input.

    Parameters
    ----------
    input_data : dict with keys:
        N, P, K, temperature, humidity, ph, rainfall, soil_type (optional)

    Returns
    -------
    dict with crop, confidence, expected_yield, explanation,
         feature_importance, top_alternatives
    """
    artifacts = load_model()
    clf       = artifacts["classifier"]
    reg       = artifacts["regressor"]
    le        = artifacts["label_encoder"]
    scaler    = artifacts["scaler"]
    feat_cols = artifacts["feature_cols"]
    feat_imp  = artifacts["feature_importance"]

    # ── Build feature vector ───────────────────────────────────────────────────
    features = {
        "N":           float(input_data.get("nitrogen",    input_data.get("N", 80))),
        "P":           float(input_data.get("phosphorus",  input_data.get("P", 40))),
        "K":           float(input_data.get("potassium",   input_data.get("K", 40))),
        "temperature": float(input_data.get("temperature", 25)),
        "humidity":    float(input_data.get("humidity",    70)),
        "ph":          float(input_data.get("ph",          6.5)),
        "rainfall":    float(input_data.get("rainfall",    100)),
    }
    soil_type = str(input_data.get("soil_type", "loamy")).lower()

    X_raw    = np.array([[features[c] for c in feat_cols]])
    X_scaled = scaler.transform(X_raw)

    # ── Classification ─────────────────────────────────────────────────────────
    proba      = clf.predict_proba(X_scaled)[0]
    top_idx    = np.argsort(proba)[::-1]
    crop       = le.classes_[top_idx[0]]
    confidence = round(float(proba[top_idx[0]]), 4)

    # Top 3 alternatives (excluding the top prediction)
    alternatives = [le.classes_[i] for i in top_idx[1:4]]

    # ── Regression ─────────────────────────────────────────────────────────────
    raw_yield = float(reg.predict(X_scaled)[0])
    multiplier = SOIL_MULTIPLIERS.get(soil_type, 1.0)
    expected_yield = round(raw_yield * multiplier, 2)

    # ── Explanation ────────────────────────────────────────────────────────────
    explanation = build_explanation(crop, features)

    return {
        "crop":               crop,
        "confidence":         confidence,
        "confidence_pct":     f"{confidence * 100:.1f}%",
        "expected_yield":     expected_yield,
        "yield_unit":         "tonnes/hectare",
        "explanation":        explanation,
        "feature_importance": feat_imp,
        "top_alternatives":   alternatives,
        "soil_type":          soil_type,
        "input_features":     features,
        "model_accuracy":     artifacts.get("accuracy"),
    }


if __name__ == "__main__":
    # Quick smoke test
    sample = {
        "nitrogen": 90, "phosphorus": 42, "potassium": 43,
        "temperature": 20.8, "humidity": 82.0, "ph": 6.5,
        "rainfall": 202.9, "soil_type": "loamy",
    }
    result = predict(sample)
    print(f"\n[RESULT] Recommended Crop : {result['crop'].upper()}")
    print(f"         Confidence       : {result['confidence_pct']}")
    print(f"         Expected Yield   : {result['expected_yield']} {result['yield_unit']}")
    print(f"         Explanation      : {result['explanation']}")
    print(f"         Alternatives     : {', '.join(result['top_alternatives'])}")
