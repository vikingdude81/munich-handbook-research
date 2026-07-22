#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_glossary.py — generate the entity glossary/index from the unified DB.

Outputs:
  docs/ENTITY_GLOSSARY.md   — human-readable glossary grouped by type,
                              alphabetical, with descriptions and provenance
  data/entity_index.csv     — machine-readable index (one row per entity)

Descriptions are assembled from the entity's merged attributes (function, rank,
role, nature, description fields) — nothing is invented; empty attributes yield
an '(attributes not extracted)' marker.
"""

import csv
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "unified_entities.json")
MD_OUT = os.path.join(ROOT, "docs", "ENTITY_GLOSSARY.md")
CSV_OUT = os.path.join(ROOT, "data", "entity_index.csv")

DESC_KEYS = ["description", "function", "functions", "role", "rank", "nature",
             "appearance", "power", "powers", "purpose", "meaning", "domain"]

TYPE_ORDER = ["spirit", "deity", "divine_name", "person", "ritual",
              "incantation", "ingredient", "tool", "location", "concept",
              "text", "unknown"]


def flat(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v[:3])
    return str(v)


def describe(e):
    attrs = e.get("attributes", {}) or {}
    parts = []
    for k in DESC_KEYS:
        if k in attrs and attrs[k]:
            parts.append(f"{k}: {flat(attrs[k])}")
        if len(parts) >= 3:
            break
    if not parts and e.get("raw_quotes"):
        parts.append(f'quote: "{e["raw_quotes"][0][:110]}"')
    return " · ".join(parts) if parts else "(attributes not extracted)"


def main():
    db = json.load(open(DB, encoding="utf-8"))
    entities = db["entities"]
    meta = db.get("metadata", {})

    # ── CSV index ────────────────────────────────────────────────────────────
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["canonical_name", "display_name", "type", "occurrences",
                    "distinct_works", "cross_work", "page_refs",
                    "name_variants", "description"])
        for e in sorted(entities, key=lambda x: (x["type"], x["canonical_name"])):
            w.writerow([
                e["canonical_name"], e["display_name"], e["type"],
                e.get("occurrence_count", 1),
                "|".join(e.get("distinct_works", [])),
                "yes" if e.get("cross_work") else "",
                "|".join(e.get("page_refs", [])[:5]),
                "|".join(e.get("name_variants", [])[:6]),
                describe(e),
            ])

    # ── Markdown glossary ────────────────────────────────────────────────────
    by_type = {}
    for e in entities:
        by_type.setdefault(e["type"], []).append(e)

    lines = [
        "# Entity Glossary — Munich Handbook Research",
        "",
        f"Generated from `data/unified_entities.json` "
        f"({meta.get('generated', '?')}; {len(entities)} entities). "
        "Descriptions are assembled from extracted attributes only — nothing "
        "here is invented. Provenance verification: see "
        "`docs/entity_verification_report.json` (99%+ of quote-bearing "
        "entities verified against source text).",
        "",
        "Machine-readable version: `data/entity_index.csv`.",
        "",
        "## Contents",
        "",
    ]
    for t in TYPE_ORDER:
        if t in by_type:
            lines.append(f"- [{t.title()} ({len(by_type[t])})](#{t})")
    lines.append("")

    for t in TYPE_ORDER:
        if t not in by_type:
            continue
        group = sorted(by_type[t], key=lambda x: x["canonical_name"])
        lines.append(f'<a id="{t}"></a>')
        lines.append(f"## {t.title()}  ({len(group)})")
        lines.append("")
        for e in group:
            works = ", ".join(e.get("distinct_works", []))
            cross = " ⭐cross-work" if e.get("cross_work") else ""
            occ = e.get("occurrence_count", 1)
            variants = e.get("name_variants", [])
            var_s = f" — variants: {', '.join(variants[:5])}" if variants else ""
            pages = e.get("page_refs", [])
            page_s = f" — pp. {', '.join(pages[:4])}" if pages else ""
            lines.append(f"**{e['display_name']}** (×{occ}; {works}{cross})"
                         f"{page_s}{var_s}  ")
            lines.append(f"  {describe(e)}")
            lines.append("")

    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Glossary: {MD_OUT} ({len(entities)} entities, "
          f"{sum(1 for t in TYPE_ORDER if t in by_type)} sections)")
    print(f"Index CSV: {CSV_OUT}")


if __name__ == "__main__":
    main()
