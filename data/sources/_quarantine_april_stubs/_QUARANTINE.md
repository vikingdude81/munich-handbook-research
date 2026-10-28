# QUARANTINED — April-era synthetic stub sources

**Quarantined:** 2026-10-27 (audit, this session).
**Decision:** Removed from the live ingest queue (`data/sources/expansion/`) and preserved here, unchanged, for the audit trail. **Do NOT feed these to `source_prep_expansion.py` or any distillation run.**

## What these files are

Six artifacts recovered from the dead `E:\munich-handbook-research` tree in the June "Round 4" cleanup (commit `28d4cbb`): four "source" texts, their manifest, and the script that generated them. Each text is 3–5 KB of LLM-generated pseudo-scholarly prose, not a translation of any real work:

| File | Red flag |
|---|---|
| `FTTF_Fournier_Trial_Records.txt` | **Historically impossible.** Frames the Fournier inquisition as "Fournier v. The Accused, Toulouse 1598–1602." The real Fournier register is Jacques Fournier's episcopal inquisition at Montaillou, 1318–1325 (Cathar heresy, not witchcraft), and adversarial case captions do not exist in inquisitorial procedure. |
| `Picatrix_Liber_Apoteles.txt` | "Liber Apoteles" is not a Picatrix title; text self-describes as "translated and adapted for the Western tradition." The real *Ghāyat al-Ḥakīm* runs to hundreds of pages (Pingree Latin ed. / Attwood-Gray English ed.). |
| `Agrippa_De_Occulta_Philosophia.txt` | 5 KB digest of Book III in modern-summary voice. A real Agrippa edition is ~300+ pages. |
| `Bavarian_Stadtbuch_Witchcraft_Statutes.txt` | Paragraph-form "statutes" with modern phrasing; no cited folio/edition. |
| `expansion_manifest_v2.json` | Manifest whose entries embed the stub prose inline — one `source_prep_expansion.py` run from here could have contaminated `data/distilled/` and `data/unified_entities.json`. |
| `source_prep_expansion.py` | Generator. Contains the stub text inline; re-running it re-materializes the fakes. |

## Why quarantine instead of delete

The repo's own correction doctrine (`docs/CLEANUP_REPORT.md`, `analysis/hallucinated_spirits_analysis.md`) is: correct the record, keep the paper trail. Deleting would erase evidence of what was almost ingested.

## Verified damage: none

`data/unified_entities.json` was audited on 2026-10-27: all 2,763 entities trace to the 7 genuine tracks (`alchemy_mysticism`, `ars_notoria`, `discoverie`, `forbidden_rites_pdf`, `liber_juratus`, `necro`, `worship_dead`). No entity or distilled chunk derives from these stubs. The expansion track was never distilled.

## What replaces them

The real editions named in `docs/expansion_sources.md` (priority-1: Picatrix/Pingree or Attwood-Gray, Lemegeton/Goetia, Heptameron). First genuine replacement already ingested: `goetia` track from *The Lesser Key of Solomon* (Mathers 1904) — see `_meta/ingest-log.md`.
