# Chunk Audit Report

## Summary

This report documents the validation status of all 39 chunks (CLM849) from the Munich Handbook necro source.

## Validation Criteria

| Criterion | Description |
|-----------|-------------|
| Exists? | File exists in the directory |
| Valid JSON? | Content parses as valid JSON |
| Contains Spirits List? | Has a 'spirits' array in structure |
| Has Provenance Fields? | At least one spirit has name, rank, and raw_quote |

## Chunk Status Table

| File Name | Exists? | Valid JSON? | Contains Spirits List? | Has Provenance Fields? |
|-----------|---------|-------------|----------------------|------------------------|
| chunk_0.json | TBD | TBD | TBD | TBD |
| chunk_1.json | TBD | TBD | TBD | TBD |
| chunk_2.json | TBD | TBD | TBD | TBD |
| ... | ... | ... | ... | ... |
| chunk_38.json | TBD | TBD | TBD | TBD |

## Notes

- This report will be populated with actual validation results once the distillation process completes.
- Failed chunks should be cleaned and reprocessed using `fix_and_reprocess_failed_chunks.py`.
- All spirits must have provenance citing exact chunk and passage numbers.

## Next Steps

1. Run distillation on all 39 chunks
2. Validate JSON structure of each output
3. Ensure all spirits have required fields (name, rank, raw_quote)
4. Generate expanded spirit_vectors.py with provenance citations
5. Create experiments.py cross-referenced to spirits
