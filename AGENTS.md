# AGENTS.md — Operations Schema for munich-handbook-research

Operating rules for any agent (human or AI) working in this repo. Modeled on the
sibling `theology-philosophy-archive` schema, adapted for a distillation pipeline.

## Ground rules
1. **Never invent data.** Every entity in `data/distilled/` or `data/unified_entities.json`
   must trace to a chunk of a real source text, with provenance (source_id, chunk_id,
   quote/page ref). Unclear attributes get `NEEDS_VERIFICATION`.
2. **Provenance before ingest.** A source gets a `source_manifest.json` entry only with:
   title, author/translator, edition/printing, language, pages, sha256, staged path.
   If the text looks like an LLM digest (modern-summary voice, no folio refs, impossible
   provenance), QUARANTINE it under `data/sources/_quarantine_<date>_stubs/` with a
   `_QUARANTINE.md` — never silently delete, never ingest.
3. **Corrections are kept, not erased.** Wrong stats get corrected in place with a dated
   note (see `docs/CLEANUP_REPORT.md`, `docs/corrected_stats.json`, the 266→13 collapse).
4. **Binaries stay out of git.** `data/sources/original_pdfs/**` is gitignored (~400 MB).
   Stage PDFs there; commit manifest entries, not bytes.

## INGEST — adding a source
```
1. Stage PDF   → data/sources/original_pdfs/<id>.pdf ; compute sha256
2. Manifest    → add entry to data/sources/source_manifest.json (status: staged → ok;
                 staged_chunked = binary+chunks, distill queued; staged_ocr = scan awaiting OCR)
3. Chunk       → python scripts/ingest_new_sources.py --id <id>   (native) or --id <id> --ocr
                 (25k chars, 500 overlap → data/sources/<id>/chunk_NNN.txt)
4. Distill     → set MHR_REASONING_SERVER / MHR_REASONING_MODEL_ID / MHR_REASONING_NUM_CTX
                 (see Endpoints), then smoke-test one chunk:
                 python scripts/distill_source.py --id <id> --max-chunks 1
                 then the full run:
                 python scripts/distill_source.py --id <id>
                 → data/distilled/<id>/distilled_*.json  (resumable)
5. Merge       → normalize + fold into data/unified_entities.json
6. Log         → append entry to _meta/ingest-log.md (date, sha256, chunks, model used)
```
New grimoire-style sources (planet/direction/rank hierarchies) also need the schema
extensions sketched in `docs/expansion_sources.md` (`planet`, `direction`, `rank_numeric`,
`seal_reference`, `specialties`, `hours_of_power`).

## NIGHTLY QUEUE — LBP Grimoire Collection (staged 2026-10-27, START IS GATED)
- 47 tracks staged from `H:\THE GRIMOIRE COLLECTION\THE LBP GRIMOIRE COLLECTION`
  (37 chunked native via `scripts/stage_grimoire_collection.py`, 10 `staged_ocr`).
- Queue: `_meta/overnight_queue.json` (tiers A grimoire primaries / B scholarly-context /
  C modern-retrofit; value-first order; Infernal Dictionary's 135 chunks last).
  Per-track distill goals: `_meta/overnight_goals.json`.
- Runner: `bash scripts/run_overnight_queue.sh [A|B|C]` — endpoint health-check, then
  per-track smoke (`--max-chunks 1`) → full (resumable); log `_meta/overnight_run_*.log`.
  **Do not run until the user explicitly says to start.**
- Post-run merge is manual: 1:1 attestation review (goetia precedent); tier-C retrofit
  tracks merge as *retrofit-lineage* witnesses only, never as early sources; tier-B
  scholarly tracks never mint primary attestations.
- OCR backlog (`staged_ocr`): abramelin, book_of_black_magic (Waite), demonomanie (Bodin),
  godwin_necromancers, prayer_magick_stars, clavicula_nox, conway_demonology_v2,
  picatrix_book2_scan, greer_picatrix_scan, grand_grimoire_trident. Use
  `scripts/ingest_new_sources.py --id <id> --ocr` when scheduled.

## QUERY — answering research questions
- Entity/relationship questions → `data/unified_entities.json` first (source families:
  alchemy_mysticism, ars_notoria, discoverie, forbidden_rites_pdf, liber_juratus, necro,
  worship_dead, goetia; 47 further tracks staged but not yet distilled).
- Always report entity counts *per source track*, not raw totals — the DB contains
  known OCR/duplicate noise (see README data-accuracy notes).
- Cross-work attestation counts must use **distinct works**, never chunk-count overlap.

## LINT — run before every commit batch
```
python scripts/munich_pipeline_diagnostic.py
python scripts/verify_entity_provenance.py
```
Plus manual checks: README/manifest statistics match `data/unified_entities.json`;
nothing under `data/sources/` lacks a manifest entry; nothing ingestable sits in a
`_quarantine_*` dir. `index`/status documents (README.md, RESEARCH_MANIFEST.md,
_meta/ingest-log.md) must stay consistent — same invariant as the archive's lint.

## Endpoints (model of record may change; record what you used in the ingest log)
- Distiller reads `config.py`: `MHR_REASONING_SERVER` / `MHR_REASONING_MODEL_ID` env overrides.
- As of 2026-10-27: LM Studio (`:1234`, local and 192.168.50.150) was DOWN; the live
  endpoint is **Ollama** `http://localhost:11434/v1`, model `qwen3.5:122b` (OpenAI-compatible).
- Embeddings: Ollama `nomic-embed-text` (already used by `build_embeddings.py`).

## Known pitfalls
- `source_prep_expansion.py` regenerates the April stubs from inline text — it lives in
  quarantine; do not restore it.
- `necro` and `forbidden_rites_pdf` are the same book; never count them as cross-attestation.
- `otherworldglimmerings.pdf` (Boott Lee 1895) is staged in original_pdfs but has no track —
  decide deliberately (OCR cost) before ingesting.
- Scanned image PDFs (Splendor Solis, Aurora Consurgens) need `--ocr` (pytesseract) —
  test with `--test 5` pages first.
