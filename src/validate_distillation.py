#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_distillation.py — THE canonical validator for this project.

Replaces ~50 redundant validate_*/verify_*/audit_*/schema_checker scripts that
had accumulated across src/, scripts/, distill/, distilled/ and data/. Those all
checked a schema the pipeline NEVER produced (`spirit_name`, `rank`,
`legion_count`, `conjuration_method`, `page_folio`). This one checks the schema
the pipeline ACTUALLY emits.

Real distilled-chunk schema (see tools/source_distill.py):
    {
      "source_id": str,
      "chunk_id": int,
      "has_relevant_content": bool,
      "entities": [ {"name", "type", "attributes"(dict),
                     "page_ref"(opt), "raw_quote"(opt)} ],
      "relationships": [ {"from", "to", "type"} ],
      "summary": str,
      "key_passages": [str]
    }
    # parse failures are saved as {"parse_error": true, "raw_extraction": ...}

Real unified-DB schema (see scripts/normalize_entities.py):
    {"metadata": {...}, "entities": [merged], "relationships": [...],
     "chunk_summaries": [...]}

Usage:
    python src/validate_distillation.py                 # validate everything
    python src/validate_distillation.py --distilled-only
    python src/validate_distillation.py --unified-only
    python src/validate_distillation.py --json          # machine-readable report
