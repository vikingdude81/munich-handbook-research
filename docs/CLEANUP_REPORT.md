# Cleanup & Correction Report — 2026-06-13

Audit of the Munich Handbook research project from an AI-research and
historical-accuracy standpoint, with the fixes applied in this pass. Nothing
destructive was done to the primary data: `data/unified_entities.json` was left
untouched and corrections were written to a side file.

---

## Summary of what changed

| Area | Before | After |
|------|--------|-------|
| Multi-source spirits | "266" (book vs. itself) | **13** genuine cross-work |
| Grimoire count | "5 grimoires" | **3** works + 1 dup + 1 non-grimoire |
| `worship_dead` | "necromantic practice context" | labelled 1909 modern secondary |
| SOM training | "2000 epochs" (really ~1.6) | `use_epochs=True`, honestly 2000 |
| Heresy/Marx conclusion | hard-coded f-string | derived from measured deltas + caveat |
| `tools/source_distill.py` | `import config` → crash | standalone `config.py` added |
| Duplicate files | 3 `source_distill*` copies | 1 canonical |
| Hard-coded `E:\…` paths | absolute, box-specific | repo-relative + env override |

---

## 1. Data-accuracy fixes

### 1a. The "266 multi-source spirits" inflation (biggest issue)
`necro` (`H:\NECRO.txt`) and `forbidden_rites_pdf` are the **same book** —
Kieckhefer's *Forbidden Rites* (the Clm 849 study), ingested twice. Measured
5-gram Jaccard between matching chunks ≈ **0.74**. The old stat counted a spirit
appearing in both ingests as "multi-source."

- Introduced a canonical **`WORK_ID`** map (`necro` + `forbidden_rites_pdf` →
  `kieckhefer_clm849`).
- Recomputed cross-references at the **work** level:
  - OLD multi-source spirits: **266**
  - …of which the same-book pair only: **253**
  - **CORRECTED genuine multi-work spirits: 13**
- Non-destructive artifacts written:
  - `data/unified_entities.corrected.json` — copy of the DB with per-entity
    `distinct_works` / `cross_work` fields added (originals preserved).
  - `docs/corrected_stats.json` — machine-readable corrected summary.
- New script: **`scripts/correct_cross_grimoire_stats.py`** (re-runnable, never
  overwrites the live DB).

### 1b. `worship_dead` is not a grimoire
The chunk title page identifies it as **Colonel J. Garnier, *The Worship of the
Dead* (Chapman & Hall, 1909)** — a Victorian/Edwardian comparative-mythology
tract on Egyptian/Babylonian paganism, **not** a medieval necromantic manual.
- Manifest description corrected (`data/sources/source_manifest.json`).
- README reclassifies it as modern secondary context, excluded from the
  grimoire count.

### 1c. Sparsity caveat on the spirit corpus
**872 / 1254 (70%)** spirit records occur exactly once and **145** have zero
attributes. The headline "1,254 spirits" is inflated by OCR fragments, Latin
case-variants, and single-occurrence noise. README now states the defensible
count is in the low hundreds.

---

## 2. Method / findings fixes

### 2a. Heresy & Revolution — hard-coded conclusion removed
`scripts/distill_heresy_revolution_v3.py::cross_document_analysis()` previously
wrote a fixed `interpretation` string that **always** "confirmed the ressentiment
hypothesis" regardless of the numbers. Replaced with text derived from the actual
measured deltas, plus an explicit instrument caveat:
- Scores come from a **1-10 rubric** applied by a **single nano-scale judge**
  (`nemotron nano`) at temp 0.1, **no control corpus, no inter-rater check**.
- Both texts park at avg entropy ≈ 7.3 and **never exceed 8** — rubric-anchoring
  to the central "heavy deconstruction" band. The near-identical profile is the
  expected output of the instrument, not independent evidence of a shared
  psychological mechanism.

> This finding should be treated as a hypothesis-generating essay, not a measured
> result, until a control corpus and a stronger/multi-model judge are added.

