"""
source_prep.py — Pre-process source texts for the AI Command Center.

Extracts text from PDFs, chunks large text files, and writes them to the
project's data/ folder as numbered .txt files that the brain can read
one at a time with read_project_file.

Usage:
    python source_prep.py E:\\munich_handbook_research

This is a ONE-TIME preprocessing step.  Run it before starting a focus
session so the brain has digestible chunks to work with.
"""

import os
import sys
import json
import textwrap
import logging

log = logging.getLogger(__name__)

# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------
CHUNK_SIZE = 25000          # chars per chunk (~6K tokens at 4 chars/tok)
CHUNK_OVERLAP = 500         # overlap between consecutive chunks
SOURCE_FILES = [
    {
        "id": "necro",
        "path": r"H:\NECRO.txt",
        "type": "txt",
        "description": "Kieckhefer, Forbidden Rites — full text of Munich Handbook study",
    },
    {
        "id": "forbidden_rites_pdf",
        "path": r"H:\Forbidden Rites - A Necromancer's Manual of the Fifteenth Century (Magic in History) - Richard Kieckhefer (1).pdf",
        "type": "pdf",
        "description": "Kieckhefer, Forbidden Rites — PDF version (cross-reference)",
    },
    {
        "id": "worship_dead",
        "path": r"H:\The_Worship_of_the_Dead_A_Rigorous_Inqui.pdf",
        "type": "pdf",
        "description": "The Worship of the Dead — necromantic practice context",
    },
    {
        "id": "aurora_consurgens",
        "path": r"H:\AuroraConsurgenszrichZentralbibliothekMs.Rh.172.pdf",
        "type": "pdf_scanned",
        "description": "Aurora Consurgens (Zurich MS Rh.172) — scanned images, no extractable text",
    },
]


# ---------------------------------------------------------------
# TEXT EXTRACTION
# ---------------------------------------------------------------
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    import fitz
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append(f"--- PAGE {i+1} ---\n{text}")
    doc.close()
    return "\n\n".join(pages)


def read_text_file(txt_path: str) -> str:
    """Read a text file."""
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ---------------------------------------------------------------
# CHUNKING
# ---------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list:
    """
    Split text into overlapping chunks, breaking at paragraph boundaries
    when possible.

    Returns:
        List of (chunk_text, start_char, end_char) tuples
    """
    chunks = []
    pos = 0
    text_len = len(text)

    while pos < text_len:
        end = min(pos + chunk_size, text_len)

        # Try to break at a paragraph boundary (double newline)
        if end < text_len:
            # Search backward from `end` for a paragraph break
            search_start = max(end - 2000, pos + chunk_size // 2)
            break_pos = text.rfind("\n\n", search_start, end)
            if break_pos > pos:
                end = break_pos + 2  # include the double newline

        chunk = text[pos:end]
        chunks.append((chunk, pos, end))

        # Next chunk starts with overlap
        pos = end - overlap if end < text_len else text_len

    return chunks


# ---------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------
def prep_source(source_def: dict, output_dir: str) -> dict:
    """
    Process one source file: extract text, chunk it, write chunks.

    Returns:
        Manifest entry dict with chunk info.
    """
    src_id = source_def["id"]
    src_path = source_def["path"]
    src_type = source_def["type"]

    if not os.path.exists(src_path):
        log.warning("Source not found: %s", src_path)
        return {"id": src_id, "status": "missing", "path": src_path}

    if src_type == "pdf_scanned":
        log.info("Skipping scanned PDF (no extractable text): %s", src_path)
        return {
            "id": src_id,
            "status": "scanned_images",
            "path": src_path,
            "description": source_def.get("description", ""),
            "note": "This PDF contains scanned images only. OCR would be needed.",
        }

    # Extract text
    log.info("Extracting text from %s (%s) ...", src_id, src_type)
    if src_type == "pdf":
        text = extract_pdf_text(src_path)
    else:
        text = read_text_file(src_path)

    if not text.strip():
        log.warning("No text extracted from %s", src_path)
        return {"id": src_id, "status": "empty", "path": src_path}

    # Chunk it
    chunks = chunk_text(text)
    log.info("  %s: %d chars -> %d chunks of ~%d chars each",
             src_id, len(text), len(chunks), CHUNK_SIZE)

    # Write chunks
    chunk_dir = os.path.join(output_dir, src_id)
    os.makedirs(chunk_dir, exist_ok=True)

    chunk_manifests = []
    for i, (chunk_text_str, start, end) in enumerate(chunks):
        chunk_file = os.path.join(chunk_dir, f"chunk_{i:03d}.txt")
        # Header with metadata for the brain
        header = (
            f"SOURCE: {source_def['description']}\n"
            f"CHUNK: {i+1}/{len(chunks)}  |  CHARS: {start}-{end} of {len(text)}\n"
            f"{'='*60}\n\n"
        )
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(header + chunk_text_str)

        chunk_manifests.append({
            "chunk_id": i,
            "file": chunk_file,
            "start_char": start,
            "end_char": end,
            "chars": len(chunk_text_str),
        })

    return {
        "id": src_id,
        "status": "ok",
        "path": src_path,
        "description": source_def.get("description", ""),
        "total_chars": len(text),
        "total_chunks": len(chunks),
        "chunk_dir": chunk_dir,
        "chunks": chunk_manifests,
    }


def run_prep(project_dir: str):
    """Run the full source prep pipeline for a project."""
    data_dir = os.path.join(project_dir, "data", "sources")
    os.makedirs(data_dir, exist_ok=True)

    manifest = {
        "project": project_dir,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "sources": [],
    }

    for source in SOURCE_FILES:
        entry = prep_source(source, data_dir)
        manifest["sources"].append(entry)
        status = entry.get("status", "?")
        n_chunks = entry.get("total_chunks", 0)
        total = entry.get("total_chars", 0)
        print(f"  [{status:>6s}] {entry['id']:25s} — {total:>10,} chars, {n_chunks} chunks")

    # Write manifest
    manifest_path = os.path.join(data_dir, "source_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {manifest_path}")

    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <project_dir>")
        print(f"Example: python {sys.argv[0]} E:\\munich_handbook_research")
        sys.exit(1)

    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"ERROR: {project_dir} is not a directory")
        sys.exit(1)

    print(f"Preparing sources for: {project_dir}")
    print(f"Chunk size: {CHUNK_SIZE} chars, overlap: {CHUNK_OVERLAP}")
    print()
    run_prep(project_dir)