Exit code is non-zero if any hard (structural) error is found.
"""

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISTILLED_DIR = os.path.join(ROOT, "data", "distilled")
UNIFIED_DB = os.path.join(ROOT, "data", "unified_entities.json")

ENTITY_TYPES = {
    "spirit", "ritual", "ingredient", "tool", "location", "person", "concept",
    "deity", "divine_name", "incantation", "text", "unknown",
}


class Report:
    def __init__(self):
        self.errors = []    # hard structural problems
        self.warnings = []  # soft / quality issues
        self.stats = {}

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def _is_str(v):
    return isinstance(v, str) and v.strip() != ""


# ── Distilled chunk validation ───────────────────────────────────────────────
def validate_distilled_chunk(path, rep):
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        rep.err(rel, f"invalid JSON ({e})")
        return None
    except OSError as e:
        rep.err(rel, f"cannot read ({e})")
        return None

    if not isinstance(data, dict):
        rep.err(rel, "top-level is not an object")
        return None

    # Parse-error placeholders are a known, tolerated state — count, don't fail.
    if data.get("parse_error"):
        rep.stats["parse_error_files"] = rep.stats.get("parse_error_files", 0) + 1
        rep.warn(rel, "unresolved parse_error placeholder (re-distill recommended)")
        return data

    n_ent = 0
    n_no_provenance = 0
    entities = data.get("entities", [])
    if not isinstance(entities, list):
        rep.err(rel, "'entities' is not a list")
    else:
        for i, e in enumerate(entities):
            if not isinstance(e, dict):
                rep.err(rel, f"entity[{i}] is not an object")
                continue
            n_ent += 1
            if not _is_str(e.get("name")):
                rep.err(rel, f"entity[{i}] missing/empty 'name'")
            etype = e.get("type")
            if not _is_str(etype):
                rep.err(rel, f"entity[{i}] missing/empty 'type'")
            elif etype not in ENTITY_TYPES:
                # Raw distilled types are intentionally messy; normalize_entities.py
                # maps them. Track for coverage, don't warn per-entity.
                rep.stats.setdefault("raw_type_counts", {})
                rep.stats["raw_type_counts"][etype] = (
                    rep.stats["raw_type_counts"].get(etype, 0) + 1)
            attrs = e.get("attributes", {})
            if not isinstance(attrs, dict):
                rep.warn(rel, f"entity[{i}] 'attributes' is not an object")
            # Provenance: at least one of page_ref / raw_quote
            if not _is_str(e.get("page_ref")) and not _is_str(e.get("raw_quote")):
                n_no_provenance += 1

    rels = data.get("relationships", [])
    if not isinstance(rels, list):
        rep.err(rel, "'relationships' is not a list")
    else:
        for i, r in enumerate(rels):
            if not isinstance(r, dict):
                rep.err(rel, f"relationship[{i}] is not an object")
                continue
            for k in ("from", "to", "type"):
                if not _is_str(r.get(k)):
                    rep.warn(rel, f"relationship[{i}] missing '{k}'")

    if data.get("has_relevant_content") and n_ent == 0:
        rep.warn(rel, "has_relevant_content=true but zero entities")

    rep.stats["chunks"] = rep.stats.get("chunks", 0) + 1
    rep.stats["entities"] = rep.stats.get("entities", 0) + n_ent
    rep.stats["entities_without_provenance"] = (
        rep.stats.get("entities_without_provenance", 0) + n_no_provenance)
    return data


def validate_distilled_tree(rep, distilled_dir=DISTILLED_DIR):
    if not os.path.isdir(distilled_dir):
        rep.err(distilled_dir, "distilled dir not found")
        return
    files = sorted(glob.glob(os.path.join(distilled_dir, "*", "distilled_*.json")))
    rep.stats["distilled_files"] = len(files)
    per_source = {}
    for path in files:
        src = os.path.basename(os.path.dirname(path))
        per_source[src] = per_source.get(src, 0) + 1
        validate_distilled_chunk(path, rep)
    rep.stats["sources"] = per_source


# ── Unified DB validation ────────────────────────────────────────────────────
def validate_unified(rep, unified_path=UNIFIED_DB):
    rel = os.path.relpath(unified_path, ROOT)
    if not os.path.isfile(unified_path):
        rep.warn(rel, "unified DB not found (skipping)")
        return
    try:
        with open(unified_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except json.JSONDecodeError as e:
        rep.err(rel, f"invalid JSON ({e})")
        return

    for key in ("metadata", "entities", "relationships"):
        if key not in db:
            rep.err(rel, f"missing top-level key '{key}'")

    entities = db.get("entities", [])
    if not isinstance(entities, list):
        rep.err(rel, "'entities' is not a list")
        return

    names_seen = set()
    n_no_canon = 0
    for i, e in enumerate(entities):
        cn = e.get("canonical_name")
        if not _is_str(cn):
            n_no_canon += 1
            continue
        key = (cn, e.get("type"))
        if key in names_seen:
            rep.warn(rel, f"duplicate merged entity {key} (merge incomplete)")
        names_seen.add(key)
        if "occurrence_count" not in e:
            rep.warn(rel, f"entity '{cn}' missing occurrence_count")
    if n_no_canon:
        rep.err(rel, f"{n_no_canon} entities missing canonical_name")

    meta = db.get("metadata", {})
    rep.stats["unified_entities"] = len(entities)
    rep.stats["unified_relationships"] = len(db.get("relationships", []))
    # Cross-check the inflated-vs-corrected cross-work figure if present
    spirits = [e for e in entities if e.get("type") == "spirit"]
    cross_work = sum(1 for s in spirits if s.get("cross_work"))
    rep.stats["spirits"] = len(spirits)
    if any("cross_work" in s for s in spirits):
        rep.stats["cross_work_spirits"] = cross_work
    if meta.get("total_merged_entities") not in (None, len(entities)):
        rep.warn(rel, f"metadata.total_merged_entities="
                      f"{meta.get('total_merged_entities')} != actual {len(entities)}")


# ── Reporting ────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Canonical distillation validator")
    ap.add_argument("--distilled-only", action="store_true")
    ap.add_argument("--unified-only", action="store_true")
    ap.add_argument("--distilled-dir", default=DISTILLED_DIR)
    ap.add_argument("--unified", default=UNIFIED_DB)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    rep = Report()
    if not args.unified_only:
        validate_distilled_tree(rep, args.distilled_dir)
    if not args.distilled_only:
        validate_unified(rep, args.unified)

    if args.json:
        print(json.dumps({
            "stats": rep.stats,
            "errors": rep.errors,
            "warnings": rep.warnings,
            "ok": len(rep.errors) == 0,
        }, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("DISTILLATION VALIDATION REPORT")
        print("=" * 60)
        for k, v in rep.stats.items():
            if k == "raw_type_counts":
                top = sorted(v.items(), key=lambda x: -x[1])[:8]
                print(f"  {k}: {len(v)} distinct non-canonical types; "
                      f"top: {top}")
            else:
                print(f"  {k}: {v}")
        print(f"\n  Hard errors: {len(rep.errors)}")
        for e in rep.errors[:40]:
            print(f"    ERROR  {e}")
        if len(rep.errors) > 40:
            print(f"    ... +{len(rep.errors) - 40} more")
        print(f"\n  Warnings: {len(rep.warnings)}")
        for w in rep.warnings[:20]:
            print(f"    WARN   {w}")
        if len(rep.warnings) > 20:
            print(f"    ... +{len(rep.warnings) - 20} more")
        print("\n  RESULT:", "PASS" if not rep.errors else "FAIL")

    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
