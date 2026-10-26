"""Shared constants for DryGYE. Constants only, no logic.

Coordinates are always (lat, lon) in EPSG:4326. Times use America/Guayaquil.
Change this file only after telling the team (CLAUDE.md, section 15).
"""
from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = ROOT / "cache"

DEM_PATH = RAW_DIR / "dem_guayaquil_glo30.tif"
TIDE_PDF_PATH = RAW_DIR / "GUAYAQUIL_RIO_4.pdf"
VALIDATION_POINTS_PATH = RAW_DIR / "validation_points.csv"

RISK_PATH = PROCESSED_DIR / "risk.tif"
TIDES_CSV_PATH = PROCESSED_DIR / "tides.csv"
GRAPH_PATH = PROCESSED_DIR / "road_graph.graphml"
REPORTS_PATH = DATA_DIR / "reports.json"
FLOOD_REFERENCE_PATH = PROCESSED_DIR / "flood_reference.geojson"
ROAD_SOURCE_PATH = RAW_DIR / "municipal_roads_pilot.geojson"

# --- Area ---
# DEM bounds: (south, west, north, east) = (lat_min, lon_min, lat_max, lon_max)
BBOX = (-2.400, -80.150, -1.950, -79.800)
# Covered area: Guasmo / Isla Trinitaria (south) to Samanes / Sauces (north), west to Monte Sinai.
PILOT_BBOX = (-2.290, -80.020, -2.070, -79.860)
CITY_CENTER = (-2.19, -79.89)
TIMEZONE = "America/Guayaquil"

# --- Terrain risk (section 11). Heuristic weights, tuned against validation points ---
WATER_MAX_ELEV_M = 0.0          # DEM pixels <= this are treated as water
HAND_SCALE_M = 10.0             # height above nearest water that maps to zero risk
WATER_DIST_SCALE_M = 1000.0     # distance to water that maps to zero risk
SLOPE_SCALE_DEG = 5.0           # slope that maps to zero risk
RISK_WEIGHTS = {"hand": 0.5, "water_dist": 0.3, "slope": 0.2}
HIGH_RISK = 0.6                 # risk >= this counts as "high" in validation

# --- Rain alerts (INAMHI thresholds for the Litoral, mm per 24 h) ---
RAIN_YELLOW_MM_24H = 19.0
RAIN_RED_MM_24H = 42.0
# Level goes up one step if a high tide coincides with this much rain in 3 h
RAIN_TIDE_BUMP_MM_3H = 10.0

# --- Tide (INOCAR, metres above INOCAR reference level) ---
TIDE_HIGH_M = 4.0
TIDE_PEAK_MIN_M = 2.0           # tide events above this are high water (pleamar)

# --- Dynamic factor: f = clip(BASE + rain_24h/RAIN_RED + TIDE_W*high_tide, MIN, MAX) ---
FACTOR_BASE = 0.5
FACTOR_TIDE_WEIGHT = 0.3
FACTOR_MIN = 0.5
FACTOR_MAX = 2.0

# --- Routing ---
RISK_COST_WEIGHT = 10.0         # edge cost = length * (1 + RISK_COST_WEIGHT * risk_dyn)
RISK_BLOCK = 0.85               # edges at or above this are avoided on red level
REPORT_RISK_BONUS = 0.5         # risk added to edges near an active citizen report
REPORT_RADIUS_M = 150.0
REPORT_TTL_HOURS = 3
DEFAULT_SPEED_KMH = 30.0        # used to estimate travel time

# --- Weather (Open-Meteo, free tier: non-commercial use only) ---
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_HOURS = 48
WEATHER_CACHE_MAX_AGE_MIN = 60

# --- Simulation ---
SIM_SENSOR_COUNT = 10
SCENARIO_NAMES = ["Normal", "Heavy rain", "Heavy rain + high tide"]

# --- Attributions shown in the UI ---
ATTRIBUTIONS = [
    'Weather data by <a href="https://open-meteo.com/">Open-Meteo.com</a>',
    "&copy; OpenStreetMap contributors",
    "Copernicus DEM GLO-30 &copy; DLR e.V. 2010-2014 and &copy; Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA",
    "Tide predictions: INOCAR",
]
