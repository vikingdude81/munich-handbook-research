# Heresy & Revolution Project — Quick Start

**Goal:** Cross-referential analysis of *The Malleus Maleficarum* (1486) and *Selected Works of Karl Marx* through the lens of deconstructionist rhetoric vs. constructive mechanisms.

## Quick Start

### 1. Install Dependencies

```bash
# Required for PDF extraction
pip install PyPDF2

# LM Studio must be running locally with a model loaded
# Download from: https://lmstudio.ai/
```

### 2. Ingest PDFs

```bash
# Chunk both PDFs into manageable pieces
python scripts/ingest_heresy_revolution.py --pdf all

# Or individually:
python scripts/ingest_heresy_revolution.py --pdf malleus
python scripts/ingest_heresy_revolution.py --pdf marx
```

This creates:
- `data/sources/malleus_marx/malleus_maleficarum/chunk_*.txt`
- `data/sources/malleus_marx/karl_marx/chunk_*.txt`

### 3. Distill with Entropy Analysis

```bash
# Analyze Malleus chunks
python scripts/distill_heresy_revolution.py --source malleus_maleficarum

# Analyze Marx chunks
python scripts/distill_heresy_revolution.py --source karl_marx
```

This produces:
- `data/distilled/malleus_marx/malleus_maleficarum_aggregate.json` — Summary stats + all analyses
- `data/distilled/malleus_marx/karl_marx_aggregate.json` — Summary stats + all analyses
- Individual chunk analyses: `malleus_maleficarum_chunk_*.json`, `karl_marx_chunk_*.json`

### 4. Cross-Document Analysis

```bash
python scripts/distill_heresy_revolution.py --analyze-cross-doc
```

Produces:
- `data/distilled/malleus_marx/cross_document_analysis.json` — Comparative insights

## Output Files

### Individual Chunk Analysis (JSON)

```json
{
  "chunk_id": "chunk_003",
  "primary_mode": "Deconstruction",
  "entropy_score": 8,
  "rhetorical_intensity": 9,
  "deconstruction_targets": ["heretics", "witches", "demon worship"],
  "constructive_proposals": ["vigilance", "ecclesiastical authority"],
  "scapegoat_identified": {
    "name": "The Witch",
    "attributes": ["servant of Satan", "corrupts virtue", "spreads plague"],
    "justification": "divine moral imperative to eradicate evil"
  },
  "semantic_markers_matched": {
    "deconstructionist": ["eradicate", "destroy", "expose"],
    "constructive": ["authority", "vigilance"]
  }
}
```

### Aggregate Analysis (JSON)

```json
{
  "source": "malleus_maleficarum",
  "total_chunks": 24,
  "successful": 24,
  "summary_stats": {
    "avg_entropy": 7.2,
    "max_entropy": 10,
    "min_entropy": 2,
    "avg_intensity": 8.1,
    "high_void_count": 8
  },
  "analyses": [...]
}
```

### Cross-Document Analysis (JSON)

```json
{
  "malleus_stats": {
    "avg_entropy": 7.2,
    "high_void_count": 8
  },
  "marx_stats": {
    "avg_entropy": 8.6,
    "high_void_count": 14
  },
  "scapegoat_mapping": {
    "malleus_scapegoats": ["The Witch", "Heretics", "Satan"],
    "marx_scapegoats": ["Capitalists", "Bourgeoisie", "Reactionaries"]
  },
  "void_analysis": {
    "interpretation": "High void = many chunks with high intensity but zero constructive proposals"
  }
}
```

## Key Metrics Explained

| Metric | Range | Meaning |
|--------|-------|---------|
| **entropy_score** | 1-10 | 1 = highly constructive/ordered; 10 = purely destructive/deconstructionist |
| **rhetorical_intensity** | 1-10 | 1 = calm observation; 10 = absolute moral condemnation |
| **primary_mode** | Categorical | Deconstruction \| Construction \| Mixed \| Neutral |
| **high_void_count** | Count | Chunks with entropy ≥ 8 AND zero constructive_proposals |

## Expected Results

### Malleus Maleficarum (Heresy Prosecution Manual)
- **Expected avg_entropy:** 6.5-8.0 (high deconstruction)
- **Expected avg_intensity:** 8.0-9.5 (moral condemnation)
- **Expected high_void_count:** 6-12 (intense critique without replacement systems)

### Selected Works of Karl Marx (Revolutionary Critique)
- **Expected avg_entropy:** 7.5-9.0 (very high deconstruction)
- **Expected avg_intensity:** 7.5-9.0 (intense moral critique)
- **Expected high_void_count:** 10-18 (heavy void: deconstruction without constructive detail)

### Semantic Convergence
- Both texts map scapegoats → "witch" ↔ "bourgeoisie" (different targets, identical psychological function)
- Both show high entropy with minimal constructive proposals
- Both use moral/cosmic justification (theological vs. materialist)

## Directory Structure

```
analysis/heresy_revolution/
  ├── RESEARCH_METHODOLOGY.md          (this file's methodology)
  ├── QUICKSTART.md                    (this file)
  └── findings/                        (generated analysis reports)

config/
  └── heresy_revolution_schema.json    (extraction schema & semantic vectors)

data/sources/malleus_marx/
  ├── malleus_maleficarum/
  │   ├── chunk_000.txt
  │   ├── chunk_001.txt
  │   └── ...
  └── karl_marx/
      ├── chunk_000.txt
      ├── chunk_001.txt
      └── ...

data/distilled/malleus_marx/
  ├── malleus_maleficarum_aggregate.json
  ├── karl_marx_aggregate.json
  ├── cross_document_analysis.json
  ├── malleus_maleficarum_chunk_000.json
  ├── malleus_maleficarum_chunk_001.json
  └── ...

scripts/
  ├── ingest_heresy_revolution.py      (PDF extraction & chunking)
  └── distill_heresy_revolution.py     (entropy analysis & extraction)
```

## Next Steps

1. **Ingest PDFs** → generates chunks
2. **Distill sources** → extracts entropy/scapegoats/constructive proposals
3. **Cross-document analysis** → maps semantic convergence
4. **Visualize results** → entropy trend plots, scapegoat matrices
5. **Synthesize thesis** → write comparative analysis paper

---

See `analysis/heresy_revolution/RESEARCH_METHODOLOGY.md` for full research framework and theoretical context.
