#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Non-destructive correction of cross-grimoire statistics.

WHY THIS EXISTS
---------------
`necro` and `forbidden_rites_pdf` are the SAME book — Kieckhefer's *Forbidden
Rites* (the Munich Handbook / Clm 849 study), ingested twice (a .txt rip and the
PDF). The original stats counted a spirit appearing in both as "multi-source",
which inflated the cross-grimoire figure to 266 when the genuine cross-WORK
overlap is far smaller.

This script collapses sources to canonical WORK ids, recomputes the honest
cross-work statistics, and writes:
  - data/unified_entities.corrected.json   (copy of the DB with corrected
                                            `distinct_works` / `cross_work`
                                            fields per entity — originals kept)
  - docs/corrected_stats.json              (machine-readable corrected summary)

It NEVER overwrites unified_entities.json. Promote the corrected copy manually
after review.

Usage:
    python scripts/correct_cross_grimoire_stats.py
"""

import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "unified_entities.json")
OUT_DB = os.path.join(ROOT, "data", "unified_entities.corrected.json")
OUT_STATS = os.path.join(ROOT, "docs", "corrected_stats.json")

# ── Canonical work map ────────────────────────────────────────────────────────
# Multiple source ingests can belong to the same underlying WORK. Two source
# ids here resolve to one work so a book can't "cross-reference" itself.
WORK_ID = {
    "necro": "kieckhefer_clm849",            # H:\NECRO.txt  (Forbidden Rites, txt rip)
    "forbidden_rites_pdf": "kieckhefer_clm849",  # same book, PDF
    "worship_dead": "garnier_1909",          # Garnier, Worship of the Dead (1909) —
                                             # modern secondary mythology, NOT a grimoire
    "ars_notoria": "ars_notoria",
    "liber_juratus": "liber_juratus",
}

# Works that are genuine primary magical texts (for an honest grimoire count)
GRIMOIRE_WORKS = {"kieckhefer_clm849", "ars_notoria", "liber_juratus"}


def source_prefix(s):
    return s.split(":")[0] if ":" in s else s


def distinct_works(sources):
    """Canonical work ids spanned by a list of '<source>:chunk_N' strings."""
    return {WORK_ID.get(source_prefix(s), source_prefix(s)) for s in sources}


def main():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    entities = db["entities"]
    spirits = [e for e in entities if e.get("type") == "spirit"]

    # Annotate every entity with corrected work-level provenance (non-destructive)
    for e in entities:
        works = sorted(distinct_works(e.get("sources", [])))
        e["distinct_works"] = works
        e["cross_work"] = len(works) >= 2

    # ── Corrected spirit cross-work stats ────────────────────────────────────
    old_multi_source = 0
    new_multi_work = 0
    same_book_pair = 0
    combo_counter = Counter()
    for s in spirits:
        prefixes = {source_prefix(x) for x in s.get("sources", [])}
        works = distinct_works(s.get("sources", []))
        if len(prefixes) > 1:
            old_multi_source += 1
        if prefixes == {"necro", "forbidden_rites_pdf"}:
            same_book_pair += 1
        if len(works) >= 2:
            new_multi_work += 1
            combo_counter[tuple(sorted(works))] += 1

    stats = {
        "note": (
            "Corrected cross-grimoire statistics. `necro` and "
            "`forbidden_rites_pdf` are the same book (Kieckhefer, Clm 849) and "
            "are collapsed to one work. `worship_dead` (Garnier 1909) is a modern "
            "secondary mythology text, not a grimoire."
        ),
        "spirits_total": len(spirits),
        "OLD_multi_source_spirits": old_multi_source,
        "of_which_same_book_only (necro+forbidden_rites)": same_book_pair,
        "CORRECTED_multi_work_spirits": new_multi_work,
        "genuine_cross_work_combinations": {
            " + ".join(k): v for k, v in sorted(combo_counter.items(), key=lambda x: -x[1])
        },
        "grimoire_works_count": len(GRIMOIRE_WORKS),
        "grimoire_works": sorted(GRIMOIRE_WORKS),
        "excluded_non_grimoire": ["garnier_1909 (Worship of the Dead, 1909)"],
        "spirits_occurring_once": sum(1 for s in spirits if s.get("occurrence_count") == 1),
        "spirits_zero_attributes": sum(1 for s in spirits if not s.get("attributes")),
    }

    db.setdefault("metadata", {})["cross_grimoire_correction"] = stats

    os.makedirs(os.path.dirname(OUT_STATS), exist_ok=True)
    with open(OUT_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    with open(OUT_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print("Corrected cross-grimoire statistics")
    print("=" * 50)
    for k, v in stats.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"{k}: {v}")
    print(f"\nWrote {OUT_DB}")
    print(f"Wrote {OUT_STATS}")


if __name__ == "__main__":
    main()
