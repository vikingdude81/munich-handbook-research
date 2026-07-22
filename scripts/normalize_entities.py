"""
Normalize and deduplicate all distilled entities into a unified database.

Steps:
1. Load all distilled JSON files (including retry recoveries)
2. Normalize entity types to a canonical set
3. Merge duplicate entities across chunks/sources
4. Build cross-reference index
5. Save unified database to E:/munich_handbook_research/data/unified_entities.json
"""
import json
import os
import re
import sys
import io
import glob
from collections import Counter, defaultdict

# Force UTF-8 stdout on Windows. LLM-generated relationship/type strings contain
# characters like '→' that crash the default cp1252 console — and because the
# crash happened during a diagnostic print BEFORE the save, the DB was never
# written on Windows at all.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Paths are resolved relative to the repo root (this file lives in scripts/).
# Previously hard-coded to E:\munich_handbook_research\... which only worked on
# the original research box.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("MHR_DISTILLED_DIR", os.path.join(_ROOT, "data", "distilled"))
OUT_DIR = os.environ.get("MHR_DATA_DIR", os.path.join(_ROOT, "data"))

# All sources currently present under data/distilled/. NOTE: `necro` and
# `forbidden_rites_pdf` are the SAME book (Kieckhefer, Clm 849) ingested twice;
# WORK_ID (below) collapses them so a book cannot cross-reference itself.
SOURCE_IDS = [
    "necro", "forbidden_rites_pdf", "worship_dead",
    "ars_notoria", "liber_juratus",
    # Pipeline-track sources (different chunk schema; adapted in load):
    "discoverie", "alchemy_mysticism",
]

# Pipeline-track sources use {description, source_ref} instead of
# {attributes.*, page_ref, raw_quote}; _adapt_pipeline_entity maps them.
PIPELINE_SOURCES = {"discoverie", "alchemy_mysticism"}

# Canonical WORK map — multiple source ingests can be the same underlying work.
WORK_ID = {
    "necro": "kieckhefer_clm849",
    "forbidden_rites_pdf": "kieckhefer_clm849",
    "worship_dead": "garnier_1909",   # modern secondary mythology, not a grimoire
    "ars_notoria": "ars_notoria",
    "liber_juratus": "liber_juratus",
    "discoverie": "scot_1584",        # early-modern primary (incl. Bk XV catalogue)
    "alchemy_mysticism": "taschen_2003",  # modern secondary art-history compendium
}


def _adapt_pipeline_entity(e):
    """Map the pipeline distill schema onto the unified entity schema."""
    if "description" in e and e["description"]:
        attrs = e.setdefault("attributes", {}) or {}
        if isinstance(attrs, dict):
            attrs.setdefault("description", e["description"])
            e["attributes"] = attrs
    if not e.get("page_ref") and e.get("source_ref"):
        e["page_ref"] = str(e["source_ref"])
    return e


def distinct_works(sources):
    """Canonical work ids spanned by a list of '<source>:chunk_N' strings."""
    out = set()
    for s in sources:
        prefix = s.split(":")[0] if ":" in s else s
        out.add(WORK_ID.get(prefix, prefix))
    return out