### 2b. SOM "2000 epochs" mislabel
`src/som_topology.py` called `train_random(data, 2000)`, which draws 2000 random
samples total — only ~1.6 passes over 1,254 spirits. Now uses
`som.train(data, 2000, use_epochs=True)` so the count means full epochs, and
`som_metrics.json` carries a degeneracy caveat (the "Unnamed Host" mega-cluster
of 436 is largely the all-zero null bucket; low QE/TE partly reflect that, not
topology quality).

### 2c. Cross-grimoire SOM feature corrected
`src/spirit_vectors.py::_source_features` counted raw source prefixes, so the
duplicated Kieckhefer text inflated `source_count` and the `cross_grimoire` flag.
Now counts **distinct works** (`max_sources=3`). Verified: the `cross_work`
feature now fires for exactly **13** spirits (was 266).

> Note: committed `som_output/` artifacts predate these fixes and should be
> regenerated. SOM was **not** retrained in this pass (requires `minisom` +
> compute and would change published figures).

---

## 3. Code / structure fixes

- **`config.py` added** at repo root so `tools/source_distill.py` runs
  standalone (was `import config` against an external host module). All values
  env-overridable; no secrets hard-coded.
- **Repo-relative paths** in `scripts/normalize_entities.py` (was
  `E:\munich_handbook_research\…`), with `MHR_DISTILLED_DIR` / `MHR_DATA_DIR`
  overrides.
- **Loader bug fixed:** `normalize_entities.py` only iterated 3 source ids while
  the live DB has 5; now iterates all 5. (The live DB was generated by a newer
  version of this script that had been overwritten — re-running the old code
  would have silently dropped `ars_notoria` and `liber_juratus`. The loader is
  fixed but was **not** re-run, to avoid touching the live DB.)
- Dynamic `generated` date + `distinct_works` in DB metadata.

---

## 4. Files removed

| File | Reason |
|------|--------|
| `tools/source_distill_clean.py` | Byte-identical duplicate of `source_distill_restored.py`; unreferenced |
| `tools/source_distill_restored.py` | Byte-identical duplicate; unreferenced |

Canonical `tools/source_distill.py` retained.

---

## 5b. Validator consolidation — DONE (2026-06-20)

The validator sprawl was eliminated. **50 standalone validate_/verify_/audit_/
schema_checker scripts deleted**, replaced by one canonical
**`src/validate_distillation.py`** that checks the real schema. Full inventory and
rationale in [`docs/SPRAWL_AUDIT.md`](SPRAWL_AUDIT.md). The new validator runs on
the live data and surfaces a real `type` bug, 9 parse-error stragglers, 61
provenance gaps, and 100 unmapped raw types. `scripts/audit_experiments.py` (DB
content analysis) was kept.

## 5. Recommended next steps (not done in this pass)

- **Consolidate JSON-repair implementations.** 4+ remain (`robust_json_parser.py`,
  `src/json_repair_utils.py`, `src/json_recovery.py`, `src/utils/json_fix.py`, the
  inline `_repair_json` in `source_distill.py`). Pick one ladder (the
  `distill_heresy_revolution_v3.py` ladder is the best) and delete the rest.
- **Fix the 1 hard error + 9 parse-error chunks** the validator flagged.

## 5c. TYPE_MAP coverage extension — DONE (2026-06-20)

Extended `scripts/normalize_entities.py::TYPE_MAP` to absorb the high-frequency
raw types that were collapsing to `unknown`. Mappings were verified against actual
entity names before assigning, e.g.:

| Raw type | → canonical | Evidence (sample names) |
|----------|-------------|-------------------------|
| `angel`, `archangel`, `ruling_angel` | spirit | Michael, Raphael, Gabriel, Kasiel |
| `demon` | spirit | Asmodeus, Bileth, Satan |
| `king` | spirit | Maimon, Arcan, Barthan (directional demon-kings) |
| `servant`, `wind` | spirit | Aboumaleth; Hebetel, Halmitab (named wind-spirits) |
| `sacred name`, `blessed name` | divine_name | Tetragrammaton, Agla, Sabaoth, Adonay |
| `material`, `substance` | ingredient | iron gall ink, wine, fire |
| `device`, `sigil`, `seal` | tool | wax tablet, vessel; Golden Seal, Seal of God |
| `cipher_method`, `method`, `historical_example` | concept | letter transposition; Timoxenus of Sicily |
| `cultural group` | person | Chaldeans, Etruscans |

