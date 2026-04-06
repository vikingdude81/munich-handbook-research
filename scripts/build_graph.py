"""
scripts/build_graph.py — Entity relationship knowledge graph builder.

Builds interactive and static visualizations of the Munich Handbook entity
relationship network from data/unified_entities.json.

The relationship network maps the infernal hierarchy as a directed graph:
  - Spirits (nodes) are conjured entities — the named models
  - Rituals (nodes) are protocols — the system prompts
  - Ingredients (nodes) are context — the fumigation/offering inputs
  - Relationships (edges) encode structural dependencies between entities

Outputs:
  docs/graph/spirit_network.html  — interactive pyvis graph (self-contained)
  docs/graph/spirit_network.png   — static matplotlib graph
  docs/graph/graph_stats.json     — graph statistics (centrality, clusters, etc.)
  docs/graph/graph_report.md      — human-readable analysis report

Node types and colors:
  spirit      — red (#e74c3c) — primary conjuration targets
  ritual      — purple (#9b59b6) — protocol nodes
  ingredient  — green (#27ae60) — fumigation/offering nodes
  tool        — orange (#e67e22) — physical instrument nodes
  location    — blue (#3498db) — spatial/directional nodes
  person      — yellow (#f1c40f) — historical/textual persons
  concept     — gray (#95a5a6) — abstract concepts
  divine_name — gold (#ffd700) — constraint/authority names

Edge types and styling:
  co_invoked   — thick red edges (co-invocation = fan-out parallelism)
  uses         — thin blue edges
  appears_in   — thin gray edges
  commands     — medium orange edges (hierarchy)
  ingredient_of — thin green edges

Usage:
  python scripts/build_graph.py
  python scripts/build_graph.py --source necro
  python scripts/build_graph.py --type spirit
  python scripts/build_graph.py --min-degree 3
  python scripts/build_graph.py --no-html
"""

import os
import sys
import json
import argparse
import math
from collections import defaultdict, Counter
from typing import Optional

# Ensure root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NODE_COLORS = {
    "spirit":      "#e74c3c",
    "ritual":      "#9b59b6",
    "ingredient":  "#27ae60",
    "tool":        "#e67e22",
    "location":    "#3498db",
    "person":      "#f1c40f",
    "concept":     "#95a5a6",
    "divine_name": "#ffd700",
    "unknown":     "#bdc3c7",
}

EDGE_COLORS = {
    "co_invoked":     "#e74c3c",
    "uses":           "#3498db",
    "appears_in":     "#95a5a6",
    "commands":       "#e67e22",
    "ingredient_of":  "#27ae60",
    "default":        "#7f8c8d",
}

EDGE_WIDTHS = {
    "co_invoked":    4.0,
    "commands":      2.5,
    "uses":          1.5,
    "ingredient_of": 1.5,
    "appears_in":    1.0,
    "default":       1.0,
}