# ================================================================
# STEP 1: TYPE NORMALIZATION MAP
# ================================================================
# Map messy LLM types to canonical types
TYPE_MAP = {
    # Spirit variants
    "spirit": "spirit",
    "spirit_name": "spirit",
    "spiritual_name": "spirit",
    "spiritual_entity": "spirit",
    "spirit-medium": "spirit",
    "spirit/name on ring": "spirit",
    "spirit name (on parchment)": "spirit",
    "spirit name (conjuration)": "spirit",
    "spirit/incantation phrase": "spirit",
    "spirit|deity": "spirit",
    "spirit|person": "spirit",
    "spirit|event": "spirit",
    "spirit|race": "spirit",
    "spirit|giant": "spirit",
    "spirit|deified ancestor": "spirit",
    "spirit|deified race": "spirit",
    "deified spirit": "spirit",
    "person|spirit": "spirit",
    "person|deified spirit": "spirit",

    # Deity variants
    "deity": "deity",
    "deity|figure": "deity",
    "location|deity": "deity",

    # Ritual variants
    "ritual": "ritual",
    "ritual text": "ritual",
    "ritual diagram": "ritual",
    "ritual constraint": "ritual",
    "ritual gesture": "ritual",
    "ritual action": "ritual",
    "ritual|concept": "ritual",
    "ritual requirement": "ritual",
    "ritual timing": "ritual",
    "ritual symbol": "ritual",
    "ritual location": "ritual",
    "ritual procedure": "ritual",
    "ritual tradition": "ritual",
    "ritual verb/action": "ritual",
    "ritual participant": "ritual",
    "ritual specialist": "ritual",
    "ritual_text": "ritual",
    "ritual_structure": "ritual",
    "ritual_concept": "ritual",
    "ritual_state": "ritual",
    "ritual_movement": "ritual",
    "ritual|spirit communication": "ritual",
    "tool|ritual": "ritual",

    # Ingredient variants
    "ingredient": "ingredient",
    "ritual ingredient": "ingredient",
    "ritual_ingredient": "ingredient",
    "ingredient/ritual element": "ingredient",
    "ingredient/ritual substance": "ingredient",
    "ingredient/tool": "ingredient",
    "ritual ingredient/tool": "ingredient",

    # Tool variants
    "tool": "tool",
    "ritual tool": "tool",
    "ritual_tool": "tool",
    "ritual instrument": "tool",
    "tool/ingredient": "tool",
    "tool|ritual": "tool",

    # Person variants
    "person": "person",
    "person/group": "person",
    "person (legendary/historical)": "person",
    "person|spiritually influential figure": "person",
    "person|spiritually empowered figure": "person",
    "biblical_figure": "person",
    "saint": "person",
    "spiritual_practitioner": "person",
    "practitioner_group": "person",
    "ritual_agent": "person",
    "religious_order": "person",
    "spiritual_role": "person",

    # Incantation / formula
    "incantation": "incantation",
    "ritual incantation": "incantation",
    "prayer/incantation": "incantation",
    "scripture/incantation": "incantation",
    "scripture/prayer": "incantation",
    "spiritual_formula": "incantation",
    "ritual_formula": "incantation",

    # Spirit-type entities the LLM labelled by rank / nature / role.
    # Verified against actual entity names (e.g. angel=Michael/Raphael,
    # demon=Asmodeus/Satan, king=Maimon/Arcan, wind=Hebetel — all named spirits).
    "angel": "spirit",
    "archangel": "spirit",
    "ruling_angel": "spirit",
    "ruling angel": "spirit",
    "demon": "spirit",
    "king": "spirit",
    "servant": "spirit",
    "servant spirit": "spirit",
    "wind": "spirit",

    # Inscribed symbols / seals / figures (artifacts) and physical devices → tool
    "sigil": "tool",
    "seal": "tool",
    "device": "tool",

    # Ritual materials / substances → ingredient
    "material": "ingredient",
    "substance": "ingredient",

    # Abstract methods / illustrative references → concept
    "cipher_method": "concept",
    "method": "concept",
    "historical_example": "concept",

    # Groups of people → person
    "cultural group": "person",

    # Divine name variants
    "divine name": "divine_name",
    "divine name (used in binding)": "divine_name",
    "sacred name": "divine_name",
    "blessed name": "divine_name",

    # Location
    "location": "location",

    # Concept
    "concept": "concept",

    # Text/source reference
    "text": "text",
    "text reference": "text",
    "text/source": "text",
    "manuscript_reference": "text",
}


