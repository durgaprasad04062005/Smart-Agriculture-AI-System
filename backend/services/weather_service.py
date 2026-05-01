"""
weather_service.py
------------------
Fetches real-time weather data from OpenWeatherMap API.
Falls back to simulated data if API key is not set.
"""

import os
import random
import logging
from datetime import datetime

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logger = logging.getLogger(__name__)

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"

# ── Simulated profiles (fallback) ─────────────────────────────────────────────
SIMULATED_PROFILES = {
    "tropical":  dict(temp=(25, 35),  hum=(70, 95),  rain=(100, 300)),
    "temperate": dict(temp=(10, 25),  hum=(50, 75),  rain=(40,  120)),
    "arid":      dict(temp=(30, 45),  hum=(10, 30),  rain=(5,   50)),
    "humid":     dict(temp=(20, 30),  hum=(80, 100), rain=(150, 400)),
}


def get_weather_by_city(city: str) -> dict:
    """
    Fetch current weather for a city using OpenWeatherMap.
    Returns temperature (°C), humidity (%), and estimated rainfall (mm).
    Falls back to simulation if API key is missing or request fails.
    """
    api_key = os.environ.get("WEATHER_API_KEY", "").strip()

    if api_key and HAS_REQUESTS:
        try:
            url = f"{OPENWEATHER_BASE}/weather"
            params = {"q": city, "appid": api_key, "units": "metric"}
            resp = _requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()

            # rainfall: OpenWeatherMap gives rain.1h in mm (may be absent)
            rain_1h = data.get("rain", {}).get("1h", 0.0)
            # Annualise roughly: multiply hourly by 8760 then scale to seasonal
            # For crop recommendation we use a 3-month seasonal estimate
            seasonal_rain = round(rain_1h * 24 * 90, 1)  # 90-day estimate

            return {
                "city":        data.get("name", city),
                "country":     data.get("sys", {}).get("country", ""),
                "temperature": round(data["main"]["temp"], 1),
                "humidity":    round(data["main"]["humidity"], 1),
                "rainfall":    seasonal_rain,
                "description": data["weather"][0]["description"].title(),
                "icon":        data["weather"][0]["icon"],
                "source":      "openweathermap",
                "timestamp":   datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.warning(f"OpenWeatherMap failed for '{city}': {e}. Using simulation.")

    # ── Fallback: simulate based on city name heuristics ──────────────────────
    return _simulate_for_city(city)


def _simulate_for_city(city: str) -> dict:
    """Heuristic simulation based on city name."""
    city_lower = city.lower()
    # Very rough climate zone mapping
    tropical_cities  = ["mumbai", "chennai", "kolkata", "delhi", "bangalore",
                         "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow",
                         "patna", "bhopal", "indore", "nagpur", "surat",
                         "jakarta", "bangkok", "manila", "singapore", "kuala"]
    arid_cities      = ["dubai", "riyadh", "cairo", "karachi", "lahore",
                         "jodhpur", "bikaner", "jaisalmer"]
    temperate_cities = ["london", "paris", "berlin", "moscow", "toronto",
                         "sydney", "melbourne", "tokyo", "seoul", "beijing"]

    if any(c in city_lower for c in tropical_cities):
        profile_key = "tropical"
    elif any(c in city_lower for c in arid_cities):
        profile_key = "arid"
    elif any(c in city_lower for c in temperate_cities):
        profile_key = "temperate"
    else:
        profile_key = "humid"

    p = SIMULATED_PROFILES[profile_key]
    return {
        "city":        city.title(),
        "country":     "IN",
        "temperature": round(random.uniform(*p["temp"]), 1),
        "humidity":    round(random.uniform(*p["hum"]),  1),
        "rainfall":    round(random.uniform(*p["rain"]), 1),
        "description": "Simulated Data",
        "icon":        "01d",
        "source":      "simulated",
        "region":      profile_key,
        "timestamp":   datetime.utcnow().isoformat(),
        "note":        "Set WEATHER_API_KEY in .env for real data",
    }
