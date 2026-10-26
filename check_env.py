"""DryGYE environment check.

Run it inside the project environment:

    python check_env.py                # imports + offline smoke tests
    python check_env.py --net          # also tests Open-Meteo and OpenStreetMap access
    python check_env.py --dem PATH     # also prints basic info about a GeoTIFF DEM

Exit code is 1 if a core package or smoke test fails, 0 otherwise.
Network problems and missing optional packages are reported as warnings only.
Output is plain ASCII on purpose, so it prints correctly in any Windows console.
"""
import argparse
import importlib
import json
import sys
import tempfile
import urllib.request
from importlib import metadata

FAILED = []
WARNED = []

# import name -> distribution name (only where they differ)
DIST_NAMES = {
    "dotenv": "python-dotenv",
    "yaml": "PyYAML",
    "telegram": "python-telegram-bot",
}

CORE = [
    "numpy", "pandas", "scipy", "networkx", "shapely", "pyproj", "geopandas",
    "rasterio", "osmnx", "pysheds", "matplotlib", "folium", "requests", "pdfplumber",
    "flask", "dotenv", "yaml", "pytest", "ipykernel",
]
OPTIONAL = [("telegram", "python-telegram-bot (deferred, installed with -WithTelegram)")]


def ok(msg):
    print("[OK]   " + msg)


def warn(msg):
    WARNED.append(msg)
    print("[WARN] " + msg)


def fail(msg):
    FAILED.append(msg)
    print("[FAIL] " + msg)


def version_of(import_name, module):
    dist = DIST_NAMES.get(import_name, import_name)
    try:
        return metadata.version(dist)
    except Exception:
        return getattr(module, "__version__", "?")


def check_imports():
    print("\n-- Imports")
    for name in CORE:
        try:
            module = importlib.import_module(name)
            ok("%-12s %s" % (name, version_of(name, module)))
        except Exception as exc:
            fail("%s could not be imported: %s: %s" % (name, type(exc).__name__, exc))
    for name, label in OPTIONAL:
        try:
            module = importlib.import_module(name)
            ok("%-12s %s" % (name, version_of(name, module)))
        except Exception:
            warn("%s is not installed" % label)


def smoke(label, func):
    try:
        detail = func()
        ok("%s%s" % (label, " (%s)" % detail if detail else ""))
    except Exception as exc:
        fail("%s: %s: %s" % (label, type(exc).__name__, exc))


def smoke_tests():
    print("\n-- Offline smoke tests")

    def geo_projection():
        import geopandas as gpd
        from shapely.geometry import Point

        gdf = gpd.GeoDataFrame(geometry=[Point(-79.8891, -2.1894)], crs="EPSG:4326")
        point = gdf.to_crs("EPSG:32717").geometry.iloc[0]  # UTM 17S, Guayaquil
        area = point.buffer(100).area
        assert 600000 < point.x < 650000 and 9740000 < point.y < 9780000, (point.x, point.y)
        assert 30000 < area < 32000, area
        return "Guayaquil -> UTM 17S x=%.0f y=%.0f" % (point.x, point.y)

    def raster_roundtrip():
        import numpy as np
        from rasterio.io import MemoryFile
        from rasterio.transform import from_origin

        data = np.arange(16, dtype="float32").reshape(4, 4)
        profile = dict(driver="GTiff", height=4, width=4, count=1, dtype="float32",
                       crs="EPSG:4326", transform=from_origin(-80.0, -2.0, 0.001, 0.001))
        with MemoryFile() as mem:
            with mem.open(**profile) as dst:
                dst.write(data, 1)
            with mem.open() as src:
                back = src.read(1)
        assert np.array_equal(data, back)

    def graph_routing():
        import networkx as nx

        g = nx.Graph()
        g.add_weighted_edges_from([("a", "b", 1), ("b", "c", 1), ("a", "c", 5)])
        assert nx.shortest_path(g, "a", "c", weight="weight") == ["a", "b", "c"]

    def distance_transform():
        import numpy as np
        from scipy import ndimage

        mask = np.ones((3, 3))
        mask[0, 0] = 0
        dist = ndimage.distance_transform_edt(mask)
        assert abs(dist[2, 2] - 8 ** 0.5) < 1e-6

    def pysheds_import():
        from pysheds.grid import Grid  # noqa: F401

    def flask_app():
        from flask import Flask

        app = Flask(__name__)

        @app.route("/ping")
        def ping():
            return "pong"

        response = app.test_client().get("/ping")
        assert response.status_code == 200 and response.data == b"pong"

    def osmnx_settings():
        import osmnx as ox

        assert hasattr(ox, "graph_from_point") and hasattr(ox, "routing")

    smoke("pyproj + geopandas + shapely", geo_projection)
    smoke("rasterio in-memory GeoTIFF round trip", raster_roundtrip)
    smoke("networkx shortest path", graph_routing)
    smoke("scipy distance transform", distance_transform)
    smoke("pysheds Grid import", pysheds_import)
    smoke("flask test client", flask_app)
    smoke("osmnx 2.x API present", osmnx_settings)


