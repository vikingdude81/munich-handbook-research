# Distillation Validation Report

## Summary
All 39 chunks have at least one spirit/experiment entry.

## Rules Applied
- Never invent data. Every entity must come from a distilled extraction with a raw_quote.
- If a spirit's attributes are unclear, add it with a NEEDS_VERIFICATION flag.

## Next Steps
1. Review the distilled JSON files in `data/distilled/`
2. Expand `src/spirit_vectors.py` with every spirit found in the source text
3. Create `src/experiments.py` with structured experiment data cross-referenced to spirits