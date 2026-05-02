"""
train.py
--------
Trains a Random Forest classifier (crop recommendation) and a
Random Forest regressor (yield prediction), then saves both models
along with the label encoder and feature scaler.
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report,
    mean_absolute_error, r2_score,
)

# Force UTF-8 output so print() never hits cp1252 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths (always relative to this script's directory) ────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(_HERE, "data", "crop_data.csv")
MODEL_DIR  = os.path.join(_HERE, "artifacts")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_CLASS = "label"
TARGET_REG   = "yield_t_ha"


def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        print("Dataset not found. Generating synthetic data ...")
        from generate_data import generate_dataset
        os.makedirs(os.path.join(_HERE, "data"), exist_ok=True)
        df = generate_dataset()
        df.to_csv(DATA_PATH, index=False)
    else:
        df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, {df[TARGET_CLASS].nunique()} unique crops.")
    return df


def train():
    df = load_data()

    X = df[FEATURE_COLS].values
    y_class = df[TARGET_CLASS].values
    y_reg   = df[TARGET_REG].values

    # ── Label encode crop names ────────────────────────────────────────────────
    le = LabelEncoder()
    y_enc = le.fit_transform(y_class)

    # ── Scale features ─────────────────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── Train / test split ─────────────────────────────────────────────────────
    X_tr, X_te, yc_tr, yc_te, yr_tr, yr_te = train_test_split(
        X_scaled, y_enc, y_reg, test_size=0.2, random_state=42, stratify=y_enc
    )

    # ── Classifier ─────────────────────────────────────────────────────────────
    clf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    clf.fit(X_tr, yc_tr)
    yc_pred = clf.predict(X_te)
    acc = accuracy_score(yc_te, yc_pred)
    print(f"\n[OK] Classifier Accuracy : {acc:.4f}")
    print(classification_report(yc_te, yc_pred, target_names=le.classes_))

    # ── Regressor ──────────────────────────────────────────────────────────────
    reg = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    reg.fit(X_tr, yr_tr)
    yr_pred = reg.predict(X_te)
    mae = mean_absolute_error(yr_te, yr_pred)
    r2  = r2_score(yr_te, yr_pred)
    print(f"[OK] Regressor  MAE      : {mae:.4f}  |  R2: {r2:.4f}")

    # ── Feature importance ─────────────────────────────────────────────────────
    importance = dict(zip(FEATURE_COLS, clf.feature_importances_.tolist()))
    importance_sorted = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    print("\n[INFO] Feature Importances:")
    for feat, imp in importance_sorted.items():
        bar = "#" * int(imp * 40)
        print(f"  {feat:<12} {imp:.4f}  {bar}")

    # ── Save artifacts ─────────────────────────────────────────────────────────
    artifacts = {
        "classifier":         clf,
        "regressor":          reg,
        "label_encoder":      le,
        "scaler":             scaler,
        "feature_cols":       FEATURE_COLS,
        "feature_importance": importance_sorted,
        "accuracy":           round(acc, 4),
        "mae":                round(mae, 4),
        "r2":                 round(r2, 4),
    }

    pkl_path = os.path.join(MODEL_DIR, "crop_model.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(artifacts, f)
    print(f"\n[SAVED] Model saved -> {pkl_path}")

    # Also save metadata as JSON for quick inspection
    meta = {
        "crops":              le.classes_.tolist(),
        "feature_cols":       FEATURE_COLS,
        "feature_importance": importance_sorted,
        "accuracy":           round(acc, 4),
        "mae":                round(mae, 4),
        "r2":                 round(r2, 4),
    }
    meta_path = os.path.join(MODEL_DIR, "model_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[SAVED] Metadata saved -> {meta_path}")

    return artifacts


if __name__ == "__main__":
    train()
