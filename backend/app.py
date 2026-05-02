"""
app.py  —  Smart Agriculture AI System (Advanced)
--------------------------------------------------
REST API endpoints:
  GET  /health
  POST /predict          crop + yield prediction
  POST /profit           profit calculation
  POST /weather          real-time weather by city
  POST /chat             AI chat assistant
  POST /train            retrain ML model
  GET  /data             sample data / history
  GET  /crops            supported crops list
  GET  /meta             model metadata
  GET  /prices           market prices
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ── Load environment variables ─────────────────────────────────────────────────
load_dotenv()

# ── Add model directory to Python path ────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model")
SVC_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "services")
sys.path.insert(0, MODEL_DIR)
sys.path.insert(0, SVC_DIR)

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ── In-memory prediction history ──────────────────────────────────────────────
prediction_history: list = []

# ── Lazy model loader ──────────────────────────────────────────────────────────
_model_loaded = False

def ensure_model():
    global _model_loaded
    if _model_loaded:
        return
    artifacts_path = os.path.join(MODEL_DIR, "artifacts", "crop_model.pkl")
    if not os.path.exists(artifacts_path):
        logger.info("Model not found — training now ...")
        _train_model()
    _model_loaded = True


def _train_model():
    import subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    for script in ["generate_data.py", "train.py"]:
        result = subprocess.run(
            [sys.executable, os.path.join(MODEL_DIR, script)],
            capture_output=True, text=True, encoding="utf-8", env=env,
        )
        logger.info(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(f"{script} failed:\n{result.stderr}")


# ── Validation helpers ─────────────────────────────────────────────────────────
FIELD_RANGES = {
    "nitrogen":    (0, 200),
    "phosphorus":  (0, 200),
    "potassium":   (0, 250),
    "temperature": (0, 50),
    "humidity":    (0, 100),
    "ph":          (0, 14),
    "rainfall":    (0, 500),
}

def validate_fields(data: dict) -> str | None:
    """Return error string or None if valid."""
    missing = [f for f in FIELD_RANGES if f not in data]
    if missing:
        return f"Missing fields: {missing}"
    for field, (lo, hi) in FIELD_RANGES.items():
        try:
            val = float(data[field])
        except (TypeError, ValueError):
            return f"{field} must be a number"
        if not (lo <= val <= hi):
            return f"{field} must be between {lo} and {hi}"
    return None


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name":      "Smart Agriculture AI API",
        "version":   "2.0",
        "status":    "running",
        "endpoints": ["/health", "/predict", "/profit", "/weather", "/chat", "/train", "/data", "/crops", "/meta", "/prices"]
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ── /predict ──────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict best crop + yield.
    Body: { nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, soil_type? }
    """
    try:
        ensure_model()
        data = request.get_json(force=True) or {}
        err  = validate_fields(data)
        if err:
            return jsonify({"error": err}), 400

        from predict import predict as run_predict
        result = run_predict(data)

        # Auto-calculate profit and attach
        from profit_service import calculate_profit
        profit = calculate_profit(
            crop=result["crop"],
            yield_t_ha=result["expected_yield"],
            hectares=float(data.get("hectares", 1.0)),
        )
        result["profit"] = profit

        # Store history
        entry = {
            "id":        len(prediction_history) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "input":     data,
            "output":    result,
        }
        prediction_history.append(entry)
        if len(prediction_history) > 50:
            prediction_history.pop(0)

        logger.info(f"Predict: {result['crop']} ({result['confidence_pct']}) profit={profit['profit_label']}")
        return jsonify(result)

    except FileNotFoundError as e:
        return jsonify({"error": str(e), "hint": "POST /train first"}), 503
    except Exception as e:
        logger.exception("Prediction error")
        return jsonify({"error": str(e)}), 500


# ── /profit ───────────────────────────────────────────────────────────────────
@app.route("/profit", methods=["POST"])
def profit():
    """
    Calculate profit for a crop + yield.
    Body: { crop, yield_t_ha, hectares?, custom_price? }
    """
    try:
        data = request.get_json(force=True) or {}
        crop = data.get("crop")
        if not crop:
            return jsonify({"error": "crop is required"}), 400
        yield_t_ha = float(data.get("yield_t_ha", 3.0))
        hectares   = float(data.get("hectares",   1.0))
        custom_price = data.get("custom_price")
        if custom_price:
            custom_price = float(custom_price)

        from profit_service import calculate_profit
        result = calculate_profit(crop, yield_t_ha, hectares, custom_price)
        return jsonify(result)

    except Exception as e:
        logger.exception("Profit error")
        return jsonify({"error": str(e)}), 500


