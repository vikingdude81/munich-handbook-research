"""
scripts/cross_source_divergence.py — Cross-source entity divergence analysis.

For each entity appearing in 2+ source corpora, extract what each source
says about it and compute divergence metrics.

High-divergence entities are "contested" — the sources disagree about their
nature, role, or attributes. In AI terms: these are the tasks where different
models give wildly different outputs.

This mirrors a key insight from the Munich Handbook project: the same spirit
(e.g. Astaroth) is described differently across Kieckhefer's commentary,
the raw Necromancy text, and the Worship of the Dead corpus. These divergences
reflect genuine manuscript tradition conflicts — and map to the phenomenon of
model disagreement in multi-source RAG systems.

Sources:
  - forbidden_rites_pdf (Kieckhefer PDF, 39 chunks)
  - necro (Necromancy text, 38 chunks)
  - worship_dead (Worship of the Dead, 49 chunks)

Divergence metrics:
  1. Attribute divergence — how different are the attributes assigned by each source?
  2. Role divergence — does each source assign the same role/type?
  3. Description length divergence — does one source say much more than another?
  4. Relationship divergence — does each source connect this entity to different others?

Output:
  docs/divergence_report.md — full analysis report
  data/divergence_scores.json — machine-readable divergence scores per entity

Usage:
  python scripts/cross_source_divergence.py
  python scripts/cross_source_divergence.py --type spirit --min-sources 2
  python scripts/cross_source_divergence.py --top 50 --export-csv
"""

import os
import sys
import json
import glob
import csv
import argparse
import math
from dataclasses import dataclass, asdict
from collections import defaultdict
from typing import List, Dict, Optional

# Ensure root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

UNIFIED_PATH = os.path.join(ROOT, "data", "unified_entities.json")
DISTILLED_DIR = os.path.join(ROOT, "data", "distilled")
REPORT_PATH = os.path.join(ROOT, "docs", "divergence_report.md")
JSON_PATH = os.path.join(ROOT, "data", "divergence_scores.json")
CSV_PATH = os.path.join(ROOT, "data", "divergence_scores.csv")

CONTESTED_THRESHOLD = 0.4  # composite score above this → contested


# ---------------------------------------------------------------------------
# DivergenceScore dataclass
# ---------------------------------------------------------------------------

@dataclass
class DivergenceScore:
    """Divergence metrics for a single entity across source corpora."""
    entity_name: str
    entity_type: str
    sources: List[str]
    n_sources: int
    attribute_divergence: float   # Jaccard distance between attribute key sets
    role_consistency: float       # 1.0 = all sources agree on type; 0.0 = all disagree
    mention_imbalance: float      # ratio max/min mention count across sources
    relationship_divergence: float  # Jaccard distance between relationship partner sets
    composite_score: float        # weighted average of the above
    contested: bool               # True if composite_score > threshold


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_unified_entities(path: str) -> tuple:
    """
    Load entities and relationships from unified_entities.json.

    Returns:
        (entities_list, relationships_list)
    """
    if not os.path.exists(path):
        return [], []

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if isinstance(data, dict) and "entities" in data:
        return data.get("entities", []), data.get("relationships", [])

    if isinstance(data, list):
        entities, relationships = [], []
        for chunk in data:
            if isinstance(chunk, dict):
                entities.extend(chunk.get("entities", []))
                relationships.extend(chunk.get("relationships", []))
        return entities, relationships

    if isinstance(data, dict):
        entities, relationships = [], []
        for chunk in data.values():
            if isinstance(chunk, dict):
                entities.extend(chunk.get("entities", []))
                relationships.extend(chunk.get("relationships", []))
        return entities, relationships

    return [], []


def load_per_source_entities(data_dir: str) -> Dict[str, List[dict]]:
    """
    Load all distilled JSON files from data/distilled/*/distilled_*.json
    and group entities by source corpus.

    Returns:
        Dict mapping source_name → list of entity dicts
    """
    pattern = os.path.join(data_dir, "**", "*.json")
    files = glob.glob(pattern, recursive=True)

    by_source: Dict[str, List[dict]] = defaultdict(list)

    for fpath in files:
        # Infer source from directory structure
        rel = os.path.relpath(fpath, data_dir)
        parts = rel.split(os.sep)
        source = parts[0] if len(parts) > 1 else "unknown"

        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue

        # Handle various formats
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    item.setdefault("_source", source)
                    by_source[source].append(item)
                elif isinstance(item, dict):
                    for ent in item.get("entities", []):
                        if isinstance(ent, dict):
                            ent.setdefault("_source", source)
                            by_source[source].append(ent)
        elif isinstance(data, dict):
            for ent in data.get("entities", []):
                if isinstance(ent, dict):
                    ent.setdefault("_source", source)
                    by_source[source].append(ent)

    return dict(by_source)


