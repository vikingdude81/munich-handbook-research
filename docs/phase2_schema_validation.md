# Phase 2 Schema Validation

## Review of RESEARCH_MANIFEST.md for Phase 2 Schema:

1. **Spirit Names**: All spirits must have a unique name (e.g., "Aether" or "Void").
2. **Ranks**: Each spirit's rank (e.g., "High Spirit", "Common Spirit") is required.
3. **Functions**: Specify roles (e.g., "Guardian", "Sorcerer").
4. **Appearances**: Count of appearances per spirit (e.g., 5).
5. **Legion Counts**: Number of legions associated with the spirit (e.g., 10).
6. **Conjuration Methods**: Techniques used (e.g., "Elemental Binding", "Celestial Ritual").
7. **Experiment Refs**: References to experiments (e.g., "EX-001", "EX-004").
8. **Page/Folio Numbers**: Page or folio number (e.g., "32" or "Folio 5").

## Validation Rules:
- All required fields must be present in each spirit entry.
- Ensure consistency in formatting (e.g., uniform spacing, case sensitivity).

## Output Example (JSON format):
```json
{
  "spirit": [
    {
      "name": "Aether",
      "rank": "High Spirit",
      "function": "Guardian",
      "appearances": 5,
      "legion_count": 10,
      "conjuration_method": "Elemental Binding",
      "experiment_ref": "EX-001",
      "page_folio": "32"
    }
  ]
}
```

## Action:
Confirm all spirits in `RESEARCH_MANIFEST.md` meet these criteria and generate the distill output.