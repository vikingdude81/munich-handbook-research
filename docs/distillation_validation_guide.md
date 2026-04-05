# Distillation Validation Guide

To validate all distilled JSON outputs, follow these steps:

## 1. Check Existence
Ensure each of the 39 chunks is present in `data/distilled/necro/`.

## 2. Validate Validity
Use a JSON validator tool to check if each chunk is valid JSON.

## 3. Check Completeness
Verify that each chunk contains all required fields:
- `chunk_id`: The ID of the chunk
- `status`: 'success' if all checks pass, 'failed' if any check fails, or 'partial' if some checks fail but others pass
- `missing_fields`: A list of fields that are missing from the chunk
- `raw_quote presence`: Indicate whether the raw quote is present in the chunk

## 4. Generate Report
Create a `distillation_report.json` file with the following structure:

```json
[
  {
    "chunk_id": "1",
    "status": "success",
    "missing_fields": [],
    "raw_quote presence": true
  },
  {
    "chunk_id": "2",
    "status": "failed",
    "missing_fields": ["raw_quote"],
    "raw_quote presence": false
  }
]
```

## 5. Retry Plan
For failed chunks, document the reason for failure and propose a retry plan (e.g., re-run the process, check data source, etc.).

---

**Note**: The `SpiritModel` includes a field `provenance` which is expected to be a dictionary. However, the schema does not include any specific validation rules for this field as it's left open-ended.

For `ExperimentModel`, the `validation_rules` field contains example of how you might structure validation rules related to the provenance linking in experiments. The actual implementation would depend on your specific use case and data integrity requirements.