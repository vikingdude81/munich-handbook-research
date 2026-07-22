#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distill Heresy & Revolution PDFs using the proven pipeline.py approach.

Fixes over v2:
  1. max_tokens=3000 (v2 used 1200 — JSON was truncated, causing 100% parse failures)
  2. Field-level regex recovery from truncated JSON (ported from pipeline._parse_distill_output)
  3. Resume validation: only skips chunks where entropy_score > 0 (not just file existence)
  4. Strips <think> / thinking blocks that some Nemotron variants emit before JSON

Usage:
    python scripts/distill_heresy_revolution_v3.py --source malleus_maleficarum
    python scripts/distill_heresy_revolution_v3.py --source karl_marx
    python scripts/distill_heresy_revolution_v3.py --source all
    python scripts/distill_heresy_revolution_v3.py --source all --resume
    python scripts/distill_heresy_revolution_v3.py --analyze-cross
"""

import argparse
import json
import io
import re
import sys
import time
from pathlib import Path
from openai import OpenAI

# Force UTF-8 stdout on Windows (avoids cp1252 UnicodeEncodeError on box-drawing chars)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Config ──────────────────────────────────────────────────────────────────
LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL         = "nvidia/nemotron-3-nano-omni"
ROOT          = Path(__file__).resolve().parent.parent
DATA_DIR      = ROOT / "data"
MAX_TOKENS    = 3000    # pipeline.py uses 6000; entropy schema is simpler → 3000 is safe
MAX_CHARS     = 6000    # truncate source text fed to model

# ── Prompts ─────────────────────────────────────────────────────────────────

SYSTEM = (
    "You are a precise historical analyst specializing in rhetoric analysis. "
    "Analyze historical texts for deconstructionist vs. constructive rhetoric patterns. "
    "Output only valid, complete JSON. Never invent data not present in the source. "
    "Score every field based on what the text actually says — do not use placeholder values."
)

USER_TEMPLATE = """\
Analyze this historical text passage for deconstructionist vs. constructive rhetoric.
Read it carefully and score it based on what it actually contains.

SCORING RUBRIC — read before scoring:

ENTROPY SCORE (how destructive/entropic is the rhetoric?):
  1-2  = Primarily constructive: proposes rules, governance, mechanisms, administrative order
  3-4  = Mild critique with meaningful constructive proposals balancing it
  5-6  = Mixed: significant criticism but also some concrete proposals or procedures
  7-8  = Heavy deconstruction: exposes, condemns, or dismantles with minimal constructive output
  9-10 = Pure destruction: absolute moral condemnation, zero constructive blueprint

RHETORICAL INTENSITY (how emotionally charged is the language?):
  1-2  = Calm, scholarly, analytical — minimal emotional charge
  3-4  = Moderately assertive, some moral language but largely factual
  5-6  = Noticeably charged: elevated moral stakes, us-vs-them framing
  7-8  = Highly charged: strong moral condemnation, apocalyptic or revolutionary tone
  9-10 = Maximum intensity: absolute evil/enemy framing, calls for eradication

PRIMARY MODE options: "Deconstruction", "Construction", "Mixed", "Neutral"
  Deconstruction = text mainly tears down, exposes, or condemns
  Construction   = text mainly builds, governs, or designs systems/procedures
  Mixed          = substantial portions of both
  Neutral        = descriptive, neither strongly deconstructing nor constructing

Source text to analyze:
{text}

