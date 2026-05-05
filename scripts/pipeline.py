#!/usr/bin/env python3
"""
pipeline.py — Generalized 3-stage ingestion pipeline for historical texts.

Wraps the three stages used for De Occultis into a single config-driven tool:
  Stage 1 (ingest):    PDF → chunked raw text files
  Stage 2 (translate): Raw chunks → English translation (for non-English sources)
  Stage 3 (distill):   Translated chunks → structured JSON entities

To add a new source, add an entry to SOURCES below. No other code changes needed.

Usage:
    python scripts/pipeline.py status                   # show all sources + progress
    python scripts/pipeline.py run --source picatrix    # run all stages for a source
    python scripts/pipeline.py run --source picatrix --stage ingest
    python scripts/pipeline.py run --source picatrix --stage translate
    python scripts/pipeline.py run --source picatrix --stage distill
    python scripts/pipeline.py run --source picatrix --resume   # skip completed chunks
    python scripts/pipeline.py aggregate --source picatrix      # merge JSON -> CSV+JSON

Model: nvidia/nemotron-3-nano-omni via LM Studio at http://192.168.50.150:1234
"""

import argparse
import json
import re
import sys
import time
import csv
import io
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# ── Global config ──────────────────────────────────────────────────────────────
LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CHUNK_SIZE = 20_000
CHUNK_OVERLAP = 400
MAX_CHARS_PER_TRANSLATE = 2000
MAX_TOKENS_DISTILL = 6000
MAX_CHARS_PER_DISTILL = 10000

# ══════════════════════════════════════════════════════════════════════════════
# SOURCE REGISTRY
# Add new sources here. That's the only change needed to process a new text.
# ══════════════════════════════════════════════════════════════════════════════