def normalize_type(raw_type):
    """Map a raw entity type to its canonical form."""
    if not raw_type:
        return "unknown"
    raw_lower = raw_type.strip().lower()
    # Direct lookup
    for key, val in TYPE_MAP.items():
        if key.lower() == raw_lower:
            return val
    # Fuzzy fallbacks
    if "spirit" in raw_lower:
        return "spirit"
    if "ritual" in raw_lower:
        return "ritual"
    if "ingredient" in raw_lower:
        return "ingredient"
    if "tool" in raw_lower or "instrument" in raw_lower:
        return "tool"
    if "person" in raw_lower or "saint" in raw_lower or "biblical" in raw_lower:
        return "person"
    if "incantation" in raw_lower or "prayer" in raw_lower or "formula" in raw_lower:
        return "incantation"
    if "divine" in raw_lower:
        return "divine_name"
    if "deity" in raw_lower:
        return "deity"
    return "unknown"


# ================================================================
# STEP 2: NAME NORMALIZATION
# ================================================================

def normalize_name(name):
    """Normalize entity names for dedup matching."""
    if not name:
        return ""
    s = name.strip()
    # Lowercase for matching
    s_lower = s.lower()
    # Remove common prefixes
    for prefix in ["the ", "a ", "an "]:
        if s_lower.startswith(prefix):
            s_lower = s_lower[len(prefix):]
    # Strip trailing punctuation
    s_lower = s_lower.rstrip(".,;:!?")
    # Collapse whitespace
    s_lower = re.sub(r'\s+', ' ', s_lower).strip()
    return s_lower


# Known variant mappings for key spirits
SPIRIT_ALIASES = {
    "sathan": "satan",
    "sathanas": "satan",
    "lucyfer": "lucifer",
    "astaroth": "astaroth",
    "ashtaroth": "astaroth",
    "belzebub": "beelzebub",
    "beel-zebub": "beelzebub",
    "beelzebuth": "beelzebub",
    "beliath": "belial",
    "belyal": "belial",
    "beliar": "belial",
    "paymon": "paimon",
    "oriens": "oriens",
    "orient": "oriens",
    "mirael": "mirael",
    "semiforas": "semiforas",
    "tetragramaton": "tetragrammaton",
    "tetragrammaton": "tetragrammaton",
    "emanuel": "emmanuel",
    "gabriell": "gabriel",
    "raphaell": "raphael",
    "michaell": "michael",
}


def canonical_name(name, entity_type):
    """Get canonical name, applying alias resolution for spirits/divine names."""
    norm = normalize_name(name)
    if entity_type in ("spirit", "deity", "divine_name"):
        return SPIRIT_ALIASES.get(norm, norm)
    return norm


# ================================================================
# STEP 3: LOAD AND PROCESS
# ================================================================

def load_all_entities():
    """Load all entities from all distilled files."""
    all_entities = []
    all_relationships = []
    chunk_summaries = []

    for source_id in SOURCE_IDS:
        src_dir = os.path.join(BASE, source_id)
        if not os.path.isdir(src_dir):
            continue

        for f in sorted(glob.glob(os.path.join(src_dir, "distilled_*.json"))):
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            if data.get("parse_error"):
                continue  # Skip unresolved parse errors

            chunk_id = data.get("chunk_id", -1)

            # Collect chunk summary
            if data.get("has_relevant_content") and data.get("summary"):
                chunk_summaries.append({
                    "source_id": source_id,
                    "chunk_id": chunk_id,
                    "summary": data["summary"],
                    "key_passages": data.get("key_passages", []),
                })

            for e in data.get("entities", []):
                if source_id in PIPELINE_SOURCES:
                    e = _adapt_pipeline_entity(e)
                e["_source"] = source_id
                e["_chunk_id"] = chunk_id
                all_entities.append(e)

            for r in data.get("relationships", []):
                r["_source"] = source_id
                r["_chunk_id"] = chunk_id
                all_relationships.append(r)

    return all_entities, all_relationships, chunk_summaries


