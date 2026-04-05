"""Analyze the full distillation output — entity counts, types, top spirits."""
import json
import os
import glob
from collections import Counter

BASE = r"E:\munich_handbook_research\data\distilled"

all_entities = []
all_relationships = []
parse_errors = []
source_stats = {}

for source_id in ["necro", "forbidden_rites_pdf", "worship_dead"]:
    src_dir = os.path.join(BASE, source_id)
    if not os.path.isdir(src_dir):
        continue
    
    files = sorted(glob.glob(os.path.join(src_dir, "distilled_*.json")))
    src_entities = 0
    src_relevant = 0
    src_errors = 0
    
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        
        if data.get("parse_error"):
            src_errors += 1
            # Try to extract from raw_extraction if available
            raw = data.get("raw_extraction", "")
            if raw:
                parse_errors.append({
                    "file": os.path.basename(f),
                    "source": source_id,
                    "raw_len": len(raw),
                })
            continue
        
        if data.get("has_relevant_content"):
            src_relevant += 1
        
        for e in data.get("entities", []):
            e["_source"] = source_id
            e["_chunk"] = os.path.basename(f)
            all_entities.append(e)
            src_entities += 1
        
        for r in data.get("relationships", []):
            r["_source"] = source_id
            all_relationships.append(r)
    
    source_stats[source_id] = {
        "files": len(files),
        "relevant": src_relevant,
        "entities": src_entities,
        "errors": src_errors,
    }

print("=" * 70)
print("DISTILLATION RESULTS SUMMARY")
print("=" * 70)
print()

# Per-source stats
for sid, stats in source_stats.items():
    print(f"  {sid:25s}: {stats['files']:3d} files, "
          f"{stats['relevant']:2d} relevant, "
          f"{stats['entities']:4d} entities, "
          f"{stats['errors']:2d} parse errors")

print(f"\n  {'TOTAL':25s}: {sum(s['files'] for s in source_stats.values()):3d} files, "
      f"{sum(s['relevant'] for s in source_stats.values()):2d} relevant, "
      f"{len(all_entities):4d} entities, "
      f"{len(parse_errors):2d} parse errors w/ raw data")

# Entity type breakdown
type_counts = Counter(e.get("type", "unknown") for e in all_entities)
print(f"\n{'='*70}")
print("ENTITY TYPES")
print("=" * 70)
for t, c in type_counts.most_common():
    print(f"  {t:25s}: {c:4d}")

# Top spirit names
spirits = [e for e in all_entities if e.get("type") == "spirit"]
spirit_names = Counter(e.get("name", "?") for e in spirits)
print(f"\n{'='*70}")
print(f"TOP NAMED SPIRITS ({len(spirits)} total)")
print("=" * 70)
for name, count in spirit_names.most_common(40):
    # Get attributes from first occurrence
    first = next(e for e in spirits if e.get("name") == name)
    attrs = first.get("attributes", {})
    if isinstance(attrs, dict):
        attr_str = ", ".join(f"{k}={v}" for k, v in list(attrs.items())[:3])
    elif isinstance(attrs, list):
        attr_str = ", ".join(str(a) for a in attrs[:3])
    else:
        attr_str = str(attrs)[:80]
    print(f"  {name:30s} x{count:2d}  | {attr_str[:60]}")

# Top ritual types
rituals = [e for e in all_entities if e.get("type") == "ritual"]
ritual_names = Counter(e.get("name", "?") for e in rituals)
print(f"\n{'='*70}")
print(f"TOP RITUALS ({len(rituals)} total)")
print("=" * 70)
for name, count in ritual_names.most_common(20):
    print(f"  {name:40s} x{count:2d}")

# Top ingredients
ingredients = [e for e in all_entities if e.get("type") == "ingredient"]
ingredient_names = Counter(e.get("name", "?") for e in ingredients)
print(f"\n{'='*70}")
print(f"TOP INGREDIENTS ({len(ingredients)} total)")
print("=" * 70)
for name, count in ingredient_names.most_common(20):
    print(f"  {name:40s} x{count:2d}")

# Relationship types
rel_types = Counter(r.get("type", "?") for r in all_relationships)
print(f"\n{'='*70}")
print(f"RELATIONSHIP TYPES ({len(all_relationships)} total)")
print("=" * 70)
for t, c in rel_types.most_common(15):
    print(f"  {t:35s}: {c:4d}")

# Parse errors with raw data
if parse_errors:
    print(f"\n{'='*70}")
    print(f"PARSE ERRORS WITH RAW DATA ({len(parse_errors)} recoverable)")
    print("=" * 70)
    total_raw = sum(p["raw_len"] for p in parse_errors)
    print(f"  Total raw text captured: {total_raw:,} chars")
    for p in parse_errors[:10]:
        print(f"  {p['source']}/{p['file']}: {p['raw_len']:,} chars of raw extraction")
