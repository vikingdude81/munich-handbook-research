# Munich Handbook Research Project
# CLM 849 - Spirits and Experiments from the Munich Handbook

## Current Status
- Phase 1: Batch distillation of all 39 chunks through 120B Thinker
- Phase 2: Expand spirit_vectors.py with extracted spirits
- Phase 3: Create experiments.py with structured experiment data

## Files Created
- `distillations/chunk_*.json` - Distilled extractions from each chunk
- `src/spirit_vectors.py` - Spirit entity definitions
- `src/experiments.py` - Experiment data structures
- `docs/research_manifest.md` - This file

## Rules
- Never invent data - every entity must come from distilled extraction
- Every spirit must have provenance citing exact chunk and passage
- If attributes unclear, add with NEEDS_VERIFICATION flag