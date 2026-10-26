"""Relative flood-risk surface derived from the supplied Copernicus DEM."""
from functools import lru_cache

import numpy as np
import rasterio
from scipy import ndimage

from drygye.config import DEM_PATH, RISK_PATH, RISK_WEIGHTS


@lru_cache(maxsize=1)
def _load_risk():
    """Load a prepared risk raster, or calculate the heuristic from the DEM."""
    path = RISK_PATH if RISK_PATH.exists() else DEM_PATH
    with rasterio.open(path) as src:
        elev = src.read(1, masked=True).filled(np.nan).astype("float32")
        profile = src.profile.copy()
        transform = src.transform
        bounds = src.bounds
        crs = src.crs
    if path == RISK_PATH:
        risk = elev
    else:
        water = np.isfinite(elev) & (elev <= 0.0)
        valid = np.isfinite(elev)
        if not water.any():
            raise ValueError("DEM has no pixels at or below sea level to use as water.")
        lat_scale = abs(transform.e) * 111_320.0
        lon_scale = abs(transform.a) * 111_320.0 * np.cos(np.deg2rad((bounds.bottom + bounds.top) / 2))
        dist_px, nearest = ndimage.distance_transform_edt(~water, sampling=(lat_scale, lon_scale), return_indices=True)
        hand = np.maximum(elev - elev[nearest[0], nearest[1]], 0.0)
        gy, gx = np.gradient(np.nan_to_num(elev, nan=0.0), lat_scale, lon_scale)
        slope = np.degrees(np.arctan(np.hypot(gx, gy)))
        hand_risk = np.clip(1.0 - hand / 10.0, 0, 1)
        water_risk = np.clip(1.0 - dist_px / 1000.0, 0, 1)
        slope_risk = np.clip(1.0 - slope / 5.0, 0, 1)
        risk = (RISK_WEIGHTS["hand"] * hand_risk + RISK_WEIGHTS["water_dist"] * water_risk + RISK_WEIGHTS["slope"] * slope_risk).astype("float32")
        risk[~valid | water] = np.nan
        profile.update(dtype="float32", count=1, nodata=np.nan, compress="deflate")
        RISK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(RISK_PATH, "w", **profile) as dst:
            dst.write(risk, 1)
    return risk, transform, bounds, crs


def risk_at(lat, lon):
    risk, transform, _, _ = _load_risk()
    row, col = rasterio.transform.rowcol(transform, lon, lat)
    if row < 0 or col < 0 or row >= risk.shape[0] or col >= risk.shape[1]:
        return 0.0
    value = risk[row, col]
    return float(value) if np.isfinite(value) else 0.0


def risk_geojson(max_side=65):
    """Return a coarse grid for the web map, keeping the payload lightweight."""
    risk, transform, _, _ = _load_risk()
    step = max(1, int(np.ceil(max(risk.shape) / max_side)))
    features = []
    for row in range(0, risk.shape[0], step):
        for col in range(0, risk.shape[1], step):
            block = risk[row:row + step, col:col + step]
            values = block[np.isfinite(block)]
            if not values.size:
                continue
            r2, c2 = min(row + step, risk.shape[0]), min(col + step, risk.shape[1])
            x1, y1 = rasterio.transform.xy(transform, row, col, offset="ul")
            x2, y2 = rasterio.transform.xy(transform, r2 - 1, c2 - 1, offset="lr")
            features.append({"type": "Feature", "properties": {"risk": round(float(values.mean()), 3)},
                             "geometry": {"type": "Polygon", "coordinates": [[[x1,y1],[x2,y1],[x2,y2],[x1,y2],[x1,y1]]]}})
    return {"type": "FeatureCollection", "features": features}
