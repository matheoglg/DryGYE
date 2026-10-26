"""Drivable street graph for the pilot area, built once from OpenStreetMap and stored on disk.

Overpass (the usual OSMnx source) is often unreachable, so the raw data comes from the
main OSM API in small tiles. Only drivable streets are kept, then OSMnx builds the graph.
"""
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import osmnx as ox
import requests

from drygye.config import GRAPH_PATH, PILOT_BBOX
from drygye.terrain import risk_at

OSM_API_MAP = "https://api.openstreetmap.org/api/0.6/map"
TILE_DEG = 0.02
DRIVE_HIGHWAYS = {
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
    "secondary", "secondary_link", "tertiary", "tertiary_link",
    "unclassified", "residential", "living_street",
}


def build_graph(bbox=PILOT_BBOX):
    """Download drivable OSM streets inside bbox and attach terrain risk to every edge.

    Only the largest strongly connected component is kept, so any two snapped
    points always have a route between them (no dead-end islands).
    """
    south, west, north, east = bbox
    with tempfile.TemporaryDirectory() as tmp:
        xml_path = Path(tmp) / "drive.osm"
        _download_drive_xml(bbox, xml_path)
        graph = ox.graph_from_xml(xml_path, simplify=True)
    graph = ox.truncate.truncate_graph_bbox(graph, (west, south, east, north))
    graph = ox.truncate.largest_component(graph, strongly=True)
    for u, v, data in graph.edges(data=True):
        data["risk_base"] = _edge_risk(graph, u, v, data)
    return graph


def save_graph(graph, path=GRAPH_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, path)


@lru_cache(maxsize=1)
def load_graph():
    """Load the stored graph (built and saved on first use if missing). Cached in memory."""
    if not GRAPH_PATH.exists():
        save_graph(build_graph())
    return ox.load_graphml(GRAPH_PATH, edge_dtypes={"risk_base": float})


def edge_coords(graph, u, v, data):
    """Street shape of an edge as [[lat, lon], ...] from u to v."""
    if "geometry" in data:
        return [[lat, lon] for lon, lat in data["geometry"].coords]
    return [[graph.nodes[u]["y"], graph.nodes[u]["x"]], [graph.nodes[v]["y"], graph.nodes[v]["x"]]]


def _edge_risk(graph, u, v, data):
    """Mean terrain risk sampled along the street shape."""
    points = edge_coords(graph, u, v, data)
    return sum(risk_at(lat, lon) for lat, lon in points) / len(points)


def _download_drive_xml(bbox, out_path):
    """Merge OSM API tiles into one .osm file holding only drivable ways and their nodes."""
    south, west, north, east = bbox
    nodes, ways = {}, {}
    lat = south
    while lat < north:
        lon = west
        while lon < east:
            tile = (lat, lon, min(lat + TILE_DEG, north), min(lon + TILE_DEG, east))
            for element in _fetch_tile(tile):
                if element.tag == "node":
                    nodes[element.get("id")] = element
                elif element.tag == "way" and _is_drivable(element):
                    ways[element.get("id")] = element
            lon += TILE_DEG
        lat += TILE_DEG
    used = {nd.get("ref") for way in ways.values() for nd in way.iter("nd")}
    root = ET.Element("osm", version="0.6")
    root.extend(nodes[ref] for ref in used if ref in nodes)
    root.extend(ways.values())
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)


def _fetch_tile(tile):
    """Elements of one tile; splits the tile in four if the API says it holds too many nodes."""
    south, west, north, east = tile
    response = requests.get(OSM_API_MAP, params={"bbox": f"{west},{south},{east},{north}"},
                            headers={"User-Agent": "DryGYE hackathon prototype"}, timeout=120)
    if response.status_code == 400:
        mid_lat, mid_lon = (south + north) / 2, (west + east) / 2
        quarters = [(south, west, mid_lat, mid_lon), (south, mid_lon, mid_lat, east),
                    (mid_lat, west, north, mid_lon), (mid_lat, mid_lon, north, east)]
        return [element for quarter in quarters for element in _fetch_tile(quarter)]
    response.raise_for_status()
    return list(ET.fromstring(response.content))


def _is_drivable(way):
    tags = {tag.get("k"): tag.get("v") for tag in way.iter("tag")}
    return (tags.get("highway") in DRIVE_HIGHWAYS
            and tags.get("access") not in {"private", "no"}
            and tags.get("area") != "yes")
