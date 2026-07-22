#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
src/chunking.py — canonical source-text cleaning + token-aware chunking.

Unifies the two divergent chunkers that existed before:
  - source_prep.py        : PyMuPDF, 25k chars, paragraph-aware, no cleaning
  - ingest_heresy_*.py    : PyPDF2, 10k chars, line-based, no cleaning
…and fixes the issues the audit flagged:
  1. OCR/encoding garbage (replacement chars, hyphenated line-breaks, page
     markers) was being fed straight into the extraction prompt.
  2. Chunk-size was measured in chars with no token budget check.
  3. The verbose "SOURCE: … CHUNK: …" header was embedded in the text the model
     distilled, polluting extraction.

Use `clean_source_text()` before chunking, and `chunk_text()` to split. Keep
human-facing headers OUT of the distilled text — pass them as separate metadata.
"""

import re

# Rough token estimate without a tokenizer dependency. Real tokenizers (tiktoken)
# can be slotted in via `token_counter=` if available.
CHARS_PER_TOKEN = 4


# ── Cleaning ──────────────────────────────────────────────────────────────────
_PAGE_MARKER = re.compile(r"^-{2,}\s*PAGE\s+\d+\s*-{2,}\s*$", re.MULTILINE | re.IGNORECASE)
_PREP_HEADER = re.compile(r"^SOURCE:.*?\n(?:CHUNK:.*?\n)?=+\s*\n", re.DOTALL)
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")          # de-hyphenate words split across lines
_MULTI_BLANK = re.compile(r"\n{3,}")
_TRAILING_WS = re.compile(r"[ \t]+\n")


def clean_source_text(text: str, drop_replacement_chars: bool = True) -> str:
    """Normalize extracted source text before chunking/distillation."""
    if not text:
        return ""
    # Strip an embedded source_prep header if present
    text = _PREP_HEADER.sub("", text)
    # Remove page markers (they are ingestion noise, not content)
    text = _PAGE_MARKER.sub("", text)
    # Repair words hyphenated across a line break: "exam-\nple" -> "example"
    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    if drop_replacement_chars:
        text = text.replace("�", "")           # U+FFFD replacement char
    # Normalize whitespace
    text = _TRAILING_WS.sub("\n", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def estimate_tokens(text: str, token_counter=None) -> int:
    if token_counter is not None:
        return token_counter(text)
    return max(1, len(text) // CHARS_PER_TOKEN)


# ── Chunking ──────────────────────────────────────────────────────────────────
def chunk_text(text, max_tokens=1500, overlap_tokens=80, token_counter=None):
    """
    Split text into paragraph-aware, token-budgeted chunks.

    Returns a list of dicts:
        {"text", "start_char", "end_char", "tokens", "overlap_prefix_chars"}

    `overlap_prefix_chars` marks how many leading chars are carried over from the
    previous chunk, so downstream extraction can avoid re-counting entities that
    live only in the overlap region (the old char-overlap double-extracted them).
    """
    max_chars = max_tokens * CHARS_PER_TOKEN
    overlap_chars = overlap_tokens * CHARS_PER_TOKEN
    chunks = []
    pos = 0
    n = len(text)

    while pos < n:
        end = min(pos + max_chars, n)
        if end < n:
            # prefer a paragraph break in the back third of the window
            search_start = max(pos + max_chars // 2, end - max_chars // 3)
            brk = text.rfind("\n\n", search_start, end)
            if brk > pos:
                end = brk + 2
        chunk = text[pos:end]
        overlap_prefix = overlap_chars if pos > 0 else 0
        chunks.append({
            "text": chunk,
            "start_char": pos,
            "end_char": end,
            "tokens": estimate_tokens(chunk, token_counter),
            "overlap_prefix_chars": min(overlap_prefix, len(chunk)),
        })
        if end >= n:
            break
        pos = max(end - overlap_chars, pos + 1)
    return chunks


if __name__ == "__main__":
    sample = (
        "SOURCE: Some Book\nCHUNK: 1/3  |  CHARS: 0-100 of 999\n"
        "============================================================\n\n"
        "--- PAGE 2 ---\nThis is an exam-\nple of �garbled� text.\n\n\n\n"
        "Second paragraph here.\n--- PAGE 3 ---\nThird paragraph."
    )
    cleaned = clean_source_text(sample)
    print("CLEANED:\n" + cleaned)
    print("\nCHUNKS:")
    for c in chunk_text(cleaned, max_tokens=10, overlap_tokens=2):
        print(f"  [{c['start_char']}:{c['end_char']}] tok~{c['tokens']} "
              f"ovl={c['overlap_prefix_chars']}  {c['text']!r}")
