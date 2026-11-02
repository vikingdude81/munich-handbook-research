#!/usr/bin/env python3
"""Stage the CCRU Pandemonium web corpus as a Tier-C provenance-flagged source.

The source is NOT a historical grimoire: it is the Cybernetic Culture Research
Unit's fiction-theory accelerationist apparatus (ccru.fandom.com), including the
formal Pandemonium Matrix / Numogram lattice and the Vysparov 'Pandemonium
Concordance for the Book of Paths' rite strings. It is staged to test whether a
fully formalized demonology (zones 0-9 over Z/9, syzygies, currents, tractors,
gates, pole-pair-identified demons, machine-checkable rite path strings) can be
distilled with the existing chunk -> LLM distill -> consolidate pipeline, and to
serve as a ground-truth structure for validating distillation against the
historical Goetia track.

Provenance discipline: raw API JSON response bytes are saved under
data/sources/ccru_pandemonium/web_snapshots/; each entry records URL, fetch date
(UTC), and sha256 of the saved bytes. Corpus text = page source text as a human
reader sees it on the wiki page (wikitext body); wiki chrome/nav is not included.

Usage: python scripts/stage_ccru_pandemonium.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SRC_ID = "ccru_pandemonium"
OUT_DIR = ROOT / "data" / "sources" / SRC_ID
SNAP_DIR = OUT_DIR / "web_snapshots"
CHUNK_SIZE = 25_000
CHUNK_OVERLAP = 500
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"}

PAGES = [
    "Pandemonium_Matrix",
    "Pandemonium_concordance_for_the_Book_of_Paths",
    "Numogram",
    "Decimal",
    "Numeric_and_numerical",
    "Zone",
    "Time-Sorcery",
    "The_Book_of_Paths",
    "Tic(k)",
    "Architectonic_Order_of_the_Eschaton_(AOE)",
    "Spheres_and_Degrees_of_the_AOE",
]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Mirror scripts/ingest_new_sources.py: paragraph-boundary chunks, same size/overlap."""
    chunks = []
    pos, text_len = 0, len(text)
    while pos < text_len:
        end = min(pos + chunk_size, text_len)
        if end < text_len:
            search_start = max(end - 2000, pos + chunk_size // 2)
            cut = text.rfind("\n\n", search_start, end)
            if cut > pos:
                end = cut
        chunks.append((text[pos:end], pos, end))
        pos = end - overlap if end < text_len else text_len
    return chunks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    fetched_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    sections, provenance = [], []
    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    for page in PAGES:
        url = (f"https://ccru.fandom.com/api.php?action=parse&page={page}"
               "&prop=wikitext&format=json")
        try:
            r = requests.get(url, headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:  # noqa: BLE001
            print(f"  {page}: FETCH FAILED {e}")
            continue
        if "parse" not in data:
            print(f"  {page}: no parse in response (missing page?) — skipping")
            continue
        raw = r.content
        snap = SNAP_DIR / f"{page}.json"
        snap.write_bytes(raw)
        sha = hashlib.sha256(raw).hexdigest()
        wikitext = data["parse"]["wikitext"]["*"].strip()
        print(f"  {page}: {len(wikitext):,} chars")
        provenance.append({
            "page": page,
            "url": url,
            "page_url": f"https://ccru.fandom.com/wiki/{page}",
            "fetched_utc": fetched_at,
            "sha256": sha,
            "snapshot_file": str(snap),
        })
        sections.append(
            f"===== CCRU WIKI PAGE: {page} =====\n"
            f"Page URL: https://ccru.fandom.com/wiki/{page}\n"
            f"Fetched: {fetched_at} (CCRU fandom wiki, MediaWiki action=parse wikitext)\n"
            f"SHA256(raw response): {sha}\n\n{wikitext}\n"
        )
        time.sleep(2)

    if not sections:
        print("nothing fetched, aborting")
        return 1

    header = (
        "CCRU PANDEMONIUM / NUMOGRAM WEB CORPUS\n"
        "Source family: Cybernetic Culture Research Unit fandom wiki (ccru.fandom.com).\n"
        "TIER-C MODERN RETROFIT / FICTION-THEORY ACCELERATIONIST APPARATUS — not a "
        "historical grimoire. Texts below are wiki page bodies as of fetch date.\n\n"
    )
    full_text = header + "\n".join(sections)
    chunks = chunk_text(full_text)
    print(f"total {len(full_text):,} chars -> {len(chunks)} chunks")
    if args.dry_run:
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunk_records = []
    for idx, (ctext, start, end) in enumerate(chunks):
        fname = f"chunk_{idx:03d}.txt"
        (OUT_DIR / fname).write_text(ctext, encoding="utf-8")
        meta = {"chunk_id": idx, "source_id": SRC_ID, "start_char": start,
                "end_char": end, "chars": len(ctext),
                "contains_labels": [p for p in PAGES if p in ctext]}
        (OUT_DIR / f"chunk_{idx:03d}.meta.json").write_text(
            json.dumps(meta, indent=1), encoding="utf-8")
        chunk_records.append({"chunk_id": idx, "file": str(OUT_DIR / fname),
                              "start_char": start, "end_char": end})

    mpath = ROOT / "data" / "sources" / "source_manifest.json"
    m = json.loads(mpath.read_text(encoding="utf-8"))
    srcs = m["sources"] if isinstance(m, dict) else m
    srcs[:] = [s for s in srcs if s.get("id") != SRC_ID]  # idempotent re-stage
    entry = {
        "id": SRC_ID,
        "status": "staged_chunked",
        "label": "CCRU Pandemonium / Numogram wiki corpus (ccru.fandom.com)",
        "path": None,
        "description": (
            "TIER-C MODERN RETROFIT — fiction-theory accelerationist apparatus, NOT a "
            "historical grimoire. Cybernetic Culture Research Unit's Lemurian Time-Sorcery "
            "system: the Pandemonium demon lattice defined over the Numogram (ten zones 0-9, "
            "five syzygy pairs by 'zygonovism', currents as syzygy differences linking to "
            "tractor zones, Time-Circuit/Warp/Plex time-systems, gates by digital cumulation, "
            "demons as irreducible zone-distances identified by zone-net pairs (e.g. Lurgo "
            "1::0), pole-classified rite path strings (Vysparov Concordance), demon classes "
            "chronodemon/amphidemon/xenodemon, AOE phase/door/planet/spinal groupings). "
            "Staged as a fully formalized demonology with machine-checkable rite strings to "
            "stress-test the distill pipeline and serve as a ground-truth validation target "
            "for the historical Goetia track. Provenance per page: URL + fetch date + sha256 "
            "of saved API JSON below; page/line anchors do not exist (web source)."
        ),
        "mode": "web",
        "paths": [str(Path(p["snapshot_file"]).relative_to(ROOT)) for p in provenance],
        "web_snapshots": provenance,
        "total_chars": len(full_text),
        "total_chunks": len(chunks),
        "chunk_count": len(chunks),
        "chunk_dir": str(OUT_DIR),
        "chunks": chunk_records,
    }
    srcs.append(entry)
    mpath.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"manifest: staged {SRC_ID} with {len(chunks)} chunks, {len(provenance)} snapshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