**Verified (function-level + end-to-end dry run into a temp dir, live DB untouched):**
- raw types → `unknown`: **18 distinct / 274 entities → 5 distinct / 5 entities**
  (only rare singletons remain).
- merged `unknown` entities: **18 → 6**; total merged entities **2467 → 2460**
  (formerly-`unknown` records like "Michael"/"Satan" now merge into their existing
  spirit records instead of orphaning — improved dedup).

> To apply this to the live `data/unified_entities.json`, re-run
> `python scripts/normalize_entities.py` (deterministic, no LLM; also folds in the
> `distinct_works`/`cross_work` fields). Left for the user to trigger so the
> committed DB isn't overwritten without sign-off.
- **Retrain the SOM** on attributed spirits only and regenerate `som_output/`.
- **Promote** `unified_entities.corrected.json` → `unified_entities.json` after
  review (or re-run the fixed `normalize_entities.py` against the full
  `data/distilled/` tree).
- **Unify chunking.** The two sub-projects use different chunkers (PyMuPDF 25k
  paragraph-aware vs. PyPDF2 10k line-based). Standardize on PyMuPDF and strip
  chunk-header/page-marker noise before it reaches the extraction prompt.
- **Add a control corpus + multi-model judge** to the entropy analysis before
  presenting the Malleus↔Marx parity as a result.

---

## Verification performed

- `ast.parse` on all edited Python files — OK.
- `import config` — OK.
- `spirit_vectors.load_seed_spirits()` → shape `(1254, 28)`, `cross_work`
  nonzero = **13** (matches corrected stats).
- `correct_cross_grimoire_stats.py` run — produced corrected artifacts.
- `source_manifest.json` re-parsed as valid JSON after edit.

---

# Round 2 — Tier 1-4 fixes (2026-06-20)

## Tier 1 — quick wins
- **`requirements.txt`** — added the missing core deps: `openai`, `pydantic`,
  `PyMuPDF`, `PyPDF2` (the project was previously un-installable for its own
  pipeline). Annotated each dep with where it's used.
- **`main.py`** — was broken (imported non-existent `FEATURE_NAMES`/
  `get_spirit_objects`, used the renamed `epochs=` kwarg). Rewritten as a thin,
  working launcher that delegates to `src/som_topology.run_full_pipeline`.
- **Hard-error data fix** — `worship_dead/distilled_038.json` "Baal (Sun god)"
  had no `type`; set to `deity`. Validator now reports 0 hard errors.
- **`scripts/audit_experiments.py`** — replaced hard-coded `E:\…` DB path with a
  repo-relative path (+ `MHR_UNIFIED_DB` override).

## Tier 2 — data
- **Regenerated `data/unified_entities.json`** (deterministic, no LLM). Found and
  fixed a **Windows-only crash**: the script hit `UnicodeEncodeError` on a `→` in
  a relationship type *during a diagnostic print that runs before the save*, so
  the regen had never actually worked on this machine. Added UTF-8 stdout. New DB:
  - entities **2467 → 2460** (better dedup), spirits **1254 → 1256**,
    `unknown` types **18 → 5**, `deity` **16 → 17**, dated today.
  - `cross_work` now baked in: **13** cross-work spirits (the corrected
    cross-grimoire figure), plus `distinct_works` on every entity.
  - Validator: **PASS, 0 errors, 0 warnings.** Vectorizer reads 13 cross_work.
  - Removed the now-superseded `unified_entities.corrected.json`.
