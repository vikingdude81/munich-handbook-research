# Munich Handbook of Necromancy — AI-Powered Research

**AI-driven entity extraction, SOM topology mapping, and structural analysis of medieval grimoires**

Mapping medieval conjuration protocols to modern AI agent orchestration patterns. Built with a multi-GPU cluster running distillation, normalization, SOM training, and experiment automation across 5 historical sources.

## What This Is

The Munich Handbook (Bayerische Staatsbibliothek, CLM 849) is a 15th-century necromancer's manual containing ~50 numbered experiments for summoning, binding, and commanding spirits. This project uses a multi-GPU AI cluster to extract, normalize, and analyze every entity, relationship, and ritual protocol from the source texts — then maps the structural patterns onto modern AI agent architecture and trains a Self-Organizing Map to reveal the hidden topology of the spirit world.

## Key Projects

### 1. Necromancy & AI Orchestration

| File | Description |
|------|-------------|
| [`munich_handbook_guide.txt`](munich_handbook_guide.txt) | **Comprehensive guide** — 1,254 spirits, cross-grimoire rituals, ingredients, Table D references (270K chars) |
| [`necromancy_to_ai_mapping.txt`](necromancy_to_ai_mapping.txt) | **Necromancy → AI mapping** — every structural element of medieval conjuration mapped to its AI agent counterpart (40K chars) |
| [`data/unified_entities.json`](data/unified_entities.json) | **Unified database** — 2,467 merged entities, 1,200 relationships, 99 chunk summaries across 5 sources |
| [`som_output/`](som_output/) | **SOM Infernal Topology** — trained 15×15 Self-Organizing Map with cluster assignments, court labels, and visualizations |
| [`experiment_results/`](experiment_results/) | **6 conjuration experiments** re-implemented as multi-GPU AI agent workflows |

### 2. Heresy & Revolution: Deconstructionist Rhetoric Analysis

**Cross-referential study of Medieval Heresy Prosecution and 19th-Century Revolutionary Socialism through personality psychology, ressentiment, and entropy scoring.**

| File | Description |
|------|-------------|
| [`analysis/heresy_revolution/RESEARCH_METHODOLOGY.md`](analysis/heresy_revolution/RESEARCH_METHODOLOGY.md) | **Full research thesis** — theoretical framework mapping medieval witch persecution to Marxist revolutionary critique |
| [`analysis/heresy_revolution/QUICKSTART.md`](analysis/heresy_revolution/QUICKSTART.md) | **Setup guide** — ingest PDFs, run extraction pipeline, interpret entropy scores |
| [`config/heresy_revolution_schema.json`](config/heresy_revolution_schema.json) | **Extraction schema** — semantic vectors for deconstructionist vs. constructive rhetoric, JSON output format |
| `data/sources/malleus_marx/` | **Chunked source texts** — *Malleus Maleficarum* (1486) + *Selected Works of Karl Marx* (1848) |
| `data/distilled/malleus_marx/` | **Extracted analyses** — entropy scores, scapegoat identification, rhetorical intensity, constructive proposals per chunk |

**Key Insight:** Both texts show remarkably similar psychological patterns—same scapegoating mechanics (witch ↔ bourgeoisie), identical entropy profiles (high deconstruction, minimal construction), and moral justifications that create social contagion when environments destabilize.

## Database Statistics

```
Sources:                         5 grimoires
Total raw entities extracted:    3,507
Unique entities after merge:     2,467
Total relationships:             1,200
Chunk summaries:                 99

All spirits:                     1,254
Multi-source spirits:            266
```

## SOM — Infernal Topology

A 15×15 Self-Organizing Map trained on 1,254 spirit vectors (28 features) to reveal the hidden structure of the grimoire spirit world.

### Metrics
```
Quantization Error:  0.1996 (good — low representation error)
Topographic Error:   0.0056 (excellent — near-perfect topology preservation)
Populated cells:     90/225
Training:            2000 epochs, PCA-initialized
```

### Feature Vector (28 dimensions)
```
rank_ordinal (1)        — hierarchical rank scaled 0–1
planet_onehot (7)       — Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
direction_onehot (4)    — North, South, East, West
function_categories (10) — binding, divination, love, protection, destruction,
                           healing, invisibility, treasure, banquet, castle
nature_flags (3)        — angelic, demonic, divine_name
source_features (3)     — source count, occurrence, cross-grimoire flag
```

### Infernal Courts (major clusters)

| Cell | Court | Population | Notable Spirits |
|------|-------|-----------|-----------------|
| (0,11) | The Unnamed Host | 436 | Generic spirits with minimal distinguishing attributes |
| (3,0) | Demonic Court | 58 | Explicitly demonic — Althes, Bicol, Cormes |
| (8,11) | Court of Binding | 58 | Conjuration specialists — Abracalos, Abyncola |
| (7,7) | Angelic Conclave | 42 | Paraclitus, Uriel, Casziel |
| (2,11) | Sacred Assembly | 41 | Cherubim, Seraphim, Holy Spirit |
| (14,14) | Divine Names – Divination | 19 | Tetragrammaton, Adonay, Emmanuel |
| (12,0) | Court of Desire | 14 | Love/lust functions — Luxuriosus |
| (10,14) | Divine Binding | 31 | Eloym, Adonav — divine names in constraining |
| (4,13) | Divination Court | 32 | Divinatory and knowledge-seeking spirits |

### Visualizations

