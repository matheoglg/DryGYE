"""Download the pilot-area street graph from OpenStreetMap and save it to data/processed.

Run once with internet (from the repo root):  python scripts/build_road_graph.py
The app then routes offline from the saved GraphML file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drygye.config import GRAPH_PATH  # noqa: E402
from drygye.roads import build_graph, save_graph  # noqa: E402

if __name__ == "__main__":
    graph = build_graph()
    save_graph(graph)
    print(f"Saved {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges to {GRAPH_PATH}")
