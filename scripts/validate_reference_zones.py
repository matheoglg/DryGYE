"""Compare terrain-risk values inside/outside flood-prone reference polygons.

This is a spatial sanity check against a different public layer, not a model
accuracy score or an independent ground-truth validation.
"""
import json

import numpy as np
import rasterio
import shapely
from shapely.geometry import shape
from shapely.ops import unary_union

from drygye.config import FLOOD_REFERENCE_PATH, HIGH_RISK, RISK_PATH


def main():
    collection = json.loads(FLOOD_REFERENCE_PATH.read_text(encoding="utf-8"))
    zones = unary_union([shape(feature["geometry"]) for feature in collection["features"]])
    with rasterio.open(RISK_PATH) as src:
        risk = src.read(1)
        rows, cols = np.mgrid[0:risk.shape[0]:10, 0:risk.shape[1]:10]
        values = risk[rows, cols]
        xs, ys = rasterio.transform.xy(src.transform, rows.ravel(), cols.ravel(), offset="center")
    values = values.ravel()
    x, y = np.asarray(xs), np.asarray(ys)
    valid = np.isfinite(values)
    in_zone = np.zeros(values.shape, dtype=bool)
    in_zone[valid] = shapely.contains(zones, shapely.points(x[valid], y[valid]))
    inside, outside = values[valid & in_zone], values[valid & ~in_zone]
    if not inside.size or not outside.size:
        raise RuntimeError("Not enough valid raster cells inside and outside the reference layer.")
    print("SANITY CHECK ONLY — not predictive accuracy or independent validation")
    for name, sample in (("inside_flood_reference", inside), ("outside_flood_reference", outside)):
        print(f"{name}: n={sample.size}, mean={sample.mean():.3f}, median={np.median(sample):.3f}, share>={HIGH_RISK}={np.mean(sample >= HIGH_RISK):.1%}")


if __name__ == "__main__":
    main()
