"""
Retry parse errors from the first batch distillation run.

Phase 1: Try to re-parse the raw_extraction locally (no LLM call needed)
Phase 2: For files that can't be recovered, delete cache and re-run via LLM with 16K max_tokens

Uses the same goals as run_full_distill.py.
"""
import json
import os
import re
import sys
import time
import glob

sys.path.insert(0, os.path.dirname(__file__))

from tools.source_distill import DistillSourceChunk

PROJECT_DIR = r"E:\munich_handbook_research"
BASE = os.path.join(PROJECT_DIR, "data", "distilled")
LOG_FILE = os.path.join(PROJECT_DIR, "retry_log.txt")

GOALS = {
    "necro": (
        "Extract spirit names (especially from Kieckhefer's Table D), attributes, "
        "conjuration methods, ritual ingredients, circle descriptions, incantation texts, "
        "page references, and key passages from the Munich Handbook of necromancy (CLM 849) "
        "as studied by Richard Kieckhefer in Forbidden Rites. "
        "Focus on: named spirits and demons, their ranks and functions, "
        "materials used in rituals (blood, herbs, metals, animal parts), "
        "instructions for drawing circles or diagrams, Latin incantations, "
        "and any cross-references to other magical texts."
    ),
    "forbidden_rites_pdf": (
        "Extract spirit names, demonic hierarchies, conjuration procedures, "
        "ritual ingredients, protective circles, incantation formulas, "
        "and page references from Kieckhefer's Forbidden Rites PDF. "
        "Focus on named entities from the Munich Handbook (CLM 849), "
        "necromantic experiments, and medieval magical practices. "
        "Note any connections to other grimoire traditions."
    ),
    "worship_dead": (
        "Extract references to spirit communication, necromantic traditions, "
        "ancestor veneration practices, death rituals, named spirits or deities "
        "associated with the dead, ritual procedures, and historical connections "
        "to medieval European necromancy from this text on worship of the dead. "
        "Note cultural and historical context relevant to the Munich Handbook tradition."
    ),
}


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _repair_json(text):
    """Enhanced JSON repair — same logic as source_distill.py plus extra fixes."""
    s = text.strip()

    # Strip markdown fences
    if s.startswith("```"):
        s = s.split("\n", 1)[-1] if "\n" in s else s[3:]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
    if s.startswith("json"):
        s = s[4:].strip()

    # Fix set-literal attributes like {"some text"} → {"description": "some text"}
    s = re.sub(
        r'\{("(?:[^"\\]|\\.)*")\}',
        lambda m: '{"description": ' + m.group(1) + '}' if ':' not in m.group(1) else m.group(0),
        s,
    )

    # Remove trailing commas before } or ]
    s = re.sub(r',\s*([}\]])', r'\1', s)

    # Fix single-quoted strings → double-quoted
    # Only if there are no double quotes nearby (crude heuristic)
    # Skip this — too risky with embedded apostrophes in medieval text

    # Try parsing as-is
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Truncation recovery: count brackets and close any unclosed
    last_good = None
    depth_b = 0  # braces
    depth_s = 0  # square brackets
    in_string = False
    escape = False
    for i, c in enumerate(s):
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth_b += 1
        elif c == '}':
            depth_b -= 1
            if depth_b >= 0:
                last_good = i
        elif c == '[':
            depth_s += 1
        elif c == ']':
            depth_s -= 1

    if depth_b > 0 or depth_s > 0:
        if last_good and last_good > len(s) // 2:
            s = s[:last_good + 1]
            s = re.sub(r',\s*$', '', s)
            opens_b = s.count('{') - s.count('}')
            opens_s = s.count('[') - s.count(']')
            s += ']' * max(0, opens_s)
            s += '}' * max(0, opens_b)

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Last resort: extract the outermost JSON object
    match = re.search(r'\{.*\}', s, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def find_parse_errors():
    """Find all distilled files with parse_error=True."""
    errors = []
    for src in ["necro", "forbidden_rites_pdf", "worship_dead"]:
        src_dir = os.path.join(BASE, src)
        if not os.path.isdir(src_dir):
            continue
        for f in sorted(glob.glob(os.path.join(src_dir, "distilled_*.json"))):
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("parse_error"):
                errors.append({
                    "source_id": src,
                    "chunk_id": data.get("chunk_id", -1),
                    "file": f,
                    "raw": data.get("raw_extraction", ""),
                    "raw_len": len(data.get("raw_extraction", "")),
                })
    return errors


def main():
    log("=" * 70)
    log("RETRY PARSE ERRORS — Enhanced repair + LLM re-run")
    log("=" * 70)

    errors = find_parse_errors()
    log(f"Found {len(errors)} parse error files")

    phase1_fixed = 0
    phase2_needed = []

    # ==============================
    # PHASE 1: LOCAL RE-PARSE
    # ==============================
    log("\n--- PHASE 1: Local re-parse of raw_extraction ---")
    for err in errors:
        raw = err["raw"]
        if not raw:
            log(f"  {err['source_id']} chunk {err['chunk_id']}: no raw data, needs LLM re-run")
            phase2_needed.append(err)
            continue

        parsed = _repair_json(raw)
        if parsed and isinstance(parsed, dict) and parsed.get("entities"):
            # Success! Overwrite the file with proper parsed data
            n_ent = len(parsed.get("entities", []))
            with open(err["file"], "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            log(f"  {err['source_id']} chunk {err['chunk_id']}: RECOVERED {n_ent} entities from raw text")
            phase1_fixed += 1
        else:
            phase2_needed.append(err)
            log(f"  {err['source_id']} chunk {err['chunk_id']}: raw text not recoverable ({err['raw_len']} chars)")

    log(f"\nPhase 1 results: {phase1_fixed} recovered locally, {len(phase2_needed)} need LLM re-run")

    # ==============================
    # PHASE 2: LLM RE-RUN
    # ==============================
    if not phase2_needed:
        log("\nNo chunks need LLM re-run. All done!")
        return

    log(f"\n--- PHASE 2: LLM re-run on {len(phase2_needed)} chunks (max_tokens=16384) ---")
    tool = DistillSourceChunk()

    phase2_fixed = 0
    phase2_errors = 0

    for i, err in enumerate(phase2_needed):
        src = err["source_id"]
        cid = err["chunk_id"]
        goal = GOALS.get(src, "Extract all relevant entities and relationships.")

        # Delete the cached parse-error file so distill tool will re-run
        if os.path.isfile(err["file"]):
            os.remove(err["file"])

        log(f"  [{i+1}/{len(phase2_needed)}] {src} chunk {cid}: sending to 120B...")
        t0 = time.time()
        try:
            result = tool.call(json.dumps({
                "project_dir": PROJECT_DIR,
                "source_id": src,
                "chunk_id": cid,
                "goal": goal,
            }))
            elapsed = time.time() - t0

            # Check result
            if os.path.isfile(err["file"]):
                with open(err["file"], "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("parse_error"):
                    # Still failed — try our enhanced repair on the new raw
                    new_raw = data.get("raw_extraction", "")
                    parsed = _repair_json(new_raw)
                    if parsed and isinstance(parsed, dict) and parsed.get("entities"):
                        n_ent = len(parsed.get("entities", []))
                        with open(err["file"], "w", encoding="utf-8") as f:
                            json.dump(parsed, f, indent=2, ensure_ascii=False)
                        log(f"    -> RECOVERED via enhanced repair: {n_ent} entities ({elapsed:.0f}s)")
                        phase2_fixed += 1
                    else:
                        phase2_errors += 1
                        log(f"    -> STILL FAILED after re-run ({elapsed:.0f}s), raw={len(new_raw)} chars")
                else:
                    n_ent = len(data.get("entities", []))
                    if n_ent > 0:
                        phase2_fixed += 1
                        log(f"    -> SUCCESS: {n_ent} entities ({elapsed:.0f}s)")
                    else:
                        log(f"    -> No relevant content ({elapsed:.0f}s)")
            else:
                phase2_errors += 1
                log(f"    -> ERROR: no file saved ({elapsed:.0f}s)")
        except Exception as e:
            elapsed = time.time() - t0
            phase2_errors += 1
            log(f"    -> EXCEPTION ({elapsed:.0f}s): {e}")

    # ==============================
    # SUMMARY
    # ==============================
    total_fixed = phase1_fixed + phase2_fixed
    log(f"\n{'='*70}")
    log(f"RETRY COMPLETE")
    log(f"  Phase 1 (local re-parse): {phase1_fixed} recovered")
    log(f"  Phase 2 (LLM re-run):     {phase2_fixed} recovered, {phase2_errors} still failing")
    log(f"  Total recovered:           {total_fixed} / {len(errors)}")
    log(f"{'='*70}")


if __name__ == "__main__":
    main()
