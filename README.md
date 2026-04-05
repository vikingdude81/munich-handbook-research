# Munich Handbook of Necromancy — AI-Powered Research

**AI-driven entity extraction and analysis of the Munich Handbook of Necromancy (CLM 849)**

Mapping medieval conjuration protocols to modern AI agent orchestration patterns. Built with a 10-model GPU cluster running 120B parameter distillation across 4 compute nodes.

## What This Is

The Munich Handbook (Bayerische Staatsbibliothek, CLM 849) is a 15th-century necromancer's manual containing ~50 numbered experiments for summoning, binding, and commanding spirits. This project used a multi-GPU AI cluster to extract, normalize, and analyze every entity, relationship, and ritual protocol from the source texts — then mapped the structural patterns onto modern AI agent architecture.

## Key Outputs

| File | Description |
|------|-------------|
| [`munich_handbook_guide.txt`](munich_handbook_guide.txt) | **Comprehensive guide** — 1,058 spirits, 212 rituals, 193 ingredients, Table D cross-references (212K chars, 2,619 lines) |
| [`necromancy_to_ai_mapping.txt`](necromancy_to_ai_mapping.txt) | **Necromancy → AI mapping** — every structural element of medieval conjuration mapped to its AI agent counterpart (35K chars) |
| [`data/unified_entities.json`](data/unified_entities.json) | **Unified database** — 2,058 merged entities, 1,018 relationships across 67 source chunks (1.4 MB) |

## Database Statistics

```
Total raw entities extracted:    2,903
Unique entities after merge:     2,058
Total relationships:             1,018
Chunk summaries:                 67

Munich Handbook spirits:         1,058
Munich Handbook rituals:         212
Munich Handbook ingredients:     192
Munich Handbook tools:           117
Munich Handbook incantations:    31
Munich Handbook divine names:    15
Munich Handbook persons:         146

Table D spirits found:           7 / 11
Multi-source spirits:            263
```

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

## Infrastructure

- **Brain**: RTX 5090 — qwen3-coder-next 120B Q4_K_M (primary distillation)
- **Workers**: RTX 4070, A2000, RTX 3060 — 9 additional models for fan-out
- **Embedding**: nomic-embed on A2000
- **Distillation runtime**: ~7 hours for 126 chunks across 3 sources
- **Retry recovery**: 14/25 parse errors recovered via escalation

## Project Structure

```
├── data/
│   ├── unified_entities.json     # Final merged database (1.4 MB)
│   ├── distilled/                # Per-chunk distillation outputs (126 JSON files)
│   │   ├── forbidden_rites_pdf/  # 39 chunks from Kieckhefer PDF
│   │   ├── necro/                # 38 chunks from Necromancy text
│   │   └── worship_dead/         # 49 chunks from Worship of the Dead
│   └── sources/                  # Chunked source texts
│       ├── forbidden_rites_pdf/  # Source chunks
│       ├── necro/                # Source chunks
│       └── worship_dead/         # Source chunks
├── scripts/                      # Processing & analysis scripts
│   ├── source_prep.py            # Source text chunking
│   ├── run_full_distill.py       # Full batch distillation runner
│   ├── retry_parse_errors.py     # 2-phase retry (local + LLM re-run)
│   ├── normalize_entities.py     # Entity normalization & dedup pipeline
│   ├── find_table_d.py           # Table D cross-reference search
│   ├── spirit_breakdown.py       # Per-source spirit/ritual analysis
│   ├── compare_sources.py        # Source text comparison
│   ├── analyze_distill.py        # Initial entity analysis
│   ├── build_guide.py            # Guide generator
│   ├── build_mapping.py          # Necromancy-to-AI mapping generator
│   └── audit_experiments.py      # Experiment/summoning data audit
├── tools/
│   └── source_distill.py         # Core distillation tool (LLM extraction)
├── docs/                         # Analysis reports and documentation
├── src/                          # Earlier iteration code and models
├── munich_handbook_guide.txt     # THE GUIDE (main output)
├── necromancy_to_ai_mapping.txt  # THE MAPPING (AI parallels)
└── README.md
```

## Sources

Based on analysis of:
- **Richard Kieckhefer**, *Forbidden Rites: A Necromancer's Manual of the Fifteenth Century* (Penn State Press, 1997)
- Munich, Bayerische Staatsbibliothek, CLM 849

## License

Private research project. Not for redistribution.
