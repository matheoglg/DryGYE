"""Simple, transparent scenario-based rain and tide alert levels."""
from drygye.config import RAIN_RED_MM_24H, RAIN_YELLOW_MM_24H, TIDE_HIGH_M

SCENARIOS = {
    "normal": {"label": "Normal", "rain_24h": 5.0, "tide_m": 2.2},
    "heavy_rain": {"label": "Heavy rain", "rain_24h": 30.0, "tide_m": 2.2},
    "heavy_rain_high_tide": {"label": "Heavy rain + high tide", "rain_24h": 45.0, "tide_m": 4.5},
}


def current_state(scenario="normal"):
    values = SCENARIOS.get(scenario, SCENARIOS["normal"])
    rain, tide = values["rain_24h"], values["tide_m"]
    level = "red" if rain > RAIN_RED_MM_24H else "yellow" if rain >= RAIN_YELLOW_MM_24H else "green"
    if level == "green" and tide >= TIDE_HIGH_M and rain >= 10:
        level = "yellow"
    factor = min(2.0, max(0.5, 0.5 + rain / RAIN_RED_MM_24H + (0.3 if tide >= TIDE_HIGH_M else 0)))
    return {"level": level, "rain_24h": rain, "tide_m": tide, "factor": round(factor, 2),
            "mode": "simulation", "scenario": values["label"]}


def forecast_state(rain_24h, tide_m=None):
    """Build route state from point forecast rain and optional INOCAR tide prediction."""
    rain = max(0.0, float(rain_24h))
    level = "red" if rain > RAIN_RED_MM_24H else "yellow" if rain >= RAIN_YELLOW_MM_24H else "green"
    high_tide = tide_m is not None and float(tide_m) >= TIDE_HIGH_M
    if level == "green" and high_tide and rain >= 10:
        level = "yellow"
    factor = min(2.0, max(0.5, 0.5 + rain / RAIN_RED_MM_24H + (0.3 if high_tide else 0)))
    return {"level": level, "rain_24h": rain, "tide_m": tide_m, "factor": round(factor, 2),
            "mode": "forecast", "scenario": "Open-Meteo + INOCAR" if tide_m is not None else "Open-Meteo point forecast",
            "tide_included": tide_m is not None}
