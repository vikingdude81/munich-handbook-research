"""Find all Table D references and the 11 seed spirits in the unified database."""
import json

db = json.load(open(r"E:\munich_handbook_research\data\unified_entities.json", "r", encoding="utf-8"))
spirits = [e for e in db["entities"] if e["type"] == "spirit"]

# Search for Table D mentions across all entity fields
def mentions_table(entity, table_letter):
    """Check if entity mentions a specific Kieckhefer table."""
    search_term = f"table {table_letter}".lower()
    # Check page_refs
    for p in entity.get("page_refs", []):
        if search_term in p.lower():
            return True
    # Check attributes
    attrs_str = json.dumps(entity.get("attributes", {})).lower()
    if search_term in attrs_str:
        return True
    # Check raw quotes
    for q in entity.get("raw_quotes", []):
        if search_term in q.lower():
            return True
    return False

# Find Table D spirits
table_d = [s for s in spirits if mentions_table(s, "d")]
table_c = [s for s in spirits if mentions_table(s, "c")]
table_b = [s for s in spirits if mentions_table(s, "b")]

print(f"Spirits referencing Table D: {len(table_d)}")
print(f"Spirits referencing Table C: {len(table_c)}")
print(f"Spirits referencing Table B: {len(table_b)}")

print(f"\n{'='*70}")
print("TABLE D SPIRITS (Kieckhefer's spirit classification)")
print("=" * 70)
for s in sorted(table_d, key=lambda x: -x["occurrence_count"]):
    print(f"\n  {s['display_name']}")
    print(f"    Occurrences: {s['occurrence_count']} across {len(s['sources'])} chunks")
    print(f"    Pages: {', '.join(s.get('page_refs', []))}")
    attrs = s.get("attributes", {})
    for k, v in attrs.items():
        print(f"    {k}: {v}")
    for q in s.get("raw_quotes", [])[:2]:
        print(f"    Quote: \"{q[:120]}\"")

# Known Table D spirits from Kieckhefer
# These are the 11 seed spirits from the conversation history
KNOWN_TABLE_D = [
    "Superbus", "Luxuriosus", "Avarus", "Desidiosus", "Gulosus",
    "Iracundus", "Invidiosus",  # 7 deadly sin demons
    "Astaroth", "Berith", "Belial", "Beelzebub",  # Major demons
]

print(f"\n{'='*70}")
print("KNOWN TABLE D SEED SPIRITS — Cross-reference")
print("=" * 70)
for name in KNOWN_TABLE_D:
    # Find in database (case-insensitive)
    matches = [s for s in spirits if s["display_name"].lower() == name.lower() 
               or s["canonical_name"].lower() == name.lower()
               or name.lower() in [v.lower() for v in s.get("name_variants", [])]]
    if matches:
        s = matches[0]
        src_names = sorted(set(src.split(":")[0] for src in s["sources"]))
        print(f"\n  {name} -> FOUND as '{s['display_name']}'")
        print(f"    Occurrences: {s['occurrence_count']} in {', '.join(src_names)}")
        print(f"    Pages: {', '.join(s.get('page_refs', [])[:5])}")
        attrs = s.get("attributes", {})
        for k, v in list(attrs.items())[:6]:
            val = str(v)[:80]
            print(f"    {k}: {val}")
        for q in s.get("raw_quotes", [])[:2]:
            print(f"    Quote: \"{q[:150]}\"")
        # Find relationships
        rels = [r for r in db["relationships"] 
                if r["from"] == s["canonical_name"] or r["to"] == s["canonical_name"]]
        if rels:
            print(f"    Relationships ({len(rels)}):")
            for r in rels[:5]:
                other = r["to"] if r["from"] == s["canonical_name"] else r["from"]
                print(f"      --[{r['type']}]--> {other}")
    else:
        print(f"\n  {name} -> NOT FOUND in database")

# Also search for the 7 deadly sin pattern
print(f"\n{'='*70}")
print("SEVEN DEADLY SIN DEMONS — Full search")
print("=" * 70)
sin_keywords = ["superb", "luxuri", "avar", "desidi", "gulos", "iracund", "invidi",
                "pride", "lust", "greed", "sloth", "glutton", "wrath", "envy"]
sin_spirits = []
for s in spirits:
    name_lower = s["display_name"].lower()
    attrs_str = json.dumps(s.get("attributes", {})).lower()
    quotes_str = " ".join(s.get("raw_quotes", [])).lower()
    all_text = f"{name_lower} {attrs_str} {quotes_str}"
    for kw in sin_keywords:
        if kw in all_text:
            sin_spirits.append(s)
            break

print(f"Spirits related to 7 deadly sins: {len(sin_spirits)}")
for s in sin_spirits:
    attrs = s.get("attributes", {})
    rank = attrs.get("rank", attrs.get("role", ""))
    appearance = attrs.get("appearance", attrs.get("form", ""))
    print(f"  {s['display_name']:25s} x{s['occurrence_count']:2d} | rank: {str(rank)[:40]}")
    if appearance:
        print(f"    appearance: {str(appearance)[:80]}")
