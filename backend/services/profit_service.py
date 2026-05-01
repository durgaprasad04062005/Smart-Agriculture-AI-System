"""
profit_service.py
-----------------
Business logic layer: calculates revenue, costs, and profit
for a given crop + yield + farm size.

All prices are in Indian Rupees (INR) per tonne.
Costs are per hectare.
"""

from typing import Dict, Any

# ── Market prices (INR per tonne) ─────────────────────────────────────────────
# Source: approximate MSP / mandi prices (2024 India)
MARKET_PRICES: Dict[str, float] = {
    "rice":        20000,
    "wheat":       22000,
    "maize":       18000,
    "sugarcane":   3500,
    "cotton":      65000,
    "jute":        45000,
    "coffee":      180000,
    "banana":      15000,
    "mango":       40000,
    "grapes":      60000,
    "apple":       80000,
    "orange":      35000,
    "papaya":      12000,
    "coconut":     25000,
    "watermelon":  10000,
    "muskmelon":   12000,
    "pomegranate": 70000,
    "chickpea":    55000,
    "kidneybeans": 60000,
    "lentil":      65000,
    "blackgram":   58000,
    "mungbean":    72000,
    "mothbeans":   50000,
    "pigeonpeas":  62000,
}

# ── Cost profiles (INR per hectare) ───────────────────────────────────────────
# Breakdown: fertilizer, water/irrigation, labor, seeds, misc
COST_PROFILES: Dict[str, Dict[str, float]] = {
    "rice":        dict(fertilizer=8000,  water=12000, labor=15000, seeds=3000,  misc=2000),
    "wheat":       dict(fertilizer=7000,  water=8000,  labor=12000, seeds=2500,  misc=1500),
    "maize":       dict(fertilizer=6000,  water=7000,  labor=10000, seeds=2000,  misc=1500),
    "sugarcane":   dict(fertilizer=12000, water=20000, labor=25000, seeds=8000,  misc=3000),
    "cotton":      dict(fertilizer=10000, water=15000, labor=20000, seeds=5000,  misc=3000),
    "jute":        dict(fertilizer=5000,  water=8000,  labor=12000, seeds=1500,  misc=1500),
    "coffee":      dict(fertilizer=15000, water=10000, labor=30000, seeds=20000, misc=5000),
    "banana":      dict(fertilizer=12000, water=18000, labor=20000, seeds=15000, misc=4000),
    "mango":       dict(fertilizer=8000,  water=10000, labor=15000, seeds=10000, misc=3000),
    "grapes":      dict(fertilizer=15000, water=20000, labor=25000, seeds=20000, misc=5000),
    "apple":       dict(fertilizer=12000, water=15000, labor=20000, seeds=15000, misc=4000),
    "orange":      dict(fertilizer=10000, water=12000, labor=18000, seeds=12000, misc=3000),
    "papaya":      dict(fertilizer=8000,  water=10000, labor=12000, seeds=5000,  misc=2000),
    "coconut":     dict(fertilizer=6000,  water=8000,  labor=10000, seeds=8000,  misc=2000),
    "watermelon":  dict(fertilizer=7000,  water=12000, labor=15000, seeds=3000,  misc=2000),
    "muskmelon":   dict(fertilizer=7000,  water=12000, labor=15000, seeds=3000,  misc=2000),
    "pomegranate": dict(fertilizer=10000, water=12000, labor=18000, seeds=12000, misc=3000),
    "chickpea":    dict(fertilizer=5000,  water=5000,  labor=10000, seeds=3000,  misc=1500),
    "kidneybeans": dict(fertilizer=5000,  water=6000,  labor=10000, seeds=3000,  misc=1500),
    "lentil":      dict(fertilizer=4000,  water=5000,  labor=8000,  seeds=2500,  misc=1500),
    "blackgram":   dict(fertilizer=5000,  water=5000,  labor=10000, seeds=2500,  misc=1500),
    "mungbean":    dict(fertilizer=5000,  water=5000,  labor=10000, seeds=2500,  misc=1500),
    "mothbeans":   dict(fertilizer=4000,  water=4000,  labor=8000,  seeds=2000,  misc=1000),
    "pigeonpeas":  dict(fertilizer=5000,  water=5000,  labor=10000, seeds=3000,  misc=1500),
}

DEFAULT_COST = dict(fertilizer=7000, water=8000, labor=12000, seeds=3000, misc=2000)
DEFAULT_PRICE = 25000


def calculate_profit(
    crop: str,
    yield_t_ha: float,
    hectares: float = 1.0,
    custom_price: float = None,
) -> Dict[str, Any]:
    """
    Calculate profit for a given crop and yield.

    Parameters
    ----------
    crop        : crop name (lowercase)
    yield_t_ha  : expected yield in tonnes per hectare
    hectares    : farm size in hectares (default 1)
    custom_price: override market price (INR/tonne)

    Returns
    -------
    dict with full profit breakdown
    """
    crop = crop.lower()
    price_per_tonne = custom_price or MARKET_PRICES.get(crop, DEFAULT_PRICE)
    costs           = COST_PROFILES.get(crop, DEFAULT_COST)

    total_yield   = round(yield_t_ha * hectares, 2)
    total_revenue = round(total_yield * price_per_tonne, 0)

    cost_per_ha   = sum(costs.values())
    total_cost    = round(cost_per_ha * hectares, 0)

    profit        = round(total_revenue - total_cost, 0)
    roi_pct       = round((profit / total_cost) * 100, 1) if total_cost > 0 else 0
    breakeven_yield = round(total_cost / price_per_tonne, 2) if price_per_tonne > 0 else 0

    return {
        "crop":              crop,
        "hectares":          hectares,
        "yield_per_ha":      yield_t_ha,
        "total_yield_t":     total_yield,
        "market_price_inr":  price_per_tonne,
        "total_revenue_inr": int(total_revenue),
        "cost_breakdown": {
            "fertilizer_inr": int(costs.get("fertilizer", 0) * hectares),
            "water_inr":      int(costs.get("water",      0) * hectares),
            "labor_inr":      int(costs.get("labor",      0) * hectares),
            "seeds_inr":      int(costs.get("seeds",      0) * hectares),
            "misc_inr":       int(costs.get("misc",       0) * hectares),
        },
        "total_cost_inr":    int(total_cost),
        "profit_inr":        int(profit),
        "roi_percent":       roi_pct,
        "breakeven_yield_t": breakeven_yield,
        "is_profitable":     profit > 0,
        "profit_label":      _format_inr(profit),
        "revenue_label":     _format_inr(int(total_revenue)),
        "cost_label":        _format_inr(int(total_cost)),
    }


def _format_inr(amount: int) -> str:
    """Format number as Indian Rupee string with commas."""
    if amount < 0:
        return f"-Rs.{_indian_comma(abs(amount))}"
    return f"Rs.{_indian_comma(amount)}"


def _indian_comma(n: int) -> str:
    """Apply Indian number formatting (e.g. 1,23,456)."""
    s = str(n)
    if len(s) <= 3:
        return s
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + "," + result if len(s) > 2 else s + "," + result
        s = s[:-2] if len(s) > 2 else ""
    return result


def get_all_prices() -> Dict[str, float]:
    return MARKET_PRICES.copy()