DATA_PATH = os.path.join(ROOT, "data", "unified_entities.json")
GRAPH_DIR = os.path.join(ROOT, "docs", "graph")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_unified_entities(path: str) -> tuple:
    """
    Load entities and relationships from unified_entities.json.

    Handles two formats:
      1. Top-level 'entities' + 'relationships' arrays
      2. Chunk-by-chunk format where each chunk has its own entities/relationships

    Returns:
        (entities_list, relationships_list)
    """
    if not os.path.exists(path):
        print(f"ERROR: {path} not found.")
        print("Run the distillation pipeline first to generate unified_entities.json.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Format 1: flat top-level lists
    if isinstance(data, dict) and "entities" in data:
        return data.get("entities", []), data.get("relationships", [])

    # Format 2: chunk-based list
    if isinstance(data, list):
        all_entities = []
        all_relationships = []
        for chunk in data:
            if isinstance(chunk, dict):
                all_entities.extend(chunk.get("entities", []))
                all_relationships.extend(chunk.get("relationships", []))
        return all_entities, all_relationships

    # Format 3: dict of chunks
    if isinstance(data, dict):
        all_entities = []
        all_relationships = []
        for key, value in data.items():
            if isinstance(value, dict):
                all_entities.extend(value.get("entities", []))
                all_relationships.extend(value.get("relationships", []))
        return all_entities, all_relationships

    print(f"ERROR: Unrecognised format in {path}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------

def build_graph(
    entities: list,
    relationships: list,
    source_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    min_degree: int = 0,
) -> "nx.DiGraph":
    """
    Build a networkx DiGraph from entity/relationship lists.

    Args:
        entities: List of entity dicts.
        relationships: List of relationship dicts.
        source_filter: If set, include only entities from this source.
        type_filter: If set, include only entities of this type.
        min_degree: Minimum degree for inclusion (applied after building).

    Returns:
        networkx.DiGraph
    """
    import networkx as nx

    G = nx.DiGraph()

    # Count mentions per entity
    mention_counts: dict = defaultdict(int)
    for ent in entities:
        name = ent.get("name", "").strip()
        if name:
            mention_counts[name] += ent.get("mention_count", 1)

    # Add nodes
    seen_names = set()
    for ent in entities:
        name = ent.get("name", "").strip()
        if not name or name in seen_names:
            continue
        entity_type = ent.get("type", ent.get("entity_type", "unknown"))
        sources = ent.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]

        if source_filter and source_filter not in sources:
            continue
        if type_filter and entity_type != type_filter:
            continue

        seen_names.add(name)
        G.add_node(
            name,
            entity_type=entity_type,
            sources=sources,
            mention_count=mention_counts.get(name, 1),
            tier=ent.get("tier", ""),
            attributes=ent.get("attributes", {}),
        )

    # Add edges
    for rel in relationships:
        src = rel.get("source", rel.get("from", rel.get("entity1", ""))).strip()
        tgt = rel.get("target", rel.get("to", rel.get("entity2", ""))).strip()
        rel_type = rel.get("relationship", rel.get("type", "default"))

        if not src or not tgt:
            continue
        if src not in G or tgt not in G:
            continue
        G.add_edge(src, tgt, relationship=rel_type)

    # Apply min_degree filter
    if min_degree > 0:
        to_remove = [n for n in G.nodes() if G.degree(n) < min_degree]
        G.remove_nodes_from(to_remove)

    return G


# ---------------------------------------------------------------------------
# Graph statistics
# ---------------------------------------------------------------------------

def compute_stats(G: "nx.DiGraph") -> dict:
    """Compute graph statistics for graph_stats.json."""
    import networkx as nx

    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    if n_nodes == 0:
        return {"nodes": 0, "edges": 0}

    # Degree distribution
    degrees = dict(G.degree())
    degree_dist = Counter(degrees.values())

    # Centrality measures
    dc = nx.degree_centrality(G)
    top_dc = sorted(dc.items(), key=lambda x: x[1], reverse=True)[:20]

    # Betweenness centrality (can be slow on large graphs; limit to 500 nodes)
    if n_nodes <= 500:
        bc = nx.betweenness_centrality(G)
    else:
        bc = nx.betweenness_centrality(G, k=min(100, n_nodes))
    top_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:20]

    # Connected components (undirected)
    undirected = G.to_undirected()
    components = list(nx.connected_components(undirected))

    # Edge type distribution
    rel_types = Counter(
        data.get("relationship", "default")
        for _, _, data in G.edges(data=True)
    )

    density = nx.density(G)

    return {
        "total_nodes": n_nodes,
        "total_edges": n_edges,
        "density": round(density, 6),
        "connected_components": len(components),
        "largest_component_size": max(len(c) for c in components) if components else 0,
        "degree_distribution": {str(k): v for k, v in sorted(degree_dist.items())},
        "top_20_degree_centrality": [
            {"name": name, "centrality": round(val, 6)} for name, val in top_dc
        ],
        "top_20_betweenness_centrality": [
            {"name": name, "centrality": round(val, 6)} for name, val in top_bc
        ],
        "relationship_type_distribution": dict(rel_types.most_common()),
    }


# ---------------------------------------------------------------------------
# Pyvis HTML output
# ---------------------------------------------------------------------------

