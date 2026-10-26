"""Fastest vs lower-risk route comparison over the pilot street graph, plus alternatives."""
from functools import lru_cache

import networkx as nx
import numpy as np
from pyproj import Geod

from drygye.config import DEFAULT_SPEED_KMH, PILOT_BBOX, RISK_BLOCK, RISK_COST_WEIGHT
from drygye.roads import edge_coords, load_graph

GEOD = Geod(ellps="WGS84")
MAX_SNAP_M = 350
MAX_ALTERNATIVES = 2
ALT_PENALTY = 1.6        # cost multiplier on streets already used by a found route
ALT_MAX_OVERLAP = 0.7    # an alternative may share at most this share of its length with another route


def compare_routes(origin, destination, state):
    """Return the fastest route, the lower-estimated-risk route and a few alternatives."""
    graph = load_graph()
    source, d1 = _snap(graph, origin, "start")
    target, d2 = _snap(graph, destination, "end")

    factor = state["factor"]

    def risk_dyn(data):
        return min(1.0, data["risk_base"] * factor)

    def risk_cost(data):
        return data["length"] * (1 + RISK_COST_WEIGHT * risk_dyn(data))

    def weight(cost):
        return lambda u, v, edges: min(cost(d) for d in edges.values())

    fast_nodes = nx.shortest_path(graph, source, target, weight="length")
    safe_nodes = nx.shortest_path(graph, source, target, weight=weight(risk_cost))
    warning = None
    if state["level"] == "red":
        # On red alert, very-high-risk streets are skipped when an alternative exists.
        open_streets = nx.subgraph_view(graph, filter_edge=lambda u, v, k: risk_dyn(graph[u][v][k]) < RISK_BLOCK)
        try:
            safe_nodes = nx.shortest_path(open_streets, source, target, weight=weight(risk_cost))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            warning = "No alternative avoids every very-high-risk street."

    alt_paths = _alternative_paths(graph, source, target, [safe_nodes, fast_nodes], risk_cost)

    def summary(nodes, cost):
        return _summary(graph, nodes, origin, destination, risk_dyn, cost)

    return {"fast": summary(fast_nodes, lambda d: d["length"]),
            "safe": summary(safe_nodes, risk_cost),
            "alternatives": [summary(nodes, risk_cost) for nodes in alt_paths],
            "snapping": {"origin_m": round(d1), "destination_m": round(d2)},
            "warning": warning}


def _alternative_paths(graph, source, target, found, cost):
    """Penalty method: make streets of found routes more expensive and search again."""
    penalty = {}
    for path in found:
        for edge in zip(path, path[1:]):
            penalty[edge] = penalty.get(edge, 1.0) * ALT_PENALTY

    def penalized(u, v, edges):
        return min(cost(d) for d in edges.values()) * penalty.get((u, v), 1.0)

    accepted, kept = list(found), []
    for _ in range(MAX_ALTERNATIVES * 3):
        if len(kept) == MAX_ALTERNATIVES:
            break
        path = nx.shortest_path(graph, source, target, weight=penalized)
        for edge in zip(path, path[1:]):
            penalty[edge] = penalty.get(edge, 1.0) * ALT_PENALTY
        if all(_overlap(graph, path, other) <= ALT_MAX_OVERLAP for other in accepted):
            accepted.append(path)
            kept.append(path)
    return kept


def _overlap(graph, path, other):
    """Share of path's length that also belongs to other."""
    other_edges = set(zip(other, other[1:]))
    total = shared = 0.0
    for u, v in zip(path, path[1:]):
        length = min(d["length"] for d in graph[u][v].values())
        total += length
        if (u, v) in other_edges:
            shared += length
    return shared / total if total else 1.0


def _summary(graph, nodes, origin, destination, risk_dyn, edge_weight):
    """Build the drawable line (clicked point -> streets -> clicked point) and route metrics."""
    coords, length, risks = [list(origin)], 0.0, []
    for u, v in zip(nodes, nodes[1:]):
        data = min(graph[u][v].values(), key=edge_weight)  # parallel edge actually used
        coords.extend(edge_coords(graph, u, v, data))
        length += data["length"]
        risks.append(risk_dyn(data))
    if len(nodes) == 1:
        coords.append([graph.nodes[nodes[0]]["y"], graph.nodes[nodes[0]]["x"]])
    coords.append(list(destination))
    return {"coords": coords, "length_m": round(length),
            "time_min": round(length / (DEFAULT_SPEED_KMH / 3.6) / 60, 1),
            "mean_risk": round(sum(risks) / len(risks), 3) if risks else 0,
            "max_risk": round(max(risks), 3) if risks else 0}


def _snap(graph, point, name):
    """Nearest street node to a chosen point, with a clear message when it cannot be used."""
    south, west, north, east = PILOT_BBOX
    if not (south <= point[0] <= north and west <= point[1] <= east):
        raise ValueError(f"The {name} point is outside the covered area. Choose a point inside the dashed border.")
    node, distance = _nearest_node(graph, *point)
    if distance > MAX_SNAP_M:
        raise ValueError(f"The {name} point is {distance / 1000:.1f} km from the nearest street "
                         "(it may be on water, a hill or a park). Choose a point on or next to a street.")
    return node, distance


@lru_cache(maxsize=1)
def _node_arrays(graph):
    """Node ids and coordinates as arrays, built once per loaded graph."""
    nodes = list(graph.nodes)
    return nodes, np.array([graph.nodes[n]["y"] for n in nodes]), np.array([graph.nodes[n]["x"] for n in nodes])


def _nearest_node(graph, lat, lon):
    """Closest graph node to (lat, lon) and its distance in metres."""
    nodes, ys, xs = _node_arrays(graph)
    # Equirectangular approximation is enough to pick the nearest node in a 9 km area.
    i = int(np.argmin((ys - lat) ** 2 + ((xs - lon) * np.cos(np.radians(lat))) ** 2))
    return nodes[i], abs(GEOD.inv(lon, lat, xs[i], ys[i])[2])
