"""Cached point forecast for Guayaquil from Open-Meteo."""
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from drygye.config import CACHE_DIR, CITY_CENTER, OPEN_METEO_FORECAST_URL, TIMEZONE, WEATHER_CACHE_MAX_AGE_MIN

CACHE_FILE = CACHE_DIR / "guayaquil_forecast.json"
LOCAL_TZ = ZoneInfo(TIMEZONE)


class WeatherUnavailable(RuntimeError):
    pass


def get_forecast(force_refresh=False):
    cached = _read_cache()
    if cached and not force_refresh:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached["fetched_at"])).total_seconds() / 60
        if age <= WEATHER_CACHE_MAX_AGE_MIN:
            cached["stale"] = False
            return cached
    try:
        response = requests.get(OPEN_METEO_FORECAST_URL, params={
            "latitude": CITY_CENTER[0], "longitude": CITY_CENTER[1],
            "hourly": "precipitation,precipitation_probability,temperature_2m",
            "forecast_hours": 48, "timezone": TIMEZONE,
        }, timeout=12)
        response.raise_for_status()
        payload = response.json()
        hourly = payload["hourly"]
        result = {
            "source": "Open-Meteo", "timezone": payload.get("timezone", TIMEZONE),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "time": hourly["time"][:48], "precip_mm": hourly["precipitation"][:48],
            "precip_probability": hourly["precipitation_probability"][:48],
            "temperature_c": hourly["temperature_2m"][:48], "stale": False,
        }
        if not result["time"]:
            raise ValueError("Forecast response had no hourly values.")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(result), encoding="utf-8")
        return result
    except Exception as exc:
        if cached:
            cached["stale"] = True
            cached["warning"] = "Showing cached forecast because the live service is unavailable."
            return cached
        raise WeatherUnavailable("Live forecast unavailable and no cached forecast exists.") from exc


def _read_cache():
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def forecast_summary(data):
    now = datetime.now(LOCAL_TZ).replace(minute=0, second=0, microsecond=0)
    times = [datetime.fromisoformat(value).replace(tzinfo=LOCAL_TZ) for value in data["time"]]
    start = next((i for i, value in enumerate(times) if value >= now), 0)
    end = min(start + 24, len(times))
    return {
        "next_24h_mm": round(sum(float(v or 0) for v in data["precip_mm"][start:end]), 1),
        "next_3h_mm": round(sum(float(v or 0) for v in data["precip_mm"][start:start + 3]), 1),
        "hours": [{"time": data["time"][i], "precip_mm": float(data["precip_mm"][i] or 0),
                   "probability": data["precip_probability"][i], "temperature_c": data["temperature_c"][i]}
                  for i in range(start, min(start + 12, len(times)))],
        "fetched_at": data["fetched_at"], "source": data["source"],
        "stale": data.get("stale", False), "warning": data.get("warning"),
        "location": {"lat": CITY_CENTER[0], "lon": CITY_CENTER[1]},
    }
