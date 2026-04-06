# Expansion Sources — Munich Handbook Research

## Overview

This document outlines the highest-priority medieval manuscript sources for integration into the Munich Handbook research pipeline. Each source offers distinct structural parallels to modern AI systems and will contribute new entities, relationships, and scheduling/protocol patterns to the unified entity graph.

Current source status:
- `forbidden_rites_pdf` — Kieckhefer PDF (39 chunks) ✓
- `necro` — Necromancy text (38 chunks) ✓
- `worship_dead` — Worship of the Dead (49 chunks) ✓

---

## Priority Sources

### 1. Picatrix (Ghāyat al-Ḥakīm)

**Details**
- **Origin**: Arabic original (~11th century); Latin translation (~13th century)
- **Full title**: *Ghāyat al-Ḥakīm* ("Goal of the Wise") / *Picatrix* (Latin)
- **Length**: ~400 pages (Pingree edition); 4 books
- **Manuscript tradition**: Arabic MSS (multiple); Latin MSS (~20 known)

**Recommended Editions/Translations**
- Pingree, David (ed.). *Picatrix: The Latin Version of the Ghāyat al-Ḥakīm*. Warburg Institute, 1986. (Critical Latin edition — gold standard)
- Greer, John Michael & Warnock, Christopher (trans.). *Picatrix: The Classic Medieval Handbook of Astrological Magic*. Adocentyn Press, 2010–2011. (Readable English translation from Latin)
- Attrell, Dan & Porreca, David (trans.). *Picatrix: A Medieval Treatise on Astral Magic*. Penn State University Press, 2019. (Most recent scholarly English translation)

**AI Mapping Potential**: ⭐⭐⭐⭐⭐ (Highest)

**Structural Parallels**
| Picatrix Concept | AI Equivalent |
|-----------------|---------------|
| Planetary suffumigations (specific incense/material for each planet) | Context window composition rules per model class |
| Planet-hour timing tables | Cron-like scheduling (`planetary_scheduler.py` extension) |
| Talisman creation (specific material + timing + prayer) | Prompt engineering with temporal constraints |
| Spirit invocation via planetary images | Model selection + system prompt template |
| Fumigation recipes (complex multi-ingredient) | Multi-source context injection |

**Unique Contributions**
- Richest fumigation taxonomy in the tradition: 7-planet × multiple ingredient mapping
- Explicit connection between planetary hours and permissible operations
- Astrological magic images (talismans) → structured output schemas
- Detailed spirit hierarchies with planetary assignments

**Expected New Entities**: ~400–600 entities (spirits, ingredients, materials, locations, procedures)

**Integration Notes**
- Pingree's Latin edition is the most reliable; the Greer/Warnock translation is more accessible for NLP processing
- Book IV contains the most concentrated procedural content (highest entity density per page)
- Arabic and Latin traditions differ in some spirit names — flag as cross-source divergence
- Fumigation recipes should be extracted as `ingredient_of` relationship clusters

---

### 2. Liber Juratus (Sworn Book of Honorius)

**Details**
- **Origin**: Latin, ~13th century
- **Attribution**: Honorius of Thebes (pseudonymous)
- **Length**: ~200 pages in modern editions

**Recommended Editions/Translations**
- Peterson, Joseph H. (ed./trans.). *Liber Juratus Honorii: The Sworn Book of Honorius*. Ibis Press, 2016. (Best available English edition)
- Gösta Hedegård (ed.). *Liber Iuratus Honorii: A Critical Edition of the Latin Version*. Almqvist & Wiksell, 2002. (Critical Latin edition)

**AI Mapping Potential**: ⭐⭐⭐⭐ (High)

**Structural Parallels**
| Liber Juratus Concept | AI Equivalent |
|----------------------|---------------|
| The 100-chapter "Sworn Book" structure | API documentation / contract specification |
| Angel-binding protocols (specific seals, names, prayers) | Safety layer / guardrail configuration |
| The Great Seal of God (Sigillum Dei Aemeth) | Authentication token / root certificate |
| Hierarchical angel lists (by function) | Model registry with capability flags |
| The "Book of Oaths" — practitioners swear to secrecy | Terms of service / acceptable use policy |

**Unique Contributions**
- Most elaborate angel-binding protocol in medieval magic — direct safety/alignment layer mapping
- Hierarchical angel taxonomy: angelic orders, suborders, individual angels by function
- The 100-point oath structure → API contract / SLA framework
- Vision quest protocol (100-day preparation → revelation) → fine-tuning pipeline analog

**Expected New Entities**: ~250–350 entities