def build_pyvis_html(G: "nx.DiGraph", output_path: str) -> None:
    """Generate a self-contained interactive pyvis HTML graph."""
    try:
        from pyvis.network import Network
    except ImportError:
        print("pyvis not installed. Skipping HTML output.")
        print("Install with: pip install pyvis>=0.3.2")
        return

    net = Network(
        height="900px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="white",
        directed=True,
    )
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=120,
        spring_strength=0.05,
        damping=0.09,
    )

    # Scale node sizes by mention count (clamped)
    max_mentions = max(
        (G.nodes[n].get("mention_count", 1) for n in G.nodes()), default=1
    )

    for node in G.nodes():
        attrs = G.nodes[node]
        entity_type = attrs.get("entity_type", "unknown")
        color = NODE_COLORS.get(entity_type, NODE_COLORS["unknown"])
        mentions = attrs.get("mention_count", 1)
        size = 10 + 30 * (mentions / max(max_mentions, 1))
        sources = attrs.get("sources", [])
        degree = G.degree(node)
        tooltip = (
            f"<b>{node}</b><br>"
            f"Type: {entity_type}<br>"
            f"Sources: {', '.join(sources) if sources else 'unknown'}<br>"
            f"Mentions: {mentions}<br>"
            f"Degree: {degree}<br>"
            f"Tier: {attrs.get('tier', '')}"
        )
        net.add_node(
            node,
            label=node,
            color=color,
            size=float(size),
            title=tooltip,
        )

    for src, tgt, data in G.edges(data=True):
        rel_type = data.get("relationship", "default")
        color = EDGE_COLORS.get(rel_type, EDGE_COLORS["default"])
        width = EDGE_WIDTHS.get(rel_type, EDGE_WIDTHS["default"])
        net.add_edge(src, tgt, color=color, width=width, title=rel_type)

    net.show_buttons(filter_=["physics"])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    net.save_graph(output_path)
    print(f"Interactive HTML saved to: {output_path}")


# ---------------------------------------------------------------------------
# Matplotlib PNG output
# ---------------------------------------------------------------------------

