"""
generate_data.py
----------------
Generates a synthetic crop recommendation dataset.
If you have a real dataset (e.g., from Kaggle), replace this file
with a loader that reads your CSV.
"""

import numpy as np
import pandas as pd
import os

# Reproducibility
np.random.seed(42)

# ── Crop profiles ──────────────────────────────────────────────────────────────
# Each crop has (N, P, K, temp, humidity, ph, rainfall) mean ± std ranges
CROP_PROFILES = {
    "rice":        dict(N=(80,20),  P=(40,10),  K=(40,10),  temp=(23,3),  hum=(82,5),  ph=(6.5,0.5), rain=(200,40)),
    "maize":       dict(N=(78,18),  P=(48,12),  K=(20,8),   temp=(22,4),  hum=(65,8),  ph=(6.2,0.5), rain=(60,20)),
    "chickpea":    dict(N=(40,10),  P=(67,15),  K=(80,15),  temp=(18,4),  hum=(16,5),  ph=(7.2,0.4), rain=(80,20)),
    "kidneybeans": dict(N=(20,8),   P=(67,15),  K=(20,8),   temp=(20,3),  hum=(21,5),  ph=(5.7,0.4), rain=(105,25)),
    "pigeonpeas":  dict(N=(20,8),   P=(67,15),  K=(20,8),   temp=(27,3),  hum=(48,8),  ph=(5.8,0.4), rain=(150,30)),
    "mothbeans":   dict(N=(21,8),   P=(48,12),  K=(20,8),   temp=(28,3),  hum=(53,8),  ph=(6.9,0.4), rain=(51,15)),
    "mungbean":    dict(N=(21,8),   P=(47,12),  K=(20,8),   temp=(28,3),  hum=(85,5),  ph=(6.7,0.4), rain=(48,15)),
    "blackgram":   dict(N=(40,10),  P=(67,15),  K=(19,8),   temp=(30,3),  hum=(65,8),  ph=(7.0,0.4), rain=(68,20)),
    "lentil":      dict(N=(19,8),   P=(67,15),  K=(19,8),   temp=(24,3),  hum=(64,8),  ph=(6.9,0.4), rain=(46,15)),
    "pomegranate": dict(N=(18,8),   P=(18,8),   K=(20,8),   temp=(21,4),  hum=(90,5),  ph=(6.0,0.4), rain=(107,25)),
    "banana":      dict(N=(100,20), P=(82,15),  K=(50,12),  temp=(27,3),  hum=(80,5),  ph=(6.0,0.4), rain=(105,25)),
    "mango":       dict(N=(0,5),    P=(0,5),    K=(30,8),   temp=(31,3),  hum=(50,8),  ph=(5.7,0.4), rain=(95,25)),
    "grapes":      dict(N=(23,8),   P=(132,20), K=(200,25), temp=(23,3),  hum=(82,5),  ph=(6.0,0.4), rain=(65,20)),
    "watermelon":  dict(N=(99,18),  P=(17,8),   K=(50,12),  temp=(25,3),  hum=(85,5),  ph=(6.5,0.4), rain=(50,15)),
    "muskmelon":   dict(N=(100,18), P=(17,8),   K=(50,12),  temp=(28,3),  hum=(92,4),  ph=(6.5,0.4), rain=(25,10)),
    "apple":       dict(N=(21,8),   P=(134,20), K=(199,25), temp=(21,3),  hum=(92,4),  ph=(5.8,0.4), rain=(113,25)),
    "orange":      dict(N=(0,5),    P=(0,5),    K=(10,5),   temp=(22,3),  hum=(92,4),  ph=(7.0,0.4), rain=(110,25)),
    "papaya":      dict(N=(49,12),  P=(59,12),  K=(50,12),  temp=(33,3),  hum=(92,4),  ph=(6.7,0.4), rain=(143,30)),
    "coconut":     dict(N=(22,8),   P=(16,8),   K=(30,8),   temp=(27,3),  hum=(94,4),  ph=(5.9,0.4), rain=(175,35)),
    "cotton":      dict(N=(118,20), P=(46,12),  K=(20,8),   temp=(24,3),  hum=(80,5),  ph=(6.9,0.4), rain=(80,20)),
    "jute":        dict(N=(78,18),  P=(46,12),  K=(40,10),  temp=(25,3),  hum=(80,5),  ph=(6.7,0.4), rain=(175,35)),
    "coffee":      dict(N=(101,18), P=(28,10),  K=(29,10),  temp=(25,3),  hum=(58,8),  ph=(6.8,0.4), rain=(158,30)),
    "wheat":       dict(N=(85,18),  P=(55,12),  K=(19,8),   temp=(20,4),  hum=(65,8),  ph=(6.5,0.5), rain=(70,20)),
    "sugarcane":   dict(N=(20,8),   P=(20,8),   K=(20,8),   temp=(27,3),  hum=(82,5),  ph=(6.5,0.4), rain=(85,20)),
}

SAMPLES_PER_CROP = 100  # 100 samples × 24 crops = 2400 rows

def generate_dataset(samples_per_crop: int = SAMPLES_PER_CROP) -> pd.DataFrame:
    rows = []
    for crop, p in CROP_PROFILES.items():
        for _ in range(samples_per_crop):
            row = {
                "N":           max(0, np.random.normal(*p["N"])),
                "P":           max(0, np.random.normal(*p["P"])),
                "K":           max(0, np.random.normal(*p["K"])),
                "temperature": np.clip(np.random.normal(*p["temp"]), 5, 45),
                "humidity":    np.clip(np.random.normal(*p["hum"]),  10, 100),
                "ph":          np.clip(np.random.normal(*p["ph"]),   3.5, 9.5),
                "rainfall":    max(0, np.random.normal(*p["rain"])),
                "label":       crop,
            }
            # Synthetic yield (tonnes/hectare) — loosely correlated with conditions
            base_yield = np.random.uniform(1.5, 6.0)
            humidity_bonus  = (row["humidity"] - 50) / 100
            rainfall_bonus  = (row["rainfall"] - 100) / 500
            row["yield_t_ha"] = round(max(0.5, base_yield + humidity_bonus + rainfall_bonus), 2)
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


if __name__ == "__main__":
    _here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(_here, "data"), exist_ok=True)
    df = generate_dataset()
    out_path = os.path.join(_here, "data", "crop_data.csv")
    df.to_csv(out_path, index=False)
    print(f"[OK] Dataset generated: {out_path}  ({len(df)} rows, {df['label'].nunique()} crops)")
    print(df.head())