# ---------------------------------------------------------------------------
# Divergence computations
# ---------------------------------------------------------------------------

def _jaccard_distance(set_a: set, set_b: set) -> float:
    """Jaccard distance between two sets (1 − Jaccard similarity)."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 1.0 - (intersection / union) if union > 0 else 0.0


def _pairwise_jaccard_mean(sets: List[set]) -> float:
    """Mean Jaccard distance across all pairs of sets."""
    if len(sets) < 2:
        return 0.0
    distances = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            distances.append(_jaccard_distance(sets[i], sets[j]))
    return sum(distances) / len(distances) if distances else 0.0


def compute_attribute_divergence(per_source_attrs: Dict[str, set]) -> float:
    """
    Compute mean pairwise Jaccard distance between attribute key sets across sources.
    """
    sets = list(per_source_attrs.values())
    return round(_pairwise_jaccard_mean(sets), 6)


def compute_role_consistency(per_source_types: Dict[str, str]) -> float:
    """
    Compute role consistency: fraction of sources that agree on the entity type.
    1.0 = all agree; < 1.0 = at least one source disagrees.
    """
    if not per_source_types:
        return 1.0
    types = list(per_source_types.values())
    most_common_count = max(types.count(t) for t in set(types))
    return round(most_common_count / len(types), 6)


def compute_mention_imbalance(per_source_mentions: Dict[str, int]) -> float:
    """
    Compute ratio of max to min mention count.
    1.0 = perfectly balanced; high values = one source dominates.
    """
    counts = [c for c in per_source_mentions.values() if c > 0]
    if len(counts) < 2:
        return 1.0
    return round(max(counts) / min(counts), 6)


def compute_relationship_divergence(per_source_rels: Dict[str, set]) -> float:
    """
    Compute mean pairwise Jaccard distance between relationship partner sets.
    """
    sets = list(per_source_rels.values())
    return round(_pairwise_jaccard_mean(sets), 6)


def _composite(attr_div, role_cons, mention_imbal, rel_div) -> float:
    """
    Weighted composite divergence score.

    Weights:
      - attribute divergence:      0.30
      - role inconsistency:        0.30  (1 - consistency)
      - mention imbalance (log):   0.15
      - relationship divergence:   0.25
    """
    role_div = 1.0 - role_cons
    # Normalise mention imbalance with log scaling:
    # imbalance=1 (perfectly balanced) → 0.0
    # imbalance=100 (extreme domination) → 1.0
    # Using log base 100 so that a 10× imbalance maps to ~0.5
    _IMBALANCE_NORM = 100.0
    mention_div = min(1.0, math.log(max(mention_imbal, 1.0)) / math.log(_IMBALANCE_NORM))
    score = (
        0.30 * attr_div
        + 0.30 * role_div
        + 0.15 * mention_div
        + 0.25 * rel_div
    )
    return round(min(1.0, score), 6)


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_all_divergence_scores(
    unified_path: str,
    data_dir: str,
    type_filter: Optional[str] = None,
    min_sources: int = 2,
    threshold: float = CONTESTED_THRESHOLD,
) -> List[DivergenceScore]:
    """
    Compute divergence scores for all multi-source entities.

    Args:
        unified_path: Path to unified_entities.json.
        data_dir: Path to data directory (for per-source distilled files).
        type_filter: Restrict to this entity type if set.
        min_sources: Minimum number of sources for inclusion.
        threshold: Composite score above which an entity is marked contested.

    Returns:
        List of DivergenceScore objects, sorted by composite_score descending.
    """
    entities, relationships = load_unified_entities(unified_path)
    per_source_data = load_per_source_entities(data_dir)

    # Build a lookup: entity_name → list of entity dicts, grouped by source
    # from the unified file (entities carry a 'sources' field)
    unified_by_name: Dict[str, List[dict]] = defaultdict(list)
    for ent in entities:
        name = ent.get("name", "").strip()
        if name:
            unified_by_name[name].append(ent)

    # Build relationship lookup: entity_name, source → set of related entity names
    # (relationships don't always carry source, so use the unified list)
    rel_partners_global: Dict[str, set] = defaultdict(set)
    for rel in relationships:
        src = rel.get("source", rel.get("from", rel.get("entity1", ""))).strip()
        tgt = rel.get("target", rel.get("to", rel.get("entity2", ""))).strip()
        if src:
            rel_partners_global[src].add(tgt)
        if tgt:
            rel_partners_global[tgt].add(src)

    # For per-source relationship data, try to extract from distilled files
    source_rel_partners: Dict[str, Dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for src_name, src_entities in per_source_data.items():
        for ent in src_entities:
            name = ent.get("name", "").strip()
            if not name:
                continue
            # Some distilled files embed related_to / relationships inline
            for rel in ent.get("relationships", []):
                partner = (
                    rel.get("target", rel.get("to", rel.get("entity", ""))) or ""
                ).strip()
                if partner:
                    source_rel_partners[name][src_name].add(partner)

    scores = []

    for name, ent_list in unified_by_name.items():
        # Collect sources from all mentions
        all_sources = set()
        for ent in ent_list:
            srcs = ent.get("sources", [])
            if isinstance(srcs, str):
                srcs = [srcs]
            all_sources.update(srcs)

        if len(all_sources) < min_sources:
            continue

        # Representative entity for type
        primary_ent = ent_list[0]
        entity_type = primary_ent.get("type", primary_ent.get("entity_type", "unknown"))

        if type_filter and entity_type != type_filter:
            continue

        # Per-source attribute key sets
        per_source_attr_keys: Dict[str, set] = {}
        per_source_types: Dict[str, str] = {}
        per_source_mentions: Dict[str, int] = {}

        for ent in ent_list:
            srcs = ent.get("sources", [])
            if isinstance(srcs, str):
                srcs = [srcs]
            etype = ent.get("type", ent.get("entity_type", "unknown"))
            attrs = ent.get("attributes", {})
            attr_keys = set(attrs.keys()) if isinstance(attrs, dict) else set()
            mentions = ent.get("mention_count", 1)

            for s in srcs:
                if s not in per_source_attr_keys:
                    per_source_attr_keys[s] = attr_keys
                else:
                    per_source_attr_keys[s] |= attr_keys
                per_source_types[s] = etype
                per_source_mentions[s] = per_source_mentions.get(s, 0) + mentions

        # Per-source relationship sets
        per_source_rels: Dict[str, set] = {}
        if name in source_rel_partners:
            per_source_rels = dict(source_rel_partners[name])
        # If no per-source rel data, use the global set split by source presence
        if len(per_source_rels) < 2 and rel_partners_global[name]:
            # Assign all known partners to every source (worst-case = no divergence)
            for s in all_sources:
                per_source_rels[s] = rel_partners_global[name]

        attr_div = compute_attribute_divergence(per_source_attr_keys)
        role_cons = compute_role_consistency(per_source_types)
        mention_imbal = compute_mention_imbalance(per_source_mentions)
        rel_div = compute_relationship_divergence(per_source_rels)

        composite = _composite(attr_div, role_cons, mention_imbal, rel_div)
        contested = composite > threshold

        scores.append(DivergenceScore(
            entity_name=name,
            entity_type=entity_type,
            sources=sorted(all_sources),
            n_sources=len(all_sources),
            attribute_divergence=attr_div,
            role_consistency=role_cons,
            mention_imbalance=mention_imbal,
            relationship_divergence=rel_div,
            composite_score=composite,
            contested=contested,
        ))

    scores.sort(key=lambda x: x.composite_score, reverse=True)
    return scores


# ---------------------------------------------------------------------------
# Export functions
# ---------------------------------------------------------------------------

def export_json(scores: List[DivergenceScore], path: str = JSON_PATH) -> None:
    """Write divergence scores to JSON."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(s) for s in scores], fh, indent=2)
    print(f"JSON scores saved to: {path}")