- **Provenance report** → `docs/provenance_gaps.json`. At the merged-DB level only
  **1 spirit** has zero provenance (24 lack a page_ref but have quotes) — far
  better than the 61 chunk-level count, because merges aggregate provenance.
- **Orphaned sources documented** (README): `de_occultis` (26 distilled chunks,
  steganography — kept separate by domain), `discoverie` (analyzed via its own
  script, not distilled). Neither folded into the spirit DB by design.

## Tier 3 — sprawl
- **One JSON-repair module** — `src/json_repair.py` (the proven v3 ladder, with
  self-test). Deleted 4 dead unimported impls (`robust_json_parser.py`,
  `src/json_repair_utils.py`, `src/json_recovery.py`, `src/utils/json_fix.py`).
- **Root clutter** — deleted root `utils.py`, `distill_utils.py` (dups of
  `src/`/`scripts/` copies, unimported).
- **Duplicate docs** — kept `docs/audit_report.md`; deleted root + 
  `src/distillations/` copies, the stray `distill/necro/VALIDATION_REPORT.md`,
  and a duplicate `data/validation_report.sh`. (10 files total this tier.)

## Tier 4 — research-validity / structural
- **`src/chunking.py`** — canonical cleaner + token-aware chunker replacing the
  two divergent ad-hoc chunkers. `clean_source_text()` strips ingestion headers,
  `--- PAGE N ---` markers, `�` chars, and de-hyphenates line-broken words;
  `chunk_text()` is token-budgeted and tracks the overlap region so it isn't
  re-extracted. Wired into `source_prep.py` (clean before chunk) and
  `tools/source_distill.py` (strip header before the model sees the text).
  Self-test passes.
- **SOM honesty** — `load_seed_spirits(require_attributes=True)` added and used by
  `run_full_pipeline`; drops the **145** zero-attribute spirits (1256 → 1111) that
  created the spurious "Unnamed Host" mega-cluster and the misleadingly low QE/TE.
- **Heresy methodology** — added a prominent "Methodology limitations" section to
  `RESEARCH_METHODOLOGY.md` (control corpus, stronger/multi-model judge, inter-rater
  reliability all required before the entropy-parity claim stands).

## Blocked on the (offline) LLM server — ready to run, not executed here
- Re-distilling the **9 parse-error chunks** (needs the model endpoint).
- Re-running the heresy pipeline with a control corpus + stronger judge.
- **SOM retrain / regenerate `som_output/`** — `minisom` isn't installed in this
  environment; the code is fixed (`require_attributes=True`), so a retrain where
  `minisom` exists will regenerate honest figures.

---

# Round 3 — Recovery from the AI_Command_Center host (2026-06-20)

