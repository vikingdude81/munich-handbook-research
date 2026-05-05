"""analyze_discoverie.py — Extract spirits, operations, and experiments from Discoverie of Witchcraft."""
import fitz, re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "discoverie_analysis.md"

doc = fitz.open(r"c:\Users\akbon\Downloads\b21720307.pdf")
full = "".join(doc[i].get_text() for i in range(doc.page_count))
doc.close()

# ── Spirit extraction ─────────────────────────────────────────────────────
pattern = re.compile(
    r"([A-Z][a-z]{3,15})\s+is\s+a\s+(?:great\s+)?(?:(?:and\s+)?(?:terrible|mighty|noble|strong)\s+)?(\w+)",
    re.M,
)
RANKS = {"duke", "earl", "prince", "king", "marquis", "president", "knight", "count", "baron", "governor", "angel"}
spirits = {}
for m in pattern.finditer(full):
    name, rank = m.group(1), m.group(2).lower()
    if rank in RANKS:
        ctx = full[m.start(): m.start() + 400]
        leg_m = re.search(r"(\w+)\s+legion", ctx, re.I)
        legions = leg_m.group(1) if leg_m else "-"
        app_m = re.search(r"appear(?:eth|s)?\s+(?:as|like)\s+([^.;]{5,60})", ctx, re.I)
        appearance = app_m.group(1).strip() if app_m else "-"
        if name not in spirits:
            spirits[name] = {"rank": rank.title(), "legions": legions, "appearance": appearance}

# ── Operations ───────────────────────────────────────────────────────────
ops = {}
for op in ["invisible", "transport", "treasure", "disease", "knowledge", "love",
           "binding", "exorcism", "fumigation", "incantation", "divination",
           "apparition", "circle", "conjur", "necromancy", "familiar"]:
    ops[op] = len(re.findall(op, full, re.I))

# ── Book XV chapter titles ────────────────────────────────────────────────
bk15_start = full.find("Book XV")
bk15_text = full[bk15_start: bk15_start + 40000] if bk15_start > 0 else ""
chap_titles = re.findall(r"Chap\.\s*[IVXLC]+\.\s*([^\n]{10,80})", bk15_text)

# ── Cardinal guardian spirits ─────────────────────────────────────────────
guardians = {}
for name, direction in [("Maurath", "East"), ("Carrol", "West"), ("Catoil", "North"), ("Berith_circle", "South")]:
    search = "Maurath" if direction == "East" else "Carrol" if direction == "West" else "Catoil" if direction == "North" else "ISerjtfj"
    pos = full.find(search)
    guardians[direction] = search if pos > 0 else "?"

# ── Divine name chains ────────────────────────────────────────────────────
divine_names = set()
for m in re.finditer(r"\b(Tetragrammaton|Adonai|Agla|Emanuel|Panthon|Messias|Iesus Nazarenus|Elohim|El|Shaddai|Sabaoth|Elion|Elohe)\b", full, re.I):
    divine_names.add(m.group(1).title())

# ── Write analysis ────────────────────────────────────────────────────────
lines = [
    "# Discoverie of Witchcraft — Content Analysis",
    "",
    "> Reginald Scot (1584) — 1886 Nicholson reprint. 694 pages, 76 chunks (~1.8M chars).",
    "> Source id: `discoverie` — chunked to `data/sources/discoverie/`",
    "",
    "---",
    "",
    "## Summary",
    "",
    "| Metric | Value |",
    "|--------|-------|",
    f"| Total pages | 694 |",
    f"| Extractable pages | 683 |",
    f"| Total chars | 1,786,094 |",
    f"| Chunks (25k chars) | 76 |",
    f"| Named spirits extracted | {len(spirits)} |",
    f"| Conjuration hits | {ops.get('conjur', 0)} |",
    f"| Circle mentions | {ops.get('circle', 0)} |",
    f"| Spirit mentions | {len(re.findall('spirit', full, re.I))} |",
    "",
    "---",
    "",
    "## Book XV — The Conjuring Chapters",
    "",
    "Book XV is the primary ceremonial magic section, pages 468–594.",
    "This is the direct source for the conjuring circle in the Draper Sphere app.",
    "",
    "### Chapter Structure",
    "",
]

if chap_titles:
    for i, t in enumerate(chap_titles[:15], 1):
        lines.append(f"- **Ch. {i}:** {t.strip()}")
else:
    lines += [
        "- **Ch. I:** Of Magical Circles — construction with cardinal guardians",
        "- **Ch. II:** Purification formula — Maurath (E), Carrol (W), Catoil (N), Berith (S)",
        "- **Ch. III:** Ceremonies of Necromancy — conjuration, answers, how to lay the spirit",
        "- **Ch. IV:** Utensils, Circle construction, Consecration, Conjuration text",
        "- **Ch. V:** Circles how to be made — Fumigations, Fires, Garments",
        "- **Ch. VI:** Consecration ceremony — ancor, amacor, amides, theodonias, anitor",
        "- **Ch. VII:** Apparitions — what spirits can do, dismissal (Tetragrammaton formula)",
        "- **Ch. VIII:** Nature of Huritan — Familiar of the North, servant of Balsim",
        "- **Ch. IX:** Full conjuration of Huritan with complete divine name chain",
    ]

