# Ingest Log — munich-handbook-research

Newest first. Every source ingest, quarantine, correction, or corpus-affecting action
gets an entry here (see `AGENTS.md`). Historical entries backfilled from
`docs/CLEANUP_REPORT.md` during the 2026-10-27 audit.

---

## 2026-10-27 — Audit, quarantine, and Goetia ingest (this session)
- **Audit:** full-repo pass vs. sibling archive schema. Verified DB clean: 2,763 entities /
  1,260 rels / 147 chunk summaries, all source keys trace to genuine tracks.
- **Quarantine:** 4 April-era synthetic "expansion" texts + `expansion_manifest_v2.json` +
  `source_prep_expansion.py` moved (git mv) to `data/sources/_quarantine_april_stubs/`.
  Rationale in `_QUARANTINE.md` (FTTF anachronism, Picatrix fake title, digest-voice stubs).
  Zero distilled contamination found.
- **Schema ported:** `AGENTS.md` (INGEST/QUERY/LINT), this log, RESEARCH_MANIFEST.md refresh,
  README stale-stat fixes (2,467→2,763; 1,200→1,260; 99→147; "5 sources"→7 tracks).
- **Staged PDFs (original_pdfs/, gitignored):**
  - `lesser_key_of_solomon_1904.pdf` — *The Lesser Key of Solomon* (Mathers 1904 trans.,
    1904 Schleier reprint scan), 107 pp, sha256 `7f84607342627d27f9a58207eb3f1d8abf671b0e45c305abdc122963816fffc2` — from `Downloads/`.
  - `splendor_solis_taschen.pdf` — Splendor Solis facsimile (Taschen), 112 pp, 97 MB
    (higher-res than the 39 MB Downloads copy), sha256 `f7e7b1433bbe246f28df11d3930f972aab991e102037e377bf88e6b4daeb7e32` — from `D:\EBOOK/`.
    Image-only; needs `--ocr` when a track is opened for it.
- **New track `goetia`:** 121,284 chars → **6 chunks** (`data/sources/goetia/chunk_000..005.txt`,
  25k/500 via `ingest_new_sources.py --id goetia`; spot-check clean Mathers text).
  Runner `scripts/distill_source.py` written (old `run_full_distill.py` had dead E:\ paths);
  `MHR_REASONING_NUM_CTX` env support added for Ollama (default ctx silently truncates).
  Distillation: endpoint = Ollama `qwen3.5:122b` @ localhost:11434, num_ctx 32768 (LM Studio down).
  Integration mode: 1:1 cross-check vs. Munich commander tier per expansion plan.
- **Distillation result (proc finished 17:42, 57.8 min):** qwen3.5:122b — 6/6 chunks relevant,
  **78 entities, 0 errors** (`_meta/distill_goetia.log`). Attributes extracted match the
  `docs/expansion_sources.md` schema ask: sequence_number, rank, direction, legions, form,
  functions, page_ref, raw_quote.
- **Merge:** `scripts/merge_goetia_into_unified.py` — 13 name-matches folded into existing
  entities (Solomon, Lemegeton, Agares, Marbas, Amon, Barbatos, Paimon, Buer, Bathin,
  Tetragrammaton, Michael, Seal of Solomon, Circle; duplicate canonical entries folded too),
  **65 new `goetia_exclusive`** entities, 15 relationships, 4 chunk summaries.
  Fuzzy doublets reported, NOT merged (review queue): Bael~baell/bel/bal, Beleth~bileth,
  Purson~curson, Balam~balaam, Alloces~aloes, Octinomos~occinomos/occinnomos,
  Magical Circle~magical circles, Pentacle of Solomon~seal of solomon.
  Work id `goetia_lemegeton` added (7th distinct work).
- **Post-merge LINT:** `munich_pipeline_diagnostic.py` modernized (old version targeted dead
  E:\ paths + April iteration logs; now enforces AGENTS.md invariants: metadata counts,
  provenance prefixes, cross_work consistency, manifest<->sources-dir agreement, quarantine
  hygiene, doc stats). `verify_entity_provenance.py`: 99.2% quote-verified, 21 unverified
  candidates — all PRE-EXISTING (liber_juratus:chunk_15 Latin quotes, forbidden_rites/necro
  chunk-boundary artifacts); zero goetia contamination.
