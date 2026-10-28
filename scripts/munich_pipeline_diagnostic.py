"""munich_pipeline_diagnostic.py — structural lint for the Munich Handbook corpus.

Modernized 2026-10-27: the original targeted dead E:\\ paths and April-era iteration
logs. This version enforces the invariants declared in AGENTS.md:
  - unified DB parses; metadata counts == actual counts
  - every entity has provenance; track prefixes are known; cross_work consistent
  - data/sources/ dirs and source_manifest.json agree (ingested -> chunks; staged -> binary)
  - quarantine dirs hold no chunk_*.txt and carry _QUARANTINE.md
  - README.md / RESEARCH_MANIFEST.md statistics match the DB
Exit code 1 on any FAIL; WARNs are informational.
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAILS, WARNS = [], []

def fail(msg): FAILS.append(msg)
def warn(msg): WARNS.append(msg)

# ---- 1. unified DB ----
db_path = REPO / "data" / "unified_entities.json"
try:
    db = json.load(open(db_path, encoding="utf-8"))
except Exception as e:
    fail(f"unified_entities.json unparseable: {e}")
    print("FAILS:", *FAILS, sep="\n  "); sys.exit(1)

md = db["metadata"]
ents, rels, sums = db["entities"], db["relationships"], db["chunk_summaries"]
for key, actual in [("total_merged_entities", len(ents)),
                    ("total_relationships", len(rels)),
                    ("total_chunk_summaries", len(sums))]:
    if md.get(key) != actual:
        fail(f"metadata.{key}={md.get(key)} != actual {actual}")

tracks = set(md["sources"])
prefixes = set()
for e in ents:
    srcs = e.get("sources") or []
    if not srcs:
        fail(f"entity '{e.get('canonical_name')}' has no sources")
    for s in srcs:
        prefixes.add(s.split(":")[0])
unknown = prefixes - tracks - {"heresy_revolution", "analysis"}
if unknown:
    fail(f"entity source prefixes not in metadata.sources: {sorted(unknown)}")
unused = tracks - prefixes
if unused:
    warn(f"metadata.sources tracks with no entities: {sorted(unused)}")

bad_cw = sum(1 for e in ents if e.get("cross_work") != (len(e.get("distinct_works", [])) > 1))
if bad_cw:
    fail(f"{bad_cw} entities with cross_work inconsistent with distinct_works")

dupe_canon = {}
for e in ents:
    dupe_canon[e["canonical_name"]] = dupe_canon.get(e["canonical_name"], 0) + 1
dupes = {k: v for k, v in dupe_canon.items() if v > 1}
if dupes:
    warn(f"{len(dupes)} canonical names have duplicate entries (legacy, review queue): "
         f"{sorted(dupes)[:12]}")

# ---- 2. sources dir vs manifest ----
man = json.load(open(REPO / "data" / "sources" / "source_manifest.json", encoding="utf-8"))
entries = man["sources"]
declared_chunk_dirs = set()
for e in entries:
    st, eid = e.get("status"), e["id"]
    if st in ("ingested", "analysis"):
        cdir = REPO / e.get("chunks_dir", f"data/sources/{eid}")
        chunks = list(cdir.glob("chunk_*.txt")) if cdir.exists() else []
        if not chunks:
            fail(f"manifest '{eid}' status={st} but no chunk_*.txt in {cdir.relative_to(REPO)}/")
        recs = len(e.get("chunk_records", []))
        if recs and recs != len(chunks):
            fail(f"manifest '{eid}': chunk_records={recs} != chunk files={len(chunks)}")
        if "chunk_count" in e and e["chunk_count"] != len(chunks):
            fail(f"manifest '{eid}': chunk_count={e['chunk_count']} != actual {len(chunks)}")
        if st == "ingested":
            ddir = REPO / e.get("distilled_dir", f"data/distilled/{eid}")
            if not any(ddir.glob("*.json")):
                warn(f"track '{eid}' ingested but no distilled outputs in {ddir.relative_to(REPO)}/")
        declared_chunk_dirs.add(cdir.resolve())
    elif st == "staged_chunked":
        # staged pre-distill: binaries + chunks exist, but no distilled output yet
        binpaths = ([e["path"]] if e.get("path") else []) + list(e.get("paths", []))
        if not binpaths:
            fail(f"staged_chunked '{eid}' has no path/paths")
        for p in binpaths:
            if not (REPO / p).exists():
                fail(f"staged_chunked '{eid}' missing binary: {p}")
        cdir = REPO / e.get("chunks_dir", f"data/sources/{eid}")
        chunks = list(cdir.glob("chunk_*.txt")) if cdir.exists() else []
        if not chunks:
            fail(f"manifest '{eid}' status=staged_chunked but no chunk_*.txt in {cdir.relative_to(REPO)}/")
        if "chunk_count" in e and e["chunk_count"] != len(chunks):
            fail(f"manifest '{eid}': chunk_count={e['chunk_count']} != actual {len(chunks)}")
        declared_chunk_dirs.add(cdir.resolve())
    elif st in ("staged", "scanned_images", "staged_ocr"):
        p = e.get("path")
        if not p:
            fail(f"staged/scanned '{eid}' has no path")
        elif not (REPO / p).exists():
            fail(f"staged '{eid}' missing binary: {p}")
    else:
        fail(f"manifest '{eid}': unrecognized status {st!r}")

# every directory under data/sources/ that contains chunk files must be declared
src_root = REPO / "data" / "sources"
for d in src_root.rglob("*"):
    if not d.is_dir():
        continue
    top = d.relative_to(src_root).parts[0]
    if top == "original_pdfs" or any(p.startswith("_quarantine") for p in d.relative_to(src_root).parts):
        continue
    if any(x.name.startswith("chunk_") and x.suffix == ".txt" for x in d.iterdir()):
        if d.resolve() not in declared_chunk_dirs:
            fail(f"chunk dir '{d.relative_to(REPO)}/' not declared by any manifest chunks_dir")

# ---- 3. quarantine hygiene ----
for q in (REPO / "data" / "sources").glob("_quarantine*"):
    if not (q / "_QUARANTINE.md").exists():
        fail(f"quarantine dir {q.name} lacks _QUARANTINE.md")
    for bad in q.glob("chunk_*.txt"):
        fail(f"ingestable-looking file inside quarantine: {q.name}/{bad.name}")

# ---- 4. doc statistics match DB ----
n_ent, n_rel, n_sum, n_tracks = len(ents), len(rels), len(sums), len(tracks)
def fmt(n): return f"{n:,}"
for doc in ["README.md", "RESEARCH_MANIFEST.md"]:
    text = (REPO / doc).read_text(encoding="utf-8")
    for label, needle in [("entities", fmt(n_ent)), ("relationships", fmt(n_rel)),
                          ("chunk summaries", fmt(n_sum))]:
        if needle not in text:
            fail(f"{doc} does not mention current {label} count {needle}")

print("=== MUNICH PIPELINE DIAGNOSTIC ===")
print(f"entities={n_ent} rels={n_rel} summaries={n_sum} tracks={n_tracks} "
      f"works={len(md['distinct_works'])}")
if WARNS:
    print("WARN:")
    for w in WARNS: print("  ~", w)
if FAILS:
    print("FAIL:")
    for f in FAILS: print("  X", f)
    sys.exit(1)
print("PASS — all structural invariants hold.")
