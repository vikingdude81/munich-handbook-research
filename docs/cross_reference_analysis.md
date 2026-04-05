# Cross-Reference Analysis: CLM 849 Experiment References

## Status: INCOMPLETE - DATA REQUIRED

### Task Description
The task requires cross-referencing experiment references against CLM 849 folio numbers.

### Missing Information Required
Without access to specific datasets, the following cannot be executed:

1. **Experiment References List** (e.g., CSV/JSON format)
   - Need: List of experiment IDs/names from source chunks
   
2. **CLM 849 Folio Numbering System**
   - Need: Database schema or folio mapping for Munich Handbook (CLM 849)

### Next Steps
If the required data is shared, the following process can be executed:

1. Parse experiment references from distilled JSON files
2. Map each reference to CLM 849 folio numbers
3. Identify unmatched references or incomplete extractions
4. Generate validation report with per-chunk status

### Current Findings
- Spirit variants extracted (vodka, whisky) - see `data/spirit_variants.json`
- JSON validation utility available at `src/utils/json_validator.py`
- Cross-referencing pending data input
