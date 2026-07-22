"""Audit summoning, experiment, and conjuration data from the unified database."""
import json
import os
from collections import Counter, defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.environ.get("MHR_UNIFIED_DB",
                          os.path.join(_ROOT, "data", "unified_entities.json"))
db = json.load(open(_DB_PATH, "r", encoding="utf-8"))
entities = db["entities"]
rels = db["relationships"]

def a(attrs, key):
    v = attrs.get(key, "")
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)

# 1. Rituals
rituals = [e for e in entities if e["type"] == "ritual"]
print(f"=== RITUALS: {len(rituals)} ===")
for r in sorted(rituals, key=lambda x: -x["occurrence_count"])[:25]:
    attrs = r.get("attributes", {})
    purpose = a(attrs, "purpose") or a(attrs, "function") or a(attrs, "type") or a(attrs, "role")
    print(f"  {r['display_name'][:55]:55s} x{r['occurrence_count']}  | {purpose[:60]}")

# 2. Incantations
incs = [e for e in entities if e["type"] == "incantation"]
print(f"\n=== INCANTATIONS: {len(incs)} ===")
for i in sorted(incs, key=lambda x: -x["occurrence_count"])[:15]:
    attrs = i.get("attributes", {})
    fn = a(attrs, "function") or a(attrs, "purpose") or a(attrs, "role")
    print(f"  {i['display_name'][:55]:55s} x{i['occurrence_count']}  | {fn[:55]}")

# 3. Relationship types
rel_types = Counter(r["type"] for r in rels)
print(f"\n=== RELATIONSHIP TYPES ({len(rel_types)}) ===")
for t, c in rel_types.most_common(30):
    print(f"  {t:45s} x{c}")

# 4. Conjuration / summoning keywords in rituals
print(f"\n=== CONJURING/SUMMONING RITUALS ===")
conjure_words = ["conjur", "summon", "invok", "invoc", "call", "appear", "evoc", "bind", "compel", "command"]
conjure_rituals = []
for r in rituals:
    blob = json.dumps(r).lower()
    hits = [w for w in conjure_words if w in blob]
    if hits:
        conjure_rituals.append((r, hits))
print(f"  {len(conjure_rituals)} rituals with conjuration/summoning content")
for r, hits in sorted(conjure_rituals, key=lambda x: -x[0]["occurrence_count"])[:20]:
    attrs = r.get("attributes", {})
    purpose = a(attrs, "purpose") or a(attrs, "function") or a(attrs, "role")
    print(f"  [{','.join(hits):20s}] {r['display_name'][:45]:45s} x{r['occurrence_count']}  | {purpose[:50]}")

# 5. Experiment numbering (Kieckhefer numbers experiments)
print(f"\n=== NUMBERED EXPERIMENTS ===")
exp_entities = [e for e in entities if "experiment" in e["display_name"].lower() or "no." in e["display_name"].lower()]
for e in sorted(exp_entities, key=lambda x: x["display_name"])[:30]:
    attrs = e.get("attributes", {})
    purpose = a(attrs, "purpose") or a(attrs, "function") or a(attrs, "role") or a(attrs, "type")
    print(f"  [{e['type']:12s}] {e['display_name'][:50]:50s} | {purpose[:55]}")

# 6. Detailed ritual attributes breakdown
print(f"\n=== RITUAL ATTRIBUTE KEYS ===")
all_keys = Counter()
for r in rituals:
    for k in r.get("attributes", {}).keys():
        all_keys[k] += 1
for k, c in all_keys.most_common(30):
    print(f"  {k:35s} x{c}")

# 7. Spirits with summoning method details
print(f"\n=== SPIRITS WITH SUMMONING DETAILS ===")
spirits = [e for e in entities if e["type"] == "spirit"]
for s in spirits:
    attrs = s.get("attributes", {})
    blob = json.dumps(attrs).lower()
    if any(w in blob for w in ["conjur", "summon", "circle", "invoc", "appear", "fumigat"]):
        method_bits = []
        for k, v in attrs.items():
            sv = str(v).lower()
            if any(w in sv for w in ["conjur", "circle", "fumig", "invoc", "appear", "candle", "inscri"]):
                method_bits.append(f"{k}={str(v)[:60]}")
        if method_bits:
            print(f"  {s['display_name'][:30]:30s} | {'; '.join(method_bits[:3])[:80]}")

# 8. Tools used in conjuration
print(f"\n=== RITUAL TOOLS ===")
tools = [e for e in entities if e["type"] == "tool"]
for t in sorted(tools, key=lambda x: -x["occurrence_count"])[:20]:
    attrs = t.get("attributes", {})
    use = a(attrs, "use") or a(attrs, "function") or a(attrs, "role") or a(attrs, "purpose")
    print(f"  {t['display_name'][:40]:40s} x{t['occurrence_count']}  | {use[:50]}")

# 9. Count entities by type
print(f"\n=== ENTITY TYPE COUNTS ===")
type_counts = Counter(e["type"] for e in entities)
for t, c in type_counts.most_common():
    print(f"  {t:20s} {c}")