def merge_entities(entities):
    """Merge duplicate entities, combining attributes and source references."""
    # Group by (canonical_name, canonical_type)
    groups = defaultdict(list)
    for e in entities:
        raw_type = e.get("type", "unknown")
        norm_type = normalize_type(raw_type)
        name = e.get("name", "?")
        canon = canonical_name(name, norm_type)
        groups[(canon, norm_type)].append(e)

    merged = []
    for (canon, norm_type), group in groups.items():
        # Pick the most common original name as display name
        name_counts = Counter(e.get("name", "?") for e in group)
        display_name = name_counts.most_common(1)[0][0]

        # Merge attributes
        all_attrs = {}
        for e in group:
            attrs = e.get("attributes", {})
            if isinstance(attrs, dict):
                for k, v in attrs.items():
                    if k not in all_attrs:
                        all_attrs[k] = v
                    elif isinstance(all_attrs[k], list):
                        if v not in all_attrs[k]:
                            all_attrs[k].append(v)
                    elif all_attrs[k] != v:
                        all_attrs[k] = [all_attrs[k], v]

        # Collect all page references
        page_refs = list(set(
            e.get("page_ref", "") for e in group if e.get("page_ref")
        ))

        # Collect all raw quotes (deduplicated, max 5)
        quotes = []
        seen_quotes = set()
        for e in group:
            q = e.get("raw_quote", "")
            if q and q not in seen_quotes:
                seen_quotes.add(q)
                quotes.append(q)
        quotes = quotes[:5]

        # Source appearances
        sources = list(set(
            f"{e['_source']}:chunk_{e['_chunk_id']}" for e in group
        ))

        # All name variants
        name_variants = sorted(set(e.get("name", "?") for e in group))

        works = sorted(distinct_works(sources))
        merged.append({
            "canonical_name": canon,
            "display_name": display_name,
            "type": norm_type,
            "name_variants": name_variants if len(name_variants) > 1 else [],
            "attributes": all_attrs,
            "page_refs": sorted(page_refs),
            "raw_quotes": quotes,
            "sources": sorted(sources),
            "distinct_works": works,         # canonical works (book-level provenance)
            "cross_work": len(works) >= 2,   # appears in 2+ DISTINCT works
            "occurrence_count": len(group),
        })

    # Sort by occurrence count descending, then name
    merged.sort(key=lambda e: (-e["occurrence_count"], e["canonical_name"]))
    return merged


def normalize_relationships(relationships, entities_by_name):
    """Normalize relationship endpoints to canonical names."""
    normalized = []
    seen = set()

    for r in relationships:
        from_name = canonical_name(r.get("from", ""), "spirit")
        to_name = canonical_name(r.get("to", ""), "spirit")
        rel_type = r.get("type", "unknown").strip().lower()

        # Normalize common relationship type variants
        rel_map = {
            "co-invoked spirit": "co-invoked",
            "co-occurs_with": "co-invoked",
            "co-occurs_in_conjuration": "co-invoked",
            "co-invoked": "co-invoked",
            "member-of": "member-of",
            "member_of": "member-of",
            "used_in": "used-in",
            "used in": "used-in",
            "invoked_by": "invoked-by",
            "invoked_in": "invoked-in",
            "inscribed_on": "inscribed-on",
            "inscribed-on-image": "inscribed-on",
            "inscribed_in": "inscribed-on",
            "binds": "binds",
            "binding_authority": "binds",
            "conjures": "conjures",
            "commanded_by": "commanded-by",
            "instance-of": "instance-of",
        }
        norm_rel = rel_map.get(rel_type, rel_type)

        key = (from_name, to_name, norm_rel)
        if key in seen:
            continue
        seen.add(key)

        normalized.append({
            "from": from_name,
            "to": to_name,
            "type": norm_rel,
            "source": r.get("_source", ""),
        })

    return sorted(normalized, key=lambda r: (r["type"], r["from"], r["to"]))


