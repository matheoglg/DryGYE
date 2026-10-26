"""Fetch public municipal road and flood-reference layers for the demo area."""
import json

import requests

from drygye.config import FLOOD_REFERENCE_PATH, PILOT_BBOX, PROCESSED_DIR, RAW_DIR, ROAD_SOURCE_PATH

FLOOD_SERVICE = "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Zonas_Inundables_GYE/FeatureServer/0/query"
ROAD_SERVICE = "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Estructura_vial_%C3%A1rea_urbana/FeatureServer/0/query"


def fetch(service, out_path):
    south, west, north, east = PILOT_BBOX
    params = {"where": "1=1", "geometry": f"{west},{south},{east},{north}",
              "geometryType": "esriGeometryEnvelope", "inSR": 4326,
              "spatialRel": "esriSpatialRelIntersects", "outFields": "*",
              "outSR": 4326, "returnGeometry": "true", "f": "geojson"}
    response = requests.get(service, params=params, timeout=45)
    response.raise_for_status()
    data = response.json()
    if data.get("type") != "FeatureCollection" or not data.get("features"):
        raise RuntimeError(f"Empty or invalid feature service response from {service}")
    if len(data["features"]) >= 2000:
        raise RuntimeError("Service record limit reached; do not accept a truncated layer.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(data['features'])} features to {out_path}")
    return len(data["features"])


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    roads = fetch(ROAD_SERVICE, ROAD_SOURCE_PATH)
    zones = fetch(FLOOD_SERVICE, FLOOD_REFERENCE_PATH)
    metadata = {
        "publisher": "Municipio de Guayaquil / MIMG ArcGIS public feature services",
        "roads_service": "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Estructura_vial_%C3%A1rea_urbana/FeatureServer",
        "flood_reference_service": "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Zonas_Inundables_GYE/FeatureServer",
        "roads_features": roads, "flood_zone_features": zones,
        "pilot_bbox_south_west_north_east": list(PILOT_BBOX),
        "note": "Flood polygons are a municipal reference layer compiled from studies and historical events; they are not current street closures or ground-truth measurements.",
        "reuse": "Public ArcGIS feature services; retain attribution and confirm applicable reuse terms.",
    }
    (PROCESSED_DIR / "municipal_reference_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
