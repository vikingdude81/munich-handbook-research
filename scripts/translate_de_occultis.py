#!/usr/bin/env python3
"""
Translate De Occultis Literarum Notis chunks (Latin → English)
Uses LM Studio at http://192.168.50.150:1234 with nvidia/nemotron-3-nano-omni

Usage:
    python scripts/translate_de_occultis.py              # translate all chunks
    python scripts/translate_de_occultis.py --chunks 1,2,3   # specific chunks
    python scripts/translate_de_occultis.py --start 0 --end 5   # range
    python scripts/translate_de_occultis.py --resume    # skip already-translated chunks
"""

import argparse
import re
import sys
import time
from pathlib import Path
from openai import OpenAI

# ── Config ───────────────────────────────────────────────────────────────────
LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"
SOURCE_DIR = Path("data/sources/de_occultis")
OUTPUT_DIR = Path("data/sources/de_occultis_translated")

SYSTEM_PROMPT = (
    "You are an expert Latin scholar specializing in 16th-century scientific, "
    "cryptographic, and natural philosophy texts. "
    "Translate the provided Latin from Giambattista della Porta's "
    "De Occultis Literarum Notis (1592) into clear, accurate modern English. "
    "Preserve technical terminology (e.g. cipher names, plant/mineral names). "
    "Where OCR has garbled a word, make your best scholarly reconstruction. "
    "Output only the English translation — no commentary, no Latin repetition."
)

# Chunks to skip (cipher table pages — columnar data, not prose)
SKIP_CHUNKS = {6, 7}  # chunk_006 and chunk_007 are substitution alphabet tables

# Characters per API call (keep short for faster reasoning model throughput)
MAX_CHARS_PER_CALL = 2000

# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_ocr_text(text: str) -> str:
    """Light cleanup to improve translation quality."""
    # Remove page boundary markers but keep page numbers for reference
    text = re.sub(r"--- PAGE (\d+) ---", r"\n[p.\1]\n", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_passages(text: str, max_chars: int = MAX_CHARS_PER_CALL) -> list[str]:
    """Split text into passages at paragraph boundaries."""
    paragraphs = re.split(r"\n\n+", text)
    passages = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars and current:
            passages.append(current.strip())
            current = para
        else:
            current = (current + "\n\n" + para) if current else para
    if current.strip():
        passages.append(current.strip())
    return passages


def translate_passage(client: OpenAI, passage: str, chunk_num: int, passage_num: int) -> str:
    """Translate a single passage, with retry on failure."""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Translate this passage:\n\n{passage}"},
                    # Pre-fill assistant turn to bypass reasoning-only mode and
                    # force the model to emit the translation in the content field.
                    {"role": "assistant", "content": "Translation:\n\n"},
                ],
                max_tokens=800,
                temperature=0.1,
                timeout=180,
            )
            content = resp.choices[0].message.content or ""
            # Strip the pre-fill prefix if the model echoed it back
            content = content.strip()
            if content.lower().startswith("translation:"):
                content = content[len("translation:"):].strip()
            if not content:
                content = "[UNTRANSLATABLE — OCR QUALITY TOO LOW]"
            return content
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"    [attempt {attempt+1}/3] error: {e} — retrying in {wait}s")
            time.sleep(wait)
    return f"[TRANSLATION FAILED for chunk {chunk_num} passage {passage_num}]"


def translate_chunk(client: OpenAI, chunk_path: Path, output_path: Path) -> None:
    chunk_num = int(re.search(r"\d+", chunk_path.stem).group())
    print(f"\n-- Chunk {chunk_num:03d}: {chunk_path.name} --")

    raw = chunk_path.read_text(encoding="utf-8")
    text = clean_ocr_text(raw)
    passages = split_into_passages(text)

    print(f"   {len(text):,} chars -> {len(passages)} passages")

    translated_parts = []
    for i, passage in enumerate(passages, 1):
        print(f"   passage {i}/{len(passages)} ({len(passage)} chars)...", end=" ", flush=True)
        t = translate_passage(client, passage, chunk_num, i)
        translated_parts.append(t)
        print("done")

    output = "\n\n".join(translated_parts)
    output_path.write_text(output, encoding="utf-8")
    print(f"   -> saved {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Translate De Occultis chunks Latin→English")
    parser.add_argument("--chunks", help="Comma-separated chunk numbers, e.g. 1,2,5")
    parser.add_argument("--start", type=int, default=0, help="Start chunk (inclusive)")
    parser.add_argument("--end", type=int, default=27, help="End chunk (inclusive)")
    parser.add_argument("--resume", action="store_true", help="Skip chunks already translated")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine which chunk numbers to process
    if args.chunks:
        chunk_nums = [int(x.strip()) for x in args.chunks.split(",")]
    else:
        chunk_nums = list(range(args.start, args.end + 1))

    # Remove skipped chunks
    chunk_nums = [n for n in chunk_nums if n not in SKIP_CHUNKS]

    client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

    # Quick connectivity check
    try:
        models = [m.id for m in client.models.list().data]
        if MODEL not in models:
            print(f"WARNING: {MODEL} not found. Available: {models}")
    except Exception as e:
        print(f"ERROR: Cannot connect to LM Studio at {LM_STUDIO_URL}: {e}")
        sys.exit(1)

    print(f"Model: {MODEL}")
    print(f"Chunks to process: {chunk_nums}")
    print(f"Output: {OUTPUT_DIR}/")
    print(f"Skipping cipher-table chunks: {sorted(SKIP_CHUNKS)}")

    processed = 0
    skipped = 0

    for n in chunk_nums:
        chunk_path = SOURCE_DIR / f"chunk_{n:03d}.txt"
        output_path = OUTPUT_DIR / f"chunk_{n:03d}_en.txt"

        if not chunk_path.exists():
            print(f"\nWARNING: {chunk_path} not found — skipping")
            continue

        if args.resume and output_path.exists():
            print(f"chunk {n:03d}: already translated — skipping")
            skipped += 1
            continue

        translate_chunk(client, chunk_path, output_path)
        processed += 1

    print(f"\n{'='*50}")
    print(f"Done. Translated: {processed}  Skipped: {skipped}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
