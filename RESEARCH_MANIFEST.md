# Munich Handbook Research Project
# CLM 849 — Spirits and Experiments from the Munich Handbook

*Refreshed 2026-10-27 audit. Previous version described the April 2026 state; paths and
model references below reflect the post-Round-4 consolidation (see `docs/CLEANUP_REPORT.md`)
and the 2026-10-27 quarantine + goetia ingest (see `_meta/ingest-log.md`).*

## Current Status
- Phase 1 ✅ Batch distillation of all CLM 849 chunks (39 `forbidden_rites_pdf` + 38 `necro`)
- Phase 2 ✅ `src/spirit_vectors.py` extended; SOM retrained 2026-07-22 (QE 0.146 / TE 0.016)
- Phase 3 ✅ `src/experiments.py` + 6 conjuration-as-agent experiments in `experiment_results/`
- Phase 4 ✅ `goetia` track (Lemegeton/Goetia via Mathers 1904): 6 chunks → 78 entities
  (Ollama qwen3.5:122b) → merged 2026-10-27 via `scripts/merge_goetia_into_unified.py`;
  1:1 cross-check vs the Munich commander tier: **Paimon only** exact CLM 849 match,
  doublet spellings held in a review queue (see `_meta/ingest-log.md`).
- Phase 5 (open): OCR decisions for image-only scans (`splendor_solis`, `aurora_consurgens`);
  ingest decision for staged `otherworld_glimmerings` (Boott Lee 1895, secondary source).

## File map (current)
- `data/sources/<track>/chunk_*.json|txt` — chunked sources (8 tracks + separate analysis tracks)
- `data/distilled/<track>/chunk_*.json` — per-chunk LLM extractions
- `data/unified_entities.json` — merged DB (2,828 entities / 1,275 relationships / 151 chunk summaries)
- `data/sources/_quarantine_april_stubs/` — **DO NOT INGEST** April-era synthetic stubs; rationale inside
- `data/sources/original_pdfs/` — original binaries (382 MB, gitignored)
- `tools/source_distill.py` — core LLM extraction tool (endpoint per `config.py`;
  historically LM Studio, last recorded `google/gemma-4-26b-a4b`; "120B Thinker" mentions
  in older docs reflect an earlier/aspirational setup)

## Rules
- Never invent data — every entity must come from distilled extraction
- Every spirit must have provenance citing exact chunk and passage
- If attributes unclear, add with NEEDS_VERIFICATION flag
- **New (2026-10-27):** source texts must be verifiable editions with provenance (title,
  edition/translator, sha256) in `data/sources/source_manifest.json`. Suspected synthetic
  texts get quarantined with a `_QUARANTINE.md`, never silently deleted or ingested.
  Log every ingest in `_meta/ingest-log.md` before closing a session.