| File | Description |
|------|-------------|
| `som_output/u_matrix.png` | U-Matrix heatmap with spirit density overlay — dark regions are "Abysses" between incompatible courts |
| `som_output/component_planes.png` | 28 feature activation planes showing how each attribute distributes across the grid |
| `som_output/hit_map.png` | Spirit density per cell — reveals the mega-cluster and court populations |
| `som_output/cluster_assignments.json` | Full spirit-to-cell mapping with counts |
| `som_output/infernal_courts.json` | Court labels with dominant function/nature tags |
| `som_output/som_metrics.json` | QE/TE, grid stats, top courts |

## The Structural Parallel

| CLM 849 (Necromantic) | AI Agent System |
|---|---|
| Named Spirits (Astaroth, Berith) | Named Models (qwen3-coder-next, qwen3.5-9b) |
| The Conjuration Text | System Prompt |
| The Circle (circulus) | Sandbox / Guardrails |
| Divine Name Chains | Alignment / RLHF Constraints |
| Fumigations & Offerings | Context Window / Token Budget |
| Mirror / Crystal / Basin | Output Interface |
| Bond of Solomon (escalation) | Retry Logic / Model Escalation |
| Co-invoked Spirits | Multi-agent Fan-out |
| Directional Spirits (N/S/E/W) | Worker Node Assignment |
| Boy Medium (puer) | Lightweight Proxy Model |
| Licentia (dismissal) | Session Teardown / VRAM Free |
| SOM Topology (spirit clusters) | Model specialization clusters |

## Experiments

Six conjuration experiments from CLM 849 re-implemented as multi-GPU AI workflows:

| # | Name | Description | Latest Result |
|---|------|-------------|---------------|
| 1 | Knowledge Conjuration | RAG over 5-grimoire DB — cross-source comparative Q&A | 3 questions, 9,754 tokens, 76s |
| 8 | Ship Ritual | Fan-out to all cluster workers like 8 sailor-spirits | 8 sailors, 16K tokens, 115s |
| 11 | Anonymization Ritual | Document redaction + verification pipeline | 2 docs anonymized+verified |
| 12 | Spirit Synthesis | 3 spirits analyze from different perspectives, then synthesize | "The Architecture of Intent" |
| 22 | Boy-Medium | Lightweight proxy scouts, heavy model does deep analysis | Boy-medium + Practitioner |
| 27 | Escalating Conjuration | Tiered retry: fast → heavy → reasoning | Complied at tier 2 with JSON |

## Sources

Five historical grimoire traditions:

| Source ID | Text | Chunks |
|-----------|------|--------|
| `forbidden_rites_pdf` | Kieckhefer, *Forbidden Rites* (CLM 849 experiments) | 39 |
| `necro` | Munich Handbook necromancy text | 38 |
| `worship_dead` | *Worship of the Dead* tradition | 49 |
| `ars_notoria` | *Ars Notoria* — angelic knowledge acquisition | variable |
| `liber_juratus` | *Liber Juratus Honorii* — Sworn Book of Honorius | variable |

Based on analysis of:
- **Richard Kieckhefer**, *Forbidden Rites: A Necromancer's Manual of the Fifteenth Century* (Penn State Press, 1997)
- Munich, Bayerische Staatsbibliothek, CLM 849

## Infrastructure

- **Brain**: RTX 5090 (32GB) — qwen3.5-35b-a3b orchestrator
- **Workers**: RTX 4070, A2000, 2× RTX 3060+Xeon
- **Embedding**: Ollama nomic-embed-text on RTX 3060
- **SOM**: MiniSom, matplotlib, scipy, numpy

## Project Structure

```
├── data/
│   ├── unified_entities.json       # Final merged database (2,467 entities)
│   ├── distilled/                  # Per-chunk distillation outputs
│   │   ├── ars_notoria/            # Ars Notoria distillations
│   │   ├── forbidden_rites_pdf/    # CLM 849 distillations (39 chunks)
│   │   ├── liber_juratus/          # Liber Juratus distillations
│   │   ├── necro/                  # Necromancy text distillations (38 chunks)
│   │   └── worship_dead/           # Worship of the Dead (49 chunks)
│   └── sources/                    # Chunked source texts
├── som_output/                     # SOM training outputs
│   ├── u_matrix.png                # U-Matrix heatmap
│   ├── component_planes.png        # 28 feature planes
│   ├── hit_map.png                 # Spirit density map
│   ├── cluster_assignments.json    # Spirit → cell mapping
│   ├── infernal_courts.json        # Court labels
│   └── som_metrics.json            # QE/TE and stats
├── experiment_results/             # Conjuration experiment outputs
├── src/
│   ├── spirit_vectors.py           # Spirit → 28D feature vectorizer
│   ├── som_topology.py             # SOM training, visualization, court labeling
│   ├── lgi_manifold.py             # Lattice-Governed Inference (Magic Circle manifold)
│   └── ...                         # Distillation, validation, analysis modules
├── scripts/                        # Processing & analysis scripts
│   ├── source_prep.py              # Source text chunking
│   ├── run_full_distill.py         # Full batch distillation runner
│   ├── normalize_entities.py       # Entity normalization & dedup
│   ├── build_guide.py              # Guide generator
│   └── build_mapping.py            # Necromancy-to-AI mapping generator
├── tools/
│   └── source_distill.py           # Core LLM entity extraction tool
├── docs/                           # Analysis reports
├── munich_handbook_guide.txt       # THE GUIDE (main output — 270K chars)
├── necromancy_to_ai_mapping.txt    # THE MAPPING (AI structural parallels)
└── README.md
```

## License

Private research project. Not for redistribution.
