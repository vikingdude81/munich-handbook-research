"""Merge distilled goetia (Lemegeton, Mathers 1904) into data/unified_entities.json.

Doctrine (AGENTS.md):
- Exact name match (canonical or variant) -> fold as new attestation.
- No match -> new entity, marked goetia_exclusive in attributes.
- Fuzzy near-matches are NOT auto-merged; they are reported as doublet
  candidates for human review (NEEDS_VERIFICATION discipline).
- cross_work recomputed from distinct_works (never chunk overlap).
- necro == forbidden_rites_pdf == kieckhefer_clm849 (never double-count).
"""
import json, glob, difflib, sys, datetime, collections

WORK = "goetia_lemegeton"
SRC = "goetia"
DB_PATH = "data/unified_entities.json"

db = json.load(open(DB_PATH, encoding="utf-8"))

# --- load goetia distillations ---
gents, grels, gsums = [], [], []
for f in sorted(glob.glob("data/distilled/goetia/distilled_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    cid = d["chunk_id"]
    for e in d.get("entities", []):
        e["_chunk"] = cid
        gents.append(e)
    for r in d.get("relationships", []) or []:
        grels.append(r)
    if d.get("summary"):
        gsums.append({"source_id": SRC, "chunk_id": cid, "summary": d["summary"]})

# --- name index over existing DB ---
index = {}
for e in db["entities"]:
    for n in [e["canonical_name"]] + list(e.get("name_variants", [])):
        index.setdefault(str(n).lower().strip(), []).append(e)

def norm_name(s):
    return str(s).lower().strip()

folded, newents, fuzzy = [], [], []
canonical_lookup = {}
for e in db["entities"]:
    canonical_lookup.setdefault(norm_name(e["canonical_name"]), e["canonical_name"])

def attr_list(target, k):
    """Return target.attributes[k] as a list, coercing legacy str values."""
    attrs = target.setdefault("attributes", {})
    v = attrs.get(k)
    if v is None:
        attrs[k] = lst = []
    elif isinstance(v, list):
        lst = v
    else:
        attrs[k] = lst = [v]
    return lst

def fold_into(target, ge):
    tag = f"{SRC}:chunk_{ge['_chunk']}"
    srcs = target.setdefault("sources", [])
    if tag not in srcs:
        srcs.append(tag)
    if WORK not in target.setdefault("distinct_works", []):
        target["distinct_works"].append(WORK)
    target["cross_work"] = len(target["distinct_works"]) > 1
    target["occurrence_count"] = target.get("occurrence_count", 1) + 1
    for k, v in (ge.get("attributes") or {}).items():
        if v in (None, "", []):
            continue
        lst = attr_list(target, str(k))
        if v not in lst:
            lst.append(v)
    pr = ge.get("page_ref")
    if pr and pr not in target.setdefault("page_refs", []):
        target["page_refs"].append(pr)
    rq = ge.get("raw_quote")
    if rq and rq not in target.setdefault("raw_quotes", []):
        target["raw_quotes"].append(rq)

for ge in gents:
    nm = norm_name(ge["name"])
    hits = index.get(nm, [])
    if hits:
        for t in hits:
            fold_into(t, ge)
        folded.append((ge["name"], [t["canonical_name"] for t in hits]))
        continue
    # fuzzy candidate check (report only, no merge)
    cand = difflib.get_close_matches(nm, list(canonical_lookup.keys()), n=3, cutoff=0.82)
    if cand:
        fuzzy.append((ge["name"], cand))
    alt = ge.get("attributes", {}).get("alternate_names")
    variants = [str(alt).strip()] if alt else []
    attrs = {str(k): [v] for k, v in (ge.get("attributes") or {}).items() if v not in (None, "", [])}
    attrs["goetia_exclusive"] = ["not attested in the seven prior source tracks under any exact name match (2026-10-27 merge); doublet review pending"]
    ne = {
        "canonical_name": nm,
        "display_name": ge["name"],
        "type": ge.get("type", "spirit"),
        "name_variants": variants,
        "attributes": attrs,
        "page_refs": [ge["page_ref"]] if ge.get("page_ref") else [],
        "raw_quotes": [ge["raw_quote"]] if ge.get("raw_quote") else [],
        "sources": [f"{SRC}:chunk_{ge['_chunk']}"],
        "distinct_works": [WORK],
        "cross_work": False,
        "occurrence_count": 1,
    }
    db["entities"].append(ne)
    newents.append(ge["name"])

# --- relationships (map to canonical names where possible) ---
rel_added = 0
existing_rel = {(r["from"], r["to"], r["type"]) for r in db["relationships"]}
for r in grels:
    frm = canonical_lookup.get(norm_name(r.get("from", "")), norm_name(r.get("from", "")))
    to = canonical_lookup.get(norm_name(r.get("to", "")), norm_name(r.get("to", "")))
    typ = norm_name(r.get("type", ""))
    key = (frm, to, typ)
    if frm and to and key not in existing_rel:
        db["relationships"].append({"from": frm, "to": to, "type": typ, "source": SRC})
        existing_rel.add(key)
        rel_added += 1

db["chunk_summaries"].extend(gsums)

# --- metadata ---
md = db["metadata"]
md["generated"] = "2026-10-27"
if SRC not in md["sources"]:
    md["sources"].append(SRC)
if WORK not in md["distinct_works"]:
    md["distinct_works"].append(WORK)
md["total_raw_entities"] = md.get("total_raw_entities", 0) + len(gents)
md["total_merged_entities"] = len(db["entities"])
md["total_relationships"] = len(db["relationships"])
md["total_chunk_summaries"] = len(db["chunk_summaries"])

json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# --- report ---
print(f"GOETIA entities in: {len(gents)} | folded into existing: {len(folded)} | new goetia_exclusive: {len(newents)}")
print("\n== ATTESTED IN PRIOR TRACKS (exact name) ==")
for n, t in folded:
    print(f"  {n:22s} -> {', '.join(sorted(set(t)))}")
print("\n== FUZZY DOUBLET CANDIDATES (NOT merged; review) ==")
for n, c in fuzzy:
    print(f"  {n:22s} ~ {', '.join(c)}")
print(f"\nrelationships added: {rel_added} | chunk summaries added: {len(gsums)}")
print(f"DB now: {md['total_merged_entities']} entities, {md['total_relationships']} rels, "
      f"{md['total_chunk_summaries']} summaries, {len(md['sources'])} source tracks, "
      f"{len(md['distinct_works'])} distinct works")

# --- Goetia vs Munich (kieckhefer_clm849) commander-tier 1:1 check ---
munich_names = {norm_name(e["canonical_name"]) for e in db["entities"]
                if "kieckhefer_clm849" in e.get("distinct_works", [])}
seq = [(e["attributes"].get("sequence_number"), e["name"]) for e in gents
       if e.get("attributes", {}).get("sequence_number")]
in_munich = [f"{s}:{n}" for s, n in sorted(seq, key=lambda x: int(x[0])) if norm_name(n) in munich_names]
print(f"\nGoetia 72-spirit roster present in Munich CLM 849 entity set (exact): {len(in_munich)}")
for x in in_munich:
    print("  ", x)
