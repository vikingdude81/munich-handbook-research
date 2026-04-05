"""Break down spirits and rituals by source, with Munich Handbook focus."""
import json
from collections import Counter, defaultdict

db = json.load(open(r"E:\munich_handbook_research\data\unified_entities.json", "r", encoding="utf-8"))

entities = db["entities"]
relationships = db["relationships"]

# ================================================================
# SPIRITS BY SOURCE
# ================================================================
spirits = [e for e in entities if e["type"] == "spirit"]

print("=" * 70)
print(f"SPIRIT BREAKDOWN — {len(spirits)} unique spirits total")
print("=" * 70)

# Categorize by which sources they appear in
necro_only = []
frpdf_only = []
worship_only = []
multi_source = []

for s in spirits:
    srcs = set(src.split(":")[0] for src in s["sources"])
    if srcs == {"necro"}:
        necro_only.append(s)
    elif srcs == {"forbidden_rites_pdf"}:
        frpdf_only.append(s)
    elif srcs == {"worship_dead"}:
        worship_only.append(s)
    else:
        multi_source.append(s)

# necro + forbidden_rites_pdf are BOTH about the Munich Handbook
munich_spirits = [s for s in spirits if any(
    src.split(":")[0] in ("necro", "forbidden_rites_pdf") for src in s["sources"]
)]

print(f"\n  Munich Handbook sources (necro + forbidden_rites_pdf): {len(munich_spirits)} spirits")
print(f"    - necro only:                {len(necro_only)}")
print(f"    - forbidden_rites_pdf only:  {len(frpdf_only)}")
print(f"    - In both Munich sources:    {len([s for s in spirits if {'necro','forbidden_rites_pdf'}.issubset(set(src.split(':')[0] for src in s['sources']))])}")
print(f"  worship_dead only:             {len(worship_only)}")
print(f"  Appear in multiple sources:    {len(multi_source)}")

# Top Munich spirits
print(f"\n{'='*70}")
print(f"TOP 40 MUNICH HANDBOOK SPIRITS (by occurrence count)")
print(f"{'='*70}")
for i, s in enumerate(sorted(munich_spirits, key=lambda x: -x["occurrence_count"])[:40]):
    srcs = sorted(set(src.split(":")[0] for src in s["sources"]))
    attrs = s.get("attributes", {})
    rank = attrs.get("rank", attrs.get("role", ""))
    if isinstance(rank, list):
        rank = rank[0]
    pages = ", ".join(s.get("page_refs", [])[:3])
    print(f"  {i+1:2d}. {s['display_name']:28s} x{s['occurrence_count']:2d}  "
          f"| {str(rank)[:35]:35s} | pp. {pages[:25]}")

# ================================================================
# RITUALS
# ================================================================
rituals = [e for e in entities if e["type"] == "ritual"]
print(f"\n{'='*70}")
print(f"RITUAL BREAKDOWN — {len(rituals)} unique rituals")
print(f"{'='*70}")

# Munich rituals
munich_rituals = [r for r in rituals if any(
    src.split(":")[0] in ("necro", "forbidden_rites_pdf") for src in r["sources"]
)]
print(f"\n  Munich Handbook rituals: {len(munich_rituals)}")

# Top rituals with details
print(f"\n  Top 30 rituals by detail:")
for i, r in enumerate(sorted(munich_rituals, key=lambda x: -x["occurrence_count"])[:30]):
    attrs = r.get("attributes", {})
    purpose = attrs.get("purpose", attrs.get("function", attrs.get("type", attrs.get("role", ""))))
    if isinstance(purpose, list):
        purpose = purpose[0]
    pages = ", ".join(r.get("page_refs", [])[:2])
    quotes = r.get("raw_quotes", [])
    quote_preview = quotes[0][:60] if quotes else ""
    print(f"  {i+1:2d}. {r['display_name']:40s} x{r['occurrence_count']:2d}")
    if purpose:
        print(f"      Purpose: {str(purpose)[:70]}")
    if pages:
        print(f"      Pages: {pages}")
    if quote_preview:
        print(f"      Quote: \"{quote_preview}...\"")

