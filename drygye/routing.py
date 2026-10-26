"""OSM route comparison with a DEM-based relative-risk edge cost."""
import networkx as nx
import osmnx as ox
from pyproj import Geod

from drygye.config import CITY_CENTER, GRAPH_PATH, RISK_BLOCK, RISK_COST_WEIGHT
from drygye.terrain import risk_at
from drygye.roads import build_pilot_graph, save_pilot_graph

GEOD = Geod(ellps="WGS84")
MAX_SNAP_M = 350


def _load_graph(origin, destination):
    if GRAPH_PATH.exists():
        graph = nx.read_graphml(GRAPH_PATH, node_type=str)
        for _, data in graph.nodes(data=True):
            data["x"], data["y"] = float(data["x"]), float(data["y"])
        for _, _, _, data in graph.edges(keys=True, data=True):
            for key in ("length", "risk_base", "risk_dyn", "risk_cost"):
                if key in data:
                    data[key] = float(data[key])
        return graph
    from drygye.config import ROAD_SOURCE_PATH
    if ROAD_SOURCE_PATH.exists():
        graph = build_pilot_graph()
        save_pilot_graph(graph)
        return graph
    lats = [origin[0], destination[0], CITY_CENTER[0]]
    lons = [origin[1], destination[1], CITY_CENTER[1]]
    pad = 0.018
    # OSMnx 2 expects (west, south, east, north), all in EPSG:4326.
    bbox = (min(lons) - pad, min(lats) - pad, max(lons) + pad, max(lats) + pad)
    graph = ox.graph_from_bbox(bbox, network_type="drive", simplify=True)
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, GRAPH_PATH)
    return graph


def compare_routes(origin, destination, state):
    graph = _load_graph(origin, destination)
    graph, source, target, snapped = _snap_to_connected_component(graph, origin, destination)
    factor = state["factor"]
    for u, v, key, data in graph.edges(keys=True, data=True):
        lat = (graph.nodes[u]["y"] + graph.nodes[v]["y"]) / 2
        lon = (graph.nodes[u]["x"] + graph.nodes[v]["x"]) / 2
        base = risk_at(lat, lon)
        dyn = min(1.0, base * factor)
        data["risk_base"] = base
        data["risk_dyn"] = dyn
        data["risk_cost"] = float(data.get("length", 1)) * (1 + RISK_COST_WEIGHT * dyn)
    fast_nodes = nx.shortest_path(graph, source, target, weight="length")
    safe_nodes = nx.shortest_path(graph, source, target, weight="risk_cost")
    safe_graph = graph
    safe_fallback = False
    if state["level"] == "red":
        blocked = graph.copy()
        blocked.remove_edges_from([(u, v, k) for u, v, k, d in blocked.edges(keys=True, data=True) if d["risk_dyn"] >= RISK_BLOCK])
        try:
            safe_nodes = nx.shortest_path(blocked, source, target, weight="risk_cost")
            safe_graph = blocked
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            safe_fallback = True
    return {"fast": _route_summary(graph, fast_nodes, "length"),
            "safe": _route_summary(safe_graph, safe_nodes, "risk_cost"), "snapping": snapped,
            "warning": "No route avoids every very-high-risk edge; the lower-cost route still includes a high-risk segment." if safe_fallback else None}


def _route_summary(graph, nodes, weight="length"):
    coords, length, risks = [], 0.0, []
    for node in nodes:
        coords.append([graph.nodes[node]["y"], graph.nodes[node]["x"]])
    for u, v in zip(nodes, nodes[1:]):
        data = min(graph.get_edge_data(u, v).values(), key=lambda edge: edge.get(weight, edge.get("length", 1)))
        length += float(data.get("length", 0))
        risks.append(float(data.get("risk_dyn", 0)))
    return {"coords": coords, "length_m": round(length), "time_min": round(length / 8.33 / 60, 1),
            "mean_risk": round(sum(risks) / len(risks), 3) if risks else 0,
            "max_risk": round(max(risks), 3) if risks else 0}


def _snap_to_connected_component(graph, origin, destination):
    """Snap both points to one connected component and disclose snap distance."""
    candidates = sorted(nx.weakly_connected_components(graph), key=len, reverse=True)
    best = None
    for component in candidates:
        if len(component) < 2:
            continue
        source = _nearest_node(graph, *origin, candidates=component)
        target = _nearest_node(graph, *destination, candidates=component)
        d1 = _distance_m(graph, source, origin)
        d2 = _distance_m(graph, target, destination)
        candidate = (d1 + d2, -len(component), component, source, target, d1, d2)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        raise nx.NetworkXNoPath("The pilot road graph has no connected route network.")
    _, _, component, source, target, d1, d2 = best
    if max(d1, d2) > MAX_SNAP_M:
        raise ValueError(f"A selected point is more than {MAX_SNAP_M} m from the connected pilot road network.")
    connected = graph.subgraph(component).copy()
    return connected, source, target, {"origin_m": round(d1), "destination_m": round(d2)}


def _nearest_node(graph, lat, lon, candidates=None):
    """Snap to the closest graph vertex without optional spatial-index packages."""
    nodes = graph.nodes if candidates is None else candidates
    return min(nodes, key=lambda node: (float(graph.nodes[node]["y"]) - lat) ** 2 + (float(graph.nodes[node]["x"]) - lon) ** 2)


def _distance_m(graph, node, point):
    lon, lat = float(graph.nodes[node]["x"]), float(graph.nodes[node]["y"])
    return abs(GEOD.inv(lon, lat, point[1], point[0])[2])