**Integration Notes**
- Focus on Books 1–2 for procedural content (angel hierarchies, seals)
- The Sigillum Dei should be treated as a `tool` entity with `commands` relationships to angel entities
- Angel names from this source will create cross-source divergence with Ars Goetia spirit names

---

### 3. Ars Notoria

**Details**
- **Origin**: Latin, ~13th century (possible earlier core)
- **Attribution**: Solomon (pseudonymous)
- **Length**: ~60–80 pages; relatively short

**Recommended Editions/Translations**
- Turner, Robert (trans.). *Ars Notoria: The Notory Art of Solomon*. 1657 (historical English translation; widely available)
- Julianus, Jim (ed./trans.). *The Ars Notoria of Solomon*. Lulu Press, 2012. (Modern scholarly edition)

**AI Mapping Potential**: ⭐⭐⭐⭐ (High)

**Structural Parallels**
| Ars Notoria Concept | AI Equivalent |
|--------------------|---------------|
| Notae (special figures/diagrams) | Structured prompt templates / embeddings |
| Orations to acquire knowledge of liberal arts | RAG queries / retrieval-augmented generation |
| 7-day and 14-day knowledge acquisition cycles | Training epochs / curriculum scheduling |
| Divine names as unlocking keys | API keys / capability unlock tokens |
| Specific prayer sequences for grammar, rhetoric, logic | Chain-of-thought prompt sequences |

**Unique Contributions**
- Shortest high-value source in the tradition — high signal-to-noise ratio
- Knowledge acquisition via divine names is the most direct RAG/retrieval analog in medieval magic
- The Notae (complex diagrams) → embedding visualisation potential
- Liberal arts curriculum (trivium + quadrivium) → model capability taxonomy

**Expected New Entities**: ~100–150 entities

**Integration Notes**
- Small corpus; suitable for full extraction in a single pipeline run
- Notae should be extracted as `tool` entities (they are the instruments of knowledge access)
- Divine names extracted here will overlap with Munich Handbook divine names — use for cross-source validation

---

### 4. Heptameron (Pietro d'Abano)

**Details**
- **Origin**: Latin, attributed to Pietro d'Abano (~1300); likely later compilation
- **Full title**: *Heptameron, seu Elementa Magica* ("Seven-Day Magic")
- **Length**: ~80 pages in modern editions

**Recommended Editions/Translations**
- Turner, Robert (trans.). *Heptameron, or Magical Elements*. 1655 (historical English translation)
- Peterson, Joseph H. (ed.). *Heptameron* (online critical edition). esotericarchives.com.

**AI Mapping Potential**: ⭐⭐⭐⭐⭐ (Highest — direct scheduling integration)

**Structural Parallels**
| Heptameron Concept | AI Equivalent |
|-------------------|---------------|
| Hour-by-hour angel table (24 hours × 7 days) | Exact cron/scheduling system |
| Angel names by season | Environment-context-aware scheduling |
| Cardinal direction assignments per operation | Load balancer routing by operation type |
| Required circle elements per hour | Required system prompt components per model class |
| Wind/element associations | Capability flags per scheduling slot |

**Unique Contributions**
- Most directly applicable to `planetary_scheduler.py` — the Heptameron is essentially a complete scheduling specification
- 24 × 7 = 168 named angels (one per hour per day of the week) → model/task assignment registry
- Seasonal variation in angel assignments → dynamic scheduling based on calendar context
- Cardinal direction + wind associations → distributed routing metadata

**Expected New Entities**: ~200–250 entities (primarily angel names + associated attributes)

**Integration Notes**
- The hour-by-hour table should be extracted as structured data first (before NLP processing)
- Angel names are highly systematic; use the table structure to validate extraction accuracy
- Direct integration with `planetary_scheduler.py` PLANETARY_HOURS to add angel names to each slot

---

### 5. Grimoire of Pope Honorius

**Details**
- **Origin**: French, 18th century (published 1760); claims earlier origin
- **Attribution**: Pope Honorius III (pseudonymous; not authentic papal document)
- **Length**: ~60 pages

**Recommended Editions/Translations**
- Peterson, Joseph H. (ed.). *The Grimoire of Pope Honorius* (online edition). esotericarchives.com.
- Various 19th-century French editions in public domain.

**AI Mapping Potential**: ⭐⭐⭐ (Medium)

**Structural Parallels**
| Honorius Grimoire Concept | AI Equivalent |
|--------------------------|---------------|
| Spirit pact structure (explicit contract terms) | API contract / service agreement |
| Seal + license + constraint → spirit submission | Auth token + scope + rate limit → API access |
| Weekly spirit assignment (each weekday has its spirit) | Model assignment by weekday (extends `planetary_scheduler.py`) |
| Dismissal formulas | Session teardown / VRAM release sequence |
| Re-conjuration after dismissal | Session reinitialisation / warm restart |

