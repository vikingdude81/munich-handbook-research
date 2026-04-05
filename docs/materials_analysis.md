# Materials, Procedures, and Spirit References Analysis

## Extraction Schema

The following categories were identified for structured extraction:

- `materials` - Raw materials used in experiments
- `procedures` - Ritual procedures and steps
- `references_to_spirits` - Cross-references between spirits and experiments

## Rules

1. You MUST call write_project_file at least once — that is your entire purpose
2. Do NOT just say 'done' without calling write_project_file first
3. Extract and save ALL code blocks, not just the first one
4. If workers produced analysis text (no code), write it as a .md file in docs/
5. Say WRITEBACK_DONE only AFTER all write_project_file calls complete

## Status

- Phase 1: Distillation of 39 chunks through 120B Thinker - IN PROGRESS
- Phase 2: Expand src/spirit_vectors.py with every spirit found - PENDING
- Phase 3: Create src/experiments.py with structured experiment data - PENDING