def main():
    print("Loading all distilled entities...")
    entities, relationships, chunk_summaries = load_all_entities()
    print(f"  Raw entities: {len(entities)}")
    print(f"  Raw relationships: {len(relationships)}")
    print(f"  Chunk summaries: {len(chunk_summaries)}")

    # Type distribution before normalization
    raw_types = Counter(e.get("type", "unknown") for e in entities)
    print(f"\n  Raw entity types: {len(raw_types)} distinct")

    # Normalize and merge
    print("\nNormalizing and merging entities...")
    merged = merge_entities(entities)
    print(f"  Merged entities: {len(merged)} (from {len(entities)} raw)")

    # Type distribution after normalization
    norm_types = Counter(e["type"] for e in merged)
    print(f"\n  Normalized type distribution:")
    for t, c in norm_types.most_common():
        print(f"    {t:15s}: {c:4d} unique entities")

    # Build name lookup for relationship normalization
    entities_by_name = {e["canonical_name"]: e for e in merged}

    # Normalize relationships
    print("\nNormalizing relationships...")
    norm_rels = normalize_relationships(relationships, entities_by_name)
    print(f"  Normalized relationships: {len(norm_rels)} (from {len(relationships)} raw)")

    rel_types = Counter(r["type"] for r in norm_rels)
    print(f"\n  Relationship type distribution:")
    for t, c in rel_types.most_common():
        print(f"    {t:20s}: {c:4d}")

    # ================================================================
    # BUILD UNIFIED DATABASE
    # ================================================================
    import datetime
    database = {
        "metadata": {
            "generated": datetime.date.today().isoformat(),
            "sources": SOURCE_IDS,
            "distinct_works": sorted(set(WORK_ID.values())),
            "total_raw_entities": len(entities),
            "total_merged_entities": len(merged),
            "total_relationships": len(norm_rels),
            "total_chunk_summaries": len(chunk_summaries),
        },
        "entities": merged,
        "relationships": norm_rels,
        "chunk_summaries": chunk_summaries,
    }

    # Save unified database
    db_path = os.path.join(OUT_DIR, "unified_entities.json")
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    print(f"\nSaved unified database to {db_path}")
    print(f"  File size: {os.path.getsize(db_path):,} bytes")

    # ================================================================
    # SPIRIT-SPECIFIC SUMMARY
    # ================================================================
    spirits = [e for e in merged if e["type"] == "spirit"]
    print(f"\n{'='*70}")
    print(f"SPIRIT DATABASE: {len(spirits)} unique spirits")
    print(f"{'='*70}")

    # Top spirits by occurrence
    print(f"\nTop 30 spirits by cross-reference count:")
    for i, s in enumerate(spirits[:30]):
        src_count = len(s["sources"])
        attr_keys = list(s["attributes"].keys())[:4]
        print(f"  {i+1:2d}. {s['display_name']:30s} "
              f"x{s['occurrence_count']:2d} in {src_count} chunks  "
              f"| {', '.join(attr_keys)}")

    # Spirits with page references
    page_spirits = [s for s in spirits if s["page_refs"]]
    print(f"\nSpirits with page references: {len(page_spirits)} / {len(spirits)}")

    # Spirits with raw quotes
    quoted_spirits = [s for s in spirits if s["raw_quotes"]]
    print(f"Spirits with direct quotes: {len(quoted_spirits)} / {len(spirits)}")

    # Spirits appearing in multiple DISTINCT WORKS (book-level, not chunk-level).
    # `necro`/`forbidden_rites_pdf` collapse to one work so the same book does
    # not count as a cross-reference (this is the fix for the inflated 266).
    multi_work = [s for s in spirits if s.get("cross_work")]
    print(f"Spirits appearing in multiple distinct works: {len(multi_work)}")
    for s in multi_work[:15]:
        print(f"  {s['display_name']:30s} in {', '.join(s['distinct_works'])}")


if __name__ == "__main__":
    main()
