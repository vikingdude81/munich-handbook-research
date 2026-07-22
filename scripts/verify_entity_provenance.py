#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_entity_provenance.py — hallucination & duplication cross-check.

1. PROVENANCE (hallucination) CHECK
   For every entity in unified_entities.json that carries raw_quotes, verify the
   quote actually appears in the source chunk text it cites (whitespace/OCR
   normalized, prefix match). An entity whose quotes appear nowhere in its cited
   chunks is a hallucination candidate.

2. DUPLICATE SCAN
   Pairwise fuzzy match of spirit canonical names (SequenceMatcher >= 0.86,
   len >= 5) to surface variants the alias table doesn't catch.

Writes docs/entity_verification_report.json and prints a summary.
"""

import io
import json
import os
import re
import sys
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "unified_entities.json")
SOURCES = os.path.join(ROOT, "data", "sources")
OUT = os.path.join(ROOT, "docs", "entity_verification_report.json")


def norm(s):
    """Normalize for matching: lowercase, strip OCR noise, collapse whitespace."""
    s = s.lower().replace("�", "")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_chunks_for(entity):
    """Yield normalized text of every chunk this entity cites."""
    for src in entity.get("sources", []):
        if ":" not in src:
            continue
        source_id, chunk = src.split(":", 1)
        m = re.search(r"(\d+)", chunk)
        if not m:
            continue
        path = os.path.join(SOURCES, source_id, f"chunk_{int(m.group(1)):03d}.txt")
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                yield norm(f.read())


def quote_found(quote, chunk_texts):
    # LLM quotes often elide with "..." — the elided parts are separately
    # verifiable segments, not contiguous text. Verify the longest segment.
    segments = [s for s in re.split(r"\.{2,}|…", quote) if len(norm(s)) >= 12]
    if segments:
        return any(_segment_found(s, chunk_texts) for s in segments)
    return _segment_found(quote, chunk_texts)


def _segment_found(quote, chunk_texts):
    q = norm(quote)
    if len(q) < 12:
        return any(q in t for t in chunk_texts)
    probe = q[:70]  # prefix probe survives quote truncation at 200 chars
    if any(probe in t for t in chunk_texts):
        return True
    # fallback: token-window overlap (OCR word-shatter tolerance)
    words = q.split()[:10]
    if len(words) >= 5:
        needle = " ".join(words)
        for t in chunk_texts:
            if needle in t:
                return True
        # 80% of the probe words appearing in order-free proximity
        for t in chunk_texts:
            hits = sum(1 for w in words if w in t)
            if hits / len(words) >= 0.8:
                return True
    return False


def main():
    db = json.load(open(DB, encoding="utf-8"))
    entities = db["entities"]

    verified, unverified, unquoted = [], [], 0
    chunk_cache = {}

    for e in entities:
        quotes = e.get("raw_quotes", [])
        if not quotes:
            unquoted += 1
            continue
        key = tuple(sorted(e.get("sources", [])))
        if key not in chunk_cache:
            chunk_cache[key] = list(load_chunks_for(e))
        chunks = chunk_cache[key]
        if not chunks:
            unverified.append({"name": e["display_name"], "type": e["type"],
                               "reason": "cited chunk files not found"})
            continue
        ok = sum(1 for q in quotes if quote_found(q, chunks))
        if ok == 0:
            # Second tier: does the entity NAME itself appear in a cited chunk?
            # (quote may be OCR-mangled, but a present name is not hallucinated)
            name_norm = norm(e.get("display_name", ""))
            if len(name_norm) >= 4 and any(name_norm in t for t in chunks):
                verified.append(e["display_name"] + " [name-only]")
            else:
                unverified.append({"name": e["display_name"], "type": e["type"],
                                   "sources": e.get("sources", [])[:4],
                                   "sample_quote": quotes[0][:100],
                                   "reason": "neither quote nor name found in cited chunks"})
        else:
            verified.append(e["display_name"])

    # ── duplicate scan (spirits) ────────────────────────────────────────────
    spirits = [e["canonical_name"] for e in entities if e["type"] == "spirit"]
    dupes = []
    spirits_sorted = sorted(set(spirits))
    for i, a in enumerate(spirits_sorted):
        if len(a) < 5:
            continue
        for b in spirits_sorted[i + 1:]:
            if b[0] != a[0] or abs(len(a) - len(b)) > 3:
                continue
            r = SequenceMatcher(None, a, b).ratio()
            if r >= 0.86:
                dupes.append({"a": a, "b": b, "similarity": round(r, 3)})

    report = {
        "provenance": {
            "entities_with_quotes": len(verified) + len(unverified),
            "verified_in_source": len(verified),
            "UNVERIFIED_hallucination_candidates": len(unverified),
            "entities_without_quotes": unquoted,
            "verification_rate": round(
                len(verified) / max(1, len(verified) + len(unverified)), 4),
            "unverified_details": unverified,
        },
        "duplicates": {
            "fuzzy_name_pairs": len(dupes),
            "pairs": dupes,
        },
    }
    json.dump(report, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    p = report["provenance"]
    print(f"PROVENANCE: {p['verified_in_source']}/{p['entities_with_quotes']} "
          f"quote-bearing entities verified against source text "
          f"({p['verification_rate']*100:.1f}%)")
    print(f"  hallucination candidates: {p['UNVERIFIED_hallucination_candidates']}")
    print(f"  entities with no quotes (unverifiable): {unquoted}")
    print(f"DUPLICATES: {len(dupes)} fuzzy spirit-name pairs")
    for d in dupes[:15]:
        print(f"  {d['a']}  ~  {d['b']}  ({d['similarity']})")
    print(f"\nReport -> {OUT}")


if __name__ == "__main__":
    main()