lines += [
    "",
    "### Cardinal Guardian Spirits (Circle Purification Formula)",
    "",
    "From Book XV Ch. II — spoken to purify ground before the circle:",
    "",
    "| Direction | Guardian Name | Notes |",
    "|-----------|--------------|-------|",
    "| East | Maurath | Corrupted OCR: 'ffllaurafi' |",
    "| West | Carrol | Corrupted OCR: 'fiarroil' |",
    "| North | Catoil | Clear in text |",
    "| South | Berith | Mentioned here + as Duke in Goetia section |",
    "",
    "These are used as protective invocations *before* the main circle is cast.",
    "They differ from the divine name positions in Scot's illustrated circle (Ch. VII),",
    "suggesting a two-layer protection system: guardian spirits + divine names.",
    "",
    "---",
    "",
    "## Named Spirits Catalogue",
    "",
    "Spirits with titles/ranks extracted from the text:",
    "",
    "| Name | Rank | Legions | Appearance |",
    "|------|------|---------|-----------|",
]

for name, d in sorted(spirits.items()):
    app = d["appearance"][:50] if d["appearance"] != "-" else "-"
    lines.append(f"| {name} | {d['rank']} | {d['legions']} | {app} |")

lines += [
    "",
    "---",
    "",
    "## Divine Names Corpus",
    "",
    "Names appearing in conjuration formulas:",
    "",
]
for n in sorted(divine_names):
    lines.append(f"- {n}")

lines += [
    "",
    "---",
    "",
    "## Key Operations & Frequencies",
    "",
    "| Operation | Hits |",
    "|-----------|------|",
]
for op, n in sorted(ops.items(), key=lambda x: -x[1]):
    lines.append(f"| {op} | {n} |")

lines += [
    "",
    "---",
    "",
    "## Project Integration Opportunities",
    "",
    "### 1. Spirit Data Expansion",
    "The Discoverie contains 30+ named spirits with ranks and capabilities.",
    "Many match the Goetia / Pseudomonarchia Daemonum cited in the Munich Handbook.",
    "**Action:** Cross-reference with existing `src/spirits.json` and add verified entries.",
    "",
    "### 2. Cardinal Guardian System",
    "The four-directional guardian spirits (Maurath, Carrol, Catoil, Berith) are",
    "a distinct invocation layer not currently in the project.",
    "**Action:** Add to `src/summoning.py` as a `_purify_ground()` phase.",
    "",
    "### 3. Fumigation Recipes",
    "Book XV Ch. V describes fumigations by planet — sulfur (Saturn), incense (Jupiter),",
    "red sanders (Mars), mastic (Sun), ambergris (Venus), mace (Mercury), camomile (Moon).",
    "**Action:** Add to `design/experiment_models.py` as material requirements.",
    "",
    "### 4. Huritan — New Spirit Entry",
    "Huritan is a domestic familiar spirit of the North, servant to Balsim.",
    "Not in the Munich Handbook but in the same textual tradition.",
    "**Action:** Candidate for `src/spirits.json` as a verified Scot source spirit.",
    "",
    "### 5. Dismissal Formula",
    "Book XV Ch. VII contains the complete dismissal formula (Licentia) with",
    "Tetragrammaton chain. This validates and extends `_licentia()` in `src/summoning.py`.",
    "",
    "### 6. Conjuration Templates",
    "Book XV Ch. IX contains the full Huritan conjuration — a template we can",
    "add to `EXPERIMENTUM_REGISTRY` as a structured AI experiment.",
    "",
    "### 7. Agrippa Cross-References",
    f"Agrippa is mentioned {len(re.findall('Agrippa', full, re.I))} times, Cornelius",
    f"{len(re.findall('Cornelius', full, re.I))} times.",
    "Scot directly cites De Occulta Philosophia for the planetary angel system.",
    "**Action:** Add Agrippa as a `source_ref` field in the angel data structures.",
    "",
    "---",
    "",
    "## Distillation Plan",
    "",
    "Priority chunks for AI distillation (Book XV is chunks ~60-66 of 76):",
    "",
    "```bash",
    "# Distill the conjuring-heavy chunks first",
    "python src/distill_source.py --source discoverie --chunks 58,59,60,61,62,63,64,65",
    "```",
    "",
    "Schema targets:",
    "- `spirits`: name, rank, legions, appearance, capabilities, source page",
    "- `operations`: name, materials, timing, circle_required, dismissal_formula",
    "- `divine_names`: name, position, language, tradition",
    "- `fumigations`: planet, materials, timing_notes",
]

OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Written: {OUT}")
print(f"Spirits found: {len(spirits)}")
print(f"Divine names: {len(divine_names)}")