def build_matplotlib_png(G: "nx.DiGraph", output_path: str) -> None:
    """Generate a static matplotlib PNG of the graph."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("matplotlib not installed. Skipping PNG output.")
        return

    try:
        import networkx as nx
    except ImportError:
        print("networkx not installed. Skipping PNG output.")
        return

    n = G.number_of_nodes()
    if n == 0:
        print("No nodes to plot.")
        return

    fig, ax = plt.subplots(figsize=(20, 16))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    k = 2.0 / math.sqrt(n) if n > 1 else 1.0
    pos = nx.spring_layout(G, k=k, seed=42)

    # Node colours and sizes
    node_colors = [
        NODE_COLORS.get(G.nodes[n].get("entity_type", "unknown"), NODE_COLORS["unknown"])
        for n in G.nodes()
    ]
    max_mentions = max((G.nodes[n].get("mention_count", 1) for n in G.nodes()), default=1)
    node_sizes = [
        100 + 600 * (G.nodes[n].get("mention_count", 1) / max(max_mentions, 1))
        for n in G.nodes()
    ]

    # Edge colours by relationship type
    edge_colors = [
        EDGE_COLORS.get(data.get("relationship", "default"), EDGE_COLORS["default"])
        for _, _, data in G.edges(data=True)
    ]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.5,
                           arrows=True, arrowsize=10, ax=ax)

    # Label only high-degree nodes to avoid clutter
    degree_threshold = max(2, G.number_of_nodes() // 20)
    labels = {
        n: n for n in G.nodes()
        if G.degree(n) >= degree_threshold
    }
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                            font_color="white", ax=ax)

    # Legend
    legend_patches = [
        mpatches.Patch(color=color, label=entity_type.capitalize())
        for entity_type, color in NODE_COLORS.items()
        if entity_type != "unknown"
    ]
    ax.legend(handles=legend_patches, loc="lower left", fontsize=8,
              facecolor="#2c2c4a", edgecolor="white", labelcolor="white")

    ax.set_title(
        "Munich Handbook Entity Relationship Network",
        color="white", fontsize=14, pad=12
    )
    ax.axis("off")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor="#1a1a2e", bbox_inches="tight")
    plt.close()
    print(f"Static PNG saved to:         {output_path}")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_report(G: "nx.DiGraph", stats: dict, output_path: str) -> None:
    """Generate a human-readable markdown analysis report."""
    import networkx as nx

    lines = [
        "# Munich Handbook Entity Relationship Graph Report\n",
        "## Summary\n",
        f"- **Total nodes**: {stats.get('total_nodes', 0)}",
        f"- **Total edges**: {stats.get('total_edges', 0)}",
        f"- **Graph density**: {stats.get('density', 0):.6f}",
        f"- **Connected components**: {stats.get('connected_components', 0)}",
        f"- **Largest component**: {stats.get('largest_component_size', 0)} nodes",
        "",
        "## Most Connected Spirits (Hub Nodes)\n",
        "| Entity | Type | Degree | Sources |",
        "|--------|------|--------|---------|",
    ]

    spirit_nodes = [
        (n, G.degree(n), G.nodes[n].get("entity_type", ""), G.nodes[n].get("sources", []))
        for n in G.nodes()
        if G.nodes[n].get("entity_type") == "spirit"
    ]
    for name, deg, etype, sources in sorted(spirit_nodes, key=lambda x: x[1], reverse=True)[:20]:
        src_str = ", ".join(sources[:3]) if sources else "—"
        lines.append(f"| {name} | {etype} | {deg} | {src_str} |")

    lines += [
        "",
        "## Key Bridge Entities (Betweenness Centrality)\n",
        "| Entity | Type | Betweenness |",
        "|--------|------|-------------|",
    ]
    for item in stats.get("top_20_betweenness_centrality", [])[:10]:
        name = item["name"]
        etype = G.nodes[name].get("entity_type", "unknown") if name in G else "unknown"
        lines.append(f"| {name} | {etype} | {item['centrality']:.6f} |")

    lines += [
        "",
        "## Isolated or Weakly Connected Entities\n",
        "Entities with degree ≤ 1:\n",
    ]
    isolated = [n for n in G.nodes() if G.degree(n) <= 1]
    if isolated:
        lines.append(", ".join(sorted(isolated)[:50]))
        if len(isolated) > 50:
            lines.append(f"… and {len(isolated) - 50} more")
    else:
        lines.append("None — all entities are connected.")

    lines += [
        "",
        "## Cross-Source Entities\n",
        "Entities appearing in 2 or more source corpora:\n",
        "| Entity | Type | Sources |",
        "|--------|------|---------|",
    ]
    cross_source = [
        (n, G.nodes[n].get("entity_type", ""), G.nodes[n].get("sources", []))
        for n in G.nodes()
        if len(G.nodes[n].get("sources", [])) >= 2
    ]
    for name, etype, sources in sorted(cross_source, key=lambda x: len(x[2]), reverse=True)[:30]:
        lines.append(f"| {name} | {etype} | {', '.join(sources)} |")

    lines += [
        "",
        "## Relationship Type Distribution\n",
        "| Relationship | Count |",
        "|--------------|-------|",
    ]
    for rel_type, count in stats.get("relationship_type_distribution", {}).items():
        lines.append(f"| {rel_type} | {count} |")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Markdown report saved to:    {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build entity relationship knowledge graph from unified_entities.json"
    )
    parser.add_argument("--source", metavar="SOURCE",
                        help="Filter to a single source corpus")
    parser.add_argument("--type", metavar="TYPE", dest="entity_type",
                        help="Filter to a single entity type")
    parser.add_argument("--min-degree", type=int, default=0,
                        help="Minimum degree for node inclusion")
    parser.add_argument("--no-html", action="store_true",
                        help="Skip pyvis HTML output")
    parser.add_argument("--no-png", action="store_true",
                        help="Skip matplotlib PNG output")
    parser.add_argument("--data", default=DATA_PATH,
                        help=f"Path to unified_entities.json (default: {DATA_PATH})")
    args = parser.parse_args()

    try:
        import networkx as nx
    except ImportError:
        print("networkx not installed. Install with: pip install networkx>=3.0")
        sys.exit(1)

    print(f"Loading data from: {args.data}")
    entities, relationships = load_unified_entities(args.data)
    print(f"  Entities:      {len(entities)}")
    print(f"  Relationships: {len(relationships)}")

    G = build_graph(
        entities,
        relationships,
        source_filter=args.source,
        type_filter=args.entity_type,
        min_degree=args.min_degree,
    )
    print(f"  Graph nodes:   {G.number_of_nodes()}")
    print(f"  Graph edges:   {G.number_of_edges()}")

    if G.number_of_nodes() == 0:
        print("WARNING: Graph has no nodes. Check filters and data format.")

    os.makedirs(GRAPH_DIR, exist_ok=True)

    # Compute statistics
    stats = compute_stats(G)
    stats_path = os.path.join(GRAPH_DIR, "graph_stats.json")
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(f"Graph stats saved to:        {stats_path}")

    # HTML output
    if not args.no_html:
        build_pyvis_html(G, os.path.join(GRAPH_DIR, "spirit_network.html"))

    # PNG output
    if not args.no_png:
        build_matplotlib_png(G, os.path.join(GRAPH_DIR, "spirit_network.png"))

    # Markdown report
    generate_report(G, stats, os.path.join(GRAPH_DIR, "graph_report.md"))


if __name__ == "__main__":
    main()
