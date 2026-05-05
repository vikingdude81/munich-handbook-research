#!/usr/bin/env python3
"""
Distill De Occultis Literarum Notis (English translations) -> structured JSON.

Reads from:  data/sources/de_occultis_translated/chunk_XXX_en.txt
Writes to:   data/distilled/de_occultis/distilled_XXX.json

Model: nvidia/nemotron-3-nano-omni via LM Studio at http://192.168.50.150:1234

Usage:
    python scripts/distill_de_occultis.py              # all chunks
    python scripts/distill_de_occultis.py --chunks 1,2 # specific chunks
    python scripts/distill_de_occultis.py --resume     # skip already done
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from openai import OpenAI

LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"
SOURCE_DIR = Path("data/sources/de_occultis_translated")
OUTPUT_DIR = Path("data/distilled/de_occultis")
SOURCE_ID = "de_occultis"

SKIP_CHUNKS = {6, 7}

SYSTEM_PROMPT = (
    "You are a precise research extraction engine for 16th-century cryptographic texts. "
    "Output only valid, complete JSON. Never invent data not present in the source."
)

RESEARCH_GOAL = (
    "Extract structured knowledge from Della Porta's De Occultis Literarum Notis (1592), "
    "a treatise on secret writing, steganography, and cryptography. "
    "Focus on: cipher methods and techniques, materials for secret writing, carrier methods "
    "(pigeons, arrows), named persons, historical examples, encoding/decoding instructions, "
    "occult connections. Note chapter/book references when present."
)


def _extract_objects_from_array(text, array_name):
    """Depth-aware extraction of objects from a named JSON array (handles nested objects)."""
    match = re.search(r'"' + array_name + r'"\s*:\s*\[', text)
    if not match:
        return []
    pos = match.end()
    objects = []
    i = pos
    while i < len(text):
        if text[i] == "]":
            break
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        obj_start = i
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    obj_text = text[obj_start:i + 1]
                    obj_text = re.sub(r",\s*([}\]])", r"\1", obj_text)
                    try:
                        obj = json.loads(obj_text)
                        if "name" in obj:
                            objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    i += 1
                    break
            i += 1
        else:
            break
    return objects


def extract_json_robust(raw_text):
    text = raw_text.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    brace_start = text.find("{")
    if brace_start == -1:
        return None
    # Full parse attempt
    brace_end = text.rfind("}")
    if brace_end > brace_start:
        candidate = re.sub(r",\s*([}\]])", r"\1", text[brace_start:brace_end + 1])
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # Salvage entities from truncated output
    entities = _extract_objects_from_array(text, "entities")
    rels = _extract_objects_from_array(text, "relationships")
    summary_m = re.search(r'"summary"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
    if entities:
        return {
            "source_id": SOURCE_ID,
            "has_relevant_content": True,
            "summary": summary_m.group(1) if summary_m else "(output truncated)",
            "entities": entities,
            "relationships": rels,
            "_truncated": True,
        }
    return None


def distill_chunk(client, chunk_num, text):
    capped = text[:10000]
    prompt = (
        f"RESEARCH GOAL: {RESEARCH_GOAL}\n\n"
        f"SOURCE TEXT (De Occultis, chunk {chunk_num}, English):\n"
        f"{'='*60}\n{capped}\n{'='*60}\n\n"
        "Extract the 10 most important entities from the text.\n"
        "Entity types: cipher_method, material, person, concept, device, location, historical_example\n\n"
        "Output this JSON structure (no markdown, no extra text):\n"
        "{\n"
        f'  "source_id": "{SOURCE_ID}",\n'
        f'  "chunk_id": {chunk_num},\n'
        '  "has_relevant_content": true,\n'
        '  "summary": "2-3 sentence summary",\n'
        '  "entities": [\n'
        '    {"name": "...", "type": "...", "description": "under 100 chars", "page_ref": "Book X Ch Y or null", "quote": "short direct quote or null"}\n'
        '  ],\n'
        '  "relationships": [\n'
        '    {"from": "...", "to": "...", "rel": "used_by|example_of|derived_from"}\n'
        '  ]\n'
        "}\n\n"
        "RULES: Only extract what is stated. Keep all strings short. Output ONLY the JSON."
    )

    pre_fill = f'{{\n  "source_id": "{SOURCE_ID}",\n  "chunk_id": {chunk_num},\n'

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": pre_fill},
                ],
                max_tokens=8192,
                temperature=0.05,
                timeout=480,
            )
            raw = resp.choices[0].message.content or ""
            full = pre_fill + raw
            parsed = extract_json_robust(full)
            if parsed:
                parsed.setdefault("source_id", SOURCE_ID)
                parsed.setdefault("chunk_id", chunk_num)
                parsed.setdefault("entities", [])
                parsed.setdefault("relationships", [])
                parsed.setdefault("summary", "")
                return parsed
            print(f"    [attempt {attempt + 1}] parse failed")
            print(f"    raw (first 500): {raw[:500]}")
            time.sleep(3)
        except Exception as e:
            wait = 8 * (attempt + 1)
            print(f"    [attempt {attempt + 1}] error: {e} -- retry in {wait}s")
            time.sleep(wait)

    return {
        "source_id": SOURCE_ID,
        "chunk_id": chunk_num,
        "has_relevant_content": False,
        "parse_error": True,
        "entities": [],
        "relationships": [],
        "summary": "DISTILLATION FAILED",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=27)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.chunks:
        nums = [int(x.strip()) for x in args.chunks.split(",")]
    else:
        nums = list(range(args.start, args.end + 1))
    nums = [n for n in nums if n not in SKIP_CHUNKS]

    client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")
    try:
        available = [m.id for m in client.models.list().data]
        if MODEL not in available:
            print(f"WARNING: {MODEL} not found. Available: {available[:5]}")
    except Exception as e:
        print(f"ERROR: Cannot reach LM Studio: {e}")
        sys.exit(1)

    print(f"Model:  {MODEL}")
    print(f"Chunks: {nums}")
    print(f"Output: {OUTPUT_DIR}/")

    processed = skipped = errors = 0
    total_entities = 0

    for n in nums:
        src = SOURCE_DIR / f"chunk_{n:03d}_en.txt"
        out = OUTPUT_DIR / f"distilled_{n:03d}.json"

        if not src.exists():
            print(f"WARNING: {src} not found -- skipping")
            continue

        if args.resume and out.exists():
            try:
                existing = json.loads(out.read_text(encoding="utf-8"))
                if not existing.get("parse_error"):
                    print(f"chunk {n:03d}: done ({len(existing.get('entities', []))} ents) -- skip")
                    skipped += 1
                    continue
            except Exception:
                pass

        text = src.read_text(encoding="utf-8")
        print(f"\n-- Chunk {n:03d} ({len(text):,} chars) --", flush=True)

        result = distill_chunk(client, n, text)
        n_ents = len(result.get("entities", []))
        n_rels = len(result.get("relationships", []))

        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        if result.get("parse_error"):
            print(f"   FAILED  -> {out.name}")
            errors += 1
        elif result.get("_truncated"):
            print(f"   PARTIAL {n_ents} entities (truncated) -> {out.name}")
            total_entities += n_ents
            processed += 1
        else:
            print(f"   OK      {n_ents} entities, {n_rels} rels -> {out.name}")
            total_entities += n_ents
            processed += 1

    print(f"\n{'='*50}")
    print(f"Done.  Processed: {processed}  Skipped: {skipped}  Errors: {errors}")
    print(f"Total entities: {total_entities}")


if __name__ == "__main__":
    main()