- **Manifest rot found + repaired** (`scripts/normalize_source_manifest.py`): manifest still
  carried the April-era schema — legacy entries with status `"ok"` and dead `H:\` paths,
  no entries for `discoverie`/`alchemy_mysticism`/`de_occultis*`, and `malleus_maleficarum` +
  `karl_marx` mislabeled `ingested` (they are analysis corpus, 162 + 61 chunks under the
  consolidated `data/sources/malleus_marx/`). Now 15 entries: 8 ingested tracks (with
  `chunks_dir`/`chunk_count`), 4 analysis, 2 staged, 1 scanned_images; all paths repo-relative
  into `original_pdfs/`. Empty `data/sources/expansion/` husk removed. Lint now enforces
  status vocabulary + chunks_dir/distilled_dir mapping and chunk-dir coverage.
- **Doublet lead (review queue):** Goetia #53 **Octinomos** vs Munich CLM 849 spirit
  **"Otaizomos / Occinomos"** (`forbidden_rites_pdf:chunk_30`) — same name appears in BOTH
  rosters under variant orthography; strongest cross-work attestation candidate found by
  this merge. Not merged pending doctrine; would promote multi-WORK count if confirmed.
- **Post-merge DB:** 2,828 entities / 1,275 rels / 151 summaries / 8 tracks; spirit records
  1,330→1,367; multi-WORK spirits 21→28. README + RESEARCH_MANIFEST synced. Pre-merge DB
  backup kept locally (`unified_entities_pre_goetia.json.bak`).
- **1:1 Munich cross-check headline:** of the 72 Goetia spirits, exactly **one** (Paimon, #9)
  appears under exact name in the CLM 849 entity set — the rosters are largely independent
  traditions; doublets hide under variant orthography (queue above).
- **Staged, no track:** `otherworldorglim01leef.pdf` — Boott Lee, *Otherworld Glimmerings*
  (1895), 308 pp, sha256 `3eb59d71e67ffd61c461d56542111500018ca523d5e87911e3cd93dcb1d6f823`,
  from `D:\EBOOK` (dup in Downloads). Companion secondary source to `worship_dead`;
  text layer present (no OCR needed) — ingest decision pending.
- **Book hunt (user hint: E:\ demonology/witchcraft/grimoire):** no such folders on E:\.
  `FTTF-fournier (1)/(2)` are false friends — a Fourier-analysis neuroevolution project, not
  Fournier inquisition records. The e-book corpus is `D:\EBOOK`; its occult holdings are now
  all staged (Aurora Consurgens, Forbidden Rites ×2, NECRO.txt, Splendor Solis,
  Worship of the Dead, Otherworld Glimmerings).

## 2026-07-22 — SOM retrain (recorded in README)
- Retrained 15×15 SOM on 1,180 attributed spirits over the full 7-source corpus
  (QE 0.1457 / TE 0.0161 / 98 populated cells). Discovery track (multi-works 266→13)
  and independent Scot attestation (9 commanders) recorded in `docs/corrected_stats.json`.

## 2026-06-20 — Round 4 consolidation (from docs/CLEANUP_REPORT.md)
- Toolchain recovered from dead `E:\munich-handbook-research` into `src/`, `scripts/`.
- All 10 original source texts consolidated to `data/sources/original_pdfs/` (gitignored,
  ~382 MB). Alchemy & Mysticism re-ingested (30 chunks). Expansion sources moved to
  `data/sources/expansion/` *(→ later recognized as stubs, quarantined 2026-10-27)*.
- Model claims corrected: config aligned to `google/gemma-4-26b-a4b` (LM Studio), not "120B Thinker".

## 2026-06 — Discoverie + Alchemy tracks
- `discoverie` (Scot 1584, `b21720307.pdf`) distilled + analyzed (planetary conjuring).
- `alchemy_mysticism` (82 MB scan, 30 chunks) re-ingested after Round 4.

## 2026-04 — Initial corpus
- `necro` (H:\NECRO.txt, 39 chunks) + `ars_notoria` (Kieckhefer MS Laud Misc 632 ed.) +
  `liber_juratus` (Peterson ed.) + `worship_dead` (49 chunks) distilled through era model.
- `forbidden_rites_pdf` (Kieckhefer PDF) ingested — later found to duplicate `necro`.