def export_csv(scores: List[DivergenceScore], path: str = CSV_PATH) -> None:
    """Write divergence scores to CSV."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    if not scores:
        return
    fields = list(asdict(scores[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for s in scores:
            row = asdict(s)
            row["sources"] = "|".join(row["sources"])
            writer.writerow(row)
    print(f"CSV scores saved to:  {path}")


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _ascii_bar(value: float, width: int = 30) -> str:
    """Generate a simple ASCII bar chart segment."""
    filled = int(round(value * width))
    return "█" * filled + "░" * (width - filled)


def generate_divergence_report(
    scores: List[DivergenceScore],
    output_path: str = REPORT_PATH,
    top_n: int = 20,
) -> None:
    """Generate a human-readable markdown divergence report."""
    contested = [s for s in scores if s.contested]
    consistent = [s for s in scores if not s.contested]

    lines = [
        "# Munich Handbook Cross-Source Divergence Analysis\n",
        "## Overview\n",
        "Entities appearing in multiple source corpora are analysed for divergence: "
        "how differently do the sources describe them?\n",
        f"- **Total multi-source entities analysed**: {len(scores)}",
        f"- **Contested entities** (composite score > {CONTESTED_THRESHOLD}): {len(contested)}",
        f"- **Consistent entities**: {len(consistent)}",
        "",
        "## Top 20 Most Contested Entities\n",
        "| Entity | Type | Sources | Composite Score |",
        "|--------|------|---------|-----------------|",
    ]

    for s in scores[:top_n]:
        src_str = ", ".join(s.sources[:4])
        lines.append(
            f"| {s.entity_name} | {s.entity_type} | {src_str} | {s.composite_score:.4f} |"
        )

    lines += [
        "",
        "## Top 20 Most Consistent Entities\n",
        "| Entity | Type | Sources | Composite Score |",
        "|--------|------|---------|-----------------|",
    ]
    for s in sorted(scores, key=lambda x: x.composite_score)[:top_n]:
        src_str = ", ".join(s.sources[:4])
        lines.append(
            f"| {s.entity_name} | {s.entity_type} | {src_str} | {s.composite_score:.4f} |"
        )

    # Per-source unique entities
    source_counts: dict = {}
    for s in scores:
        if s.n_sources == 1:
            src = s.sources[0] if s.sources else "unknown"
            source_counts[src] = source_counts.get(src, 0) + 1

    lines += [
        "",
        "## Per-Source Unique Entities\n",
        "Entities appearing in only one source corpus:\n",
        "| Source | Unique Entity Count |",
        "|--------|---------------------|",
    ]
    for src, count in sorted(source_counts.items()):
        lines.append(f"| {src} | {count} |")

    # Role conflicts
    role_conflicts = [s for s in scores if s.role_consistency < 1.0 and s.n_sources >= 2]
    lines += [
        "",
        "## Role Conflicts\n",
        "Entities where different sources assign different entity types:\n",
        "| Entity | Sources | Role Consistency |",
        "|--------|---------|------------------|",
    ]
    for s in sorted(role_conflicts, key=lambda x: x.role_consistency)[:20]:
        src_str = ", ".join(s.sources[:4])
        lines.append(f"| {s.entity_name} | {src_str} | {s.role_consistency:.4f} |")

    if not role_conflicts:
        lines.append("None — all multi-source entities have consistent types across sources.")

    # Distribution histogram
    lines += [
        "",
        "## Composite Score Distribution\n",
        "```",
    ]
    buckets = [0] * 10
    for s in scores:
        idx = min(9, int(s.composite_score * 10))
        buckets[idx] += 1
    max_count = max(buckets) if buckets else 1
    for i, count in enumerate(buckets):
        lo = i * 0.1
        hi = lo + 0.1
        bar = _ascii_bar(count / max(max_count, 1), 40)
        lines.append(f"{lo:.1f}-{hi:.1f}  {bar}  {count}")
    lines.append("```")
    lines.append("")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Divergence report saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-source entity divergence analysis for Munich Handbook"
    )
    parser.add_argument("--type", metavar="ENTITY_TYPE",
                        help="Filter to a specific entity type (e.g. spirit)")
    parser.add_argument("--min-sources", type=int, default=2,
                        help="Minimum number of sources for inclusion (default: 2)")
    parser.add_argument("--top", type=int, default=20,
                        help="Number of top entities in report (default: 20)")
    parser.add_argument("--export-csv", action="store_true",
                        help="Export scores to CSV")
    parser.add_argument("--threshold", type=float, default=CONTESTED_THRESHOLD,
                        help=f"Contested threshold (default: {CONTESTED_THRESHOLD})")
    parser.add_argument("--unified", default=UNIFIED_PATH,
                        help="Path to unified_entities.json")
    parser.add_argument("--data-dir", default=os.path.join(ROOT, "data"),
                        help="Data directory for distilled source files")
    args = parser.parse_args()

    if not os.path.exists(args.unified):
        print(f"ERROR: {args.unified} not found.")
        print("Run the distillation pipeline first to generate unified_entities.json.")
        sys.exit(1)

    print(f"Loading unified entities from: {args.unified}")
    scores = compute_all_divergence_scores(
        unified_path=args.unified,
        data_dir=args.data_dir,
        type_filter=args.type,
        min_sources=args.min_sources,
        threshold=args.threshold,
    )

    if not scores:
        print("No multi-source entities found with the current filters.")
        sys.exit(0)

    contested = sum(1 for s in scores if s.contested)
    print(f"  Entities analysed: {len(scores)}")
    print(f"  Contested:         {contested}")
    print(f"  Top contested: {scores[0].entity_name} ({scores[0].composite_score:.4f})")

    export_json(scores, JSON_PATH)
    generate_divergence_report(scores, REPORT_PATH, top_n=args.top)

    if args.export_csv:
        export_csv(scores, CSV_PATH)


if __name__ == "__main__":
    main()
