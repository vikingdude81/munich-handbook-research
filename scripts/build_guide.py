"""
Generate a comprehensive Munich Handbook Spirit & Ritual Guide from the unified database.

Outputs: E:\munich_handbook_research\munich_handbook_guide.txt
"""
import json
import os
import textwrap
from collections import Counter, defaultdict

DB_PATH = r"E:\munich_handbook_research\data\unified_entities.json"
OUT_PATH = r"E:\munich_handbook_research\munich_handbook_guide.txt"

db = json.load(open(DB_PATH, "r", encoding="utf-8"))
entities = db["entities"]
relationships = db["relationships"]
summaries = db["chunk_summaries"]

# Helpers
def is_munich(entity):
    return any(s.split(":")[0] in ("necro", "forbidden_rites_pdf") for s in entity["sources"])

def get_sources(entity):
    return sorted(set(s.split(":")[0] for s in entity["sources"]))

def attr_str(attrs, key, default=""):
    v = attrs.get(key, default)
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)

def wrap(text, indent=4, width=90):
    return textwrap.fill(str(text), width=width, initial_indent=" "*indent, subsequent_indent=" "*indent)

def get_rels(canonical_name):
    return [r for r in relationships if r["from"] == canonical_name or r["to"] == canonical_name]

# Categorize entities
spirits = sorted([e for e in entities if e["type"] == "spirit" and is_munich(e)],
                 key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
rituals = sorted([e for e in entities if e["type"] == "ritual" and is_munich(e)],
                 key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
ingredients = sorted([e for e in entities if e["type"] == "ingredient" and is_munich(e)],
                     key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
tools = sorted([e for e in entities if e["type"] == "tool" and is_munich(e)],
               key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
incantations = sorted([e for e in entities if e["type"] == "incantation" and is_munich(e)],
                      key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
divine_names = sorted([e for e in entities if e["type"] == "divine_name" and is_munich(e)],
                      key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
deities = sorted([e for e in entities if e["type"] == "deity" and is_munich(e)],
                 key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
persons = sorted([e for e in entities if e["type"] == "person" and is_munich(e)],
                 key=lambda x: (-x["occurrence_count"], x["canonical_name"]))
concepts = sorted([e for e in entities if e["type"] == "concept" and is_munich(e)],
                  key=lambda x: (-x["occurrence_count"], x["canonical_name"]))

# Table D cross-reference
TABLE_D_SPIRITS = {
    "Superbus": "Pride (Superbia) — appears to practitioner at dawn",
    "Luxuriosus": "Lust (Luxuria) — appears as charming maiden of twelve years",
    "Avarus": "Avarice (Avaritia) — key motive of the necromancer",
    "Desidiosus": "Sloth (Acedia/Desidia)",
    "Gulosus": "Gluttony (Gula)",
    "Iracundus": "Wrath (Ira)",
    "Invidiosus": "Envy (Invidia)",
    "Astaroth": "Prince of the south; reveals treasures, gives love of women",
    "Berith": "Eastern king; spirits bound in obedience to him",
    "Belial": "Principal prince; foremost prince invoked with Astaroth and Paymon",
    "Beelzebub": "Prince of demons (Belzebub/Belzebuc variant)",
}

# Build relationship graph for spirit connections
spirit_graph = defaultdict(list)
for r in relationships:
    spirit_graph[r["from"]].append((r["to"], r["type"]))
    spirit_graph[r["to"]].append((r["from"], r["type"]))

# ================================================================
# GENERATE GUIDE
# ================================================================
lines = []
def out(text=""):
    lines.append(text)

out("=" * 90)
out("  THE MUNICH HANDBOOK OF NECROMANCY (CLM 849)")
out("  A Comprehensive Guide to Spirits, Rituals, and Magical Practice")
out("  Based on Richard Kieckhefer's 'Forbidden Rites' and Related Sources")
out("=" * 90)
out()
out(f"  Generated from {db['metadata']['total_raw_entities']} extracted entities")
out(f"  across {db['metadata']['total_chunk_summaries']} source text sections")
out(f"  Covering: Forbidden Rites (text), Forbidden Rites (PDF), Worship of the Dead")
out()

# ================================================================
# PART I: TABLE D CROSS-REFERENCE
# ================================================================
out()
out("=" * 90)
out("  PART I: KIECKHEFER'S TABLE D — THE NAMED SPIRITS")
out("=" * 90)
out()
out("  Kieckhefer's Table D classifies the named spirits appearing in the Munich")
out("  Handbook (CLM 849). Below are the 11 key spirits with all data extracted")
out("  from the source texts.")
out()

for spirit_name, description in TABLE_D_SPIRITS.items():
    # Find in database
    matches = [s for s in entities if s["type"] == "spirit" and (
        s["display_name"].lower() == spirit_name.lower() or
        s["canonical_name"].lower() == spirit_name.lower() or
        spirit_name.lower() in [v.lower() for v in s.get("name_variants", [])]
    )]
    
    out(f"  {'─' * 86}")
    out(f"  {spirit_name.upper()}")
    out(f"  Classification: {description}")
    
    if matches:
        s = matches[0]
        attrs = s.get("attributes", {})
        src_names = get_sources(s)
        
        out(f"  Status: FOUND — {s['occurrence_count']} occurrences across {len(s['sources'])} chunks")
        out(f"  Sources: {', '.join(src_names)}")
        
        if s.get("page_refs"):
            out(f"  Page References: {', '.join(s['page_refs'][:8])}")
        
        if s.get("name_variants"):
            out(f"  Name Variants: {', '.join(s['name_variants'])}")
        
        out(f"  Attributes:")
        for k, v in attrs.items():
            out(f"    {k}: {attr_str(attrs, k)}")
        
        if s.get("raw_quotes"):
            out(f"  Key Passages:")
            for q in s["raw_quotes"][:3]:
                out(wrap(f'"{q}"', indent=4, width=86))
        
        rels = get_rels(s["canonical_name"])
        if rels:
            out(f"  Relationships ({len(rels)}):")
            for r in rels[:8]:
                other = r["to"] if r["from"] == s["canonical_name"] else r["from"]
                direction = "-->" if r["from"] == s["canonical_name"] else "<--"
                out(f"    {direction} [{r['type']}] {other}")
    else:
        out(f"  Status: NOT FOUND in extracted data")
        out(f"  Note: May appear in unparsed chunks or under variant spelling")
    out()

# ================================================================
# PART II: COMPLETE SPIRIT CATALOGUE
# ================================================================
out()
out("=" * 90)
out("  PART II: COMPLETE SPIRIT CATALOGUE")
out(f"  {len(spirits)} unique spirits from the Munich Handbook sources")
out("=" * 90)
out()

# Tier 1: Major spirits (5+ occurrences)
major = [s for s in spirits if s["occurrence_count"] >= 5]
mid = [s for s in spirits if 2 <= s["occurrence_count"] < 5]
minor = [s for s in spirits if s["occurrence_count"] == 1]

out(f"  MAJOR SPIRITS ({len(major)} spirits with 5+ cross-references)")
out(f"  {'─' * 86}")
for s in major:
    attrs = s.get("attributes", {})
    rank = attr_str(attrs, "rank", attr_str(attrs, "role", ""))
    out(f"  {s['display_name']:30s} [{rank[:50]}]")
    out(f"    Occurrences: {s['occurrence_count']} | Pages: {', '.join(s.get('page_refs', [])[:5])}")
    if attrs.get("function"):
        out(f"    Function: {attr_str(attrs, 'function')[:80]}")
    if attrs.get("appearance") or attrs.get("form"):
        out(f"    Appearance: {attr_str(attrs, 'appearance', attr_str(attrs, 'form', ''))[:80]}")
    if attrs.get("direction"):
        out(f"    Direction: {attr_str(attrs, 'direction')}")
    if attrs.get("planet"):
        out(f"    Planet: {attr_str(attrs, 'planet')}")
    if attrs.get("day"):
        out(f"    Day: {attr_str(attrs, 'day')}")
    rels = get_rels(s["canonical_name"])
    if rels:
        co_spirits = [r for r in rels if r["type"] in ("co-invoked", "co-appearing_spirit", 
                      "co-conjured spirit", "co-conjured kings", "co-conjured spirit in invisibility ritual")]
        if co_spirits:
            others = [r["to"] if r["from"] == s["canonical_name"] else r["from"] for r in co_spirits]
            out(f"    Co-invoked with: {', '.join(others[:6])}")
    out()

out(f"\n  INTERMEDIATE SPIRITS ({len(mid)} spirits with 2-4 cross-references)")
out(f"  {'─' * 86}")
for s in mid:
    attrs = s.get("attributes", {})
    rank = attr_str(attrs, "rank", attr_str(attrs, "role", ""))
    pages = ", ".join(s.get("page_refs", [])[:3])
    out(f"  {s['display_name']:30s} x{s['occurrence_count']}  [{rank[:40]}]  pp. {pages}")

out(f"\n  MINOR/SINGLE-MENTION SPIRITS ({len(minor)} spirits)")
out(f"  {'─' * 86}")
# Group minor spirits alphabetically in columns
minor_names = [s["display_name"] for s in minor]
for i in range(0, len(minor_names), 3):
    row = minor_names[i:i+3]
    out(f"  {'  '.join(f'{n:28s}' for n in row)}")

# ================================================================
# PART III: DEMONIC HIERARCHY
# ================================================================
out()
out("=" * 90)
out("  PART III: DEMONIC HIERARCHY & ORGANIZATION")
out("=" * 90)
out()

# Extract hierarchy from relationships
hierarchy_rels = [r for r in relationships if r["type"] in (
    "commanded-by", "member-of", "binds", "binds_obligates", "conjures",
    "co-conjured kings", "prince_of", "ruler_of", "overlord of seven demons",
    "subordination", "superior-to", "commands")]
    
if hierarchy_rels:
    out("  COMMAND STRUCTURE (from extracted relationships):")
    out(f"  {'─' * 86}")
    for r in sorted(hierarchy_rels, key=lambda x: x["type"]):
        out(f"    {r['from']:25s} --[{r['type']:25s}]--> {r['to']}")
    out()

# Directional spirits
directional_spirits = [s for s in spirits if s.get("attributes", {}).get("direction")]
if directional_spirits:
    out("  DIRECTIONAL ASSIGNMENTS:")
    out(f"  {'─' * 86}")
    for s in directional_spirits:
        direction = attr_str(s["attributes"], "direction")
        out(f"    {direction:15s}: {s['display_name']}")
    out()

# Planetary / day assignments
planetary_spirits = [s for s in spirits if s.get("attributes", {}).get("planet") or s.get("attributes", {}).get("day")]
if planetary_spirits:
    out("  PLANETARY / DAY ASSIGNMENTS:")
    out(f"  {'─' * 86}")
    for s in sorted(planetary_spirits, key=lambda x: attr_str(x["attributes"], "day", "z")):
        attrs = s["attributes"]
        planet = attr_str(attrs, "planet", "")
        day = attr_str(attrs, "day", "")
        info = f"Planet: {planet}" if planet else ""
        if day:
            info += f"  Day: {day}" if info else f"Day: {day}"
        out(f"    {s['display_name']:20s} | {info}")
    out()

# ================================================================
# PART IV: RITUALS & EXPERIMENTS
# ================================================================
out()
out("=" * 90)
out("  PART IV: RITUALS, EXPERIMENTS & PROCEDURES")
out(f"  {len(rituals)} unique rituals from the Munich Handbook sources")
out("=" * 90)
out()

for r in rituals[:50]:
    attrs = r.get("attributes", {})
    purpose = attr_str(attrs, "purpose", attr_str(attrs, "function", attr_str(attrs, "type", attr_str(attrs, "role", ""))))
    pages = ", ".join(r.get("page_refs", [])[:4])
    
    out(f"  {r['display_name']}")
    if purpose:
        out(f"    Purpose: {purpose[:80]}")
    if pages:
        out(f"    Pages: {pages}")
    if r.get("raw_quotes"):
        for q in r["raw_quotes"][:2]:
            out(wrap(f'"{q[:150]}"', indent=4, width=86))
    
    # Find connected spirits/ingredients
    r_rels = get_rels(r["canonical_name"])
    if r_rels:
        spirit_links = [(rel["from"] if rel["from"] != r["canonical_name"] else rel["to"]) 
                       for rel in r_rels]
        if spirit_links:
            out(f"    Connected to: {', '.join(spirit_links[:6])}")
    out()

# ================================================================
# PART V: RITUAL MATERIALS
# ================================================================
out()
out("=" * 90)
out("  PART V: RITUAL MATERIALS & INSTRUMENTS")
out("=" * 90)
out()

out(f"  INGREDIENTS ({len(ingredients)} unique)")
out(f"  {'─' * 86}")
# Group by usage
fumigations = [ig for ig in ingredients if "fumig" in json.dumps(ig.get("attributes", {})).lower() 
               or "suffumig" in json.dumps(ig.get("attributes", {})).lower()
               or "incense" in json.dumps(ig.get("attributes", {})).lower()]
sacrificial = [ig for ig in ingredients if "sacrific" in json.dumps(ig.get("attributes", {})).lower()
               or "blood" in ig["display_name"].lower()
               or "dove" in ig["display_name"].lower()]
inscriptions = [ig for ig in ingredients if "inscri" in json.dumps(ig.get("attributes", {})).lower()
                or "ink" in ig["display_name"].lower() or "write" in json.dumps(ig.get("attributes", {})).lower()]

if fumigations:
    out(f"\n  Fumigations/Incense ({len(fumigations)}):")
    for ig in fumigations:
        out(f"    {ig['display_name']:35s} x{ig['occurrence_count']}")

if sacrificial:
    out(f"\n  Sacrificial/Blood Materials ({len(sacrificial)}):")
    for ig in sacrificial:
        attrs = ig.get("attributes", {})
        use = attr_str(attrs, "use", attr_str(attrs, "role", attr_str(attrs, "function", "")))
        out(f"    {ig['display_name']:35s} x{ig['occurrence_count']}  | {use[:45]}")

if inscriptions:
    out(f"\n  Inscription Materials ({len(inscriptions)}):")
    for ig in inscriptions:
        attrs = ig.get("attributes", {})
        use = attr_str(attrs, "use", attr_str(attrs, "role", attr_str(attrs, "function", "")))
        out(f"    {ig['display_name']:35s} x{ig['occurrence_count']}  | {use[:45]}")

out(f"\n  All Other Ingredients:")
other_ing = [ig for ig in ingredients if ig not in fumigations and ig not in sacrificial and ig not in inscriptions]
for ig in other_ing:
    attrs = ig.get("attributes", {})
    use = attr_str(attrs, "use", attr_str(attrs, "role", attr_str(attrs, "function", "")))
    out(f"    {ig['display_name']:35s} x{ig['occurrence_count']}  | {use[:45]}")

out(f"\n\n  RITUAL TOOLS ({len(tools)} unique)")
out(f"  {'─' * 86}")
for t in tools:
    attrs = t.get("attributes", {})
    use = attr_str(attrs, "use", attr_str(attrs, "role", attr_str(attrs, "function", "")))
    pages = ", ".join(t.get("page_refs", [])[:3])
    out(f"    {t['display_name']:35s} x{t['occurrence_count']}  | {use[:40]}")
    if pages:
        out(f"      pp. {pages}")

# ================================================================
# PART VI: INCANTATIONS & DIVINE NAMES
# ================================================================
out()
out("=" * 90)
out("  PART VI: INCANTATIONS, DIVINE NAMES & CONJURATION FORMULAS")
out("=" * 90)
out()

out(f"  DIVINE NAMES ({len(divine_names)} unique)")
out(f"  {'─' * 86}")
for dn in divine_names:
    attrs = dn.get("attributes", {})
    function = attr_str(attrs, "function", attr_str(attrs, "role", ""))
    out(f"    {dn['display_name']:30s} x{dn['occurrence_count']}  | {function[:50]}")
    if dn.get("raw_quotes"):
        out(wrap(f'"{dn["raw_quotes"][0][:120]}"', indent=6, width=84))

out(f"\n  INCANTATIONS ({len(incantations)} unique)")
out(f"  {'─' * 86}")
for ic in incantations:
    attrs = ic.get("attributes", {})
    pages = ", ".join(ic.get("page_refs", [])[:3])
    out(f"    {ic['display_name']}")
    if pages:
        out(f"      Pages: {pages}")
    if ic.get("raw_quotes"):
        for q in ic["raw_quotes"][:2]:
            out(wrap(f'"{q[:180]}"', indent=6, width=84))
    out()

# ================================================================
# PART VII: HISTORICAL PERSONS & CONTEXT
# ================================================================
out()
out("=" * 90)
out("  PART VII: HISTORICAL PERSONS & PRACTITIONERS")
out("=" * 90)
out()

for p in persons[:30]:
    attrs = p.get("attributes", {})
    role = attr_str(attrs, "role", attr_str(attrs, "function", ""))
    pages = ", ".join(p.get("page_refs", [])[:3])
    out(f"  {p['display_name']:35s} x{p['occurrence_count']}  | {role[:50]}")
    if pages:
        out(f"    pp. {pages}")

# ================================================================
# PART VIII: SPIRIT CO-OCCURRENCE NETWORK
# ================================================================
out()
out("=" * 90)
out("  PART VIII: SPIRIT CO-OCCURRENCE NETWORK")
out("=" * 90)
out()
out("  Spirits that appear together in conjurations, circles, or experiments:")
out()

co_rels = [r for r in relationships if r["type"] in (
    "co-invoked", "co-appearing_spirit", "co-conjured spirit",
    "co-conjured kings", "co-conjured spirit in invisibility ritual",
    "co-occurrence_in_conjuration", "co-occurrence_in_circle",
    "co-occurs_in_demon_list", "co-occurs_on_stone")]

# Build adjacency list
co_graph = defaultdict(set)
for r in co_rels:
    co_graph[r["from"]].add(r["to"])
    co_graph[r["to"]].add(r["from"])

for spirit_name in sorted(co_graph.keys(), key=lambda x: -len(co_graph[x])):
    companions = sorted(co_graph[spirit_name])
    if len(companions) >= 2:
        out(f"  {spirit_name:25s} appears with: {', '.join(companions)}")

# ================================================================
# PART IX: SOURCE CHAPTER SUMMARIES
# ================================================================
out()
out("=" * 90)
out("  PART IX: SOURCE TEXT SUMMARIES")
out("=" * 90)
out()

for summary in sorted(summaries, key=lambda x: (x["source_id"], str(x["chunk_id"]))):
    out(f"  [{summary['source_id']} chunk {summary['chunk_id']}]")
    out(wrap(summary["summary"], indent=4, width=86))
    if summary.get("key_passages"):
        out(f"    Key passages:")
        for kp in summary["key_passages"][:3]:
            out(wrap(f'"{kp[:150]}"', indent=6, width=84))
    out()

# ================================================================
# STATISTICS
# ================================================================
out()
out("=" * 90)
out("  APPENDIX: DATABASE STATISTICS")
out("=" * 90)
out()
out(f"  Total raw entities extracted:  {db['metadata']['total_raw_entities']}")
out(f"  Unique entities after merge:   {db['metadata']['total_merged_entities']}")
out(f"  Total relationships:           {db['metadata']['total_relationships']}")
out(f"  Chunk summaries:               {db['metadata']['total_chunk_summaries']}")
out()
out(f"  Munich Handbook spirits:       {len(spirits)}")
out(f"  Munich Handbook rituals:       {len(rituals)}")
out(f"  Munich Handbook ingredients:   {len(ingredients)}")
out(f"  Munich Handbook tools:         {len(tools)}")
out(f"  Munich Handbook incantations:  {len(incantations)}")
out(f"  Munich Handbook divine names:  {len(divine_names)}")
out(f"  Munich Handbook persons:       {len(persons)}")
out()
out(f"  Table D spirits found:         {sum(1 for n in TABLE_D_SPIRITS if any(s['display_name'].lower()==n.lower() or s['canonical_name'].lower()==n.lower() for s in entities if s['type']=='spirit'))} / {len(TABLE_D_SPIRITS)}")
out(f"  Multi-source spirits:          {len([s for s in spirits if len(get_sources(s)) > 1])}")
out()
out("=" * 90)
out("  END OF GUIDE")
out("=" * 90)

# Write guide
guide_text = "\n".join(lines)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(guide_text)

print(f"Guide written to {OUT_PATH}")
print(f"Size: {len(guide_text):,} chars / {os.path.getsize(OUT_PATH):,} bytes")
print(f"Sections: 9 parts + appendix")
print(f"Lines: {len(lines)}")
