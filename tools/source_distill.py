"""
tools/source_distill.py — Source text distillation tools.

Lets the brain list pre-chunked source texts and distill them through the
configured reasoning model (see config.py; last recorded: gemma-4-26b).  Workers never touch raw source — they only see
the structured extractions the thinker produces.

Tools: list_source_chunks, read_source_chunk, distill_source_chunk
"""

import json
import logging
import os

from openai import OpenAI
import config
import json

class BaseTool:
    def __init__(self): pass
    def call(self, params, **kwargs): raise NotImplementedError()

TOOL_REG_MAP = {}
def register_tool(name):
    def decorator(cls):
        TOOL_REG_MAP[name] = cls
        return cls
    return decorator

def parse_tool_params(params_str: str) -> dict:
    try: return json.loads(params_str)
    except: return {}

log = logging.getLogger(__name__)


def _load_manifest(project_dir: str) -> dict | None:
    """Load the source_manifest.json from a project's data/sources/ dir."""
    manifest_path = os.path.join(project_dir, "data", "sources", "source_manifest.json")
    if not os.path.isfile(manifest_path):
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# TOOL: LIST SOURCE CHUNKS
# ==========================================
@register_tool('list_source_chunks')
class ListSourceChunks(BaseTool):
    description = (
        'Lists all available pre-chunked source texts for a research project. '
        'Run source_prep.py first to extract and chunk source PDFs/text files. '
        'Returns source IDs, chunk counts, and descriptions so you can decide which to read.'
    )
    parameters = [
        {
            'name': 'project_dir',
            'type': 'string',
            'description': 'Full path to the research project (e.g. "E:\\\\munich_handbook_research").',
            'required': True,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        params = parse_tool_params(params)
        project_dir = params.get('project_dir', '')

        manifest = _load_manifest(project_dir)
        if manifest is None:
            return (
                f"NO MANIFEST: No source_manifest.json found in {project_dir}/data/sources/. "
                "Run source_prep.py first to extract and chunk source texts."
            )

        lines = [f"SOURCE TEXTS for {project_dir}\n"]
        lines.append(f"Chunk size: {manifest.get('chunk_size', '?')} chars, "
                      f"overlap: {manifest.get('chunk_overlap', '?')}\n")

        for src in manifest.get('sources', []):
            status = src.get('status', '?')
            src_id = src.get('id', '?')
            desc = src.get('description', '')
            n_chunks = src.get('total_chunks', 0)
            total_chars = src.get('total_chars', 0)

            if status == 'ok':
                lines.append(f"  [{src_id}] {desc}")
                lines.append(f"    {n_chunks} chunks, {total_chars:,} chars total")
                lines.append(f"    Chunk IDs: 0 to {n_chunks - 1}")
            elif status == 'scanned_images':
                lines.append(f"  [{src_id}] {desc}")
                lines.append(f"    SCANNED IMAGES — no extractable text (needs OCR)")
            elif status == 'missing':
                lines.append(f"  [{src_id}] FILE NOT FOUND: {src.get('path', '?')}")
            else:
                lines.append(f"  [{src_id}] status={status}")
            lines.append("")

        return "\n".join(lines)


# ==========================================
# TOOL: READ SOURCE CHUNK
# ==========================================
@register_tool('read_source_chunk')
class ReadSourceChunk(BaseTool):
    description = (
        'Reads a single pre-chunked section of a source text. Each chunk is ~25K chars '
        '(about 6K tokens). Use list_source_chunks first to see available sources and chunk IDs. '
        'Returns the raw text of that chunk with a header showing its position in the full source.'
    )
    parameters = [
        {
            'name': 'project_dir',
            'type': 'string',
            'description': 'Full path to the research project.',
            'required': True,
        },
        {
            'name': 'source_id',
            'type': 'string',
            'description': 'Source identifier (e.g. "necro", "worship_dead", "forbidden_rites_pdf").',
            'required': True,
        },
        {
            'name': 'chunk_id',
            'type': 'integer',
            'description': 'Chunk number (0-based). Use list_source_chunks to see the range.',
            'required': True,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        params = parse_tool_params(params)
        project_dir = params.get('project_dir', '')
        source_id = params.get('source_id', '')
        chunk_id = params.get('chunk_id', 0)

        chunk_file = os.path.join(
            project_dir, "data", "sources", source_id, f"chunk_{int(chunk_id):03d}.txt"
        )

        if not os.path.isfile(chunk_file):
            return f"CHUNK NOT FOUND: {chunk_file}"

        with open(chunk_file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        # Cap at PROJECT_MAX_READ_CHARS to fit in context
        max_chars = getattr(config, 'PROJECT_MAX_READ_CHARS', 30000)
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... [TRUNCATED at {max_chars} chars]"

        return text


# ==========================================
# TOOL: DISTILL SOURCE CHUNK
# ==========================================
@register_tool('distill_source_chunk')
class DistillSourceChunk(BaseTool):
    description = (
        'Send a source text chunk to the configured reasoning model for distillation. '
        'The thinker reads the raw text and extracts structured data relevant to '
        'your research goal: names, attributes, page references, experiments, rituals, etc. '
        'Results are saved to the project and returned. '
        'This is the PRIMARY way to analyze source material — the 5090 digests it, '
        'then workers act on the distilled output.'
    )
    parameters = [
        {
            'name': 'project_dir',
            'type': 'string',
            'description': 'Full path to the research project.',
            'required': True,
        },
        {
            'name': 'source_id',
            'type': 'string',
            'description': 'Source identifier (e.g. "necro").',
            'required': True,
        },
        {
            'name': 'chunk_id',
            'type': 'integer',
            'description': 'Chunk number (0-based).',
            'required': True,
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': 'The research goal to guide extraction (e.g. "Extract spirit names, attributes, conjuration methods, and page references from the Munich Handbook").',
            'required': True,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        params = parse_tool_params(params)
        project_dir = params.get('project_dir', '')
        source_id = params.get('source_id', '')
        chunk_id = int(params.get('chunk_id', 0))
        goal = params.get('goal', '')

        # Check for cached distillation
        distill_dir = os.path.join(project_dir, "data", "distilled", source_id)
        distill_file = os.path.join(distill_dir, f"distilled_{chunk_id:03d}.json")
        if os.path.isfile(distill_file):
            with open(distill_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return (
                f"[CACHED] Distillation for {source_id} chunk {chunk_id} already exists.\n\n"
                + json.dumps(cached, indent=2, ensure_ascii=False)[:config.PROJECT_MAX_READ_CHARS]
            )

        # Read the source chunk
        chunk_file = os.path.join(
            project_dir, "data", "sources", source_id, f"chunk_{chunk_id:03d}.txt"
        )
        if not os.path.isfile(chunk_file):
            return f"CHUNK NOT FOUND: {chunk_file}"

        with open(chunk_file, "r", encoding="utf-8", errors="replace") as f:
            chunk_text = f.read()

        # Strip the ingestion header / page markers / OCR garbage so they don't
        # pollute extraction (canonical cleaner; best-effort if src not importable).
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.chunking import clean_source_text
            chunk_text = clean_source_text(chunk_text)
        except Exception:
            pass

        # Send to the configured reasoning model for distillation
        server = getattr(config, 'REASONING_SERVER', '')
        model_id = getattr(config, 'REASONING_MODEL_ID', '')
        api_key = getattr(config, 'REASONING_API_KEY', 'lm-studio')

        if not server or not model_id:
            return "ERROR: REASONING_SERVER / REASONING_MODEL_ID not configured in config.py"

        extraction_prompt = (
            f"RESEARCH GOAL: {goal}\n\n"
            f"SOURCE TEXT (chunk {chunk_id} of source '{source_id}'):\n"
            f"{'='*60}\n"
            f"{chunk_text}\n"
            f"{'='*60}\n\n"
            "INSTRUCTIONS:\n"
            "You are a research extraction engine. Read the source text above and extract "
            "ALL information relevant to the research goal. Be thorough and precise.\n\n"
            "Return a JSON object with these fields:\n"
            "{\n"
            '  "source_id": "' + source_id + '",\n'
            f'  "chunk_id": {chunk_id},\n'
            '  "has_relevant_content": true/false,\n'
            '  "entities": [\n'
            '    {\n'
            '      "name": "entity name",\n'
            '      "type": "spirit|ritual|ingredient|tool|location|person|concept",\n'
            '      "attributes": {"key": "value"},\n'
            '      "page_ref": "page number or section if available",\n'
            '      "raw_quote": "exact quote from source (max 200 chars)"\n'
            '    }\n'
            '  ],\n'
            '  "relationships": [\n'
            '    {"from": "entity1", "to": "entity2", "type": "relationship type"}\n'
            '  ],\n'
            '  "summary": "2-3 sentence summary of what this chunk covers",\n'
            '  "key_passages": ["important direct quotes (max 5)"]\n'
            "}\n\n"
            "RULES:\n"
            "- Extract ONLY what is actually in the source text. DO NOT hallucinate or invent.\n"
            "- If the chunk has no content relevant to the goal, set has_relevant_content=false "
            "and return empty arrays.\n"
            "- Include page references when the source provides them.\n"
            "- Quote the source directly — do not paraphrase for key_passages.\n"
            "- Return ONLY the JSON object, no other text."
        )

        log.info('[DISTILL] Sending %s chunk %d (%d chars) to %s',
                 source_id, chunk_id, len(chunk_text), model_id)

        try:
            client = OpenAI(base_url=server, api_key=api_key)
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": (
                        "You are a precise research extraction engine. "
                        "Extract structured data from source texts. "
                        "Output only valid JSON. Never invent or hallucinate data."
                    )},
                    {"role": "user", "content": extraction_prompt},
                ],
                temperature=0.1,
                max_tokens=getattr(config, 'REASONING_MAX_TOKENS', 8192),
                top_p=0.9,
            )
            result_text = response.choices[0].message.content or ""
        except Exception as e:
            log.error('[DISTILL ERROR] %s', e)
            return f"DISTILL ERROR: {str(e)}"

        # Try to parse the JSON response
        distilled = None
        # Strip markdown fences if present
        clean = result_text.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[-1] if '\n' in clean else clean[3:]
            if clean.endswith('```'):
                clean = clean[:-3]
            clean = clean.strip()

        # --- Repair common LLM JSON issues before parsing ---
        import re

        def _repair_json(text):
            """Fix common LLM JSON problems: truncation, set-literals, trailing commas."""
            s = text.strip()

            # Fix set-literal attributes like {"some text"} → {"description": "some text"}
            # Pattern: {"key": {" ... "}} where inner braces have no colon
            s = re.sub(
                r'\{("(?:[^"\\]|\\.)*")\}',
                lambda m: '{"description": ' + m.group(1) + '}' if ':' not in m.group(1) else m.group(0),
                s,
            )

            # Remove trailing commas before } or ]
            s = re.sub(r',\s*([}\]])', r'\1', s)

            # Fix truncated JSON: count open/close braces and brackets, close any unclosed
            # First, try to find last complete entity in arrays
            try:
                json.loads(s)
                return s  # Already valid
            except json.JSONDecodeError:
                pass

            # Truncation recovery: find the last valid position and close brackets
            # Strategy: remove the last incomplete array element, then close all brackets
            # Find the last complete "}" that ends an array element
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
                # JSON was truncated — try to close it
                # Cut back to the last complete } and close remaining brackets
                if last_good and last_good > len(s) // 2:
                    s = s[:last_good + 1]
                    # Remove any trailing comma
                    s = re.sub(r',\s*$', '', s)
                    # Count remaining open brackets
                    opens_b = s.count('{') - s.count('}')
                    opens_s = s.count('[') - s.count(']')
                    s += ']' * max(0, opens_s)
                    s += '}' * max(0, opens_b)

            return s

        repaired = _repair_json(clean)
        try:
            distilled = json.loads(repaired)
        except json.JSONDecodeError:
            # Last resort: find the outermost JSON object
            match = re.search(r'\{.*\}', repaired, re.DOTALL)
            if match:
                try:
                    distilled = json.loads(match.group())
                except json.JSONDecodeError:
                    pass

        if distilled is None:
            # Save raw text if JSON parsing fails
            distilled = {
                "source_id": source_id,
                "chunk_id": chunk_id,
                "parse_error": True,
                "raw_extraction": result_text,
            }

        # Save to disk
        os.makedirs(distill_dir, exist_ok=True)
        with open(distill_file, "w", encoding="utf-8") as f:
            json.dump(distilled, f, indent=2, ensure_ascii=False)

        log.info('[DISTILL OK] %s chunk %d -> %s', source_id, chunk_id, distill_file)

        # Return formatted result
        n_entities = len(distilled.get('entities', []))
        has_content = distilled.get('has_relevant_content', False)
        summary = distilled.get('summary', '')

        header = (
            f"DISTILLED: {source_id} chunk {chunk_id}\n"
            f"Relevant: {has_content} | Entities: {n_entities}\n"
            f"Summary: {summary}\n"
            f"Saved to: {distill_file}\n\n"
        )
        return header + json.dumps(distilled, indent=2, ensure_ascii=False)[:config.PROJECT_MAX_READ_CHARS]


# ==========================================
# TOOL: BATCH DISTILL SOURCE
# ==========================================
@register_tool('batch_distill_source')
class BatchDistillSource(BaseTool):
    description = (
        'Distill ALL chunks of a source through the configured reasoning model, one at a time. '
        'This is the bulk extraction tool — runs through every chunk and saves structured '
        'extractions to disk. Can resume from where it left off (skips already-distilled chunks). '
        'Use this when starting research on a new source. Returns a summary of what was found.'
    )
    parameters = [
        {
            'name': 'project_dir',
            'type': 'string',
            'description': 'Full path to the research project.',
            'required': True,
        },
        {
            'name': 'source_id',
            'type': 'string',
            'description': 'Source identifier to distill (e.g. "necro").',
            'required': True,
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': 'Research goal for extraction guidance.',
            'required': True,
        },
        {
            'name': 'max_chunks',
            'type': 'integer',
            'description': 'Optional. Max chunks to process in this batch (default: all). Use to limit time.',
            'required': False,
        },
    ]

    def call(self, params: str, **kwargs) -> str:
        params = parse_tool_params(params)
        project_dir = params.get('project_dir', '')
        source_id = params.get('source_id', '')
        goal = params.get('goal', '')
        max_chunks = params.get('max_chunks')

        manifest = _load_manifest(project_dir)
        if manifest is None:
            return "NO MANIFEST found. Run source_prep.py first."

        # Find the source in the manifest
        source_entry = None
        for src in manifest.get('sources', []):
            if src.get('id') == source_id:
                source_entry = src
                break
        if source_entry is None:
            return f"Source '{source_id}' not found in manifest."
        if source_entry.get('status') != 'ok':
            return f"Source '{source_id}' status is '{source_entry.get('status')}' — cannot distill."

        total_chunks = source_entry.get('total_chunks', 0)
        if max_chunks:
            total_chunks = min(total_chunks, int(max_chunks))

        distill_dir = os.path.join(project_dir, "data", "distilled", source_id)
        os.makedirs(distill_dir, exist_ok=True)

        # Instantiate the single-chunk distiller
        single = DistillSourceChunk()

        results_summary = []
        skipped = 0
        processed = 0
        total_entities = 0
        relevant_chunks = 0

        for i in range(total_chunks):
            distill_file = os.path.join(distill_dir, f"distilled_{i:03d}.json")
            if os.path.isfile(distill_file):
                # Already distilled — count its stats but don't re-process
                try:
                    with open(distill_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                    if existing.get('has_relevant_content'):
                        relevant_chunks += 1
                        total_entities += len(existing.get('entities', []))
                except Exception:
                    pass
                skipped += 1
                continue

            # Distill this chunk
            result = single.call(json.dumps({
                "project_dir": project_dir,
                "source_id": source_id,
                "chunk_id": i,
                "goal": goal,
            }))
            processed += 1

            # Parse the result to collect stats
            if os.path.isfile(distill_file):
                try:
                    with open(distill_file, "r", encoding="utf-8") as f:
                        distilled = json.load(f)
                    if distilled.get('has_relevant_content'):
                        relevant_chunks += 1
                        n_ent = len(distilled.get('entities', []))
                        total_entities += n_ent
                        results_summary.append(
                            f"  chunk {i}: {n_ent} entities — {distilled.get('summary', '')[:100]}"
                        )
                except Exception:
                    results_summary.append(f"  chunk {i}: processed (parse error)")

        report = (
            f"BATCH DISTILL: {source_id}\n"
            f"Total chunks: {source_entry.get('total_chunks', 0)}\n"
            f"Processed now: {processed} | Skipped (cached): {skipped}\n"
            f"Relevant chunks: {relevant_chunks} | Total entities: {total_entities}\n"
            f"Output dir: {distill_dir}\n"
        )
        if results_summary:
            report += "\nNEW FINDINGS:\n" + "\n".join(results_summary[:20])

        return report
