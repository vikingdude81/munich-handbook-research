# Discoverie of Witchcraft — Content Analysis

> Reginald Scot (1584) — 1886 Nicholson reprint. 694 pages, 76 chunks (~1.8M chars).
> Source id: `discoverie` — chunked to `data/sources/discoverie/`

---

## Summary

| Metric | Value |
|--------|-------|
| Total pages | 694 |
| Extractable pages | 683 |
| Total chars | 1,786,094 |
| Chunks (25k chars) | 76 |
| Named spirits extracted | 20 |
| Conjuration hits | 510 |
| Circle mentions | 116 |
| Spirit mentions | 1098 |

---

## Book XV — The Conjuring Chapters

Book XV is the primary ceremonial magic section, pages 468–594.
This is the direct source for the conjuring circle in the Draper Sphere app.

### Chapter Structure

- **Ch. I:** Of Magical Circles — construction with cardinal guardians
- **Ch. II:** Purification formula — Maurath (E), Carrol (W), Catoil (N), Berith (S)
- **Ch. III:** Ceremonies of Necromancy — conjuration, answers, how to lay the spirit
- **Ch. IV:** Utensils, Circle construction, Consecration, Conjuration text
- **Ch. V:** Circles how to be made — Fumigations, Fires, Garments
- **Ch. VI:** Consecration ceremony — ancor, amacor, amides, theodonias, anitor
- **Ch. VII:** Apparitions — what spirits can do, dismissal (Tetragrammaton formula)
- **Ch. VIII:** Nature of Huritan — Familiar of the North, servant of Balsim
- **Ch. IX:** Full conjuration of Huritan with complete divine name chain

### Cardinal Guardian Spirits (Circle Purification Formula)

From Book XV Ch. II — spoken to purify ground before the circle:

| Direction | Guardian Name | Notes |
|-----------|--------------|-------|
| East | Maurath | Corrupted OCR: 'ffllaurafi' |
| West | Carrol | Corrupted OCR: 'fiarroil' |
| North | Catoil | Clear in text |
| South | Berith | Mentioned here + as Duke in Goetia section |

These are used as protective invocations *before* the main circle is cast.
They differ from the divine name positions in Scot's illustrated circle (Ch. VII),
suggesting a two-layer protection system: guardian spirits + divine names.

---

## Named Spirits Catalogue

Spirits with titles/ranks extracted from the text:

| Name | Rank | Legions | Appearance |
|------|------|---------|-----------|
| Allocer | Duke | six | - |
| Barbas | President | - | - |
| Bileth | King | - | - |
| Buer | President | fiftie | - |
| Cairn | President | - | - |
| Focalor | Duke | - | - |
| Foveas | President | - | - |
| Furcas | Knight | twentie | - |
| Gicsoin | Duke | fourtie | - |
| Haborhn | Duke | - | - |
| Malphas | President | - | - |
| Murmur | Duke | - | - |
| Orobas | Prince | - | - |
| Stolas | Prince | six | - |
| Valac | President | thirtie | - |
| Vapula | Duke | six | - |
| Vine | King | - | - |
| Vteall | Duke | - | - |
| Zagan | King | - | - |
| Zepar | Duke | twentie | - |

---

## Divine Names Corpus

Names appearing in conjuration formulas:

- Adonai
- Agla
- El
- Emanuel
- Messias
- Panthon
- Sabaoth
- Tetragrammaton

---

## Key Operations & Frequencies

| Operation | Hits |
|-----------|------|
| conjur | 510 |
| love | 142 |
| circle | 116 |
| familiar | 104 |
| knowledge | 94 |
| disease | 87 |
| treasure | 45 |
| invisible | 42 |
| apparition | 40 |
| divination | 37 |
| exorcism | 24 |
| incantation | 20 |
| transport | 19 |
| fumigation | 19 |
| binding | 11 |
| necromancy | 0 |

---

## Project Integration Opportunities

### 1. Spirit Data Expansion
The Discoverie contains 30+ named spirits with ranks and capabilities.
Many match the Goetia / Pseudomonarchia Daemonum cited in the Munich Handbook.
**Action:** Cross-reference with existing `src/spirits.json` and add verified entries.

### 2. Cardinal Guardian System
The four-directional guardian spirits (Maurath, Carrol, Catoil, Berith) are
a distinct invocation layer not currently in the project.
**Action:** Add to `src/summoning.py` as a `_purify_ground()` phase.

### 3. Fumigation Recipes
Book XV Ch. V describes fumigations by planet — sulfur (Saturn), incense (Jupiter),
red sanders (Mars), mastic (Sun), ambergris (Venus), mace (Mercury), camomile (Moon).
**Action:** Add to `design/experiment_models.py` as material requirements.

### 4. Huritan — New Spirit Entry
Huritan is a domestic familiar spirit of the North, servant to Balsim.
Not in the Munich Handbook but in the same textual tradition.
**Action:** Candidate for `src/spirits.json` as a verified Scot source spirit.

### 5. Dismissal Formula
Book XV Ch. VII contains the complete dismissal formula (Licentia) with
Tetragrammaton chain. This validates and extends `_licentia()` in `src/summoning.py`.

### 6. Conjuration Templates
Book XV Ch. IX contains the full Huritan conjuration — a template we can
add to `EXPERIMENTUM_REGISTRY` as a structured AI experiment.

### 7. Agrippa Cross-References
Agrippa is mentioned 30 times, Cornelius
19 times.
Scot directly cites De Occulta Philosophia for the planetary angel system.
**Action:** Add Agrippa as a `source_ref` field in the angel data structures.

---

## Distillation Plan

Priority chunks for AI distillation (Book XV is chunks ~60-66 of 76):

```bash
# Distill the conjuring-heavy chunks first
python src/distill_source.py --source discoverie --chunks 58,59,60,61,62,63,64,65
```

Schema targets:
- `spirits`: name, rank, legions, appearance, capabilities, source page
- `operations`: name, materials, timing, circle_required, dismissal_formula
- `divine_names`: name, position, language, tradition
- `fumigations`: planet, materials, timing_notes