Return ONLY a valid JSON object. Fill every numeric field with the actual score you calculated.
Do not copy the rubric numbers — score based on this specific text:
{{
  "has_relevant_content": null,
  "primary_mode": null,
  "entropy_score": null,
  "rhetorical_intensity": null,
  "deconstruction_targets": [],
  "constructive_proposals": [],
  "scapegoat": {{
    "name": "",
    "attributes": [],
    "justification": ""
  }},
  "moral_justification": "",
  "summary": ""
}}
"""

# Assistant prefill — forces the model to continue in JSON mode (proven in pipeline.py)
PREFILL = '{\n  "has_relevant_content":'


# ── JSON recovery helpers ────────────────────────────────────────────────────

def _strip_think_blocks(text: str) -> str:
    """Remove <think>…</think> or <thinking>…</thinking> blocks some models emit."""
    text = re.sub(r"<think(?:ing)?>\s*.*?\s*</think(?:ing)?>", "", text, flags=re.DOTALL)
    return text.strip()


def _strip_md_fences(text: str) -> str:
    """Remove ```json … ``` fences."""
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    return text.strip()


def _clean_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _field_str(raw: str, field: str, default: str = "") -> str:
    m = re.search(r'"' + field + r'"\s*:\s*"([^"]{0,500})"', raw)
    return m.group(1) if m else default


def _field_int(raw: str, field: str, default: int = 0) -> int:
    m = re.search(r'"' + field + r'"\s*:\s*(\d+)', raw)
    return int(m.group(1)) if m else default


def _field_bool(raw: str, field: str, default: bool = True) -> bool:
    m = re.search(r'"' + field + r'"\s*:\s*(true|false)', raw)
    if not m:
        return default
    return m.group(1) == "true"


def _field_list(raw: str, field: str) -> list:
    """Extract a simple string array (no nested objects)."""
    m = re.search(r'"' + field + r'"\s*:\s*\[([^\]]*)\]', raw, re.DOTALL)
    if not m:
        return []
    inner = m.group(1)
    return [s.strip().strip('"') for s in re.findall(r'"([^"]*)"', inner)]


def _field_scapegoat(raw: str) -> dict:
    """Extract the scapegoat sub-object as best we can."""
    m = re.search(r'"scapegoat"\s*:\s*\{([^}]{0,800})\}', raw, re.DOTALL)
    if not m:
        return {"name": "", "attributes": [], "justification": ""}
    inner = "{" + m.group(1) + "}"
    try:
        inner = _clean_trailing_commas(inner)
        return json.loads(inner)
    except json.JSONDecodeError:
        return {
            "name": _field_str(m.group(1), "name"),
            "attributes": _field_list(m.group(1), "attributes"),
            "justification": _field_str(m.group(1), "justification"),
        }


def _recover_fields(raw: str, source_id: str, chunk_num: int) -> dict:
    """Field-by-field recovery when JSON is truncated or malformed."""
    return {
        "source_id":            source_id,
        "chunk_id":             chunk_num,
        "has_relevant_content": _field_bool(raw, "has_relevant_content"),
        "primary_mode":         _field_str(raw, "primary_mode", "Unknown"),
        "entropy_score":        _field_int(raw, "entropy_score"),
        "rhetorical_intensity": _field_int(raw, "rhetorical_intensity"),
        "deconstruction_targets": _field_list(raw, "deconstruction_targets"),
        "constructive_proposals": _field_list(raw, "constructive_proposals"),
        "scapegoat":            _field_scapegoat(raw),
        "moral_justification":  _field_str(raw, "moral_justification"),
        "summary":              _field_str(raw, "summary"),
        "_recovered":           True,
    }


def parse_response(raw: str, source_id: str, chunk_num: int) -> dict:
    """Parse model output robustly; fall back to field extraction on any JSON error.

    Strategy (in order):
    1. raw_decode  — stops at first valid JSON object, ignores post-JSON commentary
    2. trailing-comma clean + raw_decode
    3. regex-extracted object + raw_decode
    4. field-level regex recovery (partial parse)
    """
    raw = _strip_think_blocks(raw)
    raw = _strip_md_fences(raw)

    decoder = json.JSONDecoder()

    # 1. Try raw_decode directly (handles "Extra data" from post-JSON commentary)
    for candidate in [raw, _clean_trailing_commas(raw)]:
        s = candidate.strip()
        # Find first { in case there's leading text
        brace = s.find("{")
        if brace == -1:
            continue
        try:
            data, _ = decoder.raw_decode(s, brace)
            data["source_id"] = source_id
            data["chunk_id"]  = chunk_num
            return data
        except json.JSONDecodeError:
            pass

    # 2. Try finding a JSON object with regex, then raw_decode
    m = re.search(r"\{", raw)
    if m:
        segment = raw[m.start():]
        try:
            data, _ = decoder.raw_decode(_clean_trailing_commas(segment))
            data["source_id"] = source_id
            data["chunk_id"]  = chunk_num
            return data
        except json.JSONDecodeError:
            pass

    # 3. Field-level recovery (truncated JSON — partial results are still useful)
    return _recover_fields(raw, source_id, chunk_num)


def is_valid(data: dict) -> bool:
    """A chunk result is valid if entropy_score is set and non-zero."""
    return (
        data.get("entropy_score", 0) > 0
        and data.get("primary_mode", "Unknown") != "Unknown"
        and not data.get("error")
    )


# ── Core distillation ────────────────────────────────────────────────────────

def distill_source(source_id: str, client: OpenAI, resume: bool = False) -> bool:
    chunks_dir = DATA_DIR / "sources" / "malleus_marx" / source_id
    out_dir    = DATA_DIR / "distilled" / "malleus_marx"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not chunks_dir.exists():
        print(f"ERROR: chunk dir not found: {chunks_dir}")
        return False

    chunk_files = sorted(chunks_dir.glob("chunk_*.txt"))
    if not chunk_files:
        print(f"ERROR: no chunks in {chunks_dir}")
        return False

    print(f"\n{'='*70}")
    print(f"Distilling [{source_id}] — {len(chunk_files)} chunks")
    print(f"  Model:     {MODEL}")
    print(f"  Max tok:   {MAX_TOKENS}")
    print(f"  Resume:    {resume}")
    print(f"{'='*70}")

    successful, failed, skipped = 0, 0, 0

    for chunk_file in chunk_files:
        m = re.search(r"chunk_(\d+)", chunk_file.name)
        chunk_num = int(m.group(1))
        out_path  = out_dir / f"{source_id}_chunk_{chunk_num:03d}.json"

        # Resume: skip only if the existing result is actually valid
        if resume and out_path.exists():
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                if is_valid(existing):
                    skipped += 1
                    continue
            except Exception:
                pass  # Re-process if file is corrupt

        chunk_text = chunk_file.read_text(encoding="utf-8")
        if len(chunk_text) > MAX_CHARS:
            chunk_text = chunk_text[:MAX_CHARS]

        user_msg = USER_TEMPLATE.format(text=chunk_text)

        result = None
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system",    "content": SYSTEM},
                        {"role": "user",      "content": user_msg},
                        {"role": "assistant", "content": PREFILL},  # ← key: JSON prefill
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=0.1,
                )
                # Reconstruct: prefill + model continuation
                continuation = resp.choices[0].message.content or ""
                raw = PREFILL + continuation
                result = parse_response(raw, source_id, chunk_num)
                break

            except Exception as e:
                if attempt == 2:
                    print(f"  chunk_{chunk_num:03d}: ERROR — {e}")
                    result = {
                        "source_id": source_id, "chunk_id": chunk_num,
                        "error": str(e), "entropy_score": 0,
                        "rhetorical_intensity": 0, "primary_mode": "Unknown",
                    }
                time.sleep(2 ** attempt)

        if result is None:
            result = {
                "source_id": source_id, "chunk_id": chunk_num,
                "error": "No response", "entropy_score": 0,
                "rhetorical_intensity": 0, "primary_mode": "Unknown",
            }

        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

        entropy   = result.get("entropy_score", 0)
        intensity = result.get("rhetorical_intensity", 0)
        mode      = result.get("primary_mode", "?")
        recovered = " [recovered]" if result.get("_recovered") else ""
        valid_flag = "OK" if is_valid(result) else "!!"

        print(f"  [{valid_flag}] chunk_{chunk_num:03d}: "
              f"entropy={entropy}, intensity={intensity}, mode={mode}{recovered}")

        if is_valid(result):
            successful += 1
        else:
            failed += 1

    print(f"\n  Done: {successful} valid, {failed} failed, {skipped} skipped")
    _write_aggregate(source_id, out_dir)
    return failed == 0


def _write_aggregate(source_id: str, out_dir: Path):
    """Merge all chunk JSONs into a single aggregate file."""
    chunk_files = sorted(out_dir.glob(f"{source_id}_chunk_*.json"))
    if not chunk_files:
        return

    analyses = []
    for f in chunk_files:
        try:
            analyses.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass

    valid = [a for a in analyses if is_valid(a)]
    entropy_scores    = [a["entropy_score"] for a in valid if isinstance(a.get("entropy_score"), (int, float))]
    intensity_scores  = [a["rhetorical_intensity"] for a in valid if isinstance(a.get("rhetorical_intensity"), (int, float))]

    high_void = sum(
        1 for a in valid
        if a.get("entropy_score", 0) >= 8
        and len(a.get("constructive_proposals", [])) == 0
    )

    mode_dist: dict = {}
    for a in valid:
        mode = a.get("primary_mode", "Unknown")
        mode_dist[mode] = mode_dist.get(mode, 0) + 1

    aggregate = {
        "source":      source_id,
        "total_chunks": len(chunk_files),
        "valid":       len(valid),
        "failed":      len(analyses) - len(valid),
        "stats": {
            "avg_entropy":       round(sum(entropy_scores) / len(entropy_scores), 2) if entropy_scores else 0,
            "max_entropy":       max(entropy_scores) if entropy_scores else 0,
            "min_entropy":       min(entropy_scores) if entropy_scores else 0,
            "avg_intensity":     round(sum(intensity_scores) / len(intensity_scores), 2) if intensity_scores else 0,
            "high_void_count":   high_void,
            "mode_distribution": mode_dist,
        },
        "analyses": analyses,
    }

    agg_path = out_dir / f"{source_id}_aggregate.json"
    agg_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"  Aggregate → {agg_path.name}")
    print(f"    avg entropy:  {aggregate['stats']['avg_entropy']}")
    print(f"    avg intensity: {aggregate['stats']['avg_intensity']}")
    print(f"    high-void:    {aggregate['stats']['high_void_count']}")
    print(f"    mode dist:    {mode_dist}")


# ── Cross-document analysis ──────────────────────────────────────────────────

def cross_document_analysis():
    out_dir = DATA_DIR / "distilled" / "malleus_marx"

    malleus_agg_path = out_dir / "malleus_maleficarum_aggregate.json"
    marx_agg_path    = out_dir / "karl_marx_aggregate.json"

    if not malleus_agg_path.exists() or not marx_agg_path.exists():
        print("ERROR: Both source aggregates must exist. Run --source all first.")
        return False

    malleus = json.loads(malleus_agg_path.read_text(encoding="utf-8"))
    marx    = json.loads(marx_agg_path.read_text(encoding="utf-8"))

    ms = malleus["stats"]
    xs = marx["stats"]

    banner = "=" * 72
    print(f"\n{banner}")
    print("CROSS-DOCUMENT ANALYSIS: Malleus Maleficarum (1486) vs. Karl Marx (1848)")
    print(banner)

    print(f"\nMALLEUS MALEFICARUM  ({malleus['valid']} valid chunks)")
    print(f"  Avg Entropy:       {ms['avg_entropy']:.2f}  (1=constructive, 10=destructive)")
    print(f"  Avg Intensity:     {ms['avg_intensity']:.2f}  (1=calm, 10=absolute condemnation)")
    print(f"  High-Void Chunks:  {ms['high_void_count']}  (intense + zero proposals)")
    print(f"  Mode Distribution: {ms['mode_distribution']}")

    print(f"\nKARL MARX  ({marx['valid']} valid chunks)")
    print(f"  Avg Entropy:       {xs['avg_entropy']:.2f}")
    print(f"  Avg Intensity:     {xs['avg_intensity']:.2f}")
    print(f"  High-Void Chunks:  {xs['high_void_count']}")
    print(f"  Mode Distribution: {xs['mode_distribution']}")

    entropy_delta = xs['avg_entropy'] - ms['avg_entropy']
    void_delta    = xs['high_void_count'] - ms['high_void_count']
    print(f"\nDELTAS")
    print(f"  Entropy delta:  {entropy_delta:+.2f}  (Marx {'more' if entropy_delta > 0 else 'less'} destructive)")
    print(f"  Void delta:     {void_delta:+d}   (Marx {'more' if void_delta > 0 else 'less'} void-heavy)")

    # Scapegoat mapping
    malleus_scapegoats = list({
        a.get("scapegoat", {}).get("name", "").strip()
        for a in malleus["analyses"]
        if a.get("scapegoat", {}).get("name", "").strip()
    })
    marx_scapegoats = list({
        a.get("scapegoat", {}).get("name", "").strip()
        for a in marx["analyses"]
        if a.get("scapegoat", {}).get("name", "").strip()
    })

    print(f"\nSCAPEGOATS")
    print(f"  Malleus: {malleus_scapegoats[:10]}")
    print(f"  Marx:    {marx_scapegoats[:10]}")

    # ── Data-derived interpretation (was a hard-coded conclusion that always
    #    "confirmed" the thesis regardless of the numbers). Now describes what
    #    the measured deltas actually show, with explicit caveats about the
    #    instrument so the output cannot pre-decide the finding.
    similar = abs(entropy_delta) < 0.5 and abs(void_delta) <= 5
    direction = "indistinguishable" if similar else (
        "more destructive in Marx" if entropy_delta > 0 else "more destructive in Malleus")
    interpretation = (
        f"Measured average-entropy delta is {entropy_delta:+.2f} and void-chunk delta "
        f"is {void_delta:+d}; on these metrics the two texts are {direction}. "
        "CAVEAT: scores come from a 1-10 rubric applied by a single small judge "
        "model (nemotron nano) at temperature 0.1, with no control corpus and no "
        "inter-rater check. Rubric-anchoring drives scores toward the central "
        "'heavy deconstruction' band (observed max entropy = "
        f"{max(ms['max_entropy'], xs['max_entropy'])}, never reaching 9-10), so a "
        "small delta is the expected output of the instrument and is NOT, on its "
        "own, evidence that the texts share a psychological mechanism. The "
        "witch->bourgeoisie scapegoat mapping is an interpretive hypothesis, not a "
        "result derived from these numbers."
    )
    analysis = {
        "malleus_stats":   ms,
        "marx_stats":      xs,
        "entropy_delta":   entropy_delta,
        "void_delta":      void_delta,
        "malleus_scapegoats": malleus_scapegoats,
        "marx_scapegoats":   marx_scapegoats,
        "interpretation": interpretation,
    }

    analysis_path = out_dir / "cross_document_analysis.json"
    analysis_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print(f"\n  Saved → {analysis_path}")
    print(banner)
    return True


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Distill Heresy & Revolution PDFs (v3 — proven pipeline approach)"
    )
    parser.add_argument(
        "--source",
        choices=["malleus_maleficarum", "karl_marx", "all"],
        help="Which source to distill",
    )
    parser.add_argument(
        "--analyze-cross",
        action="store_true",
        help="Run cross-document analysis (both aggregates must exist)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip chunks that already have valid results (entropy_score > 0)",
    )
    parser.add_argument(
        "--model",
        default=MODEL,
        help=f"LM Studio model name (default: {MODEL})",
    )
    parser.add_argument(
        "--base-url",
        default=LM_STUDIO_URL,
        help=f"LM Studio endpoint (default: {LM_STUDIO_URL})",
    )
    args = parser.parse_args()

    if not args.source and not args.analyze_cross:
        parser.print_help()
        sys.exit(1)

    client = OpenAI(base_url=args.base_url, api_key="lm-studio")

    if args.source in ("malleus_maleficarum", "all"):
        distill_source("malleus_maleficarum", client, resume=args.resume)

    if args.source in ("karl_marx", "all"):
        distill_source("karl_marx", client, resume=args.resume)

    if args.analyze_cross:
        if not cross_document_analysis():
            sys.exit(1)


if __name__ == "__main__":
    main()