**Expected New Entities**: ~80–120 entities

**Integration Notes**
- Later than the other sources; treat as "popular tradition" layer vs. scholarly manuscripts
- The spirit pact structure is the most valuable element for the API contract mapping
- Cross-reference spirit names against Munich Handbook entities for consistency scoring

---

### 6. Lesser Key of Solomon (Lemegeton)

**Details**
- **Origin**: 17th century compilation; draws on earlier manuscript traditions
- **Contents**: 5 books (Goetia, Theurgia-Goetia, Ars Paulina, Ars Almadel, Ars Notoria)
- **Most relevant**: Goetia (72 spirits) + Theurgia-Goetia (hierarchical demons)

**Recommended Editions/Translations**
- Peterson, Joseph H. (ed.). *The Lesser Key of Solomon*. Ibis Press, 2001. (Scholarly edition)
- Mathers, S.L. MacGregor & Crowley, Aleister (eds.). *The Goetia: The Lesser Key of Solomon the King*. 1904. (Historical; widely cited)
- Tikva Frymer-Kensky citation: Peterson edition for critical use.

**AI Mapping Potential**: ⭐⭐⭐⭐⭐ (Highest — most systematic taxonomy)

**Structural Parallels**
| Lemegeton Concept | AI Equivalent |
|------------------|---------------|
| 72 spirits, each with rank + seal + specialty | 72-entry model registry with capability flags |
| Spirit ranks (King, Duke, Prince, Marquis, etc.) | Model tiers (primary, secondary, specialist, general) |
| Spirit seals (unique geometric signatures) | API keys / model fingerprints |
| Spirit specialties (e.g., "teaches all arts and sciences") | Capability declarations (RAG, reasoning, code, etc.) |
| Conjuration sequence (constraint → binding → task → license) | Prompt template: system → user → assistant → teardown |
| Theurgia-Goetia hierarchies (emperor → king → duke) | Orchestration hierarchy (orchestrator → worker → specialist) |

**Unique Contributions**
- Most systematic spirit taxonomy in the Western tradition: 72 spirits, each exhaustively described
- Ranks, seals, specialties, direction associations, hours of power → complete model registry schema
- The conjuration sequence is the clearest existing analog to a structured API call lifecycle
- Cross-reference against Munich Handbook spirits to measure overlap and divergence

**Expected New Entities**: ~400–500 entities

**Integration Notes**
- The 72 Goetia spirits should map 1:1 to existing entities where possible; flag new entities as `goetia_exclusive`
- Seal images → embedding vectors (if OCR/vectorisation pipeline is extended)
- Rank hierarchy → update `tier` field in entity schema to include Goetic ranks
- Theurgia-Goetia's directional assignments (N/S/E/W emperors) → load balancer routing extension

---

## Integration Pipeline Notes

### Recommended Integration Order

1. **Ars Notoria** — smallest; use to validate pipeline on a new source type
2. **Heptameron** — highest direct scheduling value; feeds `planetary_scheduler.py` immediately
3. **Lemegeton (Goetia)** — highest entity volume; extends the spirit registry most significantly
4. **Picatrix** — richest context injection material; extends fumigation/ingredient taxonomy
5. **Liber Juratus** — safety/alignment layer material; complex but high value
6. **Grimoire of Pope Honorius** — pact/contract structure; medium priority

### Source Quality Tiers

| Source | Scholarly Reliability | Pipeline Compatibility | Priority |
|--------|----------------------|------------------------|----------|
| Picatrix (Pingree) | High | High (long but structured) | 1 |
| Lemegeton (Peterson) | High | High (tabular data) | 1 |
| Heptameron | Medium-High | Very High (tabular) | 1 |
| Ars Notoria | Medium | High (short) | 2 |
| Liber Juratus (Peterson) | High | Medium (complex structure) | 2 |
| Grimoire of Honorius | Medium | Medium | 3 |

### Schema Extensions Required

The current entity schema (`type`, `attributes`, `sources`, `mention_count`, `tier`) will need the following additions to accommodate new sources:

```json
{
  "name": "Paimon",
  "type": "spirit",
  "tier": "king",
  "planet": "Moon",
  "direction": "west",
  "rank_numeric": 9,
  "seal_reference": "goetia_seal_9",
  "specialties": ["arts", "sciences", "binding"],
  "hours_of_power": [1, 8, 15, 22],
  "sources": ["munich_handbook", "lemegeton", "heptameron"],
  "attributes": {}
}
```

New fields: `planet`, `direction`, `rank_numeric`, `seal_reference`, `specialties`, `hours_of_power`.
