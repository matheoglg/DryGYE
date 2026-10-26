"""Download the public municipal flood-prone polygon layer for the pilot area."""
import json
from pathlib import Path

import requests

from drygye.config import FLOOD_REFERENCE_PATH, PILOT_BBOX

SERVICE = "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Zonas_Inundables_GYE/FeatureServer/0/query"


def main():
    south, west, north, east = PILOT_BBOX
    params = {
        "where": "1=1", "geometry": f"{west},{south},{east},{north}",
        "geometryType": "esriGeometryEnvelope", "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects", "outFields": "FID,Descrip,Área_ha",
        "outSR": 4326, "returnGeometry": "true", "f": "geojson",
    }
    response = requests.get(SERVICE, params=params, timeout=45)
    response.raise_for_status()
    data = response.json()
    if data.get("type") != "FeatureCollection" or not data.get("features"):
        raise RuntimeError(f"No flood-zone features returned: {data}")
    if len(data["features"]) >= 2000:
        raise RuntimeError("Response reached the service record limit; use object-ID batching before accepting it.")
    FLOOD_REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FLOOD_REFERENCE_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    meta = {
        "title": "Zonas_Inundables_GYE", "owner": "darviljg_MIMG",
        "service": "https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Zonas_Inundables_GYE/FeatureServer",
        "description": "Flood-prone zones compiled from municipal, utility, study, and historical-event sources.",
        "source_updated": "2025-10-29", "retrieved_features": len(data["features"]),
        "license_note": "Public ArcGIS feature service; confirm attribution and reuse terms before publication.",
    }
    meta_path = FLOOD_REFERENCE_PATH.with_name("flood_reference_metadata.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Saved {len(data['features'])} features to {FLOOD_REFERENCE_PATH}")


if __name__ == "__main__":
    main()