def net_tests():
    print("\n-- Network tests (failures here are warnings, not errors)")
    url = ("https://api.open-meteo.com/v1/forecast?latitude=-2.19&longitude=-79.89"
           "&hourly=precipitation&forecast_days=1&timezone=America%2FGuayaquil")
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        ok("Open-Meteo forecast reachable (%d hourly values)" % len(data["hourly"]["time"]))
    except Exception as exc:
        warn("Open-Meteo not reachable: %s: %s" % (type(exc).__name__, exc))
    try:
        import osmnx as ox

        ox.settings.use_cache = False
        ox.settings.cache_folder = tempfile.mkdtemp()
        ox.settings.requests_timeout = 60
        graph = ox.graph_from_point((-2.1894, -79.8891), dist=300, network_type="drive")
        ok("OpenStreetMap via osmnx reachable (%d nodes, %d edges near the Malecon)"
           % (graph.number_of_nodes(), graph.number_of_edges()))
    except Exception as exc:
        warn("OpenStreetMap/Overpass not reachable: %s: %s" % (type(exc).__name__, exc))


def dem_info(path):
    print("\n-- DEM: %s" % path)
    try:
        import numpy as np
        import rasterio

        with rasterio.open(path) as src:
            data = src.read(1, masked=True)
            print("       driver=%s  crs=%s  shape(rows,cols)=%s  res=%s" % (src.driver, src.crs, src.shape, src.res))
            print("       bounds=%s" % (tuple(round(v, 4) for v in src.bounds),))
            print("       min=%.2f  max=%.2f  mean=%.2f  zeros=%.1f%%" % (
                float(data.min()), float(data.max()), float(data.mean()),
                100.0 * float(np.count_nonzero(data.filled(np.nan) == 0)) / data.size))
            if src.crs is None:
                warn("The DEM has no CRS defined")
        ok("DEM opens correctly")
    except Exception as exc:
        fail("DEM could not be read: %s: %s" % (type(exc).__name__, exc))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="DryGYE environment check")
    parser.add_argument("--net", action="store_true", help="also test Open-Meteo and OpenStreetMap access")
    parser.add_argument("--dem", metavar="PATH", help="print basic info about a GeoTIFF DEM")
    args = parser.parse_args()

    print("DryGYE environment check")
    print("Python %s at %s" % (sys.version.split()[0], sys.executable))
    check_imports()
    if not FAILED:
        smoke_tests()
    if args.net:
        net_tests()
    if args.dem:
        dem_info(args.dem)

    print("\n== Result: %d failed, %d warnings" % (len(FAILED), len(WARNED)))
    if FAILED:
        print("Fix the [FAIL] lines above, or re-run setup_env with -Recreate.")
        return 1
    print("Environment is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
