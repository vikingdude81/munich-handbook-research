"""Export a compact CLM 849 entity graph for the porta-cipher-wheel app.

Reads data/unified_entities.json, filters to entities tagged with the
kieckhefer_clm849 work, scores by richness, and writes a JS constant
to ../porta-cipher-wheel/munich_graph.js for the app's crossref tab.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "unified_entities.json")
DST = os.path.normpath(os.path.join(HERE, "..", "..", "porta-cipher-wheel", "munich_graph.js"))


def firststr(v):
    if isinstance(v, list):
        for s in v:
            if s:
                return s
        return ""
    return v or ""


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    es = [x for x in d["entities"] if "kieckhefer_clm849" in x.get("distinct_works", [])]

    def score(x):
        a = x.get("attributes", {})
        rich = sum(1 for k in ("rank", "function", "description", "appearance", "role") if firststr(a.get(k)))
        return x["occurrence_count"] * 2 + rich * 3 + (2 if x.get("cross_work") else 0)

    sel = sorted(es, key=score, reverse=True)[:140]
    sel = [x for x in sel if x["type"] not in ("unknown",)]
    names = set(x["canonical_name"] for x in sel)

    ents = []
    for x in sel:
        a = x.get("attributes", {})
        q = (x.get("raw_quotes") or [""])[0][:170]
        ents.append({
            "n": x["display_name"], "c": x["canonical_name"], "t": x["type"],
            "o": x["occurrence_count"],
            "w": [w.replace("kieckhefer_", "").replace("_lemegeton", "").replace("_1584", "").replace("_1909", "")
                  for w in x.get("distinct_works", [])],
            "rank": firststr(a.get("rank"))[:60],
            "fn": firststr(a.get("function"))[:150],
            "ap": firststr(a.get("appearance"))[:110],
            "q": q,
            "p": " / ".join(x.get("page_refs", [])[:2])[:70],
        })

    MUN_SOURCES = {"necro", "forbidden_rites_pdf", "worship_dead"}
    rels = []
    seen = set()

    def canon(nm):
        nm = nm.strip().lower()
        if nm in names:
            return nm
        for x in sel:
            if x["display_name"].lower() == nm or (x["canonical_name"] and nm in x["canonical_name"]):
                return x["canonical_name"]
        return None

    for r in d["relationships"]:
        if r.get("source") not in MUN_SOURCES:
            continue
        fc, tc = canon(r.get("from", "")), canon(r.get("to", ""))
        if not fc or not tc or fc == tc:
            continue
        key = (fc, tc, r.get("type"))
        if key in seen:
            continue
        seen.add(key)
        rels.append({"f": fc, "t": tc, "k": r.get("type", "?")})
        if len(rels) >= 200:
            break

    out = {"gen": "2026-11-02", "src": "unified_entities.json (kieckhefer_clm849)", "total_ents": len(es), "total_rels": len(rels), "ents": ents, "rels": rels}
    blob = "const MUNICH_GRAPH = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(blob)
    print(f"ents={len(ents)} rels={len(rels)} -> {DST} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
