"""stage_grimoire_collection.py — stage H:\\THE GRIMOIRE COLLECTION into the repo.

Staging ONLY: copies selected PDFs into data/sources/original_pdfs/ (gitignored),
extracts text (fitz, PAGE markers), chunks via canonical pipeline, and writes
manifest entries with status 'staged*' — nothing is distilled here.

Tiers:
  A = priority overnight distill queue (grimoire primary sources, text layer)
  B = secondary scholarly/context tracks (queue night 2+)
  C = modern (re)constructions — separate retrofit-lineage layer (not queued)
  D = image-only scans — staged for OCR backlog

Skips: __MACOSX junk, exact sha256 duplicates, books already distilled in repo.
"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.chunking import clean_source_text  # canonical cleaner

CHUNK_SIZE, CHUNK_OVERLAP = 25000, 500
H = Path(r"H:\THE GRIMOIRE COLLECTION\THE LBP GRIMOIRE COLLECTION")
OP = ROOT / "data" / "sources" / "original_pdfs"
MAN = ROOT / "data" / "sources" / "source_manifest.json"
TODAY = "2026-10-27"

# (track_id, [H-filenames], staged filenames, tier, label, author, date, license, note)
TRACKS = [
 ("picatrix_english", ["Greer_and_Warnock_(transl.)_-_The_Picatrix_(Liber_Rubeus_Edition).pdf"],
  ["picatrix_liber_rubeus_greer_warnock.pdf"], "A",
  "Picatrix — Greer & Warnock trans. (Liber Rubeus ed.)", "Greer & Warnock (transl.)", "ed. 2004 (Arabic orig. ~1000 CE)",
  "modern copyrighted translation; staged for private research", "Wishlist priority-1 expansion; English text of Ghayat al-Hakim; entity-rich: planetary spirits, talismans, invocations."),
 ("picatrix_latin", ["picatrix_pingree.pdf"],
  ["picatrix_pingree_latin.pdf"], "A",
  "Picatrix — Pingree critical Latin edition", "David Pingree (ed.)", "ed. 2001 (Latin recension)",
  "modern critical edition; staged for private research", "Latin recension; witness for latin-form spirit names. 'PICATRIX - Latin Warburg Edition.pdf' is an exact duplicate — skipped."),
 ("key_of_solomon", ["The Greater Key of Solomon 1.pdf", "The Greater Key of Solomon 2.pdf",
  "The Greater Key of Solomon 3.pdf", "The Greater Key of Solomon - Order of the Pentacles.pdf"],
  ["greater_key_mathers_bk1.pdf", "greater_key_mathers_bk2.pdf", "greater_key_mathers_bk3.pdf", "greater_key_mathers_pentacles.pdf"], "A",
  "The Greater Key of Solomon — Mathers trans.", "S.L. MacGregor Mathers (transl.)", "1901",
  "public domain (translation 1901)", "Theurgic mirror of the Goetia track: consecration apparatus, circle/hexagram/pentacles, four kings + directional spirit classes; 4 part-files concatenated with FILE markers."),
 ("arbatel", ["arbatel.pdf"], ["arbatel.pdf"], "A",
  "Arbatel de Magic veteres — Olympic spirits", "anon. (Latin 1559; trans. 17th c.)", "1559",
  "public domain", "19 Olympic planetary governors + witnesses, lots, hours, prayers — new planetary topology layer."),
 ("grand_grimoire", ["Grand Grimoire.pdf"], ["grand_grimoire_llewellyn.pdf"], "A",
  "The Grand Grimoire / The Red Dragon", "anon.", "18th c. (Llewellyn reprint)",
  "public domain text; reprint scan", "Lucifuge Rofocale hierarchy + pact formulas. 'Dark Lodge version' is byte-identical — skipped. Trident version is image-only — Tier D."),
 ("black_pullet", ["Black Pullet.pdf"], ["black_pullet.pdf"], "A",
  "The Black Pullet (La Poule Noire)", "anon.", "19th c.",
  "public domain", "Ring/conjuration cabal of 43 spirits w/ seals."),
 ("ars_almadel", ["Ars Almadel.pdf"], ["ars_almadel.pdf"], "A",
  "The Sacred Magic of the Almadel / Ars Almadel", "anon. (Lemegeton Book IV)", "17th c.",
  "public domain", "Wax tablet angels — Lemegeton sibling of Goetia track. 9-pp excerpt witness."),
 ("grimoire_turiel", ["GrimoireofTuriel.pdf"], ["grimoire_turiel.pdf"], "A",
  "Grimoire of Turiel", "anon.", "17th c.",
  "public domain", "Created/fallen spirit hierarchy; oraison formulas."),
 ("infernal_dictionary", ["Infernal Dictionary.pdf"], ["collin_de_plancy_infernal_dictionary.pdf"], "A",
  "Dictionnaire Infernal", "Colin (Collin) de Plancy", "1863 ed.",
  "public domain", "739-pp demonology encyclopedia — densest entity mine in collection; queued LAST (largest)."),
 ("pgm_betz", ["Hans_Dieter_Betz_Greek_Magical_Papyri_in_Translation.pdf"],
  ["pgm_betz_complete.pdf"], "A",
  "Greek Magical Papyri in Translation", "Hans Dieter Betz (ed.)", "1986",
  "modern copyrighted edition; staged for private research", "voces magicae, phylacteries, ritual apparatus. Second identical file skipped."),
 ("magic_middle_ages", ["Magic-in-the-Middle-Ages-Richard-Kieck.pdf"], ["kieckhefer_magic_middle_ages.pdf"], "B",
  "Magic in the Middle Ages", "Richard Kieckhefer", "1989",
  "modern copyrighted; private research", "Same author as CLM 849 Forbidden Rites — direct scholarly context track."),
 ("godwin_necromancers", ["Godwin_William_-_Lives_of_the_Necromancers.pdf"], ["godwin_lives_of_necromancers.pdf"], "B",
  "The Lives of the Necromancers", "William Godwin", "1834",
  "public domain", "Biographical compendium of practitioners — practitioner-side roster cross-check."),
 ("pgm_wiki", ["Papyri Graecae Magicae.pdf"], ["pgm_selected_texts.pdf"], "B",
  "PGM selected texts (translation digest)", "anon. digest (PGM refs)", "n.d.",
  "rights unclear; digest staged for private cross-ref only", "Text digest keyed by PGM sigla; witness vs pgm_betz; do NOT treat as authoritative edition."),
 ("ars_notoria_ed2", ["Ars Notoria - The Notary Art of Solomon.pdf"], ["ars_notoria_notary_art_1909.pdf"], "B",
  "Ars Notoria — 'The Notary Art of Solomon' (2nd edition witness)", "MacGregor Mathers (transl.)", "1909?",
  "public domain", "Second translation witness of ars_notoria (differs from repo copy) — for compare_sources.py, not auto-distilled into DB."),
 ("budge_egyptian_book_dead", ["E.A. Wallis Budge - Egyptian Book Of The Dead.pdf"], ["budge_egyptian_book_of_the_dead.pdf"], "B",
  "The Egyptian Book of the Dead", "E.A. Wallis Budge (transl.)", "1895", "public domain", "Feeds worship_dead / Egyptian afterlife context."),
 ("budge_legends_gods", ["E.A. Wallis Budge - Legends of the Gods.pdf"], ["budge_legends_of_the_gods.pdf"], "B",
  "Legends of the Gods", "E.A. Wallis Budge", "1912", "public domain", "Egyptian deity context."),
 ("budge_egyptian_magic", ["egyptian_magic - Budge.pdf"], ["budge_egyptian_magic.pdf"], "B",
  "Egyptian Magic", "E.A. Wallis Budge", "1899", "public domain", "Egyptian ritual apparatus context."),
 ("handbook_egyptian_religion", ["A Handbook of Egyptian Religion.pdf"], ["handbook_egyptian_religion.pdf"], "B",
  "A Handbook of Egyptian Religion", "poide?, ed." if False else "anon.", "20th c.", "modern copyrighted; private research", "context."),
 ("pyramid_texts", ["Pyramid Texts_ Critical Analysis.pdf"], ["pyramid_texts_critical_analysis.pdf"], "B",
  "Pyramid Texts — Critical Analysis", "unknown", "n.d.", "rights unclear; private research", "check provenance before distill."),
 ("babylonian_omens", ["babylonian_birth_omens.pdf"], ["babylonian_birth_omens.pdf"], "B",
  "Babylonian Birth Omens", "unknown", "n.d.", "rights unclear; private research", "menological omens; context."),
 ("aryan_sun_myths", ["Aryan_Sun_Myths_1889.pdf"], ["aryan_sun_myths_1889.pdf"], "B",
  "Aryan Sun Myths: The Origin of Religions", "Godfrey Higgins", "1833/1889", "public domain", "comparative-mythology fringe; low-priority context."),
 ("prayer_magick_stars", ["Prayer, Magick, and Stars in Late Antiquity.pdf"], ["prayer_magick_stars_late_antiquity.pdf"], "B",
  "Prayer, Magick, and Stars in Late Antiquity", "scholarly (PGM-era studies)", "21st c.", "modern copyrighted; private research", "analytic context for pgm_betz."),
 ("ritos_muertos", ["ritos.pdf"], ["ritos_y_mitos_de_la_muerte_mexico.pdf"], "B",
  "Ritos y Mitos de la Muerte en México", "Gómez Pérez & Delgado Solís", "2000", "modern copyrighted; private research", "Spanish; Mexican death ritual — worship_dead crossover."),
 ("eleogap", ["137037732-Jake-Stratton-Kent-Eleogap.pdf"], ["strattonkent_eleogap.pdf"], "C",
  "The Eleogap (Goetia exorcism)", "Jake Stratton-Kent", "2019", "modern copyrighted; private research", "retrofit-lineage layer (construction-order studies)."),
 ("frimost_klepot", ["137037741-Jake-Stratton-Kent-Frimost-and-Klepot.pdf"], ["strattonkent_frimost_klepot.pdf"], "C",
  "Frimost and Klepot", "Jake Stratton-Kent", "2019", "modern copyrighted; private research", "retrofit-lineage layer."),
 ("goetic_divination", ["137037750-Jake-Stratton-Kent-Goetic-Divination.pdf"], ["strattonkent_goetic_divination.pdf"], "C",
  "The Goetia & Goetic Divination", "Jake Stratton-Kent", "2018", "modern copyrighted; private research", "retrofit-lineage layer."),
 ("headless_one", ["137037756-Jake-Stratton-Kent-The-Headless-One.pdf"], ["strattonkent_headless_one.pdf"], "C",
  "The Headless One", "Jake Stratton-Kent", "2018", "modern copyrighted; private research", "retrofit-lineage layer."),
 ("strattonkent_trve_grimoire", ["Kent, Jake Stratton - The Trve Grimoire.pdf"], ["strattonkent_trve_grimoire.pdf"], "C",
  "The Trve Grimoire", "Jake Stratton-Kent", "2023", "modern copyrighted; private research", "retrofit-lineage layer."),
 ("liber_falxifer_i", ["N.A-A.218 - LIBER FALXIFER -(SECOND EDITION)).pdf"], ["liber_falxifer_i_2e.pdf"], "C",
  "Liber Falxifer I (2nd ed.)", "N.A.A. / Ordo Novi Ordinis?", "2013", "modern copyrighted; private research", "modern Left-Hand-Path grimoire (Necromanticon spirit names) — retrofit layer."),
 ("liber_falxifer_ii", ["NAA 218 - Liber Falxifer II.pdf"], ["liber_falxifer_ii.pdf"], "C",
  "Liber Falxifer II", "N.A.A.", "2015", "modern copyrighted; private research", "retrofit layer."),
 ("goetic_pharmakos", ["Goetic_Pharmakos.pdf"], ["goetic_pharmakos.pdf"], "C",
  "The Goetic Pharmakos", "modern", "21st c.", "modern copyrighted; private research", "retrofit layer."),
 ("crowley_illustrated_goetia", ["Aleister Crowley-Lon Milo DuQuette - Aleister Crowley's Illustrated Goetia.pdf"], ["crowley_illustrated_goetia.pdf"], "C",
  "Aleister Crowley's Illustrated Goetia", "Crowley / DuQuette", "1995", "modern copyrighted; private research", "Goetia retrofit witness vs repo's 1904 Mathers goetia track — construction-order value."),
 ("lunar_formula_iao", ["137040102-The-Lunar-Formula-of-I-A-O-by-Derik-S.pdf"], ["lunar_formula_iao.pdf"], "C",
  "The Lunar Formula of I-A-O", "Derik S.", "n.d.", "modern; private research", "retrofit layer."),
 ("henson_lemegeton", ["Henson-Lemegeton.pdf"], ["henson_lemegeton.pdf"], "C",
  "Henson Lemegeton edition", "Henson", "n.d.", "modern; private research", "modern Lemegeton recension — retrofit layer vs goetia track."),
 # Tier D: image-only scans (auto-detected at extraction; staged, not chunked)
 ("abramelin", ["TheBookofAbramelin.pdf"], ["book_sacred_magic_abramelin_mathers.pdf"], "D",
  "The Book of the Sacred Magic of Abramelin the Mage", "MacGregor Mathers (transl.)", "1899", "public domain", "307-pp scan, NO text layer — OCR backlog; flagship operation (Holy Guardian Angel + 8+22 princes)."),
 ("book_of_black_magic", ["Book-Of-Black-Magic.pdf"], ["waite_book_of_black_magic_white_ritual.pdf"], "D",
  "Book of Black Magic and of Pacts", "A.E. Waite", "1898", "public domain", "image-only — OCR backlog."),
 ("demonomanie", ["Demonomanie.pdf"], ["bodin_demonomanie_1563.pdf"], "D",
  "De la Démonomanie des Sorciers", "Jean Bodin", "1563 (this scan: modern reprint?)", "public domain (1563)", "French demon-theory heavyweight — crossover w/ heresy-revolution archive; OCR backlog."),
 ("davies_grimoires", ["davies_-_grimoires.pdf"], ["davies_grimoires.pdf"], "D",
  "Grimoires: A History of Magic Books", "Owen Davies", "2009", "modern copyrighted; private research", "scholarly history — OCR backlog."),
 ("aradia", ["Aradia, or, The Gospel of the witches - Charles Godfrey Leland.pdf"], ["leland_aradia.pdf"], "D",
  "Aradia, or the Gospel of the Witches", "Charles Godfrey Leland", "1899", "public domain", "this copy image-only; better text editions exist (sacred-texts) — OCR or refetch."),
 ("geosophia_v1", ["Geosophia_Volume_1.pdf"], ["geosophia_v1.pdf"], "D",
  "Geosophia vol. 1", "anon. (theosophical)", "n.d.", "rights unclear; private research", "marginal; image-only."),
 ("geosophia_v2", ["Geosophia_Volume_2.pdf"], ["geosophia_v2.pdf"], "D",
  "Geosophia vol. 2", "anon. (theosophical)", "n.d.", "rights unclear; private research", "marginal; image-only."),
 ("clavicula_nox", ["Clavicula_Nox_-_Maleficarum_Nigra.pdf"], ["clavicula_nox.pdf"], "D",
  "Clavicula Nox", "Anton Szandor LaVey estate (Ordo Pro Versia ed.?)", "21st c.", "modern; private research", "modern LaVeyan text; image-only; retrofit layer."),
 ("conway_demonology_v1", ["Demonology_And_Devil-Lore_v1_1000040074.pdf"], ["conway_demonology_devil_lore_v1.pdf"], "D",
  "Demonology and Devil-Lore vol. 1", "Daniel Conway", "2010", "modern copyrighted; private research", "low scholarly value; image-only."),
 ("conway_demonology_v2", ["Daniel Conway - Demonology and Devil Lore - Volume 2.pdf"], ["conway_demonology_devil_lore_v2.pdf"], "D",
  "Demonology and Devil-Lore vol. 2", "Daniel Conway", "2010", "modern copyrighted; private research", "low scholarly value; image-only."),
 ("picatrix_book2_scan", ["Picatrix - Book 2.pdf"], ["picatrix_book2_scan.pdf"], "D",
  "Picatrix Book 2 (scan)", "Greer & Warnock?", "n.d.", "modern copyrighted; private research", "redundant w/ full Liber Rubeus text; image-only; likely skip permanently."),
 ("greer_picatrix_scan", ["greer-picatrix.pdf"], ["greer_picatrix_selected_scan.pdf"], "D",
  "Picatrix — Warnock Selected Translations (scan?)", "Christopher Warnock", "2019?", "modern copyrighted; private research", "image-only; subsumed by Liber Rubeus text; likely skip permanently."),
 ("grand_grimoire_trident", ["grand+grimoire+trident.pdf"], ["grand_grimoire_trident.pdf"], "D",
  "Grand Grimoire (trident version)", "anon.", "n.d.", "public domain", "variant edition, image-only; text version staged in Tier A."),
]

SKIP_EXACT_DUPES = {
 "PICATRIX - Latin Warburg Edition.pdf": "byte-identical to picatrix_pingree.pdf (staged as picatrix_latin)",
 "The Grand Grimoire - Dark Lodge version.pdf": "byte-identical to Grand Grimoire.pdf (staged as grand_grimoire)",
 "TheGreekMagicalPapyriinTranslation.pdf": "byte-identical to Betz file (staged as pgm_betz)",
}
SKIP_ALREADY_DISTILLED = {
 "Forbidden Rites.pdf": "same book already distilled as forbidden_rites_pdf (repo holds text copy); scan is 44 MB image — not re-staged",
 "Worship of the Dead.pdf": "same book already staged+distilled as worship_dead; scan 27 MB — not re-staged",
}

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def extract(pdf_path):
    import fitz
    doc = fitz.open(str(pdf_path))
    pages = [f"--- PAGE {i+1} ---\n{doc[i].get_text()}" for i in range(doc.page_count) if doc[i].get_text().strip()]
    n = doc.page_count
    doc.close()
    return "\n\n".join(pages), n

def main():
    import fitz  # noqa - warm import check
    man = json.load(open(MAN, encoding="utf-8"))
    by_id = {e["id"]: e for e in man["sources"]}
    report = []

    for (tid, srcs, staged_names, tier, label, author, date, lic, note) in TRACKS:
        entry = by_id.setdefault(tid, {"id": tid})
        if entry not in man["sources"]:
            man["sources"].append(entry)
        entry.update({"label": label, "author": author, "date": date, "license": lic,
                      "tier": tier, "status": "staged", "staged": TODAY,
                      "provenance": "H:\\THE GRIMOIRE COLLECTION\\THE LBP GRIMOIRE COLLECTION (LBP collection); staged 2026-10-27; distill queued but NOT started",
                      "description": note})
        # copy files + collect sha
        shas, total_pages, chars_all = [], 0, []
        for src, staged in zip(srcs, staged_names):
            sp = H / src
            if not sp.is_file():
                report.append(f"!! MISSING {src}"); continue
            dp = OP / staged
            dp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)
            shas.append(sha256(dp))
            # text extraction probe
            txt, npg = extract(dp)
            total_pages += npg
            chars_all.append(txt)
        entry["sha256"] = shas[0] if len(shas) == 1 else shas
        entry["path"] = f"data/sources/original_pdfs/{staged_names[0]}" if len(staged_names) == 1 else None
        entry["paths"] = [f"data/sources/original_pdfs/{n}" for n in staged_names]
        entry["pages"] = total_pages

        joined = "\n\n".join(f"=== FILE: {n} ===\n{t}" for t, n in zip(chars_all, staged_names)) if len(staged_names) > 1 else chars_all[0] if chars_all else ""
        text_density = len(joined.replace("---", "").strip()) / max(total_pages, 1)
        if text_density < 120:   # image-only scan
            entry["mode"] = "scanned_images"
            entry["status"] = "staged_ocr"
            report.append(f"{tid:28s} tier {tier} | {total_pages:4d}pp | IMAGE-ONLY -> OCR backlog")
            continue
        clean = clean_source_text(joined)
        cdir = ROOT / "data" / "sources" / tid
        cdir.mkdir(parents=True, exist_ok=True)
        for old in cdir.glob("chunk_*.txt"):
            old.unlink()   # clear any stale chunks from a previous run
        pos, cid, chunks_written, total = 0, 0, [], len(clean)
        while pos < total:
            end = min(pos + CHUNK_SIZE, total)
            if end < total:
                brk = clean.rfind("\n", pos + CHUNK_SIZE - 2000, end)
                if brk > pos:
                    end = brk
            (cdir / f"chunk_{cid:03d}.txt").write_text(clean[pos:end], encoding="utf-8")
            chunks_written.append((cid, end - pos))
            if end >= total:
                break
            pos = end - CHUNK_OVERLAP
            cid += 1
        entry.update({"mode": "native", "status": "staged_chunked",
                      "chunks_dir": f"data/sources/{tid}", "chunk_count": len(chunks_written),
                      "total_chars": total})
        report.append(f"{tid:28s} tier {tier} | {total_pages:4d}pp | {total:9d} chars | {len(chunks_written):3d} chunks")

    # skipped notes
    sk = [f"{k}: {v}" for k, v in {**SKIP_EXACT_DUPES, **SKIP_ALREADY_DISTILLED}.items()]
    note = "2026-10-27 LBP collection staged (see _meta/ingest-log.md); skipped dupes: " + "; ".join(sk)
    if note not in man.get("notes", ""):
        man["notes"] = (man.get("notes", "") + " | " if man.get("notes") else "") + note
    json.dump(man, open(MAN, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\n".join(report))
    print(f"\nSTAGED OK — manifest now {len(man['sources'])} entries")

if __name__ == "__main__":
    main()
