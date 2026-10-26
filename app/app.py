"""DryGYE pilot web application.

Run from the repo root with  python -m app.app  or  python app/app.py
"""
import json
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from datetime import datetime
from zoneinfo import ZoneInfo

# Lets "python app/app.py" find the drygye package in the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drygye.alerts import SCENARIOS, current_state, forecast_state
from drygye.routing import compare_routes
from drygye.terrain import risk_geojson
from drygye.weather import WeatherUnavailable, forecast_summary, get_forecast
from drygye.config import FLOOD_REFERENCE_PATH, TIMEZONE


def _forecast_state():
    summary = forecast_summary(get_forecast())
    tide_m = None
    try:
        from drygye.tides import tide_height_at
        tide_m = tide_height_at(datetime.now(ZoneInfo(TIMEZONE)))
    except (OSError, ValueError, ImportError):
        pass
    result = forecast_state(summary["next_24h_mm"], tide_m)
    result.update({"forecast_stale": summary["stale"], "source": summary["source"],
                   "tide_source": "INOCAR" if tide_m is not None else None})
    return result

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def state():
    if request.args.get("mode") == "forecast":
        try:
            return jsonify(_forecast_state())
        except WeatherUnavailable as exc:
            return jsonify({"error": str(exc)}), 503
    return jsonify(current_state(request.args.get("scenario", "normal")))


@app.get("/api/risk")
def risk():
    try:
        return jsonify(risk_geojson())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/reference/flood-zones")
def reference_flood_zones():
    if not FLOOD_REFERENCE_PATH.exists():
        return jsonify({"error": "Municipal flood reference layer is not installed."}), 404
    return jsonify(json.loads(FLOOD_REFERENCE_PATH.read_text(encoding="utf-8")))


@app.get("/api/weather")
def weather():
    try:
        return jsonify(forecast_summary(get_forecast(force_refresh=request.args.get("refresh") == "1")))
    except WeatherUnavailable as exc:
        return jsonify({"error": str(exc)}), 503


@app.get("/api/route")
def route():
    try:
        origin = tuple(map(float, request.args["from"].split(",")))
        destination = tuple(map(float, request.args["to"].split(",")))
        if len(origin) != 2 or len(destination) != 2:
            raise ValueError("Coordinates must be lat,lon pairs.")
        mode = request.args.get("mode", "simulation")
        if mode == "forecast":
            route_state = _forecast_state()
        else:
            scenario = request.args.get("scenario", "normal")
            route_state = current_state(scenario)
        result = compare_routes(origin, destination, route_state)
        result["conditions"] = route_state
        return jsonify(result)
    except KeyError:
        return jsonify({"error": "Provide from=lat,lon and to=lat,lon."}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except WeatherUnavailable:
        return jsonify({"error": "Live forecast unavailable. Try a simulation scenario."}), 503
    except Exception:
        app.logger.exception("Routing failed")
        return jsonify({"error": "Route unavailable. Try two other points."}), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