# ================================================================
# INGREDIENTS tied to rituals via relationships
# ================================================================
ingredients = [e for e in entities if e["type"] == "ingredient"]
tools = [e for e in entities if e["type"] == "tool"]

munich_ingredients = [ig for ig in ingredients if any(
    src.split(":")[0] in ("necro", "forbidden_rites_pdf") for src in ig["sources"]
)]
munich_tools = [t for t in tools if any(
    src.split(":")[0] in ("necro", "forbidden_rites_pdf") for src in t["sources"]
)]

print(f"\n{'='*70}")
print(f"RITUAL MATERIALS — Munich Handbook")
print(f"{'='*70}")
print(f"\n  Ingredients: {len(munich_ingredients)}")
for i, ig in enumerate(sorted(munich_ingredients, key=lambda x: -x["occurrence_count"])[:20]):
    attrs = ig.get("attributes", {})
    use = attrs.get("use", attrs.get("role", attrs.get("function", "")))
    if isinstance(use, list):
        use = use[0]
    print(f"    {ig['display_name']:35s} x{ig['occurrence_count']:2d}  | {str(use)[:50]}")

print(f"\n  Ritual Tools: {len(munich_tools)}")
for i, t in enumerate(sorted(munich_tools, key=lambda x: -x["occurrence_count"])[:20]):
    attrs = t.get("attributes", {})
    use = attrs.get("use", attrs.get("role", attrs.get("function", "")))
    if isinstance(use, list):
        use = use[0]
    print(f"    {t['display_name']:35s} x{t['occurrence_count']:2d}  | {str(use)[:50]}")

# ================================================================
# RITUAL-SPIRIT RELATIONSHIPS
# ================================================================
print(f"\n{'='*70}")
print(f"SPIRIT-RITUAL CONNECTIONS")
print(f"{'='*70}")

# Find relationships linking spirits to rituals/ingredients
spirit_names = {s["canonical_name"] for s in spirits}
ritual_names = {r["canonical_name"] for r in rituals}
ingredient_names = {ig["canonical_name"] for ig in ingredients}

spirit_ritual_rels = [r for r in relationships if 
    (r["from"] in spirit_names and r["to"] in ritual_names) or
    (r["to"] in spirit_names and r["from"] in ritual_names)]

spirit_ingredient_rels = [r for r in relationships if
    (r["from"] in spirit_names and r["to"] in ingredient_names) or
    (r["to"] in spirit_names and r["from"] in ingredient_names)]

print(f"\n  Spirit-Ritual links: {len(spirit_ritual_rels)}")
for r in spirit_ritual_rels[:15]:
    print(f"    {r['from']:25s} --[{r['type']}]--> {r['to']}")

print(f"\n  Spirit-Ingredient links: {len(spirit_ingredient_rels)}")
for r in spirit_ingredient_rels[:15]:
    print(f"    {r['from']:25s} --[{r['type']}]--> {r['to']}")

# ================================================================
# INCANTATIONS
# ================================================================
incantations = [e for e in entities if e["type"] == "incantation"]
munich_incantations = [ic for ic in incantations if any(
    src.split(":")[0] in ("necro", "forbidden_rites_pdf") for src in ic["sources"]
)]
print(f"\n{'='*70}")
print(f"INCANTATIONS — {len(munich_incantations)} from Munich Handbook")
print(f"{'='*70}")
for ic in sorted(munich_incantations, key=lambda x: -x["occurrence_count"])[:15]:
    quotes = ic.get("raw_quotes", [])
    q = quotes[0][:80] if quotes else ""
    pages = ", ".join(ic.get("page_refs", [])[:2])
    print(f"  {ic['display_name']:40s} x{ic['occurrence_count']:2d} | pp. {pages}")
    if q:
        print(f"    \"{q}...\"")
