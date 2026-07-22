# Munich Handbook Research Summary

## Overview
This research project focuses on the Ars Notoria, a medieval magical text containing divine names, prayers, and ritual practices. The goal is to create a structured knowledge base for these esoteric materials.

## Key Components

### 1. Directory Management
- **File**: `src/directory_manager.py`
- **Purpose**: Robust path resolution and pre-flight checks for the research directory
- **Features**:
  - Graceful error handling for missing directories
  - Detailed logging of actual paths accessed
  - Content enumeration when directory exists

### 2. Divine Name Normalization
- **File**: `normalize_divine_names.py`
- **Purpose**: Standardize spelling variants found in Ars Notoria texts
- **Normalization Rules**:
  - 'æ' → 'ae' (ligature standardization)
  - 'z'/'s' variant handling for roots like Assay/Azzay
  - Compound name preservation (Lemath, Azacgessenio, etc.)

### 3. Knowledge Graph Schema
- **File**: `src/knowledge_graph.py`
- **Purpose**: Define and populate RDF/Turtle knowledge graph for Ars Notoria entities
- **Node Types**:
  - Prayer (e.g., Queen of Tongues)
  - DivineName (e.g., Lameth series)
  - Angel (Four Angels, etc.)
  - RitualDay (lunar phase associations)
  - Language (Chaldean, Hebrew, etc.)
  - LiberalArt (associated arts)

## Output Structure
```
munich_handbook_research/
├── src/
│   ├── directory_manager.py
│   └── knowledge_graph.py
├── data/
│   ├── divine_names_canonical.json
│   ├── graph_schema.json
│   └── sample_nodes.ttl
└── docs/
    └── research_summary.md
```

## Next Steps
1. Run `directory_manager.py` to verify directory structure
2. Execute `normalize_divine_names.py` to process source texts
3. Generate full knowledge graph from complete Ars Notoria corpus
4. Implement query interface for the RDF data
