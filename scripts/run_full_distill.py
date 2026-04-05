"""
Full batch distillation runner — processes ALL source chunks through the 120B Thinker.

Sources: necro (39), forbidden_rites_pdf (39), worship_dead (48) = 126 total
Skips already-distilled chunks (resumable).
Logs progress to console and to E:\munich_handbook_research\distill_log.txt
"""
import json
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from tools.source_distill import DistillSourceChunk, BatchDistillSource

PROJECT_DIR = r"E:\munich_handbook_research"
LOG_FILE = os.path.join(PROJECT_DIR, "distill_log.txt")

SOURCES = [
    {
        "id": "necro",
        "goal": (
            "Extract spirit names (especially from Kieckhefer's Table D), attributes, "
            "conjuration methods, ritual ingredients, circle descriptions, incantation texts, "
            "page references, and key passages from the Munich Handbook of necromancy (CLM 849) "
            "as studied by Richard Kieckhefer in Forbidden Rites. "
            "Focus on: named spirits and demons, their ranks and functions, "
            "materials used in rituals (blood, herbs, metals, animal parts), "
            "instructions for drawing circles or diagrams, Latin incantations, "
            "and any cross-references to other magical texts."
        ),
    },
    {
        "id": "forbidden_rites_pdf",
        "goal": (
            "Extract spirit names, demonic hierarchies, conjuration procedures, "
            "ritual ingredients, protective circles, incantation formulas, "
            "and page references from Kieckhefer's Forbidden Rites PDF. "
            "Focus on named entities from the Munich Handbook (CLM 849), "
            "necromantic experiments, and medieval magical practices. "
            "Note any connections to other grimoire traditions."
        ),
    },
    {
        "id": "worship_dead",
        "goal": (
            "Extract references to spirit communication, necromantic traditions, "
            "ancestor veneration practices, death rituals, named spirits or deities "
            "associated with the dead, ritual procedures, and historical connections "
            "to medieval European necromancy from this text on worship of the dead. "
            "Note cultural and historical context relevant to the Munich Handbook tradition."
        ),
    },
]


def log(msg):
    """Print and append to log file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def count_entities_in_file(path):
    """Count entities in a distilled JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("parse_error"):
            return -1  # parse error
        return len(data.get("entities", []))
    except Exception:
        return -1


def run_source(source_id, goal):
    """Distill all chunks of a single source."""
    tool = DistillSourceChunk()
    src_dir = os.path.join(PROJECT_DIR, "data", "sources", source_id)
    dist_dir = os.path.join(PROJECT_DIR, "data", "distilled", source_id)

    # Count chunks
    chunks = sorted([
        f for f in os.listdir(src_dir)
        if f.startswith("chunk_") and f.endswith(".txt")
    ])
    total = len(chunks)
    log(f"=== SOURCE: {source_id} — {total} chunks ===")

    total_entities = 0
    relevant_chunks = 0
    parse_errors = 0
    skipped = 0

    for i, chunk_file in enumerate(chunks):
        chunk_id = int(chunk_file.replace("chunk_", "").replace(".txt", ""))
        distill_file = os.path.join(dist_dir, f"distilled_{chunk_id:03d}.json")

        # Skip if already done
        if os.path.isfile(distill_file):
            n = count_entities_in_file(distill_file)
            if n >= 0:
                total_entities += n
                if n > 0:
                    relevant_chunks += 1
                skipped += 1
                log(f"  [{i+1}/{total}] chunk {chunk_id}: CACHED ({n} entities)")
                continue
            else:
                # Parse error in cache — redo it
                os.remove(distill_file)
                log(f"  [{i+1}/{total}] chunk {chunk_id}: removing bad cache, re-extracting...")

        # Run extraction
        t0 = time.time()
        try:
            result = tool.call(json.dumps({
                "project_dir": PROJECT_DIR,
                "source_id": source_id,
                "chunk_id": chunk_id,
                "goal": goal,
            }))
            elapsed = time.time() - t0

            # Check result
            if os.path.isfile(distill_file):
                n = count_entities_in_file(distill_file)
                if n < 0:
                    parse_errors += 1
                    log(f"  [{i+1}/{total}] chunk {chunk_id}: PARSE ERROR ({elapsed:.0f}s)")
                elif n == 0:
                    log(f"  [{i+1}/{total}] chunk {chunk_id}: no relevant content ({elapsed:.0f}s)")
                else:
                    total_entities += n
                    relevant_chunks += 1
                    log(f"  [{i+1}/{total}] chunk {chunk_id}: {n} entities ({elapsed:.0f}s)")
            else:
                log(f"  [{i+1}/{total}] chunk {chunk_id}: ERROR — no file saved ({elapsed:.0f}s)")
                log(f"    Result: {result[:200]}")

        except Exception as e:
            elapsed = time.time() - t0
            log(f"  [{i+1}/{total}] chunk {chunk_id}: EXCEPTION ({elapsed:.0f}s) — {e}")

    log(f"--- {source_id} DONE: {relevant_chunks} relevant chunks, "
        f"{total_entities} total entities, {parse_errors} parse errors, "
        f"{skipped} cached ---")
    return total_entities, relevant_chunks, parse_errors


def main():
    log("=" * 70)
    log("FULL BATCH DISTILLATION — Munich Handbook Research")
    log(f"Project: {PROJECT_DIR}")
    log("=" * 70)

    grand_total_entities = 0
    grand_total_relevant = 0
    grand_total_errors = 0
    t_start = time.time()

    for src in SOURCES:
        entities, relevant, errors = run_source(src["id"], src["goal"])
        grand_total_entities += entities
        grand_total_relevant += relevant
        grand_total_errors += errors

    elapsed_total = time.time() - t_start
    hours = int(elapsed_total // 3600)
    mins = int((elapsed_total % 3600) // 60)

    log("=" * 70)
    log(f"ALL SOURCES COMPLETE in {hours}h {mins}m")
    log(f"Total entities: {grand_total_entities}")
    log(f"Relevant chunks: {grand_total_relevant}")
    log(f"Parse errors: {grand_total_errors}")
    log("=" * 70)


if __name__ == "__main__":
    main()
