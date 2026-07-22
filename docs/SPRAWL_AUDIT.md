# Duplicate-File Sprawl Audit — Keep/Delete Plan

**Status: EXECUTED (2026-06-20).** Option 2 chosen — the entire validator family
was deleted and replaced by one canonical validator. See "Execution outcome" at
the bottom. The proposal text below is retained for the rationale.

---

Read-only audit of same-named / overlapping files across the tree. Goal: decide
what is genuinely redundant vs. what only *looks* duplicated.

## Method & key facts established

- **Whole-tree exact-content scan:** the only byte-identical dups were two
  0-byte files and two re-run analysis JSONs — i.e. **no copied-in folder**.
- **Import graph:** grepped every `import` in the repo. The *only* cross-module
  imports are `from src.spirit_vectors …` and `from src.som_topology …`
  (used by `src/lgi_manifold.py`, `src/som_topology.py`). **None** of the
  duplicated utility/validator files are imported anywhere — they are standalone
  scripts or dead.
- **`main.py` (root) is already broken:** it does
  `from spirit_vectors import load_seed_spirits, FEATURE_NAMES, get_spirit_objects`
  — wrong module location (it's in `src/`) and `FEATURE_NAMES`/`get_spirit_objects`
  don't exist in it. Cannot run.
- **The validators target a schema that was never produced.** Copies of
  `validate_json.py` etc. check `spirit_name`, `rank`, `legion_count`,
  `conjuration_method`, `page_folio`. The actual distilled schema is
  `name`, `type`, `attributes`, `page_ref`, `raw_quote`. These validators are
  abandoned early drafts, not working tools.

---

## Category A — NOT duplicates, keep all (no action)

| Pattern | Why it's fine |
|---------|---------------|
| `data/distilled/<source>/distilled_000…038.json` | Per-source outputs. Same filename in different source dirs **by design** — `necro/distilled_004.json` ≠ `liber_juratus/distilled_004.json`. ~150 files. Leave entirely. |
| `__init__.py` ×3 (`src/`, `tools/`, `brain/`) | Package markers. Keep. |
| `design/spirit_models.py` vs `src/spirit_models.py` | **Different content** — design = full Pydantic `Spirit`/`Experiment`/`Rank`/`Provenance`; src = only `DistilledSpirit`. Not a dup. Keep both (optionally rename `design/` → `pydantic_schemas.py` for clarity). |
| `src/spirit_vectors.py`, `src/som_topology.py` | Canonical, imported. Keep. |

---

## Category B — Stale validators (dead schema, unimported) → **DELETE**

All check the never-used `spirit_name/legion_count/page_folio` schema; none
imported; all standalone. **8 files.**

| Delete | Note |
|--------|------|
| `validate_json.py` (root) | dead-schema draft |
| `scripts/validate_json.py` | dead-schema draft |
| `src/validate_json.py` | dead-schema draft |
| `data/validate_json.py` | dead-schema draft |
| `data/distilled/necro/validate_json.py` | a script sitting inside a **data output dir** — clearly misplaced |
| `chunk_validator.py` (root) | dup of `src/chunk_validator.py`, dead schema |
| `distilled_validator.py` (root) | dead-schema draft |
| `validate_distillation.py` (root) | dead-schema draft |

> Keep `src/chunk_validator.py` for now only as the least-bad reference; see
> Category E recommendation to replace the whole family with one validator that
> matches the **real** schema.

---

## Category C — Redundant validator variants (unimported, overlapping) → **DELETE after 1-line diff confirm**

Two-copy sets where one location is the obvious home (`src/` or `scripts/`) and
the other is a stray. **Recommend keeping the `src/` copy, deleting the stray.**

| Keep | Delete (stray) |
|------|----------------|
| `src/validate_jsonl.py` | `distill/validate_jsonl.py` |
| `src/validate_json_files.py` | `distilled/validate_json_files.py` |
| `src/validate_distilled_json.py` | `scripts/validate_distilled_json.py` |
| `src/validate_distillations.py` | `scripts/validate_distillations.py` |
| `src/json_validator.py` | `src/utils/json_validator.py` |
| `src/retry_failed_chunks.py` *or* `scripts/retry_failed_chunks.py` | the other (diff first — pick newer/complete) |

---

## Category D — Loose root-level clutter duplicating a canonical copy → **DELETE root copy**

Root has **15 loose `.py`** files; several duplicate a `src/`/`scripts/` file.

| Delete (root) | Canonical kept |
|---------------|----------------|
| `utils.py` | `src/utils.py` (2267 B vs 968 B — src is fuller) |
| `distill_utils.py` | `scripts/distill_utils.py` (2808 B, fullest) — also drop `src/distill_utils.py` if diff shows subset |
| `main.py` | **broken**, imports nonexistent names; delete or fix. Real entry points are `scripts/pipeline.py`, `scripts/run_full_distill.py`, `src/som_topology.py` |

> Other root one-offs (`batch_distillation.py`, `check_files.py`,
> `qrng_source.py`, `planetary_scheduler.py`, `robust_json_parser.py`,
> `distill_report_generator.py`, `distill_validation.py`) are **not** duplicated
> elsewhere — out of scope for *this* dedup pass (they're a separate "tidy the
> root" question).

---

## Category E — Duplicate docs → **CONSOLIDATE**

| Action |
|--------|
| `audit_report.md` ×3 (root, `docs/`, `src/distillations/`) → keep `docs/audit_report.md`, delete the other two |
| `VALIDATION_REPORT.md` (`distill/necro/`) vs `docs/validation_report.md` → keep `docs/`, delete the stray |
| `validation_report.sh` (`logs/` vs `data/`) → keep one, delete other |

---

## Judgment-call items (need a diff before deciding) — **5 files**

- `batch_distill_source.py`: `src/` (4 funcs) vs `utils/` (1 func — likely a stub). Probably delete `utils/` copy.
- `retry_failed_chunks.py`: `scripts/` (795 B) vs `src/` (635 B) — diff, keep fuller.
- `distill_utils.py`: 3 copies (root/scripts/src) differ in size — diff to confirm scripts/ superset before deleting the other two.

---

## Proposed totals

| Bucket | Files removed |
|--------|---------------|
| B — dead-schema validators | 8 |
| C — redundant validator strays | ~6 |
| D — root clutter dups | 2–3 |
| E — duplicate docs | 4 |
| **Total** | **~20 files** |

All removals via `git rm` (recoverable from history). **Zero** runtime imports
touched (verified none are imported). The `distilled_*.json` data and the `src/`
canonical modules are untouched.

## Bigger recommendation (separate task)

Replace the entire `validate_*` family with **one** validator in `src/` that
checks the **actual** schema (`name`/`type`/`attributes`/`page_ref`/`raw_quote`)
and the cross-grimoire/work fields. The current ~15 validators are all archaeology.

---

## Execution outcome (2026-06-20)

**Chose option 2: delete the whole validator family, write one correct validator.**

### Added
- **`src/validate_distillation.py`** — THE canonical validator. Checks the schema
  the pipeline actually emits (`name`/`type`/`attributes`/`page_ref`/`raw_quote`,
  relationships, parse_error placeholders) and the unified-DB structure. CLI with
  `--distilled-only` / `--unified-only` / `--json`; non-zero exit on hard errors.
  On first run it immediately found real signal the old family never could:
  - **1 hard error:** `data/distilled/worship_dead/distilled_038.json` entity[7]
    has a missing/empty `type`.
  - **9 parse_error stragglers** flagged for re-distillation.
  - **61 entities with no provenance** (no `page_ref` and no `raw_quote`) — relevant
    to the RESEARCH_MANIFEST "every spirit must cite chunk/passage" rule.
  - **100 distinct raw entity types** the normalizer's `TYPE_MAP` doesn't map
    (e.g. `angel`×111, `prayer`×61, `spiritual_name`×33, `device`, `cipher_method`).

### Removed — 50 files (the validator/verifier/schema/json-audit sprawl)
All were standalone scripts, **none imported anywhere**, and the JSON/spirit ones
checked the dead `spirit_name/legion_count/page_folio` schema.

- Root: `validate_json.py`, `validate_distillation.py`, `distill_validation.py`,
  `distilled_validator.py`, `chunk_validator.py`
- `scripts/`: `validate_json.py`, `validate_json.sh`, `validate_distill.sh`,
  `validate_distillations.py`, `validate_distillations.sh`, `validate_distilled.py`,
  `validate_distilled_json.py`, `validate_json_audit.py`, `validate_json_files.sh`,
  `validate_spirits.py`, `validate_csv_data.py`, `verify_distillation.py`,
  `verify_distilled_files.py`, `retry_validation.py`
- `src/`: `validate_json.py`, `validate_jsonl.py`, `validate_json_files.py`,
  `validate_chunks.py`, `validate_distillation_output.py`, `validate_distillations.py`,
  `validate_distilled_chunks.py`, `validate_distilled_files.py`,
  `validate_distilled_json.py`, `validate_distilled_jsons.py`, `verify_json_files.py`,
  `chunk_validator.py`, `json_validator.py`, `json_audit.py`, `schema_checker.py`,
  `spirit_validator.py`, `distillation_validator.py`, `audit_chunks.py`,
  `audit_files.py`, `audit_json_files.py`, `audit_utils.py`, `audit_validation.py`,
  `utils/json_validator.py`, `distillations/validate_chunks.sh`
- `data/`: `validate_json.py`, `validate_outputs.py`, `validation_report_generator.py`,
  `distilled/necro/validate_json.py`
- `distill/`: `validate_jsonl.py`, `verify.py`
- `distilled/`: `validate_json_files.py`

### Kept (deliberately)
- **`scripts/audit_experiments.py`** — genuine *content* analysis of the unified DB
  (experiments/summoning), not QA of file structure. (Note: still has a hard-coded
  `E:\…` path — separate fix.)
- `design/spirit_models.py` & `src/spirit_models.py` — different Pydantic models,
  not duplicates.

### Verified after deletion
- No remaining file imports or shells out to a deleted script (the lingering
  `validate_json` grep hits are each script's own in-file helper function).
- `docs/fanout_analysis.md` pointer updated to `src/validate_distillation.py`.
- `python src/validate_distillation.py` runs and reports as above.
