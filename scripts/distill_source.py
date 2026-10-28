"""Distill all chunks of one source track through the configured reasoning model.

Modernized, parameterized version of run_full_distill.py (which still points at
the dead E:\ project root). Resumable: cached distilled_<id>.json files are kept,
parse-error caches are removed and redone.

Endpoint comes from config.py env overrides:
  MHR_REASONING_SERVER   (default LM Studio 192.168.50.150:1234; use
                          http://localhost:11434/v1 for Ollama)
  MHR_REASONING_MODEL_ID (Ollama: qwen3.5:122b)
  MHR_REASONING_NUM_CTX  (set e.g. 32768 for Ollama; 0 = server default)

Usage:
  python scripts/distill_source.py --id goetia
  python scripts/distill_source.py --id goetia --max-chunks 1   # smoke test
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.source_distill import DistillSourceChunk  # noqa: E402
import config  # noqa: E402

GOALS = {
    "goetia": (
        "Extract the 72 Goetia spirits and all ritual apparatus from the Mathers 1904 "
        "Lesser Key of Solomon. For EACH spirit capture: name (and alternate spellings), "
        "sequence number, rank/title (King, Duke, Prince, Marquis, President, Count, "
        "Countess, Knight), legions governed, planetary/planetary-hour association if "
        "present, form/appearance, offices/functions (what it gives or does), seal "
        "description, and the conjuration address formulas. Also extract: the Shemhamphorash, "
        "the magical circle, triangle, hexagram, pentagram, disc, vessel of brass, secret "
        "seal of Solomon, the call/general conjurations, and the classified rank list. "
        "Preserve page refs from the scan (PAGE n markers) and exact quotes."
    ),
}


def log_line(logfile, msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def count_entities(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("parse_error"):
            return -1
        return len(data.get("entities", []))
    except Exception:
        return -1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--id", required=True, help="source id (chunk dir name)")
    ap.add_argument("--goal", help="research goal; default: builtin per-source goal")
    ap.add_argument("--max-chunks", type=int, default=0,
                    help="limit chunks processed this run (0 = all)")
    args = ap.parse_args()

    goal = args.goal or GOALS.get(args.id)
    if not goal:
        sys.exit(f"No builtin goal for source '{args.id}' — pass --goal")

    src_dir = os.path.join(ROOT, "data", "sources", args.id)
    dist_dir = os.path.join(ROOT, "data", "distilled", args.id)
    os.makedirs(dist_dir, exist_ok=True)
    logfile = os.path.join(ROOT, "_meta", f"distill_{args.id}.log")

    log_line(logfile, f"=== DISTILL {args.id} | server={config.REASONING_SERVER} "
                      f"model={config.REASONING_MODEL_ID} "
                      f"num_ctx={getattr(config, 'REASONING_NUM_CTX', 0)} ===")

    chunks = sorted(f for f in os.listdir(src_dir)
                    if f.startswith("chunk_") and f.endswith(".txt"))
    tool = DistillSourceChunk()
    total_entities = relevant = parse_errors = skipped = done = 0
    t_all = time.time()

    for i, chunk_file in enumerate(chunks):
        if args.max_chunks and done >= args.max_chunks:
            break
        chunk_id = int(chunk_file.replace("chunk_", "").replace(".txt", ""))
        distill_file = os.path.join(dist_dir, f"distilled_{chunk_id:03d}.json")

        if os.path.isfile(distill_file):
            n = count_entities(distill_file)
            if n >= 0:
                total_entities += n
                relevant += (n > 0)
                skipped += 1
                log_line(logfile, f"  chunk {chunk_id}: CACHED ({n} entities)")
                continue
            os.remove(distill_file)
            log_line(logfile, f"  chunk {chunk_id}: bad cache removed, redoing")

        t0 = time.time()
        try:
            tool.call(json.dumps({
                "project_dir": ROOT,
                "source_id": args.id,
                "chunk_id": chunk_id,
                "goal": goal,
            }))
        except Exception as e:  # endpoint died mid-run; keep going chunk by chunk
            log_line(logfile, f"  chunk {chunk_id}: EXCEPTION {e} ({time.time()-t0:.0f}s)")
            continue
        elapsed = time.time() - t0
        done += 1

        if os.path.isfile(distill_file):
            n = count_entities(distill_file)
            if n < 0:
                parse_errors += 1
                log_line(logfile, f"  chunk {chunk_id}: PARSE ERROR ({elapsed:.0f}s)")
            else:
                total_entities += n
                relevant += (n > 0)
                log_line(logfile, f"  chunk {chunk_id}: OK ({n} entities, {elapsed:.0f}s)")
        else:
            parse_errors += 1
            log_line(logfile, f"  chunk {chunk_id}: NO OUTPUT ({elapsed:.0f}s)")

    log_line(logfile, f"=== DONE {args.id}: {total_entities} entities | "
                      f"{relevant} relevant | {parse_errors} errors | "
                      f"{skipped} cached | {(time.time()-t_all)/60:.1f} min ===")


if __name__ == "__main__":
    main()