SOURCES = {
    # ── Already processed ────────────────────────────────────────────────────
    "de_occultis": {
        "label": "Giambattista della Porta — De Occultis Literarum Notis (1592)",
        "pdf": r"c:\Users\akbon\Downloads\De Occultis Literarum Notis seu Artis.pdf",
        "mode": "ocr",              # 'ocr' or 'native' (native = embedded text)
        "language": "la",           # ISO 639-1: la=Latin, en=English, de=German, etc.
        "translate": True,          # True = run stage 2 (translation)
        "ocr_lang": "lat+eng",
        "skip_chunks": {6, 7},      # Substitution table pages — columnar, not prose
        "research_goal": (
            "Extract structured knowledge from Porta's De Occultis Literarum Notis (1592): "
            "cipher methods, steganographic techniques, materials, carrier methods, "
            "named persons, historical examples, and occult connections."
        ),
        "entity_types": ["cipher_method", "material", "device", "person",
                         "concept", "location", "historical_example"],
    },

    # ── Ready to process ─────────────────────────────────────────────────────
    "picatrix": {
        "label": "Picatrix — Ghayat al-Hakim (Arabic, c. 1000 CE; Latin trans. 13th c.)",
        "pdf": r"c:\Users\akbon\Downloads\picatrix.pdf",
        "mode": "native",
        "language": "la",
        "translate": True,
        "research_goal": (
            "Extract structured knowledge from the Picatrix (Ghayat al-Hakim), "
            "the most comprehensive medieval grimoire of astrological magic: "
            "planetary talismans, ritual procedures, material ingredients, "
            "spirit names, magical operations, astrological timing, and "
            "connections to Hermetic and Neoplatonic philosophy."
        ),
        "entity_types": ["spirit", "talisman", "material", "ritual", "person",
                         "concept", "astrology", "plant", "stone", "planet"],
    },

    "agrippa_occult": {
        "label": "Heinrich Cornelius Agrippa — De Occulta Philosophia (1531)",
        "pdf": r"c:\Users\akbon\Downloads\agrippa_occult_philosophy.pdf",
        "mode": "native",
        "language": "la",
        "translate": True,
        "research_goal": (
            "Extract structured knowledge from Agrippa's Three Books of Occult Philosophy: "
            "elemental magic, celestial magic, ceremonial magic; planetary intelligence "
            "tables, magic squares, angelic hierarchies, divine names (Shem HaMephorash), "
            "plant/stone/metal correspondences, and the theory of sympathetic magic."
        ),
        "entity_types": ["angel", "spirit", "divine_name", "material", "planet",
                         "zodiac", "ritual", "concept", "magic_square", "person"],
    },

    "discoverie": {
        "label": "Reginald Scot — Discoverie of Witchcraft (1584)",
        "pdf": r"c:\Users\akbon\Downloads\b21720307.pdf",
        "mode": "native",
        "language": "en",
        "translate": False,         # Already in English — skip translation stage
        "research_goal": (
            "Extract structured knowledge from Scot's Discoverie of Witchcraft: "
            "spirit names and hierarchies, conjuration circles, planetary angels, "
            "ritual equipment, sceptical arguments against magic, "
            "historical persons cited, and connections to the Munich Handbook tradition."
        ),
        "entity_types": ["spirit", "angel", "person", "ritual", "material",
                         "concept", "location", "critique"],
    },

    "key_of_solomon": {
        "label": "Key of Solomon (Clavicula Salomonis) — multiple MSS, c. 14th-17th c.",
        "pdf": r"c:\Users\akbon\Downloads\key_of_solomon.pdf",
        "mode": "native",
        "language": "en",
        "translate": False,
        "research_goal": (
            "Extract structured knowledge from the Key of Solomon: "
            "pentacles and their powers, planetary attributions, spirit names, "
            "ritual preparations (fasting, garments, tools), days and hours of operation, "
            "divine names invoked, circle construction, and the grimoire's theory of "
            "how angelic authority compels demonic obedience."
        ),
        "entity_types": ["pentacle", "spirit", "angel", "divine_name", "ritual",
                         "material", "planet", "day_hour", "concept"],
    },

    "lemegeton": {
        "label": "Lemegeton Clavicula Salomonis (Lesser Key of Solomon) — c. 17th c.",
        "pdf": r"c:\Users\akbon\Downloads\lemegeton.pdf",
        "mode": "native",
        "language": "en",
        "translate": False,
        "research_goal": (
            "Extract structured knowledge from the Lemegeton: "
            "the 72 spirits of the Goetia (name, rank, powers, appearance, seal), "
            "Theurgia-Goetia aerial spirits, Ars Paulina planetary spirits, "
            "Ars Almadel angelic choirs, and Ars Notoria orisons. "
            "Cross-reference with Munich Handbook spirit names."
        ),
        "entity_types": ["spirit", "seal", "rank", "power", "appearance",
                         "angel", "ritual", "divine_name", "planet", "concept"],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def paths_for(source_id: str) -> dict:
    """Return standard directory paths for a given source."""
    return {
        "raw":        DATA_DIR / "sources" / source_id,
        "translated": DATA_DIR / "sources" / f"{source_id}_translated",
        "distilled":  DATA_DIR / "distilled" / source_id,
        "aggregate_json": DATA_DIR / "distilled" / f"{source_id}_entities.json",
        "aggregate_csv":  DATA_DIR / "distilled" / f"{source_id}_entities.csv",
    }


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks at paragraph boundaries."""
    paragraphs = re.split(r"\n\n+", text)
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > chunk_size and current:
            chunks.append(current.strip())
            # Overlap: carry last `overlap` chars
            current = current[-overlap:] + "\n\n" + para if overlap else para
        else:
            current = (current + "\n\n" + para).strip() if current else para.strip()
    if current.strip():
        chunks.append(current.strip())
    return chunks


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("\x0c", "\n\n")
    for lig, rep in [("ﬁ","fi"),("ﬂ","fl"),("ﬀ","ff"),("ﬃ","ffi"),("ﬄ","ffl")]:
        text = text.replace(lig, rep)
    return text.strip()


def _extract_objects_from_array(text: str, array_name: str) -> list:
    """Depth-aware extraction of objects from a named JSON array."""
    match = re.search(r'"' + array_name + r'"\s*:\s*\[', text)
    if not match:
        return []
    pos = match.end()
    objects, i = [], pos
    while i < len(text):
        if text[i] == "]":
            break
        if text[i] != "{":
            i += 1
            continue
        depth, obj_start = 0, i
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


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1: INGEST
# ══════════════════════════════════════════════════════════════════════════════

def stage_ingest(source_id: str, cfg: dict, resume: bool = False):
    """PDF → chunked text files in data/sources/{source_id}/"""
    p = paths_for(source_id)
    raw_dir = p["raw"]
    raw_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = cfg["pdf"]
    if not Path(pdf_path).exists():
        print(f"  [SKIP] PDF not found: {pdf_path}")
        return

    # Check if already done
    existing = sorted(raw_dir.glob("chunk_*.txt"))
    if resume and existing:
        print(f"  [RESUME] {len(existing)} chunks already exist in {raw_dir}")
        return

    print(f"  Extracting text from {pdf_path} ...")
    if cfg["mode"] == "ocr":
        text = _extract_ocr(pdf_path, cfg)
    else:
        text = _extract_native(pdf_path)

    chunks = chunk_text(text)
    print(f"  Splitting into {len(chunks)} chunks ...")
    for i, chunk in enumerate(chunks):
        out = raw_dir / f"chunk_{i:03d}.txt"
        out.write_text(chunk, encoding="utf-8")
    print(f"  Done. {len(chunks)} chunks -> {raw_dir}")


def _extract_native(pdf_path: str) -> str:
    import fitz
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        if i % 100 == 0:
            print(f"    Reading page {i+1}/{doc.page_count} ...")
        t = page.get_text()
        if t.strip():
            pages.append(f"--- PAGE {i+1} ---\n{clean_text(t)}")
    doc.close()
    return "\n\n".join(pages)


def _extract_ocr(pdf_path: str, cfg: dict) -> str:
    import fitz
    import pytesseract
    from PIL import Image
    import io as _io
    tc = cfg.get("tesseract_cmd", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    pytesseract.pytesseract.tesseract_cmd = tc
    lang = cfg.get("ocr_lang", "eng")
    doc = fitz.open(pdf_path)
    pages = []
    n = doc.page_count
    for i in range(n):
        if i % 10 == 0:
            print(f"    OCR page {i+1}/{n} ...")
        page = doc[i]
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        img = Image.open(_io.BytesIO(pix.tobytes("png")))
        t = pytesseract.image_to_string(img, lang=lang)
        if t.strip():
            pages.append(f"--- PAGE {i+1} ---\n{clean_text(t)}")
    doc.close()
    return "\n\n".join(pages)


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2: TRANSLATE
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATE_SYSTEM = (
    "You are an expert scholar specializing in {century}-century {language_name} texts "
    "covering natural philosophy, magic, cryptography, and occult sciences. "
    "Translate the provided text into clear, accurate modern English. "
    "Preserve technical terminology (spirit names, plant names, cipher names). "
    "Where OCR has garbled a word, make your best scholarly reconstruction. "
    "Output only the English translation — no commentary."
)

LANGUAGE_NAMES = {
    "la": ("Latin", "16th"),
    "de": ("German", "15th"),
    "ar": ("Arabic", "10th"),
    "fr": ("French", "17th"),
    "it": ("Italian", "16th"),
    "en": ("English", "16th"),  # old English — still useful to modernize
}


def stage_translate(source_id: str, cfg: dict, client: OpenAI,
                    resume: bool = False, skip_chunks: set = None):
    """Raw chunks → English translations in data/sources/{source_id}_translated/"""
    p = paths_for(source_id)
    in_dir = p["raw"]
    out_dir = p["translated"]
    out_dir.mkdir(parents=True, exist_ok=True)
    skip_chunks = skip_chunks or cfg.get("skip_chunks", set())

    lang_code = cfg.get("language", "la")
    lang_name, century = LANGUAGE_NAMES.get(lang_code, ("Latin", "16th"))
    system = TRANSLATE_SYSTEM.format(century=century, language_name=lang_name)

    chunks = sorted(in_dir.glob("chunk_*.txt"))
    if not chunks:
        print(f"  [SKIP] No chunks found in {in_dir}")
        return

    for chunk_path in chunks:
        num = int(re.search(r"chunk_(\d+)", chunk_path.name).group(1))
        if num in skip_chunks:
            print(f"  [SKIP] chunk_{num:03d} (skip_chunks)")
            continue

        out_path = out_dir / f"chunk_{num:03d}_en.txt"
        if resume and out_path.exists():
            continue

        text = chunk_path.read_text(encoding="utf-8")
        passages = _split_passages(text, MAX_CHARS_PER_TRANSLATE)
        translated_parts = []

        print(f"  Translating chunk_{num:03d} ({len(passages)} passages) ...")
        for j, passage in enumerate(passages):
            for attempt in range(3):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": f"Translate:\n\n{passage}"},
                            {"role": "assistant", "content": "Translation:\n\n"},
                        ],
                        max_tokens=2048,
                        temperature=0.1,
                    )
                    t = resp.choices[0].message.content or ""
                    translated_parts.append(t.strip())
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"    [ERROR] passage {j}: {e}")
                        translated_parts.append(f"[TRANSLATION ERROR: {e}]")
                    time.sleep(2 ** attempt)

        out_path.write_text("\n\n".join(translated_parts), encoding="utf-8")

    print(f"  Done. Translations -> {out_dir}")


def _split_passages(text: str, max_chars: int) -> list[str]:
    paragraphs = re.split(r"\n\n+", text)
    passages, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars and current:
            passages.append(current.strip())
            current = para
        else:
            current = (current + "\n\n" + para).strip() if current else para.strip()
    if current.strip():
        passages.append(current.strip())
    return passages or [text]


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3: DISTILL
# ══════════════════════════════════════════════════════════════════════════════

DISTILL_SYSTEM = (
    "You are a precise research extraction engine for historical occult and scientific texts. "
    "Output only valid, complete JSON. Never invent data not present in the source."
)

DISTILL_USER_TEMPLATE = """\
Extract structured entities and relationships from this passage of {source_label}.

Research goal: {research_goal}

Source text:
{text}

Return ONLY a JSON object with this schema:
{{
  "has_relevant_content": true/false,
  "entities": [
    {{
      "name": "...",
      "type": "...",
      "description": "...",
      "source_ref": "page or chapter reference if mentioned",
      "attributes": {{}}
    }}
  ],
  "relationships": [
    {{
      "from": "entity name",
      "relation": "...",
      "to": "entity name"
    }}
  ],
  "summary": "2-3 sentence summary of this passage",
  "key_passages": ["direct quote 1", "direct quote 2"]
}}

Entity types for this source: {entity_types}
"""


def stage_distill(source_id: str, cfg: dict, client: OpenAI,
                  resume: bool = False, skip_chunks: set = None):
    """Translated chunks → structured JSON in data/distilled/{source_id}/"""
    p = paths_for(source_id)
    # Use translated dir if translation was done, else raw dir
    in_dir = p["translated"] if cfg.get("translate") else p["raw"]
    out_dir = p["distilled"]
    out_dir.mkdir(parents=True, exist_ok=True)
    skip_chunks = skip_chunks or cfg.get("skip_chunks", set())

    pattern = "chunk_*_en.txt" if cfg.get("translate") else "chunk_*.txt"
    chunks = sorted(in_dir.glob(pattern))
    if not chunks:
        print(f"  [SKIP] No translated chunks found in {in_dir}")
        return

    entity_types = ", ".join(cfg.get("entity_types", ["concept", "person", "material"]))

    for chunk_path in chunks:
        num = int(re.search(r"chunk_(\d+)", chunk_path.name).group(1))
        if num in skip_chunks:
            continue

        out_path = out_dir / f"distilled_{num:03d}.json"
        if resume and out_path.exists():
            continue

        text = chunk_path.read_text(encoding="utf-8")
        if len(text) > MAX_CHARS_PER_DISTILL:
            text = text[:MAX_CHARS_PER_DISTILL]

        print(f"  Distilling chunk_{num:03d} ({len(text)} chars) ...")
        user_msg = DISTILL_USER_TEMPLATE.format(
            source_label=cfg["label"],
            research_goal=cfg["research_goal"],
            text=text,
            entity_types=entity_types,
        )

        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": DISTILL_SYSTEM},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": '{\n  "has_relevant_content":'},
                    ],
                    max_tokens=MAX_TOKENS_DISTILL,
                    temperature=0.1,
                )
                raw = '{\n  "has_relevant_content":' + (resp.choices[0].message.content or "")
                result = _parse_distill_output(raw, source_id, num)
                out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                n_entities = len(result.get("entities", []))
                print(f"    -> {n_entities} entities")
                break
            except Exception as e:
                if attempt == 2:
                    print(f"    [ERROR] chunk_{num:03d}: {e}")
                    out_path.write_text(json.dumps({
                        "source_id": source_id, "chunk_id": num,
                        "error": str(e), "entities": [], "relationships": []
                    }, indent=2))
                time.sleep(2 ** attempt)

    print(f"  Done. Distilled -> {out_dir}")


def _parse_distill_output(raw: str, source_id: str, chunk_id: int) -> dict:
    """Parse and recover distillation output, handling truncation."""
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    try:
        data = json.loads(raw)
        data["source_id"] = source_id
        data["chunk_id"] = chunk_id
        return data
    except json.JSONDecodeError:
        pass

    # Depth-aware recovery
    entities = _extract_objects_from_array(raw, "entities")
    relationships = _extract_objects_from_array(raw, "relationships")

    summary_match = re.search(r'"summary"\s*:\s*"([^"]{10,})"', raw)
    summary = summary_match.group(1) if summary_match else ""

    relevant_match = re.search(r'"has_relevant_content"\s*:\s*(true|false)', raw)
    relevant = (relevant_match.group(1) == "true") if relevant_match else bool(entities)

    return {
        "source_id": source_id,
        "chunk_id": chunk_id,
        "has_relevant_content": relevant,
        "entities": entities,
        "relationships": relationships,
        "summary": summary,
        "key_passages": [],
        "_truncated": True,
    }


# ══════════════════════════════════════════════════════════════════════════════
# AGGREGATE: merge all distilled chunks -> entities.json + entities.csv
# ══════════════════════════════════════════════════════════════════════════════

def stage_aggregate(source_id: str):
    """Merge all distilled_XXX.json files into a single entities.json + .csv"""
    p = paths_for(source_id)
    distill_dir = p["distilled"]
    json_files = sorted(distill_dir.glob("distilled_*.json"))

    if not json_files:
        print(f"  [SKIP] No distilled files in {distill_dir}")
        return

    all_entities = []
    seen = set()
    for f in json_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for ent in data.get("entities", []):
            key = (ent.get("name", "").lower().strip(), ent.get("type", ""))
            if key in seen or not ent.get("name"):
                continue
            seen.add(key)
            ent["source_id"] = source_id
            ent["chunk_id"] = data.get("chunk_id", "?")
            all_entities.append(ent)

    # Write JSON
    p["aggregate_json"].write_text(json.dumps(all_entities, indent=2), encoding="utf-8")

    # Write CSV
    if all_entities:
        fieldnames = ["name", "type", "description", "source_ref", "source_id", "chunk_id"]
        with open(p["aggregate_csv"], "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_entities)

    print(f"  {len(all_entities)} unique entities -> {p['aggregate_json'].name} + .csv")


# ══════════════════════════════════════════════════════════════════════════════
# STATUS
# ══════════════════════════════════════════════════════════════════════════════

def show_status():
    """Print a table of all sources and their pipeline progress."""
    print(f"\n{'SOURCE':30} {'INGEST':8} {'TRANSLATE':10} {'DISTILL':8} {'ENTITIES':10}")
    print("-" * 72)
    for sid, cfg in SOURCES.items():
        p = paths_for(sid)
        raw_chunks = len(list(p["raw"].glob("chunk_*.txt"))) if p["raw"].exists() else 0
        tr_chunks = len(list(p["translated"].glob("chunk_*_en.txt"))) if p["translated"].exists() else 0
        dist_chunks = len(list(p["distilled"].glob("distilled_*.json"))) if p["distilled"].exists() else 0
        entities = 0
        if p["aggregate_json"].exists():
            try:
                entities = len(json.loads(p["aggregate_json"].read_text()))
            except Exception:
                pass
        translate_col = f"{tr_chunks}ch" if cfg.get("translate") else "skip"
        print(f"  {sid:28} {raw_chunks:5}ch   {translate_col:8}   {dist_chunks:5}ch   {entities:6} ents")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generalized historical text pipeline")
    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Show pipeline progress for all sources")

    # run
    run_p = sub.add_parser("run", help="Run pipeline stages for a source")
    run_p.add_argument("--source", required=True, choices=list(SOURCES.keys()),
                       help="Source ID to process")
    run_p.add_argument("--stage", choices=["ingest", "translate", "distill", "all"],
                       default="all", help="Which stage to run")
    run_p.add_argument("--resume", action="store_true",
                       help="Skip already-completed chunks")
    run_p.add_argument("--chunks", type=str,
                       help="Comma-separated chunk numbers to process (e.g. 1,2,5)")

    # aggregate
    agg_p = sub.add_parser("aggregate", help="Merge distilled chunks into entities.json/csv")
    agg_p.add_argument("--source", required=True, choices=list(SOURCES.keys()))

    # list
    sub.add_parser("list", help="List all available sources")

    args = parser.parse_args()

    if args.command == "status":
        show_status()
        return

    if args.command == "list":
        for sid, cfg in SOURCES.items():
            print(f"  {sid:25} — {cfg['label']}")
        return

    if args.command == "aggregate":
        print(f"Aggregating {args.source} ...")
        stage_aggregate(args.source)
        return

    if args.command == "run":
        cfg = SOURCES[args.source]
        skip_chunks = set()
        if args.chunks:
            # Only process specified chunks (inverse: skip everything else)
            pass  # handled inside each stage via filtering

        print(f"\nPipeline: {cfg['label']}")
        print(f"Source ID: {args.source}  |  Stage: {args.stage}  |  Resume: {args.resume}\n")

        client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

        if args.stage in ("ingest", "all"):
            print("[Stage 1] INGEST")
            stage_ingest(args.source, cfg, resume=args.resume)

        if args.stage in ("translate", "all") and cfg.get("translate"):
            print("[Stage 2] TRANSLATE")
            stage_translate(args.source, cfg, client, resume=args.resume)
        elif args.stage == "translate" and not cfg.get("translate"):
            print("[Stage 2] SKIP — source is already in English")

        if args.stage in ("distill", "all"):
            print("[Stage 3] DISTILL")
            stage_distill(args.source, cfg, client, resume=args.resume)

        print("\nAggregating entities ...")
        stage_aggregate(args.source)

        show_status()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
