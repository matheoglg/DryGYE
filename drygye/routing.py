"""OSM route comparison with a DEM-based relative-risk edge cost."""
import os

import networkx as nx
import osmnx as ox

from drygye.config import CITY_CENTER, GRAPH_PATH, RISK_BLOCK, RISK_COST_WEIGHT
from drygye.terrain import risk_at


def _load_graph(origin, destination):
    if GRAPH_PATH.exists():
        return ox.load_graphml(GRAPH_PATH)
    lats = [origin[0], destination[0], CITY_CENTER[0]]
    lons = [origin[1], destination[1], CITY_CENTER[1]]
    pad = 0.018
    graph = ox.graph_from_bbox((max(lats) + pad, min(lats) - pad, max(lons) + pad, min(lons) - pad), network_type="drive", simplify=True)
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, GRAPH_PATH)
    return graph


def compare_routes(origin, destination, state):
    graph = _load_graph(origin, destination)
    factor = state["factor"]
    for u, v, key, data in graph.edges(keys=True, data=True):
        lat = (graph.nodes[u]["y"] + graph.nodes[v]["y"]) / 2
        lon = (graph.nodes[u]["x"] + graph.nodes[v]["x"]) / 2
        base = risk_at(lat, lon)
        dyn = min(1.0, base * factor)
        data["risk_base"] = base
        data["risk_dyn"] = dyn
        data["risk_cost"] = float(data.get("length", 1)) * (1 + RISK_COST_WEIGHT * dyn)
    source = ox.distance.nearest_nodes(graph, X=origin[1], Y=origin[0])
    target = ox.distance.nearest_nodes(graph, X=destination[1], Y=destination[0])
    fast_nodes = nx.shortest_path(graph, source, target, weight="length")
    safe_nodes = nx.shortest_path(graph, source, target, weight="risk_cost")
    if state["level"] == "red":
        blocked = graph.copy()
        blocked.remove_edges_from([(u, v, k) for u, v, k, d in blocked.edges(keys=True, data=True) if d["risk_dyn"] >= RISK_BLOCK])
        try:
            safe_nodes = nx.shortest_path(blocked, source, target, weight="risk_cost")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            pass
    return {"fast": _route_summary(graph, fast_nodes), "safe": _route_summary(graph, safe_nodes)}


def _route_summary(graph, nodes):
    coords, length, risks = [], 0.0, []
    for node in nodes:
        coords.append([graph.nodes[node]["y"], graph.nodes[node]["x"]])
    for u, v in zip(nodes, nodes[1:]):
        data = min(graph.get_edge_data(u, v).values(), key=lambda edge: edge.get("risk_cost", edge.get("length", 1)))
        length += float(data.get("length", 0))
        risks.append(float(data.get("risk_dyn", 0)))
    return {"coords": coords, "length_m": round(length), "time_min": round(length / 8.33 / 60, 1),
            "mean_risk": round(sum(risks) / len(risks), 3) if risks else 0,
            "max_risk": round(max(risks), 3) if risks else 0}
