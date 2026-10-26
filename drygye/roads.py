"""Build and persist a small routable graph from the municipal pilot road layer."""
import json

import networkx as nx
from pyproj import Geod
from shapely.geometry import LineString, MultiLineString, box, shape
from shapely.ops import unary_union

from drygye.config import GRAPH_PATH, PILOT_BBOX, ROAD_SOURCE_PATH
from drygye.terrain import risk_at

GEOD = Geod(ellps="WGS84")


def build_pilot_graph(source_path=ROAD_SOURCE_PATH):
    """Node municipal road centerlines at intersections and create both directions.

    The source has no one-way attribute, so both directions are assumed. This is
    suitable for a prototype network comparison, not turn-by-turn navigation.
    """
    collection = json.loads(source_path.read_text(encoding="utf-8"))
    south, west, north, east = PILOT_BBOX
    clip = box(west, south, east, north)
    lines = []
    for feature in collection["features"]:
        geom = shape(feature["geometry"]).intersection(clip)
        if isinstance(geom, LineString) and geom.length:
            lines.append(geom)
        elif isinstance(geom, MultiLineString):
            lines.extend(line for line in geom.geoms if line.length)
    noded = unary_union(lines)
    segments = []
    stack = [noded]
    while stack:
        geom = stack.pop()
        if isinstance(geom, LineString):
            segments.extend(zip(list(geom.coords), list(geom.coords)[1:]))
        elif hasattr(geom, "geoms"):
            stack.extend(geom.geoms)

    graph = nx.MultiDiGraph(crs="EPSG:4326", source="Municipio de Guayaquil Estructura Vial área urbana")
    for first, second in segments:
        lon1, lat1 = first[:2]
        lon2, lat2 = second[:2]
        if (lon1, lat1) == (lon2, lat2):
            continue
        u, v = _node_id(lon1, lat1), _node_id(lon2, lat2)
        graph.add_node(u, x=float(lon1), y=float(lat1))
        graph.add_node(v, x=float(lon2), y=float(lat2))
        _, _, length = GEOD.inv(lon1, lat1, lon2, lat2)
        midpoint = ((lat1 + lat2) / 2, (lon1 + lon2) / 2)
        base = risk_at(*midpoint)
        attrs = {"length": float(length), "risk_base": base, "risk_dyn": base, "risk_cost": float(length) * (1 + 10 * base)}
        graph.add_edge(u, v, **attrs)
        graph.add_edge(v, u, **attrs)
    if graph.number_of_nodes() == 0:
        raise ValueError("Municipal road layer produced an empty pilot graph.")
    return graph


def save_pilot_graph(graph, path=GRAPH_PATH):
    import osmnx as ox
    path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, path)


def _node_id(lon, lat):
    return f"{lon:.6f},{lat:.6f}"
