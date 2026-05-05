# Discoverie of Witchcraft — Project Integration

> Reginald Scot, *The Discoverie of Witchcraft* (1584, Nicholson reprint 1886).
> Ingested as source `discoverie` — 76 chunks, ~1.8M chars, in `data/sources/discoverie/`.

---

## What Was Added

### 1. New Spirits (`src/spirits.json`)

Seven spirits added from the *Discoverie*, sourced from Book XV and the
Pseudomonarchia Daemonum appendix (Weyer / Scot's version of the Goetia):

| Name | Rank | Function | Notes |
|------|------|----------|-------|
| **Huritan** | Familiar | domestic_assistance | Book XV Ch. VIII–IX; North-aspected domestic spirit, servant of Balsim |
| **Bathin** | Duke | transport_knowledge | Transports to foreign countries; herbs and stones knowledge |
| **Vine** | King | revelation_building | Reveals hidden things; builds/destroys towers |
| **Purson** | King | treasure_discovery | Hidden treasure; divine/secret knowledge |
| **Shax** | Marquis | stealth_theft | Weakens senses; stealth extraction |
| **Valac** | President | serpent_command | Commands serpents; discovers treasure |
| **Berith** | Duke | transmutation_knowledge | Turns metals to gold; knowledge of tongues. Also the **South guardian** in the Book XV circle purification formula |

The 11 original CLM 849 spirits (Forbidden Rites / Munich Handbook) are unchanged.
All entries now carry a `source` field: `"forbidden_rites"` or `"discoverie"`.

### 2. New Experiments (`src/summoning.py`)

Five new experiments added to `EXPERIMENTUM_REGISTRY`, each grounded in a
specific Book XV chapter:

| # | Title | Source Chapter | AI Operation |
|---|-------|---------------|-------------|
| **13** | Familiar summoning — Huritan | Bk XV Ch. VIII–IX | Domestic Q&A bound to North quarter |
| **14** | Ground purification — cardinal guardian invocation | Bk XV Ch. II | Four-quadrant critical analysis (Maurath/Carrol/Catoil/Berith) |
| **15** | Planetary fumigation — material preparation | Bk XV Ch. V | Classify passage by planetary domain |
| **16** | Dismissal — Licentia | Bk XV Ch. VII | Structured summary + task closure |
| **17** | Apparition signs — pre-appearance detection | Bk XV Ch. VII | Pre-scan for OCR errors, anomalies |

All experiments carry a `"source"` key with a `discoverie/bk15/chN` path.

### 3. Cardinal Guardian System (`src/summoning.py`)

The `Circle` dataclass now has a `cardinal_guardians` field with the four
directional spirits from Book XV Ch. II:

```python
cardinal_guardians = {
    "East":  "Maurath",
    "West":  "Carrol",
    "North": "Catoil",
    "South": "Berith",
}
```

The `Circle.as_system_message(purify=True)` method prepends a ground-purification
header before the main system prompt, mirroring the spoken invocation in Scot.

---

## What Was Analysed

Full analysis doc: [docs/discoverie_analysis.md](discoverie_analysis.md)

### Book XV Chapter Map

Book XV is pages 468–594 of the 1886 reprint (chunks ~60–66 of 76):

| Chapter | Title | Key Content |
|---------|-------|-------------|
| Ch. I | Of Magical Circles | Construction with cardinal guardians |
| Ch. II | Circle purification | Fourfold guardian invocation (Maurath, Carrol, Catoil, Berith) |
| Ch. III | Ceremonies of Necromancy | Conjuration, Spirit answers, How to lay the Spirit |
| Ch. IV | Utensils / Circle / Consecration | Materials list; Circle diagram with divine names |
| Ch. V | Circles — Fumigations | Planetary fumigation recipes; garment consecration |
| Ch. VI | Consecration ceremony | Names: ancor, amacor, amides, theodonias, anitor |
| Ch. VII | Apparitions / Dismissal | What spirits can do; Licentia formula with Tetragrammaton |
| Ch. VIII | Nature of Huritan | Domestic familiar of the North; servant of Balsim |
| Ch. IX | Conjuration of Huritan | Full text with divine name chain |
| App. II Bk. II | Discourse on Devils and Spirits | Seven good Angels; Astral spirits; Familiars |

### Spirit Capabilities (Scot Book XV)

From Ch. IV — what the conjured spirit can do:

- Transport the magician to **foreign countries**
- Knowledge of **physical processes** and operations
- Go **invisible** and fly through the airy region
- Give the **Girdle of Victory** (protective talisman)
- Reveal hidden **treasure** locations
- Teach **languages** and knowledge of tongues

These map to the following AI capabilities in `EXPERIMENTUM_REGISTRY`:
invisibility → Exp. 11; transport → Exp. 8 (fan-out); knowledge → Exp. 1; treasure → Exp. 27.

### Divine Names Corpus

Names found in conjuration formulas across the Discoverie:

`AGLA` · `Adonai` · `El` · `Elohim` · `Emanuel` · `Messias` · `Panthon` · `Tetragrammaton`

Plus the Consecration chain from Ch. VI:
**ancor · amacor · amides · theodonias · anitor**

And the Dismissal chain from Ch. VII:
**Tetragrammaton · Saiiat · Ohon · Emillaf · Saifianatos · Panaretos**

### Agrippa Cross-References

Scot cites Agrippa (*De Occulta Philosophia*) **30 times**, Cornelius **19 times**.
The planetary angel system and the seven good Angels in Appendix II both trace to
Agrippa Bk. III. This confirms the Agrippa → Scot → CLM 849 transmission chain.

---

## What Remains To Do

### Near-term

1. **Distill Book XV chunks** through the AI pipeline to extract structured
   spirit/ritual data automatically:
   ```bash
   python src/distill_source.py --source discoverie --chunks 60,61,62,63,64,65,66
   ```

2. **De Occultis OCR** — background job running in terminal `25858d64-...`.
   When complete (~30 chunks), run the same analysis for cipher/steganography content
   to enhance the Cipher tab in the Draper Sphere app.

3. **Cross-reference `spirits.json`** — verify Scot's Berith (red soldier, 26 legions)
   against CLM 849 Berith description.

### Future / Optional

4. **Fumigation recipes** as a new `materials` sub-schema:
   `{planet, ingredient, substitutes, timing_notes}` — useful for the Circle
   construction UI in the Draper Sphere.

5. **Planetary angel list** from Discoverie Appendix II (Jubaillatace, Gaontin, Palanu...)
   — compare with the Munich Handbook's angel attribution tables.

6. **Experiment 18 (Agrippa synthesis)** — cross-reference query that asks the LLM
   to match a Munich Handbook passage with its probable Agrippa source chapter.

---

## Source Location

| Asset | Path |
|-------|------|
| Chunked text | `data/sources/discoverie/chunk_000.txt` – `chunk_075.txt` |
| Source manifest | `data/sources/source_manifest.json` (entry: `discoverie`) |
| This doc | `docs/discoverie_integration.md` |
| Analysis report | `docs/discoverie_analysis.md` |
| Spirits data | `src/spirits.json` |
| Experiments code | `src/summoning.py` (`EXPERIMENTUM_REGISTRY` keys 13–17) |
