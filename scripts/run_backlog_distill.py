#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-distill the 9 parse-error chunks through the configured reasoning model.

Deletes each parse_error placeholder so DistillSourceChunk's cache check
re-processes it, then invokes the tool directly. Run from the repo root.
Progress goes to stdout; safe to re-run (skips chunks that now parse clean).
"""

import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from tools.source_distill import DistillSourceChunk  # noqa: E402

GOAL = (
    "Extract spirit names, attributes, conjuration methods, rituals, "
    "ingredients, tools, and page references from this historical source text."
)

PENDING = [
    ("forbidden_rites_pdf", 6), ("forbidden_rites_pdf", 13),
    ("forbidden_rites_pdf", 14), ("forbidden_rites_pdf", 22),
    ("forbidden_rites_pdf", 24), ("forbidden_rites_pdf", 32),
    ("forbidden_rites_pdf", 37), ("necro", 27), ("worship_dead", 1),
]


def main():
    tool = DistillSourceChunk()
    ok, fail = 0, 0
    for src, ch in PENDING:
        path = os.path.join(ROOT, "data", "distilled", src, f"distilled_{ch:03d}.json")
        # Only clear genuine parse_error placeholders
        if os.path.isfile(path):
            try:
                existing = json.load(open(path, encoding="utf-8"))
                if not existing.get("parse_error"):
                    print(f"[skip] {src}/{ch}: already clean "
                          f"({len(existing.get('entities', []))} entities)")
                    ok += 1
                    continue
            except Exception:
                pass
            os.remove(path)

        print(f"[distill] {src} chunk {ch} ...", flush=True)
        tool.call(json.dumps({
            "project_dir": ROOT, "source_id": src, "chunk_id": ch, "goal": GOAL,
        }))
        try:
            result = json.load(open(path, encoding="utf-8"))
            if result.get("parse_error"):
                print(f"  -> STILL parse_error")
                fail += 1
            else:
                print(f"  -> OK: {len(result.get('entities', []))} entities")
                ok += 1
        except Exception as e:
            print(f"  -> ERROR reading result: {e}")
            fail += 1

    print(f"\nDone: {ok} ok, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
