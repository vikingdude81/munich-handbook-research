"""normalize_source_manifest.py — one-off (2026-10-27) manifest normalization, idempotent.

Repairs rot found by the modernized lint:
- legacy entries with status "ok" and dead H:\\ paths -> status "ingested",
  repo-relative paths into data/sources/original_pdfs/, chunk_count recorded
- missing entries added: discoverie, alchemy_mysticism, de_occultis,
  de_occultis_translated
- malleus_maleficarum / karl_marx corrected to status "analysis" (NOT part of the
  unified-DB 8 tracks; used for heresy/analysis corpus), consolidated chunks_dir
  and distilled_dir pointed at data/{sources,distilled}/malleus_marx/...
- goetia path made repo-relative
"""
import json, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAN = REPO / "data" / "sources" / "source_manifest.json"
OP = "data/sources/original_pdfs"

m = json.load(open(MAN, encoding="utf-8"))
by_id = {e["id"]: e for e in m["sources"]}

def chunkcount(rel):
    return len(list((REPO / rel).glob("chunk_*.txt"))) if (REPO / rel).is_dir() else 0

def setop(e, fname):
    e["path"] = f"{OP}/{fname}"

# --- legacy ingested tracks ---
ing = {
    "necro": ("NECRO.txt", "data/sources/necro"),
    "forbidden_rites_pdf": ("Forbidden Rites - A Necromancer's Manual of the Fifteenth Century (Magic in History) - Richard Kieckhefer (1).pdf", "data/sources/forbidden_rites_pdf"),
    "worship_dead": ("The_Worship_of_the_Dead_A_Rigorous_Inqui.pdf", "data/sources/worship_dead"),
    "ars_notoria": ("ars_notoria.pdf", "data/sources/ars_notoria"),
    "liber_juratus": ("Sworn Book of Honorius Liber - Juratus Honorii - Joseph Peterson.pdf", "data/sources/liber_juratus"),
    "alchemy_mysticism": ("Alchemy___Mysticism_-_Taschen__2003__text.pdf", "data/sources/alchemy_mysticism"),
}
for tid, (fname, cdir) in ing.items():
    e = by_id.setdefault(tid, {"id": tid})
    if e not in m["sources"]:
        m["sources"].append(e)
    e["status"] = "ingested"
    setop(e, fname)
    e["chunks_dir"] = cdir
    e["chunk_count"] = chunkcount(cdir)
    e.setdefault("title", tid)
    e.setdefault("notes", "")
    e["notes"] = (e["notes"] + " " if e["notes"] else "") + "manifest normalized 2026-10-27 (legacy entry)"

# discoverie: text fetched source, no staged binary
e = by_id.setdefault("discoverie", {"id": "discoverie"})
if e not in m["sources"]:
    m["sources"].append(e)
e.update({"status": "ingested",
          "title": "Scot, The Discoverie of Witchcraft (1584)",
          "chunks_dir": "data/sources/discoverie",
          "chunk_count": chunkcount("data/sources/discoverie"),
          "path": None,
          "notes": "public-domain text fetch (2026); original binary not staged; normalized 2026-10-27"})

# goetia path relative
g = by_id["goetia"]
g["path"] = f"{OP}/lesser_key_of_solomon_1904.pdf"
g["chunks_dir"] = "data/sources/goetia"
g["status"] = "ingested"

# --- analysis corpus ---
for tid, cdir in [("malleus_maleficarum", "data/sources/malleus_marx/malleus_maleficarum"),
                  ("karl_marx", "data/sources/malleus_marx/karl_marx")]:
    e = by_id[tid]
    e["status"] = "analysis"
    e["chunks_dir"] = cdir
    e["chunk_count"] = chunkcount(cdir)
    e["distilled_dir"] = "data/distilled/malleus_marx"
    e["notes"] = (e.get("notes", "") + " " if e.get("notes") else "") + \
        "not part of unified-DB 8 tracks; consolidated malleus_marx dirs; normalized 2026-10-27"
setop(by_id["malleus_maleficarum"], "The Malleus Maleficarum.pdf")
setop(by_id["karl_marx"], "selected-works-karl-marx.pdf")

for tid, cdir, note in [
    ("de_occultis", "data/sources/de_occultis", "hocr distillation experiment (scripts/distill_de_occultis.py); analysis corpus"),
    ("de_occultis_translated", "data/sources/de_occultis_translated", "translation pass feeding heresy/analysis docs; no distilled dir"),
]:
    e = by_id.setdefault(tid, {"id": tid})
    if e not in m["sources"]:
        m["sources"].append(e)
    e["status"] = "analysis"
    e["chunks_dir"] = cdir
    e["chunk_count"] = chunkcount(cdir)
    e.setdefault("notes", note)

# aurora: keep scanned_images, relative path
a = by_id["aurora_consurgens"]
setop(a, "AuroraConsurgenszrichZentralbibliothekMs.Rh.172.pdf")
a["notes"] = (a.get("notes", "") + " " if a.get("notes") else "") + "image-only scan; OCR decision pending (Phase 5)"

m.setdefault("schema_version", "1.2")
m["updated"] = "2026-10-27"

with open(MAN, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("manifest entries:", len(m["sources"]))
for e in m["sources"]:
    print(f"  {e['id']:22s} {e.get('status'):10s} chunks={e.get('chunk_count','-')}")