Explored `C:\Users\akbon\Projects\AI_Command_Center` (the host system the
distill tools were written for) plus the still-attached `E:\munich_handbook_research`
and `H:\` research drives. Findings:

## Recovered into the repo
- **`data/distilled/necro/distilled_020.json`** — a fully valid distillation
  (33 entities: the CLM 849 spirit-hierarchy ranks — marquis, president, count,
  duke, prince, king) that existed only on E: and was never copied to the repo.
  DB regenerated: **2,460 → 2,472 entities, 1,256 → 1,258 spirits**; validator PASS.
- **`ontology/ars_notoria.ttl`** — RDF/Turtle ontology sketch from E:'s
  `ontology/` dir (a directory the repo never had).

## Located (not yet re-ingested)
- **The Alchemy & Mysticism source PDF exists**:
  `C:\Users\akbon\Downloads\Alchemy___Mysticism_-_Taschen__2003__text.pdf` (82.5 MB).
  The `alchemy_mysticism` ingest can be re-run via
  `python scripts/pipeline.py` (needs PyMuPDF installed) — resolves the
  "data-missing" flag in APPS_MAPPING_AUDIT §4.
- All other source PDFs (Malleus, Marx, Ars Notoria, Sworn Book) are still in
  Downloads.

## Facts established from the host
- **Host `config.py` shows the last-configured distillation model was
  `google/gemma-4-26b-a4b`** — NOT a "120B Thinker" as the README/tool
  docstrings claim, and not the nemotron default I put in the repo's
  `config.py`. The "distilled through the 120B Thinker" framing should be
  treated as aspirational/stale unless an earlier config revision proves
  otherwise.
- Host `normalize_entities.py` is the 5-source version that generated the
  April DB — confirming the repo's 3-source copy was stale (already fixed in
  Round 2, and the repo version now supersedes the host's: WORK_ID collapse,
  UTF-8 fix, extended TYPE_MAP).
- Host `source_prep.py` includes the ars_notoria + liber_juratus entries the
  repo copy lacks (repo copy still lists only the original 4 sources — cosmetic,
  since chunking is already done).
- The 9 parse-error chunks are **parse errors on E: as well** — no rescue
  possible; they genuinely require LLM re-distillation.

---

# Round 4 — Consolidation, alchemy re-ingest, model-claim fixes, Draper deploy (2026-06-20)

## Consolidation from E: / host into the repo
- **Entity/KG toolchain recovered → `src/`** (22 modules + extractors + data):
  `summoning_engine`, `symbolic_engine`, `entity_resolver`, `entity_resolution`,
  `entity_loader`, `divine_name_extractor`, `fuzzy_disambiguate`,
  `ontology_generator`, `knowledge_graph(_schema)`, `ritual_engine`,
  `ritual_constraints_extractor`, `ars_notoria_*` (analyzer, divine names,
  graph builder, extractor, schema), `map_entities_to_folios`, `io_utils`,
  `writeback`, `loader`/`file_loader`, `load_munich_entities`, + `src/data/*.json`.
- **Scripts** → `scripts/`: `normalize_divine_names.py`,
  `munich_pipeline_diagnostic.py`, `entity_writer.py`.
- **Reference data** → `data/`: `entities.json`, `divine_names.json/.csv`,
  `general_abilities.json`, `metadata/master_index.csv`, `munich_entities.json`.
- **Expansion sources** → `data/sources/expansion/`: Agrippa *De Occulta
  Philosophia*, Picatrix (Liber Apoteles), Fournier trial records, Bavarian
  Stadtbuch witchcraft statutes + the v2 chunk/embedding manifest.
- **Docs** → `docs/`: loader_audit, research_summary, notes_analysis,
  extraction_analysis, ability_levels, prerequisites.
- **All 10 original source texts** (NECRO.txt + 9 PDFs incl. the 82 MB Alchemy &
  Mysticism scan) consolidated to `data/sources/original_pdfs/` — **gitignored**
  (382 MB of binaries stay out of git history).
- Deliberately NOT copied: E:'s copies of the deleted validator/JSON-repair
  sprawl, logs, `.env`.

## Alchemy & Mysticism re-ingested
`python scripts/pipeline.py run --source alchemy_mysticism --stage ingest` →
**30 chunks** in `data/sources/alchemy_mysticism/`. Resolves the data-missing
flag from APPS_MAPPING_AUDIT §4. Distillation stage still requires the LM Studio
endpoint (offline at audit time).

## "120B Thinker" claims corrected
- `tools/source_distill.py` docstrings now say "configured reasoning model
  (see config.py; last recorded: gemma-4-26b)".
- Repo `config.py` default model aligned to the host's actual last-recorded
  `google/gemma-4-26b-a4b`.
- README Infrastructure section notes the discrepancy explicitly. Essay docs
  (mapping, conjuration_theory) retain "120B" as historical narrative.

## Draper v1+v2 merge — deployed to Hugging Face
- Ported v1's **Conjuring Circle tab** (SVG circle, divine-name ring, Scot
  *Discoverie* Bk XV context) and **Julian date labeling** into v2, alongside
  v2's alchemy features. 7 content tabs total.
- Verified locally (all tabs, zero errors), then deployed to
  `Vikingdude81/the-sphere-of-hew-draper` (commit da0f7e7) and **live-verified**
  on the Space: renders, Circle+Bruno both present, Julian label shown.
