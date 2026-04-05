# Validation Report: Spirit Data Check

## Warnings:

1. **Duplicate Spirit Names:**  
   - Found 2 spirits with identical names (case-insensitive): "Dragon" and "dragon".  
   *Warning:* Ensure unique spirit names to avoid confusion.

2. **Inconsistent Rank Case:**  
   - Ranks like "King" and "king" detected.  
   *Warning:* Maintain consistent casing for ranks ("King" or "king").

3. **Missing Required Fields:**  
   - 3 spirits lack required fields: `name`, `rank`, `experiment_id`.  
   *Warning:* All spirits must include these fields.

4. **Experiment-Spirit Reference Mismatch:**  
   - Experiment ID "E123" lacks a corresponding spirit.  
   *Warning:* Ensure every experiment maps to at least one spirit.

## Action Required:
- Resolve duplicates, case inconsistencies, missing fields, and reference mismatches for data integrity.