# ── /weather ──────────────────────────────────────────────────────────────────
@app.route("/weather", methods=["POST"])
def weather():
    """
    Fetch real-time weather for a city.
    Body: { city: "Mumbai" }
    Returns: { temperature, humidity, rainfall, description, source }
    """
    try:
        data = request.get_json(force=True) or {}
        city = data.get("city", "").strip()
        if not city:
            return jsonify({"error": "city is required"}), 400

        from weather_service import get_weather_by_city
        result = get_weather_by_city(city)
        return jsonify(result)

    except Exception as e:
        logger.exception("Weather error")
        return jsonify({"error": str(e)}), 500


# ── /chat ─────────────────────────────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """
    AI chat assistant.
    Body: { message, context? (prediction result), history? }
    """
    try:
        data    = request.get_json(force=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "message is required"}), 400

        context = data.get("context")   # optional prediction result
        history = data.get("history")   # optional conversation history

        from chat_service import get_chat_response
        result = get_chat_response(message, context, history)
        return jsonify(result)

    except Exception as e:
        logger.exception("Chat error")
        return jsonify({"error": str(e)}), 500


# ── /train ────────────────────────────────────────────────────────────────────
@app.route("/train", methods=["POST"])
def train():
    """Retrain the ML model."""
    try:
        global _model_loaded
        _model_loaded = False
        _train_model()
        _model_loaded = True

        meta_path = os.path.join(MODEL_DIR, "artifacts", "model_meta.json")
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        return jsonify({"status": "success", "message": "Model retrained", "metadata": meta})
    except Exception as e:
        logger.exception("Training error")
        return jsonify({"error": str(e)}), 500


# ── /data ─────────────────────────────────────────────────────────────────────
@app.route("/data", methods=["GET"])
def data():
    """GET /data?type=sample|history"""
    try:
        dtype = request.args.get("type", "sample")

        if dtype == "history":
            return jsonify({"count": len(prediction_history), "history": prediction_history[-20:]})

        import pandas as pd
        data_path = os.path.join(MODEL_DIR, "data", "crop_data.csv")
        if not os.path.exists(data_path):
            return jsonify({"error": "Dataset not found. POST /train first."}), 404

        df = pd.read_csv(data_path)
        sample = df.sample(10, random_state=42).to_dict(orient="records")
        stats  = {
            col: {"mean": round(df[col].mean(), 2), "min": round(df[col].min(), 2), "max": round(df[col].max(), 2)}
            for col in ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "yield_t_ha"]
        }
        return jsonify({
            "total_rows":  len(df),
            "sample":      sample,
            "stats":       stats,
            "crop_counts": df["label"].value_counts().to_dict(),
        })
    except Exception as e:
        logger.exception("Data error")
        return jsonify({"error": str(e)}), 500


# ── /crops ────────────────────────────────────────────────────────────────────
@app.route("/crops", methods=["GET"])
def crops():
    meta_path = os.path.join(MODEL_DIR, "artifacts", "model_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            return jsonify({"crops": json.load(f).get("crops", [])})
    return jsonify({"crops": list(__import__("profit_service").MARKET_PRICES.keys())})


# ── /meta ─────────────────────────────────────────────────────────────────────
@app.route("/meta", methods=["GET"])
def meta():
    meta_path = os.path.join(MODEL_DIR, "artifacts", "model_meta.json")
    if not os.path.exists(meta_path):
        return jsonify({"error": "Model not trained. POST /train first."}), 404
    with open(meta_path, encoding="utf-8") as f:
        return jsonify(json.load(f))


# ── /prices ───────────────────────────────────────────────────────────────────
@app.route("/prices", methods=["GET"])
def prices():
    """Return all crop market prices."""
    from profit_service import get_all_prices
    return jsonify({"prices": get_all_prices(), "currency": "INR", "unit": "per tonne"})


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Smart Agriculture AI on port {port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
